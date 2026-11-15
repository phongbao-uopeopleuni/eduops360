"""Tests for auth services."""

from app.modules.auth.services import (
    MAX_FAILED_ATTEMPTS,
    generate_session_token,
    hash_password,
    hash_session_token,
    needs_rehash,
    should_lock_account,
    verify_password,
)


class TestPasswordHashing:
    """Tests for Argon2id password hashing."""

    def test_hash_password_returns_argon2_format(self):
        """Password hash should be Argon2id format."""
        password = "SecureP@ssw0rd123"
        hashed = hash_password(password)

        assert hashed.startswith("$argon2id$")
        assert len(hashed) > 50

    def test_same_password_different_hashes(self):
        """Same password should produce different hashes (salted)."""
        password = "SecureP@ssw0rd123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_verify_correct_password(self):
        """Correct password should verify successfully."""
        password = "SecureP@ssw0rd123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Incorrect password should fail verification."""
        password = "SecureP@ssw0rd123"
        wrong_password = "WrongPassword123"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_empty_password_fails(self):
        """Empty password should fail against any hash."""
        password = "SecureP@ssw0rd123"
        hashed = hash_password(password)

        assert verify_password("", hashed) is False

    def test_unicode_password_supported(self):
        """Vietnamese characters should be supported in passwords."""
        password = "Mật_khẩu_bảo_mật_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_needs_rehash_returns_false_for_current_params(self):
        """Freshly hashed password should not need rehashing."""
        password = "SecureP@ssw0rd123"
        hashed = hash_password(password)

        assert needs_rehash(hashed) is False


class TestSessionToken:
    """Tests for session token generation."""

    def test_generate_session_token_is_unique(self):
        """Each generated token should be unique."""
        tokens = [generate_session_token() for _ in range(100)]

        assert len(set(tokens)) == 100

    def test_generate_session_token_is_url_safe(self):
        """Token should be URL-safe base64."""
        token = generate_session_token()

        # URL-safe characters only
        assert all(c.isalnum() or c in "-_" for c in token)

    def test_generate_session_token_has_sufficient_length(self):
        """Token should have sufficient entropy."""
        token = generate_session_token()

        # 32 bytes = 43 base64 characters
        assert len(token) >= 40

    def test_hash_session_token_is_deterministic(self):
        """Same token should produce same hash."""
        token = "test-token-abc123"
        hash1 = hash_session_token(token)
        hash2 = hash_session_token(token)

        assert hash1 == hash2

    def test_hash_session_token_is_hex(self):
        """Token hash should be hex-encoded SHA-256."""
        token = "test-token"
        hashed = hash_session_token(token)

        assert len(hashed) == 64  # SHA-256 = 64 hex chars
        assert all(c in "0123456789abcdef" for c in hashed)


class TestAccountLockout:
    """Tests for account lockout logic."""

    def test_should_lock_after_max_attempts(self):
        """Account should lock after MAX_FAILED_ATTEMPTS."""
        assert should_lock_account(MAX_FAILED_ATTEMPTS) is True
        assert should_lock_account(MAX_FAILED_ATTEMPTS + 1) is True

    def test_should_not_lock_before_max_attempts(self):
        """Account should not lock before reaching max attempts."""
        assert should_lock_account(0) is False
        assert should_lock_account(MAX_FAILED_ATTEMPTS - 1) is False


class TestPasswordVerificationErrors:
    """Password verification error handling.

    Router lockout/expiry is covered live in tests/integration/test_auth_remediation.py
    (A0102-F08); the unused ``check_account_locked`` helper was removed.
    """

    def test_verify_password_with_corrupt_hash(self):
        """Corrupt hash should return False, not raise (LOW fix)."""
        assert verify_password("password", "not-a-valid-hash") is False


class TestModuleImports:
    """Verify all Phase 02 modules can be imported (F04/F05 fix)."""

    def test_import_auth_constants(self):
        from app.modules.auth import constants  # noqa: F401

    def test_import_auth_models(self):
        from app.modules.auth import models  # noqa: F401

    def test_import_auth_permissions(self):
        from app.modules.auth import permissions  # noqa: F401

    def test_import_auth_schemas(self):
        from app.modules.auth import schemas  # noqa: F401

    def test_import_auth_services(self):
        from app.modules.auth import services  # noqa: F401

    def test_import_audit_logs_models(self):
        from app.modules.audit_logs import models  # noqa: F401

    def test_import_audit_logs_service(self):
        from app.modules.audit_logs import service  # noqa: F401
