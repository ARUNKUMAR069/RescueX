from typing import List, Optional, Dict
from pydantic import BaseModel

class WeatherData(BaseModel):
    temperature: float = 0.0
    humidity: float = 0.0
    precipitation: float = 0.0
    wind_speed: float = 0.0
    pressure: float = 1013.0
    snow_depth: float = 0.0
    temperature_gradient: float = 0.0
    consecutive_dry_days: int = 0
    soil_saturation: float = 0.0
    temperature_change: float = 0.0
    snow_fall: float = 0.0
    air_quality_index: int = 0
    seismic_activity: float = 0.0
    coastal_proximity: float = 9999.0  # Default to far from coast
    volcanic_activity: float = 0.0
    pressure_change: float = 0.0
    cloud_height: float = 10000.0
    dew_point: float = 0.0
    stagnant_water_index: float = 0.0
    urban_runoff_index: float = 0.0
    temperature_profile: str = "normal"

class Location(BaseModel):
    city: str
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DisasterPrediction(BaseModel):
    disaster_type: str
    probability: float
    severity: str
    description: str
    
class PreventionMeasure(BaseModel):
    title: str
    description: str
    urgency: str
    
class PredictionResponse(BaseModel):
    location: Location
    weather: WeatherData
    predictions: List[DisasterPrediction]
    preventions: Dict[str, List[PreventionMeasure]]
    prediction_id: Optional[int] = None  # Add this for tracking predictions