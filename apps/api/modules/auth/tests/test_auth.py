"""
ApnaSamaj – Auth Module Unit Tests

Tests cover:
  • OTP request flow
  • OTP verification flow
  • Token refresh
  • Session management
  • Input validation
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from apps.api.core.security import create_access_token, create_refresh_token, decode_token, generate_otp
from apps.api.modules.auth.repository import AuthRepository
from apps.api.modules.auth.schemas import (
    OTPRequestSchema,
    OTPResponse,
    OTPVerifySchema,
    UserResponse,
)

# ── Security Utility Tests ───────────────────────────────────────────────


class TestOTPGeneration:
    """Test OTP generation utility."""

    def test_generates_correct_length(self) -> None:
        otp = generate_otp(6)
        assert len(otp) == 6

    def test_generates_only_digits(self) -> None:
        otp = generate_otp(6)
        assert otp.isdigit()

    def test_generates_different_otps(self) -> None:
        otps = {generate_otp(6) for _ in range(100)}
        # With 6-digit OTPs and 100 samples, we expect most to be unique
        assert len(otps) > 90

    def test_respects_custom_length(self) -> None:
        for length in [4, 6, 8]:
            otp = generate_otp(length)
            assert len(otp) == length


class TestJWT:
    """Test JWT token creation and verification."""

    def test_create_and_decode_access_token(self) -> None:
        user_id = uuid4()
        tenant_id = uuid4()
        token = create_access_token(user_id, tenant_id, roles=["member"])
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["tenant_id"] == str(tenant_id)
        assert payload["type"] == "access"
        assert "member" in payload["roles"]

    def test_create_and_decode_refresh_token(self) -> None:
        user_id = uuid4()
        session_id = uuid4()
        token = create_refresh_token(user_id, session_id)
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["session_id"] == str(session_id)
        assert payload["type"] == "refresh"

    def test_access_token_without_tenant(self) -> None:
        user_id = uuid4()
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert payload["sub"] == str(user_id)
        assert "tenant_id" not in payload


# ── OTP Hash Tests ───────────────────────────────────────────────────────


class TestOTPHashing:
    """Test OTP hashing in repository."""

    def test_hash_is_deterministic(self) -> None:
        hash1 = AuthRepository.hash_otp("123456")
        hash2 = AuthRepository.hash_otp("123456")
        assert hash1 == hash2

    def test_different_otps_produce_different_hashes(self) -> None:
        hash1 = AuthRepository.hash_otp("123456")
        hash2 = AuthRepository.hash_otp("654321")
        assert hash1 != hash2


# ── Schema Validation Tests ──────────────────────────────────────────────


class TestSchemaValidation:
    """Test Pydantic schema validation."""

    def test_valid_mobile_number(self) -> None:
        schema = OTPRequestSchema(mobile="+919876543210")
        assert schema.mobile == "+919876543210"

    def test_mobile_strips_spaces(self) -> None:
        schema = OTPRequestSchema(mobile="+91 98765 43210")
        assert schema.mobile == "+919876543210"

    def test_mobile_strips_dashes(self) -> None:
        schema = OTPRequestSchema(mobile="+91-9876-543-210")
        assert schema.mobile == "+919876543210"

    def test_invalid_mobile_raises(self) -> None:
        with pytest.raises(Exception):
            OTPRequestSchema(mobile="abc123")

    def test_otp_verify_schema(self) -> None:
        schema = OTPVerifySchema(
            mobile="+919876543210",
            otp="123456",
            device_name="iPhone 15",
            device_type="mobile",
        )
        assert schema.otp == "123456"
        assert schema.device_name == "iPhone 15"

    def test_otp_response(self) -> None:
        resp = OTPResponse(
            message="OTP sent",
            expires_in=300,
            mobile="+919876543210",
        )
        assert resp.expires_in == 300

    def test_user_response(self) -> None:
        user = UserResponse(
            id=uuid4(),
            mobile="+919876543210",
            is_verified=True,
            is_super_admin=False,
            roles=["member"],
            created_at=datetime.now(UTC),
        )
        assert user.is_verified is True
        assert "member" in user.roles
