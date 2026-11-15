# PHASE-04 — Student bulk import/export & Unicode

**Status:** NOT_STARTED / SPEC_ONLY  
**Implementers:** Data Engineer / Backend Agent  
**Independent reviewer:** QA Agent / Security Agent  
**Prerequisite:** PHASE-03 accepted; cross-phase tasks explicitly reviewed.  
**Approval:** domain owner/tech lead; high-impact security, grades, legal or production changes require designated human sign-off.

## A. Purpose and implementation boundaries
Student bulk import/export & Unicode; implement only the scope approved on task journal, not additional speculative modules. Use synthetic data in development.

## B. Expected artifacts
- `CSV v1 schema`
- `Preflight staging`
- `Idempotency`
- `Error download`

## C. Detailed execution steps
1. **P04-T01:** Publish versioned CSV template with stable ASCII headers and Vietnamese field guide.
2. **P04-T02:** Accept UTF-8 and BOM with strict decoding; validate length, delimiter, header schema and file type/size.
3. **P04-T03:** Normalize NFC on appropriate fields; keep immutable student code as TEXT, date ISO and leading zeros.
4. **P04-T04:** Validate referential class/year existence, duplicate within file, duplicate already in DB and scope permission.
5. **P04-T05:** Create staged import batch with row-level valid/invalid/conflicting status and preview endpoint.
6. **P04-T06:** Support explicit create-only vs carefully reviewed update mode; require confirm before DB transaction.
7. **P04-T07:** Use chunked/staged processing, batch idempotency key, audit, retry and operator-readable error file.
8. **P04-T08:** Implement safe export: machine CSV vs Excel-compatible BOM or typed XLSX; protect formula injection.
9. **P04-T09:** Test malformed bytes, NFC/NFD, CSV quotation, huge records, BOM, leading 0 and rollback on failure.

## D. Where files belong
- `backend/app/modules/student_import/`
- `frontend/src/features/students/import/`
- `samples/templates/`

## E. Verification and exit gate
- [ ] Invalid file cannot partially mutate student master unexpectedly
- [ ] Batch duplicate replay idempotent
- [ ] 2,000-row synthetic roundtrip preserves Vietnamese and codes
- [ ] Failing tests written for relevant edge cases; targeted tests and contract/security checks run and evidenced.
- [ ] Task journal has changed files, verification commands, Git states and unresolved issues; `TASK_BOARD.md` regenerated.
- [ ] An independent reviewer and required human authority have approved; do not mark complete based on Agent self-assessment alone.

## F. Failure/rollback plan
On failed validation, do not publish. Preserve logs, isolate defective change, restore prior immutable version/data via controlled procedure; document diagnosis + correction task. For irreversible DB operations, require reviewed backward/forward migration plan before running.

## G. Suggested work breakdown / evidence
Create one `EDU-XXXX` task per coherent feature. Include exact commands and sanitized output, CI job URL or local artifact, git SHA and handoff. Distinguish `planned`, `in_progress`, `in_review`, `done` from `accepted` phase milestone.
