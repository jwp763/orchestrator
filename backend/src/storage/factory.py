from typing import Any, Dict

from src.storage.repositories.base import BaseStorageRepository
from src.storage.repositories.delta_repository import DeltaStorageRepository
from src.storage.repositories.sql_repository import SQLStorageRepository


def get_storage_repository(config: Dict[str, Any]) -> BaseStorageRepository:
    """Factory function to get the appropriate storage repository."""
    repo_type = config.get("repository_type", "sql")

    if repo_type == "delta":
        repo = DeltaStorageRepository()
    elif repo_type == "sql":
        repo = SQLStorageRepository()
    else:
        raise ValueError(f"Unknown repository type: {repo_type}")

    repo.initialize(config.get(repo_type, {}))
    return repo
