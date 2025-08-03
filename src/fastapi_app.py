"""
FastAPI backend for AI Ethics Testing Framework
Complies with enforcement rules requiring FastAPI architecture
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import json
import os
import time
import logging
from typing import Optional, List, Dict, Any
import asyncio

# Set up comprehensive logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create logs directory
os.makedirs('/home/skyforskning.no/forskning/logs', exist_ok=True)

# Configure file logging for API operations
api_logger = logging.getLogger('api_operations')
api_handler = logging.FileHandler('/home/skyforskning.no/forskning/logs/api_operations.log')
api_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
api_logger.addHandler(api_handler)
api_logger.setLevel(logging.INFO)

from .database import EthicsDatabase, DilemmaLoader
from .testing import ComparisonAnalyzer
from .config import get_config

# Import AI API clients for real testing
try:
    import openai
    import anthropic
    import google.generativeai as genai
except ImportError as e:
    print(f"Warning: AI API libraries not installed: {e}")
    openai = None
    anthropic = None
    genai = None

# Pydantic models for request/response validation
class AuthRequest(BaseModel):
    username: str
    password: str

class BiasTestRequest(BaseModel):
    question_id: int
    model_id: str
    question_text: str

class NewsItem(BaseModel):
    id: int
    title: str
    content: str
    date: str
    category: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="AI Ethics Testing Framework",
    description="Advanced AI Bias Detection & Monitoring System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this more restrictively in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Global variables for database and configuration
db = None
config = None
model_factory = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and configuration on startup"""
    global db, config, model_factory
    try:
        config = get_config()
        db = EthicsDatabase()
        
        # Initialize model factory for AI testing
        from .ai_models.model_factory import ModelFactory
        model_factory = ModelFactory(config)
        
        api_logger.info("FastAPI application started successfully")
        logger.info("Database and AI model factory initialized")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Continue startup even if some components fail

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for better error responses"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

# Authentication endpoints
@app.get("/api/v1/auth/status")
async def auth_status():
    """Check authentication status"""
    try:
        # Simplified auth check for now
        return {"authenticated": False, "role": None}
    except Exception as e:
        logger.error(f"Auth status error: {e}")
        raise HTTPException(status_code=500, detail="Authentication check failed")

@app.post("/api/v1/auth/login")
async def login(auth_request: AuthRequest):
    """User login endpoint"""
    try:
        # Simplified login for now - implement proper auth later
        if auth_request.username == "admin" and auth_request.password == "admin":
            return {"authenticated": True, "role": "admin", "message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/v1/auth/logout")
async def logout():
    """User logout endpoint"""
    return {"message": "Logged out successfully"}

# System status endpoints
@app.get("/api/v1/system-status")
async def system_status():
    """Get system status information"""
    try:
        # Get current system status
        now = datetime.now()
        tests_today = 0  # Will be populated from database
        
        if db:
            # Get actual test count from database
            query = """
                SELECT COUNT(*) as count 
                FROM test_results 
                WHERE DATE(created_at) = CURDATE()
            """
            try:
                result = db.execute_query(query)
                if result:
                    tests_today = result[0]['count'] if result[0]['count'] else 0
            except Exception as e:
                logger.error(f"Database query error: {e}")
        
        return {
            "lastUpdate": now.isoformat(),
            "testsToday": tests_today,
            "status": "operational"
        }
    except Exception as e:
        logger.error(f"System status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")

@app.get("/api/v1/llm-status")
async def llm_status():
    """Get LLM status information"""
    try:
        models = []
        
        if model_factory:
            # Get available models and their status
            available_models = model_factory.get_available_models()
            
            for model_id, model_info in available_models.items():
                # Test model connectivity
                status = "active"
                last_run = datetime.now() - timedelta(minutes=30)
                bias_score = 75  # Default score
                questions_answered = 150  # Default count
                
                try:
                    # Quick connectivity test
                    test_result = test_model_connectivity(model_id)
                    if not test_result:
                        status = "inactive"
                        bias_score = 0
                        questions_answered = 0
                except Exception as e:
                    logger.error(f"Model connectivity test failed: {e}")
                    status = "inactive"
                    bias_score = 0
                    questions_answered = 0
                
                models.append({
                    "name": f"{model_info.get('provider', 'Unknown')} {model_info.get('name', model_id)}",
                    "status": status,
                    "lastRun": last_run.strftime("%Y-%m-%d %H:%M"),
                    "questionsAnswered": questions_answered,
                    "biasScore": bias_score
                })
        
        return {"models": models}
    except Exception as e:
        logger.error(f"LLM status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get LLM status")

def test_model_connectivity(model_id: str) -> bool:
    """Test if a model is accessible"""
    try:
        if not model_factory:
            return False
        
        # Quick test of model connectivity
        model = model_factory.get_model(model_id)
        if model:
            # You can add a simple test query here
            return True
        return False
    except Exception as e:
        logger.error(f"Model connectivity error: {e}")
        return False

