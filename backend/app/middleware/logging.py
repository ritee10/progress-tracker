# ============================================================
# Middleware — Request Logging
# ============================================================

import logging
import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("skill_tracker")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP request with:
    - Request ID (for tracing)
    - Method, path, status code
    - Response time in milliseconds
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        # Attach request_id to request state for downstream use
        request.state.request_id = request_id

        logger.info(
            "[%s] → %s %s",
            request_id,
            request.method,
            request.url.path,
        )

        response: Response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "[%s] ← %s %s → %d (%.1fms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )

        # Add request-id header for client-side tracing
        response.headers["X-Request-ID"] = request_id
        return response
