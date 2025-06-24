"""Base integration class for all external services"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

from ..models import IntegrationConfig, User
from ..storage import DeltaManager


logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Base exception for integration errors"""

    pass


class BaseIntegration(ABC):
    """Abstract base class for all integrations"""

    def __init__(self, config: IntegrationConfig, delta_manager: DeltaManager):
        self.config = config
        self.delta = delta_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the integration configuration"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test the connection to the external service"""
        pass

    # User operations
    @abstractmethod
    def get_current_user(self) -> Dict[str, Any]:
        """Get the current authenticated user"""
        pass

    @abstractmethod
    def list_users(self) -> List[Dict[str, Any]]:
        """List users from the external service"""
        pass

    # Helper methods to be implemented by subclasses
    @property
    @abstractmethod
    def integration_type(self) -> str:
        """Return the integration type identifier"""
        pass
