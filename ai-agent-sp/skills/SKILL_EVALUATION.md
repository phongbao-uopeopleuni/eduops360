# Skill Evaluation Protocol (before declaring a skill dependable)

1. Select 3 representative and 2 adversarial/edge task prompts **per skill**.
2. Run an Agent against an isolated fake-data repo using skill+same tool configuration. Repeat without skill as baseline where possible.
3. Evaluate: trigger correctness, adherence to ownership, complete evidence, no false Git claim, test behavior, token/cost/time tradeoff, security false positives/negatives.
4. Record findings in task journal and revise skill description/procedure; no unreviewed policy copy.
5. Never treat a valid SKILL.md frontmatter or successful governance static check as proof that an Agent uses it correctly.

Examples:
- `unicode-regression`: NFC/NFD and leading-zero CSV + invalid bytes.
- `regression-debugger`: intentionally stale academic year, wrong API IDOR and unknown root cause.
- `timetable-cpsat`: infeasible vs unknown/time limit, holiday collision.
- `audit-trail-verification`: forced audit-outbox failure and admin deletion attempt.
