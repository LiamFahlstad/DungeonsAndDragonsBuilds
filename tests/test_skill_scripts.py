"""The scripts bundled with the .claude/skills keep working against the real codebase.

Skills point agents at these scripts as the source of truth, so a script that silently broke
(a renamed import, a moved file) would mislead every agent that preloads the skill.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".claude" / "skills"
SCRIPTS = sorted(SKILLS.glob("*/*.py"))


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, timeout=300)


@pytest.mark.parametrize("script", SCRIPTS, ids=[f"{p.parent.name}/{p.name}" for p in SCRIPTS])
def test_script_help(script):
    result = run(str(script), "--help")
    assert result.returncode == 0, result.stderr


def test_every_usage_tag_is_valid():
    result = run(str(SKILLS / "usage-tags" / "tag_report.py"), "check")
    assert result.returncode == 0, result.stdout + result.stderr


def test_abilities_reference_renders_every_subclass():
    from Model.Creatures import MonsterAbilities

    expected = {
        name
        for name, obj in vars(MonsterAbilities).items()
        if isinstance(obj, type)
        and issubclass(obj, MonsterAbilities.MonsterAbility)
        and obj is not MonsterAbilities.MonsterAbility
    }
    result = run(str(SKILLS / "monster-stat-blocks" / "abilities.py"))
    assert result.returncode == 0, result.stderr
    listed = {line.split()[1] for line in result.stdout.splitlines() if line.startswith("## ")}
    assert listed == expected
    assert "could not build" not in result.stdout


def test_check_monster_reports_every_check():
    result = run(str(SKILLS / "balance-monster" / "check_monster.py"), "Accursed")
    for label in ("score", "implied CR", "outliers", "abilities", "fields", "RESULT"):
        assert f"  {label}" in result.stdout, result.stdout + result.stderr


def test_check_monster_never_fails_official_monsters():
    result = run(str(SKILLS / "balance-monster" / "check_monster.py"), "Air Elemental")
    assert result.returncode == 0, result.stdout
    assert "n/a (official monster)" in result.stdout
