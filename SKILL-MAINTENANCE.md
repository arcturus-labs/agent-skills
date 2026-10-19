# Skill maintenance

Edit canonical skill files in `skills/` or the appropriate harness directory.
Keep supporting scripts, references, and assets with the skill that uses them.
Template skills live in `template_skills/`, not `skills/`; deploy and edit them
through project-specific worktree branches as described in
`skills/creating-and-managing-skills/references/template-skills.md`.
Do not copy private planning artifacts or local worktrees into this distribution.

Before publishing, inspect the diff for credentials, personal information,
generated outputs, caches, and machine-specific paths. Run the sync script to
verify shared and harness skill links, then review Git status and the final file
list. Use `--user-root <temporary-directory>` for isolated verification without
changing your active agent installations. Template skills are intentionally not
exposed by the global sync script; verify their project deployment separately.

Do not commit API keys or reports containing private data.
