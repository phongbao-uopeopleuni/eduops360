# AI AGENT SP — One canonical agent knowledge base

**Do not create parallel policy sets for Claude vs Codex.** `AGENTS.md` and `CLAUDE.md` are short entrypoint adapters only.

Recommended entry flow: read root entrypoint → PROJECT_CONTEXT → OPERATING_RULES → relevant SRS/phase → one role card → chosen skill(s) from `skills/REGISTRY.md` → active task journal. Avoid reading every document for small changes.

Contents:
- `skills/` 7 named groups, original implementation-oriented SOPs.
- `roles/` is at `docs/roles/`, where reviewers and human approvers are defined.
- `standards/` shared UTF-8 and future cross-module rules.
- `workflows/` task, branch, review and Git operational conventions.

**Important discovery limitation:** arbitrary `ai-agent-sp/` directory is not automatically a recognized native skill location for every tool. Configure each Agent's project entrypoint to read this registry or make a generated tool-specific adapter with validation (no divergent body content).