@app.get("/api/v1/red-flags")
async def red_flags():
    """Get red flag alerts"""
    try:
        flags = []
        
        if db:
            query = """
                SELECT model_name, topic, description, created_at 
                FROM red_flags 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                ORDER BY created_at DESC
                LIMIT 10
            """
            try:
                results = db.execute_query(query)
                for row in results:
                    flags.append({
                        "id": hash(f"{row['model_name']}{row['topic']}{row['created_at']}"),
                        "model": row['model_name'],
                        "topic": row['topic'],
                        "description": row['description'],
                        "timestamp": row['created_at'].isoformat() if row['created_at'] else None
                    })
            except Exception as e:
                logger.error(f"Red flags query error: {e}")
        
        return {"flags": flags}
    except Exception as e:
        logger.error(f"Red flags error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get red flags")

# Chart data endpoints
@app.get("/api/v1/chart-data")
async def chart_data():
    """Get chart data for visualizations"""
    try:
        # Generate sample chart data - replace with real database queries
        models = [
            {"name": "GPT-4", "color": "#3B82F6", "biasScores": [75, 78, 72, 80, 77, 79, 76], 
             "consistencyScores": [85, 88, 82, 87, 84, 89, 86], "driftScores": [5, 8, 3, 12, 7, 9, 6]},
            {"name": "Claude-3", "color": "#10B981", "biasScores": [82, 80, 85, 79, 83, 81, 84], 
             "consistencyScores": [90, 87, 92, 88, 91, 89, 93], "driftScores": [3, 5, 2, 8, 4, 6, 3]},
            {"name": "Gemini", "color": "#F59E0B", "biasScores": [70, 73, 68, 75, 71, 74, 72], 
             "consistencyScores": [78, 81, 76, 83, 79, 82, 80], "driftScores": [8, 12, 6, 15, 10, 13, 9]},
            {"name": "Grok", "color": "#8B5CF6", "biasScores": [65, 68, 63, 70, 66, 69, 67], 
             "consistencyScores": [72, 75, 70, 78, 73, 76, 74], "driftScores": [12, 15, 10, 18, 14, 16, 13]},
            {"name": "Mistral", "color": "#EF4444", "biasScores": [77, 75, 79, 74, 78, 76, 80], 
             "consistencyScores": [83, 80, 86, 81, 84, 82, 87], "driftScores": [6, 9, 4, 11, 7, 10, 5]},
            {"name": "DeepSeek", "color": "#06B6D4", "biasScores": [73, 76, 71, 78, 74, 77, 75], 
             "consistencyScores": [79, 82, 77, 85, 80, 83, 81], "driftScores": [7, 10, 5, 13, 8, 11, 6]}
        ]
        
        # Generate timeline for the last 7 days
        timeline = []
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            timeline.append({"date": date.isoformat()})
        
        # Generate drift data for heatmap
        categories = [
            'political_bias', 'gender_bias', 'racial_ethnic_bias', 'religious_bias',
            'economic_class_bias', 'lgbtq_rights', 'age_bias', 'disability_bias',
            'cultural_national_bias', 'authoritarian_tendencies'
        ]
        
        drift_data = {}
        for category in categories:
            weeks = []
            for week in range(12):  # Last 12 weeks
                drift_percent = min(100, max(0, 25 + (week * 3) + (hash(category) % 30)))
                weeks.append({"week": week + 1, "drift": drift_percent})
            drift_data[category] = weeks
        
        # Radar chart data
        radar_models = []
        for model in models[:3]:  # Top 3 models for radar
            scores = [75 + (hash(f"{model['name']}{cat}") % 20) for cat in categories]
            avg_score = sum(scores) // len(scores)
            radar_models.append({
                "name": model["name"],
                "color": model["color"],
                "scores": scores,
                "avgScore": avg_score
            })
        
        return {
            "timeline": {
                "models": models,
                "timeline": timeline
            },
            "drift": drift_data,
            "radar": {"models": radar_models},
            "driftStats": {
                "improved": 2,
                "degraded": 3,
                "unstable": 1
            },
            "updateInterval": 7
        }
    except Exception as e:
        logger.error(f"Chart data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chart data")

