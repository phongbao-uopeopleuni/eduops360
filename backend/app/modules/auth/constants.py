"""Auth module constants and enums.

Values marked TẠM are pending OD-007/OD-008 Product Owner decisions.
Do NOT treat these as confirmed requirements.
"""

from enum import StrEnum


class ActionType(StrEnum):
    """Actions that can be performed on resources."""

    # CRUD
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

    # Domain actions
    APPROVE = "approve"
    REJECT = "reject"
    SUBMIT = "submit"
    PUBLISH = "publish"
    ARCHIVE = "archive"
    LOCK = "lock"
    UNLOCK = "unlock"

    # Data operations
    IMPORT = "import"
    EXPORT = "export"

    # Admin actions
    GRANT_ROLE = "grant_role"
    REVOKE_ROLE = "revoke_role"
    SUSPEND = "suspend"
    ACTIVATE = "activate"
    PASSWORD_RESET = "password_reset"


class ResourceType(StrEnum):
    """Resource types that can be protected."""

    # Phase 02 - IAM
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    SESSION = "session"
    AUDIT_LOG = "audit_log"

    # Phase 03 - Student
    STUDENT = "student"
    ENROLLMENT = "enrollment"
    ACADEMIC_YEAR = "academic_year"
    CLASS = "class"

    # Phase 05-06 - Timetable
    TIMETABLE = "timetable"
    TIMESLOT = "timeslot"
    HOLIDAY = "holiday"

    # Phase 07 - Examination
    GRADE = "grade"
    ASSESSMENT_POLICY = "assessment_policy"

    # Phase 08 - Legal
    LEGAL_DOCUMENT = "legal_document"


class ScopeType(StrEnum):
    """Scope dimensions for permission checks.

    TẠM - chờ OD-008 xác nhận chiều scope chính xác.
    Current dimensions are proposed defaults, NOT confirmed.
    """

    GLOBAL = "global"  # System-wide, no restriction
    SCHOOL = "school"  # school_id boundary (DEC-001: single school MVP)
    ACADEMIC_YEAR = "academic_year"  # year_id, archived = read-only
    GRADE = "grade"  # grade level 1-12
    CLASS = "class"  # specific class
    SUBJECT = "subject"  # specific subject


class RoleCode(StrEnum):
    """System role codes.

    TẠM - role hierarchy pending OD-008.
    """

    SYSTEM_ADMIN = "system_admin"
    SCHOOL_ADMIN = "school_admin"
    ACADEMIC_ADMIN = "academic_admin"
    EXAM_ADMIN = "exam_admin"
    GRADE_COORDINATOR = "grade_coordinator"
    CLASS_TEACHER = "class_teacher"
    AUDITOR = "auditor"


class UserStatus(StrEnum):
    """User account status."""

    PENDING = "pending"  # Invited, not yet activated
    ACTIVE = "active"
    SUSPENDED = "suspended"
    LOCKED = "locked"  # Too many failed attempts


class SessionStatus(StrEnum):
    """Session status."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


# Actions requiring two-step approval
# TẠM - chờ OD-007 xác nhận danh sách chính xác
ACTIONS_REQUIRING_APPROVAL: set[tuple[ResourceType, ActionType]] = {
    (ResourceType.GRADE, ActionType.LOCK),
    (ResourceType.GRADE, ActionType.APPROVE),
    (ResourceType.TIMETABLE, ActionType.PUBLISH),
    (ResourceType.ASSESSMENT_POLICY, ActionType.ACTIVATE),
}


def requires_two_step_approval(resource: ResourceType, action: ActionType) -> bool:
    """Check if an action requires two-step approval.

    TẠM - pending OD-007. This will be data-driven from permissions table.
    """
    return (resource, action) in ACTIONS_REQUIRING_APPROVAL
