"""Database session management for thread-safe operations."""

import threading
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .sql_models import Base


class DatabaseSessionManager:
    """Thread-safe database session manager."""
    
    def __init__(self, database_url: str = "sqlite:///orchestrator.db"):
        """Initialize the session manager."""
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=False,
            # SQLite specific settings for thread safety
            poolclass=None,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        # Thread-local storage for sessions
        self._local = threading.local()
    
    def get_session(self) -> Session:
        """Get a session for the current thread."""
        if not hasattr(self._local, 'session') or self._local.session is None:
            self._local.session = self.SessionLocal()
        return self._local.session
    
    def close_session(self) -> None:
        """Close the session for the current thread."""
        if hasattr(self._local, 'session') and self._local.session is not None:
            try:
                self._local.session.close()
            except Exception:
                pass  # Ignore close errors
            finally:
                self._local.session = None
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_new_session(self) -> Session:
        """Create a completely new session for isolated operations."""
        return self.SessionLocal()


# Global session manager instance
_session_manager: Optional[DatabaseSessionManager] = None


def get_session_manager() -> DatabaseSessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = DatabaseSessionManager()
    return _session_manager


def get_db_session() -> Session:
    """Dependency function to get a database session."""
    return get_session_manager().get_session()


def close_db_session() -> None:
    """Close the current thread's database session."""
    get_session_manager().close_session()