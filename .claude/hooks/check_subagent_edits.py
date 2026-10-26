"""SubagentStop hook: refuse to let a subagent finish while a file it edited is broken.

Reads the hook input JSON from stdin, collects every file the subagent touched with
Edit/Write/NotebookEdit (from its own transcript, so parallel agents never block each
other), and checks:

- every edited .py file still compiles;
- no edit landed in another agent's worktree under .claude/worktrees/.

On a problem it exits 2 with the details on stderr, which Claude Code hands back to the
subagent as its next instruction. It blocks at most once per stop (stop_hook_active),
so a subagent that cannot fix the problem still ends and reports it.

Edits made through Bash (sed, scripts) are not in the transcript as file edits and are
not checked here - the verify-agent-work skill covers those.
"""

import json
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
WORKTREES = Path(".claude") / "worktrees"


def edited_files(transcript: Path) -> list[Path]:
    files: dict[str, None] = {}
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if block.get("type") == "tool_use" and block.get("name") in EDIT_TOOLS:
                path = block.get("input", {}).get("file_path") or block.get("input", {}).get("notebook_path")
                if path:
                    files[path] = None
    return [Path(p) for p in files]


def own_worktree(cwd: Path) -> Path | None:
    """The worktree the agent runs in, if it runs in one."""
    parts = cwd.resolve().parts
    for i in range(len(parts) - 2):
        if parts[i] == ".claude" and parts[i + 1] == "worktrees":
            return Path(*parts[: i + 3])
    return None


def problems_in(files: list[Path], cwd: Path) -> list[str]:
    problems = []
    home_worktree = own_worktree(cwd)
    for path in files:
        resolved = path.resolve()
        if WORKTREES.as_posix() in resolved.as_posix():
            if home_worktree is None or not resolved.is_relative_to(home_worktree):
                problems.append(f"{path}: edited inside another agent's worktree (.claude/worktrees). Revert that edit.")
                continue
        if resolved.suffix != ".py" or not resolved.exists():
            continue
        try:
            compile(resolved.read_text(encoding="utf-8"), str(resolved), "exec")
        except SyntaxError as error:
            problems.append(f"{path}:{error.lineno}: {error.msg}")
        except (UnicodeDecodeError, ValueError) as error:
            problems.append(f"{path}: {error}")
    return problems


def main() -> int:
    hook_input = json.load(sys.stdin)
    if hook_input.get("stop_hook_active"):
        return 0
    transcript = hook_input.get("agent_transcript_path")
    if not transcript or not Path(transcript).expanduser().exists():
        return 0
    cwd = Path(hook_input.get("cwd") or ".")
    problems = problems_in(edited_files(Path(transcript).expanduser()), cwd)
    if not problems:
        return 0
    print(
        "Before you finish, fix these problems in files you edited "
        "(and mention them in your final report):\n" + "\n".join(f"- {p}" for p in problems),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
