# PHASE-08 — Legal documents sync, provenance & temporal search

**Status:** P08_T01_REGISTRY_IN_REVIEW / PHASE_07_DEBT_OPEN
**Implementers:** Legal Data Agent / Backend Agent  
**Independent reviewer:** Education Domain SME / Security QA  
**Prerequisite:** PHASE-07 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

**Conditional kickoff exception — 2026-11-15:** the user explicitly instructed
the agent to proceed through Phase 08. Because Phase 07 is not accepted, this
exception is limited to P08-T01's fail-closed official-source registry. All
automated rates are zero until terms/API/security approval exists. P08-T02..T09
and every connector/job/search/RAG implementation remain gated. Evidence: EDU-0061.

## A. Purpose and implementation boundaries
Legal documents sync, provenance & temporal search; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `Official-source adapters`
- `Versioned archive`
- `Human review queue`
- `Search and RAG boundaries`

## C. Detailed execution steps
1. **P08-T01:** Define allowed official sources, usage terms, rate limits and connector capabilities; API preferred where available. Fail-closed registry published in EDU-0061; independent review pending.
2. **P08-T02:** Collect metadata, attachment, source URL and timestamps into raw staging, never assume source completeness.
3. **P08-T03:** Save original bytes, content checksum and retrieval log; retain every observed version.
4. **P08-T04:** Extract PDF/DOCX text with error reporting, preserve original and normalize extracted search text appropriately.
5. **P08-T05:** Model legal relations: amend/repeal/replace/effective-from/transition, with reviewer status.
6. **P08-T06:** Build full-text & accent-insensitive search by code/title/section/school year; semantic search optional.
7. **P08-T07:** Create an AI citation-only assistant that displays original source and states unknown on insufficient evidence.
8. **P08-T08:** Connect reviewed legal policy references to examination/calendars; do not auto-change live grades/schedules.
9. **P08-T09:** Test sync retries, duplicate detection, feed gaps, source poisoning/prompt injection and supersession timeline.

## D. Where files belong
- `backend/app/modules/legal_documents/`
- `backend/app/jobs/legal_sync_jobs.py`
- `frontend/src/features/legal-documents/`

## E. Verification and exit gate
- [ ] Every claim has source/time and reviewed status
- [ ] No legal text changes policies automatically
- [ ] Search historical as-of effective interval
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.
