"""
Unit tests for FavoritesService.

Tests cover favorites management with both local JSON fallback
and Supabase persistence when authenticated.
"""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
from src.services.favorites_service import FavoritesService


@pytest.mark.unit
class TestFavoritesService:
    """Test suite for FavoritesService."""
    
    @pytest.fixture
    def favorites_service(self, mock_supabase_client):
        """Create FavoritesService instance with mocked Supabase client."""
        with patch('src.services.favorites_service.get_supabase_client', return_value=mock_supabase_client):
            service = FavoritesService()
            return service
    
    def test_initialization(self, favorites_service):
        """Test FavoritesService initializes correctly."""
        assert favorites_service.client is not None
        assert isinstance(favorites_service._favorites, list)
    
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    def test_load_local_favorites_empty(self, mock_file, mock_exists, favorites_service):
        """Test loading empty local favorites file."""
        favorites_service._load_local_favorites()
        
        assert favorites_service._favorites == []
    
    @patch('os.path.exists', return_value=True)
    def test_load_local_favorites_with_data(self, mock_exists, favorites_service, sample_favorites_list):
        """Test loading local favorites file with data."""
        mock_data = json.dumps(sample_favorites_list)
        
        with patch('builtins.open', mock_open(read_data=mock_data)):
            favorites_service._load_local_favorites()
            
            assert len(favorites_service._favorites) == 2
            assert favorites_service._favorites[0]["name"] == "Test Place"
    
    @patch('os.path.exists', return_value=False)
    def test_load_local_favorites_file_not_exists(self, mock_exists, favorites_service):
        """Test loading when favorites file doesn't exist."""
        favorites_service._load_local_favorites()
        
        assert favorites_service._favorites == []
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_local_favorites(self, mock_json_dump, mock_file, favorites_service):
        """Test saving favorites to local JSON file."""
        favorites_service._favorites = [{"place_id": "test123", "name": "Test"}]
        
        favorites_service._save_local_favorites()
        
        # Verify file was opened with encoding
        mock_file.assert_called_once()
        call_args = mock_file.call_args
        assert call_args[0][0] == favorites_service.FILE_PATH
        assert call_args[0][1] == 'w'
        assert call_args[1]['encoding'] == 'utf-8'
    
    def test_get_favorites_when_authenticated(self, favorites_service, sample_favorites_list):
        """Test get_favorites returns Supabase data when authenticated."""
        # Mock Supabase response with 2 favorites
        mock_execute = Mock()
        mock_execute.data = [
            {"data": sample_favorites_list[0]},
            {"data": sample_favorites_list[1]}
        ]
        mock_eq = Mock()
        mock_eq.execute.return_value = mock_execute
        mock_select = Mock()
        mock_select.eq.return_value = mock_eq
        mock_table = Mock()
        mock_table.select.return_value = mock_select
        favorites_service.client.table.return_value = mock_table
        
        # Mock authenticated user
        favorites_service._get_current_user_id = Mock(return_value="user-123")
        favorites_service._supabase_fetch_done = False  # Force fetch
        
        result = favorites_service.get_favorites()
        
        assert len(result) == 2
        assert result[0]["name"] == "Test Place"
    
    def test_get_favorites_when_not_authenticated(self, favorites_service, sample_favorites_list):
        """Test get_favorites returns local data when not authenticated."""
        # Set up local favorites
        favorites_service._favorites = sample_favorites_list
        
        # Mock no authenticated user
        favorites_service._get_current_user_id = Mock(return_value=None)
        
        result = favorites_service.get_favorites()
        
        assert len(result) == 2
    
    def test_is_favorite_true(self, favorites_service, sample_place_data):
        """Test is_favorite returns True for favorited place."""
        favorites_service._favorites = [sample_place_data]
        
        result = favorites_service.is_favorite(sample_place_data["place_id"])
        
        assert result is True
    
    def test_is_favorite_false(self, favorites_service):
        """Test is_favorite returns False for non-favorited place."""
        favorites_service._favorites = []
        
        result = favorites_service.is_favorite("non-existent-id")
        
        assert result is False
    
    @patch('builtins.open', new_callable=mock_open)
    def test_add_favorite_when_not_authenticated(self, mock_file, favorites_service, sample_place_data):
        """Test add_favorite saves to local file when not authenticated."""
        # Mock unauthenticated
        favorites_service.client.auth.get_user.return_value = Mock(user=None)
        favorites_service._favorites = []
        
        favorites_service.add_favorite(sample_place_data)
        
        assert len(favorites_service._favorites) == 1
        assert favorites_service._favorites[0]["place_id"] == sample_place_data["place_id"]
    
    def test_add_favorite_when_authenticated(self, favorites_service, sample_place_data):
        """Test add_favorite saves to Supabase when authenticated."""
        # Mock authenticated user
        mock_user = Mock()
        mock_user.id = "test-user-123"
        favorites_service.client.auth.get_user.return_value = Mock(user=mock_user)
        
        # Mock Supabase insert
        mock_table = Mock()
        mock_insert = Mock()
        mock_execute = Mock()
        mock_execute.data = [sample_place_data]
        mock_insert.execute.return_value = mock_execute
        mock_table.insert.return_value = mock_insert
        favorites_service.client.table.return_value = mock_table
        
        favorites_service._favorites = []
        favorites_service.add_favorite(sample_place_data)
        
        # Verify Supabase was called
        mock_table.insert.assert_called_once()
    
    def test_add_favorite_already_exists(self, favorites_service, sample_place_data):
        """Test add_favorite doesn't duplicate existing favorite."""
        favorites_service._favorites = [sample_place_data]
        
        favorites_service.add_favorite(sample_place_data)
        
        # Should still only have one
        assert len(favorites_service._favorites) == 1
    
    @patch('builtins.open', new_callable=mock_open)
    def test_remove_favorite_when_not_authenticated(self, mock_file, favorites_service, sample_place_data):
        """Test remove_favorite updates local file when not authenticated."""
        # Mock unauthenticated
        favorites_service.client.auth.get_user.return_value = Mock(user=None)
        favorites_service._favorites = [sample_place_data]
        
        favorites_service.remove_favorite(sample_place_data["place_id"])
        
        assert len(favorites_service._favorites) == 0
    
    def test_remove_favorite_when_authenticated(self, favorites_service, sample_place_data):
        """Test remove_favorite updates Supabase when authenticated."""
        # Mock authenticated user
        mock_user = Mock()
        mock_user.id = "test-user-123"
        favorites_service.client.auth.get_user.return_value = Mock(user=mock_user)
        
        # Mock Supabase delete
        mock_table = Mock()
        mock_delete = Mock()
        mock_eq = Mock()
        mock_execute = Mock()
        mock_eq.execute.return_value = mock_execute
        mock_delete.eq.return_value = mock_eq
        mock_table.delete.return_value = mock_delete
        favorites_service.client.table.return_value = mock_table
        
        favorites_service._favorites = [sample_place_data]
        favorites_service.remove_favorite(sample_place_data["place_id"])
        
        # Verify Supabase was called
        mock_table.delete.assert_called_once()
    
    def test_toggle_favorite_adds_when_not_favorite(self, favorites_service, sample_place_data):
        """Test toggle_favorite adds place when not already favorited."""
        favorites_service._favorites = []
        favorites_service.client.auth.get_user.return_value = Mock(user=None)
        
        with patch.object(favorites_service, '_save_local_favorites'):
            result = favorites_service.toggle_favorite(sample_place_data)
        
        assert result is True
        assert len(favorites_service._favorites) == 1
    
    def test_toggle_favorite_removes_when_favorite(self, favorites_service, sample_place_data):
        """Test toggle_favorite removes place when already favorited."""
        favorites_service._favorites = [sample_place_data]
        favorites_service.client.auth.get_user.return_value = Mock(user=None)
        
        with patch.object(favorites_service, '_save_local_favorites'):
            result = favorites_service.toggle_favorite(sample_place_data)
        
        assert result is False
        assert len(favorites_service._favorites) == 0


