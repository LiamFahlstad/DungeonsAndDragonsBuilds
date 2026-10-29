"""Combatant cards (CardsMixin._make_card), pinned against
tests/snapshots/combat_ui_cards.json: the widget tree each kind of combatant
and state produces, and which handler every button and context menu calls.
A change meant to alter the cards regenerates it on purpose:

    UPDATE_SNAPSHOTS=1 pytest tests/test_combat_ui_cards.py
"""

import json
from functools import cache

import pytest
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QPushButton, QWidget

from Combat.EncounterLogs import LogJSONEncoder
from Combat.Monsters.CR_0.monsters import DraconicSpirit
from Combat.Monsters.CR_12.monsters import Arcanaloth
from Combat.Monsters.CR_17.monsters import SphinxOfValor
from Combat.Monsters.CR_4.monsters import ShadowDemon
from tests._combat_ui import check_golden, dump_widget, make_ui
from tests._snapshot_helpers import SNAPSHOT_DIR, build

GOLDEN_PATH = SNAPSHOT_DIR / "combat_ui_cards.json"
PLAYER_BUILD = "Y2014WarlockHexbladeDravenCursebladeCharacterBuilder"

# Handlers a card's widgets call back into; replaced by recorders.
_HANDLERS = (
    "_select_character",
    "_select_target_character",
    "_apply_failed_death_save",
    "_apply_success_death_save",
    "_revive",
    "_show_condition_info",
    "_show_rule_popup",
    "_show_visibility_info",
    "_remove_active_spell",
    "_remove_active_feature",
    "_remove_condition_from",
)


@cache
def _player():
    return build(PLAYER_BUILD)


def _ui(tmp_path):
    ui = make_ui(
        tmp_path,
        [SphinxOfValor(), Arcanaloth(), ShadowDemon(), DraconicSpirit()],
        [_player()],
    )
    return ui, {
        c["combatant_type"] if "cr" in c else "player": c for c in ui.characters
    }


def _resumed(char: dict) -> dict:
    """The char dict as a resumed combat log hands it back (plain JSON)."""
    plain = {k: v for k, v in char.items() if not k.startswith("_")}
    return json.loads(json.dumps(plain, cls=LogJSONEncoder))


def _set_hp(fraction):
    def apply(ui, chars):
        char = chars["Sphinx of Valor"]
        char["hp"] = int(char["max_hp"] * fraction)
        char["temp_hp"] = 5
        return char

    return apply


def _death(fail, success):
    def apply(ui, chars):
        char = chars["player"]
        char.update(hp=0, death_saves_fail=fail, death_saves_success=success)
        return char

    return apply


def _conditions(ui, chars):
    char = chars["Shadow Demon"]
    feature_name = chars["player"]["_feature_objects"][0].name
    char["conditions"] = ["Poisoned", "Hexed", "Bless", "Concentrating", feature_name]
    char["spell_condition_descriptions"] = {"Bless": "Add 1d4 to attacks and saves."}
    char["spell_condition_colors"] = {"Bless": "#123456"}
    return char


def _visibility(ui, chars):
    char = chars["Arcanaloth"]
    char["visibility_states"] = ["Invisible", "Half Cover", "Shimmering"]
    return char


def _timed(ui, chars):
    char = chars["player"]
    char["active_spells"] = [
        {"name": "Hex", "time_left": 42, "duration": 3600},
        {"name": "Shield", "time_left": -1},
    ]
    char["active_features"] = [{"name": "Hexblade's Curse", "time_left": 10}]
    char["action_uses"] = {"Action": 2, "Bonus Action": 0, "Reaction": 1}
    char["spell_slots"] = {3: 1, 1: 2, 2: 0}
    return char


def _modifier_scores(ui, chars):
    char = chars["Draconic Spirit"]
    char["Ability Scores"] = {"STR": 2, "DEX": -1, "CON": 0, "INT": 1, "WIS": 3}
    char["Saving Throws"] = {}
    return char


def _resumed_monster(ui, chars):
    char = _resumed(chars["Arcanaloth"])
    ui.characters.append(char)
    return char


def _selection(source, active, target):
    def apply(ui, chars):
        char = chars["Sphinx of Valor"]
        other = chars["Arcanaloth"]
        ui.phase = "COMBAT"
        ui.initiative_order = [char if active else other]
        ui.current_turn_idx = 0
        ui.selected_character = char if source else other
        ui.target_characters = [char] if target else [other]
        return char

    return apply


CASES = {
    "player": lambda ui, chars: chars["player"],
    "sphinx": lambda ui, chars: chars["Sphinx of Valor"],
    "arcanaloth": lambda ui, chars: chars["Arcanaloth"],
    "shadow_demon": lambda ui, chars: chars["Shadow Demon"],
    "draconic_spirit": lambda ui, chars: chars["Draconic Spirit"],
    "resumed_arcanaloth": _resumed_monster,
    "hp_quarter": _set_hp(0.25),
    "hp_half": _set_hp(0.5),
    "dying": _death(1, 2),
    "stabilized": _death(0, 3),
    "dead": _death(3, 0),
    "conditions": _conditions,
    "visibility": _visibility,
    "timed_and_action_uses": _timed,
    "modifier_scores": _modifier_scores,
    **{
        f"selection_{'s' * s}{'a' * a}{'t' * t}": _selection(s, a, t)
        for s, a, t in (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1),
            (1, 1, 0),
            (1, 0, 1),
            (0, 1, 1),
            (1, 1, 1),
        )
    },
}


def _describe(value):
    if isinstance(value, dict):
        return value.get("name", sorted(value))
    return value


def _record_clicks(ui, card) -> list:
    calls: list = []
    for name in _HANDLERS:

        def recorder(*args, _name=name, **kwargs):
            calls.append(
                [
                    _name,
                    [_describe(a) for a in args],
                    {k: _describe(v) for k, v in kwargs.items()},
                ]
            )

        setattr(ui, name, recorder)

    card._on_left_click()
    card._on_right_click(False)
    card._on_right_click(True)
    for widget in card.findChildren(QWidget):
        if isinstance(widget, QPushButton):
            calls.append(["click", widget.text()])
            widget.click()
        if widget.contextMenuPolicy() == Qt.ContextMenuPolicy.CustomContextMenu:
            text = widget.text() if hasattr(widget, "text") else ""
            calls.append(["context_menu", text])
            widget.customContextMenuRequested.emit(QPoint())
    return calls


@pytest.mark.parametrize("case", sorted(CASES))
def test_card_unchanged(tmp_path, case):
    ui, chars = _ui(tmp_path)
    char = CASES[case](ui, chars)
    card = ui._make_card(char)
    check_golden(
        GOLDEN_PATH,
        case,
        {"card": dump_widget(card), "clicks": _record_clicks(ui, card)},
    )
