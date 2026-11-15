"""User and authentication services.

Implements password hashing, account management, and role operations.
All operations that change user/role state MUST be audited.
"""

from datetime import datetime, timedelta

from anyio import CapacityLimiter, to_thread
from anyio.lowlevel import RunVar
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# Password hasher configuration per ADR-0005
_password_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)

# Security constants
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
SESSION_DURATION_HOURS = 24

# A0102-F07 — TẠM, chờ đo tải theo OD-004: số phép Argon2id chạy đồng thời tối đa trên
# một event loop. Mỗi phép dùng 64 MB (memory_cost), nên 4 luồng giới hạn khoảng 256 MB.
PASSWORD_HASH_CONCURRENCY = 4
_password_hash_limiter: RunVar[CapacityLimiter] = RunVar("eduops_password_hash_limiter")


def hash_password(password: str) -> str:
    """Hash a password using Argon2id.

    Args:
        password: Plain text password

    Returns:
        Argon2id hash string containing algorithm parameters and salt
    """
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash.

    Args:
        password: Plain text password to verify
        password_hash: Stored Argon2id hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        _password_hasher.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False
    except InvalidHashError:
        return False


def _current_password_hash_limiter() -> CapacityLimiter:
    """Return the per-event-loop limiter that bounds concurrent Argon2 work."""
    try:
        return _password_hash_limiter.get()
    except LookupError:
        limiter = CapacityLimiter(PASSWORD_HASH_CONCURRENCY)
        _password_hash_limiter.set(limiter)
        return limiter


async def hash_password_async(password: str) -> str:
    """Hash in a bounded worker thread so request handlers never block the event loop."""
    return await to_thread.run_sync(
        hash_password, password, limiter=_current_password_hash_limiter()
    )


async def verify_password_async(password: str, password_hash: str) -> bool:
    """Verify in a bounded worker thread so request handlers never block the event loop."""
    return await to_thread.run_sync(
        verify_password, password, password_hash, limiter=_current_password_hash_limiter()
    )


def needs_rehash(password_hash: str) -> bool:
    """Check if password needs rehashing due to parameter changes.

    Should be called on successful login to upgrade old hashes.

    Args:
        password_hash: Stored Argon2id hash

    Returns:
        True if hash should be regenerated with current parameters
    """
    return _password_hasher.check_needs_rehash(password_hash)


def should_lock_account(failed_attempts: int) -> bool:
    """Check if account should be locked after failed attempts.

    Args:
        failed_attempts: Current number of consecutive failed login attempts

    Returns:
        True if account should be locked
    """
    return failed_attempts >= MAX_FAILED_ATTEMPTS


def calculate_lockout_until() -> datetime:
    """Calculate lockout expiry time.

    Returns:
        Datetime when lockout expires (timezone-aware)
    """
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    return datetime.now(tz) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)


def calculate_session_expiry() -> datetime:
    """Calculate session expiry time.

    Returns:
        Datetime when session expires (timezone-aware)
    """
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("Asia/Ho_Chi_Minh")
    return datetime.now(tz) + timedelta(hours=SESSION_DURATION_HOURS)


def generate_session_token() -> str:
    """Generate a cryptographically secure session token.

    Returns:
        URL-safe base64 encoded random token
    """
    import secrets

    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Hash a session token for storage.

    Uses SHA-256 for fast lookup while maintaining security.
    Session tokens are already high-entropy random values.

    Args:
        token: Raw session token

    Returns:
        Hex-encoded SHA-256 hash
    """
    import hashlib

    return hashlib.sha256(token.encode()).hexdigest()
