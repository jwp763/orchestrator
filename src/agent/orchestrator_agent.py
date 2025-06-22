"""PydanticAI-based orchestrator agent with multi-provider support"""

import json
from typing import Optional, Dict, Any, List, Union
from functools import lru_cache
import logging

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import (
    AnthropicModel,
    OpenAIModel,
    GeminiModel,
    GroqModel,
    Model
)

from ..models import AgentRequest, AgentResponse, AgentAction
from ..config import get_settings
from .prompts import SYSTEM_PROMPT, get_task_prompt
from .tools import AgentTools


logger = logging.getLogger(__name__)


class ToolCall(BaseModel):
    """Structured tool call from the agent"""
    tool: str = Field(..., description="Tool name to call")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")


class AgentOutput(BaseModel):
    """Structured output from the agent"""
    message: str = Field(..., description="Response message to user")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tools to execute")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in response")


class OrchestratorAgent:
    """Provider-agnostic orchestrator agent using PydanticAI"""
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self._agents = {}  # Cache agents by provider
        self._models = {}  # Cache model instances
    
    def _get_model(self, provider: str, model_name: str) -> Model:
        """Get or create a model instance"""
        cache_key = f"{provider}:{model_name}"
        
        if cache_key not in self._models:
            api_key = self.settings.get_api_key(provider)
            if not api_key:
                raise ValueError(f"No API key configured for provider: {provider}")
            
            if provider == "anthropic":
                self._models[cache_key] = AnthropicModel(
                    model_name=model_name,
                    api_key=api_key
                )
            elif provider == "openai":
                self._models[cache_key] = OpenAIModel(
                    model_name=model_name,
                    api_key=api_key
                )
            elif provider == "gemini":
                self._models[cache_key] = GeminiModel(
                    model_name=model_name,
                    api_key=api_key
                )
            elif provider == "xai":
                # Using Groq as a placeholder - you'd implement XAI model
                self._models[cache_key] = GroqModel(
                    model_name=model_name,
                    api_key=api_key
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        
        return self._models[cache_key]
    
    def _get_agent(self, provider: str, model_name: str) -> Agent[None, AgentOutput]:
        """Get or create an agent for a specific provider/model"""
        cache_key = f"{provider}:{model_name}"
        
        if cache_key not in self._agents:
            model = self._get_model(provider, model_name)
            
            # Create agent with structured output
            self._agents[cache_key] = Agent(
                model=model,
                result_type=AgentOutput,
                system_prompt=SYSTEM_PROMPT,
                deps_type=None
            )
        
        return self._agents[cache_key]
    
    async def process_request(self, request: AgentRequest) -> AgentResponse:
        """Process a user request with the appropriate model"""
        # Determine provider and model
        if request.preferred_provider and request.preferred_model:
            provider = request.preferred_provider
            model = request.preferred_model
        elif request.task_type:
            provider, model = self.settings.get_model_for_task(request.task_type)
        else:
            provider = self.settings.default_provider
            model = self.settings.default_model or self.settings.providers.providers[provider].default
        
        logger.info(f"Using {provider}:{model} for request")
        
        # Get appropriate agent
        agent = self._get_agent(provider, model)
        
        # Build prompt
        if request.task_type:
            prompt = get_task_prompt(request.task_type, request.message)
        else:
            prompt = request.message
        
        # Add context if provided
        if request.context:
            prompt += f"\n\nContext: {json.dumps(request.context)}"
        
        if request.project_id:
            prompt += f"\n\nCurrent project: {request.project_id}"
        
        if request.task_id:
            prompt += f"\n\nCurrent task: {request.task_id}"
        
        try:
            # Run the agent
            result = await agent.run(prompt)
            
            # Convert tool calls to actions
            actions = []
            for tool_call in result.data.tool_calls:
                actions.append(AgentAction(
                    action_type=tool_call.tool,
                    parameters=tool_call.parameters,
                    target_integration=tool_call.parameters.get("integration")
                ))
            
            # Build response
            return AgentResponse(
                message=result.data.message,
                actions=actions,
                confidence=result.data.confidence,
                provider_used=provider,
                model_used=model,
                tokens_used=getattr(result, "tokens_used", None),
                executed_actions=[],
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                message=f"I encountered an error processing your request: {str(e)}",
                actions=[],
                confidence=0.0,
                provider_used=provider,
                model_used=model,
                errors=[str(e)]
            )
    
    def process_request_sync(self, request: AgentRequest) -> AgentResponse:
        """Synchronous wrapper for process_request"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.process_request(request))
        finally:
            loop.close()


@lru_cache()
def get_agent() -> OrchestratorAgent:
    """Get a cached agent instance"""
    return OrchestratorAgent()