# Phase 11 — Observability contract v1

**Status:** `LOCAL_HTTP_SLICE_IN_REVIEW / NOT APPROVED / NO EXTERNAL OBSERVABILITY`

## Scope and authority boundary

P11-T03A implements one local HTTP request-completion event and documents the
remaining observability boundaries. It does not create a metrics backend, trace
exporter, alert channel, dashboard, queue worker, backup monitor, production
credential, endpoint or deployment.

Phase 10 is not accepted; Operations/Security/Data owners and OD-011 retention,
RPO/RTO and incident authority are still open. This contract therefore grants no
operational monitoring authority.

## Implemented local HTTP event

Every API request receives a server-generated UUID request ID. The same ID is
returned in `X-Request-ID`, carried into safe error envelopes and available to
transactional audit writers. The client cannot select the value.

Logger `eduops.http` emits exactly one JSON request-completion event with this
allowlist:

| Field | Purpose |
| --- | --- |
| `event` | Fixed `http_request_completed` event name |
| `request_id` | Server-generated correlation ID |
| `method` | HTTP method |
| `route` | Matched route template, or `unmatched`; never raw path/query |
| `status_code` | Final HTTP response status |
| `duration_ms` | In-process elapsed duration in milliseconds |

No request/response body, query string, header, cookie, authorization token,
session ID, IP address, user agent, password, secret, student data or exception
detail is sent to this logger. A logging-handler failure is swallowed so it does
not change the HTTP response; this does not replace audit fail-closed behavior.
Responses at 500+ log at error level; other completion events log at info level.

Audit logs remain a separate transactional integrity record and retain their own
credential redaction. Operational logs must never become a substitute for audit.

## Metrics, tracing, alert and worker boundary

| Capability | Current state | Gate before implementation |
| --- | --- | --- |
| Metrics exporter/dashboards | `NOT IMPLEMENTED` | Select approved collector, retention, access policy and synthetic-only validation |
| Distributed trace exporter | `NOT IMPLEMENTED` | Select approved trace backend/sampling/redaction policy; do not export request bodies or identities |
| Alert routing | `NOT IMPLEMENTED` | Name Operations owner, routing channel, escalation/on-call and false-positive handling |
| Queue/worker health | `NOT IMPLEMENTED` | A queue and independently authenticated worker must exist; API health may not claim worker health |
| Backup/disk/archive monitoring | `NOT IMPLEMENTED` | OD-011 RPO/RTO, archive/backup owner and verified targets |

Candidate signals for later human review are API 5xx rate, readiness failures,
queue age/failure, audit-delivery failure, backup age/integrity, storage capacity
and security-rate-limit denials. Thresholds, retention, recipients and escalation
are deliberately `NOT APPROVED` rather than silently configured.

## Failure and privacy review

- Correlate a user report with `X-Request-ID`; do not ask the user to disclose a
  cookie, authorization value, record contents or full URL query.
- Investigate operational logs with access controlled separately from business
  Admin; preserve audit evidence and follow the incident sequence in the threat
  model.
- If a future exporter cannot enforce redaction, access control or retention, do
  not enable it. If an alert channel/owner is absent, record the signal locally
  but do not claim actionable monitoring.
- Tests must prove a query token, authorization value and exception detail do not
  appear in the emitted event.

## Review required

Independent Security and Operations reviewers must validate event allowlist,
logger destination/access, retention, sampling, incident routing and every later
metrics/tracing/alert/worker integration. Reverting this slice removes the local
request event only; no external monitoring state exists to roll back.
