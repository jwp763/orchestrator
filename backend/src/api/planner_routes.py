"""API routes for the PlannerAgent functionality."""

import logging
from typing import Dict, Any
from functools import lru_cache

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from .models import (
    PlannerRequest, PlannerResponse, PlannerConfig, 
    ProvidersResponse, ConfigResponse, ErrorResponse,
    ProjectMetadata, TaskMetadata, ProviderInfo, ProviderModel
)
from ..agent.planner_agent import PlannerAgent
from ..agent.base import AgentError, JSONParsingError, ValidationError
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()


def get_settings_dependency():
    """Dependency to get settings instance."""
    return get_settings()


@lru_cache(maxsize=50)
def get_cached_planner_agent(
    provider: str,
    model_name: str,
    create_milestones: bool,
    max_milestones: int,
    max_retries: int,
    retry_delay: float
) -> PlannerAgent:
    """
    Get or create a cached PlannerAgent instance.
    
    This function caches PlannerAgent instances based on their configuration
    to avoid creating new agents for every request with the same parameters.
    
    Args:
        provider: AI provider name
        model_name: Model name (or "default" for provider default)
        create_milestones: Whether to create milestones
        max_milestones: Maximum number of milestones
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries
    
    Returns:
        Cached PlannerAgent instance
    """
    logger.info(f"Creating/retrieving cached PlannerAgent: {provider}:{model_name}, milestones={create_milestones}({max_milestones})")
    
    # Create agent with the specified configuration
    return PlannerAgent(
        provider=provider,
        model_name=model_name if model_name != "default" else None,
        create_milestones=create_milestones,
        max_milestones=max_milestones,
        max_retries=max_retries,
        retry_delay=retry_delay
    )


@router.post("/generate", response_model=PlannerResponse)
async def generate_project_plan(request: PlannerRequest, settings = Depends(get_settings_dependency)):
    """
    Generate a project plan from a natural language idea.
    
    Takes a project idea and configuration, then uses the PlannerAgent to generate
    structured project metadata with optional milestone tasks.
    """
    try:
        logger.info(f"Generating project plan for idea: {request.idea[:100]}...")
        
        # Normalize model name for caching
        model_name = request.config.model_name or "default"
        
        # Get or create cached PlannerAgent
        agent = get_cached_planner_agent(
            provider=request.config.provider,
            model_name=model_name,
            create_milestones=request.config.create_milestones,
            max_milestones=request.config.max_milestones,
            max_retries=request.config.max_retries,
            retry_delay=request.config.retry_delay
        )
        
        # Generate the project plan
        result = await agent.get_diff(request.idea, context=request.context)
        
        # Extract project metadata
        project_metadata = None
        if result.project_patches:
            project_patch = result.project_patches[0]
            project_metadata = ProjectMetadata(
                name=project_patch.name,
                description=project_patch.description,
                status=project_patch.status,
                priority=project_patch.priority,
                tags=project_patch.tags or [],
                estimated_total_minutes=project_patch.estimated_total_minutes
            )
        
        # Extract task metadata
        task_metadata = []
        if result.task_patches:
            for task_patch in result.task_patches:
                task_metadata.append(TaskMetadata(
                    title=task_patch.title,
                    description=task_patch.description,
                    status=task_patch.status,
                    priority=task_patch.priority,
                    estimated_minutes=task_patch.estimated_minutes
                ))
        
        # Build response metadata
        response_metadata = {
            "provider_used": request.config.provider,
            "model_used": request.config.model_name or "default",
            "milestones_created": len(task_metadata),
            "total_estimated_hours": project_metadata.estimated_total_hours if project_metadata else None,
            "agent_cached": True,  # Indicate this used a cached agent
            "cache_info": {
                "cache_size": get_cached_planner_agent.cache_info().currsize,
                "cache_hits": get_cached_planner_agent.cache_info().hits,
                "cache_misses": get_cached_planner_agent.cache_info().misses
            }
        }
        
        logger.info(f"Successfully generated project plan: {project_metadata.name if project_metadata else 'Unknown'}")
        
        return PlannerResponse(
            success=True,
            project=project_metadata,
            tasks=task_metadata,
            raw_patch=result.model_dump(),
            metadata=response_metadata
        )
        
    except JSONParsingError as e:
        logger.error(f"JSON parsing error: {e}")
        return PlannerResponse(
            success=False,
            error=f"The AI model returned invalid JSON. This may be due to a complex request or model limitations. Please try again or simplify your project idea."
        )
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return PlannerResponse(
            success=False,
            error=f"The AI model returned data that doesn't match the expected format. Please try again."
        )
        
    except AgentError as e:
        logger.error(f"Agent error: {e}")
        return PlannerResponse(
            success=False,
            error=f"The AI agent encountered an error: {str(e)}"
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Invalid configuration",
                details={"message": str(e)},
                code="INVALID_CONFIG"
            ).dict()
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return PlannerResponse(
            success=False,
            error="An unexpected error occurred while generating the project plan. Please try again."
        )


