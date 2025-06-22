from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    message: str = Field(..., description="User message to agent")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    project_id: Optional[str] = Field(None, description="Current project context")
    task_id: Optional[str] = Field(None, description="Current task context")
    
    # Model preferences
    preferred_provider: Optional[str] = Field(None, description="Preferred LLM provider")
    preferred_model: Optional[str] = Field(None, description="Preferred model")
    task_type: Optional[Literal["complex_reasoning", "quick_tasks", "code_generation", "cost_optimized"]] = Field(
        None, description="Task type for model selection"
    )


class AgentAction(BaseModel):
    action_type: Literal["create_task", "update_task", "create_project", "update_project", "sync", "query"]
    target_integration: Optional[str] = Field(None, description="Target integration for action")
    parameters: Dict[str, Any] = Field(..., description="Action parameters")


class AgentResponse(BaseModel):
    message: str = Field(..., description="Agent response message")
    actions: List[AgentAction] = Field(default_factory=list, description="Suggested actions")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score")
    
    # Model info
    provider_used: str = Field(..., description="LLM provider used")
    model_used: str = Field(..., description="Model used")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    
    # Execution results
    executed_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Executed action results")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")


class AgentContext(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation ID")
    user_id: str = Field(..., description="User ID")
    
    # Conversation history
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation messages")
    
    # Current context
    active_project_id: Optional[str] = Field(None, description="Active project")
    active_task_ids: List[str] = Field(default_factory=list, description="Active tasks")
    
    # Preferences
    default_provider: Optional[str] = Field(None, description="Default LLM provider")
    default_integration: Optional[str] = Field(None, description="Default integration for actions")
    
    # Metadata
    created_at: datetime = Field(..., description="Context creation time")
    updated_at: datetime = Field(..., description="Last update time")
    total_tokens_used: int = Field(0, description="Total tokens used in conversation")
    
    class Config:
        from_attributes = True