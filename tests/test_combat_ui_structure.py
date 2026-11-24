"""The combat UI's structure only gets better (Notes/combat-ui-refactor-plan.md,
Step 0).

Each rule starts from today's numbers, as test_layering.py does:

- No function in Combat/ is longer than MAX_FUNCTION_LINES, except the ones
  in LONG_FUNCTIONS, and those may not grow past their listed length. One
  that is short enough now must come off the list, so it can't go stale.
- CombatWindowState (Combat/CombatUIQt/state.py) has at most
  MAX_WINDOW_STATE_STUBS methods: each is a call from one mixin into
  another, which the plan's steps 5 and 7 remove.
- At most MAX_INLINE_STYLES setStyleSheet(...) calls outside styles.py:
  styling belongs in its QSS (Step 1).
- Folders and names (Step 10): no file loose in Combat/ beyond
  LOOSE_IN_COMBAT, no two modules under Combat/ named alike beyond
  NAME_CLASHES, and no Combat.Tools import that makes Tools/ runtime code
  beyond TOOLS_IMPORTERS. Each list may only shrink, and an entry that's
  clean now must come off it.

A refactor step that lowers a number lowers it here too. Feature work that
would raise one extracts a helper instead (a long function), or says why in
the plan's Revisions and raises the number (a stub, a style).
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.xdist_group("repo_scan")

REPO = Path(__file__).resolve().parent.parent
COMBAT = REPO / "Combat"
UI = COMBAT / "CombatUIQt"
# Generated stat blocks and hand-run report scripts aren't the fight's code.
SKIPPED = {"Monsters", "Tools", "__pycache__"}

MAX_FUNCTION_LINES = 150

# "path::Qualified.name" -> the most lines it may have.
LONG_FUNCTIONS = {
    "Combat/CombatUIQt/conditions_mixin.py::ConditionsMixin._apply_effect_to_targets": 236,
    "Combat/CombatUIQt/dialogs_mixin.py::DialogsMixin._show_statistics": 177,
    "Combat/Fight/effect_options.py::_described_option": 161,
}

# 207 at step 0; +4 at step 3c, so the Use / Cast dialog (use_cast/dialog.py)
# can type its app as CombatWindowState instead of importing ConditionsMixin;
# -1 at step 5.3's summons slice (_place_as_in_turn_order is Fight's, R26),
# -1 at the log's (_take_combatants_from is Combat/Fight/log.py's, R29).
MAX_WINDOW_STATE_STUBS = 209
MAX_INLINE_STYLES = 23


def _combat_files() -> list[Path]:
    return sorted(
        path
        for path in COMBAT.rglob("*.py")
        if not SKIPPED.intersection(path.relative_to(COMBAT).parts)
    )


def _functions(node: ast.AST, prefix: str = ""):
    """(qualified name, line count) of every function under node, nested
    ones included ("Class.method.inner")."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = f"{prefix}.{child.name}" if prefix else child.name
            if not isinstance(child, ast.ClassDef):
                assert child.end_lineno is not None
                yield name, child.end_lineno - child.lineno + 1
            yield from _functions(child, name)
        else:
            yield from _functions(child, prefix)


def _function_lengths() -> dict[str, int]:
    lengths = {}
    for path in _combat_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        where = path.relative_to(REPO).as_posix()
        for name, lines in _functions(tree):
            lengths[f"{where}::{name}"] = lines
    return lengths


def test_no_new_long_functions():
    too_long = {
        key: lines
        for key, lines in _function_lengths().items()
        if lines > MAX_FUNCTION_LINES and key not in LONG_FUNCTIONS
    }
    assert not too_long, (
        f"Functions over {MAX_FUNCTION_LINES} lines; split them into named "
        f"helpers: {too_long}"
    )


