"""Add, update and list entries in Notes/discovered-issues.md, safely from many agents at once.

Every write takes a lock file next to the document, re-reads it, changes one entry, writes a
temp file and swaps it in, so concurrent agents never overwrite each other's entries. The
document always lives in the main checkout: an agent running in a .claude/worktrees/ worktree
writes to the same file as everyone else instead of a copy that would conflict on merge.

    python .claude/skills/discovered-issues/issues.py list [--status open] [--grep TEXT]
    python .claude/skills/discovered-issues/issues.py show DI-004
    python .claude/skills/discovered-issues/issues.py add --title "..." --area combat-simulator \\
        --where "Combat/CombatUIQt/damage_mixin.py:456" --by rules-checker --details "..."
    python .claude/skills/discovered-issues/issues.py update DI-004 --status fixed \\
        --commit 03bcecb0 --by combat-simulator --note "Temp HP now keep the higher value"
"""

import argparse
import datetime
import os
import re
import subprocess
import sys
import time
from pathlib import Path

DOC_RELATIVE = Path("Notes") / "discovered-issues.md"
STATUSES = ("open", "in-progress", "fixed", "wontfix")
SECTIONS = (
    ("Open", ("open", "in-progress")),
    ("Fixed", ("fixed",)),
    ("Won't fix", ("wontfix",)),
)
SECTION_TITLES = {title for title, _ in SECTIONS}
EMPTY_SECTION = "_None._"
ENTRY_HEADING = re.compile(r"^### (DI-(\d+)) · (.*)$")
STATUS_LINE = re.compile(r"^- \*\*Status:\*\* (.*)$")
LOCK_TIMEOUT_S = 30
STALE_LOCK_S = 60

PREAMBLE = """# Discovered issues

Bugs, rules mismatches and gaps that agents (and people) found but did not fix in the task at
hand. Every agent may add to this file and mark entries fixed, **only through the script**:

```bash
python .claude/skills/discovered-issues/issues.py list --status open      # what's known
python .claude/skills/discovered-issues/issues.py add --title "..." --area <agent or area> \\
    --where "<path:line>" --by <your name> --details "<what's wrong, a failing scenario, a fix>"
python .claude/skills/discovered-issues/issues.py update DI-007 --status fixed --commit <hash> --by <your name>
```

The script locks the file, so several agents can write at the same time. Don't edit entries
with Edit/Write. The `discovered-issues` skill has the rules for when to add, fix or close one.
"""


def doc_path() -> Path:
    """The document in the main checkout, even when run from a worktree.
    DISCOVERED_ISSUES_FILE overrides it (for testing the script on a scratch copy)."""
    if os.environ.get("DISCOVERED_ISSUES_FILE"):
        return Path(os.environ["DISCOVERED_ISSUES_FILE"])
    here = Path(__file__).resolve().parents[3]
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=here,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return Path(common).parent / DOC_RELATIVE
    except (OSError, subprocess.CalledProcessError):
        return here / DOC_RELATIVE


class Lock:
    """An exclusive lock file; a lock older than STALE_LOCK_S is from a crashed writer."""

    def __init__(self, path: Path):
        self.path = path.with_name(path.name + ".lock")

    def __enter__(self):
        deadline = time.monotonic() + LOCK_TIMEOUT_S
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"{os.getpid()}\n".encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > STALE_LOCK_S:
                        self.path.unlink(missing_ok=True)
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() > deadline:
                    sys.exit(
                        f"Timed out waiting for {self.path}; delete it if no writer is running."
                    )
                time.sleep(0.1)

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


def parse(text: str) -> tuple[str, list[str]]:
    """Split the document into its preamble and its entry blocks (each starting at ### DI-)."""
    preamble: list[str] = []
    entries: list[list[str]] = []
    for line in text.splitlines():
        if ENTRY_HEADING.match(line):
            entries.append([line])
        elif (
            line.startswith("## ") and line[3:].strip() in SECTION_TITLES
        ) or line.strip() == EMPTY_SECTION:
            continue
        elif entries:
            entries[-1].append(line)
        else:
            preamble.append(line)
    return "\n".join(preamble).rstrip() + "\n", [
        "\n".join(block).strip() for block in entries
    ]


def entry_id(block: str) -> int:
    return int(ENTRY_HEADING.match(block.splitlines()[0]).group(2))


def entry_status(block: str) -> str:
    for line in block.splitlines():
        match = STATUS_LINE.match(line)
        if match:
            word = match.group(1).split()[0].strip("*`·")
            return word if word in STATUSES else "open"
    return "open"


def render(preamble: str, entries: list[str]) -> str:
    parts = [preamble.rstrip()]
    for title, statuses in SECTIONS:
        parts.append(f"## {title}")
        chosen = sorted(
            (b for b in entries if entry_status(b) in statuses), key=entry_id
        )
        parts.extend(chosen or [EMPTY_SECTION])
    return "\n\n".join(parts) + "\n"