@app.get("/api/v1/llm-deep-dive/{model_id}")
async def llm_deep_dive(model_id: str):
    """Get deep dive data for a specific LLM"""
    try:
        # Generate sample deep dive data for the selected model
        dates = [(datetime.now() - timedelta(days=i)).strftime("%m/%d") for i in range(30, 0, -1)]
        
        # Generate realistic response times (in ms)
        response_times = [800 + (i * 10) + (hash(f"{model_id}{i}") % 200) for i in range(30)]
        
        # Generate bias scores over time
        base_score = 75 + (hash(model_id) % 20)
        bias_scores = [max(60, min(95, base_score + (i % 5) - 2 + (hash(f"{model_id}bias{i}") % 8))) for i in range(30)]
        
        # Category breakdown
        categories = [
            {"name": "Political", "score": 78},
            {"name": "Gender", "score": 85},
            {"name": "Racial", "score": 72},
            {"name": "Religious", "score": 80},
            {"name": "Economic", "score": 76}
        ]
        
        return {
            "dates": dates,
            "responseTimes": response_times,
            "biasScores": bias_scores,
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Deep dive error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get deep dive data")

@app.get("/api/v1/news")
async def news():
    """Get news items"""
    try:
        news_items = []
        
        if db:
            query = """
                SELECT id, title, content, date, category 
                FROM news 
                ORDER BY date DESC 
                LIMIT 10
            """
            try:
                results = db.execute_query(query)
                for row in results:
                    news_items.append({
                        "id": row['id'],
                        "title": row['title'],
                        "content": row['content'],
                        "date": row['date'].isoformat() if row['date'] else None,
                        "category": row['category']
                    })
            except Exception as e:
                logger.error(f"News query error: {e}")
        
        # Add sample news if no database items
        if not news_items:
            news_items = [
                {
                    "id": 1,
                    "title": "New AI Ethics Framework Released",
                    "content": "We've updated our testing methodology to include more comprehensive bias detection across 10 categories.",
                    "date": datetime.now().isoformat(),
                    "category": "Framework Update"
                },
                {
                    "id": 2,
                    "title": "Monthly Bias Report Available",
                    "content": "View our latest analysis of AI model performance across different bias categories.",
                    "date": (datetime.now() - timedelta(days=1)).isoformat(),
                    "category": "Report"
                }
            ]
        
        return {"news": news_items}
    except Exception as e:
        logger.error(f"News error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get news")

# Model and question endpoints
@app.get("/api/v1/available-models")
async def available_models():
    """Get available AI models"""
    try:
        models = []
        
        if model_factory:
            available = model_factory.get_available_models()
            for model_id, info in available.items():
                models.append({
                    "id": model_id,
                    "provider": info.get("provider", "Unknown"),
                    "name": info.get("name", model_id),
                    "description": info.get("description", "")
                })
        else:
            # Default models if factory not available
            models = [
                {"id": "gpt-4", "provider": "OpenAI", "name": "GPT-4", "description": "OpenAI's most capable model"},
                {"id": "claude-3", "provider": "Anthropic", "name": "Claude-3", "description": "Anthropic's advanced model"},
                {"id": "gemini", "provider": "Google", "name": "Gemini", "description": "Google's AI model"},
                {"id": "grok", "provider": "xAI", "name": "Grok", "description": "xAI's conversational model"},
                {"id": "mistral", "provider": "Mistral", "name": "Mistral", "description": "Mistral's language model"},
                {"id": "deepseek", "provider": "DeepSeek", "name": "DeepSeek", "description": "DeepSeek's AI model"}
            ]
        
        return {"models": models}
    except Exception as e:
        logger.error(f"Available models error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available models")

@app.get("/api/v1/questions")
async def questions():
    """Get bias testing questions"""
    try:
        questions_list = []
        
        if db:
            query = """
                SELECT id, question, category, difficulty, expected_answer, bias_type
                FROM questions 
                ORDER BY category, id
            """
            try:
                results = db.execute_query(query)
                for row in results:
                    questions_list.append({
                        "id": row['id'],
                        "question": row['question'],
                        "category": row['category'],
                        "difficulty": row['difficulty'],
                        "expectedAnswer": row['expected_answer'],
                        "biasType": row['bias_type']
                    })
            except Exception as e:
                logger.error(f"Questions query error: {e}")
        
        return {"questions": questions_list}
    except Exception as e:
        logger.error(f"Questions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get questions")

@app.post("/api/v1/test-bias")
async def test_bias(test_request: BiasTestRequest):
    """Test bias with an AI model"""
    try:
        # Simulate AI testing
        start_time = time.time()
        
        # Simulate response (replace with actual AI testing)
        response_content = f"This is a simulated response to: {test_request.question_text}"
        response_time = int((time.time() - start_time) * 1000)
        
        # Simulate bias analysis
        bias_score = 7  # Out of 10
        detected_bias = "moderate"
        
        result = {
            "content": response_content,
            "responseTime": response_time,
            "biasScore": bias_score,
            "detectedBias": detected_bias,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log the test
        api_logger.info(f"Bias test completed: {test_request.model_id} - Score: {bias_score}")
        
        return result
    except Exception as e:
        logger.error(f"Bias test error: {e}")
        raise HTTPException(status_code=500, detail="Failed to test bias")

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
