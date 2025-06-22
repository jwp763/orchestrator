import os
from typing import Dict, Any, Optional, List
from functools import lru_cache
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ProviderConfig(BaseModel):
    models: List[str]
    default: str
    api_key_env: str
    

class SelectionRule(BaseModel):
    preferred: List[str]
    model_preference: List[str]


class ProvidersConfig(BaseModel):
    providers: Dict[str, ProviderConfig]
    selection_rules: Dict[str, SelectionRule]
    
    @classmethod
    def from_yaml(cls, path: str) -> "ProvidersConfig":
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)


class Settings(BaseSettings):
    # Database settings
    catalog_name: str = Field("jwp763", description="Delta catalog name")
    schema_name: str = Field("orchestrator", description="Delta schema name")
    
    @property
    def database_name(self) -> str:
        """Full database name (catalog.schema)"""
        return f"{self.catalog_name}.{self.schema_name}"
    
    # Provider settings
    default_provider: str = Field("anthropic", description="Default LLM provider")
    default_model: Optional[str] = Field(None, description="Default model (uses provider default if None)")
    providers_config_path: str = Field("configs/providers.yaml", description="Path to providers config")
    
    # Integration settings
    motion_api_key: Optional[str] = Field(None, env="MOTION_API_KEY")
    linear_api_key: Optional[str] = Field(None, env="LINEAR_API_KEY")
    gitlab_token: Optional[str] = Field(None, env="GITLAB_TOKEN")
    notion_token: Optional[str] = Field(None, env="NOTION_TOKEN")
    
    # LLM API keys
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    xai_api_key: Optional[str] = Field(None, env="XAI_API_KEY")
    google_api_key: Optional[str] = Field(None, env="GOOGLE_API_KEY")
    
    # Agent settings
    max_conversation_history: int = Field(20, description="Max messages to keep in context")
    default_temperature: float = Field(0.7, description="Default temperature for LLM")
    max_tokens: int = Field(4096, description="Max tokens per response")
    
    # Sync settings
    enable_auto_sync: bool = Field(True, description="Enable automatic syncing")
    sync_interval_minutes: int = Field(30, description="Default sync interval")
    
    # Security
    encryption_key: Optional[str] = Field(None, env="ORCHESTRATOR_ENCRYPTION_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def providers(self) -> ProvidersConfig:
        """Load providers configuration"""
        return ProvidersConfig.from_yaml(self.providers_config_path)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        key_mapping = {
            "anthropic": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "xai": self.xai_api_key,
            "gemini": self.google_api_key,
        }
        return key_mapping.get(provider)
    
    def get_model_for_task(self, task_type: str) -> tuple[str, str]:
        """Get best provider and model for a task type"""
        selection_rule = self.providers.selection_rules.get(task_type)
        if not selection_rule:
            return self.default_provider, self.default_model or self.providers.providers[self.default_provider].default
        
        # Find first available provider with API key
        for provider in selection_rule.preferred:
            if self.get_api_key(provider):
                # Get preferred model for this provider
                provider_models = self.providers.providers[provider].models
                for model in selection_rule.model_preference:
                    if model in provider_models:
                        return provider, model
                # Fall back to provider default
                return provider, self.providers.providers[provider].default
        
        # Fall back to default
        return self.default_provider, self.default_model or self.providers.providers[self.default_provider].default


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()