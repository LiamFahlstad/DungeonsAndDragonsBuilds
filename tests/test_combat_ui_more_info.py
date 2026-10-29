"""The combat UI's More Info dialog (DialogsMixin._show_more_info), pinned
against tests/snapshots/combat_ui_more_info.json: the widget tree it builds
for each kind of combatant, and what each expandable section shows when
toggled. A change meant to alter the dialog regenerates it on purpose:

    UPDATE_SNAPSHOTS=1 pytest tests/test_combat_ui_more_info.py
"""

import json
from functools import cache

import pytest
from PyQt6.QtWidgets import QLabel, QPushButton

from Combat.Combatants import Pirate
from Combat.EncounterLogs import LogJSONEncoder
from Combat.Monsters.CR_0.monsters import DraconicSpirit, SwarmOfBats
from Combat.Monsters.CR_12.monsters import Arcanaloth
from Combat.Monsters.CR_17.monsters import SphinxOfValor
from Combat.Monsters.CR_4.monsters import ShadowDemon
from tests._combat_ui import check_golden, dump_widget, make_ui, open_dialog
from tests._snapshot_helpers import SNAPSHOT_DIR, build

GOLDEN_PATH = SNAPSHOT_DIR / "combat_ui_more_info.json"
PLAYER_BUILD = "Y2014WarlockHexbladeDravenCursebladeCharacterBuilder"


@cache
def _player():
    return build(PLAYER_BUILD)


def _texts(dialog) -> list[str]:
    return [w.text() for w in dialog.findChildren((QLabel, QPushButton))]


def test_a_save_with_a_prose_dc_opens_without_a_probability_table(
    tmp_path, monkeypatch
):
    # Draconic Spirit's Breath Weapon DC "equals your spell save DC": there's
    # no number to tabulate, so it's listed as a plain ability.
    ui = make_ui(tmp_path, [DraconicSpirit()])
    ui.selected_character = ui.characters[0]
    texts = _texts(open_dialog(monkeypatch, ui._show_more_info))
    breath = [t for t in texts if t.startswith("<b><i>Breath Weapon.")]
    assert breath == [
        "<b><i>Breath Weapon.</i></b> Dexterity Saving Throw: DC equals your"
        " spell save DC, each creature in a 30-foot Cone. Failure: 2d6 damage of"
        " a type this spirit has Resistance to (your choice when you cast the"
        " spell). Success: Half damage."
    ]


def test_more_info_needs_a_selected_combatant(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate()])
    opened = []
    monkeypatch.setattr(
        "PyQt6.QtWidgets.QDialog.exec", lambda self: opened.append(self)
    )
    ui._show_more_info()
    assert opened == []


class _QuietFeature:
    """A feature whose description is None: listed by name only."""

    name = "Quiet Feature"
    origin = "Test"

    def get_description(self, character):
        return None


class _BrokenFeature:
    """A feature whose description raises: listed by name only."""

    name = "Broken Feature"
    origin = "Test"

    def get_description(self, character):
        raise RuntimeError("no description")


def _player_case(adjust=None):
    """The full player, or (with `adjust`) a trimmed one -- two features,
    three spells, one weapon -- so each variant's golden stays small."""

    def make(tmp_path):
        ui = make_ui(tmp_path, [], [_player()])
        char = ui.characters[0]
        if adjust:
            char["_feature_objects"] = char["_feature_objects"][:2]
            char["features"] = char["features"][:2]
            char["spells_with_level"] = char["spells_with_level"][:3]
            char["_weapons_objects"] = char["_weapons_objects"][:1]
            adjust(char)
        return ui, char

    return make


def _monster_case(monster_class, adjust=None):
    def make(tmp_path):
        ui = make_ui(tmp_path, [monster_class()])
        char = ui.characters[0]
        if adjust:
            adjust(char)
        return ui, char

    return make


def _resumed(char: dict) -> None:
    """Replace the dict's contents with what a resumed combat log hands back."""
    plain = {k: v for k, v in char.items() if not k.startswith("_")}
    char.clear()
    char.update(json.loads(json.dumps(plain, cls=LogJSONEncoder)))


def _in_combat(char):
    char.update(
        temp_hp=4,
        conditions=["Poisoned", "Hexed"],
        spell_slots={1: 2, 2: 0, 3: 1},
    )


def _without_stat_block(char):
    del char["_stat_block"]


def _feature_fallbacks(char):
    char["_feature_objects"] = [
        _QuietFeature(),
        _BrokenFeature(),
        *char["_feature_objects"],
    ]


def _features_list_only(char):
    char["_feature_objects"] = []


def _unknown_spell(char):
    char["spells_with_level"] = [
        *char["spells_with_level"],
        ("Homebrew Hex", 1, char["spells_with_level"][0][2]),
    ]


def _described(char):
    char["description"] = "A cloud of shrieking bats."
    char["Saving Throws"] = {}


CASES = {
    "player": _player_case(),
    "player_in_combat": _player_case(_in_combat),
    "player_without_stat_block": _player_case(_without_stat_block),
    "player_feature_fallbacks": _player_case(_feature_fallbacks),
    "player_features_list_only": _player_case(_features_list_only),
    "player_unknown_spell": _player_case(_unknown_spell),
    "sphinx": _monster_case(SphinxOfValor),
    "arcanaloth": _monster_case(Arcanaloth),
    "arcanaloth_resumed": _monster_case(Arcanaloth, _resumed),
    "shadow_demon": _monster_case(ShadowDemon),
    "draconic_spirit": _monster_case(DraconicSpirit),
    "swarm_described_no_saves": _monster_case(SwarmOfBats, _described),
    "pirate": _monster_case(Pirate),
}


def _toggles(dialog) -> list:
    """Expand then collapse every expandable section; record its header text
    and whether its content shows."""
    out = []
    for button in dialog.findChildren(QPushButton):
        if not button.isCheckable():
            continue
        wrapper = button.parentWidget()
        assert wrapper is not None and wrapper.layout() is not None
        content_item = wrapper.layout().itemAt(1)  # type: ignore[union-attr]
        assert content_item is not None
        content = content_item.widget()
        assert content is not None
        states = []
        for _ in range(2):
            button.toggle()
            states.append([button.text(), not content.isHidden()])
        out.append(states)
    return out


@pytest.mark.parametrize("case", sorted(CASES))
def test_more_info_unchanged(tmp_path, monkeypatch, case):
    ui, char = CASES[case](tmp_path)
    ui.selected_character = char
    dialog = open_dialog(monkeypatch, ui._show_more_info)
    check_golden(
        GOLDEN_PATH,
        case,
        {"dialog": dump_widget(dialog), "toggles": _toggles(dialog)},
    )
