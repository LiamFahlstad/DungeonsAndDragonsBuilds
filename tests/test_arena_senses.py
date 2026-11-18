"""Light and senses on the battle map, with no Qt (Notes/combat-arena-plan.md,
step 28; DI-068): who sees whom (Rules Glossary, Vision and Senses:
Darkness is Heavily Obscured, "You have the Blinded condition while trying
to see something in a Heavily Obscured space"; Darkvision, Blindsight,
Truesight; Invisible), and what that counts in an attack roll and a
trigger's "you can see it"."""

from typing import Any

import pytest

from Combat.Arena.arena import ArenaSettings
from Combat.Arena.geometry import Cell
from Combat.Arena.ranges import AttackRange, check_attack_range
from Combat.Arena.senses import (
    DARKNESS,
    DEEP_DARKNESS,
    FOG,
    area_obscures,
    sees,
    sense_ranges,
)
from Combat.Arena.terrain import DARK, WALL
from Combat.Effects.active_effects import give_modifiers
from Combat.Effects.modifiers import attack_plan, has_condition
from Combat.Effects.sight import UNKNOWN, Seen, Sight
from Combat.Effects.triggers import (
    DamageOutcome,
    TriggerMode,
    TriggerRow,
    outcome_firings,
)
from Core.Definitions import Condition, Sense
from Model.Content.CombatModifiers import AttacksAgainst, Modifier, RollMode, Vision
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from Model.Creatures.Combatants import Visibility


def _creature(name: str, at=None, **keys: Any) -> dict:
    char: dict = {"name": name, "size": "Medium", "hp": 20, "conditions": []}
    if at is not None:
        char["position"] = list(at)
    return {**char, **keys}


def _badge(char: dict, name: str, *modifiers: Modifier) -> dict:
    char["conditions"].append(name)
    give_modifiers(char, name, modifiers)
    return char


def _dark(*cells) -> ArenaSettings:
    settings = ArenaSettings()
    for cell in cells:
        settings.terrain.change(Cell.of(cell), light=DARK)
    return settings


def _area(caster: dict, name: str, text: str, *cells) -> dict:
    """A kept area of caster's on `cells` with rules text `text`."""
    record = {
        "shape": "Sphere",
        "size_ft": 15,
        "cells": [list(c) for c in cells],
        "follows": False,
        "about": text,
    }
    caster.setdefault("active_spells", []).append({"name": name, "area": record})
    return caster


def _sees(viewer, other, settings=None, *others) -> Seen:
    return sees(viewer, other, [viewer, other, *others], settings or ArenaSettings())


DARKNESS_TEXT = (
    "For the duration, magical Darkness spreads from a point within range and"
    " fills a 15-foot-radius Sphere. Darkvision can’t see through it, and"
    " nonmagical light can’t illuminate it."
)
FOG_TEXT = (
    "You create a 20-foot-radius Sphere of fog centered on a point within"
    " range. The Sphere is Heavily Obscured."
)


# ---------------------------------------------------------------------------
# Reading what a kept area is to sight, and a creature's senses


@pytest.mark.parametrize(
    "text, kind",
    [
        (DARKNESS_TEXT, DEEP_DARKNESS),
        (FOG_TEXT, FOG),
        ("A 20-foot-radius Sphere of Darkness appears", DARKNESS),  # Hunger of Hadar
        ("The fog is magical Darkness and lasts for the duration", DARKNESS),
        ("A silvery beam of pale light shines down in a 5-foot-radius", None),
    ],
)
def test_area_obscures(text, kind):
    assert area_obscures(text) == kind


class _Sheet:
    senses = {Sense.DARKVISION: 60}


def test_senses_from_a_stat_block_a_sheet_and_a_badge():
    monster = _creature(
        "Ghoul", senses="Blindsight 10 ft., Darkvision 60 ft., Passive Perception 10"
    )
    assert sense_ranges(monster) == {Sense.BLINDSIGHT: 10, Sense.DARKVISION: 60}
    player = _creature("Elf", _stat_block=_Sheet())
    assert sense_ranges(player) == {Sense.DARKVISION: 60}
    _badge(player, "Darkvision", Vision(darkvision_ft=150))  # the spell's
    assert sense_ranges(player) == {Sense.DARKVISION: 150}


