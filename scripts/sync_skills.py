#!/usr/bin/env python3
"""Sync repo skills to a Hermes skills directory; detect drift with --check.

Layout mirrored:
  <repo>/SKILL.md            -> <target>/software-engineering-team/SKILL.md
  <repo>/<tracked files>     -> <target>/software-engineering-team/<path>
  <repo>/skills/se-team-*/SKILL.md -> <target>/se-team-*/SKILL.md

Known-divergent skills (see docs/UPDATE_BACKLOG.md U-23): se-team-rules is on an
ignore-list — the installed copy intentionally differs (Floratech rules, out of
scope), so it is neither copied nor checked.

Modes:
  default   copy repo files -> target (one-way; extra target files are kept)
  --check   compare repo files vs target; exit 0 if identical, 1 + diff summary
            when any non-ignored file drifted
  --target  explicit target directory (the Hermes skills dir is user-machine-
            specific; never hardcoded in CI)
"""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

IGNORED_SKILLS = {"se-team-rules"}
MASTER_NAME = "software-engineering-team"


def _tracked_files(repo):
    result = subprocess.run(["git", "-C", str(repo), "ls-files"], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise ValueError(f"not a git repository: {repo}")
    return [path for path in result.stdout.splitlines() if path]


def _digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _mirror_paths(repo, tracked):
    """Map every tracked repo file to its target path under <target>/ (posix form)."""
    for path in tracked:
        if path == "SKILL.md":
            yield path, "software-engineering-team/SKILL.md"
        elif path.startswith("skills/se-team-") and path.endswith("/SKILL.md"):
            skill = path.split("/")[1]
            if skill in IGNORED_SKILLS:
                continue
            yield path, f"{skill}/SKILL.md"
        elif not path.startswith("skills/"):
            yield path, f"software-engineering-team/{path}"
        # skills/se-team-*/SKILL.md handled above; other skills/ files are not mirrored.


def copy_all(repo, target):
    target = Path(target)
    copied = []
    for source_rel, target_rel in _mirror_paths(repo, _tracked_files(repo)):
        destination = target / target_rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((Path(repo) / source_rel).read_bytes())
        copied.append(target_rel)
    return copied


def check(repo, target):
    target = Path(target)
    drifted = []
    missing = []
    for source_rel, target_rel in _mirror_paths(repo, _tracked_files(repo)):
        destination = target / target_rel
        if not destination.is_file():
            missing.append(str(target_rel))
            continue
        if _digest(destination) != _digest(Path(repo) / source_rel):
            drifted.append(str(target_rel))
    return missing, drifted


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sync repo skills to a Hermes skills directory.")
    parser.add_argument("--repo", type=Path, default=None, help="repo root (default: parent of this script)")
    parser.add_argument("--target", type=Path, default=None, help="Hermes skills dir (default: platform standard)")
    parser.add_argument("--check", action="store_true", help="compare only; exit 1 on drift, never write")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve() if args.repo is not None else Path(__file__).resolve().parents[1]
    target = Path(args.target).resolve() if args.target is not None else _default_target()

    try:
        if args.check:
            missing, drifted = check(repo, target)
            if missing:
                for path in missing:
                    print("MISSING", path)
            if drifted:
                for path in drifted:
                    print("DRIFTED", path)
            if missing or drifted:
                print(f"sync --check FAILED: {len(missing)} missing, {len(drifted)} drifted")
                return 1
            print("sync --check OK: repo and target are identical (ignoring", ", ".join(sorted(IGNORED_SKILLS)) + ")")
            return 0
        copied = copy_all(repo, target)
        print(f"synced {len(copied)} files to {target}")
        return 0
    except (OSError, ValueError) as error:
        print("BLOCKED:", error)
        return 1


def _default_target():
    if sys.platform == "win32":
        return Path.home() / "AppData/Local/hermes/skills"
    return Path.home() / ".config/hermes/skills"


if __name__ == "__main__":
    sys.exit(main())