def test_long_functions_do_not_grow():
    lengths = _function_lengths()
    grown = {
        key: f"{lengths[key]} > {limit}"
        for key, limit in LONG_FUNCTIONS.items()
        if key in lengths and lengths[key] > limit
    }
    assert not grown, (
        "These long functions grew; extract the new code into a helper "
        f"instead: {grown}"
    )


def test_long_function_list_is_current():
    lengths = _function_lengths()
    stale = [key for key in LONG_FUNCTIONS if lengths.get(key, 0) <= MAX_FUNCTION_LINES]
    assert not stale, f"Gone or short enough now; take them off LONG_FUNCTIONS: {stale}"


def _window_state_stubs() -> int:
    tree = ast.parse((UI / "state.py").read_text(encoding="utf-8"))
    state = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "CombatWindowState"
    )
    return sum(
        isinstance(node, ast.FunctionDef)
        and isinstance(node.body[-1], ast.Raise)
        and "NotImplementedError" in ast.unparse(node.body[-1])
        for node in state.body
    )


def test_window_state_stubs_do_not_grow():
    if not (UI / "state.py").exists():
        return  # Step 7 deleted it.
    count = _window_state_stubs()
    assert count <= MAX_WINDOW_STATE_STUBS, (
        f"CombatWindowState has {count} methods, more than "
        f"{MAX_WINDOW_STATE_STUBS}."
    )


def _inline_styles() -> int:
    count = 0
    for path in sorted(UI.rglob("*.py")):
        if path.name == "styles.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        count += sum(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "setStyleSheet"
            for node in ast.walk(tree)
        )
    return count


def test_inline_styles_do_not_grow():
    count = _inline_styles()
    assert count <= MAX_INLINE_STYLES, (
        f"{count} setStyleSheet calls outside styles.py, more than "
        f"{MAX_INLINE_STYLES}: style it in styles.py by objectName instead."
    )


# The fight's Qt-free core (combat-ui-refactor-plan step 5): its folders
# never import Qt or the window, so it runs and is tested without a
# QApplication, and a second front end (the player link) can use it.
QT_FREE = ("Combat/Fight", "Combat/Effects", "Combat/Arena")


