"""API middleware for session management."""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..storage.session_manager import close_db_session


class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure database sessions are properly closed after each request."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and ensure session cleanup."""
        try:
            response = await call_next(request)
            return response
        finally:
            # Always close the session after the request
            close_db_session()