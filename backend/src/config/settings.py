import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings


class ProviderConfig(BaseModel):
    """
    Configuration for a single AI provider.

    Defines available models, default model selection, and environment
    variable for API key retrieval.
    """

    models: List[str]
    default: str
    api_key_env: str


class SelectionRule(BaseModel):
    """
    Rules for automatic provider and model selection.

    Defines preferences for different task types to optimize
    performance, cost, and capabilities.
    """

    preferred: List[str]
    model_preference: List[str]


class ProvidersConfig(BaseModel):
    """
    Complete provider configuration loaded from YAML.

    Contains all provider definitions and task-specific selection
    rules for intelligent model routing.
    """

    providers: Dict[str, ProviderConfig]
    selection_rules: Dict[str, SelectionRule]

    @classmethod
    def from_yaml(cls, path: str) -> "ProvidersConfig":
        """
        Load provider configuration from YAML file.

        Args:
            path (str): Path to providers.yaml configuration file

        Returns:
            ProvidersConfig: Parsed configuration instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    Centralizes all configuration including database settings, AI provider
    credentials, and integration API keys. Uses Pydantic BaseSettings for
    automatic environment variable loading and validation.

    Features:
    - Automatic environment variable binding
    - Type validation and conversion
    - Default value specification
    - Nested configuration loading from YAML
    """

    # Environment settings
    environment: str = Field("development", description="Environment name (development, staging, production)")
    database_url: str = Field("sqlite:///backend/orchestrator_dev.db", description="Database URL for SQLite")
    api_port: int = Field(8000, description="API server port")
    frontend_port: int = Field(5174, description="Frontend development server port")
    backup_enabled: bool = Field(False, description="Enable automated backups")
    
    # Application settings
    debug: bool = Field(True, description="Debug mode")
    log_level: str = Field("DEBUG", description="Logging level")
    reload: bool = Field(True, description="Auto-reload on code changes")
    
    # Database settings (for Delta/Databricks)
    catalog_name: str = Field("jwp763", description="Delta catalog name")
    schema_name: str = Field("orchestrator", description="Delta schema name")

    @property
    def database_name(self) -> str:
        """
        Get the full database name in catalog.schema format.

        Returns:
            str: Fully qualified database name for Delta operations

        Example:
            >>> settings.database_name
            'jwp763.orchestrator'
        """
        return f"{self.catalog_name}.{self.schema_name}"

    # Provider settings
    default_provider: str = Field("anthropic", description="Default LLM provider")
    default_model: Optional[str] = Field(None, description="Default model (uses provider default if None)")
    providers_config_path: str = Field("configs/providers.yaml", description="Path to providers config")

    # Integration settings
    motion_api_key: Optional[str] = Field(None, description="Motion API key")
    linear_api_key: Optional[str] = Field(None, description="Linear API key")
    gitlab_token: Optional[str] = Field(None, description="GitLab token")
    notion_token: Optional[str] = Field(None, description="Notion token")

    # LLM API keys
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    xai_api_key: Optional[str] = Field(None, description="XAI API key")
    gemini_api_key: Optional[str] = Field(None, description="Google API key")

    # Agent settings
    max_conversation_history: int = Field(20, description="Max messages to keep in context")
    default_temperature: float = Field(0.7, description="Default temperature for LLM")
    max_tokens: int = Field(4096, description="Max tokens per response")

    # Sync settings
    enable_auto_sync: bool = Field(True, description="Enable automatic syncing")
    sync_interval_minutes: int = Field(30, description="Default sync interval")

    # Security
    encryption_key: Optional[str] = Field(None, description="Encryption key for sensitive data")

    model_config = ConfigDict(
        env_file=[".env.dev", ".env.staging", ".env.prod", ".env"], 
        env_file_encoding="utf-8"
    )

    @property
    def providers(self) -> ProvidersConfig:
        """
        Load and cache providers configuration from YAML file.

        Returns:
            ProvidersConfig: Provider definitions and selection rules

        Raises:
            FileNotFoundError: If providers config file is missing
        """
        return ProvidersConfig.from_yaml(self.providers_config_path)

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for the specified AI provider.

        Retrieves API keys from environment variables using the provider-specific
        environment variable names.

        Args:
            provider (str): Provider name (anthropic, openai, xai, google)

        Returns:
            Optional[str]: API key if configured, None otherwise

        Example:
            >>> settings.get_api_key("anthropic")
            'sk-ant-...'
        """
        key_mapping = {
            "anthropic": self.anthropic_api_key,
            "openai": self.openai_api_key,
            "xai": self.xai_api_key,
            "gemini": self.gemini_api_key,
        }
        return key_mapping.get(provider)

    def get_model_for_task(self, task_type: str) -> tuple[str, str]:
        """
        Get the optimal provider and model for a specific task type.

        Uses configured selection rules to choose the best AI provider
        and model based on task requirements, availability, and preferences.

        Args:
            task_type (str): Type of task (complex_reasoning, quick_tasks, etc.)

        Returns:
            tuple[str, str]: (provider_name, model_name) pair

        Example:
            >>> provider, model = settings.get_model_for_task("complex_reasoning")
            >>> provider, model
            ('anthropic', 'claude-3-opus-20240229')
        """
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

    def validate_required_api_keys(self) -> tuple[bool, list[str]]:
        """
        Validate that required API keys are configured.
        
        Returns:
            tuple[bool, list[str]]: (is_valid, missing_keys)
        """
        required_keys = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
        missing_keys = []
        
        for key in required_keys:
            # Check if the corresponding setting is None or empty
            setting_name = key.lower()
            value = getattr(self, setting_name, None)
            if not value:
                missing_keys.append(key)
        
        return len(missing_keys) == 0, missing_keys

    def validate_database_connection(self) -> tuple[bool, Optional[str]]:
        """
        Validate database connection.
        
        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            import sqlalchemy
            from pathlib import Path
            
            if self.database_url.startswith("sqlite:///"):
                # SQLite validation
                db_path = self.database_url.replace("sqlite:///", "")
                if not os.path.isabs(db_path):
                    # Relative path - check if parent directory exists
                    parent_dir = Path(db_path).parent
                    if not parent_dir.exists():
                        return False, f"Database directory does not exist: {parent_dir}"
                
                # Try to create engine and connect
                engine = sqlalchemy.create_engine(self.database_url)
                with engine.connect() as conn:
                    conn.execute(sqlalchemy.text("SELECT 1"))
                return True, None
            else:
                # PostgreSQL or other database validation
                engine = sqlalchemy.create_engine(self.database_url)
                with engine.connect() as conn:
                    conn.execute(sqlalchemy.text("SELECT 1"))
                return True, None
                
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"

    def validate_startup_configuration(self) -> Any:
        """
        Perform comprehensive startup validation.
        
        Returns:
            ValidationResult: Comprehensive validation results
        """
        from dataclasses import dataclass
        
        @dataclass
        class ValidationResult:
            is_valid: bool
            errors: list[dict]
            warnings: list[dict]
        
        errors = []
        warnings = []
        
        # Validate API keys
        api_valid, missing_keys = self.validate_required_api_keys()
        if not api_valid:
            for key in missing_keys:
                errors.append({
                    "type": "missing_api_key",
                    "message": f"{key} is required for AI provider functionality",
                    "action": f"Set {key} in .env.local file"
                })
        
        # Validate database connection
        db_valid, db_error = self.validate_database_connection()
        if not db_valid:
            errors.append({
                "type": "database_connection",
                "message": f"Database connection failed: {db_error}",
                "action": "Check database configuration and ensure database is accessible"
            })
        
        # Add warnings for optional configurations
        if not self.xai_api_key:
            warnings.append({
                "type": "optional_api_key",
                "message": "XAI_API_KEY is not configured",
                "action": "Add XAI API key for additional provider support"
            })
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


@lru_cache()
def get_settings() -> Settings:
    """
    Get a cached singleton instance of application settings.

    Uses LRU cache to ensure settings are loaded only once and reused
    across the application, improving performance and consistency.

    Returns:
        Settings: Singleton settings instance with all configuration loaded

    Example:
        >>> settings = get_settings()
        >>> settings.database_name
        'jwp763.orchestrator'
    """
    return Settings()
