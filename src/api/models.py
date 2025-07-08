"""Pydantic models for API requests and responses."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, computed_field

from ..models.patch import Patch
from ..models.project import ProjectPriority, ProjectStatus
from ..models.task import TaskPriority, TaskStatus


class PlannerConfig(BaseModel):
    """Configuration for the PlannerAgent."""
    
    provider: str = Field(default="openai", description="AI provider to use")
    model_name: Optional[str] = Field(default=None, description="Specific model name (uses provider default if None)")
    create_milestones: bool = Field(default=True, description="Whether to create milestone tasks")
    max_milestones: int = Field(default=5, ge=0, le=8, description="Maximum number of milestone tasks")
    max_retries: int = Field(default=2, ge=0, le=5, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Delay between retries in seconds")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        """Validate provider is supported."""
        supported_providers = ['openai', 'anthropic', 'gemini', 'xai']
        if v not in supported_providers:
            raise ValueError(f"Provider must be one of {supported_providers}")
        return v


class PlannerRequest(BaseModel):
    """Request model for the planner endpoint."""
    
    idea: str = Field(..., min_length=10, max_length=5000, description="Project idea description")
    config: PlannerConfig = Field(default_factory=PlannerConfig, description="Agent configuration")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for planning")
    
    @field_validator('idea')
    @classmethod
    def validate_idea(cls, v):
        """Validate project idea is meaningful."""
        if not v.strip():
            raise ValueError("Project idea cannot be empty")
        return v.strip()


class ProjectMetadata(BaseModel):
    """Project metadata from the generated patch."""
    
    name: str = Field(..., description="Generated project name")
    description: str = Field(..., description="Project description")
    status: ProjectStatus = Field(..., description="Project status")
    priority: ProjectPriority = Field(..., description="Project priority")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    estimated_total_minutes: Optional[int] = Field(default=None, description="Estimated total minutes")
    
    @computed_field
    @property
    def estimated_total_hours(self) -> Optional[float]:
        """Convert estimated total minutes to hours."""
        return self.estimated_total_minutes / 60.0 if self.estimated_total_minutes else None


class TaskMetadata(BaseModel):
    """Task metadata from the generated patch."""
    
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    status: TaskStatus = Field(..., description="Task status")
    priority: TaskPriority = Field(..., description="Task priority")
    estimated_minutes: Optional[int] = Field(default=None, description="Estimated minutes")
    
    @computed_field
    @property
    def estimated_hours(self) -> Optional[float]:
        """Convert estimated minutes to hours."""
        return self.estimated_minutes / 60.0 if self.estimated_minutes else None


class PlannerResponse(BaseModel):
    """Response model for the planner endpoint."""
    
    success: bool = Field(..., description="Whether the request was successful")
    project: Optional[ProjectMetadata] = Field(default=None, description="Generated project metadata")
    tasks: List[TaskMetadata] = Field(default_factory=list, description="Generated milestone tasks")
    raw_patch: Optional[Dict[str, Any]] = Field(default=None, description="Raw patch data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    error: Optional[str] = Field(default=None, description="Error message if request failed")


class ProviderModel(BaseModel):
    """Model information for a provider."""
    
    name: str = Field(..., description="Model name")
    display_name: str = Field(..., description="Human-readable model name")
    description: Optional[str] = Field(default=None, description="Model description")
    is_default: bool = Field(default=False, description="Whether this is the default model")


class ProviderInfo(BaseModel):
    """Provider information."""
    
    name: str = Field(..., description="Provider name")
    display_name: str = Field(..., description="Human-readable provider name")
    models: List[ProviderModel] = Field(..., description="Available models")
    is_available: bool = Field(..., description="Whether provider is available (has API key)")
    is_default: bool = Field(default=False, description="Whether this is the default provider")


class ProvidersResponse(BaseModel):
    """Response model for the providers endpoint."""
    
    providers: List[ProviderInfo] = Field(..., description="Available providers")
    default_provider: str = Field(..., description="Default provider name")


class ConfigResponse(BaseModel):
    """Response model for the config endpoint."""
    
    default_config: PlannerConfig = Field(..., description="Default configuration")
    provider_info: ProvidersResponse = Field(..., description="Provider information")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    code: Optional[str] = Field(default=None, description="Error code")