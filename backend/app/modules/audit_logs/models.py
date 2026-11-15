"""SQLAlchemy models for audit logging.

Implements immutable audit trail that is written in the same transaction
as high-risk data changes. If audit write fails, the operation fails (fail closed).

Admin CANNOT delete or modify audit records.
"""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditLog(Base):
    """Immutable audit log entry.

    Written in the SAME transaction as the data change.
    Business Admin cannot delete or modify these records.

    Retention policy: TẠM - pending OD-011 (7 years proposed).
    """

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # What happened
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Who did it
    actor_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Context
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # State change
    before_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    extra_data: Mapped[dict[str, Any] | None] = mapped_column("extra_data", JSONB, nullable=True)

    # Timestamps (TIMESTAMPTZ for audit per NFR-TIME)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Reason/notes
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_audit_logs_actor", "actor_id"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id"),
        Index("ix_audit_logs_created", "created_at"),
        Index("ix_audit_logs_action", "action"),
    )


class AuditOutbox(Base):
    """Transactional outbox for audit events.

    Used when audit needs to be delivered to external systems.
    Written in the same transaction as the data change.
    Processed by a separate worker that marks entries as delivered.

    This ensures audit is captured even if external delivery fails temporarily.
    """

    __tablename__ = "audit_outbox"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Link to main audit log
    audit_log_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("audit_logs.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Delivery status
    delivered: Mapped[bool] = mapped_column(nullable=False, default=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (Index("ix_audit_outbox_pending", "delivered", "created_at"),)
