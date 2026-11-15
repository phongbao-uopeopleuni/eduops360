# Domain Data Model — canonical logical entities

| Entity / aggregate | Required keys / major fields | Consistency and policy |
|---|---|---|
| schools | id, name, timezone, active_year_id nullable | restrict tenant scope |
| academic_years | id, school_id, name, start/end DATE, status, revision | unique school+name; check dates; active uniqueness |
| academic_terms | id, academic_year_id, start/end DATE | term subset of year |
| students | id, school_id, student_code(TEXT), full_name, birth_date | unique school+code; NFC name; no grade columns |
| enrollments | id, student_id, academic_year_id, class_id, state | unique applicable enrollment; history immutable on year close |
| classes / subjects / teachers | ID, owner school/year, catalog and assignment | FK and distinct times |
| teaching_assignments | teacher, class, subject, year, weekly load | authority and scope |
| time_slots | id, template_id, day-of-week, session, start/end TIME | start < end, no invalid overlap |
| calendar_exceptions | id, scope, from/to DATE, optional start/end TIME | inclusive date range, approved status |
| timetable_versions | id, school/year, state, revision, published_at | approved/published immutable version |
| timetable_entries | id, version_id, class/group/teacher/room/date/start/end | intersection checks, resource FK |
| assessment_policies | policy_id, legal_doc_id, effective interval, version | rules only after domain approval |
| assessment_results | student_id, year_id, subject, event, value, status, revision | policy snapshot, audit before/after |
| legal_documents | id, source_url, doc_code, issuer, effective periods | provenance, legal relation reviewed |
| document_versions | doc_id, SHA-256, source timestamp, collected_at | original bytes retained |
| import_batches | id, actor, template_version, checksum, counters, status | idempotency and rollback |
| model_versions / predictions | features_as_of, training_data_ref, metrics, model hash | no automatic official classification |
| audit_outbox | event id, actor, action, resource, correlation_id, timestamp | transactional write |

Constraints need DB migration proof; this document is logical design, not a tested physical schema.
