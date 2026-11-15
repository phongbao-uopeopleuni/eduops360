# Critical workflows — data flow, steps and transaction boundaries

## 1. Import 2,000 student CSV rows
1. User with `students.import` for school+year downloads a versioned template.
2. Browser uploads to preflight endpoint; server stores temporary object with strict size/type limits and hash.
3. Parser reads strict UTF-8 (`utf-8-sig` supported); schema check and NFC on appropriate fields.
4. Resolve student identity by scoped stable code; resolve class and academic year by FK; do not infer identity from full name.
5. Staging table records valid/new/conflicting/invalid rows and reasons; no operational student mutation yet.
6. API responds with counts and sample errors; user chooses create-only/update-approved-fields and confirms.
7. Backend checks permission again and idempotency key, commits student/enrollment changes and audit outbox in a transaction or defined chunks with per-chunk checkpoint.
8. Worker sends audit event to isolated store; results kept until retention expiry.
9. UI shows totals, downloadable error report and batch history.
10. Regression: duplicate replay, unauthorized class, UTF-8 malformed, leading zeros, concurrent import and rollback.

## 2. Add school holiday after timetable publication
1. User selects start/end dates, entire-day/AM/PM time window, class/school scope and year.
2. Validate inclusive date range and year; overlaps existing closure are flagged, not silently merged.
3. Simulate affected timetable entries and show list of subject/teacher/room collisions.
4. Authorized reviewer approves closure; record it with revision and audit.
5. Published timetable history is preserved, current active version marked for repair.
6. Solver creates a draft local repair with only authorized movable entries; class/teacher/room availability validated.
7. Publish revised timetable only after review; notify impacted staff.
8. Test time-zone/year filtering and partial-day overlaps.

## 3. Grade edit for locked semester
1. A user sends value, record revision, year, reason.
2. Authenticate, check grade edit permission, class+subject assignment, original policy version, lock state.
3. If locked, reject routine edit; controlled reopen request requires independent approval.
4. If allowed, validate grade type/scale/missing value and run rules pure function.
5. Transaction updates row revision and audit outbox with old/new; 409 on stale revision.
6. Audit archive receives immutable record; notify reviewer.
7. Historical queries use original policy and published revision; never recalculate with future rules.
8. Test two writers, out-of-scope ID, tampering and audit failure.

## 4. CP-SAT scheduling job
1. Save immutable snapshot for selected school/year, valid slots, holidays, teacher assignments, resources.
2. Check feasibility bounds; reject inconsistent inputs with explanations and appropriate 422.
3. Enqueue bounded solver job; API immediately returns job ID.
4. Worker applies hard constraints and weighted soft objectives; records runtime, status, objective.
5. If feasible, independently validate overlapping actual time intervals and complete required lessons.
6. Save draft version with snapshot hash; no automatic publish.
7. UI shows schedule draft, warnings and constraints; user can drag/drop with instant conflict check.
8. Authorized publisher confirms; audit links old/new version and change reasons.
9. Test solver UNKNOWN vs INFEASIBLE and worker timeout/cancel/retry.

## 5. Legal source auto sync
1. Timer selects trusted source adapter with approved rate limits and last-success cursor.
2. Verify response and attachment metadata, quarantine unexpected content/size.
3. Store original bytes + SHA-256 and retrieval history; never overwrite observed version.
4. Extract textual sections for search, preserving original and linking OCR quality if applicable.
5. AI may propose category/supersession relation but marks it unreviewed.
6. Human reviewer confirms scope/effective dates; only then update applicable policy suggestion queue.
7. Alert domain owner; never silently change live timetable or scores.
8. Test duplicates, source outage, delayed effective date and malicious instruction-like content.
