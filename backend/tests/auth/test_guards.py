from uuid import uuid4

from app.modules.auth.constants import ActionType, ResourceType
from app.modules.auth.guards import can_delegate_role
from app.modules.auth.permissions import Permission, Principal, Scope


def test_role_delegation_requires_every_permission_within_scope() -> None:
    school_id = uuid4()
    year_id = uuid4()
    other_school_id = uuid4()
    principal = Principal(
        user_id=uuid4(),
        permissions=frozenset(
            {
                Permission(
                    resource_type=ResourceType.USER,
                    action=ActionType.READ,
                    scope=Scope(school_id=school_id, academic_year_id=year_id),
                ),
                Permission(
                    resource_type=ResourceType.STUDENT,
                    action=ActionType.READ,
                    scope=Scope(school_id=school_id, academic_year_id=year_id),
                ),
            }
        ),
    )
    role_permissions = [("user", "read"), ("student", "read")]
    assert can_delegate_role(
        principal,
        role_permissions,
        Scope(school_id=school_id, academic_year_id=year_id),
    )
    assert not can_delegate_role(
        principal,
        role_permissions,
        Scope(school_id=other_school_id, academic_year_id=year_id),
    )


def test_role_delegation_denies_empty_or_unknown_policy() -> None:
    principal = Principal(user_id=uuid4(), permissions=frozenset())
    assert not can_delegate_role(principal, [], Scope())
    assert not can_delegate_role(principal, [("unknown", "read")], Scope())
