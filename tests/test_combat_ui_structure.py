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
# -1 at step 5.3's summons slice (_place_as_in_turn_order is Fight's, R26).
MAX_WINDOW_STATE_STUBS = 210
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
