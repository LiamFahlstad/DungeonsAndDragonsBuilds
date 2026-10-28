"""The commit-plans script commits exactly what a plan names, even while the shared tree moves.

Each test runs the script against a scratch git repository (and a scratch bare remote), never
against this checkout.
"""

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "skills"
    / "commit-plans"
    / "commit_plan.py"
)


def sh(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(args, cwd=repo, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AssertionError(f"{args} failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def plan(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        env={
            **__import__("os").environ,
            "COMMIT_PLANS_DIR": str(repo.parent / "plans"),
        },
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    work.mkdir()
    sh(tmp_path, "git", "init", "-q", "--bare", str(remote))
    sh(work, "git", "init", "-q", "-b", "main")
    sh(work, "git", "config", "user.name", "Test")
    sh(work, "git", "config", "user.email", "test@example.com")
    sh(work, "git", "config", "core.autocrlf", "false")
    (work / "a.py").write_text("x = 1\n")
    (work / "b.txt").write_text("one\n")
    sh(work, "git", "add", "a.py", "b.txt")
    sh(work, "git", "commit", "-q", "-m", "Initial")
    sh(work, "git", "remote", "add", "origin", str(remote))
    sh(work, "git", "push", "-q", "origin", "main")
    return work


def write_message(repo: Path, text: str = "Change a\n\nWhy it changes.\n") -> str:
    path = repo.parent / "msg.txt"
    path.write_text(text)
    return str(path)


def new_plan(repo: Path, *paths: str) -> str:
    args = ["new", "--message-file", write_message(repo), "--by", "test"]
    for p in paths:
        args += ["--path", p]
    result = plan(repo, *args)
    assert result.returncode == 0, result.stderr
    return result.stdout.splitlines()[0]


def test_apply_commits_only_the_planned_file(repo):
    (repo / "a.py").write_text("x = 2\n")
    plan_id = new_plan(repo, "a.py")
    # Another agent stages its own work after the plan was written.
    (repo / "b.txt").write_text("two\n")
    sh(repo, "git", "add", "b.txt")

    result = plan(repo, "apply", plan_id)

    assert result.returncode == 0, result.stdout + result.stderr
    assert sh(repo, "git", "log", "-1", "--format=%s") == "Change a"
    assert sh(repo, "git", "show", "--name-only", "--format=", "HEAD") == "a.py"
    assert sh(repo, "git", "show", "HEAD:a.py") == "x = 2"
    # The other agent's staging survives, and a.py doesn't show as a staged revert.
    assert sh(repo, "git", "diff", "--cached", "--name-only") == "b.txt"
    assert sh(repo, "git", "status", "--porcelain", "--", "a.py") == ""
    assert "done" in plan(repo, "list", "--state", "all").stdout


def test_plan_is_blocked_when_the_file_moves_after_planning(repo):
    (repo / "a.py").write_text("x = 2\n")
    plan_id = new_plan(repo, "a.py")
    (repo / "a.py").write_text("x = 3\n")

    result = plan(repo, "apply", plan_id)

    assert result.returncode == 1
    assert "changed in the working tree" in result.stdout
    assert sh(repo, "git", "log", "-1", "--format=%s") == "Initial"
    assert "blocked" in plan(repo, "list", "--state", "blocked").stdout


def test_plan_is_blocked_when_head_changes_the_file(repo):
    (repo / "a.py").write_text("x = 2\n")
    plan_id = new_plan(repo, "a.py")
    (repo / "a.py").write_text("x = 5\n")
    sh(repo, "git", "commit", "-q", "-am", "Someone else commits a.py")
    (repo / "a.py").write_text("x = 2\n")

    result = plan(repo, "apply", plan_id)

    assert result.returncode == 1
    assert "changed in HEAD since planning" in result.stdout
    assert sh(repo, "git", "show", "HEAD:a.py") == "x = 5"


def test_a_plan_someone_already_committed_is_marked_done(repo):
    (repo / "a.py").write_text("x = 2\n")
    plan_id = new_plan(repo, "a.py")
    sh(repo, "git", "commit", "-q", "-am", "Someone else commits the same change")

    result = plan(repo, "apply", plan_id)

    assert result.returncode == 0
    assert "already in HEAD" in result.stdout
    assert sh(repo, "git", "rev-list", "--count", "HEAD") == "2"


def test_a_partial_plan_commits_the_given_bytes(repo):
    (repo / "b.txt").write_text("one\nmine\ntheirs\n")
    partial = repo.parent / "b_partial.txt"
    partial.write_bytes(b"one\nmine\n")
    result = plan(
        repo,
        "new",
        "--message-file",
        write_message(repo, "Add mine\n"),
        "--by",
        "test",
        "--content",
        f"b.txt={partial}",
    )
    assert result.returncode == 0, result.stderr

    assert plan(repo, "apply", "--all").returncode == 0

    assert sh(repo, "git", "show", "HEAD:b.txt") == "one\nmine"
    assert (repo / "b.txt").read_text() == "one\nmine\ntheirs\n"


def test_two_plans_cant_claim_the_same_file(repo):
    (repo / "a.py").write_text("x = 2\n")
    new_plan(repo, "a.py")
    result = plan(
        repo,
        "new",
        "--message-file",
        write_message(repo),
        "--by",
        "t",
        "--path",
        "a.py",
    )
    assert result.returncode == 2
    assert "already in pending plan" in result.stderr


def test_new_refuses_python_that_does_not_compile(repo):
    (repo / "a.py").write_text("x = (\n")
    result = plan(
        repo,
        "new",
        "--message-file",
        write_message(repo),
        "--by",
        "t",
        "--path",
        "a.py",
    )
    assert result.returncode == 2
    assert "doesn't compile" in result.stderr


def test_push_check_refuses_to_publish_someone_elses_commit(repo):
    (repo / "b.txt").write_text("two\n")
    sh(repo, "git", "commit", "-q", "-am", "Someone else's unpushed commit")
    (repo / "a.py").write_text("x = 2\n")
    plan_id = new_plan(repo, "a.py")
    assert plan(repo, "apply", plan_id).returncode == 0
    mine = sh(repo, "git", "rev-parse", "HEAD")

    result = plan(repo, "push-check", "--target", "main", mine)

    assert result.returncode == 1
    assert "Someone else's unpushed commit" in result.stdout


def test_push_check_prints_the_push_command_for_own_commits(repo):
    (repo / "a.py").write_text("x = 2\n")
    assert plan(repo, "apply", new_plan(repo, "a.py")).returncode == 0
    mine = sh(repo, "git", "rev-parse", "HEAD")

    result = plan(repo, "push-check", "--target", "main", mine)

    assert result.returncode == 0, result.stdout
    assert f"git push origin {mine}:main" in result.stdout
