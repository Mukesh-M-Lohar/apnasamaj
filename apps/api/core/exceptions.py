"""
ApnaSamaj – Custom Exceptions & FastAPI Error Handlers

Domain exceptions are raised from services/repositories and
translated to HTTP responses by the handlers registered on the app.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ── Base Exception ───────────────────────────────────────────────────────


class AppException(Exception):
    """Base exception for all domain errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 400,
        error_code: str = "APP_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# ── Specific Exceptions ─────────────────────────────────────────────────


class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource", resource_id: str = "") -> None:
        super().__init__(
            message=f"{resource} not found" + (f": {resource_id}" if resource_id else ""),
            status_code=404,
            error_code="NOT_FOUND",
        )


class AlreadyExistsException(AppException):
    def __init__(self, resource: str = "Resource", field: str = "") -> None:
        super().__init__(
            message=f"{resource} already exists" + (f" with {field}" if field else ""),
            status_code=409,
            error_code="ALREADY_EXISTS",
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class RateLimitException(AppException):
    def __init__(self, message: str = "Too many requests") -> None:
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMITED",
        )


class OTPException(AppException):
    def __init__(self, message: str = "OTP verification failed") -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="OTP_ERROR",
        )


class TenantException(AppException):
    def __init__(self, message: str = "Tenant context required") -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="TENANT_ERROR",
        )


# ── Error Handlers ───────────────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(_request: Request, _exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                },
            },
        )
