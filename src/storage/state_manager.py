"""State management for agent conversations"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models import AgentContext, AgentRequest, AgentResponse
from .factory import get_storage_repository

logger = logging.getLogger(__name__)


class StateManager:
    """Manages agent conversation state"""

    def __init__(self, config: Dict[str, Any]):
        self.storage = get_storage_repository(config)

    def create_conversation(self, user_id: str) -> AgentContext:
        """Create a new conversation"""
        context_data = self.delta.create_agent_context(user_id)

        return AgentContext(
            conversation_id=context_data["conversation_id"],
            user_id=user_id,
            messages=[],
            active_project_id=None,
            active_task_ids=[],
            default_provider=None,
            default_integration=None,
            created_at=context_data["created_at"],
            updated_at=context_data["updated_at"],
            total_tokens_used=0,
        )

    def get_conversation(self, conversation_id: str) -> Optional[AgentContext]:
        """Get an existing conversation"""
        context_data = self.delta.get_agent_context(conversation_id)

        if context_data:
            return AgentContext(
                conversation_id=context_data["conversation_id"],
                user_id=context_data["user_id"],
                messages=context_data["messages"],
                active_project_id=context_data.get("active_project_id"),
                active_task_ids=context_data.get("active_task_ids", []),
                default_provider=context_data.get("default_provider"),
                default_integration=context_data.get("default_integration"),
                created_at=context_data["created_at"],
                updated_at=context_data["updated_at"],
                total_tokens_used=context_data.get("total_tokens_used", 0),
            )

        return None

    def add_message(self, conversation_id: str, request: AgentRequest, response: AgentResponse):
        """Add a message exchange to the conversation"""
        context = self.get_conversation(conversation_id)
        if not context:
            logger.error(f"Conversation not found: {conversation_id}")
            return

        # Create message entry
        message = {
            "timestamp": datetime.now().isoformat(),
            "request": request.model_dump(),
            "response": response.model_dump(),
        }

        # Update messages list
        messages = context.messages + [message]

        # Keep only last N messages based on settings
        from ..config import get_settings

        settings = get_settings()
        if len(messages) > settings.max_conversation_history:
            messages = messages[-settings.max_conversation_history :]

        # Update total tokens
        total_tokens = context.total_tokens_used + (response.tokens_used or 0)

        # Update in Delta
        self.delta.update_agent_context(conversation_id, {"messages": messages, "total_tokens_used": total_tokens})

        # Log the interaction
        self.delta.create_agent_log(
            {
                "conversation_id": conversation_id,
                "request": json.dumps(request.model_dump()),
                "response": json.dumps(response.model_dump()),
                "provider_used": response.provider_used,
                "model_used": response.model_used,
                "tokens_used": response.tokens_used,
                "response_time_ms": 0,  # Would need to track this
                "actions_executed": [json.dumps(action.model_dump()) for action in response.executed_actions],
                "errors": response.errors,
            }
        )

    def update_context(self, conversation_id: str, updates: Dict[str, Any]):
        """Update conversation context"""
        allowed_updates = {"active_project_id", "active_task_ids", "default_provider", "default_integration"}

        filtered_updates = {k: v for k, v in updates.items() if k in allowed_updates}

        if filtered_updates:
            self.delta.update_agent_context(conversation_id, filtered_updates)

    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[AgentContext]:
        """Get recent conversations for a user"""
        # In a real implementation, you'd query Delta tables
        # For now, returning empty list
        return []
