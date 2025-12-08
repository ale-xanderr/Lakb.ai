# src/services/ai_engine.py
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from services.api_service import APIService
from services.db_manager import DBManager

logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, api: APIService, db: DBManager):
        self.api = api
        self.db = db

    def generate_trip_plan(self, location: str, duration_days: int, budget_range: str, travel_style: str, activity_preferences: str, time_preference: str, dietary_restrictions: str) -> Dict[str, Any]:
        
        context_notes = []
        
        # 1. Context Gathering
        lat, lng = None, None
        try:
            loc_data = self.api.search_places(query=location, limit=1)
            if loc_data.get("results"):
                geo = loc_data["results"][0].get("geometry", {}).get("location", {})
                lat = geo.get("lat")
                lng = geo.get("lng")
        except Exception: pass

        if self.api.config.OPENWEATHER_API_KEY:
            w = self.api.get_weather_forecast(location)
            if w: context_notes.append(f"Weather: {w}.")

        # 2. Gemini Prompt (Summary & Tips)
        prompt = (
            f"Act as a travel guide for {location}. "
            f"Context: {travel_style} style, {activity_preferences}, {budget_range} budget. "
            f"Real-time Data: {' '.join(context_notes)}. "
            f"Task: Provide two sections.\n"
            f"1. SUMMARY: A 2-sentence overview.\n"
            f"2. TIPS: Exactly 3 bullet points for travel advice."
        )
        
        raw_ai = self.api.get_ai_recommendation(prompt) or "Enjoy your trip!"
        
        # Parse Response
        ai_insight = raw_ai
        ai_tips = ["Bring a power bank.", "Stay hydrated.", "Download offline maps."]
        
        if "TIPS:" in raw_ai:
            try:
                parts = raw_ai.split("TIPS:")
                ai_insight = parts[0].replace("SUMMARY:", "").strip()
                tips_raw = parts[1].strip().split("\n")
                ai_tips = [t.strip("- *• ") for t in tips_raw if len(t.strip()) > 5][:3]
            except: pass

        # 3. Dates
        start_date = datetime.now() + timedelta(days=1)
        end_date = start_date + timedelta(days=duration_days)
        date_str = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}"

        # 4. Itinerary & Place Descriptions
        q = activity_preferences if activity_preferences else f"attractions in {location}"
        candidates = self._gather_candidates(q, location)
        
        if not candidates:
            candidates = [{"name": f"{location} City Center", "formatted_address": location, "rating": 4.5}]

        # --- FIX: Generate Descriptions for Places ---
        candidates = self._enrich_places_with_ai(candidates, location)

        daily = []
        idx = 0
        for i in range(duration_days):
            day_places = []
            for _ in range(3):
                if candidates:
                    p = candidates[idx % len(candidates)]
                    day_places.append({
                        "place_id": p.get("place_id"),
                        "name": p.get("name"),
                        "address": p.get("formatted_address"),
                        "rating": p.get("rating"),
                        # Ensure geometry is passed for the map
                        "geometry": p.get("geometry"), 
                        # Use the AI generated description
                        "description": p.get("ai_description", "A popular local spot."),
                        "photo_ref": p.get("photos")[0].get("photo_reference") if p.get("photos") else None
                    })
                    idx += 1
            daily.append({
                "day_label": f"Day {i+1}",
                "date": (start_date + timedelta(days=i)).strftime("%b %d"),
                "places": day_places
            })

        return {
            "summary_preview": {
                "destination_header": location,
                "sub_header": f"{duration_days} Days • {travel_style}",
                "dates": date_str,
                "budget_range": budget_range,
                "travel_style": travel_style,
                "activities": activity_preferences,
                "time_preference": time_preference,
                "dietary_preferences": dietary_restrictions,
                "ai_insight": ai_insight,
                "ai_tips": ai_tips
            },
            "itinerary": daily,
            # FIX: Ensure tips are accessible at root level for SummaryView
            "tips": ai_tips,
            "image_url": None
        }

    def _gather_candidates(self, query, location):
        try:
            res = self.api.search_places(query=query, location=location, limit=20)
            return res.get("results", [])
        except Exception: return []

    def _enrich_places_with_ai(self, candidates: List[Dict], location: str) -> List[Dict]:
        """Asks Gemini to describe the top 5 places briefly."""
        if not candidates: return candidates
        
        top_candidates = candidates[:6] # Limit to save tokens/time
        names = [p.get("name") for p in top_candidates]
        
        prompt = (
            f"Write a very short, engaging 1-sentence description for each of these places in {location}: "
            f"{', '.join(names)}. "
            f"Format strictly as: 'Place Name: Description'"
        )
        
        try:
            raw = self.api.get_ai_recommendation(prompt)
            desc_map = {}
            if raw:
                for line in raw.split("\n"):
                    if ":" in line:
                        parts = line.split(":", 1)
                        desc_map[parts[0].strip()] = parts[1].strip()
            
            # Map descriptions back to candidates
            for p in candidates:
                p["ai_description"] = desc_map.get(p.get("name"), "A great place to visit.")
                
        except Exception as e:
            print(f"AI Description Error: {e}")
            
        return candidates