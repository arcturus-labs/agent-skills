# agent-skills

Public Codex, Claude Code, and Pi skills.

## Layout

- `skills/`: shared skills (`creating-and-managing-skills`, `update-ai-model-frontier`, and `video-editing`).
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

## Video editing

[`skills/video-editing/SKILL.md`](skills/video-editing/SKILL.md) provides a
transcript-led, collaborative editing workflow: source discovery, quote auditioning,
isolated video stitches, synchronized camera layouts, branding, numbered drafts,
and verification. Optional Python helpers cover cached AssemblyAI transcription,
transcript lookup, FFmpeg previews, and macOS QuickTime cueing. Creative builds can
use custom project scripts; no transcription model is pinned. See the skill's
references for setup, permissions, and platform-specific requirements.

Keep API keys and generated reports outside the repository.
