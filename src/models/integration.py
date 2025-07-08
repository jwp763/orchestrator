from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, SecretStr


class IntegrationType(str, Enum):
    MOTION = "motion"
    LINEAR = "linear"
    GITLAB = "gitlab"
    NOTION = "notion"


class IntegrationConfig(BaseModel):
    api_key: Optional[SecretStr] = Field(None, description="API key")
    api_token: Optional[SecretStr] = Field(None, description="API token")
    workspace_id: Optional[str] = Field(None, description="Workspace ID")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    base_url: Optional[str] = Field(None, description="API base URL")
    webhook_secret: Optional[SecretStr] = Field(None, description="Webhook secret")
    additional_config: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration")


class Integration(BaseModel):
    id: str = Field(..., description="Unique integration ID")
    type: IntegrationType = Field(..., description="Integration type")
    name: str = Field(..., description="Integration name")
    enabled: bool = Field(True, description="Whether integration is enabled")
    config: IntegrationConfig = Field(..., description="Integration configuration")
    
    # Sync settings
    sync_enabled: bool = Field(True, description="Whether sync is enabled")
    sync_interval_minutes: int = Field(60, description="Sync interval in minutes")
    last_sync_at: Optional[datetime] = Field(None, description="Last sync timestamp")
    last_sync_status: Optional[str] = Field(None, description="Last sync status")
    
    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str = Field(..., description="Creator ID or name")
    
    model_config = ConfigDict(from_attributes=True)