def write_atomically(path: Path, text: str) -> None:
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    for attempt in range(20):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:  # Windows: a reader has the file open for a moment
            time.sleep(0.1 * (attempt + 1))
    tmp.unlink(missing_ok=True)
    sys.exit(f"Could not replace {path}; is it open in another program?")


def load(path: Path) -> tuple[str, list[str]]:
    if not path.exists():
        return PREAMBLE, []
    return parse(path.read_text(encoding="utf-8"))


def find(entries: list[str], ident: str) -> int:
    wanted = int(ident.upper().removeprefix("DI-"))
    for i, block in enumerate(entries):
        if entry_id(block) == wanted:
            return i
    sys.exit(f"No entry {ident}.")


def today() -> str:
    return datetime.date.today().isoformat()


def status_text(status: str, commit: str | None) -> str:
    if status == "fixed":
        return f"fixed · {today()} · {commit or 'uncommitted'}"
    return status


def cmd_add(args) -> None:
    path = doc_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    details = args.details or ""
    if args.details_file:
        details = Path(args.details_file).read_text(encoding="utf-8")
    with Lock(path):
        preamble, entries = load(path)
        new_id = max((entry_id(b) for b in entries), default=0) + 1
        lines = [
            f"### DI-{new_id:03d} · {args.title.strip()}",
            f"- **Status:** {args.status}",
            f"- **Area:** {args.area}",
        ]
        if args.where:
            lines.append(f"- **Where:** {', '.join(f'`{w}`' for w in args.where)}")
        if details.strip():
            lines += ["", details.strip()]
        lines += ["", "**History**", f"- {today()} {args.by}: found"]
        entries.append("\n".join(lines))
        write_atomically(path, render(preamble, entries))
    print(f"DI-{new_id:03d}")


def cmd_update(args) -> None:
    if not (args.status or args.note):
        sys.exit("Give --status and/or --note.")
    path = doc_path()
    with Lock(path):
        preamble, entries = load(path)
        i = find(entries, args.id)
        lines = entries[i].splitlines()
        event = []
        if args.status:
            for j, line in enumerate(lines):
                if STATUS_LINE.match(line):
                    lines[j] = f"- **Status:** {status_text(args.status, args.commit)}"
                    break
            else:
                lines.insert(
                    1, f"- **Status:** {status_text(args.status, args.commit)}"
                )
            event.append(
                f"marked {args.status}" + (f" in {args.commit}" if args.commit else "")
            )
        if args.note:
            event.append(args.note.strip())
        if "**History**" not in lines:
            lines += ["", "**History**"]
        lines.append(f"- {today()} {args.by}: {'; '.join(event)}")
        entries[i] = "\n".join(lines)
        write_atomically(path, render(preamble, entries))
    print(f"{args.id.upper()} updated")


def cmd_list(args) -> None:
    _, entries = load(doc_path())
    for block in sorted(entries, key=entry_id):
        status = entry_status(block)
        if args.status and status != args.status:
            continue
        if args.grep and args.grep.lower() not in block.lower():
            continue
        heading = ENTRY_HEADING.match(block.splitlines()[0])
        print(f"{heading.group(1)}  {status:<11} {heading.group(3)}")


def cmd_show(args) -> None:
    _, entries = load(doc_path())
    print(entries[find(entries, args.id)])


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a new entry; prints its id")
    add.add_argument("--title", required=True, help="one line: what is wrong")
    add.add_argument(
        "--area", required=True, help="the agent or area that owns the fix"
    )
    add.add_argument("--where", action="append", help="path[:line]; repeatable")
    add.add_argument("--by", required=True, help="who found it (agent name or 'user')")
    add.add_argument("--details", help="what's wrong, a failing scenario, the fix")
    add.add_argument("--details-file", help="read --details from this file")
    add.add_argument("--status", choices=STATUSES, default="open")
    add.set_defaults(func=cmd_add)

    update = sub.add_parser("update", help="change an entry's status and/or add a note")
    update.add_argument("id", help="e.g. DI-004")
    update.add_argument("--status", choices=STATUSES)
    update.add_argument("--commit", help="the commit that fixed it")
    update.add_argument("--note", help="one line for the entry's history")
    update.add_argument("--by", required=True, help="who made the change")
    update.set_defaults(func=cmd_update)

    lister = sub.add_parser("list", help="one line per entry")
    lister.add_argument("--status", choices=STATUSES)
    lister.add_argument("--grep", help="case-insensitive text the entry must contain")
    lister.set_defaults(func=cmd_list)

    show = sub.add_parser("show", help="print one entry")
    show.add_argument("id")
    show.set_defaults(func=cmd_show)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
