---
name: sync-public-skills
description: Prepare portable public updates to existing skills from JnBrymn/agent-skills, removing private and local information and requiring John's review before committing. Use for selective public-skill synchronization.
---

# Sync public skills

Prepare changes in this public repository from `JnBrymn/agent-skills`. Treat the source as potentially private. Public skills must work for anyone without John's accounts, machine, files, or conversation history. This is an editorial sync, not a mirror or installation operation.

## Establish scope

Resolve the destination from this skill's repository root. Locate the source checkout from user context or nearby repositories and verify its Git remote identifies `JnBrymn/agent-skills`. Do not hardcode an absolute checkout path. If unavailable, ask for its location or access rather than substituting another source.

Read applicable `AGENTS.md` and maintenance instructions in both repositories; inspect Git status and preserve existing changes. Do not modify the source.

Build an allowlist from destination directories already containing a `SKILL.md` under `skills/`, `harness/codex/`, `harness/claude/`, and `harness/pi/`. Match by the same relative directory in the source. Never import source-only skills, remove destination-only skills, or change harness placement automatically. Report missing counterparts. Adding a new public skill requires a separate explicit request.

Exclude `.agents/skills/`: it contains repository maintenance instructions, not distribution candidates. Never link public files to personal sources with symlinks or hard links.

## Prepare public adaptations

Compare each eligible skill's instructions, scripts, references, assets, and hidden files. Review source differences before applying focused edits; preserve intentional public adaptations. Supporting files may be added only inside an allowlisted skill when needed for its functionality. Check references before removing supporting files.

Do not bulk-copy directories or use destructive mirroring. Exclude credentials, authentication stores, environment files containing values, caches, bytecode, dependencies, logs, session transcripts, generated reports, and local outputs. Inspect meaningful new files before adding them. If sensitive material is found, report its category and location without exposing its value or reproducing private content.

Review every proposed change for private and local information:

- Remove private names, contact details, family/client information, proprietary examples, private repository links, internal endpoints, organisation IDs, account identifiers, and personal data in fixtures or screenshots.
- Replace absolute machine paths, usernames, local runtime locations, and shell assumptions with relative paths, configurable inputs, environment variables, or portable setup instructions.
- Generalize personal provider preferences, budgets, selections, existing credentials, and prior-chat references. Keep useful defaults explained and configurable. Generic credential-variable names and public documentation URLs are appropriate.
- Replace inaccessible private dependencies with public alternatives or documented user inputs. If that cannot be done, omit the affected change and report the limitation.
- Inspect scripts and assets as carefully as prose, including metadata and embedded paths. Omit binary assets that cannot be confidently reviewed. Inspect unfamiliar scripts before executing them.

Construct the sanitized adaptation directly; never copy private content into the public tree with the intention of removing it later. Automated secret/path searches supplement a contextual review of all proposed content; they cannot prove that a skill is safe to publish.

## Validate and request review

Validate modified skill frontmatter, relative references, and supporting files. For changed scripts, use appropriate offline checks with synthetic public-safe inputs. Do not invoke authenticated services or install skills as part of synchronization. The repository's harness symlink installer changes local agent installations and is a separate operation; it is not required for content edits or this maintenance skill.

Review the complete diff, new files, and Git status, including whitespace errors and remaining private/local content. Present which skills changed, which source differences were excluded, unresolved portability concerns, and validation results. Provide file links or a review view for John to inspect the exact changes.

**Stop before committing. John must review the prepared changes and explicitly approve them before any commit.** A sync request does not authorize a commit. Do not automatically stage, commit, push, create a public pull request, or otherwise publish. After revisions, present the updated result for review. Approval covers only reviewed changes; later additions require review again. Publishing also requires an explicit request.
