import math



import numpy as np

from models import WeatherData, DisasterPrediction
from typing import List, Union, Dict, Any, Optional
import difflib  # Add this for fuzzy matching
from prediction_storage import PredictionStorage
from datetime import datetime, timedelta

class DisasterPredictor:
    # Known alternative spellings or common typos for attribute names
    ATTRIBUTE_ALIASES = {
        # Common typos
        'tempature': 'temperature',
        'temperatue': 'temperature',
        'temprature': 'temperature',
        'humid': 'humidity',
        'humidty': 'humidity',
        'precip': 'precipitation',
        'rainfall': 'precipitation',
        'wind': 'wind_speed',
        'windspeed': 'wind_speed',
        'pressure': 'pressure',
        
        # Alternative names
        'temp': 'temperature',
        'rain': 'precipitation',
        'winds': 'wind_speed',
        'soil_moisture': 'soil_saturation',
        'dry_days': 'consecutive_dry_days',
        'hot_days': 'consecutive_hot_days',
        'air_quality': 'air_quality_index',
        'aqi': 'air_quality_index',
        'earthquake': 'seismic_activity',
        'coastal_distance': 'coastal_proximity',
        'volcano': 'volcanic_activity',
    }

    # Add a dictionary of known locations with common misspellings
    LOCATION_ALIASES = {
        # India
        'cherrapunji': ['chirapunji', 'cheerapunji', 'chirrapunji', 'cherapunji'],
        'mumbai': ['bombay', 'mumbia', 'mumbye'],
        'delhi': ['new delhi', 'dilli', 'dehli'],
        'bangalore': ['bengaluru', 'banglore', 'bangalor'],
        'chennai': ['madras', 'chenai', 'chinnai'],
        'kolkata': ['calcutta', 'kolkatta', 'kolkota'],
        
        # USA
        'new york': ['newyork', 'ny', 'new york city', 'nyc'],
        'los angeles': ['la', 'l.a.', 'losangeles'],
        'san francisco': ['sf', 'sanfran', 'sanfrancisco'],
        'new orleans': ['neworleans', 'nawlins'],
        
        # Other major cities
        'london': ['londra', 'londen'],
        'paris': ['pari', 'paree'],
        'tokyo': ['tokio', 'toyko'],
        'beijing': ['peking', 'beijing'],
        'sydney': ['sidney'],
    }
    
    # Valid value ranges for sanity checks
    VALID_RANGES = {
        'temperature': (-70, 60),       # Celsius, Earth's record extremes
        'humidity': (0, 100),           # Percentage
        'precipitation': (0, 2000),     # mm per day, record is ~1800mm
        'wind_speed': (0, 150),         # m/s, ~500 km/h for tornadoes
        'pressure': (870, 1085),        # hPa, record extremes
        'air_quality_index': (0, 1000), # AQI scale
        'seismic_activity': (0, 10),    # Richter scale
    }
    
    def __init__(self):
        # Initialize storage
        self.storage = PredictionStorage()
        # Learning coefficients - can be adjusted based on feedback
        self.learning_coefficients = {
            'flood': 1.0,
            'heat_wave': 1.0,
            'storm': 1.0,
            'wildfire': 1.0,
            'tornado': 1.0,
            'earthquake': 1.0,
            'air_quality': 1.0
        }
    
    def correct_location_name(self, location_input: str) -> str:
        """
        Correct misspelled location names using fuzzy matching
        
        Args:
            location_input: The potentially misspelled location name
            
        Returns:
            Corrected location name or the original if no close match found
        """
        if not location_input:
            return location_input
            
        # Convert to lowercase for matching
        location_lower = location_input.lower().strip()
        
        # Direct match in aliases
        for correct_name, aliases in self.LOCATION_ALIASES.items():
            if location_lower == correct_name:
                return correct_name
            
            if location_lower in aliases:
                return correct_name
                
        # Try fuzzy matching if no direct match
        all_locations = list(self.LOCATION_ALIASES.keys())
        for aliases in self.LOCATION_ALIASES.values():
            all_locations.extend(aliases)
            
        # Use difflib to find close matches
        matches = difflib.get_close_matches(location_lower, all_locations, n=1, cutoff=0.7)
        if matches:
            matched_alias = matches[0]
            # If matched an alias, get the correct name
            for correct_name, aliases in self.LOCATION_ALIASES.items():
                if matched_alias == correct_name or matched_alias in aliases:
                    return correct_name
                    
        # No good match found, return original
        return location_input

    def predict_disasters(self, raw_weather_data: Union[WeatherData, Dict[str, Any]]) -> list[DisasterPrediction]:
        """
        Predict potential disasters based on weather data with enhanced accuracy and combinations.
        
        Args:
            raw_weather_data: Either a WeatherData object or a dictionary with weather attributes
            
        Returns:
            A list of potential disaster predictions
        """
        # First, ensure we have a valid WeatherData object
        weather_data = self._sanitize_input(raw_weather_data)
        
        predictions = []
        
        # ------------ HYDROLOGICAL DISASTERS ------------ #
        
        # Advanced flood prediction with multiple factors
        flood_risk = self._calculate_flood_risk(weather_data)
        if flood_risk > 0.8:
            predictions.append(DisasterPrediction(
                disaster_type="Severe Flood",
                probability=flood_risk,
                severity="Severe",
                description="Multiple high-risk conditions indicate serious flooding potential"
            ))
        elif flood_risk > 0.6:
            predictions.append(DisasterPrediction(
                disaster_type="Moderate Flood",
                probability=flood_risk,
                severity="Moderate",
                description="Combined conditions suggest moderate flooding risk"
            ))
        elif flood_risk > 0.4:
            predictions.append(DisasterPrediction(
                disaster_type="Minor Flood",
                probability=flood_risk,
                severity="Low",
                description="Some flood risk factors present but limited severity expected"
            ))
        
        # Flash flood specific conditions
        if weather_data.precipitation > 30 and weather_data.precipitation_intensity > 15:
            flash_flood_probability = min(0.95, 0.6 + (weather_data.precipitation - 30) * 0.02)
            predictions.append(DisasterPrediction(
                disaster_type="Flash Flood",
                probability=flash_flood_probability,
                severity="Severe",
                description="High intensity rainfall may cause rapid flooding in vulnerable areas"
            ))
        
        # Urban flooding with additional factors
        if weather_data.precipitation > 20:
            urban_flood_risk = 0.3 + (min(1.0, weather_data.urban_runoff_index / 100) * 0.6)
            if urban_flood_risk > 0.65:
                predictions.append(DisasterPrediction(
                    disaster_type="Urban Flooding",
                    probability=urban_flood_risk,
                    severity="High",
                    description="Rain with high urban runoff potential indicates significant flood risk in city areas"
                ))
        
        # ------------ METEOROLOGICAL DISASTERS ------------ #
        
        # Complex heat wave evaluation
        heat_risk = self._calculate_heat_risk(weather_data)
        if heat_risk > 0.85:
            predictions.append(DisasterPrediction(
                disaster_type="Extreme Heat Wave",
                probability=heat_risk,
                severity="Extreme",
                description="Critical combination of high temperature, humidity and duration poses severe health risks"
            ))
        elif heat_risk > 0.7:
            predictions.append(DisasterPrediction(
                disaster_type="Severe Heat Wave",
                probability=heat_risk,
                severity="Severe",
                description="Extended high temperature with humidity creates significant health danger"
            ))
        elif heat_risk > 0.5:
            predictions.append(DisasterPrediction(
                disaster_type="Heat Wave",
                probability=heat_risk,
                severity="Moderate",
                description="Elevated temperatures may cause heat-related health issues"
            ))
        
        # Advanced storm prediction system
        storm_severity = self._calculate_storm_severity(weather_data)
        if storm_severity > 0.8:
            predictions.append(DisasterPrediction(
                disaster_type="Severe Storm System",
                probability=0.85,
                severity="Severe",
                description="Multiple severe storm indicators present including pressure drop, wind and instability"
            ))
        elif storm_severity > 0.6:
            predictions.append(DisasterPrediction(
                disaster_type="Moderate Storm",
                probability=0.75,
                severity="Moderate",
                description="Storm conditions developing with potential for significant impact"
            ))
        
        # Hurricane/Cyclone tracking with enhanced parameters
        if weather_data.wind_speed > 75 and weather_data.pressure < 980 and weather_data.sea_surface_temp > 26:
            cat_level = min(5, 1 + int((119 - weather_data.pressure) / 10))
            predictions.append(DisasterPrediction(
                disaster_type=f"Category {cat_level} Hurricane/Cyclone",
                probability=0.9,
                severity="Extreme",
                description=f"Category {cat_level} tropical system with damaging winds, storm surge and flooding potential"
            ))
        
        # Enhanced tornado prediction
        tornado_risk = self._calculate_tornado_risk(weather_data)
        if tornado_risk > 0.7:
            predictions.append(DisasterPrediction(
                disaster_type="Tornado Warning",
                probability=tornado_risk,
                severity="Severe",
                description="Atmospheric conditions highly favorable for tornado formation"
            ))
        elif tornado_risk > 0.5:
            predictions.append(DisasterPrediction(
                disaster_type="Tornado Watch",
                probability=tornado_risk,
                severity="High",
                description="Conditions support possible tornado development in the coming hours"
            ))
        
        # Winter storm complex
        if weather_data.temperature < 2 and weather_data.precipitation > 10:
            winter_severity = 0.5
            if weather_data.temperature < -5:
                winter_severity += 0.2
            if weather_data.wind_speed > 30:
                winter_severity += 0.2
            if weather_data.precipitation > 20:
                winter_severity += 0.1
                
            storm_type = "Winter Storm"
            if winter_severity > 0.8 and weather_data.wind_speed > 35:
                storm_type = "Blizzard"
            
            predictions.append(DisasterPrediction(
                disaster_type=storm_type,
                probability=winter_severity,
                severity="Severe" if winter_severity > 0.8 else "Moderate",
                description=f"Significant winter precipitation with freezing temperatures creating hazardous conditions"
            ))
        
        # ------------ GEOLOGICAL DISASTERS ------------ #
        
        # Enhanced earthquake/tsunami cascade prediction
        if hasattr(weather_data, 'seismic_activity') and weather_data.seismic_activity > 5.0:
            # Earthquake severity
            quake_severity = "Minor" if weather_data.seismic_activity < 6.0 else \
                            "Moderate" if weather_data.seismic_activity < 7.0 else \
                            "Major" if weather_data.seismic_activity < 8.0 else "Extreme"
            
            earthquake_prob = min(0.95, 0.5 + (weather_data.seismic_activity - 5.0) * 0.1)
            predictions.append(DisasterPrediction(
                disaster_type=f"{quake_severity} Earthquake",
                probability=earthquake_prob,
                severity=quake_severity,
                description=f"Seismic activity of magnitude {weather_data.seismic_activity:.1f} detected"
            ))
            
            # Tsunami risk assessment
            if weather_data.seismic_activity > 6.5 and hasattr(weather_data, 'coastal_proximity') and weather_data.coastal_proximity < 100:
                tsunami_probability = 0.4 + min(0.5, (weather_data.seismic_activity - 6.5) * 0.2)
                tsunami_severity = "Moderate" if weather_data.seismic_activity < 7.5 else "Severe"
                
                # Adjusting for underwater earthquakes
                if hasattr(weather_data, 'underwater_quake') and weather_data.underwater_quake:
                    tsunami_probability += 0.3
                
                predictions.append(DisasterPrediction(
                    disaster_type="Tsunami",
                    probability=tsunami_probability,
                    severity=tsunami_severity,
                    description=f"Seismic activity near coast creates tsunami risk, potential wave height: {(weather_data.seismic_activity - 5.0) * 0.5:.1f}m"
                ))
        
        # ------------ ENVIRONMENTAL DISASTERS ------------ #
        
        # Comprehensive wildfire prediction system
        wildfire_risk = self._calculate_wildfire_risk(weather_data)
        if wildfire_risk > 0.8:
            predictions.append(DisasterPrediction(
                disaster_type="Extreme Fire Danger",
                probability=wildfire_risk,
                severity="Extreme",
                description="Critical fire weather conditions present extreme wildfire danger"
            ))
        elif wildfire_risk > 0.6:
            predictions.append(DisasterPrediction(
                disaster_type="High Fire Danger",
                probability=wildfire_risk,
                severity="High",
                description="Weather conditions favorable for rapid fire spread"
            ))
        elif wildfire_risk > 0.4:
            predictions.append(DisasterPrediction(
                disaster_type="Moderate Fire Danger",
                probability=wildfire_risk,
                severity="Moderate",
                description="Some fire risk conditions present, caution advised"
            ))
        
        # Advanced air quality evaluation
        if hasattr(weather_data, 'air_quality_index') and weather_data.air_quality_index > 0:
            if weather_data.air_quality_index > 300:
                predictions.append(DisasterPrediction(
                    disaster_type="Hazardous Air Quality Emergency",
                    probability=0.95,
                    severity="Extreme",
                    description="Extremely dangerous air quality levels pose immediate health threats to all"
                ))
            elif weather_data.air_quality_index > 200:
                predictions.append(DisasterPrediction(
                    disaster_type="Very Unhealthy Air Quality",
                    probability=0.9,
                    severity="Severe",
                    description="Very poor air quality may cause serious health effects for everyone"
                ))
            elif weather_data.air_quality_index > 150:
                predictions.append(DisasterPrediction(
                    disaster_type="Unhealthy Air Quality",
                    probability=0.8,
                    severity="High",
                    description="Unhealthy air quality affects sensitive groups and may affect general population"
                ))
        
        # Default case with confidence assessment
        if not predictions:
            predictions.append(DisasterPrediction(
                disaster_type="No Significant Hazards",
                probability=0.8,
                severity="Low",
                description="Current conditions do not indicate any significant disaster risks"
            ))
            
        return predictions
    
    def learn_from_history(self):
        """
        Analyze historical predictions and adjust prediction coefficients
        based on accuracy feedback
        """
        recent_predictions = self.storage.get_recent_predictions(limit=100)
        
        # Skip if not enough historical data
        if len(recent_predictions) < 5:
            return
            
        # Collect accuracy data by disaster type
        accuracy_by_type = {}
        
        for record in recent_predictions:
            # Skip records without accuracy feedback
            if record['accuracy'] is None:
                continue
                
            for prediction in record['predictions']:
                disaster_type = prediction['disaster_type'].lower()
                
                # Map to broader categories
                category = self._map_to_category(disaster_type)
                
                if category not in accuracy_by_type:
                    accuracy_by_type[category] = []
                    
                accuracy_by_type[category].append(record['accuracy'])
        
        # Update learning coefficients based on accuracy
        for category, accuracies in accuracy_by_type.items():
            if len(accuracies) > 0:
                avg_accuracy = sum(accuracies) / len(accuracies)
                
                # Adjust coefficient - increase if predictions were accurate,
                # decrease if they were not
                adjustment = (avg_accuracy - 0.5) * 0.1  # Small adjustment factor
                
                if category in self.learning_coefficients:
                    self.learning_coefficients[category] = max(0.5, min(1.5, 
                        self.learning_coefficients[category] + adjustment))
    
    def _map_to_category(self, disaster_type: str) -> str:
        """Map specific disaster types to broader categories for learning"""
        disaster_type = disaster_type.lower()
        
        if any(term in disaster_type for term in ['flood', 'rain', 'water']):
            return 'flood'
        elif any(term in disaster_type for term in ['heat', 'hot']):
            return 'heat_wave'
        elif any(term in disaster_type for term in ['storm', 'hurricane', 'cyclone', 'typhoon']):
            return 'storm'
        elif any(term in disaster_type for term in ['fire', 'wildfire']):
            return 'wildfire'
        elif any(term in disaster_type for term in ['tornado']):
            return 'tornado'
        elif any(term in disaster_type for term in ['earthquake', 'seismic']):
            return 'earthquake'
        elif any(term in disaster_type for term in ['air', 'pollution']):
            return 'air_quality'
        
        return 'other'
    
    def _sanitize_input(self, raw_data: Union[WeatherData, Dict[str, Any]]) -> WeatherData:
        """
        Sanitize and normalize input data to ensure we have a valid WeatherData object.
        Handles typos in attribute names and performs basic data validation.
        
        Args:
            raw_data: Input data either as WeatherData object or dictionary
            
        Returns:
            Sanitized WeatherData object
        """
        # If it's already a WeatherData object, validate it
        if isinstance(raw_data, WeatherData):
            return self._validate_weather_data(raw_data)
        
        # Convert dictionary to WeatherData
        try:
            # First, normalize the attribute names to handle typos and aliases
            normalized_data = {}
            for key, value in raw_data.items():
                # Clean up the key - lowercase and strip spaces
                clean_key = key.lower().strip()
                
                # Check if it's a known alias/typo
                if clean_key in self.ATTRIBUTE_ALIASES:
                    normalized_key = self.ATTRIBUTE_ALIASES[clean_key]
                else:
                    normalized_key = clean_key
                
                normalized_data[normalized_key] = value
            
            # Create a WeatherData object
            weather_data = WeatherData(**normalized_data)
            
            # Validate values
            return self._validate_weather_data(weather_data)
        except Exception as e:
            # If conversion fails, create a basic WeatherData with defaults
            print(f"Error processing input data: {e}. Using defaults with available valid data.")
            try:
                # Extract any valid data we can
                valid_data = {}
                for attr in ['temperature', 'humidity', 'precipitation', 'wind_speed', 'pressure']:
                    normalized_attr = self.ATTRIBUTE_ALIASES.get(attr, attr)
                    if normalized_attr in normalized_data:
                        valid_data[attr] = normalized_data[normalized_attr]
                
                return WeatherData(**valid_data)
            except:
                # Last resort - use completely default values
                return WeatherData()
    
    def _validate_weather_data(self, weather_data: WeatherData) -> WeatherData:
        """
        Validate and correct WeatherData values to ensure they're within sensible ranges.
        
        Args:
            weather_data: WeatherData object to validate
            
        Returns:
            Validated WeatherData object
        """
        # Clone the object to avoid modifying the original
        validated_data = dict(weather_data.dict())
        
        # Check each attribute against valid ranges
        for attr, (min_val, max_val) in self.VALID_RANGES.items():
            if hasattr(weather_data, attr):
                value = getattr(weather_data, attr)
                
                # Skip if not a number
                if not isinstance(value, (int, float)):
                    continue
                    
                # Apply range constraints
                if value < min_val:
                    validated_data[attr] = min_val
                    print(f"Warning: {attr} value {value} below minimum range {min_val}. Using {min_val} instead.")
                elif value > max_val:
                    validated_data[attr] = max_val
                    print(f"Warning: {attr} value {value} above maximum range {max_val}. Using {max_val} instead.")
        
        # Create a new validated WeatherData object
        return WeatherData(**validated_data)
    
    def _get_attribute_safely(self, weather_data: WeatherData, attr: str, default_value: Any = 0) -> Any:
        """
        Safely get an attribute value, handling missing attributes.
        
        Args:
            weather_data: WeatherData object
            attr: Attribute name to get
            default_value: Default value if attribute is missing
            
        Returns:
            Attribute value or default
        """
        if hasattr(weather_data, attr):
            return getattr(weather_data, attr)
        
        # Check for aliases
        for alias, target in self.ATTRIBUTE_ALIASES.items():
            if target == attr and hasattr(weather_data, alias):
                return getattr(weather_data, alias)
                
        return default_value

    def _calculate_flood_risk(self, weather_data: WeatherData) -> float:
        """Calculate comprehensive flood risk based on multiple factors with learning"""
        base_risk = 0.0
        
        # Get values safely
        precipitation = self._get_attribute_safely(weather_data, 'precipitation')
        soil_saturation = self._get_attribute_safely(weather_data, 'soil_saturation')
        river_level_percent = self._get_attribute_safely(weather_data, 'river_level_percent')
        snow_depth = self._get_attribute_safely(weather_data, 'snow_depth')
        temperature = self._get_attribute_safely(weather_data, 'temperature')
        upstream_precipitation = self._get_attribute_safely(weather_data, 'upstream_precipitation')
        
        # Calculate risk (same as before)
        if precipitation > 20:
            base_risk += min(0.6, (precipitation - 20) * 0.015)
        
        if soil_saturation > 60:
            base_risk += min(0.3, (soil_saturation - 60) * 0.0075)
        
        if river_level_percent > 70:
            base_risk += min(0.4, (river_level_percent - 70) * 0.013)
        
        if snow_depth > 10 and temperature > 5:
            base_risk += min(0.3, 0.1 + (temperature - 5) * 0.02)
        
        if upstream_precipitation > 30:
            base_risk += min(0.3, (upstream_precipitation - 30) * 0.01)
        
        # Apply learning coefficient
        base_risk *= self.learning_coefficients.get('flood', 1.0)
        
        return min(0.95, base_risk)
    
    def _calculate_heat_risk(self, weather_data: WeatherData) -> float:
        """Calculate heat wave risk using temperature, humidity and duration"""
        if weather_data.temperature < 30:
            return 0.0
        
        # Base risk from temperature
        base_risk = min(0.7, (weather_data.temperature - 30) * 0.07)
        
        # Humidity contribution (heat index adjustment)
        if weather_data.humidity > 40:
            humidity_factor = min(0.3, (weather_data.humidity - 40) * 0.005)
            base_risk += humidity_factor
        
        # Duration factor
        if hasattr(weather_data, 'consecutive_hot_days') and weather_data.consecutive_hot_days > 1:
            duration_factor = min(0.2, (weather_data.consecutive_hot_days - 1) * 0.04)
            base_risk += duration_factor
        
        # Urban heat island effect
        if hasattr(weather_data, 'urban_density') and weather_data.urban_density > 50:
            urban_factor = min(0.15, (weather_data.urban_density - 50) * 0.003)
            base_risk += urban_factor
        
        return min(0.95, base_risk)
    
    def _calculate_storm_severity(self, weather_data: WeatherData) -> float:
        """Calculate storm severity based on multiple meteorological factors"""
        severity = 0.0
        
        # Wind contribution
        if weather_data.wind_speed > 30:
            severity += min(0.4, (weather_data.wind_speed - 30) * 0.01)
        
        # Pressure contribution
        if weather_data.pressure < 1005:
            severity += min(0.3, (1005 - weather_data.pressure) * 0.02)
        
        # Pressure change rate (if available)
        if hasattr(weather_data, 'pressure_change') and weather_data.pressure_change < -3:
            severity += min(0.2, abs(weather_data.pressure_change + 3) * 0.06)
        
        # Precipitation intensity
        if hasattr(weather_data, 'precipitation_intensity') and weather_data.precipitation_intensity > 10:
            severity += min(0.2, (weather_data.precipitation_intensity - 10) * 0.02)
        
        # Atmospheric instability
        if hasattr(weather_data, 'cape_value') and weather_data.cape_value > 1000:
            severity += min(0.2, (weather_data.cape_value - 1000) * 0.0002)
            
        return min(0.95, severity)
    
    def _calculate_tornado_risk(self, weather_data: WeatherData) -> float:
        """Calculate tornado risk based on atmospheric conditions"""
        if not all(hasattr(weather_data, attr) for attr in ['wind_shear', 'cape_value', 'temperature_gradient']):
            # Fall back to basic estimation if advanced parameters unavailable
            if weather_data.wind_speed > 40 and hasattr(weather_data, 'temperature_gradient') and weather_data.temperature_gradient > 10:
                return 0.4 + min(0.3, (weather_data.wind_speed - 40) * 0.01)
            return 0.0
        
        risk = 0.0
        
        # Wind shear contribution
        if weather_data.wind_shear > 20:
            risk += min(0.3, (weather_data.wind_shear - 20) * 0.015)
        
        # CAPE (Convective Available Potential Energy) contribution
        if weather_data.cape_value > 1500:
            risk += min(0.3, (weather_data.cape_value - 1500) * 0.0002)
        
        # Temperature gradient
        if weather_data.temperature_gradient > 8:
            risk += min(0.2, (weather_data.temperature_gradient - 8) * 0.025)
        
        # Helicity (if available)
        if hasattr(weather_data, 'helicity') and weather_data.helicity > 150:
            risk += min(0.2, (weather_data.helicity - 150) * 0.001)
        
        # Lifted index (if available)
        if hasattr(weather_data, 'lifted_index') and weather_data.lifted_index < -4:
            risk += min(0.2, abs(weather_data.lifted_index + 4) * 0.05)
            
        return min(0.95, risk)
    
    def _calculate_wildfire_risk(self, weather_data: WeatherData) -> float:
        """Calculate wildfire risk based on multiple environmental factors"""
        if weather_data.humidity > 60 or weather_data.precipitation > 5:
            return 0.0
        
        risk = 0.0
        
        # Temperature contribution
        if weather_data.temperature > 25:
            risk += min(0.3, (weather_data.temperature - 25) * 0.02)
        
        # Low humidity contribution
        if weather_data.humidity < 40:
            risk += min(0.3, (40 - weather_data.humidity) * 0.0075)
        
        # Wind speed contribution
        if weather_data.wind_speed > 15:
            risk += min(0.2, (weather_data.wind_speed - 15) * 0.01)
        
        # Drought conditions
        if hasattr(weather_data, 'consecutive_dry_days') and weather_data.consecutive_dry_days > 7:
            risk += min(0.2, (weather_data.consecutive_dry_days - 7) * 0.02)
        
        # Vegetation dryness
        if hasattr(weather_data, 'vegetation_dryness') and weather_data.vegetation_dryness > 60:
            risk += min(0.2, (weather_data.vegetation_dryness - 60) * 0.005)
        
        # Lightning activity without rain
        if hasattr(weather_data, 'dry_lightning_probability') and weather_data.dry_lightning_probability > 0.3:
            risk += min(0.2, weather_data.dry_lightning_probability)
            
        return min(0.95, risk)