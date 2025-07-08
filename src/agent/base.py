"""Base class for all AI agents with common LLM functionality."""

import json
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union, Type, TypeVar
from functools import lru_cache

from pydantic import BaseModel
from pydantic_core._pydantic_core import ValidationError as PydanticValidationError
from json.decoder import JSONDecodeError
from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.groq import GroqModel

from ..config import get_settings
from ..models.schemas import Patch, ProjectPatch, TaskPatch


T = TypeVar('T', bound=BaseModel)


class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass


class JSONParsingError(AgentError):
    """Raised when JSON parsing fails after all retries."""
    pass


class ValidationError(AgentError):
    """Raised when Pydantic validation fails after all retries."""
    pass


class AgentBase(ABC):
    """
    Abstract base class for all AI agents in the orchestrator system.
    
    Provides common functionality for LLM communication, JSON parsing,
    validation, and retry logic. All concrete agents should inherit from
    this class and implement the abstract get_diff method.
    
    Features:
    - Multi-provider LLM support (Anthropic, OpenAI, Gemini, XAI)
    - Configurable retry mechanism for JSON parsing
    - Automatic Pydantic validation of responses
    - Model caching for performance
    - Structured error handling
    
    Attributes:
        settings: Application configuration settings
        provider: AI provider name (anthropic, openai, etc.)
        model_name: Specific model name
        max_retries: Maximum number of retry attempts for parsing
        retry_delay: Base delay between retries in seconds
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        max_retries: int = 2,
        retry_delay: float = 1.0
    ):
        """
        Initialize the agent base with configuration.
        
        Args:
            provider: AI provider name. If None, uses default from settings
            model_name: Specific model name. If None, uses provider default
            max_retries: Maximum retry attempts for JSON parsing (default: 2)
            retry_delay: Base delay between retries in seconds (default: 1.0)
        """
        self.settings = get_settings()
        self.provider = provider or self.settings.default_provider
        self.model_name = model_name or self._get_default_model()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._model_cache: Dict[str, Model] = {}
    
    def _get_default_model(self) -> str:
        """Get the default model for the current provider."""
        try:
            providers = self.settings.providers
            return providers.providers[self.provider].default
        except (FileNotFoundError, KeyError):
            # Fallback defaults if config is missing
            fallback_models = {
                "anthropic": "claude-3-haiku-20240307",
                "openai": "gpt-4o-mini",
                "gemini": "gemini-1.5-flash",
                "xai": "grok-beta"
            }
            return fallback_models.get(self.provider, "claude-3-haiku-20240307")
    
    @lru_cache(maxsize=10)
    def _get_model(self) -> Model:
        """
        Get or create a model instance for the current provider.
        
        Creates and caches model instances to avoid repeated initialization.
        
        Returns:
            Model: Configured model instance for the provider
            
        Raises:
            ValueError: If no API key is configured or provider is unsupported
        """
        cache_key = f"{self.provider}:{self.model_name}"
        
        if cache_key not in self._model_cache:
            api_key = self.settings.get_api_key(self.provider)
            if not api_key:
                raise ValueError(f"No API key configured for provider: {self.provider}")
            
            if self.provider == "anthropic":
                self._model_cache[cache_key] = AnthropicModel(
                    model_name=self.model_name,
                    api_key=api_key
                )
            elif self.provider == "openai":
                self._model_cache[cache_key] = OpenAIModel(
                    model_name=self.model_name,
                    api_key=api_key
                )
            elif self.provider == "gemini":
                self._model_cache[cache_key] = GeminiModel(
                    model_name=self.model_name,
                    api_key=api_key
                )
            elif self.provider == "xai":
                # Using Groq as a placeholder for XAI
                self._model_cache[cache_key] = GroqModel(
                    model_name=self.model_name,
                    api_key=api_key
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        
        return self._model_cache[cache_key]
    
    def _create_agent(self, system_prompt: str) -> Agent[None, str]:
        """
        Create a PydanticAI agent with the specified system prompt.
        
        Args:
            system_prompt: System prompt to guide the agent's behavior
            
        Returns:
            Agent: Configured PydanticAI agent instance
        """
        model = self._get_model()
        return Agent(
            model=model,
            output_type=str,
            system_prompt=system_prompt
        )
    
    async def _call_llm_with_retry(
        self,
        prompt: str,
        system_prompt: str,
        response_type: Type[T]
    ) -> T:
        """
        Call the LLM with automatic retry logic for JSON parsing and validation.
        
        Implements exponential backoff retry strategy when the LLM returns
        invalid JSON or data that fails Pydantic validation.
        
        Args:
            prompt: User prompt to send to the LLM
            system_prompt: System prompt to guide behavior
            response_type: Pydantic model class to validate response
            
        Returns:
            Validated instance of response_type
            
        Raises:
            JSONParsingError: If JSON parsing fails after all retries
            ValidationError: If Pydantic validation fails after all retries
        """
        agent = self._create_agent(system_prompt)
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Call the LLM
                result = await agent.run(prompt)
                response_text = result.output
                
                # Parse JSON
                try:
                    json_data = json.loads(response_text)
                except JSONDecodeError as e:
                    last_error = e
                    if attempt < self.max_retries:
                        # Add error feedback to next prompt
                        error_prompt = (
                            f"{prompt}\n\n"
                            f"Previous response contained invalid JSON: {e}\n"
                            f"Please respond with valid JSON only."
                        )
                        prompt = error_prompt
                        await self._sleep_with_backoff(attempt)
                        continue
                    else:
                        raise JSONParsingError(
                            f"Failed to parse JSON after {self.max_retries + 1} attempts. "
                            f"Last error: {e}"
                        )
                
                # Validate with Pydantic
                try:
                    return response_type.model_validate(json_data)
                except PydanticValidationError as e:
                    last_error = e
                    if attempt < self.max_retries:
                        # Add validation error feedback to next prompt
                        error_prompt = (
                            f"{prompt}\n\n"
                            f"Previous response failed validation: {e}\n"
                            f"Please ensure the response matches the required schema exactly."
                        )
                        prompt = error_prompt
                        await self._sleep_with_backoff(attempt)
                        continue
                    else:
                        raise ValidationError(
                            f"Failed validation after {self.max_retries + 1} attempts. "
                            f"Last error: {e}"
                        )
                        
            except (JSONParsingError, ValidationError):
                # Let our custom exceptions propagate without catching them
                raise
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    await self._sleep_with_backoff(attempt)
                    continue
                else:
                    # Handle other unexpected exceptions
                    raise AgentError(f"LLM call failed after {self.max_retries + 1} attempts: {e}")
        
        # This should never be reached, but just in case
        raise AgentError(f"Unexpected error in retry loop. Last error: {last_error}")
    
    async def _sleep_with_backoff(self, attempt: int) -> None:
        """
        Sleep with exponential backoff based on attempt number.
        
        Args:
            attempt: Current attempt number (0-indexed)
        """
        delay = self.retry_delay * (2 ** attempt)
        time.sleep(delay)
    
    def _call_llm_with_retry_sync(
        self,
        prompt: str,
        system_prompt: str,
        response_type: Type[T]
    ) -> T:
        """
        Synchronous wrapper for _call_llm_with_retry.
        
        Args:
            prompt: User prompt to send to the LLM
            system_prompt: System prompt to guide behavior
            response_type: Pydantic model class to validate response
            
        Returns:
            Validated instance of response_type
        """
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._call_llm_with_retry(prompt, system_prompt, response_type)
            )
        finally:
            loop.close()
    
    @abstractmethod
    async def get_diff(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Union[Patch, ProjectPatch, TaskPatch]:
        """
        Generate a diff/patch based on user input and context.
        
        This is the main interface method that all concrete agents must implement.
        It should process the user input and return an appropriate patch object.
        
        Args:
            user_input: Natural language input from the user
            context: Optional context information (current project state, etc.)
            
        Returns:
            A patch object (Patch, ProjectPatch, or TaskPatch) representing
            the changes to be applied
            
        Raises:
            AgentError: If the agent fails to generate a valid diff
        """
        pass
    
    def get_diff_sync(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Union[Patch, ProjectPatch, TaskPatch]:
        """
        Synchronous wrapper for get_diff method.
        
        Args:
            user_input: Natural language input from the user
            context: Optional context information
            
        Returns:
            A patch object representing the changes to be applied
        """
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_diff(user_input, context))
        finally:
            loop.close()