@pytest.mark.unit
class TestFavoritesServiceCaching:
    """Test caching behavior in FavoritesService."""
    
    @pytest.fixture
    def favorites_service(self, mock_supabase_client):
        """Create FavoritesService instance with mocked Supabase client."""
        with patch('src.services.favorites_service.get_supabase_client', return_value=mock_supabase_client):
            service = FavoritesService()
            return service
    
    def test_get_favorites_uses_cache(self, favorites_service, sample_place_data):
        """Test get_favorites uses cached data when force_refresh=False."""
        favorites_service._favorites = [sample_place_data]
        favorites_service.client.auth.get_user.return_value = Mock(user=None)
        
        # First call should not reload
        favorites1 = favorites_service.get_favorites(force_refresh=False)
        favorites2 = favorites_service.get_favorites(force_refresh=False)
        
        assert favorites1 == favorites2
    
    def test_user_cache_reduces_api_calls(self, favorites_service):
        """Test user ID is cached to reduce API calls."""
        mock_user = Mock()
        mock_user.id = "cached-user-123"
        favorites_service.client.auth.get_user.return_value = Mock(user=mock_user)
        
        # First call populates cache
        user_id1 = favorites_service._get_current_user_id()
        # Second call should use cache
        user_id2 = favorites_service._get_current_user_id()
        
        assert user_id1 == user_id2
        # Verify auth.get_user was only called once
        assert favorites_service.client.auth.get_user.call_count == 1
