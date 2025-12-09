"""
Integration tests for places search workflows.

Tests cover complete place search and discovery flows.
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.integration
@pytest.mark.api
class TestPlacesFlows:
    """Integration tests for places search workflows."""
    
    @pytest.fixture
    def api_service(self):
        """Create APIService instance."""
        from src.services.api_service import APIService
        return APIService()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_search_and_get_details_flow(self, mock_client_class, api_service, 
                                        mock_google_places_response, mock_place_details_response):
        """Test searching places and getting details."""
        # Step 1: Search for places (sync method)
        with patch('httpx.get') as mock_get:
            search_response = Mock()
            search_response.status_code = 200
            search_response.json.return_value = mock_google_places_response
            mock_get.return_value = search_response
            
            search_results = api_service.search_places(query="restaurant in test city")
            
            assert search_results["status"] == "OK"
            assert len(search_results["results"]) > 0
        
        # Step 2: Get details for first result (async method)
        place_id = search_results["results"][0]["place_id"]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_place_details_response
        
        with patch.object(api_service, '_get_async_client') as mock_client_getter:
            mock_client = Mock()
            mock_client.get = Mock(return_value=mock_response)
            mock_client_getter.return_value = mock_client
            
            details = await api_service.get_place_details(place_id)
            
            assert details is not None
    
    def test_geocode_and_search_flow(self, api_service, mock_google_places_response):
        """Test geocoding address then searching nearby."""
        # Step 1: Geocode address (sync method)
        geocode_response = Mock()
        geocode_response.status_code = 200
        geocode_response.json.return_value = {
            "results": [{
                "geometry": {"location": {"lat": 13.621, "lng": 123.194}},
                "address_components": [{"long_name": "Test City", "types": ["locality"]}],
                "formatted_address": "Test City"
            }],
            "status": "OK"
        }
        
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.get.return_value = geocode_response
            mock_client_class.return_value.__enter__.return_value = mock_client
            
            location = api_service.geocode("Test City, Philippines")
        
        assert location is not None
        assert "lat" in location
        assert "lng" in location
        
        # Step 2: Search places near this location (sync method)
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = mock_google_places_response
        
        with patch('httpx.get') as mock_get:
            mock_get.return_value = search_response
            
            location_str = f"{location['lat']},{location['lng']}"
            places = api_service.search_places(query="restaurant", location=location_str)
            
            assert places["status"] == "OK"
    
    @pytest.mark.asyncio
    async def test_nearby_places_discovery_flow(self, api_service):
        """Test discovering nearby places around a location."""
        # Mock nearby places response 
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "places": [
                {
                    "id": "ChIJTest1",
                    "displayName": {"text": "Nearby Place 1"},
                    "formattedAddress": "123 Near St",
                    "location": {"latitude": 13.622, "longitude": 123.195}
                }
            ]
        }
        
        with patch.object(api_service, '_get_async_client') as mock_client_getter:
            mock_client = Mock()
            mock_client.post = Mock(return_value=mock_response)
            mock_client_getter.return_value = mock_client
            
            nearby = await api_service.get_nearby_places(13.621, 123.194, radius=5000)
            
            assert len(nearby) == 1
            assert nearby[0]["name"] == "Nearby Place 1"
    
    def test_reverse_geocode_flow(self, api_service):
        """Test converting coordinates to address."""
        # Mock reverse geocode response (sync method uses httpx.Client context manager)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{
                "address_components": [
                    {"long_name": "Test City", "types": ["locality"]},
                    {"long_name": "Test Province", "types": ["administrative_area_level_1"]}
                ],
                "formatted_address": "Test City, Test Province"
            }],
            "status": "OK"
        }
        
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__enter__.return_value = mock_client
            
            # Reverse geocode
            city = api_service.reverse_geocode(13.621, 123.194)
            
            assert city == "Test City"


@pytest.mark.integration
class TestPlacesWithFavorites:
    """Integration tests combining places search with favorites."""
    
    @pytest.fixture
    def services(self, mock_supabase_client):
        """Create both API and Favorites services."""
        from src.services.api_service import APIService
        from src.services.favorites_service import FavoritesService
        
        with patch('src.services.favorites_service.get_supabase_client', return_value=mock_supabase_client):
            return {
                "api": APIService(),
                "favorites": FavoritesService()
            }
    
    @patch('builtins.open', create=True)
    def test_search_and_favorite_flow(self, mock_file, services, mock_google_places_response):
        """Test searching for place and adding to favorites."""
        # Step 1: Search for place
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = mock_google_places_response
        
        with patch('httpx.get') as mock_get:
            mock_get.return_value = search_response
            results = services["api"].search_places(query="restaurant")
        
        place = results["results"][0]
        
        # Step 2: Add to favorites
        services["favorites"].client.auth.get_user.return_value = Mock(user=None)
        services["favorites"]._favorites = []
        
        services["favorites"].add_favorite({
            "place_id": place["place_id"],
            "name": place["name"],
            "address": place.get("formatted_address", place.get("address", "")),
            "lat": place["geometry"]["location"]["lat"],
            "lng": place["geometry"]["location"]["lng"]
        })
        
        # Step 3: Verify in favorites
        assert services["favorites"].is_favorite(place["place_id"]) is True
