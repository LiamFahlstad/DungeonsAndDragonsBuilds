"""KEYBOARD_SHORTCUTS.md and the window's shortcut table (shortcuts.py) list
the same keys (Notes/combat-ui-refactor-plan.md, step 4): a shortcut added
to the window is documented for the GM, and a documented one exists."""

import re
from pathlib import Path

from Combat.CombatUIQt.shortcuts import SHORTCUTS

DOC = Path(__file__).resolve().parent.parent / "Combat/CombatUIQt/KEYBOARD_SHORTCUTS.md"
# How the doc writes a key that QKeySequence spells otherwise.
_DOC_NAMES = {
    "Escape": "Esc",
    "Right arrow": "Right",
    "Left arrow": "Left",
    "Up arrow": "Up",
    "Down arrow": "Down",
}


def _documented_keys() -> set[str]:
    """Every key in the first column of the doc's Shortcut Reference table:
    each bold part, "Enter / Return" being two keys and "1-9" nine."""
    text = DOC.read_text(encoding="utf-8")
    section = text.split("## Shortcut Reference", 1)[1].split("\n## ", 1)[0]
    keys: set[str] = set()
    for line in section.splitlines():
        if not line.startswith("| **"):
            continue
        first_column = line.split("|")[1]
        for bold in re.findall(r"\*\*(.+?)\*\*", first_column):
            for key in bold.split(" / "):
                key = key.strip()
                if re.fullmatch(r"\d-\d", key):
                    low, high = map(int, key.split("-"))
                    keys.update(str(n) for n in range(low, high + 1))
                else:
                    keys.add(_DOC_NAMES.get(key, key))
    return keys


def test_the_doc_lists_keys():
    assert len(_documented_keys()) > 20


def test_every_action_is_documented():
    """Each shortcut action has at least one of its keys in the doc (it may
    list one spelling: Shift+Enter, not also Shift+Return)."""
    documented = _documented_keys()
    missing = [s.name for s in SHORTCUTS if not documented & set(s.keys)]
    assert not missing, f"Shortcuts KEYBOARD_SHORTCUTS.md doesn't list: {missing}"


def test_every_documented_key_exists():
    made = {key for s in SHORTCUTS for key in s.keys}
    stale = sorted(_documented_keys() - made)
    assert (
        not stale
    ), f"KEYBOARD_SHORTCUTS.md lists keys the window doesn't have: {stale}"
