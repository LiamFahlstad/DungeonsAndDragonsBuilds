"""Distances in triggers, counted from the battle map (Notes/combat-arena-plan.md,
step 27; DI-085), with no Qt: a `when` that asks how far the other creature
is (Fire Shield's "it's within 5 feet of you", Hellish Rebuke's "you can see
it within 60 feet") is settled by the distance when it's known, and Dark
One's Blessing also answers a knockout someone else makes within 10 feet of
its owner (combat-effects plan Q63)."""

import pytest

from Combat.CombatUIQt.effect_options import badge_trigger_row
from Combat.Effects.active_effects import give_modifiers
from Combat.Effects.triggers import (
    AttackOutcome,
    DamageOutcome,
    KnockoutOutcome,
    TriggerMode,
    TriggerRow,
    badge_hit_firings,
    outcome_firings,
    settle_when,
)
from Model.Content.CombatModifiers import AttackKind, WhenHit
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent


@pytest.mark.parametrize(
    "when, feet, settled",
    [
        ("it's within 5 feet of you", 5, (True, "")),
        ("it's within 5 feet of you", 10, (False, "")),
        ("it is within 60 feet", 60, (True, "")),
        ("you can see it within 60 feet", 25, (True, "you can see it")),
        ("you can see it within 30 feet of you", 35, (False, "")),
        # No distance known, or none in the `when`: the GM's.
        ("it's within 5 feet of you", None, (None, "it's within 5 feet of you")),
        (
            "the target is a Fiend or an Undead",
            5,
            (None, "the target is a Fiend or an Undead"),
        ),
    ],
)
def test_settle_when(when, feet, settled):
    assert settle_when(when, feet) == settled


def _creature(name: str, party: bool = False) -> dict:
    char = {"name": name, "hp": 30, "max_hp": 30, "conditions": []}
    if party:
        char["_is_player"] = True
    return char


def _distance(feet):
    return lambda a, b: feet


# ---------------------------------------------------------------------------
# Fire Shield (a badge's WhenHit)


@pytest.fixture
def fire_shield():
    wizard, ogre = _creature("Wizard", party=True), _creature("Ogre")
    warm = WhenHit("Fire Shield: warm flames", when="it's within 5 feet of you")
    wizard["conditions"].append("Fire Shield")
    give_modifiers(wizard, "Fire Shield", (warm,))
    record = next(e for e in wizard["active_effects"] if e["name"] == "Fire Shield")
    record["source"], record["caster"] = "Fire Shield", "Wizard"
    return wizard, ogre


def _shield_firings(wizard, ogre, feet):
    return badge_hit_firings(
        AttackOutcome(ogre, wizard, True, kind=AttackKind.MELEE),
        lambda bearer, record, modifier: badge_trigger_row(
            bearer, record.get("source"), modifier
        ),
        distance_of=_distance(feet),
    )


def test_fire_shield_answers_a_hit_from_5_feet_by_itself(fire_shield):
    (firing,) = _shield_firings(fire_shield[0], fire_shield[1], 5)
    assert firing.mode is TriggerMode.AUTO and firing.why == ""


def test_fire_shield_doesnt_answer_a_reach_weapon_from_10_feet(fire_shield):
    assert _shield_firings(fire_shield[0], fire_shield[1], 10) == []


def test_fire_shield_still_asks_off_the_map(fire_shield):
    (firing,) = _shield_firings(fire_shield[0], fire_shield[1], None)
    assert firing.mode is TriggerMode.ASK
    assert firing.why == "if it's within 5 feet of you"


# ---------------------------------------------------------------------------
# A row's trigger (Hellish Rebuke)

REBUKE = TriggerRow(
    name="Hellish Rebuke",
    trigger=CombatTrigger(
        TriggerEvent.TAKES_DAMAGE, reaction=True, when="you can see it within 60 feet"
    ),
)


def _rebukes(feet):
    warlock, ogre = _creature("Warlock", party=True), _creature("Ogre")
    found, _ = outcome_firings(
        [DamageOutcome(ogre, warlock, 7)],
        lambda char: [REBUKE] if char is warlock else [],
        distance_of=_distance(feet),
    )
    return found


def test_hellish_rebuke_asks_only_whether_it_can_see_the_attacker():
    (firing,) = _rebukes(25)
    assert firing.mode is TriggerMode.ASK
    assert firing.why == "if you can see it (25 ft. away)"


def test_hellish_rebuke_is_not_offered_past_60_feet():
    assert _rebukes(65) == []


def test_off_the_map_it_asks_as_before():
    (firing,) = _rebukes(None)
    assert firing.why == "if you can see it within 60 feet"


# ---------------------------------------------------------------------------
# Dark One's Blessing for someone else's knockout (Q63)

BLESSING = TriggerRow(
    name="Dark One's Blessing",
    trigger=CombatTrigger(
        TriggerEvent.REDUCES_TO_ZERO,
        optional=False,
        enemy_only=True,
        others_within_ft=10,
    ),
)


def _blessings(feet, who_drops: str = "fighter"):
    warlock = _creature("Warlock", party=True)
    fighter = _creature("Fighter", party=True)
    goblin = _creature("Goblin")
    goblin["hp"] = 0
    source = warlock if who_drops == "warlock" else fighter
    found, _ = outcome_firings(
        [KnockoutOutcome(source, goblin)],
        lambda char: [BLESSING] if char is warlock else [],
        distance_of=_distance(feet),
        others=[warlock, fighter, goblin],
    )
    return found, warlock, goblin


def test_a_knockout_within_10_feet_of_the_warlock_blesses_it():
    (firing,), warlock, goblin = _blessings(10)
    assert firing.owner is warlock and firing.target is goblin
    assert firing.mode is TriggerMode.AUTO


def test_a_knockout_farther_off_gives_nothing():
    found, *_ = _blessings(15)
    assert found == []


def test_off_the_map_it_asks():
    (firing,), *_ = _blessings(None)
    assert firing.mode is TriggerMode.ASK
    assert firing.why == "if it was within 10 feet of you"


def test_the_warlocks_own_knockout_counts_whatever_the_distance():
    (firing,), warlock, _ = _blessings(40, who_drops="warlock")
    assert firing.owner is warlock and firing.mode is TriggerMode.AUTO


def test_others_within_ft_is_for_knockouts_only():
    with pytest.raises(ValueError):
        CombatTrigger(TriggerEvent.HIT, others_within_ft=10)
    with pytest.raises(ValueError):
        CombatTrigger(TriggerEvent.REDUCES_TO_ZERO, others_within_ft=0)
