# Data flow and control diagrams (Mermaid)

## Application and trust boundaries
```mermaid
flowchart TD
  Browser[Browser / PWA] -->|HTTPS + session| API[FastAPI Modular Monolith]
  API --> AUTH[AuthZ scope / year policy]
  API --> DOMAIN[Domain service]
  DOMAIN --> DB[(PostgreSQL)]
  DOMAIN --> OUTBOX[(Audit Outbox)]
  API --> QUEUE[Task Queue]
  QUEUE --> WORKERS[CP-SAT / Legal / ML Workers]
  WORKERS --> DB
  OUTBOX --> AUDIT[Immutable Audit Archive]
  API --> FILES[(Private Document Storage)]
```

## Task lifecycle
```mermaid
flowchart LR
  P[Planned] --> IP[In progress]
  IP --> IR[In review]
  IR --> D[Done]
  IP --> B[Blocked]
  IR --> B
  B --> IP
  D --> A[Phase accepted by authority]
```

Diagrams reflect intended architecture, not deployed services. Regenerate/review when an ADR changes the boundaries.
