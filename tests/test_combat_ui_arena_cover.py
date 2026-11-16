"""Cover from the battle map in the combat window (Notes/combat-arena-plan.md,
step 19). Rules Glossary, Cover: Half Cover "+2 bonus to AC and Dexterity
saving throws", Total Cover "can't be targeted directly". It counts in
every attack path (the Use / Cast dialog, a monster's button, the Attack
roll field) and in the dialog's saves, once the map is in use (Decision 29);
Total Cover is warned about, not refused (as a range is, Decision 19)."""

import random

import pytest

from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.Arena.terrain import HALF, TOTAL, WALL, MapObject, Spot
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.monster_actions import DamageRoll, MonsterAction
from Combat.CombatUIQt.saves import CustomEffect, save_modifier
from Core.Definitions import DamageType
from tests._combat_ui import make_ui

FIRE = DamageType.FIRE.value
BARREL = Spot(thing=MapObject("Barrel", blocks=True, cover=HALF))
DOOR = Spot(thing=MapObject("Door", blocks=True, cover=TOTAL))
BETWEEN = Cell(2, 0)  # between the Pirate at A1 and the Tiger at E1
# A +0 attack: an 11 hits AC 10, and misses it with Half Cover's +2.
PUNCH = {"damage": [(5, FIRE)], "attack_bonus": 0}
BITE = MonsterAction(
    "Bite", "A bite.", to_hit=5, damage=(DamageRoll("1d6", "Piercing"),)
)


