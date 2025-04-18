from fastapi import FastAPI, HTTPException, Query, Form, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from models import WeatherData, DisasterPrediction, Location, PredictionResponse
from weather_service import WeatherService
from disaster_predictor import DisasterPredictor
from prevention_service import PreventionService
from prediction_storage import PredictionStorage
from typing import List, Dict, Any
import uvicorn
import os
import httpx

app = FastAPI(
    title="Disaster Prediction and Prevention API",
    description="API for predicting potential disasters and recommending preventive measures",
    version="1.0.0"
)

# Add CORS middleware to allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static files directory (for CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

weather_service = WeatherService()
disaster_predictor = DisasterPredictor()
prevention_service = PreventionService()
storage = PredictionStorage()

# Add custom exception handlers for 404 errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        # Check if this is an API request (looking for JSON)
        accept_header = request.headers.get("accept", "")
        if "application/json" in accept_header:
            return JSONResponse(
                status_code=404,
                content={"error": "Resource not found", "detail": str(exc.detail)}
            )
        # Return a simple 404 page for browser requests
        return HTMLResponse(
            content="<html><body><h1>404 - Page Not Found</h1><p>The page you're looking for doesn't exist.</p></body></html>",
            status_code=404
        )
    # For other HTTP exceptions, just raise them
    raise exc

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # This will handle validation errors from incorrect API requests
    accept_header = request.headers.get("accept", "")
    if "application/json" in accept_header:
        return JSONResponse(
            status_code=422,
            content={"error": "Validation Error", "detail": str(exc)}
        )
    return HTMLResponse(
        content="<html><body><h1>422 - Validation Error</h1><p>The request data was invalid.</p></body></html>",
        status_code=422
    )

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the index page"""
    try:
        index_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
        if not os.path.exists(index_path):
            index_path = os.path.join(os.path.dirname(__file__), "index.html")
            
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(
            content=f"<html><body><h1>Error loading index page</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )

@app.get("/documentation", response_class=HTMLResponse)
async def read_documentation():
    """Serve the documentation page"""
    try:
        docs_path = os.path.join(os.path.dirname(__file__), "documentation.html")
        with open(docs_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(
            content=f"<html><body><h1>Error loading documentation</h1><p>{str(e)}</p></body></html>",
            status_code=500
        )

@app.get("/api/predict", response_model=PredictionResponse)
async def predict_disasters(location: str = Query(..., description="City name or lat,lng coordinates")):
    """
    Get disaster predictions and prevention recommendations for a location
    """
    try:
        # Apply learning from history
        disaster_predictor.learn_from_history()
        
        # Check if location is in format "lat,lng"
        if "," in location and all(c.isdigit() or c in ".-," for c in location):
            # This is likely a lat,lng format
            corrected_location = location  # No need to correct coordinates
        else:
            # Correct potential spelling errors in location name
            corrected_location = disaster_predictor.correct_location_name(location)
        
        # Fetch weather data for the corrected location
        weather_data = await weather_service.get_weather_data(corrected_location)
        
        # Make prediction with the corrected location
        predictions = disaster_predictor.predict_disasters(weather_data)
        
        # Generate prevention measures based on predictions
        preventions = prevention_service.get_prevention_measures(predictions)
        
        # Create location object
        location_obj = Location(
            city=weather_data.city if hasattr(weather_data, "city") else corrected_location, 
            country=weather_data.country if hasattr(weather_data, "country") else None,
            latitude=weather_data.latitude if hasattr(weather_data, "latitude") else None,
            longitude=weather_data.longitude if hasattr(weather_data, "longitude") else None
        )
        
        # Save prediction
        prediction_id = storage.save_prediction(location_obj, weather_data, predictions)
        
        response = PredictionResponse(
            location=location_obj,
            weather=weather_data,
            predictions=predictions,
            preventions=preventions,
            prediction_id=prediction_id
        )
        
        return response
        
    except Exception as e:
        # Provide a helpful error instead of 500 internal server error
        error_msg = f"Error processing prediction request: {str(e)}"
        if "location not found" in str(e).lower() or "geocoding failed" in str(e).lower():
            error_msg = f"Location '{location}' not found. Please check the spelling or try a nearby major city."
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/weather")
async def get_weather(location: str = Query(..., description="City name or lat,long coordinates")):
    """
    Get current weather data for a location
    """
    try:
        weather_data = await weather_service.get_weather_data(location)
        location_obj = Location(city=location)
        return {
            "location": location_obj.dict(),
            "weather": weather_data.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast")
async def get_forecast(
    location: str = Query(..., description="City name or lat,long coordinates"),
    days: int = Query(3, description="Number of forecast days (1-3)")
):
    """
    Get weather forecast for a location
    """
    try:
        # Implement forecast functionality when needed
        # For now, return a placeholder
        return {"message": "Forecast functionality not implemented yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history", response_model=List[Dict[str, Any]])
async def get_prediction_history(limit: int = Query(10, description="Maximum number of records to return")):
    """Get recent prediction history"""
    try:
        return storage.get_recent_predictions(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving prediction history: {str(e)}")

@app.post("/api/feedback")
async def submit_feedback(
    prediction_id: int = Form(...),
    feedback_type: str = Form(...),
    feedback_value: str = Form(...),
):
    """Submit feedback for a prediction"""
    try:
        storage.save_feedback(prediction_id, feedback_type, feedback_value)
        return {"status": "success", "message": "Feedback recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)