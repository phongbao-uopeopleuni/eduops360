"""Audit logging service.

Provides transactional audit logging that MUST succeed for high-risk operations.
If audit write fails, the entire operation fails (fail closed).

IMPORTANT: Use write_audit_in_transaction() for high-risk operations.
This ensures audit is written in the same DB transaction as the data change.
"""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit_logs.models import AuditLog, AuditOutbox

# audit_logs.user_agent and sessions.user_agent are VARCHAR(500).
USER_AGENT_MAX_LENGTH = 500


def bound_user_agent(value: str | None) -> str | None:
    """Fit a client-supplied User-Agent into its VARCHAR(500) columns (A0102-F02).

    An over-length header must never make the audit/session insert fail: that failure
    rolls back the failed-login counter together with the audit row.
    """
    return None if value is None else value[:USER_AGENT_MAX_LENGTH]


_SENSITIVE_KEY_PARTS = frozenset(
    {
        "authorization",
        "cookie",
        "csrf",
        "password",
        "secret",
        "session_token",
        "token",
    }
)


def sanitize_audit_data(value: Any, *, depth: int = 0) -> Any:
    """Redact credential-like fields before persistence and bound nesting depth."""
    if depth >= 8:
        return "[TRUNCATED]"
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(part in normalized for part in _SENSITIVE_KEY_PARTS):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = sanitize_audit_data(item, depth=depth + 1)
        return sanitized
    if isinstance(value, (list, tuple)):
        return [sanitize_audit_data(item, depth=depth + 1) for item in value[:100]]
    return value


async def write_audit_in_transaction(
    session: AsyncSession,
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    actor_id: UUID | None = None,
    actor_email: str | None = None,
    request_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    before_state: dict[str, Any] | None = None,
    after_state: dict[str, Any] | None = None,
    extra_data: dict[str, Any] | None = None,
    reason: str | None = None,
    create_outbox: bool = False,
) -> AuditLog:
    """Write an audit log entry within the current transaction.

    This MUST be called within the same transaction as the data change.
    If this fails, the transaction should be rolled back (fail closed).

    Args:
        session: Active SQLAlchemy async session (must be in a transaction)
        action: Action performed (e.g., "create", "update", "delete", "grant_role")
        resource_type: Type of resource affected (e.g., "user", "student", "grade")
        resource_id: ID of the specific resource (optional)
        actor_id: UUID of the user performing the action
        actor_email: Email of the user (for display/search)
        request_id: Request correlation ID
        ip_address: Client IP address
        user_agent: Client user agent
        before_state: State before the change (for updates/deletes)
        after_state: State after the change (for creates/updates)
        extra_data: Additional context
        reason: Human-readable reason for the action
        create_outbox: Also create an outbox entry for external delivery

    Returns:
        The created AuditLog entry

    Raises:
        SQLAlchemyError: If audit write fails (operation should be rolled back)
    """
    # Create audit log entry
    audit_log = AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        actor_id=actor_id,
        actor_email=actor_email,
        request_id=request_id,
        ip_address=ip_address,
        user_agent=bound_user_agent(user_agent),
        before_state=sanitize_audit_data(before_state),
        after_state=sanitize_audit_data(after_state),
        extra_data=sanitize_audit_data(extra_data),
        reason=reason,
    )
    session.add(audit_log)

    # Flush to get the ID (but don't commit - caller controls transaction)
    await session.flush()

    # Create outbox entry if needed
    if create_outbox:
        outbox = AuditOutbox(audit_log_id=audit_log.id)
        session.add(outbox)
        await session.flush()

    return audit_log


def format_state_diff(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> dict[str, Any]:
    """Format state changes for audit display.

    Args:
        before: State before change
        after: State after change

    Returns:
        Dict with changed fields only
    """
    if before is None and after is None:
        return {}

    if before is None:
        return {"created": after}

    if after is None:
        return {"deleted": before}

    changes = {}
    all_keys = set(before.keys()) | set(after.keys())

    for key in all_keys:
        old_val = before.get(key)
        new_val = after.get(key)
        if old_val != new_val:
            changes[key] = {"from": old_val, "to": new_val}

    return changes