@pytest.fixture
def fight(tmp_path):
    """The Pirate (the source, whose turn it is) at A1, the Tiger at E1, AC
    10, on a map in use."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    pirate[POSITION_KEY] = [0, 0]
    tiger[POSITION_KEY] = [4, 0]
    tiger["ac"] = 10
    ui.arena_settings.in_use = True
    return ui, pirate, tiger


def _paint(ui, cell: Cell, spot: Spot):
    ui.arena_settings.terrain.put(cell, spot)


def _d20s(monkeypatch, *rolls: int):
    results = iter(rolls)
    monkeypatch.setattr(random, "randint", lambda low, high: next(results, 3))


def _log(ui) -> str:
    return str(ui._read_log())


def test_a_barrel_between_raises_the_ac_of_a_dialog_attack(fight, monkeypatch):
    ui, _, tiger = fight
    _paint(ui, BETWEEN, BARREL)
    _d20s(monkeypatch, 11, 11)
    ui._apply_custom_effect(CustomEffect(**PUNCH))
    assert tiger["hp"] == tiger["max_hp"]
    assert "Pirate's attack roll of 11 misses Tiger" in _log(ui)


def test_the_same_roll_hits_with_nothing_between(fight, monkeypatch):
    ui, _, tiger = fight
    _d20s(monkeypatch, 11, 11)
    ui._apply_custom_effect(CustomEffect(**PUNCH))
    assert tiger["hp"] == tiger["max_hp"] - 5


def test_before_the_map_is_in_use_the_barrel_counts_nothing(fight, monkeypatch):
    """Decision 29: the tokens may only be where the fight started them."""
    ui, _, tiger = fight
    ui.arena_settings.in_use = False
    _paint(ui, BETWEEN, BARREL)
    _d20s(monkeypatch, 11, 11)
    ui._apply_custom_effect(CustomEffect(**PUNCH))
    assert tiger["hp"] == tiger["max_hp"] - 5
    assert "Barrel" not in ui.target_label.text()


def test_a_creature_between_gives_half_cover(fight, monkeypatch):
    ui, pirate, tiger = fight
    ui.characters.append(
        {"name": "Goblin", "size": "Small", "hp": 7, POSITION_KEY: [2, 0]}
    )
    _d20s(monkeypatch, 11, 11)
    ui._apply_custom_effect(CustomEffect(**PUNCH))
    assert tiger["hp"] == tiger["max_hp"]


def test_the_target_label_names_the_cover(fight):
    ui, _, _ = fight
    _paint(ui, BETWEEN, BARREL)
    ui._update_target_label()
    assert (
        ui.target_label.text() == "Target: Tiger (20 ft., Half Cover from Barrel at C1)"
    )


def test_total_cover_is_warned_about_on_the_label_and_the_roll(fight, monkeypatch):
    ui, _, tiger = fight
    _paint(ui, BETWEEN, DOOR)
    ui._update_target_label()
    assert "Total Cover from Door at C1: can't be targeted" in ui.target_label.text()
    ui.attack_roll_input.setText("15")
    ui.attack_roll_input.returnPressed.emit()
    status = ui._status_label.text()
    assert "Tiger is behind Total Cover (Door at C1)" in status
    assert "vs AC 10" in status  # no bonus: it's the GM's to allow


def test_the_attack_roll_field_counts_the_maps_cover(fight):
    ui, _, _ = fight
    _paint(ui, BETWEEN, BARREL)
    ui.attack_roll_input.setText("11")
    ui.attack_roll_input.returnPressed.emit()
    assert ui._status_label.text() == "Tiger: 11 vs AC 12 with cover, miss"


def test_a_monsters_button_counts_the_maps_cover(fight, monkeypatch):
    ui, pirate, _ = fight
    _paint(ui, BETWEEN, BARREL)
    _d20s(monkeypatch, 6, 6)  # 11 with its +5: AC 12 with the barrel
    ui._roll_action(BITE, pirate)
    text = ui._action_result_label.text()
    assert "vs AC 12" in text
    assert "MISS" in text


def test_a_dexterity_save_gets_the_cover_bonus(fight, monkeypatch):
    ui, _, tiger = fight
    _paint(ui, BETWEEN, BARREL)
    dc = save_modifier(tiger, "DEX") + 11  # a 10 fails it, +2 makes it
    _d20s(monkeypatch, 10, 10)
    ui._apply_custom_effect(
        CustomEffect(damage=[(8, FIRE)], ability="DEX", dc=dc, half_on_save=True)
    )
    assert "Tiger makes a DC" in _log(ui)
    assert "Half Cover: +2" in _log(ui)


def test_an_areas_save_counts_cover_from_its_point_of_origin(fight, monkeypatch):
    """A Fireball bursting at E5, below the Tiger: the barrel between the
    Pirate and the Tiger isn't between the burst and the Tiger, the one at
    E3 is."""
    ui, _, tiger = fight
    _paint(ui, BETWEEN, BARREL)
    dc = save_modifier(tiger, "DEX") + 11
    burst = [Cell(4, 4)]
    _d20s(monkeypatch, 10, 10)
    ui._apply_custom_effect(
        CustomEffect(damage=[(8, FIRE)], ability="DEX", dc=dc, cover_origin=burst)
    )
    assert "Tiger fails a DC" in _log(ui)
    _paint(ui, Cell(4, 2), BARREL)
    _d20s(monkeypatch, 10, 10)
    ui._apply_custom_effect(
        CustomEffect(damage=[(8, FIRE)], ability="DEX", dc=dc, cover_origin=burst)
    )
    assert "Tiger makes a DC" in _log(ui)


def test_what_ignores_cover_leaves_only_total_cover(fight):
    ui, pirate, tiger = fight
    _paint(ui, BETWEEN, BARREL)
    assert ui._covered(pirate, tiger, ignores_cover=True) is tiger
    assert "Half Cover" in ui._covered(pirate, tiger)["visibility_states"]
    assert "Half Cover" not in tiger.get("visibility_states", [])


def test_a_wall_keeps_a_fireball_off_whoever_is_behind_it(fight):
    """Areas aimed on the map stop at Total Cover (Rules Glossary, Area of
    Effect), so the Tiger behind a wall isn't among its targets."""
    from Combat.Arena.areas import AreaOfEffect, AreaShape, area_cells, creatures_in

    ui, pirate, tiger = fight
    fireball = AreaOfEffect(AreaShape.SPHERE, 20)
    cells = area_cells(fireball, pirate, Cell(2, 0), ui.arena_settings)
    assert tiger in creatures_in(ui.characters, cells, ui.arena_settings)
    _paint(ui, Cell(3, 0), Spot(ground=WALL))
    _paint(ui, Cell(3, 1), Spot(ground=WALL))
    cells = area_cells(fireball, pirate, Cell(2, 0), ui.arena_settings)
    assert tiger not in creatures_in(ui.characters, cells, ui.arena_settings)
