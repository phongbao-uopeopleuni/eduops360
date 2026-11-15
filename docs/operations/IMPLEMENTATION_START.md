# Start implementing the blueprint — ordered checklist

1. Extract to clean directory and **compare files** with existing repo; do not overwrite changes from other agents.
2. Run `python scripts/validate_blueprint.py` and previous `python scripts/check_structure.py`, `python scripts/check_text_encoding.py`, `python -m unittest discover -s tests`.
3. Review `docs/phases/PHASE-00.md` + SRS + roles; assign owner/reviewer and authority.
4. Create task with `python scripts/create_task.py EDU-0005 --title 'Implement Phase 00 governance review' --phase 00` (run only if ID free).
5. Create approved branch/worktree and implement task. Generate task board after updating metadata; no automatic Git write.
6. Once Phase 00 accepted, begin Phase 01; do not skip IAM before using real data.

Development fixtures only; do not commit secrets or personal data.
