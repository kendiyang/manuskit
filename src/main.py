"""
FastAPI-based web content extraction platform.
Industrial-grade automated content extraction service.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.models import (
    ExtractionRequest,
    ExtractionResult,
    TaskCreateResponse,
    TaskStatus,
    TaskStatusResponse,
    TaskInfo
)
from src.services.task_manager import TaskManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global task manager instance
task_manager: Optional[TaskManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global task_manager
    
    # Startup
    logger.info("Starting web content extraction platform...")
    
    # Initialize task manager
    max_concurrent = int(os.getenv("MAX_CONCURRENT_TASKS", "5"))
    task_manager = TaskManager(max_concurrent_tasks=max_concurrent)
    
    logger.info("Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down platform...")


# Create FastAPI app
app = FastAPI(
    title="Web Content Extraction Platform",
    description="Industrial-grade automated content extraction using Steel SDK and browser-use",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "web-content-extraction-platform",
        "version": "1.0.0"
    }


# Statistics endpoint
@app.get("/api/v1/stats", tags=["System"])
async def get_statistics():
    """Get platform statistics"""
    if not task_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    stats = task_manager.get_statistics()
    return {
        "statistics": stats,
        "max_concurrent_tasks": task_manager.max_concurrent_tasks
    }


# Extraction endpoints
@app.post(
    "/api/v1/extract",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Extraction"]
)
async def create_extraction_task(request: ExtractionRequest):
    """
    Create a new content extraction task.
    
    The task will be executed asynchronously. Use the returned task_id
    to check the status and retrieve results.
    
    Args:
        request: Extraction request with question
        
    Returns:
        Task creation response with task_id
    """
    if not task_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Create task
        task_id = task_manager.create_task(request.question)
        
        # Submit for execution
        task_manager.submit_task(task_id)
        
        return TaskCreateResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="Task created and submitted for processing"
        )
        
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create extraction task")


@app.get(
    "/api/v1/tasks/{task_id}",
    response_model=TaskStatusResponse,
    tags=["Extraction"]
)
async def get_task_status(task_id: str):
    """
    Get the status and result of an extraction task.
    
    Args:
        task_id: Task ID from task creation
        
    Returns:
        Task status and result (if completed)
    """
    if not task_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        task_id=task.task_id,
        status=task.status,
        progress=task.metadata.get("progress"),
        result=task.result,
        error=task.error,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@app.get(
    "/api/v1/tasks",
    response_model=List[TaskInfo],
    tags=["Extraction"]
)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks")
):
    """
    List extraction tasks with optional filtering.
    
    Args:
        status: Filter by task status (optional)
        limit: Maximum number of tasks to return
        
    Returns:
        List of task information
    """
    if not task_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    tasks = task_manager.list_tasks(status=status, limit=limit)
    return tasks


@app.delete(
    "/api/v1/tasks/{task_id}",
    tags=["Extraction"]
)
async def cancel_task(task_id: str):
    """
    Cancel a pending extraction task.
    
    Args:
        task_id: Task ID to cancel
        
    Returns:
        Cancellation status
    """
    if not task_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task with status: {task.status}"
        )
    
    success = task_manager.cancel_task(task_id)
    
    if success:
        return {"message": "Task cancelled successfully", "task_id": task_id}
    else:
        raise HTTPException(status_code=400, detail="Failed to cancel task")


# Synchronous extraction endpoint (for simple use cases)
@app.post(
    "/api/v1/extract/sync",
    response_model=ExtractionResult,
    tags=["Extraction"]
)
async def extract_sync(request: ExtractionRequest):
    """
    Synchronous content extraction (blocking).
    
    Warning: This endpoint will block until extraction completes.
    For production use, prefer the async endpoint (/api/v1/extract).
    
    Args:
        request: Extraction request with question
        
    Returns:
        Extraction result
    """
    if not task_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Execute extraction directly
        result = await task_manager.extraction_service.extract_reddit_answers(
            request.question
        )
        return result
        
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Extraction failed")


# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Web Content Extraction Platform",
        "version": "1.0.0",
        "description": "Industrial-grade automated content extraction",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "async_extract": "/api/v1/extract",
            "sync_extract": "/api/v1/extract/sync",
            "task_status": "/api/v1/tasks/{task_id}",
            "list_tasks": "/api/v1/tasks",
            "statistics": "/api/v1/stats"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=True,  # Enable for development
        log_level="info"
    )