def test_a_vision_needs_a_rule_and_feet_above_0():
    with pytest.raises(ValueError):
        Vision()
    with pytest.raises(ValueError):
        Vision(darkvision_ft=0)


# ---------------------------------------------------------------------------
# Who sees whom


def test_off_the_map_its_not_known():
    assert _sees(_creature("A"), _creature("B", (1, 0))) == UNKNOWN


def test_in_the_light_its_seen():
    assert _sees(_creature("A", (0, 0)), _creature("B", (3, 0))) == Seen(True)


def test_darkness_hides_from_eyes_but_not_from_darkvision_in_range():
    settings = _dark((3, 0))
    goblin = _creature("Goblin", (3, 0))
    seen = _sees(_creature("Human", (0, 0)), goblin, settings)
    assert seen == Seen(False, "Darkness at D1", obscured=True)
    elf = _creature("Elf", (0, 0), senses="Darkvision 60 ft.")
    assert _sees(elf, goblin, settings) == Seen(True, "Darkvision 60 ft.")
    short = _creature("Mole", (0, 0), senses="Darkvision 10 ft.")
    assert _sees(short, goblin, settings).can is False  # 15 ft. away


def test_a_creature_partly_in_the_light_is_seen():
    ogre = _creature("Ogre", (3, 0), size="Large")  # D1, E1, D2, E2
    assert _sees(_creature("A", (0, 0)), ogre, _dark((3, 0), (4, 0), (3, 1))).can


def test_the_viewer_in_darkness_still_sees_out():
    assert _sees(_creature("A", (0, 0)), _creature("B", (3, 0)), _dark((0, 0))).can


def test_the_darkness_spell_stops_darkvision_not_truesight():
    goblin = _creature("Goblin", (3, 0))
    caster = _area(_creature("Warlock"), "Darkness", DARKNESS_TEXT, (3, 0))
    elf = _creature("Elf", (0, 0), senses="Darkvision 60 ft.")
    seen = _sees(elf, goblin, None, caster)
    assert seen == Seen(False, "Warlock's Darkness", obscured=True)
    devil = _creature("Devil", (0, 0), senses="Truesight 30 ft.")
    assert _sees(devil, goblin, None, caster) == Seen(True, "Truesight 30 ft.")


def test_a_fog_hides_from_every_sight_but_blindsight():
    goblin = _creature("Goblin", (3, 0))
    caster = _area(_creature("Druid"), "Fog Cloud", FOG_TEXT, (3, 0))
    devil = _creature("Devil", (0, 0), senses="Truesight 120 ft.")
    assert _sees(devil, goblin, None, caster).can is False
    bat = _creature("Bat", (0, 0), senses="Blindsight 60 ft.")
    assert _sees(bat, goblin, None, caster) == Seen(True, "Blindsight 60 ft.")


def test_a_blinded_viewer_sees_only_by_blindsight_and_not_past_total_cover():
    goblin = _creature("Goblin", (1, 0))
    blinded = _creature("Fighter", (0, 0), conditions=["Blinded"])
    assert _sees(blinded, goblin) == Seen(False, "Fighter is Blinded")
    blinded["senses"] = "Blindsight 10 ft."
    assert _sees(blinded, goblin) == Seen(True, "Blindsight 10 ft.")
    settings = ArenaSettings()
    settings.terrain.change(Cell.of((1, 0)), ground=WALL)
    behind = _creature("Goblin", (2, 0))
    assert _sees(blinded, behind, settings).can is False


def test_blind_beyond_its_blindsight():
    ooze = _creature(
        "Ooze", (0, 0), senses="Blindsight 10 ft. (blind beyond this radius)"
    )
    assert _sees(ooze, _creature("A", (2, 0))).can is True
    far = _sees(ooze, _creature("B", (3, 0)))
    assert far == Seen(False, "blind beyond its Blindsight 10 ft.")


