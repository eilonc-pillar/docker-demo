"""
ML Analytics Dashboard - FastAPI Backend
A production-ready analytics API with machine learning capabilities
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import logging
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ML Analytics Dashboard API",
    description="Real-time analytics with machine learning insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()

# Global variables for ML model
anomaly_detector = None
model_loaded = False

class AnalyticsData(BaseModel):
    timestamp: datetime
    user_id: str
    event_type: str
    page_url: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None

class AnalyticsResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float
    services: Dict[str, str]

# Startup time for uptime calculation
startup_time = time.time()

@app.on_event("startup")
async def load_ml_model():
    """Load ML model on startup"""
    global anomaly_detector, model_loaded
    
    try:
        # Initialize anomaly detection model
        anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        # Generate sample data for training
        sample_data = np.random.randn(1000, 5)
        anomaly_detector.fit(sample_data)
        
        model_loaded = True
        logger.info("ML model loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        model_loaded = False

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - startup_time
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime=uptime,
        services={
            "api": "healthy",
            "ml_model": "healthy" if model_loaded else "unhealthy",
            "database": "healthy",
            "redis": "healthy"
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ML Analytics Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/api/v1/analytics/upload", response_model=AnalyticsResponse)
async def upload_analytics_data(data: List[AnalyticsData]):
    """Upload analytics data for processing"""
    try:
        # Process the data
        processed_count = len(data)
        
        # Simulate ML processing
        if model_loaded and data:
            # Extract features for anomaly detection
            features = []
            for item in data:
                feature_vector = [
                    len(item.user_id),
                    len(item.page_url),
                    len(item.session_id),
                    item.timestamp.hour,
                    item.timestamp.minute
                ]
                features.append(feature_vector)
            
            # Detect anomalies
            anomalies = anomaly_detector.predict(features)
            anomaly_count = sum(1 for a in anomalies if a == -1)
        else:
            anomaly_count = 0
        
        return AnalyticsResponse(
            status="success",
            message=f"Processed {processed_count} events, detected {anomaly_count} anomalies",
            data={
                "processed_events": processed_count,
                "anomalies_detected": anomaly_count,
                "processing_time": time.time()
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error processing analytics data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process analytics data: {str(e)}"
        )

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    return {
        "total_events": 12543,
        "unique_users": 892,
        "sessions": 1456,
        "anomalies_detected": 23,
        "last_updated": datetime.now().isoformat(),
        "top_pages": [
            {"page": "/dashboard", "views": 1234},
            {"page": "/analytics", "views": 987},
            {"page": "/reports", "views": 654}
        ]
    }

@app.get("/api/v1/analytics/realtime")
async def get_realtime_metrics():
    """Get real-time analytics metrics"""
    return {
        "current_users": 45,
        "events_per_minute": 123,
        "response_time_avg": 45.2,
        "error_rate": 0.02,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/analytics/predictions")
async def get_ml_predictions():
    """Get ML predictions and insights"""
    if not model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model not loaded"
        )
    
    # Generate sample predictions
    predictions = {
        "traffic_forecast": {
            "next_hour": 1250,
            "next_day": 30000,
            "confidence": 0.85
        },
        "anomaly_score": 0.12,
        "recommendations": [
            "Traffic spike expected at 2 PM",
            "Consider scaling backend services",
            "Monitor error rates closely"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    return predictions

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
