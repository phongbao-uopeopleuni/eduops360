"""Tests for permission checking logic."""

from uuid import uuid4

from app.modules.auth.constants import ActionType, ResourceType
from app.modules.auth.permissions import (
    AuthorizationRequest,
    Permission,
    Principal,
    Scope,
    can_access_audit_logs,
    can_modify_audit_logs,
    check_authorization,
)


class TestScope:
    """Tests for scope covering logic."""

    def test_null_scope_covers_all(self):
        """NULL scope should cover any specific scope."""
        global_scope = Scope()
        specific_scope = Scope(
            school_id=uuid4(),
            academic_year_id=uuid4(),
            grade_id=5,
        )

        assert global_scope.covers(specific_scope) is True

    def test_specific_scope_covers_matching(self):
        """Specific scope should cover matching scope."""
        school_id = uuid4()
        scope1 = Scope(school_id=school_id)
        scope2 = Scope(school_id=school_id, grade_id=5)

        assert scope1.covers(scope2) is True

    def test_specific_scope_not_covers_different(self):
        """Specific scope should not cover different values."""
        scope1 = Scope(school_id=uuid4())
        scope2 = Scope(school_id=uuid4())  # Different school

        assert scope1.covers(scope2) is False

    def test_grade_scope_matching(self):
        """Grade scope should match correctly."""
        scope1 = Scope(grade_id=5)
        scope2 = Scope(grade_id=5)
        scope3 = Scope(grade_id=6)

        assert scope1.covers(scope2) is True
        assert scope1.covers(scope3) is False


class TestCheckAuthorization:
    """Tests for authorization checking."""

    def test_deny_by_default_no_permissions(self):
        """Should deny when principal has no permissions."""
        principal = Principal(user_id=uuid4(), permissions=frozenset())
        request = AuthorizationRequest(
            action=ActionType.READ,
            resource_type=ResourceType.STUDENT,
            resource_scope=Scope(),
        )

        authorized, reason = check_authorization(principal, request)

        assert authorized is False
        assert "Không có quyền" in reason

    def test_allow_with_matching_permission(self):
        """Should allow when principal has matching permission."""
        user_id = uuid4()
        permission = Permission(
            resource_type=ResourceType.STUDENT,
            action=ActionType.READ,
            scope=Scope(),
        )
        principal = Principal(user_id=user_id, permissions=frozenset([permission]))
        request = AuthorizationRequest(
            action=ActionType.READ,
            resource_type=ResourceType.STUDENT,
            resource_scope=Scope(school_id=uuid4()),
        )

        authorized, reason = check_authorization(principal, request)

        assert authorized is True
        assert reason == ""

    def test_deny_mismatched_action(self):
        """Should deny when action doesn't match."""
        permission = Permission(
            resource_type=ResourceType.STUDENT,
            action=ActionType.READ,
            scope=Scope(),
        )
        principal = Principal(user_id=uuid4(), permissions=frozenset([permission]))
        request = AuthorizationRequest(
            action=ActionType.UPDATE,  # Different action
            resource_type=ResourceType.STUDENT,
            resource_scope=Scope(),
        )

        authorized, _ = check_authorization(principal, request)

        assert authorized is False

    def test_deny_mismatched_resource(self):
        """Should deny when resource type doesn't match."""
        permission = Permission(
            resource_type=ResourceType.STUDENT,
            action=ActionType.READ,
            scope=Scope(),
        )
        principal = Principal(user_id=uuid4(), permissions=frozenset([permission]))
        request = AuthorizationRequest(
            action=ActionType.READ,
            resource_type=ResourceType.GRADE,  # Different resource
            resource_scope=Scope(),
        )

        authorized, _ = check_authorization(principal, request)

        assert authorized is False

    def test_deny_out_of_scope(self):
        """Should deny when request is outside permission scope."""
        school_id = uuid4()
        permission = Permission(
            resource_type=ResourceType.STUDENT,
            action=ActionType.READ,
            scope=Scope(school_id=school_id),
        )
        principal = Principal(user_id=uuid4(), permissions=frozenset([permission]))
        request = AuthorizationRequest(
            action=ActionType.READ,
            resource_type=ResourceType.STUDENT,
            resource_scope=Scope(school_id=uuid4()),  # Different school
        )

        authorized, _ = check_authorization(principal, request)

        assert authorized is False

    def test_deny_self_approval(self):
        """Should deny when approver is same as submitter."""
        user_id = uuid4()
        permission = Permission(
            resource_type=ResourceType.GRADE,
            action=ActionType.LOCK,
            scope=Scope(),
        )
        principal = Principal(user_id=user_id, permissions=frozenset([permission]))
        request = AuthorizationRequest(
            action=ActionType.LOCK,
            resource_type=ResourceType.GRADE,
            resource_scope=Scope(),
            submitter_id=user_id,  # Same as approver
        )

        authorized, reason = check_authorization(principal, request)

        assert authorized is False
        assert "Người phê duyệt" in reason

    def test_deny_approval_without_submitter_id(self):
        """Should deny two-step action when submitter_id is missing (F07)."""
        permission = Permission(
            resource_type=ResourceType.GRADE,
            action=ActionType.LOCK,
            scope=Scope(),
        )
        principal = Principal(user_id=uuid4(), permissions=frozenset([permission]))
        request = AuthorizationRequest(
            action=ActionType.LOCK,
            resource_type=ResourceType.GRADE,
            resource_scope=Scope(),
            submitter_id=None,  # Missing → must be denied
        )

        authorized, reason = check_authorization(principal, request)

        assert authorized is False
        assert "thiếu thông tin người gửi" in reason


class TestAuditLogAccess:
    """Tests for audit log access control."""

    def test_can_access_audit_logs_with_permission(self):
        """Should allow audit log read with permission."""
        permission = Permission(
            resource_type=ResourceType.AUDIT_LOG,
            action=ActionType.READ,
            scope=Scope(),
        )
        principal = Principal(user_id=uuid4(), permissions=frozenset([permission]))

        assert can_access_audit_logs(principal, Scope()) is True

    def test_cannot_access_audit_logs_without_permission(self):
        """Should deny audit log read without permission."""
        principal = Principal(user_id=uuid4(), permissions=frozenset())

        assert can_access_audit_logs(principal, Scope()) is False

    def test_cannot_modify_audit_logs_ever(self):
        """Should ALWAYS deny audit log modification."""
        # Even with every possible permission
        all_permissions = frozenset(
            [
                Permission(ResourceType.AUDIT_LOG, ActionType.DELETE, Scope()),
                Permission(ResourceType.AUDIT_LOG, ActionType.UPDATE, Scope()),
                Permission(ResourceType.AUDIT_LOG, ActionType.CREATE, Scope()),
            ]
        )
        principal = Principal(user_id=uuid4(), permissions=all_permissions)

        # can_modify_audit_logs always returns False
        assert can_modify_audit_logs(principal) is False
