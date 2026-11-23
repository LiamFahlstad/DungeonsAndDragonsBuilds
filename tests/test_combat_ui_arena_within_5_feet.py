"""The rules that ask "within 5 feet", counted from the battle map
(Notes/combat-arena-plan.md, step 16). Expected results come from the Rules
Glossary's conditions (SourceTexts/RulesGlossary/Conditions/):

- Prone: "An attack roll against you has Advantage if the attacker is
  within 5 feet of you. Otherwise, that attack roll has Disadvantage."
- Paralyzed and Unconscious: "Any attack roll that hits you is a Critical
  Hit if the attacker is within 5 feet of you."

With both creatures on the map the distance settles it; with either off it,
it stays a note for the GM, as before the map."""

import random

import pytest

from Combat.Arena.arena import IN_USE_KEY, POSITION_KEY, ArenaSettings, distance_ft
from Combat.Arena.geometry import Cell
from Combat.Arena.maps import ARENA_KEY, MapDesign
from Combat.Combatants import Pirate, Tiger
from Combat.Fight.monster_actions import DamageRoll, MonsterAction
from Combat.Fight.saves import CustomEffect
from Core.Definitions import DamageType
from tests._combat_ui import make_ui

FIRE = DamageType.FIRE.value
# A +0 attack against AC 10: a 17 hits, a 4 misses.
PUNCH = {"damage": [(5, FIRE)], "attack_bonus": 0}
# A +5 attack that hits AC 15 on a 10, with its damage doubled on a Critical Hit.
BOLT = {"damage": [(5, FIRE)], "critical_damage": [(10, FIRE)], "attack_bonus": 5}
NEXT_TO = [1, 0]  # the Tiger beside the Pirate at A1
FAR_OFF = [7, 0]  # 35 ft. away along the row


@pytest.fixture
def fight(tmp_path):
    """The Pirate (the source, whose turn it is) at A1, attacking the Tiger."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    pirate[POSITION_KEY] = [0, 0]
    # A fight played on the map (Decision 29); `unused` below is one that isn't.
    ui.arena_settings.in_use = True
    return ui, pirate, tiger


@pytest.fixture
def unused(tmp_path):
    """The same fight with nobody moved on the map yet: everyone where
    place_new put them as combat started."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    return ui, pirate, tiger


def _d20s(monkeypatch, *rolls: int):
    """random.randint gives these (an attack throws two d20s), then 3s for
    any damage dice."""
    results = iter(rolls)
    monkeypatch.setattr(random, "randint", lambda low, high: next(results, 3))


def _place(ui, tiger: dict, where: list[int] | None, feet: int | None):
    """The Tiger at `where` (None: off the map), `feet` from the Pirate."""
    if where is None:
        tiger.pop(POSITION_KEY, None)
    else:
        tiger[POSITION_KEY] = where
    assert distance_ft(ui.characters[0], tiger, ui.arena_settings) == feet


def _log(ui) -> str:
    return str(ui._read_log())


# ---------------------------------------------------------------------------
# Prone


def test_a_prone_target_beside_the_attacker_gives_advantage(fight, monkeypatch):
    ui, _, tiger = fight
    tiger["ac"] = 10
    tiger["conditions"].append("Prone")
    _place(ui, tiger, NEXT_TO, 5)
    _d20s(monkeypatch, 4, 17)  # Advantage keeps the 17
    ui._apply_custom_effect(CustomEffect(**PUNCH))
    assert tiger["hp"] == tiger["max_hp"] - 5
    assert "Tiger is Prone, attacker 5 ft. away: Advantage" in _log(ui)
    assert "not counted" not in _log(ui)


def test_a_prone_target_farther_than_5_feet_gives_disadvantage(fight, monkeypatch):
    ui, _, tiger = fight
    tiger["ac"] = 10
    tiger["conditions"].append("Prone")
    _place(ui, tiger, FAR_OFF, 35)
    _d20s(monkeypatch, 17, 4)  # Disadvantage keeps the 4
    ui._apply_custom_effect(CustomEffect(**PUNCH))
    assert tiger["hp"] == tiger["max_hp"]
    assert "Tiger is Prone, attacker 35 ft. away: Disadvantage" in _log(ui)


def test_a_prone_target_off_the_map_stays_a_note(fight, monkeypatch):
    ui, _, tiger = fight
    tiger["ac"] = 10
    tiger["conditions"].append("Prone")
    _place(ui, tiger, None, None)
    _d20s(monkeypatch, 17, 4)  # a straight roll keeps the first
    ui._apply_custom_effect(CustomEffect(**PUNCH))
    assert tiger["hp"] == tiger["max_hp"] - 5
    assert "Tiger is Prone (not counted): Advantage if the attacker" in _log(ui)


# ---------------------------------------------------------------------------
# Paralyzed and Unconscious


@pytest.mark.parametrize("condition", ["Paralyzed", "Unconscious"])
def test_a_hit_from_beside_is_a_critical_hit(fight, monkeypatch, condition):
    ui, _, tiger = fight
    tiger["ac"] = 15
    tiger["conditions"].append(condition)
    _place(ui, tiger, NEXT_TO, 5)
    _d20s(monkeypatch, 10, 10)  # 15: a hit, not a natural 20
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 10
    log = _log(ui)
    assert "Pirate's attack roll of 15 hits Tiger (critical hit)" in log
    assert f"Tiger is {condition}, attacker 5 ft. away: a Critical Hit" in log


