"""
Unit tests for AIEngine.

Tests cover weather data, holidays, air quality, and trip planning with mocked external APIs.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
from src.services.ai_engine import AIEngine


@pytest.mark.unit
@pytest.mark.slow
class TestAIEngine:
    """Test suite for AIEngine."""
    
    @pytest.fixture
    def ai_engine(self, mock_api_service):
        """Create AIEngine instance with mocked dependencies."""
        with patch('src.services.ai_engine.APIService', return_value=mock_api_service):
            engine = AIEngine()
            return engine
    
    def test_initialization(self, ai_engine):
        """Test AIEngine initializes correctly."""
        assert ai_engine.config is not None
        assert ai_engine.api_service is not None
    
    @pytest.mark.asyncio
    async def test_get_weather_data_success(self, ai_engine, mock_weather_response):
        """Test successful weather data retrieval."""
        # Mock the async client get method
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_weather_response
        
        with patch.object(ai_engine, '_get_async_client') as mock_client_getter:
            mock_client = Mock()
            mock_client.get = Mock(return_value=mock_response)
            mock_client_getter.return_value = mock_client
            
            weather = await ai_engine.get_weather_data("Test City", date(2024, 1, 15))
            assert weather is not None
        assert weather["main"]["temp"] == 28.5
    
    @pytest.mark.asyncio
    async def test_get_weather_data_api_error(self, ai_engine):
        """Test weather data retrieval handles API errors."""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch.object(ai_engine, '_get_async_client') as mock_client_getter:
            mock_client = Mock()
            mock_client.get = Mock(return_value=mock_response)
            mock_client_getter.return_value = mock_client
            
            weather = await ai_engine.get_weather_data("Invalid City", date(2024, 1, 15))
        
        assert weather is None
    
    @pytest.mark.asyncio
    async def test_get_holidays_success(self, ai_engine):
        """Test successful holidays data retrieval."""
        # Mock holidays API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": {
                "holidays": [
                    {
                        "name": "Test Holiday",
                        "date": {"iso": "2024-01-15"},
                        "type": ["National holiday"]
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        results = await ai_engine.get_holidays("PH", date(2024, 1, 15))
        
        assert len(holidays) == 1
        assert holidays[0]["name"] == "Test Holiday"
    
    @pytest.mark.asyncio
    async def test_get_air_quality_success(self, ai_engine):
        """Test successful air quality data retrieval."""
        # Mock air quality API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "parameter": "pm25",
                    "value": 15.5,
                    "unit": "µg/m³"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        air_quality = await ai_engine.get_air_quality("Test City")
        
        assert air_quality is not None
        assert len(air_quality) > 0
    
    @pytest.mark.asyncio
    async def test_generate_itinerary_with_gemini_success(self, ai_engine, mock_gemini_response):
        """Test successful itinerary generation with Gemini."""
        # Mock Gemini API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_gemini_response
        mock_post.return_value = mock_response
        
        itinerary = ai_engine.generate_itinerary_with_gemini(
            destination="Test City",
            date_from=date(2024, 1, 15),
            date_to=date(2024, 1, 17),
            budget_min="1000",
            budget_max="5000",
            travel_style="Adventure",
            time_preference="Morning",
            activity="Sightseeing",
            dietary="None",
            weather_data=[{"date": "2024-01-15", "temp": 28}],
            holidays=[],
            air_quality=None
        )
        
        assert itinerary is not None
        assert "days" in itinerary
    
    @pytest.mark.asyncio
    async def test_generate_itinerary_handles_api_error(self, ai_engine):
        """Test itinerary generation handles API errors."""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        itinerary = ai_engine.generate_itinerary_with_gemini(
            destination="Test City",
            date_from=date(2024, 1, 15),
            date_to=date(2024, 1, 17),
            budget_min="1000",
            budget_max="5000",
            travel_style="Adventure",
            time_preference="Morning",
            activity="Sightseeing",
            dietary="None",
            weather_data=[],
            holidays=[],
            air_quality=None
        )
        
        assert itinerary is None
    
    def test_enrich_places_with_google(self, ai_engine, mock_api_service):
        """Test place enrichment with Google Places data."""
        # Mock itinerary with places
        itinerary = {
            "days": [
                {
                    "date": "2024-01-15",
                    "places": [
                        {"name": "Test Place", "time": "09:00"}
                    ]
                }
            ]
        }
        
        # Mock Google Places search
        mock_api_service.search_places.return_value = {
            "results": [
                {
                    "place_id": "test123",
                    "name": "Test Place",
                    "photos": [{"name": "photo123"}]
                }
            ]
        }
        mock_api_service.get_photo_url.return_value = "https://example.com/photo.jpg"
        
        enriched = ai_engine.enrich_places_with_google(itinerary, "Test City")
        
        assert enriched is not None
        assert len(enriched["days"]) == 1
    
    @pytest.mark.asyncio
    async def test_cleanup(self, ai_engine):
        """Test cleanup closes async client."""
        mock_client = Mock()
        mock_async_close = Mock(return_value=None)
        mock_client.aclose = mock_async_close
        ai_engine._async_client = mock_client
        
        await ai_engine.cleanup()
        
        assert ai_engine._async_client is None


@pytest.mark.unit
@pytest.mark.integration
class TestAIEngineIntegration:
    """Integration tests for complete trip plan generation."""
    
    @pytest.fixture
    def ai_engine(self, mock_api_service):
        """Create AIEngine instance with mocked dependencies."""
        with patch('src.services.ai_engine.APIService', return_value=mock_api_service):
            engine = AIEngine()
            return engine
    
    @patch('httpx.get')
    @patch('httpx.post')
    def test_generate_plan_end_to_end(self, mock_post, mock_get, ai_engine, mock_api_service,
                                     mock_weather_response, mock_gemini_response, mock_supabase_client):
        """Test complete trip plan generation workflow."""
        # Mock weather API
        weather_resp = Mock()
        weather_resp.status_code = 200
        weather_resp.json.return_value = mock_weather_response
        
        # Mock Gemini API
        gemini_resp = Mock()
        gemini_resp.status_code = 200
        gemini_resp.json.return_value = mock_gemini_response
        
        mock_get.return_value = weather_resp
        mock_post.return_value = gemini_resp
        
        # Mock Supabase save
        with patch('src.services.ai_engine.get_supabase_client', return_value=mock_supabase_client):
            mock_table = Mock()
            mock_insert = Mock()
            mock_execute = Mock()
            mock_execute.data = [{"id": "plan-123"}]
            mock_insert.execute.return_value = mock_execute
            mock_table.insert.return_value = mock_insert
            mock_supabase_client.table.return_value = mock_table
            
            plan = ai_engine.generate_plan(
                user_id="user-123",
                destination="Test City",
                date_from=date(2024, 1, 15),
                date_to=date(2024, 1, 17),
                budget_min="1000",
                budget_max="5000",
                travel_style="Adventure",
                time_preference="Morning",
                activity="Sightseeing",
                dietary="None"
            )
            
            assert plan is not None
