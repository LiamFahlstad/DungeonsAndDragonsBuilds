"""Check what agents actually changed, independent of what they reported.

Usage (from the repo root):
    python .claude/skills/verify-agent-work/verify.py                        # changed files + static checks
    python .claude/skills/verify-agent-work/verify.py --claimed a.py b.py    # also compare against an agent's claimed file list
    python .claude/skills/verify-agent-work/verify.py --tests                # also run the test suite (quiet, stop on first failure)
    python .claude/skills/verify-agent-work/verify.py --off-limits Model/Content/Feature.py Model/Ledger
                                                                            # FAIL if the agent touched files it was told not to
    python .claude/skills/verify-agent-work/verify.py --root .claude/worktrees/agent-x   # check an isolated agent's worktree

Steps, each printed as its own section:
1. Changed files: tracked modifications plus untracked files, never .claude/worktrees. Agent
   memory (.claude/agent-memory/) is listed separately, for review rather than claim-checking.
2. Claimed vs actual (with --claimed): files claimed but untouched, and touched but not claimed.
   Off-limits (with --off-limits): changed files equal to or under any given path.
3. Compile every changed .py file.
4. pyflakes for undefined names - catches a name used in a method body but never imported,
   which compile and import both miss.
5. Import every changed module, so import-time errors show up.
6. Other agent worktrees with uncommitted changes (a stray repo-wide script may have touched them).
7. Tests (with --tests).

Exit code 1 if any check failed.
"""

import argparse
import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKTREES = ".claude/worktrees/"
AGENT_MEMORY = ".claude/agent-memory/"


def git(*args: str, cwd: Path | None = None) -> str:
    # cwd defaults at call time, so --root (which rebinds ROOT) is honoured.
    return subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True, check=True).stdout


def changed_files() -> list[str]:
    files = []
    for line in git("status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:].split(" -> ")[-1].strip('"')
        if not path.startswith(WORKTREES):
            files.append(path)
    return sorted(files)


def normalize(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve().relative_to(ROOT)
        except ValueError:
            return candidate.as_posix()
    return candidate.as_posix()


def section(title: str) -> None:
    print(f"\n== {title}")


def check_claims(claimed: list[str], changed: list[str]) -> bool:
    claimed_set = {normalize(p) for p in claimed}
    changed_set = set(changed)
    untouched = sorted(claimed_set - changed_set)
    unclaimed = sorted(changed_set - claimed_set)
    for path in untouched:
        print(f"  CLAIMED BUT UNCHANGED  {path}")
    for path in unclaimed:
        print(f"  CHANGED BUT UNCLAIMED  {path}")
    if not untouched and not unclaimed:
        print("  claims match the working tree")
    return not untouched


def check_off_limits(paths: list[str], changed: list[str]) -> bool:
    fences = [normalize(p).rstrip("/") for p in paths]
    hits = [c for c in changed if any(c == f or c.startswith(f + "/") for f in fences)]
    for path in hits:
        print(f"  FAIL  {path} was changed but is off-limits")
    if not hits:
        print(f"  none of {len(fences)} off-limits path(s) changed")
    return not hits


def check_compile(py_files: list[str]) -> bool:
    ok = True
    for path in py_files:
        try:
            compile((ROOT / path).read_text(encoding="utf-8"), path, "exec")
        except SyntaxError as error:
            ok = False
            print(f"  FAIL  {path}:{error.lineno}: {error.msg}")
    if ok:
        print(f"  {len(py_files)} file(s) compile")
    return ok


def check_undefined_names(py_files: list[str]) -> bool:
    if not py_files:
        print("  nothing to check")
        return True
    result = subprocess.run(
        [sys.executable, "-m", "pyflakes", *py_files], cwd=ROOT, capture_output=True, text=True
    )
    problems = [line for line in result.stdout.splitlines() if "undefined name" in line]
    for line in problems:
        print(f"  FAIL  {line}")
    if result.returncode != 0 and "No module named pyflakes" in result.stderr:
        print("  skipped: pip install pyflakes")
        return True
    if not problems:
        print("  no undefined names")
    return not problems


def check_imports(py_files: list[str]) -> bool:
    sys.path.insert(0, str(ROOT))
    ok = True
    modules = [
        Path(p).with_suffix("").as_posix().replace("/", ".")
        for p in py_files
        if not p.startswith(("tests/", ".claude/")) and Path(p).name != "__init__.py"
    ]
    for module in modules:
        try:
            importlib.import_module(module)
        except Exception as error:  # noqa: BLE001 - report every kind of import failure
            ok = False
            print(f"  FAIL  {module}: {type(error).__name__}: {error}")
    if ok:
        print(f"  {len(modules)} module(s) import")
    return ok


def check_worktrees() -> bool:
    dirty = False
    blocks = git("worktree", "list", "--porcelain").split("\n\n")
    for block in blocks:
        lines = block.splitlines()
        if not lines or not lines[0].startswith("worktree "):
            continue
        path = Path(lines[0][len("worktree "):])
        if path.resolve() == ROOT:
            continue
        count = len(git("status", "--porcelain", cwd=path).splitlines())
        if count:
            dirty = True
            print(f"  {path}: {count} uncommitted change(s) - make sure they belong to that agent")
    if not dirty:
        print("  no other worktree has uncommitted changes")
    return True


def run_tests() -> bool:
    result = subprocess.run(["bash", "run_tests.sh", "-q", "-x"], cwd=ROOT)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--claimed", nargs="*", default=None, help="file paths an agent reported changing")
    parser.add_argument("--tests", action="store_true", help="also run ./run_tests.sh -q -x")
    parser.add_argument("--off-limits", nargs="*", default=None, help="files/folders the agent was told not to touch")
    parser.add_argument("--root", help="repo or worktree to inspect (default: this repo)")
    args = parser.parse_args()

    global ROOT
    if args.root:
        ROOT = Path(args.root).resolve()
        print(f"Inspecting {ROOT}")

    all_changed = changed_files()
    memory = [p for p in all_changed if p.startswith(AGENT_MEMORY)]
    changed = [p for p in all_changed if not p.startswith(AGENT_MEMORY)]
    py_files = [p for p in changed if p.endswith(".py") and (ROOT / p).exists()]

    section(f"Changed files ({len(changed)})")
    for path in changed:
        print(f"  {path}")
    if memory:
        section(f"Agent memory changed ({len(memory)}) - review: git diff -- {AGENT_MEMORY}")
        for path in memory:
            print(f"  {path}")

    results = []
    if args.claimed is not None:
        section("Claimed vs actual")
        results.append(check_claims(args.claimed, changed))
    if args.off_limits:
        section("Off-limits")
        results.append(check_off_limits(args.off_limits, changed))
    section("Compile")
    results.append(check_compile(py_files))
    section("Undefined names (pyflakes)")
    results.append(check_undefined_names(py_files))
    section("Import")
    results.append(check_imports(py_files))
    section("Other worktrees")
    results.append(check_worktrees())
    if args.tests:
        section("Tests")
        results.append(run_tests())

    section("Result: " + ("PASS" if all(results) else "FAIL"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
