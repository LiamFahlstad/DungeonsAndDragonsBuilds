"""Auras and Pack Tactics (Notes/combat-effects-plan.md, step 9.4): always-on
modifiers that depend on where creatures stand, counted from the battle
map's distances and noted for the GM where the map can't say.

Expected values are the rules text's:

- Aura of Protection (Paladin 6): "You radiate a protective, unseeable aura
  in a 10-foot Emanation that originates from you. The aura is inactive
  while you have the Incapacitated condition. You and your allies in the
  aura gain a bonus to saving throws equal to your Charisma modifier
  (minimum bonus of +1). If another Paladin is present, a creature can
  benefit from only one Aura of Protection at a time".
- Aura Expansion (Paladin 18): "Your Aura of Protection is now a 30-foot
  Emanation."
- Pack Tactics: "Advantage on an attack roll against a creature if at least
  one of the [creature]'s allies is within 5 feet of the creature and the
  ally doesn't have the Incapacitated condition."
"""

import pytest

from CharacterContent.Features.ClassFeatures.Paladin.PaladinFeatures import (
    AuraOfProtection,
)
from Combat.Arena.arena import POSITION_KEY
from Combat.Effects.modifiers import attack_plan
from Combat.Effects.roll_plans import save_plan
from Combat.Fight.auras import aura_modifiers, pack_tactics, with_auras
from Combat.Monsters.CR_0.monsters import Wolf
from Core.Definitions import CharacterClass
from tests._combat_ui import make_ui

NEUTRAL = "Neutral"


class _Sheet:
    """A Paladin's sheet, as much as the aura reads of it."""

    def __init__(self, level: int, charisma: int):
        self.level, self.charisma = level, charisma

    def get_class_level(self, character_class) -> int:
        return self.level if character_class is CharacterClass.PALADIN else 0

    def get_charisma_modifier(self) -> int:
        return self.charisma


def _paladin(name="Edmund", level=6, charisma=3, **keys) -> dict:
    return {
        "name": name,
        "hp": 40,
        "max_hp": 40,
        "conditions": [],
        "_is_player": True,
        "_stat_block": _Sheet(level, charisma),
        "_feature_objects": [AuraOfProtection()],
        **keys,
    }


def _player(name="Clover", **keys) -> dict:
    return {
        "name": name,
        "hp": 20,
        "max_hp": 20,
        "conditions": [],
        "_is_player": True,
        **keys,
    }


def _feet(table: dict):
    """A distance function from {(a name, b name): feet}; None for a pair
    not in it (off the map)."""

    def distance(a: dict, b: dict) -> int | None:
        return table.get((a["name"], b["name"]), table.get((b["name"], a["name"])))

    return distance


def _save_bonuses(char, chars, distance) -> tuple:
    reading = with_auras(char, aura_modifiers(char, chars, distance))
    return save_plan(reading, "WIS", NEUTRAL).bonuses


# ---------------------------------------------------------------------------
# Aura of Protection


def test_an_ally_within_10_feet_adds_the_paladins_charisma_modifier():
    edmund, clover = _paladin(), _player()
    bonuses = _save_bonuses(clover, [edmund, clover], _feet({("Edmund", "Clover"): 10}))
    assert bonuses == (("Edmund's Aura of Protection", "3"),)


def test_an_ally_farther_than_10_feet_gets_nothing():
    edmund, clover = _paladin(), _player()
    assert (
        _save_bonuses(clover, [edmund, clover], _feet({("Edmund", "Clover"): 15})) == ()
    )


def test_off_the_map_it_is_noted_not_counted():
    edmund, clover = _paladin(), _player()
    plan = save_plan(
        with_auras(clover, aura_modifiers(clover, [edmund, clover], _feet({}))),
        "WIS",
        NEUTRAL,
    )
    assert plan.bonuses == ()
    assert plan.notes == (
        "Edmund's Aura of Protection (not counted): 3 if it's within 10 feet of Edmund",
    )


def test_the_paladins_own_bonus_is_the_sheets():
    """apply() adds it to the Paladin's own saving throw bonuses already."""
    edmund = _paladin()
    assert aura_modifiers(edmund, [edmund], _feet({})) == []


def test_an_enemy_in_the_aura_gets_nothing():
    edmund = _paladin()
    ogre = {"name": "Ogre", "hp": 59, "max_hp": 59, "conditions": []}
    assert aura_modifiers(ogre, [edmund, ogre], _feet({("Edmund", "Ogre"): 5})) == []


@pytest.mark.parametrize(
    "changes",
    [{"conditions": ["Incapacitated"]}, {"conditions": ["Stunned"]}],
    ids=["incapacitated", "stunned (incapacitated)"],
)
def test_the_aura_is_inactive_while_the_paladin_is_incapacitated(changes):
    edmund, clover = _paladin(**changes), _player()
    near = _feet({("Edmund", "Clover"): 5})
    assert aura_modifiers(clover, [edmund, clover], near) == []


def test_a_dead_paladins_aura_gives_nothing():
    edmund = _paladin(hp=0, death_saves_fail=3)
    clover = _player()
    assert (
        aura_modifiers(clover, [edmund, clover], _feet({("Edmund", "Clover"): 5})) == []
    )


