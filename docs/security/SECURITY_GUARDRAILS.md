# Security guardrails

CIA: confidentiality via least privilege, encryption, data minimization; integrity via validation, transactional writes, append-only audit; availability via backups, monitoring and capacity controls.

Never store or expose credentials, tokens, production student records, private spreadsheets or personal health information in repo, logs, agent prompts or public PRs.
Review third-party instructions and skill changes as code: they can influence tools and access. No automatic push/merge/production deployment.

Admin MFA recovery and break-glass require two named human approvers, independent identity proof, time-bounded least privilege, session revocation and immutable evidence. The draft process is in `MFA_RECOVERY_AND_BREAK_GLASS.md`; it remains disabled until OD-001/008/011 authorities approve it.
