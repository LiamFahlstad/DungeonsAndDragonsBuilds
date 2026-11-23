"""Gaining and losing a condition without the combat window
(Combat/Fight/conditions.py, Notes/combat-ui-refactor-plan.md step 5.3).

A condition doesn't stack with itself (Rules Glossary, Conditions: "a
condition doesn't get more severe if you have it more than once"), so
gaining one you have changes nothing; Grappled names its grappler."""

from Combat.Arena.arena import GRAPPLER_KEY
from Combat.Effects.active_effects import effect_for, find_effect
from Combat.Fight.conditions import gain_condition, lose_condition


def _creature(name: str, *conditions: str) -> dict:
    return {"name": name, "hp": 10, "max_hp": 10, "conditions": list(conditions)}


def test_a_condition_is_gained_once_and_counted():
    ogre, wizard = _creature("Ogre"), _creature("Wizard")
    assert gain_condition(ogre, "Restrained", wizard)
    assert not gain_condition(ogre, "Restrained", wizard)
    assert ogre["conditions"] == ["Restrained"]
    assert ogre["stats"]["conditions_received"] == 1
    assert wizard["stats"]["conditions_given"] == 1
    assert ogre["stats"]["conditions_received_by_name"] == {"Restrained": 1}


def test_a_badge_beside_its_conditions_isnt_counted():
    ogre = _creature("Ogre")
    assert gain_condition(ogre, "Friends", None, counted=False)
    assert ogre["stats"].get("conditions_received", 0) == 0


def test_grappled_names_its_grappler_and_loses_it_with_the_condition():
    goblin, fighter = _creature("Goblin"), _creature("Fighter")
    gain_condition(goblin, "Grappled", fighter)
    assert goblin[GRAPPLER_KEY] == "Fighter"
    lost = lose_condition(goblin, "Grappled")
    assert lost is not None and GRAPPLER_KEY not in goblin
    assert goblin["conditions"] == []


def test_losing_a_condition_ends_its_lasting_effect():
    ogre = _creature("Ogre", "Hexed")
    effect_for(ogre, "Hexed")["tooltip"] = "Hex: 1d6 Necrotic"
    lose_condition(ogre, "Hexed")
    assert find_effect(ogre, "Hexed") is None


def test_losing_one_it_doesnt_have_does_nothing():
    assert lose_condition(_creature("Ogre", "Prone"), "Stunned") is None


def test_the_hit_point_maximum_before_is_kept_for_the_follow_up():
    ogre = _creature("Ogre", "Prone")
    lost = lose_condition(ogre, "Prone")
    assert lost is not None and lost.maximum_before == 10
