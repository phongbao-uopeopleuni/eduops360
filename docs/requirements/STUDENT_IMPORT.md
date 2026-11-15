# EDU Student Bulk Import — Functional Requirement Draft v1.1

## Scope

CSV upload for grades 1–12. Separate persistent `students` identities from year-specific `enrollments`. No direct import of grades/assessment scores via this template; that needs a separate policy-aware pipeline.

## Required header (v1)

`student_code,full_name,date_of_birth,gender,academic_year,grade_level,class_code,enrollment_status`

The published artifact is `samples/templates/students_import_template.csv`;
`samples/templates/STUDENTS_IMPORT_V1.vi.md` records the immutable v1 header,
artifact checksum and Vietnamese field guide. Any header change requires a new
template version.

- `student_code`: required school-scoped identifier, as **text**; preserve leading zeros; future production UI can generate code before import.
- `full_name`: required, nonempty, Vietnamese UTF-8; string length caps.
- `date_of_birth`: ISO `YYYY-MM-DD`; use a date, not a datetime.
- `gender`: configured school vocabulary; default demo accepts Nam/Nữ/Khác/Không khai báo.
- `academic_year`: `YYYY-YYYY`, matching server-selected year and valid following year.
- `grade_level`: integer 1–12.
- `class_code`: existing class in selected school/year; example `8A1`.
- `enrollment_status`: `active`, `transferred`, `withdrawn`, `graduated` (demo vocabulary).

## Upload pipeline

1. Download current versioned template and its documentation.
2. Select school and academic year **in authenticated UI**; enforce permissions on the server.
3. Upload CSV (UTF-8 / UTF-8 BOM; comma delimiter). Limit file size and row count; stream parse for scale.
4. Parse into private staging (`import_batches`, `import_rows`, `import_errors`) with quarantine and retention controls.
5. Verify exact headers, malformed quoting, data validation, class existence, gender/status dictionary, duplicates inside file and conflicts with existing students/enrollments.
6. Preview `valid/new/existing/conflicting/error` counts; report **row number + column + error code** without exposing unnecessary PII. Never commit during preview.
7. Confirm mode: `create_only` (default), or explicit `update_allowed_fields` with permissions and protected fields; require idempotency key.
8. Commit only validated rows through transactional service. Document either all-or-nothing per batch, or chunked commits with explicit partial-success policy and safe retries. Never silently overwrite.
9. Audit actor, school/year scope, counts, checksum, timestamp, policy, batch status and verified results. Log no plaintext student records.
10. Provide completion/error report and status accessible only to authorized users. Destroy files per retention policy.

## Database keys

- `students`: unique `(school_id, student_code)`; student internal UUID remains stable across years.
- `enrollments`: unique `(student_id, academic_year_id)` if one annual placement is allowed; class changes require separate transfer history/temporal membership records.
- `import_batches`: unique idempotency key in school and user scope, SHA-256 file checksum, mode, actor, state.
- `import_rows`: staging-only values with restrictive ACL and retention limit.

## Encoding & security

- Do not rely on spreadsheet app auto-formatting: maintain IDs as text and validate encoded bytes.
- CSV delimiters, quoting and newlines handled by standard parser, never naive `.split(',')`.
- Treat uploaded data as untrusted. Validate formula-triggering prefixes and sanitize spreadsheet **exports** so inputs cannot become executable formulas.
- Limit upload size, apply permission checks and avoid real PII in development, logs, tickets or repository.
- Test replay, concurrency and data race when two users import same codes.

## Local starter validator

`python scripts/validate_students_csv.py samples/templates/students_import_template.csv`

This script checks only file-level/row-level schema. **It does not touch PostgreSQL, verify school/class existence, authenticate users, or apply records.**


## UTF-8/Unicode processing requirement (v1.2)
Read `ai-agent-sp/standards/UNICODE_UTF8.md`. Import accepts strict UTF-8 / UTF-8-BOM. Normalize appropriate text to NFC during the staging pipeline; inspect legacy encodings rather than guessing. CSV intended for Excel uses BOM; IDs must remain text. Add round-trip Unicode, XLSX Text cells, and CSV-injection tests before production.
