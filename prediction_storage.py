import sqlite3
from datetime import datetime
from typing import List, Dict, Any
import json
from models import WeatherData, DisasterPrediction, Location

class PredictionStorage:
    def __init__(self, db_path="predictions.db"):
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self):
        """Create the database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            weather_data TEXT NOT NULL,
            predictions TEXT NOT NULL,
            accuracy REAL DEFAULT NULL
        )
        ''')
        
        # Create feedback table for learning
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            feedback_value TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (prediction_id) REFERENCES predictions (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_prediction(self, location: Location, weather_data: WeatherData, predictions: List[DisasterPrediction]) -> int:
        """
        Save a prediction to the database
        
        Args:
            location: Location object
            weather_data: WeatherData object
            predictions: List of DisasterPrediction objects
            
        Returns:
            The ID of the saved prediction
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert objects to JSON for storage
        location_str = json.dumps(location.dict())
        weather_data_str = json.dumps(weather_data.dict())
        predictions_str = json.dumps([p.dict() for p in predictions])
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO predictions (location, timestamp, weather_data, predictions) VALUES (?, ?, ?, ?)",
            (location_str, timestamp, weather_data_str, predictions_str)
        )
        
        # Get the ID of the inserted row
        prediction_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return prediction_id
    
    def get_recent_predictions(self, limit=10) -> List[Dict[str, Any]]:
        """
        Get the most recent predictions
        
        Args:
            limit: Maximum number of predictions to return
            
        Returns:
            List of prediction records
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        
        rows = cursor.fetchall()
        predictions = []
        
        for row in rows:
            prediction = dict(row)
            # Parse JSON strings back to dictionaries
            prediction['location'] = json.loads(prediction['location'])
            prediction['weather_data'] = json.loads(prediction['weather_data'])
            prediction['predictions'] = json.loads(prediction['predictions'])
            predictions.append(prediction)
        
        conn.close()
        return predictions
    
    def save_feedback(self, prediction_id: int, feedback_type: str, feedback_value: str) -> None:
        """
        Save user feedback for a prediction
        
        Args:
            prediction_id: ID of the prediction
            feedback_type: Type of feedback (accuracy, relevance, etc.)
            feedback_value: Feedback value
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO prediction_feedback (prediction_id, feedback_type, feedback_value, timestamp) VALUES (?, ?, ?, ?)",
            (prediction_id, feedback_type, feedback_value, timestamp)
        )
        
        conn.commit()
        conn.close()
    
    def update_prediction_accuracy(self, prediction_id: int, accuracy: float) -> None:
        """
        Update the accuracy of a prediction after verification
        
        Args:
            prediction_id: ID of the prediction
            accuracy: Accuracy score (0.0 to 1.0)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE predictions SET accuracy = ? WHERE id = ?",
            (accuracy, prediction_id)
        )
        
        conn.commit()
        conn.close()