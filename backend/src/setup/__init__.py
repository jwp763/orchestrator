"""Database setup utilities for Databricks orchestrator"""

# Import migration manager first since it doesn't depend on pyspark
from .migration_manager import MigrationManager

# Only import database_setup if pyspark is available
try:
    from .database_setup import DatabaseSetup, get_validation_queries
    __all__ = ["DatabaseSetup", "get_validation_queries", "MigrationManager"]
except ImportError:
    # pyspark not available, skip database_setup
    __all__ = ["MigrationManager"]
