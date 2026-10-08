# agent-skills

Public Codex, Claude Code, and Pi skills.

## Layout

- `skills/`: shared skills.
- `harness/codex/`: Codex-only skills.
- `harness/claude/`: Claude Code-only skills.
- `harness/pi/`: Pi-only skills.
- `scripts/sync-skills.py`: installs directory symlinks for the supported harnesses.

This distribution currently includes `update-ai-model-frontier`,
`creating-and-managing-skills`, and `software-factory`.

Run `python3 scripts/sync-skills.py` after adding, removing, or renaming a
skill. Keep API keys and generated reports outside the repository.
