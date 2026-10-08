# Template skills

Template skills (`template_skills/<name>/`) are deployed into other projects, diverge there, and are later recombined into main semantically. One worktree branch per destination project lives under `template_skills/worktrees/<project>/`, named after the destination repo — not the skill — because a project may symlink several template skills (and only the ones it needs). `template_skills/worktrees/` is gitignored via the `worktrees/` pattern; the branches themselves may be pushed.

Never edit the main copy to reflect one project's needs, and never `git merge` a project branch into main — recombination is semantic (see below).

## Promoting a skill to a template skill

A template skill usually starts life as a normal skill inside a project directory. When the user decides it should become a template skill:

1. Copy the entire skill directory into `template_skills/<name>/` on main and commit.
2. Create (or reuse) the worktree branch named for that project: `git worktree add template_skills/worktrees/<project> -b <project>` from main.
3. In the destination repo, replace the original skill directory with a symlink to the worktree copy, e.g. `<dest>/.agents/skills/software-factory` → `<repo>/template_skills/worktrees/<project>/template_skills/software-factory`.

## Deploying into a project

In `template_skills/worktrees/`, create (or reuse) the branch named for the destination repo, then symlink whichever template skills that project needs into its skills directory. Linking one skill is all deployment takes — a project branch may carry several skills, but only link what's needed.

Example: `template_skills/worktrees/my-project/template_skills/software-factory` is symlinked to `<dest>/.agents/skills/software-factory`.

## Modifying in the destination repo

The agent working in the destination repo edits the skill in place through the symlink when project work reveals an improvement — never chase the link, never touch main. The change serves that repo's context, but keep the wording generic: no project-specific details, since the skill redeploys to other projects. Preserve the skill's structure and organization; reorganization should be rare and discussed with the user first. Exercise the change if possible so the rationale isn't lost.

Commit every change against the worktree branch with a Change/Context/Rationale message — concise but sufficient to understand the change, and free to reference project-specific files or commits to make the case:

```bash
target="$(realpath .agents/skills/foobarbaz)" && repo="$(git -C "$target" rev-parse --show-toplevel)" && path="${target#"$repo"/}" && git -C "$repo" add -- "$path" && git -C "$repo" commit -m "Update foobarbaz skill" -m $'Change: describe what changed.\n\nContext: explain what prompted the change.\n\nRationale: explain why it was made.'
```

This oneliner resolves the symlink, stages the skill inside its worktree repo, and commits there — run it from the destination project directory.

## Recombining into main

At some point the diverged copies (e.g. `template_skills/worktrees/project-a/template_skills/software-factory` and `template_skills/worktrees/project-b/template_skills/software-factory`) are reintegrated into `template_skills/software-factory` on main. This is a semantic N-way merge, not a git merge, and it is driven by the user throughout: the agent researches and presents, the user decides what lands.

The user starts it by saying it's time to recombine or reincorporate the learnings, however they phrase it. The ask may be wide open, or scoped to one skill, one project, or one aspect within a skill. Read the scope from what he said and research exactly what matches — all worktrees, or only the ones in scope.

### Research first

Before proposing any edit, read the relevant worktree copies and their branch history. Commit messages carry the Change/Context/Rationale that explains each change, so read them: the user will ask about provenance and rationale, and you should be able to answer without going back to dig.

Then present what you found, pre-grouped. Unless the user asks for something else, use this hierarchy:

1. **By skill** — every in-scope change to that skill.
2. **By semantic concept** — one entry per idea. Several projects may have made the same change in different words; a change may also be a singleton.
3. **Details of that change** — fold in the variations, and call out differences and especially contradictions between projects. Keep the explanations concise.

This presentation is the starting point for a conversation, not a plan to execute. The user walks through the groups and tells you what to take, drop, reword, or combine. Some changes overlap, some are inconsistent, some are bad ideas — that judgment is the user's to make, though you should say so when you see a problem.

### Writing the changes into main

Apply only what the user has agreed to, and rewrite rather than append. Reshape whatever text the change touches so it reads as a single coherent description of how things now work. No continuity commentary — don't note what the text used to say or that something changed, unless the history itself is genuinely useful to a reader. Someone reading the skill for the first time should never have to reconstruct its past.

Goals while editing: reduce duplication, preserve the skill's overall structure, keep it organized, and keep it generic so it can redeploy.

Once agent and user are satisfied, commit the result to main with a to-the-point but sufficient message — sections per change, each headed by the change with context and rationale in the body.

### Redeploying

After the main commit, ask the user whether to push the result back out now — they may want to exclude a project. For each included project, merge main into its worktree branch (`git -C template_skills/worktrees/<project> merge main`); the symlinks pick up the update automatically.
