"""
Unit tests for PlansService.

Tests cover plan fetching, caching, offline support, and cache management.
Supabase client calls are mocked to ensure fast, reliable tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from src.services.plans_service import PlansService


@pytest.mark.unit
class TestPlansService:
    """Test suite for PlansService."""
    
    @pytest.fixture
    def plans_service(self, mock_supabase_client):
        """Create PlansService instance with mocked Supabase client."""
        with patch('src.services.plans_service.get_supabase_client', return_value=mock_supabase_client):
            service = PlansService()
            return service
    
    @pytest.fixture
    def mock_page_with_storage(self, mock_page):
        """Create mock page with client storage."""
        mock_page.client_storage = Mock()
        mock_page.client_storage.get = Mock(return_value=None)
        mock_page.client_storage.set = Mock()
        mock_page.client_storage.remove = Mock()
        return mock_page
    
    @pytest.fixture
    def sample_plan_data(self):
        """Sample plan data for testing."""
        return {
            "id": "plan-123",
            "user_id": "test-user-id-123",
            "title": "Trip to Manila",
            "description": "3-day adventure in Manila",
            "image_url": "https://example.com/manila.jpg",
            "created_at": "2025-12-01T10:00:00Z",
            "data": {
                "status": "completed",
                "itinerary": [
                    {
                        "day": 1,
                        "locations": [
                            {
                                "name": "Rizal Park",
                                "rating": 4.5,
                                "address": "Manila, Philippines"
                            }
                        ]
                    }
                ]
            }
        }
    
    @pytest.fixture
    def sample_generating_plan_data(self):
        """Sample plan data that is still generating."""
        return {
            "id": "plan-456",
            "user_id": "test-user-id-123",
            "title": "Trip to Cebu",
            "description": "Planning...",
            "image_url": None,
            "created_at": "2025-12-02T10:00:00Z",
            "data": {
                "status": "generating",
                "itinerary": []
            }
        }
    
    def test_initialization(self, plans_service):
        """Test PlansService initializes correctly."""
        assert plans_service.client is not None
        assert plans_service._cached_plans == []
        assert plans_service._page is None
    
    def test_initialize_with_page(self, plans_service, mock_page_with_storage):
        """Test initialize() sets page reference and loads cache."""
        plans_service.initialize(mock_page_with_storage)
        
        assert plans_service._page == mock_page_with_storage
        mock_page_with_storage.client_storage.get.assert_called_once_with(PlansService.CACHE_KEY)
    
    def test_get_current_user_id_when_authenticated(self, plans_service, mock_supabase_user):
        """Test _get_current_user_id returns user ID when authenticated."""
        mock_response = Mock()
        mock_response.user = mock_supabase_user
        plans_service.client.auth.get_user.return_value = mock_response
        
        user_id = plans_service._get_current_user_id()
        
        assert user_id == "test-user-id-123"
    
    def test_get_current_user_id_when_not_authenticated(self, plans_service):
        """Test _get_current_user_id returns None when not authenticated."""
        mock_response = Mock()
        mock_response.user = None
        plans_service.client.auth.get_user.return_value = mock_response
        
        user_id = plans_service._get_current_user_id()
        
        assert user_id is None
    
    @patch('src.services.plans_service.mark_offline')
    def test_get_current_user_id_handles_network_error(self, mock_mark_offline, plans_service):
        """Test _get_current_user_id handles network errors."""
        plans_service.client.auth.get_user.side_effect = Exception("Network error")
        
        user_id = plans_service._get_current_user_id()
        
        assert user_id is None
        mock_mark_offline.assert_called_once()
    
    def test_load_from_cache_success(self, plans_service, mock_page_with_storage, sample_plan_data):
        """Test _load_from_cache loads plans from storage."""
        cached_plans = [sample_plan_data]
        mock_page_with_storage.client_storage.get.return_value = json.dumps(cached_plans)
        
        plans_service.initialize(mock_page_with_storage)
        
        assert len(plans_service._cached_plans) == 1
        assert plans_service._cached_plans[0]["id"] == "plan-123"
    
    def test_load_from_cache_empty(self, plans_service, mock_page_with_storage):
        """Test _load_from_cache handles empty cache."""
        mock_page_with_storage.client_storage.get.return_value = None
        
        plans_service.initialize(mock_page_with_storage)
        
        assert plans_service._cached_plans == []
    
    def test_save_to_cache(self, plans_service, mock_page_with_storage, sample_plan_data):
        """Test _save_to_cache saves plans to storage."""
        plans_service.initialize(mock_page_with_storage)
        plans = [sample_plan_data]
        
        plans_service._save_to_cache(plans)
        
        mock_page_with_storage.client_storage.set.assert_called()
        call_args = mock_page_with_storage.client_storage.set.call_args
        assert call_args[0][0] == PlansService.CACHE_KEY
        saved_data = json.loads(call_args[0][1])
        assert len(saved_data) == 1
        assert saved_data[0]["id"] == "plan-123"
    
    def test_get_plans_success_online(self, plans_service, mock_page_with_storage, 
                                      sample_plan_data, mock_supabase_user):
        """Test get_plans fetches from Supabase when online."""
        plans_service.initialize(mock_page_with_storage)
        
        # Mock authenticated user
        mock_user_response = Mock()
        mock_user_response.user = mock_supabase_user
        plans_service.client.auth.get_user.return_value = mock_user_response
        
        # Mock Supabase response
        mock_table_response = Mock()
        mock_table_response.data = [sample_plan_data]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_table_response
        plans_service.client.table.return_value = mock_table
        
        plans, is_from_cache = plans_service.get_plans()
        
        assert len(plans) == 1
        assert plans[0]["id"] == "plan-123"
        assert plans[0]["title"] == "Trip to Manila"
        assert is_from_cache is False
    
    def test_get_plans_transforms_generating_status(self, plans_service, mock_page_with_storage,
                                                    sample_generating_plan_data, mock_supabase_user):
        """Test get_plans correctly identifies generating plans."""
        plans_service.initialize(mock_page_with_storage)
        
        # Mock authenticated user
        mock_user_response = Mock()
        mock_user_response.user = mock_supabase_user
        plans_service.client.auth.get_user.return_value = mock_user_response
        
        # Mock Supabase response with generating plan
        mock_table_response = Mock()
        mock_table_response.data = [sample_generating_plan_data]
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_table_response
        plans_service.client.table.return_value = mock_table
        
        plans, is_from_cache = plans_service.get_plans()
        
        assert len(plans) == 1
        assert plans[0]["is_generating"] is True
    
    @patch('src.services.plans_service.mark_offline')
    def test_get_plans_falls_back_to_cache_on_error(self, mock_mark_offline, plans_service, 
                                                     mock_page_with_storage, sample_plan_data):
        """Test get_plans returns cached plans on network error."""
        plans_service.initialize(mock_page_with_storage)
        plans_service._cached_plans = [sample_plan_data]
        
        # Mock network error
        plans_service.client.table.side_effect = Exception("Network connection failed")
        
        plans, is_from_cache = plans_service.get_plans()
        
        assert len(plans) == 1
        assert plans[0]["id"] == "plan-123"
        assert is_from_cache is True
        mock_mark_offline.assert_called_once()
    
    def test_get_plans_no_user_returns_cache(self, plans_service, mock_page_with_storage, sample_plan_data):
        """Test get_plans returns cache when no user is authenticated."""
        plans_service.initialize(mock_page_with_storage)
        plans_service._cached_plans = [sample_plan_data]
        
        # Mock no authenticated user
        mock_user_response = Mock()
        mock_user_response.user = None
        plans_service.client.auth.get_user.return_value = mock_user_response
        
        with patch('src.services.plans_service.get_connectivity_state') as mock_connectivity:
            mock_connectivity.return_value.is_online = False
            
            plans, is_from_cache = plans_service.get_plans()
            
            assert len(plans) == 1
            assert is_from_cache is True
    
    def test_get_cached_plans(self, plans_service, sample_plan_data):
        """Test get_cached_plans returns cached plans."""
        plans_service._cached_plans = [sample_plan_data]
        
        plans = plans_service.get_cached_plans()
        
        assert len(plans) == 1
        assert plans[0]["id"] == "plan-123"
    
    def test_clear_cache(self, plans_service, mock_page_with_storage, sample_plan_data):
        """Test clear_cache removes all cached plans."""
        plans_service.initialize(mock_page_with_storage)
        plans_service._cached_plans = [sample_plan_data]
        
        plans_service.clear_cache()
        
        assert plans_service._cached_plans == []
        mock_page_with_storage.client_storage.remove.assert_called_once_with(PlansService.CACHE_KEY)
    
    def test_update_cache_with_plan_new_plan(self, plans_service, mock_page_with_storage, sample_plan_data):
        """Test update_cache_with_plan adds new plan to cache."""
        plans_service.initialize(mock_page_with_storage)
        
        plans_service.update_cache_with_plan(sample_plan_data)
        
        assert len(plans_service._cached_plans) == 1
        assert plans_service._cached_plans[0]["id"] == "plan-123"
        mock_page_with_storage.client_storage.set.assert_called()
    
    def test_update_cache_with_plan_existing_plan(self, plans_service, mock_page_with_storage, sample_plan_data):
        """Test update_cache_with_plan updates existing plan in cache."""
        plans_service.initialize(mock_page_with_storage)
        plans_service._cached_plans = [sample_plan_data.copy()]
        
        # Update the plan
        updated_plan = sample_plan_data.copy()
        updated_plan["title"] = "Updated Trip to Manila"
        
        plans_service.update_cache_with_plan(updated_plan)
        
        # Should still have only 1 plan (replaced, not added)
        assert len(plans_service._cached_plans) == 1
        assert plans_service._cached_plans[0]["title"] == "Updated Trip to Manila"
    
    def test_update_cache_with_plan_adds_to_beginning(self, plans_service, mock_page_with_storage, 
                                                      sample_plan_data, sample_generating_plan_data):
        """Test update_cache_with_plan adds new plan at the beginning."""
        plans_service.initialize(mock_page_with_storage)
        plans_service._cached_plans = [sample_plan_data]
        
        plans_service.update_cache_with_plan(sample_generating_plan_data)
        
        assert len(plans_service._cached_plans) == 2
        # New plan should be first (most recent)
        assert plans_service._cached_plans[0]["id"] == "plan-456"
        assert plans_service._cached_plans[1]["id"] == "plan-123"
    
    def test_remove_from_cache(self, plans_service, mock_page_with_storage, 
                               sample_plan_data, sample_generating_plan_data):
        """Test remove_from_cache removes specific plan from cache."""
        plans_service.initialize(mock_page_with_storage)
        plans_service._cached_plans = [sample_plan_data, sample_generating_plan_data]
        
        plans_service.remove_from_cache("plan-123")
        
        assert len(plans_service._cached_plans) == 1
        assert plans_service._cached_plans[0]["id"] == "plan-456"
        mock_page_with_storage.client_storage.set.assert_called()
    
    def test_remove_from_cache_nonexistent_plan(self, plans_service, mock_page_with_storage, sample_plan_data):
        """Test remove_from_cache handles nonexistent plan gracefully."""
        plans_service.initialize(mock_page_with_storage)
        plans_service._cached_plans = [sample_plan_data]
        
        plans_service.remove_from_cache("nonexistent-plan-id")
        
        # Should still have the original plan
        assert len(plans_service._cached_plans) == 1
        assert plans_service._cached_plans[0]["id"] == "plan-123"


@pytest.mark.unit
class TestPlansServiceOfflineSupport:
    """Test offline support functionality."""
    
    @pytest.fixture
    def plans_service(self, mock_supabase_client):
        """Create PlansService instance with mocked Supabase client."""
        with patch('src.services.plans_service.get_supabase_client', return_value=mock_supabase_client):
            service = PlansService()
            return service
    
    @pytest.fixture
    def mock_page_with_storage(self, mock_page):
        """Create mock page with client storage."""
        mock_page.client_storage = Mock()
        mock_page.client_storage.get = Mock(return_value=None)
        mock_page.client_storage.set = Mock()
        mock_page.client_storage.remove = Mock()
        return mock_page
    
    @patch('src.services.plans_service.mark_online')
    def test_get_plans_marks_online_on_success(self, mock_mark_online, plans_service, 
                                               mock_page_with_storage, mock_supabase_user):
        """Test get_plans marks app as online when fetch succeeds."""
        plans_service.initialize(mock_page_with_storage)
        
        # Mock authenticated user
        mock_user_response = Mock()
        mock_user_response.user = mock_supabase_user
        plans_service.client.auth.get_user.return_value = mock_user_response
        
        # Mock successful Supabase response
        mock_table_response = Mock()
        mock_table_response.data = []
        
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_table_response
        plans_service.client.table.return_value = mock_table
        
        plans_service.get_plans()
        
        mock_mark_online.assert_called_once()
    
    @patch('src.services.plans_service.mark_offline')
    def test_get_plans_marks_offline_on_network_error(self, mock_mark_offline, plans_service, 
                                                       mock_page_with_storage):
        """Test get_plans marks app as offline on network error."""
        plans_service.initialize(mock_page_with_storage)
        
        # Mock network error
        plans_service.client.table.side_effect = Exception("Connection timeout")
        
        plans_service.get_plans()
        
        mock_mark_offline.assert_called_once()
    
    def test_cache_persistence_across_sessions(self, plans_service, mock_page_with_storage):
        """Test cache persists across service instances."""
        # First session - save to cache
        cached_data = [{"id": "plan-1", "title": "Cached Plan"}]
        mock_page_with_storage.client_storage.get.return_value = json.dumps(cached_data)
        
        plans_service.initialize(mock_page_with_storage)
        
        # Verify cache was loaded
        assert len(plans_service._cached_plans) == 1
        assert plans_service._cached_plans[0]["id"] == "plan-1"
