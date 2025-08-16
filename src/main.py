"""
LawVriksh Credit Management API - Main Application Entry Point
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from src.config import settings
from src.database import db
from src.schemas import (
    CreditAmount, 
    APIResponse, 
    SchemaUpdateRequest
)
from src.services import credit_service
from src.utils import BackgroundScheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await db.create_pool()
    BackgroundScheduler.start_scheduler_thread()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    await db.close_pool()
    logger.info("Application shut down successfully")

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend Intern Assignment - Credit Management System",
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "OK",
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        "service": settings.app_name
    }

# Credit management endpoints
@app.get("/api/credits/{user_id}", response_model=APIResponse)
async def get_user_credits(user_id: int):
    """Retrieve current credit balance and last update timestamp"""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    try:
        user_data = await credit_service.get_user_credits(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return APIResponse(success=True, data=user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving credits: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/credits/{user_id}/add", response_model=APIResponse)
async def add_credits(user_id: int, credit_amount: CreditAmount):
    """Add credits to user account"""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if not await credit_service.user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        result = await credit_service.add_credits(user_id, credit_amount.amount)
        await credit_service.log_transaction(
            user_id, credit_amount.amount, 'ADD', 'Manual credit addition'
        )
        
        return APIResponse(
            success=True,
            message=f"Added {credit_amount.amount} credits to user {user_id}",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/credits/{user_id}/deduct", response_model=APIResponse)
async def deduct_credits(user_id: int, credit_amount: CreditAmount):
    """Deduct credits from user account"""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if not await credit_service.user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Check current balance
        user_data = await credit_service.get_user_credits(user_id)
        current_credits = user_data.get('credits', 0)
        
        if current_credits < credit_amount.amount:
            raise HTTPException(status_code=400, detail="Insufficient credits")
        
        result = await credit_service.deduct_credits(user_id, credit_amount.amount)
        await credit_service.log_transaction(
            user_id, -credit_amount.amount, 'DEDUCT', 'Manual credit deduction'
        )
        
        return APIResponse(
            success=True,
            message=f"Deducted {credit_amount.amount} credits from user {user_id}",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deducting credits: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.patch("/api/credits/{user_id}/reset", response_model=APIResponse)
async def reset_credits(user_id: int):
    """Reset user's credits to zero"""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    if not await credit_service.user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        result = await credit_service.reset_credits(user_id)
        await credit_service.log_transaction(
            user_id, 0, 'RESET', 'Credits reset to zero'
        )
        
        return APIResponse(
            success=True,
            message=f"Reset credits to zero for user {user_id}",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error resetting credits: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/schema/update", response_model=APIResponse)
async def update_schema(schema_request: SchemaUpdateRequest):
    """External schema update endpoint"""
    try:
        # This is a placeholder for schema updates
        # In production, this should be handled with proper migrations
        raise HTTPException(
            status_code=501, 
            detail="Schema updates should be handled through migrations"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating schema: {e}")
        raise HTTPException(status_code=500, detail=f"Schema update failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
