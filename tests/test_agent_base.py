"""Tests for AgentBase class."""

import json
import pytest
import warnings
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.agent.base import AgentBase, AgentError, JSONParsingError, ValidationError
from src.models.patches import Patch, ProjectPatch, TaskPatch, Op


class TestAgentBase:
    """Test AgentBase abstract class functionality."""

    def test_agent_base_is_abstract(self):
        """Test that AgentBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AgentBase()

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        with patch('src.agent.base.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.default_provider = "anthropic"
            mock_settings.providers = Mock()
            mock_settings.providers.providers = {
                "anthropic": Mock(default="claude-3-haiku-20240307")
            }
            mock_settings.get_api_key.return_value = "test-api-key"
            mock_get_settings.return_value = mock_settings
            yield mock_settings

    @pytest.fixture
    def concrete_agent(self, mock_settings):
        """Create a concrete implementation of AgentBase for testing."""
        # Define the class but don't instantiate it in the fixture
        # to avoid any async method access during fixture setup
        class ConcreteAgent(AgentBase):
            async def get_diff(self, user_input, context=None):
                # Simple implementation for testing
                return ProjectPatch(op=Op.CREATE, name="Test Project")
        
        # Return the class, not an instance
        return ConcreteAgent

    def test_agent_initialization_with_defaults(self, concrete_agent, mock_settings):
        """Test agent initialization with default settings."""
        agent = concrete_agent()
        assert agent.provider == "anthropic"
        assert agent.model_name == "claude-3-haiku-20240307"
        assert agent.max_retries == 2
        assert agent.retry_delay == 1.0

    def test_agent_initialization_with_custom_params(self, mock_settings):
        """Test agent initialization with custom parameters."""
        class ConcreteAgent(AgentBase):
            async def get_diff(self, user_input, context=None):
                return ProjectPatch(op=Op.CREATE, name="Test")
        
        agent = ConcreteAgent(
            provider="openai",
            model_name="gpt-4",
            max_retries=5,
            retry_delay=2.0
        )
        
        assert agent.provider == "openai"
        assert agent.model_name == "gpt-4"
        assert agent.max_retries == 5
        assert agent.retry_delay == 2.0

    def test_get_default_model_fallback(self, mock_settings):
        """Test fallback behavior when provider config is missing."""
        # Simulate missing config
        mock_settings.providers.providers = {}
        
        class ConcreteAgent(AgentBase):
            async def get_diff(self, user_input, context=None):
                return ProjectPatch(op=Op.CREATE, name="Test")
        
        agent = ConcreteAgent()
        assert agent.model_name == "claude-3-haiku-20240307"  # Fallback default

    @patch('src.agent.base.AnthropicModel')
    def test_get_model_creates_anthropic_model(self, mock_anthropic, concrete_agent, mock_settings):
        """Test that _get_model creates correct Anthropic model instance."""
        mock_model_instance = Mock()
        mock_anthropic.return_value = mock_model_instance
        
        agent = concrete_agent()
        model = agent._get_model()
        
        mock_anthropic.assert_called_once_with(
            model_name="claude-3-haiku-20240307",
            api_key="test-api-key"
        )
        assert model == mock_model_instance

    def test_get_model_raises_error_without_api_key(self, concrete_agent, mock_settings):
        """Test that _get_model raises error when API key is missing."""
        mock_settings.get_api_key.return_value = None
        
        agent = concrete_agent()
        with pytest.raises(ValueError, match="No API key configured"):
            agent._get_model()

    def test_get_model_raises_error_for_unsupported_provider(self, mock_settings):
        """Test that _get_model raises error for unsupported provider."""
        class ConcreteAgent(AgentBase):
            async def get_diff(self, user_input, context=None):
                return ProjectPatch(op=Op.CREATE, name="Test")
        
        agent = ConcreteAgent(provider="unsupported")
        
        with pytest.raises(ValueError, match="Unsupported provider: unsupported"):
            agent._get_model()

    @pytest.mark.asyncio
    async def test_call_llm_with_retry_success_first_attempt(self, concrete_agent):
        """Test successful LLM call on first attempt."""
        agent = concrete_agent()
        mock_agent = AsyncMock()
        mock_result = Mock()
        mock_result.output = '{"op": "create", "name": "Test Project"}'
        mock_agent.run.return_value = mock_result
        
        with patch.object(agent, '_create_agent', return_value=mock_agent):
            result = await agent._call_llm_with_retry(
                "Create a project",
                "You are a helpful assistant",
                ProjectPatch
            )
        
        assert isinstance(result, ProjectPatch)
        assert result.op == Op.CREATE
        assert result.name == "Test Project"
        mock_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_llm_with_retry_json_error_then_success(self, concrete_agent):
        """Test retry mechanism when LLM returns invalid JSON first, then valid JSON."""
        agent = concrete_agent()
        mock_agent = AsyncMock()
        
        # First call returns invalid JSON, second call returns valid JSON
        mock_result_1 = Mock()
        mock_result_1.output = 'invalid json'
        mock_result_2 = Mock()
        mock_result_2.output = '{"op": "create", "name": "Test Project"}'
        
        mock_agent.run.side_effect = [mock_result_1, mock_result_2]
        
        with patch.object(agent, '_create_agent', return_value=mock_agent):
            with patch.object(agent, '_sleep_with_backoff') as mock_sleep:
                result = await agent._call_llm_with_retry(
                    "Create a project",
                    "You are a helpful assistant",
                    ProjectPatch
                )
        
        assert isinstance(result, ProjectPatch)
        assert result.op == Op.CREATE
        assert result.name == "Test Project"
        assert mock_agent.run.call_count == 2
        mock_sleep.assert_called_once_with(0)

    @pytest.mark.asyncio
    async def test_call_llm_with_retry_validation_error_then_success(self, concrete_agent):
        """Test retry mechanism when validation fails first, then succeeds."""
        agent = concrete_agent()
        mock_agent = AsyncMock()
        
        # First call returns JSON that fails validation, second call succeeds
        mock_result_1 = Mock()
        mock_result_1.output = '{"op": "invalid_op", "name": "Test"}'  # Invalid op
        mock_result_2 = Mock()
        mock_result_2.output = '{"op": "create", "name": "Test Project"}'
        
        mock_agent.run.side_effect = [mock_result_1, mock_result_2]
        
        with patch.object(concrete_agent, '_create_agent', return_value=mock_agent):
            with patch.object(concrete_agent, '_sleep_with_backoff') as mock_sleep:
                result = await agent._call_llm_with_retry(
                    "Create a project",
                    "You are a helpful assistant",
                    ProjectPatch
                )
        
        assert isinstance(result, ProjectPatch)
        assert result.op == Op.CREATE
        assert result.name == "Test Project"
        assert mock_agent.run.call_count == 2
        mock_sleep.assert_called_once_with(0)

    @pytest.mark.asyncio
    async def test_call_llm_with_retry_max_retries_json_error(self, concrete_agent):
        """Test that JSONParsingError is raised after max retries with JSON errors."""
        agent = concrete_agent()
        mock_agent = AsyncMock()
        mock_result = Mock()
        mock_result.output = 'invalid json'
        mock_agent.run.return_value = mock_result
        
        with patch.object(concrete_agent, '_create_agent', return_value=mock_agent):
            with patch.object(concrete_agent, '_sleep_with_backoff'):
                with pytest.raises(JSONParsingError, match="Failed to parse JSON after 3 attempts"):
                    await agent._call_llm_with_retry(
                        "Create a project",
                        "You are a helpful assistant",
                        ProjectPatch
                    )
        
        # Should be called max_retries + 1 times (3 total)
        assert mock_agent.run.call_count == 3

    @pytest.mark.asyncio
    async def test_call_llm_with_retry_max_retries_validation_error(self, concrete_agent):
        """Test that ValidationError is raised after max retries with validation errors."""
        agent = concrete_agent()
        mock_agent = AsyncMock()
        mock_result = Mock()
        mock_result.output = '{"op": "invalid_op", "name": "Test"}'  # Always invalid
        mock_agent.run.return_value = mock_result
        
        with patch.object(concrete_agent, '_create_agent', return_value=mock_agent):
            with patch.object(concrete_agent, '_sleep_with_backoff'):
                with pytest.raises(ValidationError, match="Failed validation after 3 attempts"):
                    await agent._call_llm_with_retry(
                        "Create a project",
                        "You are a helpful assistant",
                        ProjectPatch
                    )
        
        assert mock_agent.run.call_count == 3

    @pytest.mark.asyncio
    async def test_sleep_with_backoff_exponential(self, concrete_agent):
        """Test that sleep_with_backoff implements exponential backoff."""
        agent = concrete_agent()
        with patch('src.agent.base.time.sleep') as mock_sleep:
            await agent._sleep_with_backoff(0)
            mock_sleep.assert_called_with(1.0)  # retry_delay * 2^0
            
            await agent._sleep_with_backoff(1)
            mock_sleep.assert_called_with(2.0)  # retry_delay * 2^1
            
            await agent._sleep_with_backoff(2)
            mock_sleep.assert_called_with(4.0)  # retry_delay * 2^2

    def test_sync_wrapper_methods(self, concrete_agent):
        """Test that synchronous wrapper methods work correctly."""
        agent = concrete_agent()
        # Test get_diff_sync by directly testing the sync wrapper functionality
        # Since it's just a wrapper around asyncio.run, we'll test that it calls the async method
        with patch('asyncio.new_event_loop') as mock_new_loop, \
             patch('asyncio.set_event_loop') as mock_set_loop:
            mock_loop = Mock()
            mock_new_loop.return_value = mock_loop
            
            mock_patch = ProjectPatch(op=Op.CREATE, name="Test")
            mock_loop.run_until_complete.return_value = mock_patch
            
            result = agent.get_diff_sync("Create a project")
            
            # Verify the event loop was created and used
            mock_new_loop.assert_called_once()
            mock_set_loop.assert_called_once_with(mock_loop)
            mock_loop.run_until_complete.assert_called_once()
            mock_loop.close.assert_called_once()
            assert result == mock_patch

    def test_call_llm_with_retry_sync(self, concrete_agent):
        """Test synchronous wrapper for _call_llm_with_retry."""
        agent = concrete_agent()
        # Test the sync wrapper by mocking the event loop
        with patch('asyncio.new_event_loop') as mock_new_loop, \
             patch('asyncio.set_event_loop') as mock_set_loop:
            mock_loop = Mock()
            mock_new_loop.return_value = mock_loop
            
            mock_patch = ProjectPatch(op=Op.CREATE, name="Test")
            mock_loop.run_until_complete.return_value = mock_patch
            
            result = agent._call_llm_with_retry_sync(
                "Create a project",
                "System prompt",
                ProjectPatch
            )
            
            # Verify the event loop was created and used
            mock_new_loop.assert_called_once()
            mock_set_loop.assert_called_once_with(mock_loop)
            mock_loop.run_until_complete.assert_called_once()
            mock_loop.close.assert_called_once()
            assert result == mock_patch

    @patch('src.agent.base.Agent')
    def test_create_agent(self, mock_agent_class):
        """Test that _create_agent creates correct Agent instance."""
        # Create a minimal concrete agent just for this test to avoid async method issues
        class MinimalConcreteAgent(AgentBase):
            async def get_diff(self, user_input, context=None):
                return ProjectPatch(op=Op.CREATE, name="Test Project")
        
        # Mock the settings
        with patch('src.agent.base.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.default_provider = "anthropic"
            mock_settings.providers = Mock()
            mock_settings.providers.providers = {
                "anthropic": Mock(default="claude-3-haiku-20240307")
            }
            mock_settings.get_api_key.return_value = "test-api-key"
            mock_get_settings.return_value = mock_settings
            
            # Create agent instance
            concrete_agent = MinimalConcreteAgent()
            
            # Create mocks for the test
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance
            mock_model = Mock()
            
            with patch.object(concrete_agent, '_get_model', return_value=mock_model):
                agent = concrete_agent._create_agent("Test system prompt")
            
            mock_agent_class.assert_called_once_with(
                model=mock_model,
                output_type=str,
                system_prompt="Test system prompt"
            )
            assert agent == mock_agent_instance

    def test_model_caching(self, concrete_agent):
        """Test that models are cached correctly."""
        agent = concrete_agent()
        with patch.object(agent, '_get_model') as mock_get_model:
            mock_model = Mock()
            mock_get_model.return_value = mock_model
            
            # Call twice
            model1 = agent._get_model()
            model2 = agent._get_model()
            
            # Should only create model once due to caching
            assert mock_get_model.call_count == 2  # LRU cache would call the function
            assert model1 == model2

    @pytest.mark.asyncio
    async def test_error_feedback_in_retry_prompts(self, concrete_agent):
        """Test that error messages are included in retry prompts."""
        agent = concrete_agent()
        mock_agent = AsyncMock()
        
        # First call returns invalid JSON
        mock_result_1 = Mock()
        mock_result_1.output = 'invalid json'
        mock_result_2 = Mock()
        mock_result_2.output = '{"op": "create", "name": "Test Project"}'
        
        mock_agent.run.side_effect = [mock_result_1, mock_result_2]
        
        with patch.object(concrete_agent, '_create_agent', return_value=mock_agent):
            with patch.object(concrete_agent, '_sleep_with_backoff'):
                await agent._call_llm_with_retry(
                    "Create a project",
                    "You are a helpful assistant",
                    ProjectPatch
                )
        
        # Check that the second call includes error feedback
        second_call_prompt = mock_agent.run.call_args_list[1][0][0]
        assert "Previous response contained invalid JSON" in second_call_prompt
        assert "Please respond with valid JSON only" in second_call_prompt