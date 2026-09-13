#!/usr/bin/env python3
"""Expose canonical shared and harness skills through directory symlinks."""
import argparse
import datetime
from pathlib import Path

def sync(repo, user_root):
    roots = {"codex": user_root / ".codex/skills", "claude": user_root / ".claude/skills", "pi": user_root / ".pi/agent/skills"}
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    for harness, root in roots.items():
        desired = {}
        for source in (repo / "skills", repo / "harness" / harness):
            for skill in sorted(source.iterdir()):
                if skill.is_dir() and (skill / "SKILL.md").is_file():
                    desired[skill.name] = skill.resolve()
        if not desired:
            raise RuntimeError(f"No skills found for {harness}")
        backup = root.parent / f"skills.backup-{stamp}"
        if root.is_symlink():
            raise RuntimeError(f"Expected real directory: {root}")
        root.mkdir(parents=True, exist_ok=True)
        for entry in list(root.iterdir()):
            if entry.name == ".system" and harness == "codex":
                continue
            target = desired.get(entry.name)
            if target and entry.is_symlink() and entry.resolve() == target:
                continue
            backup.mkdir(exist_ok=True)
            entry.rename(backup / entry.name)
        for name, target in desired.items():
            link = root / name
            if not link.is_symlink():
                link.symlink_to(target, target_is_directory=True)
            assert link.resolve() == target and (link / "SKILL.md").is_file()
        print(f"{harness}: {len(desired)} verified links; backup: {backup if backup.exists() else 'none needed'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--user-root", type=Path, default=Path.home())
    args = parser.parse_args()
    sync(args.repo.resolve(), args.user_root.resolve())
