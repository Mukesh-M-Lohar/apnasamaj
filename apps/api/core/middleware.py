"""
ApnaSamaj – Middleware Stack

Middleware applied to every request:
  • TenantContextMiddleware – injects tenant_id into request.state
  • RequestIDMiddleware – generates a unique request ID for tracing
  • SecureHeadersMiddleware – adds security headers (XSS, CSRF, etc.)
  • RateLimitMiddleware – basic in-memory rate limiting (use Redis in prod)
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from apps.api.core.config import get_settings
from apps.api.core.exceptions import RateLimitException

settings = get_settings()


# ── Request ID ───────────────────────────────────────────────────────────


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request/response for tracing."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ── Secure Headers ───────────────────────────────────────────────────────


class SecureHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard security headers to all responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


# ── Rate Limiting (in-memory – replace with Redis in production) ─────────


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple sliding-window rate limiter.
    In production, swap this for a Redis-backed implementation.
    """

    def __init__(self, app: FastAPI, max_requests: int = 60, window_seconds: int = 60) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/docs", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        self._requests[client_ip] = [t for t in self._requests[client_ip] if t > window_start]

        if len(self._requests[client_ip]) >= self.max_requests:
            raise RateLimitException()

        self._requests[client_ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - len(self._requests[client_ip]))
        return response


# ── Tenant Context ───────────────────────────────────────────────────────


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Extract tenant context from the JWT payload (set by auth dependency)
    and store it on request.state for downstream use.

    Also accepts X-Tenant-ID header for Super Admin cross-tenant access.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Tenant can be set via header (for super admin) or via JWT
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            request.state.tenant_id = tenant_header
        response = await call_next(request)
        return response


# ── Register All Middleware ──────────────────────────────────────────────


def register_middleware(app: FastAPI) -> None:
    """Register all middleware on the FastAPI app instance."""
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecureHeadersMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=settings.RATE_LIMIT_PER_MINUTE,
        window_seconds=60,
    )
    app.add_middleware(TenantContextMiddleware)
