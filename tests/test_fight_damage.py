"""Damage on a combatant without the combat window (Combat/Fight/damage.py,
Notes/combat-ui-refactor-plan.md step 5.3).

Expected values are the 2024 rules' (Rules Glossary, Damage and Healing):
Resistance halves damage (rounded down) and Vulnerability doubles it,
Resistance first; Immunity means none; Temporary Hit Points are lost first;
Hit Points don't go below 0."""

from Combat.Fight.damage import (
    damage_after_defenses,
    damage_type_modifier,
    take_damage,
)


def _creature(**keys) -> dict:
    return {"name": "Ogre", "hp": 30, "temp_hp": 0, "conditions": [], **keys}


def _defense(*types: str) -> list[dict]:
    return [{"damage_types": list(types)}]


def test_resistance_halves_rounding_down():
    ogre = _creature(damage_resistances=_defense("Fire"))
    assert damage_type_modifier(ogre, 13, "Fire") == (6, "resisted")
    assert damage_type_modifier(ogre, 13, "Cold") == (13, None)


def test_vulnerability_doubles_after_resistance():
    ogre = _creature(damage_vulnerabilities=_defense("Fire"))
    assert damage_type_modifier(ogre, 7, "Fire") == (14, "vulnerable")
    both = _creature(
        damage_resistances=_defense("Fire"), damage_vulnerabilities=_defense("Fire")
    )
    # 7 halved is 3, doubled is 6: not 7.
    assert damage_type_modifier(both, 7, "Fire") == (6, "resisted and vulnerable")


def test_immunity_means_no_damage():
    ogre = _creature(damage_immunities=_defense("Poison"))
    assert damage_type_modifier(ogre, 20, "Poison") == (0, "immune")


def test_a_save_halves_before_the_defenses():
    ogre = _creature(damage_resistances=_defense("Fire"))
    # 15 halved for the save is 7, halved for the Resistance is 3.
    assert damage_after_defenses(ogre, 15, "Fire", True, saved=True) == 3
    assert damage_after_defenses(ogre, 15, "Fire", False, saved=True) == 7


def test_temporary_hit_points_go_first():
    ogre = _creature(temp_hp=5)
    taken = take_damage(ogre, 8, "Slashing", None)
    assert (ogre["temp_hp"], ogre["hp"]) == (0, 27)
    assert (taken.temp_delta, taken.hp_delta, taken.knockout) == (-5, -3, False)


def test_hit_points_stop_at_zero_and_count_a_knockout():
    ogre, fighter = _creature(hp=6), _creature(name="Fighter")
    taken = take_damage(ogre, 20, "Slashing", fighter)
    assert ogre["hp"] == 0 and taken.knockout and taken.hp_delta == -6
    assert ogre["stats"]["times_downed"] == 1
    assert fighter["stats"]["knockouts"] == 1
    assert fighter["stats"]["damage_dealt"] == 20 == ogre["stats"]["damage_taken"]


def test_a_floor_holds_hit_points_up():
    # Relentless Endurance: 1 Hit Point instead of 0, not a knockout.
    orc = _creature(hp=4)
    taken = take_damage(orc, 10, "Bludgeoning", None, floor=1)
    assert orc["hp"] == 1 and not taken.knockout


def test_damage_to_someone_already_down_is_no_new_knockout():
    down = _creature(hp=0)
    assert not take_damage(down, 5, "Fire", None).knockout
