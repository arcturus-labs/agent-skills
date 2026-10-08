---
name: creating-and-managing-skills
description: >-
  Create, manage, and publish agent skills: canonical repo layout
  (shared, harness-specific, and template skills), generality default, and the
  sync script that symlinks skills into every harness. Use when creating,
  editing, renaming, or removing a skill, changing harness exposure, or
  deploying, modifying, or recombining template skills.
---

# Creating and managing skills

Keep one canonical skills repo. Never home a skill in one agent's directory — create it in the repo, expose via symlinks (see below). And never make changes to a skill unless explicitly asked to by the user.

## Layout

- `skills/` — shared skills. Default everything here.
- `harness/<agent>/` — only skills that depend on one harness's tools/APIs (today: `harness/pi/` with `brave-search`, `browser-tools`). Same-name harness skill overrides the shared one for that harness.
- `template_skills/` — skills deployed into other projects where they diverge per project and are later recombined. One worktree branch per destination project under `template_skills/worktrees/<project>/`, named after the destination repo (a project may symlink several template skills). Full lifecycle: `references/template-skills.md`.
- `scripts/sync-skills.py` — symlinks shared + harness skills into every harness below. **Run after adding, removing, or renaming skills** (edits need no sync; links share the files). Then restart agents.

## Generality default

Write for any harness unless the user says otherwise: plain markdown, relative paths, no harness-specific APIs. Prefer shared instructions + small harness note over forking.

## Shape

`skills/<name>/SKILL.md` (frontmatter `name` + `description` starting with a verb like "Use when…"), plus optional `references/`, `scripts/`, `assets/`. Keep secrets, caches, `node_modules` out of Git.

## Harnesses (sync-managed)

| Harness | Skills dir |
|---|---|
| Pi | `~/.pi/agent/skills` |
| Claude Code | `~/.claude/skills` |
| Codex CLI | `~/.codex/skills` (`.system` preserved) |

Verify links resolve to the intended source and `SKILL.md` reads through them. Report backups and `git status`; don't push unasked. Import-then-sync procedure and agent prompt: `SKILL-MAINTENANCE.md` at repo root.

## Shared and harness skills

When any shared or harness skill change is finalized, commit it on main with a message describing the change that was made.

## Template skills

Template skills diverge per project and recombine semantically — never edit them like shared skills. Follow `references/template-skills.md`: promoting a skill, deploying it to a project, committing in-project changes (Change/Context/Rationale), user-driven N-way recombination into main, and redeploy.
