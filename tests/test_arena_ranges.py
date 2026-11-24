"""Reach and range checked on the battle map, with no Qt
(Notes/combat-arena-plan.md, step 20). Expected results come from the rules:

- Rules Glossary, Reach: 5 feet, 10 with the Reach property.
- Player's Handbook, Range: "Disadvantage on an attack roll against a target
  beyond normal range, and you can't attack a target beyond the long range";
  the Weapons table's ranges (Longbow 150/600, Dagger Thrown 20/60).
- Player's Handbook, Ranged Attacks in Close Combat: Disadvantage "if you
  are within 5 feet of an enemy who can see you and who doesn't have the
  Incapacitated condition".

On 5-foot cells counted Manhattan; what can't be done is warned about, not
refused (Decision 31)."""

from dataclasses import replace
from typing import Any

import pytest

from CharacterContent.Items.Weapons.Magic import MarksmansLongbow
from CharacterContent.Items.Weapons.MartialMelee import Glaive, Longsword
from CharacterContent.Items.Weapons.Ranged import Longbow
from CharacterContent.Items.Weapons.SimpleMelee import Dagger
from Combat.Arena.arena import ArenaSettings
from Combat.Arena.ranges import (
    NO_RANGE_CHECK,
    AttackRange,
    check_attack_range,
    monster_action_range,
    spell_attack_range,
    spell_range_warning,
    weapon_range,
)
from Combat.Effects.modifiers import attack_plan
from Combat.Fight.monster_actions import parse_action
from Combat.Effects.sight import NO_SIGHT
from Combat.EncounterLogs import _plain
from Combat.Fight.monster_effect_text import read_effects, read_reach_and_range
from Core.Definitions import Ability
from Model.Content.CombatEffect import CombatEffect, EffectRoll
from Model.Content.CombatModifiers import AttackKind
from Model.Creatures.MonsterAbilities import (
    MeleeAttack,
    MeleeOrRangedAttack,
    MonsterAbility,
    RangedAttack,
)

BOW = AttackRange(normal_ft=150, long_ft=600, what="Longbow")
SWORD = AttackRange(reach_ft=5, what="Longsword")
THROWN = AttackRange(reach_ft=5, normal_ft=20, long_ft=60, what="Dagger")


def _monster(name: str, at, **keys: Any) -> dict:
    return {"name": name, "size": "Medium", "hp": 7, "position": list(at), **keys}


def _player(name: str, at, **keys: Any) -> dict:
    char = {"name": name, "_is_player": True, "size": "Medium", "hp": 20}
    return {**char, **keys, "position": list(at)}


def _check(attack, attacker, target, *others):
    """The range part of the check: its sight (who sees whom, step 28) is
    tests/test_arena_senses.py's."""
    check = check_attack_range(
        attack, attacker, target, [attacker, target, *others], ArenaSettings()
    )
    return replace(check, sight=NO_SIGHT)


# ---------------------------------------------------------------------------
# Reading the reach and range


def test_a_stat_blocks_attack_text_is_read_for_its_reach_or_range():
    """Where content is written (generate_monsters.py, an old log as it
    loads): the reach and range an attack states before its "Hit:"."""
    read = read_reach_and_range
    assert read("Melee Attack Roll: +6, reach 10 ft. Hit: 9 (1d10 + 4).") == (
        10,
        None,
        None,
    )
    assert read("Ranged Attack Roll: +4, range 80/320 ft. Hit: 5.") == (None, 80, 320)
    assert read("Ranged Weapon Attack: +7 to hit, range 150/600 ft.") == (
        None,
        150,
        600,
    )
    assert read("Melee or Ranged Attack Roll: +4, reach 5 ft. or range 20/60 ft.") == (
        5,
        20,
        60,
    )
    assert read("Melee Attack Roll: +5, reach 5 feet. Hit: 5.") == (5, None, None)
    # What its hit does isn't its reach.
    assert read(
        "Melee Attack Roll: +5, reach 5 ft. Hit: 5. It pulls the target up to"
        " 15 feet, within range 30 ft. of it."
    ) == (5, None, None)
    assert read("The dragon exhales fire in a 60-foot Cone.") == (None, None, None)


def test_the_reader_writes_an_attacks_reach_and_range_on_its_effect():
    (bow,) = read_effects(
        "Longbow",
        "Ranged Attack Roll: +4, range 150/600 ft. Hit: 6 (1d8 + 2)"
        " Piercing damage.",
    )
    assert (bow.reach_ft, bow.range_ft, bow.long_range_ft) == (None, 150, 600)
    assert bow.attack_kind is AttackKind.RANGED
    (save,) = read_effects(
        "Spit",
        "Dexterity Saving Throw: DC 12, one creature within range 30 ft."
        " Failure: 7 (2d6) Acid damage.",
    )
    assert save.range_ft is None