def test_the_invisible_visibility_state_is_the_invisible_condition():
    # DI-068: the GM's visibility combo gives the condition's rules.
    ghost = _creature("Ghost", (3, 0), visibility_states=[Visibility.INVISIBLE.value])
    assert has_condition(ghost, Condition.INVISIBLE)
    assert _sees(_creature("A", (0, 0)), ghost) == Seen(False, "Ghost is Invisible")


def test_invisible_is_seen_by_truesight_blindsight_and_see_invisibility():
    ghost = _creature("Ghost", (3, 0), conditions=["Invisible"])
    devil = _creature("Devil", (0, 0), senses="Truesight 30 ft.")
    assert _sees(devil, ghost) == Seen(True, "Truesight 30 ft.")
    bat = _creature("Bat", (0, 0), senses="Blindsight 60 ft.")
    assert _sees(bat, ghost).can
    wizard = _badge(
        _creature("Wizard", (0, 0)), "See Invisibility", Vision(sees_invisible=True)
    )
    assert _sees(wizard, ghost) == Seen(True, "See Invisibility")
    # Seeing Invisible creatures isn't seeing in the dark.
    assert _sees(wizard, ghost, _dark((3, 0))).can is False


def test_faerie_fire_takes_the_invisible_conditions_benefit_away():
    ghost = _badge(
        _creature("Ghost", (3, 0), conditions=["Invisible"]),
        "Faerie Fire",
        Vision(outlined=True),
    )
    assert _sees(_creature("A", (0, 0)), ghost) == Seen(True)


# ---------------------------------------------------------------------------
# What it counts in an attack roll


UNSEEN = Seen(False, "Ghost is Invisible")
SEEN = Seen(True)


def test_without_the_map_invisible_is_only_noted():
    ghost = _creature("Ghost", conditions=["Invisible"])
    plan = attack_plan(_creature("Fighter"), ghost, "Neutral")
    assert plan.mode == "Neutral"
    assert any("(not counted)" in note for note in plan.notes)


def test_an_unseen_invisible_target_gives_disadvantage():
    ghost = _creature("Ghost", conditions=["Invisible"])
    plan = attack_plan(
        _creature("Fighter"), ghost, "Neutral", sight=Sight(UNSEEN, SEEN)
    )
    assert plan.mode == "Disadvantage"
    assert plan.notes == (
        "Ghost is Invisible, the attacker doesn't see it (Ghost is Invisible):"
        " Disadvantage",
    )


def test_an_invisible_attacker_seen_by_truesight_gets_no_advantage():
    ghost = _creature("Ghost", conditions=["Invisible"])
    sight = Sight(SEEN, Seen(True, "Truesight 60 ft."))
    plan = attack_plan(ghost, _creature("Devil"), "Neutral", sight=sight)
    assert plan.mode == "Neutral"
    assert plan.notes == (
        "Ghost is Invisible: no Advantage, the target sees it (Truesight 60 ft.)",
    )


def test_an_unseen_invisible_attacker_has_advantage():
    ghost = _creature("Ghost", conditions=["Invisible"])
    sight = Sight(SEEN, Seen(False, "Ghost is Invisible"))
    assert attack_plan(ghost, _creature("Fighter"), "Neutral", sight=sight).mode == (
        "Advantage"
    )


def test_a_target_in_darkness_is_blindeds_disadvantage_for_the_attacker():
    sight = Sight(Seen(False, "Darkness at D1", obscured=True), SEEN)
    plan = attack_plan(
        _creature("Fighter"), _creature("Goblin"), "Neutral", sight=sight
    )
    assert plan.mode == "Disadvantage"
    assert plan.notes == ("Fighter can't see Goblin (Darkness at D1): Disadvantage",)


def test_an_attacker_in_darkness_has_advantage_on_a_target_that_cant_see_it():
    sight = Sight(SEEN, Seen(False, "Darkness at A1", obscured=True))
    plan = attack_plan(
        _creature("Goblin"), _creature("Fighter"), "Neutral", sight=sight
    )
    assert plan.mode == "Advantage"


