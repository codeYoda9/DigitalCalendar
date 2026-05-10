"""Main FastAPI application for Digital Calendar Phase 1."""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

import models
from database import engine, get_db
import routes_tasks
import routes_groceries
import routes_meals
import routes_calendar
import schemas

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    # Startup: Create tables
    logger.info("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # Shutdown: Any cleanup
    logger.info("Shutting down application")


app = FastAPI(
    title="Digital Calendar API",
    description="Phase 1 API for household dashboard",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_tasks.router)
app.include_router(routes_groceries.router)
app.include_router(routes_meals.router)
app.include_router(routes_calendar.router)


@app.get("/health", response_model=schemas.HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Check application and database health."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        raise HTTPException(status_code=503, detail="Database connection failed")

    return schemas.HealthResponse(
        status="healthy",
        database=db_status,
    )


@app.get("/", tags=["root"])
def root():
    """Root endpoint with API information."""
    return {
        "name": "Digital Calendar API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "development") == "development",
    )
