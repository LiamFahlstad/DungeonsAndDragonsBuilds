"""The subagent edit check blocks a handback over a broken file once, then lets it through.

It was verified live on 2026-10-27, but its two input shapes are easy to break: PreToolUse
(SubagentHandback) gives no agent_transcript_path, so the hook derives it from the session
transcript and agent_id; SubagentStop gives it directly.
"""

import json
import subprocess
import sys
from pathlib import Path

HOOK = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "hooks"
    / "check_subagent_edits.py"
)


def make_session(tmp_path: Path, agent_id: str, edited: Path) -> Path:
    """A session transcript plus <session>/subagents/agent-<id>.jsonl recording one Write."""
    session = tmp_path / "session.jsonl"
    session.write_text("", encoding="utf-8")
    subagents = tmp_path / "session" / "subagents"
    subagents.mkdir(parents=True)
    entry = {
        "type": "assistant",
        "message": {
            "content": [
                {
                    "type": "tool_use",
                    "name": "Write",
                    "input": {"file_path": str(edited)},
                }
            ]
        },
    }
    (subagents / f"agent-{agent_id}.jsonl").write_text(
        json.dumps(entry) + "\n", encoding="utf-8"
    )
    return session


def run(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )


def test_handback_blocks_once_then_lets_the_agent_report(tmp_path):
    broken = tmp_path / "broken.py"
    broken.write_text("def f(:\n    pass\n", encoding="utf-8")
    agent_id = f"test-{tmp_path.name}"
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "SubagentHandback",
        "agent_id": agent_id,
        "transcript_path": str(make_session(tmp_path, agent_id, broken)),
        "cwd": str(tmp_path),
    }
    first = run(payload)
    assert first.returncode == 2 and "broken.py:1" in first.stderr
    assert run(payload).returncode == 0, "the same problem must not block twice"


def test_handback_passes_once_the_file_is_fixed(tmp_path):
    fixed = tmp_path / "fixed.py"
    fixed.write_text("def f():\n    pass\n", encoding="utf-8")
    agent_id = f"test-{tmp_path.name}"
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "SubagentHandback",
        "agent_id": agent_id,
        "transcript_path": str(make_session(tmp_path, agent_id, fixed)),
        "cwd": str(tmp_path),
    }
    assert run(payload).returncode == 0


def test_subagent_stop_uses_the_given_transcript_and_respects_stop_hook_active(
    tmp_path,
):
    broken = tmp_path / "broken.py"
    broken.write_text("x = (\n", encoding="utf-8")
    session = make_session(tmp_path, "a1", broken)
    transcript = session.with_suffix("") / "subagents" / "agent-a1.jsonl"
    base = {
        "hook_event_name": "SubagentStop",
        "agent_transcript_path": str(transcript),
        "cwd": str(tmp_path),
    }
    assert run(base | {"stop_hook_active": False}).returncode == 2
    assert run(base | {"stop_hook_active": True}).returncode == 0
