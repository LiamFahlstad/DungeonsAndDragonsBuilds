"""format_changed.sh formats what it's given, honours format.sh's exclusions, and never re-stages
a partly staged file (which would sneak unstaged edits into a commit)."""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "format_changed.sh"
UGLY = "def f( a ):\n  return a\n"

pytestmark = [
    pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash"),
    pytest.mark.skipif(
        subprocess.run(
            ["python", "-m", "black", "--version"], capture_output=True
        ).returncode
        != 0,
        reason="needs black",
    ),
]


def run(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    # Relative paths only: on Windows "bash" may be Git Bash or WSL, which see drive paths
    # differently (and bash reads a Windows path's backslashes as escapes).
    return subprocess.run(
        ["bash", "format_changed.sh", *args], cwd=cwd, capture_output=True, text=True
    )


def test_formats_a_given_file(tmp_path):
    shutil.copy(SCRIPT, tmp_path / "format_changed.sh")
    target = tmp_path / "ugly.py"
    target.write_text(UGLY, encoding="utf-8")
    assert run("--check", "ugly.py", cwd=tmp_path).returncode == 1
    assert run("ugly.py", cwd=tmp_path).returncode == 0
    assert target.read_text(encoding="utf-8") == "def f(a):\n    return a\n"


def test_skips_format_sh_exclusions():
    # .claude/ is excluded (it holds other agents' worktrees), even when a file is named explicitly.
    result = run("--check", ".claude/hooks/rebuild_agent_index.py")
    assert result.returncode == 0, result.stdout + result.stderr


def test_staged_refuses_partly_staged_file(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(SCRIPT, repo / "format_changed.sh")
    git = lambda *a: subprocess.run(
        ["git", *a], cwd=repo, check=True, capture_output=True
    )  # noqa: E731
    git("init", "-q")
    (repo / "mod.py").write_text(UGLY, encoding="utf-8")
    git("add", "mod.py")
    (repo / "mod.py").write_text(
        UGLY + "x=1\n", encoding="utf-8"
    )  # an unstaged edit on top
    result = run("--staged", cwd=repo)
    assert result.returncode == 1
    assert "unstaged changes" in result.stderr
    assert (repo / "mod.py").read_text(
        encoding="utf-8"
    ) == UGLY + "x=1\n", "must not touch the file"
