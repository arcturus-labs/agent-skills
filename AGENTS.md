# Skill maintenance

For updates from `JnBrymn/agent-skills`, use
`.agents/skills/sync-public-skills/SKILL.md`. Sync only skills already present
here, generalize private/local content, and present the changes to John for
explicit approval before committing. A sync request alone is not commit approval.
Repository-local maintenance skills in `.agents/skills/` are not distributed
skills and do not require running the harness installation script.

This repository owns the public skill files in `skills/` and optional
harness-specific skills in `harness/codex/`, `harness/claude/`, and
`harness/pi/`.

Keep credentials, generated outputs, runtime caches, and machine-specific
paths out of Git. Review changes before publishing. Add new shared skills under
`skills/`; use a harness directory only when the skill genuinely depends on
that harness. Run `python3 scripts/sync-skills.py` after adding, removing, or
renaming a skill.