@router.get("/providers", response_model=ProvidersResponse)
async def get_providers(settings = Depends(get_settings_dependency)):
    """
    Get available AI providers and their models.
    
    Returns information about all configured AI providers including their
    available models and whether they have API keys configured.
    """
    try:
        providers = []
        
        # Map provider names to display names
        provider_display_names = {
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "gemini": "Google Gemini",
            "xai": "xAI"
        }
        
        # Get provider configuration
        provider_config = settings.providers
        
        for provider_name, provider_info in provider_config.providers.items():
            # Check if API key is available
            api_key = settings.get_api_key(provider_name)
            is_available = api_key is not None
            
            # Build model list
            models = []
            for model_name in provider_info.models:
                models.append(ProviderModel(
                    name=model_name,
                    display_name=model_name,
                    is_default=(model_name == provider_info.default)
                ))
            
            providers.append(ProviderInfo(
                name=provider_name,
                display_name=provider_display_names.get(provider_name, provider_name.title()),
                models=models,
                is_available=is_available,
                is_default=(provider_name == settings.default_provider)
            ))
        
        logger.info(f"Returned {len(providers)} providers")
        
        return ProvidersResponse(
            providers=providers,
            default_provider=settings.default_provider
        )
        
    except Exception as e:
        logger.error(f"Error getting providers: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to retrieve provider information",
                details={"message": str(e)},
                code="PROVIDER_ERROR"
            ).dict()
        )


@router.get("/config", response_model=ConfigResponse)
async def get_config(settings = Depends(get_settings_dependency)):
    """
    Get default configuration for the PlannerAgent.
    
    Returns the default configuration along with provider information
    to help users understand available options.
    """
    try:
        # Get default configuration
        default_config = PlannerConfig(
            provider=settings.default_provider,
            model_name=None,  # Will use provider default
            create_milestones=True,
            max_milestones=5,
            max_retries=2,
            retry_delay=1.0
        )
        
        # Get provider information
        providers_response = await get_providers(settings)
        
        logger.info("Returned default configuration")
        
        return ConfigResponse(
            default_config=default_config,
            provider_info=providers_response
        )
        
    except Exception as e:
        logger.error(f"Error getting config: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error="Failed to retrieve configuration",
                details={"message": str(e)},
                code="CONFIG_ERROR"
            ).dict()
        )


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics for debugging and monitoring.
    
    Returns information about the agent cache performance.
    """
    cache_info = get_cached_planner_agent.cache_info()
    
    return {
        "cache_size": cache_info.currsize,
        "max_cache_size": cache_info.maxsize,
        "hits": cache_info.hits,
        "misses": cache_info.misses,
        "hit_rate": cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0,
        "cache_keys": []  # Cache keys not directly accessible from lru_cache
    }


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear the agent cache.
    
    Useful for debugging or when you want to force recreation of agents.
    """
    get_cached_planner_agent.cache_clear()
    
    return {
        "success": True,
        "message": "Agent cache cleared successfully"
    }