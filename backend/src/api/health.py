"""
Health check endpoints with detailed status for DEL-006.
Provides comprehensive health information for monitoring and debugging.
"""

import time
import psutil
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..config.settings import get_settings

router = APIRouter()

# Store startup time for uptime calculation
startup_time = time.time()


def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics."""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        "response_time": 0,  # Will be calculated per request
        "memory_usage": {
            "rss": memory_info.rss,
            "vms": memory_info.vms,
            "percent": process.memory_percent()
        },
        "uptime": time.time() - startup_time,
        "cpu_percent": process.cpu_percent()
    }


def get_database_status() -> Dict[str, Any]:
    """Get database connection status."""
    settings = get_settings()
    
    try:
        is_valid, error = settings.validate_database_connection()
        return {
            "status": "healthy" if is_valid else "unhealthy",
            "connection": "established" if is_valid else "failed",
            "error": error if not is_valid else None,
            "url_type": "sqlite" if settings.database_url.startswith("sqlite") else "postgresql"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "connection": "failed", 
            "error": str(e),
            "url_type": "unknown"
        }


def get_api_providers_status() -> Dict[str, Any]:
    """Get API providers status."""
    settings = get_settings()
    
    # For now, just check if API keys are configured
    # TODO: Implement actual API connectivity validation
    providers = {}
    
    if settings.anthropic_api_key:
        providers["anthropic"] = {
            "status": "configured",
            "response_time": None
        }
    
    if settings.openai_api_key:
        providers["openai"] = {
            "status": "configured", 
            "response_time": None
        }
    
    if settings.gemini_api_key:
        providers["gemini"] = {
            "status": "configured",
            "response_time": None
        }
    
    if settings.xai_api_key:
        providers["xai"] = {
            "status": "configured",
            "response_time": None
        }
    
    return providers


def get_startup_validation_status() -> Dict[str, Any]:
    """Get startup validation status."""
    settings = get_settings()
    
    try:
        validation_result = settings.validate_startup_configuration()
        return {
            "status": "valid" if validation_result.is_valid else "invalid",
            "timestamp": datetime.utcnow().isoformat(),
            "errors": len(validation_result.errors),
            "warnings": len(validation_result.warnings),
            "details": {
                "error_types": [e["type"] for e in validation_result.errors],
                "warning_types": [w["type"] for w in validation_result.warnings]
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/health")
async def health_check(request: Request):
    """Basic health check endpoint with comprehensive status."""
    start_time = time.time()
    
    settings = get_settings()
    
    # Get all health components
    database_status = get_database_status()
    api_providers_status = get_api_providers_status()
    startup_validation = get_startup_validation_status()
    performance = get_performance_metrics()
    
    # Calculate response time
    response_time = (time.time() - start_time) * 1000  # milliseconds
    performance["response_time"] = response_time
    
    # Determine overall status
    overall_status = "healthy"
    if database_status["status"] != "healthy":
        overall_status = "degraded"
    if startup_validation["status"] not in ["valid", "warning"]:
        overall_status = "unhealthy"
    
    health_data = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": {
            "name": settings.environment,
            "version": "1.0.0"
        },
        "database": database_status,
        "api_providers": api_providers_status,
        "startup_validation": startup_validation,
        "performance": performance
    }
    
    return JSONResponse(
        content=health_data,
        status_code=200 if overall_status in ["healthy", "degraded"] else 503
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with comprehensive diagnostics."""
    settings = get_settings()
    validation_result = settings.validate_startup_configuration()
    
    # Get detailed component status
    components = {
        "database": get_database_status(),
        "api_providers": get_api_providers_status(),
        "configuration": get_startup_validation_status(),
        "performance": get_performance_metrics()
    }
    
    # Run comprehensive checks
    checks = []
    
    # Database checks
    db_valid, db_error = settings.validate_database_connection()
    checks.append({
        "name": "database_connection",
        "status": "pass" if db_valid else "fail",
        "message": "Database connection is healthy" if db_valid else f"Database connection failed: {db_error}"
    })
    
    # API key checks
    api_valid, missing_keys = settings.validate_required_api_keys()
    checks.append({
        "name": "api_keys",
        "status": "pass" if api_valid else "fail", 
        "message": "All required API keys configured" if api_valid else f"Missing API keys: {', '.join(missing_keys)}"
    })
    
    # Generate recommendations
    recommendations = []
    if not api_valid:
        recommendations.append("Configure missing API keys in .env.local file")
    if not db_valid:
        recommendations.append("Check database configuration and connectivity")
    
    detailed_data = {
        "status": "healthy" if all(check["status"] == "pass" for check in checks) else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": components,
        "checks": checks,
        "diagnostics": {
            "validation_errors": validation_result.errors,
            "validation_warnings": validation_result.warnings,
            "environment": settings.environment,
            "debug_mode": settings.debug
        },
        "recommendations": recommendations
    }
    
    return JSONResponse(content=detailed_data)


@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    settings = get_settings()
    database_status = get_database_status()
    api_providers_status = get_api_providers_status()
    performance = get_performance_metrics()
    
    # Generate Prometheus metrics format
    metrics = []
    
    # Health status metrics
    health_status = 1 if database_status["status"] == "healthy" else 0
    metrics.append(f"health_check_status {health_status}")
    
    # Database metrics
    db_status = 1 if database_status["status"] == "healthy" else 0
    metrics.append(f"database_connection_status {db_status}")
    
    # API provider metrics
    for provider, status in api_providers_status.items():
        provider_status = 1 if status["status"] == "configured" else 0
        metrics.append(f'api_provider_status{{provider="{provider}"}} {provider_status}')
    
    # Performance metrics
    metrics.append(f"response_time_seconds {performance['response_time'] / 1000}")
    metrics.append(f"memory_usage_bytes {performance['memory_usage']['rss']}")
    metrics.append(f"uptime_seconds {performance['uptime']}")
    
    metrics_text = "\n".join(metrics) + "\n"
    
    return JSONResponse(
        content=metrics_text,
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )