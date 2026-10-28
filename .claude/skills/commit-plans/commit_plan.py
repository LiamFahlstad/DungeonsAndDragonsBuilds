"""Write, list and apply commit plans, so committing is safe while many agents share one tree.

A commit plan is a commit written down instead of made: its message, and for every file the
exact content to commit (a git blob), the content it replaces (the HEAD blob) and what the
working-tree file looked like when the plan was written. A later run applies it: it checks that
nothing moved under the plan, builds the commit in a private index (so files other agents stage
meanwhile can't ride along) and moves HEAD with a compare-and-swap. It never pushes; `push-check`
says whether a push is safe and prints the command to run.

Plans live in the main checkout's .claude/commit-plans/ (git-ignored), one folder per plan under
pending/, applying/, done/, blocked/ or dropped/. COMMIT_PLANS_DIR overrides the location.

    python .claude/skills/commit-plans/commit_plan.py new --message-file MSG --by git-commit \\
        --push main --path Model/View.py --path tests/test_view.py \\
        [--content tests/snapshots/sheet_hashes.json=<scratch file with the exact bytes>] \\
        [--left "Combat/app.py: another agent's work in progress"] [--note "..."]
    python .claude/skills/commit-plans/commit_plan.py list [--state pending|all|...]
    python .claude/skills/commit-plans/commit_plan.py show CP-... [--diff]
    python .claude/skills/commit-plans/commit_plan.py check CP-...|--all
    python .claude/skills/commit-plans/commit_plan.py apply CP-...|--all
    python .claude/skills/commit-plans/commit_plan.py push-check --target main <hash>...
    python .claude/skills/commit-plans/commit_plan.py requeue CP-...        # blocked/applying -> pending
    python .claude/skills/commit-plans/commit_plan.py drop CP-... --reason "..."
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PLANS_RELATIVE = Path(".claude") / "commit-plans"
STATES = ("pending", "applying", "done", "blocked", "dropped")
PUSH_TARGETS = ("main", "branch", "ask")
EMPTY_TREE_FILE_MODE = "100644"
TITLE_LIMIT = 72
LOCK_TIMEOUT_S = 30
STALE_LOCK_S = 60
CAS_RETRIES = 3


class PlanError(Exception):
    pass


# ------------------------------------------------------------------ git helpers


def git(*args, env=None, input_bytes=None, check=True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=toplevel(),
        env=env,
        input=input_bytes,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise PlanError(
            f"git {' '.join(args)} failed: {result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout.decode("utf-8", "replace").strip()


def git_bytes(*args) -> bytes:
    result = subprocess.run(["git", *args], cwd=toplevel(), capture_output=True)
    if result.returncode != 0:
        raise PlanError(f"git {' '.join(args)} failed")
    return result.stdout


def git_ok(*args) -> bool:
    return (
        subprocess.run(["git", *args], cwd=toplevel(), capture_output=True).returncode
        == 0
    )


_TOPLEVEL = None


def toplevel() -> Path:
    global _TOPLEVEL
    if _TOPLEVEL is None:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
        )
        if out.returncode != 0:
            sys.exit("error: not inside a git repository")
        _TOPLEVEL = Path(out.stdout.strip()).resolve()
    return _TOPLEVEL


def plans_root() -> Path:
    """The plans folder in the main checkout, even when run from a worktree."""
    if os.environ.get("COMMIT_PLANS_DIR"):
        return Path(os.environ["COMMIT_PLANS_DIR"])
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    return Path(common).parent / PLANS_RELATIVE


def head_commit() -> str:
    return git("rev-parse", "HEAD")


def current_branch() -> str:
    return git("branch", "--show-current") or "(detached)"


def head_blob(path: str, commit: str = "HEAD") -> str | None:
    out = git("ls-tree", commit, "--", path)
    return out.split()[2] if out else None


def head_mode(path: str) -> str | None:
    out = git("ls-tree", "HEAD", "--", path)
    return out.split()[0] if out else None


def index_blob(path: str) -> str | None:
    out = git("ls-files", "-s", "--", path)
    return out.split()[1] if out else None


def worktree_blob(path: str, write: bool = False) -> str | None:
    """The blob `git add` would make of the working file (filters applied), or None if absent."""
    if not (toplevel() / path).is_file():
        return None
    return git("hash-object", *(["-w"] if write else []), "--", path)


def empty_blob() -> str:
    return git("hash-object", "-w", "--stdin", input_bytes=b"")


def short(sha: str | None) -> str:
    return sha[:8] if sha else "(none)"


def normalize(path: str) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            p = p.resolve().relative_to(toplevel())
        except ValueError:
            raise PlanError(f"{path} is outside the repository {toplevel()}")
    rel = p.as_posix()
    if rel.startswith("./"):
        rel = rel[2:]
    if rel.startswith(".claude/worktrees/") or rel.startswith(".git/"):
        raise PlanError(f"{rel}: never commit files under .claude/worktrees/ or .git/")
    return rel


# --------------------------------------------------------------------- storage


class Lock:
    """An exclusive lock file; a lock older than STALE_LOCK_S is from a crashed writer."""

    def __init__(self, root: Path):
        self.path = root / ".lock"

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.time() + LOCK_TIMEOUT_S
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > STALE_LOCK_S:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.time() > deadline:
                    raise PlanError(f"timed out waiting for {self.path}")
                time.sleep(0.2)

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def find_plan(plan_id: str) -> tuple[str, Path]:
    root = plans_root()
    for state in STATES:
        folder = root / state / plan_id
        if folder.is_dir():
            return state, folder
    raise PlanError(f"no plan {plan_id} (see `list --state all`)")


def load(folder: Path) -> dict:
    return json.loads((folder / "plan.json").read_text(encoding="utf-8"))


def save(folder: Path, plan: dict) -> None:
    tmp = folder / "plan.json.tmp"
    tmp.write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, folder / "plan.json")


def move(folder: Path, state: str) -> Path:
    target = plans_root() / state / folder.name
    target.parent.mkdir(parents=True, exist_ok=True)
    os.rename(folder, target)  # atomic; fails if someone else moved it first
    return target


def plans_in(state: str) -> list[Path]:
    folder = plans_root() / state
    return sorted(p for p in folder.iterdir() if p.is_dir()) if folder.is_dir() else []


def title_of(folder: Path) -> str:
    return (folder / "message.txt").read_text(encoding="utf-8").splitlines()[0]


def now() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


# ------------------------------------------------------------------- commands


def read_message(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8").replace("\r\n", "\n").strip("\n")
    lines = text.split("\n")
    if not lines or not lines[0].strip():
        raise PlanError("the message's first line (the title) is empty")
    if len(lines[0]) > TITLE_LIMIT + 8:
        raise PlanError(
            f"title is {len(lines[0])} characters; keep it near {TITLE_LIMIT}"
        )
    if len(lines) > 1 and lines[1].strip():
        raise PlanError("the message needs a blank line after the title")
    return text + "\n"


def check_python(path: str, blob: str) -> None:
    if not path.endswith(".py"):
        return
    try:
        compile(git_bytes("cat-file", "blob", blob), path, "exec")
    except SyntaxError as e:
        raise PlanError(f"{path} doesn't compile: {e}")


def cmd_new(args) -> int:
    message = read_message(args.message_file)
    if not args.path and not args.content:
        raise PlanError("name at least one --path or --content")
    files = []
    seen = set()
    for raw in args.path or []:
        path = normalize(raw)
        base = head_blob(path)
        target = worktree_blob(path, write=True)
        if target is None and base is None:
            raise PlanError(f"{path} exists neither in HEAD nor in the working tree")
        files.append(
            {
                "path": path,
                "kind": "whole file" if target else "delete",
                "mode": head_mode(path) or EMPTY_TREE_FILE_MODE,
                "base": base,
                "target": target,
                "worktree": target,
            }
        )
    for spec in args.content or []:
        if "=" not in spec:
            raise PlanError(f"--content wants PATH=FILE, got {spec}")
        raw, source = spec.split("=", 1)
        path = normalize(raw)
        target = git(
            "hash-object", "-w", "--no-filters", "--", str(Path(source).resolve())
        )
        files.append(
            {
                "path": path,
                "kind": "partial",
                "mode": head_mode(path) or EMPTY_TREE_FILE_MODE,
                "base": head_blob(path),
                "target": target,
                "worktree": worktree_blob(path),
            }
        )
    for f in files:
        if f["path"] in seen:
            raise PlanError(f"{f['path']} is named twice")
        seen.add(f["path"])
        if f["target"] == f["base"]:
            raise PlanError(f"{f['path']} has no change against HEAD")
        if f["target"]:
            check_python(f["path"], f["target"])

    root = plans_root()
    with Lock(root):
        for state in ("pending", "applying"):
            for other in plans_in(state):
                taken = {f["path"] for f in load(other)["files"]} & seen
                if taken:
                    raise PlanError(
                        f"{', '.join(sorted(taken))} already in {state} plan {other.name} "
                        f"({title_of(other)}). Apply or drop that plan first, or ask the "
                        "caller whether to fold this change into it."
                    )
        slug = re.sub(r"[^a-z0-9]+", "-", message.split("\n")[0].lower()).strip("-")[
            :40
        ]
        plan_id = f"CP-{datetime.datetime.now():%Y%m%d-%H%M%S}-{slug}"
        tmp = root / f".new-{os.getpid()}"
        tmp.mkdir(parents=True)
        (tmp / "message.txt").write_text(message, encoding="utf-8", newline="\n")
        plan = {
            "id": plan_id,
            "created": now(),
            "by": args.by,
            "push": args.push,
            "branch": current_branch(),
            "toplevel": str(toplevel()),
            "head_at_plan": head_commit(),
            "files": files,
            "left_uncommitted": args.left or [],
            "note": args.note or "",
            "history": [f"{now()} {args.by}: planned"],
        }
        save(tmp, plan)
        (root / "pending").mkdir(parents=True, exist_ok=True)
        os.rename(tmp, root / "pending" / plan_id)
    print(plan_id)
    print(f"  {message.splitlines()[0]}")
    for f in files:
        print(f"  {f['kind']:10} {f['path']}")
    print(
        f"  push: {args.push}   branch: {plan['branch']}   HEAD: {short(plan['head_at_plan'])}"
    )
    return 0


def cmd_list(args) -> int:
    states = STATES if args.state == "all" else (args.state,)
    any_shown = False
    for state in states:
        for folder in plans_in(state):
            plan = load(folder)
            extra = f"  -> {plan['commit'][:8]}" if plan.get("commit") else ""
            if state == "blocked" and plan.get("blocked_reason"):
                extra += f"  [{plan['blocked_reason'][0]}]"
            print(
                f"{plan['id']}  {state:8}  push={plan['push']:6} "
                f"{len(plan['files'])} file(s)  {title_of(folder)}{extra}"
            )
            any_shown = True
    if not any_shown:
        print(f"no {args.state} plans" if args.state != "all" else "no plans")
    return 0


def numstat(base: str | None, target: str | None) -> str:
    a, b = base or empty_blob(), target or empty_blob()
    out = git("diff", "--numstat", a, b)
    if not out:
        return "no textual change"
    added, removed = out.split()[:2]
    return "binary" if added == "-" else f"+{added} -{removed}"


def cmd_show(args) -> int:
    state, folder = find_plan(args.id)
    plan = load(folder)
    print(f"{plan['id']}  ({state})  by {plan['by']}  push={plan['push']}")
    print(f"branch {plan['branch']}, planned at HEAD {short(plan['head_at_plan'])}")
    if plan.get("commit"):
        print(f"commit {plan['commit']}")
    print()
    print((folder / "message.txt").read_text(encoding="utf-8").rstrip())
    print()
    for f in plan["files"]:
        print(f"  {f['kind']:10} {f['path']}  {numstat(f['base'], f['target'])}")
    for left in plan["left_uncommitted"]:
        print(f"  left uncommitted: {left}")
    if plan["note"]:
        print(f"  note: {plan['note']}")
    for reason in plan.get("blocked_reason", []):
        print(f"  BLOCKED: {reason}")
    for line in plan["history"]:
        print(f"  - {line}")
    if args.diff:
        for f in plan["files"]:
            print(f"\n=== {f['path']}")
            a, b = f["base"] or empty_blob(), f["target"] or empty_blob()
            print(git("diff", a, b))
    return 0


def evaluate(plan: dict) -> tuple[list[str], bool]:
    """(problems, already_committed) for applying `plan` to the current HEAD."""
    problems = []
    if Path(plan["toplevel"]).resolve() != toplevel():
        problems.append(f"planned in {plan['toplevel']}, but this is {toplevel()}")
    if plan["branch"] != current_branch():
        problems.append(
            f"planned on branch {plan['branch']}, but HEAD is on {current_branch()}"
        )
    in_head = 0
    for f in plan["files"]:
        path, now_head = f["path"], head_blob(f["path"])
        if now_head == f["target"]:
            in_head += 1
            continue
        if now_head != f["base"]:
            problems.append(
                f"{path} changed in HEAD since planning ({short(f['base'])} -> "
                f"{short(now_head)}); re-plan it"
            )
        if worktree_blob(path) != f["worktree"]:
            problems.append(
                f"{path} changed in the working tree since planning; re-plan it"
            )
        staged = index_blob(path)
        if staged not in (now_head, f["target"]):
            problems.append(f"{path} has other staged changes in the index")
    if 0 < in_head < len(plan["files"]):
        problems.append(
            "part of this plan is already in HEAD and part isn't; re-plan it"
        )
    return problems, in_head == len(plan["files"])


def cmd_check(args) -> int:
    folders = plans_in("pending") if args.all else [find_plan(args.id)[1]]
    worst = 0
    for folder in folders:
        problems, done = evaluate(load(folder))
        if done:
            print(f"{folder.name}: already in HEAD")
        elif problems:
            worst = 1
            print(f"{folder.name}: BLOCKED")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"{folder.name}: ready")
    if not folders:
        print("no pending plans")
    return worst


def build_commit(folder: Path, plan: dict) -> str:
    """Commit the plan's blobs on top of the current HEAD; returns the new commit hash."""
    index_file = folder / "index"
    env = {**os.environ, "GIT_INDEX_FILE": str(index_file)}
    for _ in range(CAS_RETRIES):
        problems, _ = evaluate(plan)
        if problems:
            raise PlanError("; ".join(problems))
        old = head_commit()
        if index_file.exists():
            index_file.unlink()
        git("read-tree", old, env=env)
        for f in plan["files"]:
            if f["target"] is None:
                git("update-index", "--force-remove", "--", f["path"], env=env)
            else:
                git(
                    "update-index",
                    "--add",
                    "--cacheinfo",
                    f"{f['mode']},{f['target']},{f['path']}",
                    env=env,
                )
        tree = git("write-tree", env=env)
        new = git("commit-tree", tree, "-p", old, "-F", str(folder / "message.txt"))
        title = title_of(folder)
        if git_ok(
            "update-ref", "-m", f"commit (plan {plan['id']}): {title}", "HEAD", new, old
        ):
            index_file.unlink()
            return new
        time.sleep(0.5)  # HEAD moved between the check and the swap; look again
    raise PlanError(f"HEAD kept moving; gave up after {CAS_RETRIES} tries")


def sync_real_index(plan: dict, base_commit: str) -> list[str]:
    """Point the shared index at the committed blobs, so `git status` shows them as clean
    instead of as a staged revert. Leaves alone any entry someone else changed meanwhile.
    """
    skipped = []
    for f in plan["files"]:
        staged = index_blob(f["path"])
        if staged == f["target"]:
            continue
        if staged != head_blob(f["path"], base_commit):
            skipped.append(f["path"])
            continue
        for _ in range(10):
            if f["target"] is None:
                ok = git_ok("update-index", "--force-remove", "--", f["path"])
            else:
                ok = git_ok(
                    "update-index",
                    "--add",
                    "--cacheinfo",
                    f"{f['mode']},{f['target']},{f['path']}",
                )
            if ok:
                break
            time.sleep(0.3)  # index.lock held by another git process
        else:
            skipped.append(f["path"])
    return skipped


def apply_one(folder: Path, by: str) -> tuple[str, str]:
    """('done'|'already'|'blocked'|'skipped', commit hash or reason)."""
    try:
        folder = move(folder, "applying")
    except OSError:
        return "skipped", "another run claimed it first"
    plan = load(folder)
    problems, already = evaluate(plan)
    if already:
        plan["commit"] = head_commit()
        plan["history"].append(f"{now()} {by}: already in HEAD")
        save(folder, plan)
        move(folder, "done")
        return "already", plan["commit"]
    try:
        if problems:
            raise PlanError("; ".join(problems))
        new = build_commit(folder, plan)
    except PlanError as e:
        plan["blocked_reason"] = str(e).split("; ")
        plan["history"].append(f"{now()} {by}: blocked: {e}")
        save(folder, plan)
        move(folder, "blocked")
        return "blocked", str(e)
    skipped = sync_real_index(plan, git("rev-parse", f"{new}^"))
    plan["commit"] = new
    plan["history"].append(f"{now()} {by}: committed {new[:8]} on {current_branch()}")
    if skipped:
        plan["history"].append(
            f"{now()} {by}: index left alone for {', '.join(skipped)}"
        )
    save(folder, plan)
    move(folder, "done")
    return "done", new


def report_commit(sha: str) -> None:
    print(f"{sha[:8]} on {current_branch()}")
    print(git("log", "-1", "--format=%B", sha).rstrip())
    print()
    print("Files:", git("show", "--stat", "--format=", sha).splitlines()[-1].strip())


def cmd_apply(args) -> int:
    folders = plans_in("pending") if args.all else [find_plan(args.id)[1]]
    if not args.all and folders[0].parent.name != "pending":
        raise PlanError(
            f"{args.id} is {folders[0].parent.name}, not pending (see `requeue`)"
        )
    if not folders:
        print("no pending plans")
        return 0
    committed, failed = [], 0
    for folder in folders:
        outcome, detail = apply_one(folder, args.by)
        print(f"== {folder.name}: {outcome}")
        if outcome == "done":
            committed.append(detail)
            report_commit(detail)
        elif outcome == "already":
            print(f"already in HEAD ({detail[:8]})")
        else:
            failed += 1
            print(f"  {detail}")
        print()
    if committed:
        print("Committed, oldest first:", " ".join(c[:8] for c in committed))
        print(
            "To push: commit_plan.py push-check --target <main|branch> "
            + " ".join(c[:8] for c in committed)
        )
    return 1 if failed else 0


def cmd_push_check(args) -> int:
    hashes = [git("rev-parse", h) for h in args.hashes]
    last = hashes[-1]
    branch = current_branch()
    target = "main" if args.target == "main" else branch
    git("fetch", "origin")
    remote = f"origin/{target}"
    if not git_ok("rev-parse", "--verify", "-q", remote):
        if args.target == "main":
            raise PlanError("origin/main doesn't exist")
        print(
            f"{remote} doesn't exist yet. Push with: git push -u origin {last}:refs/heads/{target}"
        )
        return 0
    if not git_ok("merge-base", "--is-ancestor", remote, last):
        behind = git("log", "--oneline", f"{last}..{remote}")
        print(f"NOT a fast-forward: {remote} has commits {last[:8]} lacks:\n{behind}")
        return 1
    ahead = git("rev-list", "--reverse", f"{remote}..{last}").split()
    extra = [c for c in ahead if c not in hashes]
    if extra:
        print(
            f"Pushing {last[:8]} to {target} would also publish commits that aren't yours:"
        )
        for c in extra:
            print("  " + git("log", "-1", "--format=%h %an %s", c))
        print("Don't push; report them so the user can decide.")
        return 1
    if not ahead:
        print(f"Nothing to push: {last[:8]} is already on {remote}.")
        return 0
    print(f"Safe: fast-forward, publishes only {', '.join(c[:8] for c in ahead)}.")
    print(f"Push with: git push origin {last}:{target}")
    print(
        f"Then confirm: git fetch origin && git merge-base --is-ancestor {last} {remote}"
    )
    return 0


def cmd_requeue(args) -> int:
    with Lock(plans_root()):
        state, folder = find_plan(args.id)
        if state not in ("blocked", "applying"):
            raise PlanError(
                f"{args.id} is {state}; only blocked or applying plans requeue"
            )
        plan = load(folder)
        plan.pop("blocked_reason", None)
        plan["history"].append(f"{now()} {args.by}: requeued from {state}")
        save(folder, plan)
        move(folder, "pending")
    problems, _ = evaluate(plan)
    print(
        f"{args.id}: pending"
        + ("" if not problems else " (but: " + "; ".join(problems) + ")")
    )
    return 0


def cmd_drop(args) -> int:
    with Lock(plans_root()):
        state, folder = find_plan(args.id)
        if state in ("done", "dropped"):
            raise PlanError(f"{args.id} is already {state}")
        plan = load(folder)
        plan["history"].append(f"{now()} {args.by}: dropped: {args.reason}")
        save(folder, plan)
        move(folder, "dropped")
    print(f"{args.id}: dropped")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n\n")[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("new", help="write a commit plan (stages and commits nothing)")
    p.add_argument(
        "--message-file",
        required=True,
        help="full message: title, blank, body, trailers",
    )
    p.add_argument("--by", required=True, help="who wrote the plan (agent name)")
    p.add_argument(
        "--push",
        choices=PUSH_TARGETS,
        default="ask",
        help="push target the caller named",
    )
    p.add_argument(
        "--path",
        action="append",
        help="commit this file's working-tree content (or its deletion)",
    )
    p.add_argument(
        "--content",
        action="append",
        help="PATH=FILE: commit FILE's exact bytes as PATH (partial change)",
    )
    p.add_argument(
        "--left", action="append", help="'path: reason' for related work left out"
    )
    p.add_argument("--note", help="anything the applier should know")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("list", help="list plans")
    p.add_argument("--state", choices=(*STATES, "all"), default="pending")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="show one plan")
    p.add_argument("id")
    p.add_argument("--diff", action="store_true", help="print each file's full diff")
    p.set_defaults(func=cmd_show)

    for name, func, help_text in (
        ("check", cmd_check, "dry run: would the plan apply cleanly now?"),
        ("apply", cmd_apply, "commit pending plans, oldest first (never pushes)"),
    ):
        p = sub.add_parser(name, help=help_text)
        group = p.add_mutually_exclusive_group(required=True)
        group.add_argument("id", nargs="?")
        group.add_argument("--all", action="store_true")
        if name == "apply":
            p.add_argument("--by", default="git-commit")
        p.set_defaults(func=func)

    p = sub.add_parser(
        "push-check", help="is pushing these commits safe? prints the command"
    )
    p.add_argument("--target", choices=("main", "branch"), required=True)
    p.add_argument("hashes", nargs="+", help="the commits you made, oldest first")
    p.set_defaults(func=cmd_push_check)

    for name, func in (("requeue", cmd_requeue), ("drop", cmd_drop)):
        p = sub.add_parser(name)
        p.add_argument("id")
        p.add_argument("--by", default="git-commit")
        if name == "drop":
            p.add_argument("--reason", required=True)
        p.set_defaults(func=func)

    args = parser.parse_args()
    try:
        return args.func(args)
    except PlanError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
