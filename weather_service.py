import httpx
from typing import Dict, List, Any, Optional
from models import WeatherData, Location, DisasterPrediction, PreventionMeasure
from config import WEATHER_API_KEY, WEATHER_API_URL

class WeatherService:
    """Service for fetching weather data and generating prevention measures"""
    
    async def get_weather_data(self, location: str) -> WeatherData:
        """
        Fetch current weather data for a location using WeatherAPI
        """
        async with httpx.AsyncClient() as client:
            # Make request to WeatherAPI current weather endpoint
            response = await client.get(
                f"{WEATHER_API_URL}/current.json",
                params={
                    "key": WEATHER_API_KEY,
                    "q": location,
                    "aqi": "yes"  # Include air quality data
                }
            )
            
            if response.status_code != 200:
                # Handle error responses
                if response.status_code == 400:
                    raise ValueError(f"Invalid location: {location}")
                else:
                    raise Exception(f"Weather API error: {response.status_code}")
            
            # Parse response
            data = response.json()
            
            # Extract weather data
            current = data["current"]
            
            # Create WeatherData object with additional fields needed for disaster prediction
            weather_data = WeatherData(
                temperature=current["temp_c"],
                humidity=current["humidity"],
                precipitation=current["precip_mm"],
                wind_speed=current["wind_kph"] / 3.6,  # Convert km/h to m/s
                pressure=current["pressure_mb"],
                precipitation_intensity=current["precip_mm"] / 3,  # Estimated intensity
                air_quality_index=current.get("air_quality", {}).get("us-epa-index", 0),
                consecutive_dry_days=0,  # Default value
                soil_saturation=50,  # Default value 
                temperature_gradient=5,  # Default value
                urban_runoff_index=50,  # Default value
                consecutive_hot_days=1 if current["temp_c"] > 30 else 0,  # Simple estimation
                river_level_percent=50,  # Default value
                urban_density=50  # Default value
            )

            # Add extra fields if available in the API response
            extra_data = {}
            if "uv" in current:
                extra_data["uv_index"] = current["uv"]
                
            if "vis_km" in current:
                extra_data["visibility"] = current["vis_km"]
                
            # Add location data if needed
            if "location" in data:
                extra_data["country"] = data["location"].get("country")

            # Try to update the model with extra data if the fields exist
            try:
                for key, value in extra_data.items():
                    if hasattr(weather_data, key):
                        setattr(weather_data, key, value)
            except Exception as e:
                print(f"Warning: Could not set some weather attributes: {e}")
                
            return weather_data
    
    async def get_prevention_measures(self, predictions: List[DisasterPrediction]) -> Dict[str, List[PreventionMeasure]]:
        """
        Generate prevention measures based on disaster predictions
        
        Args:
            predictions: List of disaster predictions
            
        Returns:
            Dictionary mapping disaster types to lists of prevention measures
        """
        prevention_measures = {}
        
        for prediction in predictions:
            disaster_type = prediction.disaster_type
            severity = prediction.severity
            
            # Skip "None" predictions
            if disaster_type == "None":
                continue
                
            # Get appropriate measures based on disaster type and severity
            measures = self._get_measures_for_disaster(disaster_type, severity)
            
            if measures:
                prevention_measures[disaster_type] = measures
                
        return prevention_measures
    
    def _get_measures_for_disaster(self, disaster_type: str, severity: str) -> List[PreventionMeasure]:
        """Get specific prevention measures for a disaster type and severity"""
        measures = []
        
        # Flood measures
        if any(term in disaster_type.lower() for term in ["flood", "flash flood"]):
            if severity in ["Severe", "Extreme"]:
                measures.append(PreventionMeasure(
                    title="Evacuate Low-Lying Areas",
                    description="Move to higher ground immediately if you're in flood-prone areas",
                    urgency="Immediate"
                ))
                measures.append(PreventionMeasure(
                    title="Avoid Flood Waters",
                    description="Never walk or drive through flood waters. 6 inches of water can knock you down, 12 inches can float a vehicle",
                    urgency="Critical"
                ))
            
            measures.append(PreventionMeasure(
                title="Prepare Emergency Kit",
                description="Include water, non-perishable food, medications, flashlight, radio, and essential documents",
                urgency="High" if severity in ["Severe", "Extreme"] else "Medium"
            ))
            
        # Heat wave measures
        elif any(term in disaster_type.lower() for term in ["heat", "hot"]):
            if severity in ["Severe", "Extreme"]:
                measures.append(PreventionMeasure(
                    title="Stay Indoors",
                    description="Remain in air-conditioned buildings during peak heat (10am-4pm)",
                    urgency="High"
                ))
                measures.append(PreventionMeasure(
                    title="Check on Vulnerable People",
                    description="Regularly check on elderly neighbors, young children, and those with health conditions",
                    urgency="High"
                ))
            
            measures.append(PreventionMeasure(
                title="Stay Hydrated",
                description="Drink plenty of water even if you don't feel thirsty",
                urgency="High"
            ))
            
        # Storm measures
        elif any(term in disaster_type.lower() for term in ["storm", "hurricane", "typhoon", "cyclone"]):
            if severity in ["Severe", "Extreme"]:
                measures.append(PreventionMeasure(
                    title="Secure Your Home",
                    description="Board up windows, secure outdoor objects, and prepare for power outages",
                    urgency="Immediate"
                ))
                
                if "hurricane" in disaster_type.lower() or "cyclone" in disaster_type.lower():
                    measures.append(PreventionMeasure(
                        title="Evacuation Plan",
                        description="Follow local evacuation orders. Know your evacuation route and shelter locations",
                        urgency="Critical"
                    ))
            
            measures.append(PreventionMeasure(
                title="Emergency Supplies",
                description="Prepare water, food, medications, flashlight, and battery-powered radio for at least 3 days",
                urgency="High"
            ))
            
        # Tornado measures
        elif "tornado" in disaster_type.lower():
            measures.append(PreventionMeasure(
                title="Seek Shelter Immediately",
                description="Go to a basement, storm cellar, or interior room without windows on the lowest floor",
                urgency="Critical"
            ))
            measures.append(PreventionMeasure(
                title="Stay Informed",
                description="Keep a battery-powered weather radio to receive updates",
                urgency="High"
            ))
            
        # Wildfire measures
        elif any(term in disaster_type.lower() for term in ["fire", "wildfire"]):
            if severity in ["Severe", "Extreme"]:
                measures.append(PreventionMeasure(
                    title="Evacuation",
                    description="Be ready to evacuate at a moment's notice. Pack essential items in advance",
                    urgency="Critical"
                ))
            
            measures.append(PreventionMeasure(
                title="Create Defensible Space",
                description="Clear flammable vegetation and materials at least 30 feet from your home",
                urgency="High"
            ))
            measures.append(PreventionMeasure(
                title="Indoor Air Quality",
                description="Keep windows and doors closed. Use air purifiers if available",
                urgency="Medium"
            ))
            
        # Earthquake measures
        elif "earthquake" in disaster_type.lower():
            measures.append(PreventionMeasure(
                title="Drop, Cover, and Hold On",
                description="During shaking, drop to the ground, take cover under sturdy furniture, and hold on",
                urgency="Critical"
            ))
            measures.append(PreventionMeasure(
                title="After Shaking Stops",
                description="Check for injuries and damage. Be prepared for aftershocks",
                urgency="High"
            ))
            
        # Tsunami measures
        elif "tsunami" in disaster_type.lower():
            measures.append(PreventionMeasure(
                title="Move to Higher Ground",
                description="If you feel strong shaking or receive a tsunami warning, immediately move inland or to higher ground",
                urgency="Critical"
            ))
            measures.append(PreventionMeasure(
                title="Stay Away from Coast",
                description="Do not return to coastal areas until officials declare it safe",
                urgency="Critical"
            ))
            
        # Air quality measures
        elif any(term in disaster_type.lower() for term in ["air", "pollution", "quality"]):
            measures.append(PreventionMeasure(
                title="Stay Indoors",
                description="Keep windows and doors closed. Use air conditioning on recirculate mode",
                urgency="High" if severity in ["Severe", "Extreme"] else "Medium"
            ))
            measures.append(PreventionMeasure(
                title="Use N95 Masks",
                description="If you must go outside, wear a properly fitted N95 mask",
                urgency="High" if severity in ["Severe", "Extreme"] else "Medium"
            ))
            
        # Winter storm measures
        elif any(term in disaster_type.lower() for term in ["winter", "snow", "blizzard", "ice"]):
            measures.append(PreventionMeasure(
                title="Stay Indoors",
                description="Avoid traveling unless absolutely necessary",
                urgency="High" if severity in ["Severe", "Extreme"] else "Medium"
            ))
            measures.append(PreventionMeasure(
                title="Prevent Freezing Pipes",
                description="Let faucets drip slightly to prevent pipes from freezing",
                urgency="Medium"
            ))
            measures.append(PreventionMeasure(
                title="Emergency Heat",
                description="Have alternative heating methods ready. Never use generators or grills indoors",
                urgency="High"
            ))
            
        # Generic measures for any other disaster type
        if not measures:
            measures.append(PreventionMeasure(
                title="Stay Informed",
                description="Monitor local news and weather updates for the latest information",
                urgency="Medium"
            ))
            measures.append(PreventionMeasure(
                title="Emergency Kit",
                description="Prepare basic supplies including water, food, medications, and first aid kit",
                urgency="Medium"
            ))
            
        return measures