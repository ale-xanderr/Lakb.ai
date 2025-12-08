import httpx
import json
import datetime
from typing import Dict, List, Optional, Any
from core.config import Config
from core.supabase_client import get_supabase_client
from services.api_service import APIService


class AIEngine:
    """
    Service for generating trip plans using AI (Gemini) and various APIs (OpenWeather, Calendarific, OpenAQ).
    """
    
    def __init__(self):
        self.config = Config
        self.api_service = APIService()
        self.supabase = get_supabase_client()
        self._async_client = None
    
    def _get_async_client(self):
        """Get or create a shared async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=60.0)
        return self._async_client
    
    async def cleanup(self):
        """Clean up resources."""
        if self._async_client is not None:
            try:
                await self._async_client.aclose()
            except Exception as e:
                print(f"Error closing async client: {e}")
            finally:
                self._async_client = None
    
    async def get_weather_data(self, destination: str, date: datetime.date) -> Optional[Dict]:
        """
        Fetch weather data for a destination and date using OpenWeatherMap API.
        
        Args:
            destination: Destination name or city
            date: Date to get weather for
            
        Returns:
            Weather data dict or None if error
        """
        if not self.config.OPENWEATHER_API_KEY:
            print("Warning: OPENWEATHER_API_KEY not configured")
            return None
        
        try:
            # First, get coordinates for the destination
            # Try with more specific location if initial geocode fails
            geocode_data = self.api_service.geocode(destination)
            if not geocode_data:
                # Try with country suffix for Philippines destinations
                if "Philippines" not in destination and "PH" not in destination:
                    geocode_data = self.api_service.geocode(f"{destination}, Philippines")
                if not geocode_data:
                    print(f"Could not geocode destination: {destination}")
                    return None
            
            lat = geocode_data["lat"]
            lng = geocode_data["lng"]
            
            # Get weather forecast (using 5-day forecast API)
            url = f"{self.config.OPENWEATHER_BASE_URL}/forecast"
            params = {
                "lat": lat,
                "lon": lng,
                "appid": self.config.OPENWEATHER_API_KEY,
                "units": "metric"
            }
            
            client = self._get_async_client()
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Find forecast for the specific date
            target_date_str = date.strftime("%Y-%m-%d")
            for item in data.get("list", []):
                item_date = datetime.datetime.fromtimestamp(item["dt"]).date()
                if item_date == date:
                    return {
                        "date": target_date_str,
                        "temp": item["main"]["temp"],
                        "feels_like": item["main"]["feels_like"],
                        "description": item["weather"][0]["description"],
                        "icon": item["weather"][0]["icon"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item.get("wind", {}).get("speed", 0)
                    }
            
            # If exact date not found, return current weather
            current_url = f"{self.config.OPENWEATHER_BASE_URL}/weather"
            current_response = await client.get(current_url, params=params)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            return {
                "date": target_date_str,
                "temp": current_data["main"]["temp"],
                "feels_like": current_data["main"]["feels_like"],
                "description": current_data["weather"][0]["description"],
                "icon": current_data["weather"][0]["icon"],
                "humidity": current_data["main"]["humidity"],
                "wind_speed": current_data.get("wind", {}).get("speed", 0)
            }
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    async def get_holidays(self, country_code: str, date: datetime.date) -> List[Dict]:
        """
        Fetch holidays/events for a date using Calendarific API.
        
        Args:
            country_code: ISO country code (e.g., "PH" for Philippines)
            date: Date to check for holidays
            
        Returns:
            List of holiday/event dicts
        """
        if not self.config.CALENDARIFIC_API_KEY:
            print("Warning: CALENDARIFIC_API_KEY not configured")
            return []
        
        try:
            url = f"{self.config.CALENDARIFIC_BASE_URL}/holidays"
            params = {
                "api_key": self.config.CALENDARIFIC_API_KEY,
                "country": country_code,
                "year": date.year,
                "month": date.month,
                "day": date.day
            }
            
            client = self._get_async_client()
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            holidays = []
            for holiday in data.get("response", {}).get("holidays", []):
                holidays.append({
                    "name": holiday.get("name"),
                    "description": holiday.get("description"),
                    "type": holiday.get("type", [])
                })
            
            return holidays
            
        except Exception as e:
            print(f"Error fetching holidays: {e}")
            return []
    
    async def get_air_quality(self, destination: str) -> Optional[Dict]:
        """
        Fetch air quality data for a destination using OpenAQ API.
        
        Args:
            destination: Destination name or city
            
        Returns:
            Air quality data dict or None if error
        """
        if not self.config.OPENAQ_API_KEY:
            print("Warning: OPENAQ_API_KEY not configured")
            return None
        
        try:
            # Get coordinates for the destination
            # Try with more specific location if initial geocode fails
            geocode_data = self.api_service.geocode(destination)
            if not geocode_data:
                # Try with country suffix for Philippines destinations
                if "Philippines" not in destination and "PH" not in destination:
                    geocode_data = self.api_service.geocode(f"{destination}, Philippines")
                if not geocode_data:
                    print(f"Could not geocode destination: {destination}")
                    return None
            
            lat = geocode_data["lat"]
            lng = geocode_data["lng"]
            
            # OpenAQ v3 API endpoint
            url = f"{self.config.OPENAQ_BASE_URL}/locations"
            params = {
                "coordinates": f"{lat},{lng}",
                "radius": 10000,  # 10km radius
                "limit": 1
            }
            
            headers = {
                "X-API-Key": self.config.OPENAQ_API_KEY
            }
            
            client = self._get_async_client()
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results") and len(data["results"]) > 0:
                location = data["results"][0]
                # Get latest measurements
                location_id = location.get("id")
                if location_id:
                    measurements_url = f"{self.config.OPENAQ_BASE_URL}/locations/{location_id}/latest"
                    measurements_response = await client.get(measurements_url, headers=headers)
                    measurements_response.raise_for_status()
                    measurements_data = measurements_response.json()
                    
                    if measurements_data.get("results") and len(measurements_data["results"]) > 0:
                        latest = measurements_data["results"][0]
                        return {
                            "aqi": latest.get("measurements", [{}])[0].get("value") if latest.get("measurements") else None,
                            "parameter": latest.get("measurements", [{}])[0].get("parameter") if latest.get("measurements") else None,
                            "location": location.get("name")
                        }
            
            return None
            
        except Exception as e:
            print(f"Error fetching air quality: {e}")
            return None
    
    async def generate_itinerary_with_gemini(
        self,
        destination: str,
        date_from: datetime.date,
        date_to: datetime.date,
        budget_min: str,
        budget_max: str,
        travel_style: str,
        time_preference: str,
        activity: str,
        dietary: str,
        weather_data: List[Dict],
        holidays: List[Dict],
        air_quality: Optional[Dict]
    ) -> Optional[Dict]:
        """
        Generate itinerary using Gemini API with context from weather, holidays, and air quality.
        
        Args:
            destination: Destination name
            date_from: Start date
            date_to: End date
            budget_min: Minimum budget
            budget_max: Maximum budget
            travel_style: Travel style preference
            time_preference: Time preference
            activity: Selected activity
            dietary: Dietary requirements
            weather_data: List of weather data for each day
            holidays: List of holidays during the trip
            air_quality: Air quality data
            
        Returns:
            Generated itinerary dict with places per day
        """
        if not self.config.GEMINI_API_KEY:
            print("Error: GEMINI_API_KEY not configured")
            return None
        
        try:
            # Calculate number of days
            num_days = (date_to - date_from).days + 1
            
            # Build context prompt
            weather_context = ""
            if weather_data:
                weather_context = "\nWeather Forecast:\n"
                for w in weather_data:
                    weather_context += f"- {w.get('date')}: {w.get('description')}, {w.get('temp')}°C\n"
            
            holidays_context = ""
            if holidays:
                holidays_context = "\nHolidays/Events during trip:\n"
                for h in holidays:
                    holidays_context += f"- {h.get('name')}: {h.get('description', '')}\n"
            
            air_quality_context = ""
            if air_quality:
                aqi = air_quality.get("aqi")
                if aqi:
                    air_quality_context = f"\nAir Quality: {air_quality.get('parameter', 'AQI')} = {aqi}\n"
            
            prompt = f"""Generate a {num_days}-day travel itinerary for {destination} from {date_from} to {date_to}.