@pytest.mark.parametrize("condition", ["Paralyzed", "Unconscious"])
def test_a_hit_from_farther_off_is_not(fight, monkeypatch, condition):
    ui, _, tiger = fight
    tiger["ac"] = 15
    tiger["conditions"].append(condition)
    _place(ui, tiger, FAR_OFF, 35)
    _d20s(monkeypatch, 10, 10)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 5
    log = _log(ui)
    assert "(critical hit)" not in log
    assert f"Tiger is {condition}, attacker 35 ft. away: not a Critical Hit" in log


def test_a_paralyzed_target_off_the_map_stays_a_note(fight, monkeypatch):
    ui, _, tiger = fight
    tiger["ac"] = 15
    tiger["conditions"].append("Paralyzed")
    _place(ui, tiger, None, None)
    _d20s(monkeypatch, 10, 10)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 5
    assert (
        "Tiger is Paralyzed: a Critical Hit if the attacker is within 5 feet"
        " of it (not counted)"
    ) in _log(ui)


def test_a_miss_is_no_critical_hit_however_close(fight, monkeypatch):
    """ "Any attack roll that hits you": a miss stays a miss."""
    ui, _, tiger = fight
    tiger["ac"] = 15
    tiger["conditions"].append("Paralyzed")
    _place(ui, tiger, NEXT_TO, 5)
    _d20s(monkeypatch, 2, 2)  # 7 misses, Advantage or not
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"]
    assert "(critical hit)" not in _log(ui)


# ---------------------------------------------------------------------------
# The other attack paths: a monster's button and the Attack roll field

BITE = MonsterAction(
    "Bite", "A bite.", to_hit=5, damage=(DamageRoll("1d6", "Piercing"),)
)


@pytest.mark.parametrize("where, feet, damage", [(NEXT_TO, 5, 6), (FAR_OFF, 35, 3)])
def test_a_monsters_bite_on_a_paralyzed_target(fight, monkeypatch, where, feet, damage):
    """The button rolls the damage dice, twice over for a Critical Hit."""
    ui, pirate, tiger = fight
    tiger["ac"] = 15
    tiger["conditions"].append("Paralyzed")
    _place(ui, tiger, where, feet)
    _d20s(monkeypatch, 10, 10)  # 15: a hit; then a 3 on each d6
    ui._roll_action(BITE, pirate)
    text = ui._action_result_label.text()
    assert ("CRITICAL HIT" in text) is (feet == 5)
    assert f"attacker {feet} ft. away" in text
    assert ui.damage_input.text() == f"{damage} Piercing"


def test_the_attack_roll_field_counts_it_too(fight):
    ui, _, tiger = fight
    tiger["ac"] = 15
    tiger["conditions"].append("Unconscious")
    _place(ui, tiger, NEXT_TO, 5)
    ui.attack_roll_input.setText("16")
    ui._apply_attack_roll()
    assert "Pirate's attack roll of 16 hits Tiger (critical hit)" in _log(ui)
    assert "Tiger is Unconscious, attacker 5 ft. away: a Critical Hit" in _log(ui)


# ---------------------------------------------------------------------------
# Only once the map is in use (Decision 29): a fight played on the cards
# alone has only place_new's starting edges, which say nothing about where
# anyone really is.


def test_before_the_map_is_used_a_prone_target_stays_a_note(unused, monkeypatch):
    ui, pirate, tiger = unused
    assert not ui.arena_settings.in_use
    assert distance_ft(pirate, tiger, ui.arena_settings) is not None
    tiger["ac"] = 10
    tiger["conditions"].append("Prone")
    _d20s(monkeypatch, 17, 4)  # a straight roll keeps the first
    ui._apply_custom_effect(CustomEffect(**PUNCH))
    assert tiger["hp"] == tiger["max_hp"] - 5
    assert "Tiger is Prone (not counted): Advantage if the attacker" in _log(ui)


def test_before_the_map_is_used_a_paralyzed_target_stays_a_note(unused):
    ui, pirate, tiger = unused
    tiger["conditions"].append("Paralyzed")
    assert not ui._critical_against(pirate, tiger)
    assert ui._attacker_distance_ft(pirate, tiger) is None


def test_moving_a_token_puts_the_map_in_use_and_undo_takes_it_back(unused):
    ui, pirate, tiger = unused
    tiger["conditions"].append("Paralyzed")
    pirate[POSITION_KEY], tiger[POSITION_KEY] = [5, 5], [10, 5]
    ui._move_combatant(tiger, Cell(6, 5))  # beside the Pirate
    assert ui.arena_settings.in_use
    assert ui._attacker_distance_ft(pirate, tiger) == 5
    assert ui._critical_against(pirate, tiger)
    ui._undo_last()
    assert not ui.arena_settings.in_use
    assert ui._attacker_distance_ft(pirate, tiger) is None


def test_a_painted_maps_starts_put_it_in_use(unused, monkeypatch):
    ui, pirate, tiger = unused
    ui.arena_settings.in_use = False
    for char in ui.characters:
        char.pop(POSITION_KEY, None)
    design = MapDesign(starts={pirate["name"]: Cell(0, 0), tiger["name"]: Cell(1, 0)})
    monkeypatch.setattr(ui, "_encounter_map", lambda _encounter: design)
    ui._place_on_arena()
    assert ui.arena_settings.in_use
    assert ui._attacker_distance_ft(pirate, tiger) == 5


def test_in_use_is_kept_with_the_fight_but_not_in_a_map_file():
    settings = ArenaSettings()
    assert IN_USE_KEY not in settings.to_dict()  # older logs stay as they were
    settings.in_use = True
    assert ArenaSettings.from_dict(settings.to_dict()).in_use
    assert IN_USE_KEY not in MapDesign(settings).to_dict()[ARENA_KEY]
