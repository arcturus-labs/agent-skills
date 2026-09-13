# Skill maintenance

This repository owns the public skill files in `skills/` and optional
harness-specific skills in `harness/codex/`, `harness/claude/`, and
`harness/pi/`.

Keep credentials, generated outputs, runtime caches, and machine-specific
paths out of Git. Review changes before publishing. Add new shared skills under
`skills/`; use a harness directory only when the skill genuinely depends on
that harness. Run `python3 scripts/sync-skills.py` after adding, removing, or
renaming a skill.