Travel Preferences:
- Budget: ₱{budget_min} - ₱{budget_max}
- Travel Style: {travel_style}
- Time Preference: {time_preference}
- Activity Interest: {activity}
- Dietary Requirements: {dietary}

{weather_context}
{holidays_context}
{air_quality_context}

Please provide exactly 3 recommended places to visit per day. For each day, provide:
1. Day number
2. Three places with:
   - Place name (must be real, searchable places in {destination})
   - Brief description (1-2 sentences)
   - Suggested time to visit
   - Why it fits the travel style and preferences

Format the response as JSON with this structure:
{{
  "itinerary": [
    {{
      "day": 1,
      "date": "{date_from}",
      "places": [
        {{
          "name": "Place Name",
          "description": "Brief description",
          "suggested_time": "Morning/Afternoon/Evening",
          "reason": "Why this place fits"
        }},
        ...
      ]
    }},
    ...
  ],
  "tips": [
    "Travel tip 1",
    "Travel tip 2",
    ...
  ]
}}

Return ONLY valid JSON, no additional text."""
            
            # Call Gemini API
            # Format: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
            model_name = "gemini-2.5-flash"
            base_url = self.config.GEMINI_BASE_URL.strip() if self.config.GEMINI_BASE_URL else "https://generativelanguage.googleapis.com/v1beta"
            url = f"{base_url}/models/{model_name}:generateContent"
            
            if not self.config.GEMINI_API_KEY:
                print("Error: GEMINI_API_KEY not configured")
                return None
            
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.config.GEMINI_API_KEY.strip()
            }
            body = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            print(f"DEBUG: Calling Gemini API at: {url}")
            print(f"DEBUG: Using API key: {self.config.GEMINI_API_KEY[:10]}...")
            
            client = self._get_async_client()
            response = await client.post(url, headers=headers, json=body)
            
            # Log response for debugging
            if response.status_code != 200:
                print(f"DEBUG: Gemini API error - Status: {response.status_code}")
                print(f"DEBUG: Response: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            
            # Extract text from response
            # Response structure: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        text_content = parts[0]["text"]
                    else:
                        print("Error: No text in Gemini response parts")
                        return None
                else:
                    print("Error: No content in Gemini response candidate")
                    return None
            else:
                print("Error: No candidates in Gemini response")
                return None
            
            # Try to extract JSON from the response (might have markdown code blocks)
            text_content = text_content.strip()
            if text_content.startswith("```json"):
                text_content = text_content[7:]
            if text_content.startswith("```"):
                text_content = text_content[3:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]
            text_content = text_content.strip()
            
            # Parse JSON
            itinerary_data = json.loads(text_content)
            return itinerary_data
                
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini JSON response: {e}")
            return None
        except Exception as e:
            print(f"Error generating itinerary with Gemini: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def enrich_places_with_google(self, itinerary: Dict, destination: str) -> Dict:
        """
        Enrich itinerary places with Google Places API data (photos, details).
        
        Args:
            itinerary: Itinerary dict with places
            destination: Destination name for location bias
            
        Returns:
            Enriched itinerary with place details
        """
        try:
            # Get destination coordinates for location bias
            geocode_data = self.api_service.geocode(destination)
            location_bias = None
            if geocode_data:
                location_bias = f"{geocode_data['lat']},{geocode_data['lng']}"
            
            enriched_itinerary = {"itinerary": [], "tips": itinerary.get("tips", [])}
            
            for day_data in itinerary.get("itinerary", []):
                enriched_day = {
                    "day": day_data.get("day"),
                    "date": day_data.get("date"),
                    "places": []
                }
                
                for place in day_data.get("places", []):
                    place_name = place.get("name")
                    if not place_name:
                        enriched_day["places"].append(place)
                        continue
                    
                    # Search for the place using Google Places API
                    search_query = f"{place_name} {destination}"
                    search_result = self.api_service.search_places(
                        query=search_query,
                        location=location_bias
                    )
                    
                    enriched_place = place.copy()
                    
                    if "results" in search_result and len(search_result["results"]) > 0:
                        # Use the first result
                        place_result = search_result["results"][0]
                        enriched_place["place_id"] = place_result.get("place_id")
                        enriched_place["formatted_address"] = place_result.get("formatted_address")
                        enriched_place["rating"] = place_result.get("rating")
                        
                        # Get photo URL if available
                        photos = place_result.get("photos", [])
                        if photos and len(photos) > 0:
                            photo_ref = photos[0].get("photo_reference")
                            if photo_ref:
                                enriched_place["image_url"] = self.api_service.get_photo_url(photo_ref, max_width=800)
                    else:
                        print(f"Warning: Could not find place '{place_name}' in Google Places")
                    
                    enriched_day["places"].append(enriched_place)
                
                enriched_itinerary["itinerary"].append(enriched_day)
            
            return enriched_itinerary
            
        except Exception as e:
            print(f"Error enriching places with Google: {e}")
            import traceback
            traceback.print_exc()
            return itinerary  # Return original if enrichment fails
    
    async def generate_plan(
        self,
        user_id: str,
        destination: str,
        date_from: datetime.date,
        date_to: datetime.date,
        budget_min: str,
        budget_max: str,
        travel_style: str,
        time_preference: str,
        activity: str,
        dietary: str,
        country_code: str = "PH"
    ) -> Optional[Dict]:
        """
        Main method to generate a complete trip plan.
        
        Args:
            user_id: User ID for saving the plan
            destination: Destination name
            date_from: Start date
            date_to: End date
            budget_min: Minimum budget
            budget_max: Maximum budget
            travel_style: Travel style preference
            time_preference: Time preference
            activity: Selected activity
            dietary: Dietary requirements
            country_code: ISO country code for holidays (default: PH)
            
        Returns:
            Generated plan dict with id, or None if error
        """
        try:
            print(f"Starting plan generation for {destination}...")
            
            # 1. Fetch weather data for each day
            print("Fetching weather data...")
            weather_data = []
            current_date = date_from
            while current_date <= date_to:
                weather = await self.get_weather_data(destination, current_date)
                if weather:
                    weather_data.append(weather)
                current_date += datetime.timedelta(days=1)
            
            # 2. Fetch holidays for the date range
            print("Fetching holidays...")
            all_holidays = []
            current_date = date_from
            while current_date <= date_to:
                holidays = await self.get_holidays(country_code, current_date)
                all_holidays.extend(holidays)
                current_date += datetime.timedelta(days=1)
            
            # 3. Fetch air quality
            print("Fetching air quality data...")
            air_quality = await self.get_air_quality(destination)
            
            # 4. Generate itinerary with Gemini
            print("Generating itinerary with Gemini AI...")
            itinerary = await self.generate_itinerary_with_gemini(
                destination=destination,
                date_from=date_from,
                date_to=date_to,
                budget_min=budget_min,
                budget_max=budget_max,
                travel_style=travel_style,
                time_preference=time_preference,
                activity=activity,
                dietary=dietary,
                weather_data=weather_data,
                holidays=all_holidays,
                air_quality=air_quality
            )
            
            if not itinerary:
                print("Error: Failed to generate itinerary")
                return None
            
            # 5. Enrich places with Google Places API
            print("Enriching places with Google Places API...")
            enriched_itinerary = await self.enrich_places_with_google(itinerary, destination)
            
            # 6. Prepare plan data for database
            plan_data = {
                "destination": destination,
                "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat(),
                "budget_min": budget_min,
                "budget_max": budget_max,
                "travel_style": travel_style,
                "time_preference": time_preference,
                "activity": activity,
                "dietary": dietary,
                "itinerary": enriched_itinerary.get("itinerary", []),
                "tips": enriched_itinerary.get("tips", []),
                "weather_data": weather_data,
                "holidays": all_holidays,
                "air_quality": air_quality
            }
            
            # Generate title and description
            num_days = (date_to - date_from).days + 1
            title = f"{num_days}-Day Trip to {destination}"
            description = f"{travel_style} trip exploring {activity.lower()} activities"
            
            # Get image URL from first place if available
            image_url = None
            if enriched_itinerary.get("itinerary") and len(enriched_itinerary["itinerary"]) > 0:
                first_day = enriched_itinerary["itinerary"][0]
                if first_day.get("places") and len(first_day["places"]) > 0:
                    first_place = first_day["places"][0]
                    image_url = first_place.get("image_url")
            
            # 7. Save to Supabase (create placeholder first, then update)
            print("Saving plan to database...")
            if not self.supabase:
                print("Error: Supabase client not available")
                return None
            
            try:
                # First, create a placeholder plan with generating status
                placeholder_data = {
                    "destination": destination,
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat(),
                    "budget_min": budget_min,
                    "budget_max": budget_max,
                    "travel_style": travel_style,
                    "time_preference": time_preference,
                    "activity": activity,
                    "dietary": dietary,
                    "status": "generating",
                    "itinerary": [],
                    "tips": []
                }
                
                insert_response = self.supabase.table("plans").insert({
                    "user_id": user_id,
                    "title": title,
                    "description": description,
                    "image_url": None,  # Will be updated later
                    "data": placeholder_data
                }).execute()
                
                if not insert_response.data or len(insert_response.data) == 0:
                    print("Error: No data returned from Supabase insert")
                    return None
                
                plan_id = insert_response.data[0]["id"]
                print(f"Placeholder plan created with ID: {plan_id}")
                
                # Now update with full data
                plan_data["status"] = "completed"
                update_response = self.supabase.table("plans").update({
                    "title": title,
                    "description": description,
                    "image_url": image_url,
                    "data": plan_data
                }).eq("id", plan_id).execute()
                
                if update_response.data and len(update_response.data) > 0:
                    print(f"Plan updated successfully with ID: {plan_id}")
                    return {
                        "id": plan_id,
                        "title": title,
                        "description": description,
                        "image_url": image_url,
                        "data": plan_data
                    }
                else:
                    print("Warning: Plan created but update failed")
                    return {
                        "id": plan_id,
                        "title": title,
                        "description": description,
                        "image_url": None,
                        "data": placeholder_data
                    }
                    
            except Exception as e:
                print(f"Error saving plan to database: {e}")
                import traceback
                traceback.print_exc()
                return None
                
        except Exception as e:
            print(f"Error generating plan: {e}")
            import traceback
            traceback.print_exc()
            return None
