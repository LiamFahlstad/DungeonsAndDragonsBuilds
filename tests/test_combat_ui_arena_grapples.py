"""Grapples on the battle map in the combat UI (Notes/combat-arena-plan.md,
step 22): the Grappled creature names its grappler, the grappler's walk
drags it along at 1 extra foot a foot (Rules Glossary, Grappled: Movable),
and the grapple ends when the two end up farther apart than its range or
the grappler is Incapacitated (Grappling)."""

import pytest

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Combat.Arena.arena import GRAPPLER_KEY, MOVED_KEY, POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.CombatUIQt.arena_view import MoveKind
from Combat.Fight.effect_options import effect_options
from Combat.EncounterLogs import PLAYER_FIGHT_KEYS
from Combat.Effects.triggers import OpportunityAttack
from Combat.LogFiles import read_json
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.PlayerLog import is_round_key
from Model.Content.UnarmedStrikeEffects import GRAPPLE
from tests._combat_ui import make_ui


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    from PyQt6.QtWidgets import QMessageBox

    def refuse(*args, **kwargs):
        raise AssertionError(f"Unexpected question: {args[1:3]}")

    monkeypatch.setattr(QMessageBox, "question", refuse)


def _fight(tmp_path, monkeypatch):
    """Edmund (Speed 30 ft.) at F6 has just grappled the Large Tiger at
    G6-H7 with his Unarmed Strike, on his turn; the map in use."""
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    player[POSITION_KEY] = [5, 5]
    tiger[POSITION_KEY] = [6, 5]
    ui.arena_settings.in_use = True
    monkeypatch.setattr(
        type(ui), "_roll_effect_save", lambda self, *args, **kwargs: False
    )
    grapple = next(
        o for _, options in effect_options(player) for o in options if o.name == GRAPPLE
    )
    assert ui._apply_row(player, tiger, grapple)
    return ui, player, tiger


def _logged(ui, line: str) -> bool:
    data = read_json(ui.log_file)
    keys = sorted((k for k in data if is_round_key(k)), key=lambda k: int(k[6:]))
    return any(e["text"].endswith(line) for k in keys for e in data[k])


def _at(char) -> Cell:
    return Cell.of(char[POSITION_KEY])


def test_the_grapple_row_names_its_grappler(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    assert "Grappled" in tiger["conditions"]
    assert tiger[GRAPPLER_KEY] == "Edmund"
    sheet = player["_stat_block"]
    dc = 8 + sheet.get_strength_modifier() + sheet.get_proficiency_bonus()
    grapple = next(
        o for _, options in effect_options(player) for o in options if o.name == GRAPPLE
    )
    assert grapple.dc == dc and grapple.ability == "STR"
    assert f"Escape DC {dc}" in grapple.note
    assert "grappled_by" in PLAYER_FIGHT_KEYS, "kept with a player's fight"


def test_walking_drags_the_grappled_creature_at_double_cost(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    ui._move_combatant(player, Cell(3, 5))
    assert _at(player) == Cell(3, 5)
    assert player[MOVED_KEY] == 20, "10 ft. walked, each foot costing 2"
    assert _at(tiger) == Cell(4, 5), "kept beside Edmund"
    assert MOVED_KEY not in tiger, "not its own movement"
    assert _logged(ui, "Tiger is dragged from G6 to E6 (10 ft.; no movement spent).")
    assert "Edmund drags Tiger" in ui._status_label.text()
    assert "Grappled" in tiger["conditions"]
    assert not [p for p in ui._hit_prompts if isinstance(p, OpportunityAttack)]


def test_a_drag_is_undone_with_the_walk(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    ui._move_combatant(player, Cell(3, 5))
    ui._undo_last()
    assert _at(player) == Cell(5, 5)
    assert _at(tiger) == Cell(6, 5)


def test_a_teleport_away_ends_the_grapple(tmp_path, monkeypatch):
    """Misty Step doesn't drag: the two end up past the grapple's 5 ft."""
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    ui._move_combatant(player, Cell(1, 5), MoveKind.TELEPORT)
    assert _at(tiger) == Cell(6, 5)
    assert "Grappled" not in tiger["conditions"]
    assert GRAPPLER_KEY not in tiger
    line = "Edmund's grapple on Tiger ends: 25 ft. apart, past its 5 ft. range."
    assert _logged(ui, line)
    assert line in ui._status_label.text()


def test_pushing_the_grappled_creature_away_ends_the_grapple(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    ui._move_combatant(tiger, Cell(8, 5), MoveKind.PUSH)
    assert "Grappled" not in tiger["conditions"]


def test_the_grappler_incapacitated_ends_the_grapple(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    ui._add_condition_to(player, "Stunned")
    assert "Grappled" not in tiger["conditions"]
    assert GRAPPLER_KEY not in tiger


def test_released_by_hand_drags_nobody(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path, monkeypatch)
    ui._remove_condition_from(tiger, "Grappled")
    assert GRAPPLER_KEY not in tiger
    ui._move_combatant(player, Cell(3, 5))
    assert player[MOVED_KEY] == 10
    assert _at(tiger) == Cell(6, 5)