def test_the_fight_core_imports_no_qt():
    offenders = []
    for folder in QT_FREE:
        for path in sorted((REPO / folder).rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names, line = [], 0
                if isinstance(node, ast.Import):
                    names, line = [alias.name for alias in node.names], node.lineno
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    names, line = [node.module or ""], node.lineno
                for name in names:
                    if name.startswith(("PyQt6", "Combat.CombatUIQt")):
                        where = path.relative_to(REPO).as_posix()
                        offenders.append(f"{where}:{line} {name}")
    assert not offenders, offenders


# Folders and names (combat-ui-refactor-plan step 10).


def _check_allowlist(found: set, allowlist: set, rule: str, fix: str) -> None:
    new = sorted(found - allowlist)
    stale = sorted(allowlist - found)
    assert not new, f"{rule}: new ones {new}. {fix}"
    assert not stale, f"{rule}: these are gone now, take them off the list: {stale}"


# Combat/ holds packages, these two files, and the files loose in it today,
# which step 10 moves into packages.
KEPT_IN_COMBAT = {"CHEATSHEET.md", "Definitions.py"}
LOOSE_IN_COMBAT = {
    "Campaign.py",
    "Combatants.py",
    "EncounterConfig.py",
    "EncounterDifficulty.py",
    "EncounterLogs.py",
    "LogFiles.py",
    "PartyAllies.py",
    "PlayerCombatant.py",
    "PlayerLog.py",
    "Rules.py",
    "Scenario.py",
    "Scenarios.py",
    "Summons.py",
    "WildShape.py",
    "monsters_raw.json",
    "rules.json",
}


def test_no_new_files_loose_in_combat():
    loose = {path.name for path in COMBAT.iterdir() if path.is_file()}
    _check_allowlist(
        loose - KEPT_IN_COMBAT,
        LOOSE_IN_COMBAT,
        "Files loose in Combat/",
        "Put them in the package for their job.",
    )


# Files that every folder of a kind has by design, so they share a name:
# each campaign's (Combat/Campaigns/<Campaign>/) and each generated CR tier's
# (Combat/Monsters/CR_<x>/). Matched with their case.
REPEATED_BY_DESIGN = {
    "Campaigns": {"campaign.py", "encounters.py"},
    "Monsters": {"monsters.py", "monsters_homebrew.py"},
}

# Module names under Combat/ that clash today, ignoring case and "_": the
# name -> every module that has it.
NAME_CLASHES: dict[str, set[str]] = {
    "summons": {"Combat/Fight/summons.py", "Combat/Summons.py"},
    "wildshape": {"Combat/Fight/wild_shape.py", "Combat/WildShape.py"},
}


def _name_clashes() -> dict[str, set[str]]:
    homes: dict[str, set[str]] = {}
    for path in COMBAT.rglob("*.py"):
        parts = path.relative_to(COMBAT).parts
        if "__pycache__" in parts or path.name == "__init__.py":
            continue
        if len(parts) == 3 and path.name in REPEATED_BY_DESIGN.get(parts[0], ()):
            continue
        name = path.stem.lower().replace("_", "")
        homes.setdefault(name, set()).add(path.relative_to(REPO).as_posix())
    return {name: paths for name, paths in homes.items() if len(paths) > 1}


def test_no_new_name_clashes():
    clashes = _name_clashes()
    _check_allowlist(
        {(name, frozenset(paths)) for name, paths in clashes.items()},
        {(name, frozenset(paths)) for name, paths in NAME_CLASHES.items()},
        "Modules under Combat/ with the same name, ignoring case and _",
        "Name each for what's in it (a clash that changed members is listed"
        " here too: update its NAME_CLASHES entry).",
    )


# Tools/ holds scripts run by hand, never code the app runs. Only tests and
# the skills' scripts import Combat.Tools, to test or reuse such a script,
# and never a Tools module that other code imports too. Today's offenders
# (none since monster_effect_text.py moved to Fight/):
TOOLS_IMPORTERS: set[str] = set()
_NOT_SCANNED = {".claude", ".git", ".venv", "venv", "Output", "SourceTexts"}
_MAY_USE_TOOLS = ("tests/", ".claude/skills/")


def _python_files_outside_tools():
    """Every project .py file but Combat/Tools/'s, the skills' scripts
    included (not .claude/worktrees/: other agents' checkouts)."""
    for top in sorted(REPO.iterdir()):
        if top.is_dir() and top.name not in _NOT_SCANNED:
            yield from sorted(top.rglob("*.py"))
        elif top.suffix == ".py":
            yield top
    yield from sorted((REPO / ".claude" / "skills").glob("*/*.py"))


def _tools_imports() -> set[tuple[str, str]]:
    """(file, Combat.Tools module) for each import of Tools/ outside it."""
    found = set()
    for path in _python_files_outside_tools():
        where = path.relative_to(REPO).as_posix()
        if where.startswith("Combat/Tools/") or "__pycache__" in where:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                module = node.module or ""
                if module == "Combat.Tools":
                    names = [f"{module}.{alias.name}" for alias in node.names]
                else:
                    names = [module]
            else:
                continue
            found.update(
                (where, name)
                for name in names
                if name == "Combat.Tools" or name.startswith("Combat.Tools.")
            )
    return found


def test_tools_is_not_runtime_code():
    imports = _tools_imports()
    runtime_modules = {
        module for where, module in imports if not where.startswith(_MAY_USE_TOOLS)
    }
    offenders = {
        where
        for where, module in imports
        if not where.startswith(_MAY_USE_TOOLS) or module in runtime_modules
    }
    _check_allowlist(
        offenders,
        TOOLS_IMPORTERS,
        "Combat.Tools imported as runtime code",
        "Move the module the app runs out of Tools/ (into Fight/, say).",
    )
