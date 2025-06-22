from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str = Field(..., description="User name")
    email: Optional[str] = Field(None, description="User email")
    
    # Integration user IDs
    motion_user_id: Optional[str] = Field(None, description="Motion user ID")
    linear_user_id: Optional[str] = Field(None, description="Linear user ID")
    notion_user_id: Optional[str] = Field(None, description="Notion user ID")
    gitlab_user_id: Optional[str] = Field(None, description="GitLab user ID")


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    motion_user_id: Optional[str] = None
    linear_user_id: Optional[str] = None
    notion_user_id: Optional[str] = None
    gitlab_user_id: Optional[str] = None


class User(UserBase):
    id: str = Field(..., description="Unique user ID")
    is_active: bool = Field(True, description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True