def test_an_effects_reach_and_range():
    """Explicit-attributes plan 4.5: an attack effect states how far it
    goes, and which kind it is follows."""
    attack = EffectRoll.ATTACK
    assert CombatEffect(roll=attack, reach_ft=10).attack_kind is AttackKind.MELEE
    assert CombatEffect(roll=attack, range_ft=80).attack_kind is AttackKind.RANGED
    either = CombatEffect(roll=attack, reach_ft=5, range_ft=20, long_range_ft=60)
    assert either.attack_kind is None
    assert CombatEffect(roll=attack).attack_kind is None
    assert CombatEffect.from_dict(either.to_dict()) == either
    for wrong in (
        {"roll": EffectRoll.SAVE, "save_ability": Ability.DEXTERITY, "reach_ft": 5},
        {"roll": attack, "long_range_ft": 60},
        {"roll": attack, "range_ft": 60, "long_range_ft": 60},
        {"roll": attack, "reach_ft": 0},
        {"roll": attack, "reach_ft": True},
    ):
        with pytest.raises(ValueError):
            CombatEffect(**wrong)


def test_a_structured_attack_gives_its_fields():
    """Explicit-attributes plan 1.1 and 4.5: a MeleeAttack's `reach_ft` and
    a RangedAttack's `range_ft` / `long_range_ft` are read as fields, in the
    stat block and in the dict a saved log keeps; a freeform ability's are
    its attack effect's. No text is read."""
    pike = parse_action(MeleeAttack(name="Pike", attack_bonus=5, reach_ft=10))
    bow = parse_action(
        RangedAttack(name="Longbow", attack_bonus=4, range_ft=150, long_range_ft=600)
    )
    spear = parse_action(
        MeleeOrRangedAttack(name="Spear", attack_bonus=4, range_ft=20, long_range_ft=60)
    )
    assert monster_action_range(pike, "Pike") == AttackRange(10, what="Pike")
    assert monster_action_range(bow) == AttackRange(normal_ft=150, long_ft=600)
    assert monster_action_range(spear) == AttackRange(5, 20, 60)
    # A logged dict's fields win over its text, which is only shown.
    logged = {"name": "Pike", "description": "reach 10 ft.", "reach_ft": 15}
    assert monster_action_range(parse_action(logged)) == AttackRange(15)
    text = "Melee Attack Roll: +6, reach 10 ft. Hit: 9."
    freeform = MonsterAbility(
        name="Claw",
        description=text,
        combat_effects=(
            CombatEffect(roll=EffectRoll.ATTACK, attack_bonus=6, reach_ft=10),
        ),
    )
    claw = parse_action(freeform)
    assert monster_action_range(claw) == AttackRange(10)
    assert claw.attack_kind is AttackKind.MELEE
    # The same in its log dict.
    assert monster_action_range(parse_action(_plain({"a": freeform})["a"])) == (
        AttackRange(10)
    )
    # The text alone says nothing to the fight.
    assert monster_action_range(parse_action(MonsterAbility("Claw", text))) is None
    assert monster_action_range(parse_action(MonsterAbility("Roar", "Roars."))) is None


def test_a_weapon_has_the_weapons_tables_range():
    assert weapon_range(Longbow()) == AttackRange(
        normal_ft=150, long_ft=600, what="Longbow"
    )
    magic, glaive = weapon_range(MarksmansLongbow()), weapon_range(Glaive())
    assert magic is not None and magic.range_text == "150/600 ft."
    assert weapon_range(Dagger()) == AttackRange(5, 20, 60, "Dagger")
    assert glaive is not None and glaive.reach_ft == 10
    assert weapon_range(Longsword()) == AttackRange(reach_ft=5, what="Longsword")


def test_a_spells_attack_reaches_its_range_or_touch():
    fire_bolt = spell_attack_range(
        120, "Make a ranged spell attack against the target."
    )
    grasp = spell_attack_range(5, "Make a melee spell attack against the target.")
    assert fire_bolt == AttackRange(normal_ft=120)
    assert grasp == AttackRange(reach_ft=5)
    assert spell_attack_range(None, "Make a ranged spell attack.") is None
    assert spell_attack_range(60, "Each creature makes a Dexterity save.") is None


# ---------------------------------------------------------------------------
# Melee


def test_a_melee_attack_within_its_reach_has_nothing_to_say():
    fighter, goblin = _player("Fighter", (0, 0)), _monster("Goblin", (1, 0))
    assert _check(SWORD, fighter, goblin) == NO_RANGE_CHECK


def test_a_melee_attack_past_its_reach_is_warned_about():
    fighter, goblin = _player("Fighter", (0, 0)), _monster("Goblin", (3, 0))
    check = _check(SWORD, fighter, goblin)
    assert check.warnings == ("Goblin is 15 ft. away, past the 5 ft. reach",)
    assert check.disadvantages == ()


