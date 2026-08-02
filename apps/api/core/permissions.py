"""
ApnaSamaj – Permission & RBAC System

Design decisions:
  • Permissions are string-based (e.g. "member:read", "donation:create").
  • Roles map to a set of permissions stored in the database.
  • A FastAPI dependency `require_permissions(...)` checks the current
    user's roles against required permissions.
  • Super Admin bypasses all checks.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from fastapi import Depends, Request

from apps.api.core.exceptions import ForbiddenException, UnauthorizedException


# ── Built-in Role Names ─────────────────────────────────────────────────

class RoleName(StrEnum):
    SUPER_ADMIN = "super_admin"
    COMMUNITY_ADMIN = "community_admin"
    PRESIDENT = "president"
    VICE_PRESIDENT = "vice_president"
    CHAIRMAN = "chairman"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    COMMITTEE_MEMBER = "committee_member"
    VOLUNTEER = "volunteer"
    FAMILY_HEAD = "family_head"
    MEMBER = "member"
    GUEST = "guest"


# ── Permission Strings ──────────────────────────────────────────────────

class Permission(StrEnum):
    # Community
    COMMUNITY_CREATE = "community:create"
    COMMUNITY_READ = "community:read"
    COMMUNITY_UPDATE = "community:update"
    COMMUNITY_DELETE = "community:delete"

    # Members
    MEMBER_CREATE = "member:create"
    MEMBER_READ = "member:read"
    MEMBER_UPDATE = "member:update"
    MEMBER_DELETE = "member:delete"
    MEMBER_EXPORT = "member:export"

    # Family
    FAMILY_CREATE = "family:create"
    FAMILY_READ = "family:read"
    FAMILY_UPDATE = "family:update"
    FAMILY_DELETE = "family:delete"

    # Committee
    COMMITTEE_CREATE = "committee:create"
    COMMITTEE_READ = "committee:read"
    COMMITTEE_UPDATE = "committee:update"
    COMMITTEE_DELETE = "committee:delete"

    # Donation
    DONATION_CREATE = "donation:create"
    DONATION_READ = "donation:read"
    DONATION_UPDATE = "donation:update"
    DONATION_DELETE = "donation:delete"
    DONATION_EXPORT = "donation:export"

    # Events
    EVENT_CREATE = "event:create"
    EVENT_READ = "event:read"
    EVENT_UPDATE = "event:update"
    EVENT_DELETE = "event:delete"

    # Volunteers
    VOLUNTEER_CREATE = "volunteer:create"
    VOLUNTEER_READ = "volunteer:read"
    VOLUNTEER_UPDATE = "volunteer:update"
    VOLUNTEER_DELETE = "volunteer:delete"

    # Complaints
    COMPLAINT_CREATE = "complaint:create"
    COMPLAINT_READ = "complaint:read"
    COMPLAINT_UPDATE = "complaint:update"
    COMPLAINT_DELETE = "complaint:delete"

    # Documents
    DOCUMENT_UPLOAD = "document:upload"
    DOCUMENT_READ = "document:read"
    DOCUMENT_DELETE = "document:delete"

    # Notifications
    NOTIFICATION_SEND = "notification:send"
    NOTIFICATION_READ = "notification:read"

    # Reports
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"

    # Settings
    SETTINGS_READ = "settings:read"
    SETTINGS_UPDATE = "settings:update"

    # Audit
    AUDIT_READ = "audit:read"


# ── Default Role → Permission Mapping ────────────────────────────────────

DEFAULT_ROLE_PERMISSIONS: dict[RoleName, list[Permission]] = {
    RoleName.SUPER_ADMIN: list(Permission),  # All permissions
    RoleName.COMMUNITY_ADMIN: [
        Permission.COMMUNITY_READ, Permission.COMMUNITY_UPDATE,
        Permission.MEMBER_CREATE, Permission.MEMBER_READ, Permission.MEMBER_UPDATE, Permission.MEMBER_DELETE,
        Permission.MEMBER_EXPORT,
        Permission.FAMILY_CREATE, Permission.FAMILY_READ, Permission.FAMILY_UPDATE, Permission.FAMILY_DELETE,
        Permission.COMMITTEE_CREATE, Permission.COMMITTEE_READ, Permission.COMMITTEE_UPDATE, Permission.COMMITTEE_DELETE,
        Permission.DONATION_CREATE, Permission.DONATION_READ, Permission.DONATION_UPDATE, Permission.DONATION_DELETE,
        Permission.DONATION_EXPORT,
        Permission.EVENT_CREATE, Permission.EVENT_READ, Permission.EVENT_UPDATE, Permission.EVENT_DELETE,
        Permission.VOLUNTEER_CREATE, Permission.VOLUNTEER_READ, Permission.VOLUNTEER_UPDATE, Permission.VOLUNTEER_DELETE,
        Permission.COMPLAINT_CREATE, Permission.COMPLAINT_READ, Permission.COMPLAINT_UPDATE, Permission.COMPLAINT_DELETE,
        Permission.DOCUMENT_UPLOAD, Permission.DOCUMENT_READ, Permission.DOCUMENT_DELETE,
        Permission.NOTIFICATION_SEND, Permission.NOTIFICATION_READ,
        Permission.REPORT_VIEW, Permission.REPORT_EXPORT,
        Permission.SETTINGS_READ, Permission.SETTINGS_UPDATE,
        Permission.AUDIT_READ,
    ],
    RoleName.MEMBER: [
        Permission.COMMUNITY_READ,
        Permission.MEMBER_READ,
        Permission.FAMILY_READ,
        Permission.COMMITTEE_READ,
        Permission.DONATION_READ,
        Permission.EVENT_READ,
        Permission.COMPLAINT_CREATE, Permission.COMPLAINT_READ,
        Permission.DOCUMENT_READ,
        Permission.NOTIFICATION_READ,
    ],
    RoleName.GUEST: [
        Permission.COMMUNITY_READ,
        Permission.EVENT_READ,
    ],
}


# ── FastAPI Dependency ───────────────────────────────────────────────────

class RequirePermissions:
    """
    FastAPI dependency that checks whether the current user
    holds ALL of the required permissions.

    Usage::

        @router.get("/members", dependencies=[Depends(RequirePermissions(Permission.MEMBER_READ))])
        async def list_members(...):
            ...
    """

    def __init__(self, *permissions: Permission) -> None:
        self.required = set(permissions)

    async def __call__(self, request: Request) -> None:
        user: dict[str, Any] | None = getattr(request.state, "user", None)
        if not user:
            raise UnauthorizedException()

        user_roles: list[str] = user.get("roles", [])

        # Super admin bypass
        if RoleName.SUPER_ADMIN in user_roles:
            return

        user_permissions: set[str] = set(user.get("permissions", []))

        if not self.required.issubset(user_permissions):
            missing = self.required - user_permissions
            raise ForbiddenException(
                message=f"Missing permissions: {', '.join(sorted(missing))}"
            )
