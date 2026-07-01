# ============================================================
# Middleware — Rate Limiting
# ============================================================

import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter (per-IP, sliding window).

    For production, replace with Redis-backed rate limiting.
    This in-memory version is suitable for single-instance dev/staging.
    """

    _MAX_TRACKED_IPS = 10_000  # Prevent unbounded memory growth
    _CLEANUP_INTERVAL = 100    # Prune stale entries every N requests

    def __init__(self, app, max_requests: int | None = None):
        super().__init__(app)
        settings = get_settings()
        self.max_requests = max_requests or settings.RATE_LIMIT_PER_MINUTE
        self.window_seconds = 60
        # { ip_address: [timestamp, timestamp, ...] }
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._request_counter = 0

        if settings.is_production:
            import logging
            logging.getLogger("skill_tracker").warning(
                "In-memory rate limiter is active. For multi-instance deployments, "
                "switch to Redis-backed rate limiting."
            )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health check
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds

        # Prune old requests outside the window for this IP
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > window_start
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Rate limit exceeded. Try again later.",
                    "data": None,
                    "errors": [{
                        "code": "RATE_LIMITED",
                        "detail": f"Max {self.max_requests} requests per minute",
                    }],
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        self._requests[client_ip].append(now)

        # Periodic full cleanup to prevent unbounded memory growth
        self._request_counter += 1
        if self._request_counter % self._CLEANUP_INTERVAL == 0:
            cutoff = now - self.window_seconds
            stale = [ip for ip, ts_list in self._requests.items()
                     if not any(t > cutoff for t in ts_list)]
            for ip in stale:
                del self._requests[ip]
            # Hard cap: if still over limit, evict oldest-tracked IPs
            if len(self._requests) > self._MAX_TRACKED_IPS:
                overflow = len(self._requests) - self._MAX_TRACKED_IPS
                for ip in list(self._requests.keys())[:overflow]:
                    del self._requests[ip]

        response = await call_next(request)

        # Expose rate-limit headers to clients
        remaining = self.max_requests - len(self._requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))

        return response
