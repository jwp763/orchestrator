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
    """
    Structured representation of a tool call from the AI agent.
    
    Used to capture the agent's intent to execute specific tools with
    parameters, enabling structured tool execution and validation.
    """
    tool: str = Field(..., description="Tool name to call")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")


class AgentOutput(BaseModel):
    """
    Structured output from the orchestrator agent.
    
    Encapsulates the agent's response including natural language message,
    any tool calls to execute, and confidence in the response quality.
    """
    message: str = Field(..., description="Response message to user")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Tools to execute")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in response")


class OrchestratorAgent:
    """
    Provider-agnostic orchestrator agent using PydanticAI framework.
    
    This agent handles task and project management operations through natural
    language interaction. It supports multiple AI providers (Anthropic, OpenAI,
    Gemini, Groq) and provides structured tool calling for database operations.
    
    Features:
    - Multi-provider AI model support with automatic fallback
    - Structured tool calling for CRUD operations
    - Task-specific prompt optimization
    - Response caching and error handling
    - Context-aware conversation management
    
    Attributes:
        settings: Configuration settings for AI providers and API keys
        _agents: Cached agent instances by provider
        _models: Cached model instances for reuse
    """
    
    def __init__(self, settings=None):
        """
        Initialize the orchestrator agent with configuration.
        
        Args:
            settings (optional): Configuration settings. If None, loads from environment.
        """
        self.settings = settings or get_settings()
        self._agents = {}  # Cache agents by provider
        self._models = {}  # Cache model instances
    
    def _get_model(self, provider: str, model_name: str) -> Model:
        """
        Get or create a model instance for the specified provider.
        
        Creates and caches model instances to avoid repeated initialization.
        Supports Anthropic, OpenAI, Gemini, and XAI (via Groq) providers.
        
        Args:
            provider (str): AI provider name (anthropic, openai, gemini, xai)
            model_name (str): Specific model name for the provider
            
        Returns:
            Model: Configured model instance for the provider
            
        Raises:
            ValueError: If no API key is configured or provider is unsupported
            
        Example:
            >>> model = agent._get_model("anthropic", "claude-3-sonnet-20240229")
            >>> isinstance(model, AnthropicModel)
            True
        """
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
        """
        Get or create a PydanticAI agent for a specific provider and model.
        
        Creates and caches agent instances with configured tools and prompts.
        Agents are initialized with the orchestrator toolset for database
        operations and task management.
        
        Args:
            provider (str): AI provider name
            model_name (str): Specific model name
            
        Returns:
            Agent[None, AgentOutput]: Configured PydanticAI agent instance
            
        Note:
            Agents are cached by provider:model combination to improve
            performance for repeated calls.
        """
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
        """
        Process a user request through the appropriate AI model.
        
        Handles model selection based on task type or user preferences,
        constructs appropriate prompts with context, executes the agent,
        and returns structured response with any tool calls.
        
        Args:
            request (AgentRequest): User request containing:
                - message: Natural language input
                - task_type: Optional task type for model selection
                - preferred_provider/model: Optional specific model choice
                - context: Optional conversation context
                
        Returns:
            AgentResponse: Structured response containing:
                - message: Agent's natural language response
                - actions: List of tool calls to execute
                - metadata: Provider info, tokens used, etc.
                
        Raises:
            ValueError: If model selection fails or API keys missing
            Exception: If agent execution fails
            
        Example:
            >>> request = AgentRequest(
            ...     message="Create a new project called 'Website Redesign'",
            ...     task_type="project_management"
            ... )
            >>> response = await agent.process_request(request)
            >>> print(response.message)
            "I'll create the project for you..."
        """
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
        """
        Synchronous wrapper for process_request method.
        
        Provides a blocking interface to the async process_request method
        for use in synchronous contexts like Jupyter notebooks.
        
        Args:
            request (AgentRequest): User request to process
            
        Returns:
            AgentResponse: Same response as async version
            
        Note:
            Creates a new event loop for the async operation.
            Use the async version when possible for better performance.
        """
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.process_request(request))
        finally:
            loop.close()


@lru_cache()
def get_agent() -> OrchestratorAgent:
    """
    Get a cached singleton instance of the orchestrator agent.
    
    Uses LRU cache to ensure only one agent instance is created,
    improving performance by reusing cached models and agents.
    
    Returns:
        OrchestratorAgent: Singleton agent instance with default configuration
        
    Example:
        >>> agent = get_agent()
        >>> response = agent.process_request_sync(request)
    """
    return OrchestratorAgent()