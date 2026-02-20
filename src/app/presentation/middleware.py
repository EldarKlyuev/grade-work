"""Middleware - Request/response interceptors"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class SlowRequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log slow requests (> 1 second)"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and log if slow"""
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        duration = time.perf_counter() - start_time
        
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration:.2f}s (client: {request.client.host if request.client else 'unknown'})"
            )
        else:
            logger.info(
                f"{request.method} {request.url.path} "
                f"completed in {duration:.3f}s"
            )
        
        response.headers["X-Process-Time"] = str(duration)
        
        return response
