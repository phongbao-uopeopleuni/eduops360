# ADR-0003 — Action-scoped RBAC with two-step approval

**Date:** 2026-11-12  
**Status:** Accepted as principle; exact action matrix unresolved (OD-007)

## Decision
- Authorization is checked on backend per principal + action + school/year/resource scope + current workflow state.
- Workflow supports `draft → submitted → approved/rejected → published/locked` where applicable.
- Record submitter/approver IDs, timestamps, revision, reason and immutable audit event.
- Default policy for critical changes: approver is not the same human principal as submitter. Any emergency override requires separately approved break-glass procedure and audit.
- No user, including business Admin, can modify protected audit evidence by application permission.

## Consequences
Requires workflow modeling and additional UX states; may slow urgent operations without an authorized emergency policy.

## Outstanding
Confirm exact critical operations and available human approvers before activating production workflows.
