# agent-skills

Public Codex, Claude Code, and Pi skills.

## Layout

- `skills/`: shared skills (`creating-and-managing-skills` and `update-ai-model-frontier`).
- `template_skills/`: project-deployed template skills (`software-factory`).
- `template_skills/worktrees/<project>/`: local, gitignored worktrees for project-specific template branches.
- `harness/codex/`: Codex-only skills.
- `harness/claude/`: Claude Code-only skills.
- `harness/pi/`: Pi-only skills.
- `scripts/sync-skills.py`: installs directory symlinks for the supported harnesses.

Run `python3 scripts/sync-skills.py` after adding, removing, or renaming a
shared or harness skill. The script exposes only `skills/` and `harness/<agent>/`;
it does not install template skills globally. Restart agents after changing links.

Deploy `template_skills/software-factory/` through a project-specific worktree
branch, then symlink the worktree copy into the destination project's
`.agents/skills/software-factory`. See the
[template lifecycle](skills/creating-and-managing-skills/references/template-skills.md)
for deployment, editing, and semantic recombination. Keep activation links and
worktrees local; do not publish machine-specific symlinks or private planning files.

Keep API keys and generated reports outside the repository.