def test_both_unseen_in_darkness_cancel_out():
    dark = Seen(False, "Darkness", obscured=True)
    plan = attack_plan(
        _creature("A"), _creature("B"), "Neutral", sight=Sight(dark, dark)
    )
    assert plan.mode == "Neutral"


def test_a_blinded_attacker_isnt_counted_twice():
    dark = Seen(False, "Fighter is Blinded")
    blinded = _creature("Fighter", conditions=["Blinded"])
    plan = attack_plan(blinded, _creature("Goblin"), "Neutral", sight=Sight(dark, SEEN))
    assert plan.notes == ("Fighter is Blinded: Disadvantage",)


def test_faerie_fires_advantage_counts_when_the_attacker_sees_it():
    lit = _badge(
        _creature("Ghost", conditions=["Invisible"]),
        "Faerie Fire",
        Vision(outlined=True),
        AttacksAgainst(RollMode.ADVANTAGE, when="the attacker can see it"),
    )
    plan = attack_plan(_creature("Fighter"), lit, "Neutral", sight=Sight(SEEN, SEEN))
    assert plan.mode == "Advantage"
    unseen = Sight(Seen(False, "Darkness", obscured=True), SEEN)
    assert attack_plan(_creature("Fighter"), lit, "Neutral", sight=unseen).mode == (
        "Disadvantage"
    )


def test_dodge_counts_only_against_an_attacker_its_bearer_sees():
    dodging = _badge(
        _creature("Fighter"),
        "Dodge",
        AttacksAgainst(RollMode.DISADVANTAGE, seen_attacker=True),
    )
    ghost = _creature("Ghost", conditions=["Invisible"])
    sight = Sight(SEEN, Seen(False, "Ghost is Invisible"))
    plan = attack_plan(ghost, dodging, "Neutral", sight=sight)
    assert plan.mode == "Advantage"  # Invisible's, and no Dodge
    assert "Fighter's Dodge: no Disadvantage" in " ".join(plan.notes)


# ---------------------------------------------------------------------------
# The map's checks: close combat, the attack's sight


def test_an_enemy_close_by_that_cant_see_the_archer_imposes_nothing():
    archer = _creature("Archer", (0, 0), _is_player=True)
    archer["visibility_states"] = [Visibility.INVISIBLE.value]
    goblin, orc = _creature("Goblin", (6, 0)), _creature("Orc", (0, 1))
    bow = AttackRange(normal_ft=150, long_ft=600, what="Longbow")
    check = check_attack_range(
        bow, archer, goblin, [archer, goblin, orc], ArenaSettings()
    )
    assert check.disadvantages == ()
    assert check.notes == (
        "Ranged attack within 5 ft. of Orc: no Disadvantage, it doesn't see the"
        " attacker (Archer is Invisible)",
    )
    assert check.sight.attacker == SEEN
    assert check.sight.target == Seen(False, "Archer is Invisible")


# ---------------------------------------------------------------------------
# A trigger's "you can see it" (Hellish Rebuke)

REBUKE = TriggerRow(
    name="Hellish Rebuke",
    trigger=CombatTrigger(
        TriggerEvent.TAKES_DAMAGE, reaction=True, when="you can see it within 60 feet"
    ),
)


def _rebukes(seen):
    warlock = _creature("Warlock", _is_player=True)
    ogre = _creature("Ogre")
    found, _ = outcome_firings(
        [DamageOutcome(ogre, warlock, 7)],
        lambda char: [REBUKE] if char is warlock else [],
        distance_of=lambda a, b: 25,
        sees_of=lambda a, b: seen,
    )
    return found


def test_hellish_rebuke_against_an_attacker_it_sees_asks_nothing_more():
    (firing,) = _rebukes(True)
    assert firing.why == ""
    assert firing.mode is TriggerMode.ASK  # a Reaction and a spell slot


def test_hellish_rebuke_isnt_offered_against_one_it_cant_see():
    assert _rebukes(False) == []


def test_hellish_rebuke_asks_when_sight_isnt_known():
    (firing,) = _rebukes(None)
    assert firing.why == "if you can see it (25 ft. away)"
