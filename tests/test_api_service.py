"""
Unit tests for APIService.

Tests cover Google Places API interactions, geocoding, and static map generation.
All external API calls are mocked to ensure fast, reliable tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.api_service import APIService


@pytest.mark.unit
@pytest.mark.api
class TestAPIService:
    """Test suite for APIService."""
    
    @pytest.fixture
    def api_service(self):
        """Create APIService instance for testing."""
        return APIService()
    
    def test_initialization(self, api_service):
        """Test APIService initializes correctly."""
        assert api_service.config is not None
        assert api_service.headers["User-Agent"] == "Lakb.ai/0.5"
    
    @patch('httpx.get')
    def test_search_places_success(self, mock_get, api_service, mock_google_places_response):
        """Test successful place search."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_google_places_response
        mock_get.return_value = mock_response
        
        result = api_service.search_places(query="restaurant", location="13.621,123.194")
        
        assert result["status"] == "OK"
        assert len(result["results"]) == 1
        assert result["results"][0]["name"] == "Test Place"
    
    @patch('httpx.get')
    def test_search_places_api_error(self, mock_get, api_service):
        """Test place search handles API errors gracefully."""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_get.return_value = mock_response
        
        result = api_service.search_places(query="restaurant")
        
        assert "error" in result
    
    @patch('httpx.get')
    def test_reverse_geocode_success(self, mock_get, api_service):
        """Test successful reverse geocoding."""
        # Mock geocoding response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "address_components": [
                        {
                            "long_name": "Test City",
                            "types": ["locality", "political"]
                        }
                    ],
                    "formatted_address": "Test City, Test Province"
                }
            ],
            "status": "OK"
        }
        mock_get.return_value = mock_response
        
        city = api_service.reverse_geocode(13.621, 123.194)
        
        assert city == "Test City"
    
    @patch('httpx.get')
    def test_reverse_geocode_no_results(self, mock_get, api_service):
        """Test reverse geocoding with no results."""
        # Mock no results response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [], "status": "ZERO_RESULTS"}
        mock_get.return_value = mock_response
        
        city = api_service.reverse_geocode(0, 0)
        
        assert city is None
    
    @patch('httpx.get')
    def test_geocode_success(self, mock_get, api_service):
        """Test successful address geocoding."""
        # Mock geocoding response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "geometry": {
                        "location": {
                            "lat": 13.621,
                            "lng": 123.194
                        }
                    },
                    "address_components": [
                        {
                            "long_name": "Test City",
                            "types": ["locality", "political"]
                        }
                    ],
                    "formatted_address": "Test City, Test Province"
                }
            ],
            "status": "OK"
        }
        mock_get.return_value = mock_response
        
        result = api_service.geocode("Test City")
        
        assert result["lat"] == 13.621
        assert result["lng"] == 123.194
        assert result["city"] == "Test City"
    
    def test_get_photo_url(self, api_service):
        """Test photo URL generation."""
        photo_ref = "places/ChIJN1t_tDeuEmsRUsoyG83frY4/photos/test123"
        
        url = api_service.get_photo_url(photo_ref, max_width=400)
        
        assert "https://places.googleapis.com/v1/" in url
        assert photo_ref in url
        assert "maxWidthPx=400" in url
    
    def test_get_static_map_url(self, api_service):
        """Test static map URL generation."""
        url = api_service.get_static_map_url(13.621, 123.194, width=600, height=300, zoom=15)
        
        assert "https://maps.googleapis.com/maps/api/staticmap" in url
        assert "center=13.621,123.194" in url
        assert "zoom=15" in url
        assert "size=600x300" in url
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_get_place_details_success(self, mock_get, api_service, mock_place_details_response):
        """Test successful place details retrieval."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_place_details_response
        mock_get.return_value = mock_response
        
        result = await api_service.get_place_details("ChIJN1t_tDeuEmsRUsoyG83frY4")
        
        assert result is not None
        assert "name" in result  # The method returns mapped result with 'name' not 'displayName'
        assert result["name"] == "Test Place"
        assert result["rating"] == 4.5
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_get_nearby_places_success(self, mock_post, api_service):
        """Test successful nearby places search."""
        # Mock nearby places response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "id": "ChIJTest1",
                    "displayName": {"text": "Test Place 1"},
                    "formattedAddress": "123 Test St",
                    "location": {"latitude": 13.621, "longitude": 123.194}
                }
            ]
        }
        mock_post.return_value = mock_response
        
        results = await api_service.get_nearby_places(13.621, 123.194, radius=5000)
        
        assert len(results) == 1
        assert results[0]["name"] == "Test Place 1"
    
    @pytest.mark.asyncio
    async def test_cleanup(self, api_service):
        """Test cleanup closes async client."""
        # Set up a mock client
        mock_client = Mock()
        mock_client.aclose = Mock(return_value=None) # Mock aclose to be awaitable
        api_service._async_client = mock_client
        
        await api_service.cleanup()
        
        mock_client.aclose.assert_called_once() # Verify aclose was called
        assert api_service._async_client is None


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.slow
class TestAPIServiceAsync:
    """Test suite for async operations in APIService."""
    
    @pytest.fixture
    def api_service(self):
        """Create APIService instance for testing."""
        return APIService()
    
    def test_get_async_client_creates_client(self, api_service):
        """Test async client creation."""
        assert api_service._async_client is None
        
        client = api_service._get_async_client()
        
        assert client is not None
        assert api_service._async_client is not None
    
    def test_get_async_client_reuses_existing(self, api_service):
        """Test async client is reused."""
        client1 = api_service._get_async_client()
        client2 = api_service._get_async_client()
        
        assert client1 is client2
