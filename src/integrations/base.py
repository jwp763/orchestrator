"""Base integration class for all external services"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

from ..models import IntegrationConfig, User
from ..storage import DeltaManager


logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """
    Base exception for integration-related errors.
    
    Raised when external service integrations encounter errors such as
    API failures, authentication issues, or data synchronization problems.
    """
    pass


class BaseIntegration(ABC):
    """
    Abstract base class for all external service integrations.
    
    Provides the foundation for implementing integrations with external
    task management systems like Motion, Linear, GitLab, and Notion.
    Defines the required interface for authentication, data operations,
    and synchronization.
    
    Attributes:
        config (IntegrationConfig): Integration configuration and credentials
        delta (DeltaManager): Database manager for local data operations
        logger: Integration-specific logger instance
    """

    def __init__(self, config: IntegrationConfig, delta_manager: DeltaManager):
        """
        Initialize the integration with configuration and database access.
        
        Args:
            config (IntegrationConfig): Integration configuration containing
                credentials, API endpoints, and settings
            delta_manager (DeltaManager): Database manager for local operations
        """
        self.config = config
        self.delta = delta_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the integration configuration and credentials.
        
        Checks that all required configuration parameters are present
        and valid, including API keys, endpoints, and settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise
            
        Raises:
            IntegrationError: If configuration validation fails
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection to the external service.
        
        Performs a lightweight API call to verify that the integration
        is properly configured and can communicate with the external service.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            IntegrationError: If connection test fails with specific error details
        """
        pass

    # User operations
    @abstractmethod
    def get_current_user(self) -> Dict[str, Any]:
        """
        Get information about the current authenticated user.
        
        Retrieves user profile information from the external service
        using the configured authentication credentials.
        
        Returns:
            Dict[str, Any]: User information including:
                - id: External user ID
                - name: Display name
                - email: Email address
                - additional service-specific fields
                
        Raises:
            IntegrationError: If user retrieval fails or user is not authenticated
        """
        pass

    @abstractmethod
    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users accessible through the external service.
        
        Retrieves a list of users that the authenticated account can
        access, useful for assignment and collaboration features.
        
        Returns:
            List[Dict[str, Any]]: List of user records with same structure
                as get_current_user()
                
        Raises:
            IntegrationError: If user list retrieval fails
        """
        pass

    # Helper methods to be implemented by subclasses
    @property
    @abstractmethod
    def integration_type(self) -> str:
        """
        Return the integration type identifier.
        
        Provides a unique string identifier for this integration type,
        used for configuration management and service selection.
        
        Returns:
            str: Integration type (e.g., 'motion', 'linear', 'gitlab', 'notion')
        """
        pass
