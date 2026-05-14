"""
Pytest configuration and shared fixtures for LAKb.ai testing.

This module provides common test fixtures for mocking external dependencies
like Supabase, Google APIs, and Flet page objects.
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

# Add src directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_page():
    """Mock Flet Page object for UI-related tests."""
    page = Mock()
    page.client_storage = Mock()
    page.client_storage.get = Mock(return_value=None)
    page.client_storage.set = Mock()
    page.client_storage.remove = Mock()
    page.overlay = []
    page.update = Mock()
    page.session = Mock()
    page.session.get = Mock(return_value=None)
    page.session.set = Mock()
    page.platform = "linux"
    return page


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client with common methods."""
    client = Mock()
    
    # Mock auth methods
    client.auth = Mock()
    client.auth.get_user = Mock(return_value=Mock(user=None))
    client.auth.sign_in_with_password = Mock()
    client.auth.sign_up = Mock()
    client.auth.sign_out = Mock()
    client.auth.get_session = Mock(return_value=None)
    client.auth.set_session = Mock()
    client.auth.sign_in_with_oauth = Mock()
    client.auth.exchange_code_for_session = Mock()
    client.auth.reset_password_for_email = Mock()
    
    # Mock table methods
    client.table = Mock()
    client.from_ = Mock()
    
    # Mock storage methods
    client.storage = Mock()
    
    return client


@pytest.fixture
def mock_supabase_user():
    """Mock authenticated Supabase user."""
    user = Mock()
    user.id = "test-user-id-123"
    user.email = "test@example.com"
    user.user_metadata = {
        "full_name": "Test User",
        "avatar_url": "https://example.com/avatar.jpg"
    }
    return user


@pytest.fixture
def mock_supabase_session():
    """Mock Supabase session."""
    session = Mock()
    session.access_token = "mock-access-token"
    session.refresh_token = "mock-refresh-token"
    session.expires_at = 1234567890
    session.user = Mock()
    session.user.id = "test-user-id-123"
    return session


@pytest.fixture
def mock_google_places_response():
    """Mock Google Places API response."""
    return {
        "results": [
            {
                "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
                "name": "Test Place",
                "formatted_address": "123 Test St, Test City, TC 12345",
                "geometry": {
                    "location": {
                        "lat": 13.621,
                        "lng": 123.194
                    }
                },
                "rating": 4.5,
                "user_ratings_total": 100,
                "types": ["restaurant", "food"],
                "photos": [
                    {
                        "name": "places/ChIJN1t_tDeuEmsRUsoyG83frY4/photos/test123"
                    }
                ]
            }
        ],
        "status": "OK"
    }


@pytest.fixture
def mock_place_details_response():
    """Mock Google Place Details API response."""
    return {
        "result": {
            "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
            "displayName": {"text": "Test Place"},
            "formattedAddress": "123 Test St, Test City, TC 12345",
            "location": {
                "latitude": 13.621,
                "longitude": 123.194
            },
            "rating": 4.5,
            "userRatingCount": 100,
            "types": ["restaurant", "food"],
            "photos": [
                {
                    "name": "places/ChIJN1t_tDeuEmsRUsoyG83frY4/photos/test123"
                }
            ],
            "editorialSummary": {"text": "A great test place"}
        }
    }


@pytest.fixture
def mock_weather_response():
    """Mock OpenWeatherMap API response."""
    return {
        "dt": 1234567890,
        "main": {
            "temp": 28.5,
            "feels_like": 30.2,
            "humidity": 75
        },
        "weather": [
            {
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d"
            }
        ],
        "wind": {
            "speed": 3.5
        }
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"days": [{"date": "2024-01-15", "places": [{"name": "Test Destination", "time": "09:00", "activity": "Visit"}]}]}'
                        }
                    ]
                }
            }
        ]
    }


@pytest.fixture
def sample_place_data():
    """Sample place data for testing."""
    return {
        "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
        "name": "Test Place",
        "address": "123 Test St, Test City",
        "lat": 13.621,
        "lng": 123.194,
        "rating": 4.5,
        "photo_url": "https://example.com/photo.jpg"
    }


@pytest.fixture
def sample_favorites_list(sample_place_data):
    """Sample list of favorite places."""
    return [
        sample_place_data,
        {
            "place_id": "ChIJTest2",
            "name": "Another Place",
            "address": "456 Another St",
            "lat": 13.622,
            "lng": 123.195,
            "rating": 4.0,
            "photo_url": "https://example.com/photo2.jpg"
        }
    ]


@pytest.fixture
def temp_favorites_file(tmp_path):
    """Create a temporary favorites.json file for testing."""
    favorites_file = tmp_path / "favorites.json"
    return str(favorites_file)


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "test-google-api-key")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-weather-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("CALENDARIFIC_API_KEY", "test-calendar-key")
    monkeypatch.setenv("OPENAQ_API_KEY", "test-openaq-key")


@pytest.fixture
def mock_httpx_client():
    """Mock httpx async client for API testing."""
    client = MagicMock()
    client.get = MagicMock()
    client.post = MagicMock()
    client.aclose = MagicMock()
    return client


@pytest.fixture
def mock_api_service():
    """Mock APIService for integration tests."""
    service = Mock()
    service.search_places = Mock(return_value={"results": [], "status": "OK"})
    service.reverse_geocode = Mock(return_value="Test City")
    service.geocode = Mock(return_value={"lat": 13.621, "lng": 123.194, "city": "Test City"})
    service.get_photo_url = Mock(return_value="https://example.com/photo.jpg")
    service.get_static_map_url = Mock(return_value="https://example.com/map.jpg")
    service.get_place_details = Mock(return_value={})
    service.get_nearby_places = Mock(return_value=[])
    return service


@pytest.fixture
def mock_auth_service():
    """Mock AuthService for integration tests."""
    service = Mock()
    service.get_user = Mock(return_value=None)
    service.sign_in_with_password = Mock()
    service.sign_up = Mock()
    service.sign_out = Mock()
    service.get_session = Mock(return_value=None)
    return service


@pytest.fixture
def mock_favorites_service():
    """Mock FavoritesService for integration tests."""
    service = Mock()
    service.get_favorites = Mock(return_value=[])
    service.is_favorite = Mock(return_value=False)
    service.add_favorite = Mock()
    service.remove_favorite = Mock()
    service.toggle_favorite = Mock(return_value=True)
    return service


# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Any cleanup code here
