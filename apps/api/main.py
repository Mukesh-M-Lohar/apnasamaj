"""
ApnaSamaj – FastAPI Application Entry Point

Wires up:
  • CORS middleware
  • Custom middleware stack (rate limiting, secure headers, request ID, tenant context)
  • Exception handlers
  • API versioning (v1)
  • Module routers
  • Health check endpoint
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.core.config import get_settings
from apps.api.core.exceptions import register_exception_handlers
from apps.api.core.middleware import register_middleware
from apps.api.modules.auth.routes import router as auth_router
from apps.api.modules.tenant.routes import router as community_router
from apps.api.modules.member.routes import router as member_router
from apps.api.modules.family.routes import router as family_router
from apps.api.modules.committee.routes import router as committee_router
from apps.api.modules.donation.routes import router as donation_router
from apps.api.modules.event.routes import router as event_router
from apps.api.modules.volunteer.routes import router as volunteer_router

settings = get_settings()


def create_app() -> FastAPI:
    """Application factory – creates and configures the FastAPI instance."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Open-source community management platform – Connecting Communities Digitally",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom Middleware ────────────────────────────────────────────────
    register_middleware(app)

    # ── Exception Handlers ──────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Health Check ────────────────────────────────────────────────────
    @app.get("/health", tags=["System"])
    async def health_check() -> dict:
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    # ── API v1 Routes ───────────────────────────────────────────────────
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(community_router, prefix=settings.API_V1_PREFIX)
    app.include_router(member_router, prefix=settings.API_V1_PREFIX)
    app.include_router(family_router, prefix=settings.API_V1_PREFIX)
    app.include_router(committee_router, prefix=settings.API_V1_PREFIX)
    app.include_router(donation_router, prefix=settings.API_V1_PREFIX)
    app.include_router(event_router, prefix=settings.API_V1_PREFIX)
    app.include_router(volunteer_router, prefix=settings.API_V1_PREFIX)

    # Future module routers will be added here:
    # app.include_router(committee_router, prefix=settings.API_V1_PREFIX)
    # app.include_router(donation_router, prefix=settings.API_V1_PREFIX)
    # app.include_router(event_router, prefix=settings.API_V1_PREFIX)
    # app.include_router(volunteer_router, prefix=settings.API_V1_PREFIX)
    # app.include_router(complaint_router, prefix=settings.API_V1_PREFIX)

    return app


# ── App Instance ────────────────────────────────────────────────────────
app = create_app()