def test_of_two_paladins_only_the_better_aura_counts():
    edmund, gabriel, clover = _paladin(), _paladin("Gabriel", charisma=1), _player()
    near = _feet({("Edmund", "Clover"): 5, ("Gabriel", "Clover"): 5})
    assert _save_bonuses(clover, [gabriel, edmund, clover], near) == (
        ("Edmund's Aura of Protection", "3"),
    )


def test_aura_expansion_reaches_30_feet_and_the_bonus_is_at_least_1():
    edmund, clover = _paladin(level=18, charisma=-1), _player()
    bonuses = _save_bonuses(clover, [edmund, clover], _feet({("Edmund", "Clover"): 30}))
    assert bonuses == (("Edmund's Aura of Protection", "1"),)


# ---------------------------------------------------------------------------
# Pack Tactics


def _wolf(name: str, **keys) -> dict:
    return {
        "name": name,
        "hp": 11,
        "max_hp": 11,
        "conditions": [],
        "traits": [{"name": "Pack Tactics", "description": "..."}],
        **keys,
    }


def test_an_ally_within_5_feet_of_the_target_gives_advantage():
    wolf, other, clover = _wolf("Wolf"), _wolf("Wolf 2"), _player()
    near = _feet({("Wolf 2", "Clover"): 5})
    found = pack_tactics(wolf, clover, [wolf, other, clover], near)
    plan = attack_plan(wolf, clover, NEUTRAL, extra=found)
    assert plan.mode == "Advantage"
    assert plan.notes == ("Pack Tactics (Wolf 2 5 ft. from the target): Advantage",)


@pytest.mark.parametrize(
    "ally, table",
    [
        ({}, {("Wolf 2", "Clover"): 10}),
        ({"conditions": ["Incapacitated"]}, {("Wolf 2", "Clover"): 5}),
        ({"hp": 0}, {("Wolf 2", "Clover"): 5}),
    ],
    ids=["10 feet away", "incapacitated", "dead"],
)
def test_no_active_ally_within_5_feet_gives_nothing(ally, table):
    wolf, other, clover = _wolf("Wolf"), _wolf("Wolf 2", **ally), _player()
    assert pack_tactics(wolf, clover, [wolf, other, clover], _feet(table)) == []


def test_an_ally_off_the_map_is_noted_for_the_gm():
    wolf, other, clover = _wolf("Wolf"), _wolf("Wolf 2"), _player()
    found = pack_tactics(wolf, clover, [wolf, other, clover], _feet({}))
    plan = attack_plan(wolf, clover, NEUTRAL, extra=found)
    assert plan.mode == NEUTRAL
    assert plan.notes == (
        "Pack Tactics (not counted): Advantage if an ally of it without the"
        " Incapacitated condition is within 5 feet of the target",
    )


def test_without_the_trait_or_allies_nothing():
    plain = {"name": "Ogre", "hp": 59, "max_hp": 59, "conditions": []}
    wolf, clover = _wolf("Wolf"), _player()
    assert pack_tactics(plain, clover, [plain, clover], _feet({})) == []
    assert pack_tactics(wolf, clover, [wolf, clover], _feet({})) == []


# ---------------------------------------------------------------------------
# In the window, on the battle map


def test_the_fight_counts_pack_tactics_from_the_map(tmp_path):
    ui = make_ui(tmp_path, [Wolf(), Wolf()])
    first, second = ui.characters
    ui.arena_settings.in_use = True
    target = {
        "name": "Clover",
        "hp": 20,
        "max_hp": 20,
        "conditions": [],
        "_is_player": True,
    }
    ui.characters.append(target)
    first[POSITION_KEY], target[POSITION_KEY] = [0, 0], [1, 0]
    second[POSITION_KEY] = [2, 0]  # beside Clover
    reach = ui.fight.range_check(first, target, None)
    assert (
        attack_plan(first, target, NEUTRAL, extra=reach.modifiers).mode == "Advantage"
    )
    second[POSITION_KEY] = [5, 0]  # 15 ft. off
    reach = ui.fight.range_check(first, target, None)
    assert attack_plan(first, target, NEUTRAL, extra=reach.modifiers).mode == NEUTRAL


def test_the_fight_gives_an_allys_save_the_aura_from_the_map(tmp_path):
    ui = make_ui(tmp_path, [])
    edmund, clover = _paladin(), _player()
    ui.characters.extend([edmund, clover])
    ui.arena_settings.in_use = True
    edmund[POSITION_KEY], clover[POSITION_KEY] = [0, 0], [2, 0]  # 10 ft.
    assert save_plan(ui.fight.with_auras(clover), "WIS", NEUTRAL).bonuses == (
        ("Edmund's Aura of Protection", "3"),
    )
    assert save_plan(ui.fight.covered(None, clover), "WIS", NEUTRAL).bonuses == (
        ("Edmund's Aura of Protection", "3"),
    )
    clover[POSITION_KEY] = [3, 0]  # 15 ft.
    assert save_plan(ui.fight.with_auras(clover), "WIS", NEUTRAL).bonuses == ()
