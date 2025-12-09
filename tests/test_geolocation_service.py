"""
Unit tests for GeolocationService.

Tests cover location requests, position handling, and reverse geocoding integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.geolocation_service import GeolocationService


@pytest.mark.unit
class TestGeolocationService:
    """Test suite for GeolocationService."""
    
    @pytest.fixture
    def geo_service(self, mock_page, mock_api_service):
        """Create GeolocationService instance with mocked dependencies."""
        with patch('src.services.geolocation_service.APIService', return_value=mock_api_service):
            service = GeolocationService(mock_page)
            return service
    
    def test_initialization(self, geo_service, mock_page):
        """Test GeolocationService initializes correctly."""
        assert geo_service.page is mock_page
        assert geo_service.api_service is not None
        assert geo_service.last_location is None
        assert geo_service.geolocator is not None
    
    def test_geolocator_added_to_overlay(self, mock_page, mock_api_service):
        """Test geolocator is added to page overlay on init."""
        with patch('src.services.geolocation_service.APIService', return_value=mock_api_service):
            service = GeolocationService(mock_page)
            
            assert len(mock_page.overlay) == 1
            assert service.geolocator in mock_page.overlay
    
    def test_cleanup_removes_geolocator(self, geo_service, mock_page):
        """Test cleanup removes geolocator from overlay."""
        geo_service.cleanup()
        
        assert geo_service.geolocator not in mock_page.overlay
        assert geo_service._is_cleaned_up is True
    
    def test_cleanup_idempotent(self, geo_service):
        """Test cleanup can be called multiple times safely."""
        geo_service.cleanup()
        geo_service.cleanup()  # Should not raise error
        
        assert geo_service._is_cleaned_up is True
    
    @patch('threading.Thread')
    def test_request_location_starts_async(self, mock_thread, geo_service):
        """Test request_location starts asynchronous location request."""
        geo_service.request_location()
        
        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_request_location_skips_when_cleaned_up(self, geo_service):
        """Test request_location skips when service is cleaned up."""
        geo_service._is_cleaned_up = True
        
        # Should not raise error
        geo_service.request_location()
    
    def test_handle_position_updates_location(self, geo_service, mock_api_service):
        """Test _handle_position processes location update."""
        # Mock position event
        mock_event = Mock()
        mock_event.latitude = 13.621
        mock_event.longitude = 123.194
        
        # Mock reverse geocoding
        mock_api_service.reverse_geocode.return_value = "Test City"
        
        # Mock callback
        callback = Mock()
        geo_service.on_location_update = callback
        
        geo_service._handle_position(mock_event)
        
        assert geo_service.last_location == (13.621, 123.194)
        mock_api_service.reverse_geocode.assert_called_once_with(13.621, 123.194)
        callback.assert_called_once_with(13.621, 123.194, "Test City")
    
    def test_handle_position_throttles_small_changes(self, geo_service, mock_api_service):
        """Test _handle_position throttles insignificant location changes."""
        # Set initial location
        geo_service.last_location = (13.621, 123.194)
        
        # Mock small position change (< 0.001 degrees)
        mock_event = Mock()
        mock_event.latitude = 13.6211  # Very small change
        mock_event.longitude = 123.1941
        
        callback = Mock()
        geo_service.on_location_update = callback
        
        geo_service._handle_position(mock_event)
        
        # Should not trigger update due to throttling
        mock_api_service.reverse_geocode.assert_not_called()
        callback.assert_not_called()
    
    def test_handle_position_processes_significant_changes(self, geo_service, mock_api_service):
        """Test _handle_position processes significant location changes."""
        # Set initial location
        geo_service.last_location = (13.621, 123.194)
        
        # Mock significant position change (> 0.001 degrees ~111m)
        mock_event = Mock()
        mock_event.latitude = 13.625  # Significant change
        mock_event.longitude = 123.198
        
        mock_api_service.reverse_geocode.return_value = "New City"
        callback = Mock()
        geo_service.on_location_update = callback
        
        geo_service._handle_position(mock_event)
        
        # Should trigger update
        mock_api_service.reverse_geocode.assert_called_once()
        callback.assert_called_once_with(13.625, 123.198, "New City")
    
    def test_handle_error_logs_error(self, geo_service, capsys):
        """Test _handle_error logs error message."""
        error_msg = "Location permission denied"
        
        geo_service._handle_error(error_msg)
        
        # Error is logged (in real implementation, check logs)
        # For now, just verify it doesn't raise exception
    
    def test_callback_optional(self, mock_page, mock_api_service):
        """Test GeolocationService works without callback."""
        with patch('src.services.geolocation_service.APIService', return_value=mock_api_service):
            service = GeolocationService(mock_page, on_location_update=None)
            
            # Should not raise error even without callback
            mock_event = Mock()
            mock_event.latitude = 13.621
            mock_event.longitude = 123.194
            
            mock_api_service.reverse_geocode.return_value = "Test City"
            
            service._handle_position(mock_event)
    
    def test_destructor_calls_cleanup(self, geo_service):
        """Test destructor calls cleanup if not already done."""
        geo_service._is_cleaned_up = False
        
        # Trigger destructor
        geo_service.__del__()
        
        assert geo_service._is_cleaned_up is True