def test_a_reach_weapon_reaches_10_feet():
    fighter, goblin = _player("Fighter", (0, 0)), _monster("Goblin", (2, 0))
    assert _check(AttackRange(reach_ft=10), fighter, goblin) == NO_RANGE_CHECK


# ---------------------------------------------------------------------------
# Ranged


def test_within_the_normal_range_a_ranged_attack_is_a_straight_roll():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (10, 0))
    assert _check(BOW, archer, goblin) == NO_RANGE_CHECK


def test_past_the_normal_range_it_has_disadvantage():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (5, 0))
    short = AttackRange(normal_ft=20, long_ft=60)
    check = _check(short, archer, goblin)
    assert check.disadvantages == ("Long range, 25 ft. of 20/60 ft.",)
    assert check.warnings == ()


def test_past_the_long_range_it_cant_reach():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (13, 0))
    check = _check(AttackRange(normal_ft=20, long_ft=60), archer, goblin)
    assert check.warnings == ("Goblin is 65 ft. away, past its 20/60 ft. range",)
    assert check.disadvantages == ()


def test_a_spell_has_no_long_range():
    wizard, goblin = _player("Wizard", (0, 0)), _monster("Goblin", (5, 0))
    check = _check(AttackRange(normal_ft=20), wizard, goblin)
    assert check.warnings == ("Goblin is 25 ft. away, past its 20 ft. range",)


def test_an_enemy_within_5_feet_gives_a_ranged_attack_disadvantage():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (6, 0))
    beside = _monster("Orc", (0, 1))
    check = _check(BOW, archer, goblin, beside)
    assert check.disadvantages == ("Ranged attack within 5 ft. of Orc",)


def test_the_target_itself_within_5_feet_counts_too():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (1, 0))
    assert _check(BOW, archer, goblin).disadvantages == (
        "Ranged attack within 5 ft. of Goblin",
    )


def test_an_ally_or_an_incapacitated_or_fallen_enemy_close_by_doesnt():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (6, 0))
    friend = _player("Friend", (0, 1))
    stunned = _monster("Orc", (1, 0), conditions=["Stunned"])
    fallen = _monster("Ogre", (1, 1), hp=0)
    assert _check(BOW, archer, goblin, friend, stunned, fallen) == NO_RANGE_CHECK


def test_an_enemy_that_cant_see_the_attacker_imposes_nothing():
    # "within 5 feet of an enemy who can see you": a Blinded one can't
    # (step 28; before, it was left to the GM).
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (6, 0))
    blinded = _monster("Orc", (0, 1), conditions=["Blinded"])
    check = _check(BOW, archer, goblin, blinded)
    assert check.disadvantages == ()
    assert check.notes == (
        "Ranged attack within 5 ft. of Orc: no Disadvantage, it doesn't see"
        " the attacker (Orc is Blinded)",
    )


def test_a_thrown_dagger_is_melee_within_reach_and_thrown_past_it():
    rogue = _player("Rogue", (0, 0))
    assert _check(THROWN, rogue, _monster("Goblin", (1, 0))) == NO_RANGE_CHECK
    far = _check(THROWN, rogue, _monster("Goblin", (6, 0)))
    assert far.disadvantages == ("Long range, 30 ft. of 20/60 ft.",)


def test_off_the_map_or_unknown_there_is_nothing_to_check():
    archer = _player("Archer", (0, 0))
    goblin = {"name": "Goblin", "hp": 7}
    assert _check(BOW, archer, goblin) == NO_RANGE_CHECK
    assert _check(None, archer, _monster("Goblin", (90, 0))) == NO_RANGE_CHECK


def test_the_disadvantage_counts_in_the_attack_plan():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (5, 0))
    check = _check(AttackRange(normal_ft=20, long_ft=60), archer, goblin)
    plan = attack_plan(archer, goblin, "Neutral", extra=check.modifiers)
    assert plan.mode == "Disadvantage"
    assert any("Long range, 25 ft. of 20/60 ft." in note for note in plan.notes)
    helped = attack_plan(archer, goblin, "Advantage", extra=check.modifiers)
    assert helped.mode == "Neutral"


def test_a_spell_aimed_at_a_creature_past_its_range_is_warned_about():
    wizard, goblin = _player("Wizard", (0, 0)), _monster("Goblin", (13, 0))
    settings = ArenaSettings()
    assert spell_range_warning(60, wizard, goblin, settings) == (
        "Goblin is 65 ft. away, past the spell's 60 ft. range"
    )
    assert spell_range_warning(120, wizard, goblin, settings) == ""
    assert spell_range_warning(None, wizard, goblin, settings) == ""
