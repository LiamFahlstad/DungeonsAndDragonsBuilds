"""The Claude Code setup under .claude/ stays loadable.

Claude Code silently skips an agent or skill whose frontmatter is broken, and a `skills:` entry
naming a missing skill is only logged, so these mistakes would otherwise go unnoticed.
"""

import json
import re
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".claude" / "agents"
SKILLS = ROOT / ".claude" / "skills"
MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
REPO_PATH = re.compile(r"\.claude/(?:skills|hooks|agents)/[\w./-]+\.\w+")


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path}: no frontmatter"
    return yaml.safe_load(text.split("---\n", 2)[1]) or {}


def agent_files() -> list[Path]:
    return sorted(AGENTS.rglob("*.md"))


def skill_dirs() -> list[Path]:
    return sorted(p.parent for p in SKILLS.glob("*/SKILL.md"))


@pytest.mark.parametrize("path", agent_files(), ids=lambda p: p.stem)
def test_agent_frontmatter(path):
    meta = frontmatter(path)
    assert meta.get("name") == path.stem, "name must match the file name"
    assert meta.get("description"), "description is what routing reads"
    assert meta.get("model") in MODELS
    assert meta.get("memory") == "project", "every agent keeps a project memory so it can learn from its runs"
    for skill in meta.get("skills") or []:
        assert (SKILLS / skill / "SKILL.md").exists(), f"preloads missing skill {skill!r}"


MEMORIES = sorted((ROOT / ".claude" / "agent-memory").glob("*/MEMORY.md"))


@pytest.mark.parametrize("memory", MEMORIES, ids=[p.parent.name for p in MEMORIES])
def test_agent_memory_stays_curated(memory):
    # Claude Code injects only the first 200 lines; CLAUDE.md asks agents to stay under 100.
    assert len(memory.read_text(encoding="utf-8").splitlines()) <= 100, "promote or prune lessons"
    agent_names = {frontmatter(p)["name"] for p in agent_files()}
    assert memory.parent.name in agent_names, "memory folder for an agent that no longer exists"


def test_agent_names_are_unique():
    names = [frontmatter(p)["name"] for p in agent_files()]
    assert len(names) == len(set(names))


@pytest.mark.parametrize("folder", skill_dirs(), ids=lambda p: p.name)
def test_skill_frontmatter_and_links(folder):
    meta = frontmatter(folder / "SKILL.md")
    assert meta.get("name") == folder.name
    assert meta.get("description")
    for md in folder.glob("*.md"):
        for target in re.findall(r"\]\(([^)#]+)\)", md.read_text(encoding="utf-8")):
            if "://" not in target:
                assert (folder / target).exists() or (ROOT / target).exists(), f"{md.name}: broken link {target}"


@pytest.mark.parametrize("path", agent_files() + sorted(SKILLS.rglob("*.md")), ids=lambda p: p.stem)
def test_referenced_claude_files_exist(path):
    for ref in REPO_PATH.findall(path.read_text(encoding="utf-8")):
        assert (ROOT / ref).exists(), f"{path.name} points at missing {ref}"


def test_hook_scripts_exist():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    for groups in settings.get("hooks", {}).values():
        for group in groups:
            for hook in group["hooks"]:
                for ref in REPO_PATH.findall(hook.get("command", "")):
                    assert (ROOT / ref).exists(), f"hook runs missing {ref}"
