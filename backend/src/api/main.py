"""FastAPI application entry point for the Databricks Orchestrator API."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .planner_routes import router as planner_router
from .project_routes import router as project_router
from .task_routes import router as task_router
from .health import router as health_router
from .models import ErrorResponse
from ..config.settings import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    logger.info("Starting Databricks Orchestrator API...")
    
    # Run startup validation
    settings = get_settings()
    try:
        logger.info("Running startup configuration validation...")
        validation_result = settings.validate_startup_configuration()
        
        if not validation_result.is_valid:
            logger.error("Startup validation failed!")
            for error in validation_result.errors:
                logger.error(f"  ERROR: {error.get('message', error)}")
            
            # Log warnings but don't fail startup
            for warning in validation_result.warnings:
                logger.warning(f"  WARNING: {warning.get('message', warning)}")
                
            # In production, we might want to fail startup on critical errors
            if settings.environment == "production" and validation_result.errors:
                raise RuntimeError(f"Startup validation failed with {len(validation_result.errors)} errors")
        else:
            logger.info(f"✅ Startup validation passed (environment: {settings.environment})")
            if validation_result.warnings:
                logger.info(f"  {len(validation_result.warnings)} warnings found")
            
        # Log configuration summary
        logger.info("Configuration summary:")
        logger.info(f"  Environment: {settings.environment}")
        logger.info(f"  Database: {settings.database_url[:50]}...")
        
        # Count configured API providers
        api_providers = []
        if settings.anthropic_api_key:
            api_providers.append("Anthropic")
        if settings.openai_api_key:
            api_providers.append("OpenAI")
        if settings.gemini_api_key:
            api_providers.append("Gemini")
        if settings.xai_api_key:
            api_providers.append("XAI")
        
        logger.info(f"  API Providers: {', '.join(api_providers) if api_providers else 'None configured'}")
        
    except Exception as e:
        logger.error(f"Startup validation failed with exception: {e}")
        if settings.environment == "production":
            raise
        logger.warning("Continuing startup despite validation errors (non-production environment)")
    
    yield
    logger.info("Shutting down Databricks Orchestrator API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Databricks Orchestrator API",
        description="API for AI-powered project planning and task management",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health_router, tags=["health"])  # Health endpoints at root level
    app.include_router(planner_router, prefix="/api/planner", tags=["planner"])
    app.include_router(project_router, prefix="/api", tags=["projects"])
    app.include_router(task_router, prefix="/api", tags=["tasks"])
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                details={"type": type(exc).__name__},
                code="INTERNAL_ERROR"
            ).model_dump()
        )
    
    # Legacy health check endpoint (kept for backwards compatibility)
    @app.get("/api/health")
    async def legacy_health_check():
        """Legacy health check endpoint for backwards compatibility."""
        return {"status": "healthy", "service": "databricks-orchestrator-api"}
    
    return app


# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )