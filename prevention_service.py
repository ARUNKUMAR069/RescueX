from models import PreventionMeasure, DisasterPrediction
from typing import Dict, List, Set

class PreventionService:
    def get_prevention_measures(self, predictions: List[DisasterPrediction]) -> Dict[str, List[PreventionMeasure]]:
        """Get prevention recommendations based on predicted disasters"""
        prevention_measures = {}
        
        # If we have "No Significant Hazards" and nothing else, return empty dict
        if len(predictions) == 1 and predictions[0].disaster_type == "No Significant Hazards":
            return {}
            
        # Normalize disaster types for matching
        disaster_keywords = {
            "Flood": ["flood", "flooding"],
            "Flash Flood": ["flash flood", "flash"],
            "Heat Wave": ["heat", "heatwave", "hot"],
            "Storm": ["storm", "thunderstorm"],
            "Hurricane/Cyclone": ["hurricane", "cyclone", "typhoon"],
            "Wildfire": ["fire", "wildfire", "bush fire"],
            "Tornado": ["tornado", "twister"],
            "Winter Storm": ["winter", "blizzard", "snow", "ice"],
            "Earthquake": ["earthquake", "seismic"],
            "Air Quality": ["air", "pollution", "smog", "quality"]
        }
        
        # Track what disaster types we've already processed to avoid duplicates
        processed_disasters: Set[str] = set()
        
        for prediction in predictions:
            disaster_type = prediction.disaster_type
            severity = prediction.severity
            
            # Skip "No Significant Hazards" prediction
            if disaster_type == "No Significant Hazards":
                continue
                
            # Find matching disaster category
            matched_type = None
            for category, keywords in disaster_keywords.items():
                if any(keyword in disaster_type.lower() for keyword in keywords):
                    matched_type = category
                    break
            
            # Skip if we've already processed this disaster type
            if matched_type and matched_type in processed_disasters:
                continue
                
            # Get prevention measures based on matched disaster type
            if matched_type:
                processed_disasters.add(matched_type)
                
                if matched_type == "Flood":
                    prevention_measures["Flood"] = self._get_flood_preventions(severity)
                elif matched_type == "Flash Flood":
                    prevention_measures["Flash Flood"] = self._get_flash_flood_preventions(severity)
                elif matched_type == "Heat Wave":
                    prevention_measures["Heat Wave"] = self._get_heat_wave_preventions(severity)
                elif matched_type == "Storm":
                    prevention_measures["Storm"] = self._get_storm_preventions(severity)
                elif matched_type == "Hurricane/Cyclone":
                    prevention_measures["Hurricane/Cyclone"] = self._get_hurricane_preventions(severity)
                elif matched_type == "Wildfire":
                    prevention_measures["Wildfire"] = self._get_wildfire_preventions(severity)
                elif matched_type == "Tornado":
                    prevention_measures["Tornado"] = self._get_tornado_preventions(severity)
                elif matched_type == "Winter Storm":
                    prevention_measures["Winter Storm"] = self._get_winter_storm_preventions(severity)
                elif matched_type == "Earthquake":
                    prevention_measures["Earthquake"] = self._get_earthquake_preventions(severity)
                elif matched_type == "Air Quality":
                    prevention_measures["Air Quality"] = self._get_air_quality_preventions(severity)
                
        return prevention_measures
    
    def _get_flood_preventions(self, severity: str) -> List[PreventionMeasure]:
        preventions = [
            PreventionMeasure(
                title="Avoid flood-prone areas",
                description="Stay away from low-lying areas and river banks",
                urgency="High"
            ),
            PreventionMeasure(
                title="Prepare emergency kit",
                description="Include water, food, medications, and important documents",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Move valuables to higher levels",
                description="Relocate important items and electrical equipment to upper floors",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Clear drains and gutters",
                description="Ensure proper drainage around your property to reduce flooding",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Install flood barriers",
                description="Use sandbags or specialized flood barriers around entry points",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Turn off utilities",
                description="Disconnect electricity and gas if flooding is imminent",
                urgency="High"
            ),
            PreventionMeasure(
                title="Plan evacuation routes",
                description="Familiarize yourself with safe evacuation paths and meeting points",
                urgency="Medium"
            )
        ]
        
        if severity in ["Severe", "Extreme"]:
            preventions.append(PreventionMeasure(
                title="Consider evacuation",
                description="Follow local authority evacuation instructions if issued",
                urgency="High"
            ))
            preventions.append(PreventionMeasure(
                title="Move to higher ground",
                description="Relocate to higher elevation if in a flood-prone area",
                urgency="High"
            ))
            
        return preventions

    def _get_flash_flood_preventions(self, severity: str) -> List[PreventionMeasure]:
        """Get flash flood specific preventions"""
        preventions = [
            PreventionMeasure(
                title="Evacuate immediately",
                description="Move to higher ground without delay if in a flash flood area",
                urgency="Critical"
            ),
            PreventionMeasure(
                title="Avoid flood waters",
                description="Never walk, swim, or drive through flood waters - Turn Around, Don't Drown!",
                urgency="Critical"
            ),
            PreventionMeasure(
                title="Disconnect utilities",
                description="Turn off gas, electricity, and water if safe to do so",
                urgency="High"
            ),
        ]
        
        return preventions

    def _get_heat_wave_preventions(self, severity: str) -> List[PreventionMeasure]:
        preventions = [
            PreventionMeasure(
                title="Stay hydrated",
                description="Drink plenty of water even if not thirsty",
                urgency="High"
            ),
            PreventionMeasure(
                title="Stay in cool areas",
                description="Use air conditioning or visit public cooling centers",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Wear lightweight clothing",
                description="Choose light-colored, loose-fitting clothes that breathe",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Avoid strenuous activity",
                description="Postpone outdoor activities during peak heat hours (10am-4pm)",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Use fans and cold compresses",
                description="Enhance cooling with fans and damp cloths on pulse points",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Close blinds during day",
                description="Block direct sunlight to keep indoor spaces cooler",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Know heat illness signs",
                description="Learn to recognize symptoms of heat exhaustion and heat stroke",
                urgency="High"
            )
        ]
        
        if severity in ["High", "Extreme"]:
            preventions.append(PreventionMeasure(
                title="Check on vulnerable people",
                description="Monitor elderly, young children, and those with health conditions",
                urgency="High"
            ))
            preventions.append(PreventionMeasure(
                title="Never leave pets or people in cars",
                description="Vehicle temperatures can reach deadly levels within minutes",
                urgency="Critical"
            ))
            
        return preventions
    
    def _get_storm_preventions(self, severity: str) -> List[PreventionMeasure]:
        preventions = [
            PreventionMeasure(
                title="Stay indoors",
                description="Remain inside and away from windows",
                urgency="High"
            ),
            PreventionMeasure(
                title="Secure loose objects",
                description="Bring in or tie down outdoor furniture and items",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Charge essential devices",
                description="Ensure phones and emergency communication devices are charged",
                urgency="High"
            ),
            PreventionMeasure(
                title="Fill bathtubs and containers",
                description="Store water for sanitation and drinking if supply is disrupted",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Keep emergency supplies ready",
                description="Prepare flashlights, batteries, first aid kit, and non-perishable food",
                urgency="High"
            ),
            PreventionMeasure(
                title="Stay updated with alerts",
                description="Keep a battery-powered radio to receive emergency information",
                urgency="High"
            ),
            PreventionMeasure(
                title="Identify safe shelter areas",
                description="Choose interior rooms on lowest floors away from windows",
                urgency="Medium"
            )
        ]
        
        if severity == "Severe":
            preventions.append(PreventionMeasure(
                title="Prepare for power outages",
                description="Have flashlights, batteries, and emergency supplies ready",
                urgency="High"
            ))
            preventions.append(PreventionMeasure(
                title="Avoid flooded areas",
                description="Never drive or walk through floodwaters - turn around, don't drown",
                urgency="Critical"
            ))
            
        return preventions
    
    def _get_hurricane_preventions(self, severity: str) -> List[PreventionMeasure]:
        """Get hurricane specific preventions"""
        preventions = [
            PreventionMeasure(
                title="Follow evacuation orders",
                description="If authorities order evacuation, leave immediately",
                urgency="Critical"
            ),
            PreventionMeasure(
                title="Secure your home",
                description="Board up windows, secure outdoor objects, and move valuables to upper floors",
                urgency="High"
            ),
            PreventionMeasure(
                title="Prepare emergency kit",
                description="Include water, non-perishable food, medications, important documents in waterproof containers",
                urgency="High"
            ),
            PreventionMeasure(
                title="Know your evacuation route",
                description="Plan where to go and how to get there if you need to evacuate",
                urgency="High"
            ),
        ]
        
        return preventions

    def _get_wildfire_preventions(self, severity: str) -> List[PreventionMeasure]:
        preventions = [
            PreventionMeasure(
                title="Create defensible space",
                description="Clear vegetation around your home",
                urgency="High"
            ),
            PreventionMeasure(
                title="Stay informed",
                description="Monitor local news and emergency alerts",
                urgency="High"
            ),
            PreventionMeasure(
                title="Prepare evacuation kit",
                description="Include essential items, medications, documents, and water",
                urgency="High"
            ),
            PreventionMeasure(
                title="Create evacuation plan",
                description="Identify multiple evacuation routes and a family meeting place",
                urgency="High"
            ),
            PreventionMeasure(
                title="Close all windows and doors",
                description="Prevent embers from entering your home",
                urgency="High"
            ),
            PreventionMeasure(
                title="Remove flammable materials",
                description="Move patio furniture, firewood, and other combustibles away from structures",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Fill containers with water",
                description="Have water available for firefighting and personal use",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Ensure proper home vents",
                description="Install ember-resistant vents to prevent sparks from entering",
                urgency="Medium"
            )
        ]
        
        if severity == "High":
            preventions.append(PreventionMeasure(
                title="Consider early evacuation",
                description="Leave before evacuation becomes mandatory for better safety",
                urgency="High"
            ))
            preventions.append(PreventionMeasure(
                title="Wear protective clothing",
                description="Use long sleeves, pants, masks, and goggles if smoke is present",
                urgency="High"
            ))
            
        return preventions

    def _get_tornado_preventions(self, severity: str) -> List[PreventionMeasure]:
        """Get tornado specific preventions"""
        preventions = [
            PreventionMeasure(
                title="Seek shelter immediately",
                description="Go to a basement, storm cellar, or interior room without windows on the lowest floor",
                urgency="Critical"
            ),
            PreventionMeasure(
                title="Cover yourself",
                description="Use blankets or furniture to protect yourself from flying debris",
                urgency="Critical"
            ),
            PreventionMeasure(
                title="Avoid windows",
                description="Stay away from windows and exterior doors",
                urgency="High"
            ),
            PreventionMeasure(
                title="Have emergency supplies",
                description="Keep a battery-powered weather radio, first aid kit, and emergency supplies ready",
                urgency="High"
            )
        ]
        
        return preventions

    def _get_winter_storm_preventions(self, severity: str) -> List[PreventionMeasure]:
        """Get winter storm specific preventions"""
        preventions = [
            PreventionMeasure(
                title="Stay indoors",
                description="Avoid unnecessary travel during winter storms",
                urgency="High"
            ),
            PreventionMeasure(
                title="Prepare emergency supplies",
                description="Stock up on food, water, medications, and heating fuel",
                urgency="High"
            ),
            PreventionMeasure(
                title="Prevent frozen pipes",
                description="Let faucets drip during extreme cold and insulate pipes",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Dress in layers",
                description="Wear multiple layers of loose-fitting clothing when going outside",
                urgency="High"
            ),
            PreventionMeasure(
                title="Keep alternative heat source",
                description="Have safe alternative heating methods available",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Clear snow safely",
                description="Use proper lifting technique when shoveling snow to prevent injury",
                urgency="Medium"
            )
        ]
        
        if severity in ["Severe", "Extreme"]:
            preventions.append(PreventionMeasure(
                title="Watch for signs of hypothermia",
                description="Monitor for shivering, exhaustion, confusion, memory loss, slurred speech",
                urgency="Critical"
            ))
            preventions.append(PreventionMeasure(
                title="Bring pets indoors",
                description="Provide warm shelter for pets and livestock",
                urgency="High"
            ))
        
        return preventions

    def _get_earthquake_preventions(self, severity: str) -> List[PreventionMeasure]:
        """Get earthquake specific preventions"""
        preventions = [
            PreventionMeasure(
                title="Drop, Cover, and Hold On",
                description="Drop to the ground, take cover under sturdy furniture, and hold on until shaking stops",
                urgency="Critical"
            ),
            PreventionMeasure(
                title="Stay away from windows",
                description="Move away from windows, outside walls and anything that could fall",
                urgency="High"
            ),
            PreventionMeasure(
                title="If outdoors, find a clear spot",
                description="Move to a clear area away from buildings, trees, streetlights, and power lines",
                urgency="High"
            ),
            PreventionMeasure(
                title="After shaking stops",
                description="Check yourself and others for injuries, be prepared for aftershocks",
                urgency="High"
            ),
            PreventionMeasure(
                title="Shut off utilities if damaged",
                description="Turn off gas, water, and electricity if you suspect damage",
                urgency="High"
            ),
            PreventionMeasure(
                title="Check building stability",
                description="Look for cracks in walls and foundations before re-entering buildings",
                urgency="High"
            )
        ]
        
        if severity in ["Severe", "Extreme"]:
            preventions.append(PreventionMeasure(
                title="Be aware of tsunami risk",
                description="If near the coast, move to higher ground after shaking stops",
                urgency="Critical"
            ))
            preventions.append(PreventionMeasure(
                title="Avoid bridges and overpasses",
                description="Stay away from damaged bridges, overpasses and structures",
                urgency="Critical"
            ))
        
        return preventions

    def _get_air_quality_preventions(self, severity: str) -> List[PreventionMeasure]:
        """Get air quality specific preventions"""
        preventions = [
            PreventionMeasure(
                title="Stay indoors",
                description="Keep windows and doors closed, use air conditioning on recirculate mode",
                urgency="Medium" if severity in ["Low", "Moderate"] else "High"
            ),
            PreventionMeasure(
                title="Limit outdoor activities",
                description="Avoid strenuous outdoor activities, especially for sensitive groups",
                urgency="Medium" if severity in ["Low", "Moderate"] else "High"
            ),
            PreventionMeasure(
                title="Use air purifiers",
                description="If available, use HEPA air purifiers indoors",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Stay hydrated",
                description="Drink plenty of water to help your body filter toxins",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Keep medications accessible",
                description="If you have asthma or respiratory conditions, keep medications handy",
                urgency="High"
            )
        ]
        
        if severity in ["Severe", "Extreme"]:
            preventions.append(PreventionMeasure(
                title="Wear masks outdoors",
                description="Use N95 or P100 respirators if you must go outside",
                urgency="High"
            ))
            preventions.append(PreventionMeasure(
                title="Consider temporary relocation",
                description="If possible, relocate to an area with better air quality until conditions improve",
                urgency="High"
            ))
            preventions.append(PreventionMeasure(
                title="Create a clean room",
                description="Designate one room with filtered air as a clean space in your home",
                urgency="High"
            ))
        
        return preventions

    def get_general_preventions(self) -> List[PreventionMeasure]:
        """Get general disaster preparedness measures"""
        return [
            PreventionMeasure(
                title="Create emergency plan",
                description="Have a family emergency plan with meeting points and communication strategy",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Prepare emergency kit",
                description="Maintain supplies for at least 72 hours including water, food, medications, and documents",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Stay informed",
                description="Keep a battery-powered radio and subscribe to emergency alerts",
                urgency="Medium"
            ),
            PreventionMeasure(
                title="Know evacuation routes",
                description="Familiarize yourself with local evacuation routes and shelter locations",
                urgency="Medium"
            )
        ]