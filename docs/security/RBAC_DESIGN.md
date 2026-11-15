# RBAC Design — EduOps 360 Phase 02

**Status:** DESIGN / Phase 02 implementation  
**Created:** 2026-11-12  
**Task:** EDU-0012  
**Open decisions:** OD-007, OD-008, OD-011 chưa được Product Owner chốt; các giá trị dưới đây là TẠM.

## 1. Core Principles

1. **Deny by default:** Mọi API nhạy cảm từ chối nếu không có explicit permission
2. **Backend authorizes:** Frontend guards chỉ phục vụ UX, không phải security layer
3. **Data-driven policy:** Permission matrix lưu trong database, thay đổi không cần deploy code
4. **Scope-based:** Permission gắn với dimensions (school, year, grade, class, subject)
5. **Audited:** Mọi grant/revoke/change được ghi audit trail

## 2. Authorization Model

```
Authorization = f(Principal, Action, Resource, Scope, WorkflowState)
```

### Principal
- User identity (UUID)
- Roles assigned to user
- Active session với valid token

### Action
- CRUD operations: create, read, update, delete
- Domain actions: approve, reject, publish, archive, export, import
- Admin actions: grant_permission, revoke_permission, suspend_user

### Resource
- Resource type: student, enrollment, timetable, grade, audit_log, user, role
- Resource instance ID (optional, for ABAC)

### Scope (TẠM - chờ OD-008)
| Dimension | Type | Description |
|-----------|------|-------------|
| school_id | UUID | Ranh giới trường (DEC-001: một trường MVP) |
| academic_year_id | UUID | Năm học, archived year = read-only |
| grade_id | int | Khối lớp 1-12 |
| class_id | UUID | Lớp cụ thể |
| subject_id | UUID | Môn học (nếu cần) |

### Workflow State
- Các resource có state machine: draft → submitted → approved → published/locked
- Permission có thể depend on state (e.g., chỉ edit khi draft)

## 3. Role Hierarchy (TẠM - chờ OD-008)

```
system_admin
├── school_admin
│   ├── academic_admin
│   │   ├── grade_coordinator
│   │   └── class_teacher
│   └── exam_admin
└── auditor (read-only, cross-scope)
```

| Role | Scope | Description |
|------|-------|-------------|
| system_admin | global | Quản trị hệ thống, không có quyền xóa audit |
| school_admin | school | Quản trị toàn trường |
| academic_admin | school | Quản lý học vụ |
| exam_admin | school | Quản lý khảo thí |
| grade_coordinator | school + grade | Điều phối khối |
| class_teacher | school + class | Giáo viên chủ nhiệm |
| auditor | school | Xem audit logs, không sửa |

## 4. Permission Matrix Schema

### Tables

```sql
-- Role definitions
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(100) NOT NULL,
    description_vi TEXT,
    is_system BOOLEAN DEFAULT FALSE,  -- system roles không xóa được
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Permission definitions
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(100) UNIQUE NOT NULL,  -- e.g. "student:create", "grade:approve"
    resource_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    requires_approval BOOLEAN DEFAULT FALSE,  -- TẠM chờ OD-007
    description_vi TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Role-Permission mapping
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID  -- user who granted
);

-- User-Role assignment with scope
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- FK to users table
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    -- Scope dimensions (TẠM chờ OD-008, nullable = all)
    school_id UUID,
    academic_year_id UUID,
    grade_id INTEGER CHECK (grade_id BETWEEN 1 AND 12),
    class_id UUID,
    subject_id UUID,
    -- Validity
    valid_from TIMESTAMPTZ DEFAULT NOW(),
    valid_until TIMESTAMPTZ,  -- NULL = indefinite
    is_active BOOLEAN DEFAULT TRUE,
    -- Audit
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID,
    revoked_at TIMESTAMPTZ,
    revoked_by UUID,
    revoke_reason TEXT,
    UNIQUE (user_id, role_id, school_id, academic_year_id, grade_id, class_id, subject_id)
);
```

### Seed Data (TẠM)

