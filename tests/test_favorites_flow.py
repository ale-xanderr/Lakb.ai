"""
Integration tests for favorites workflows.

Tests cover complete favorites management flows including adding, removing,
toggling, and syncing favorites.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import json


@pytest.mark.integration
class TestFavoritesFlows:
    """Integration tests for favorites workflows."""
    
    @pytest.fixture
    def favorites_service(self, mock_supabase_client):
        """Create FavoritesService with mocked Supabase."""
        from src.services.favorites_service import FavoritesService
        with patch('src.services.favorites_service.get_supabase_client', return_value=mock_supabase_client):
            return FavoritesService()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_add_favorite_local_flow(self, mock_file, favorites_service, sample_place_data):
        """Test adding favorite with local storage (not authenticated)."""
        # User is not authenticated
        favorites_service.client.auth.get_user.return_value = Mock(user=None)
        favorites_service._favorites = []
        
        # Add favorite
        favorites_service.add_favorite(sample_place_data)
        
        # Verify favorite was added
        assert len(favorites_service._favorites) == 1
        assert favorites_service.is_favorite(sample_place_data["place_id"]) is True
        
        # Verify saved to local file
        mock_file.assert_called()
    
    def test_add_favorite_cloud_flow(self, favorites_service, sample_place_data):
        """Test adding favorite with cloud storage (authenticated)."""
        # User is authenticated
        mock_user = Mock(id="user-123")
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
        
        # Add favorite
        favorites_service.add_favorite(sample_place_data)
        
        # Verify Supabase was called
        mock_table.insert.assert_called_once()
        assert len(favorites_service._favorites) == 1
    
    @patch('builtins.open', new_callable=mock_open)
    def test_remove_favorite_flow(self, mock_file, favorites_service, sample_place_data):
        """Test removing favorite."""
        # Setup: favorite exists
        favorites_service._favorites = [sample_place_data]
        favorites_service.client.auth.get_user.return_value = Mock(user=None)
        
        # Remove favorite
        favorites_service.remove_favorite(sample_place_data["place_id"])
        
        # Verify removed
        assert len(favorites_service._favorites) == 0
        assert favorites_service.is_favorite(sample_place_data["place_id"]) is False
    
    @patch('builtins.open', new_callable=mock_open)
    def test_toggle_favorite_flow(self, mock_file, favorites_service, sample_place_data):
        """Test toggling favorite status."""
        favorites_service._favorites = []
        favorites_service.client.auth.get_user.return_value = Mock(user=None)
        
        # Toggle ON
        result1 = favorites_service.toggle_favorite(sample_place_data)
        assert result1 is True
        assert len(favorites_service._favorites) == 1
        
        # Toggle OFF
        result2 = favorites_service.toggle_favorite(sample_place_data)
        assert result2 is False
        assert len(favorites_service._favorites) == 0
    
    def test_sync_local_to_cloud_on_login(self, favorites_service, sample_place_data):
        """Test local favorites sync to cloud when user logs in."""
        # Setup: User has local favorites
        favorites_service._favorites = [sample_place_data]
        
        # User logs in
        mock_user = Mock(id="new-user-123")
        favorites_service.client.auth.get_user.return_value = Mock(user=mock_user)
        
        # Mock Supabase operations
        mock_table = Mock()
        
        # Mock cloud favorites (empty)
        mock_select = Mock()
        mock_eq = Mock()
        mock_execute = Mock()
        mock_execute.data = []
        mock_eq.execute.return_value = mock_execute
        mock_select.eq.return_value = mock_eq
        mock_table.select.return_value = mock_select
        
        # Mock insert for syncing
        mock_insert = Mock()
        mock_insert_execute = Mock()
        mock_insert_execute.data = [sample_place_data]
        mock_insert.execute.return_value = mock_insert_execute
        mock_table.insert.return_value = mock_insert
        
        favorites_service.client.table.return_value = mock_table
        
        # Refresh to sync
        favorites = favorites_service.get_favorites(force_refresh=True)
        
        # Verify cloud was queried
        mock_table.select.assert_called()