```sql
-- System roles
INSERT INTO roles (code, name_vi, is_system) VALUES
('system_admin', 'Quản trị viên hệ thống', TRUE),
('school_admin', 'Quản trị viên trường', TRUE),
('academic_admin', 'Quản lý học vụ', TRUE),
('exam_admin', 'Quản lý khảo thí', TRUE),
('grade_coordinator', 'Điều phối viên khối', FALSE),
('class_teacher', 'Giáo viên chủ nhiệm', FALSE),
('auditor', 'Kiểm toán viên', TRUE);

-- Core permissions
INSERT INTO permissions (code, resource_type, action, requires_approval) VALUES
-- User management
('user:create', 'user', 'create', FALSE),
('user:read', 'user', 'read', FALSE),
('user:update', 'user', 'update', FALSE),
('user:suspend', 'user', 'suspend', FALSE),
('user:grant_role', 'user', 'grant_role', FALSE),
('user:revoke_role', 'user', 'revoke_role', FALSE),
-- Student (Phase 03)
('student:create', 'student', 'create', FALSE),
('student:read', 'student', 'read', FALSE),
('student:update', 'student', 'update', FALSE),
('student:import', 'student', 'import', FALSE),  -- TẠM chờ OD-007
-- Grade (Phase 07)
('grade:read', 'grade', 'read', FALSE),
('grade:update', 'grade', 'update', FALSE),
('grade:approve', 'grade', 'approve', TRUE),  -- TẠM chờ OD-007
('grade:lock', 'grade', 'lock', TRUE),  -- TẠM chờ OD-007
-- Timetable (Phase 06)
('timetable:read', 'timetable', 'read', FALSE),
('timetable:update', 'timetable', 'update', FALSE),
('timetable:publish', 'timetable', 'publish', TRUE),  -- TẠM chờ OD-007
-- Audit
('audit:read', 'audit_log', 'read', FALSE);
-- Note: NO delete permission for audit_log
```

## 5. Authorization Flow

```
1. Request arrives with session token
2. Middleware extracts user_id from valid session
3. Load user's active roles with scopes (cached, invalidated on change)
4. For each required permission:
   a. Check if any role grants the permission
   b. Check if role scope covers the requested resource
   c. Check workflow state allows the action
   d. If requires_approval, check approver != submitter
5. Deny if any check fails (fail closed)
6. Log access attempt (success or denial)
```

## 6. Two-Step Approval (TẠM - chờ OD-007)

Actions marked `requires_approval = TRUE`:
- grade:lock — Khóa điểm sau khi nhập
- timetable:publish — Công bố thời khóa biểu
- grade:approve — Phê duyệt điểm
- policy:activate — Kích hoạt chính sách điểm mới

Rules:
- Submitter và Approver phải là principals khác nhau
- Both must have appropriate permissions
- Break-glass requires documented emergency procedure (P02-T09)

## 7. Audit Requirements

Every permission change MUST be audited:
- user_roles INSERT/UPDATE/DELETE → audit_log
- role_permissions INSERT/DELETE → audit_log
- roles INSERT/UPDATE/DELETE → audit_log

Audit fields:
- actor_id, action, resource_type, resource_id
- before_state, after_state (JSON)
- timestamp (TIMESTAMPTZ), request_id
- client_ip, user_agent

## 8. Cache Strategy

- Role-permission mappings: cached in memory, invalidated on any change
- User-role assignments: cached per user, invalidated on user's role change
- Cache invalidation is synchronous before returning success on grant/revoke

## 9. Open Items

| Item | Blocking? | Resolution path |
|------|-----------|-----------------|
| OD-007 exact actions | No (configurable) | Update `requires_approval` in permissions table |
| OD-008 scope dimensions | No (nullable columns) | Add/remove scope columns, update checks |
| OD-011 retention | Yes for production | Define legal basis before storing personal data |
| Runtime DB role | Yes for production | Tách superuser khỏi runtime (EDU-0017) |

## 10. Implementation Files

```
backend/app/modules/auth/
├── __init__.py
├── models.py          # SQLAlchemy models: Role, Permission, UserRole
├── schemas.py         # Pydantic schemas
├── permissions.py     # Permission checking logic
├── guards.py          # FastAPI dependencies for authorization
├── services.py        # User/role management business logic
├── session.py         # Session management
├── router.py          # API endpoints
└── constants.py       # Enums, action codes
```

---

**Lưu ý:** Tài liệu này là thiết kế cho Phase 02. Các giá trị đánh dấu "TẠM" sẽ được cập nhật khi Product Owner chốt OD-007, OD-008.
