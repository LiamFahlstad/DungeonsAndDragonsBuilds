"""
Every registered build (RunCharacterCreator.BuildSelector) and every example
build (Builds/Examples) must build and produce a sane stat block. These are
broad smoke/invariant checks - they catch import errors, deleted classes and
rebuild side effects across all ~160 builds, not per-build numbers.

No sheet is written to Output/.
"""

import pytest

from Core.Definitions import Ability, CharacterClass, Skill
from RunCharacterCreator import BuildSelector, ExampleSelector

ALL_BUILDS = {**BuildSelector.builds(), **ExampleSelector.builds()}

# Builds whose 2014 subclass feature files were truncated by commit 677b444
# ("Create Feature Uses object"), deleting classes they still reference.
TRUNCATED_BY_677B444 = {
    "Y2014ArtificerAlchemistBramwellFizzlecogCharacterBuilder",
    "Y2014ArtificerBattleSmithDorricSteamwellCharacterBuilder",
    "Y2014BarbarianAncestralGuardianKodiakStonewatchCharacterBuilder",
    "Y2014BarbarianWildMagicFenwickChaosbornCharacterBuilder",
    "Y2014ClericForgeBrennaHearthforgeCharacterBuilder",
    "Y2014ClericOrderCastellanTruewardCharacterBuilder",
    "Y2014ClericPeaceHalcyonMeadowlightCharacterBuilder",
    "Y2014ClericTempestStormWavecrestCharacterBuilder",
    "Y2014ClericTwilightVesperNightsongCharacterBuilder",
    "Y2014DruidDreamsSomnaDriftwillowCharacterBuilder",
    "Y2014DruidShepherdMeridianFlockwardCharacterBuilder",
    "Y2014DruidSporesMossenRotbloomCharacterBuilder",
    "Y2014DruidWildfireEmberAshgroveCharacterBuilder",
}


def _params():
    for name in sorted(ALL_BUILDS):
        marks = ()
        if name in TRUNCATED_BY_677B444:
            marks = pytest.mark.xfail(
                strict=True,
                raises=AttributeError,
                reason="BUG: feature classes deleted by commit 677b444",
            )
        yield pytest.param(name, marks=marks, id=name)


BUILD_PARAMS = list(_params())

# PHB proficiency bonus by total character level.
PHB_PROFICIENCY_BONUS = {
    **dict.fromkeys(range(1, 5), 2),
    **dict.fromkeys(range(5, 9), 3),
    **dict.fromkeys(range(9, 13), 4),
    **dict.fromkeys(range(13, 17), 5),
    **dict.fromkeys(range(17, 21), 6),
}


def _stats(data, character):
    return (
        {a: character.get_ability_score(a) for a in Ability},
        {s: character.get_skill_modifier(s) for s in Skill},
        {a: character.get_saving_throw_modifier(a) for a in Ability},
        character.calculate_hit_points(),
        character.calculate_armor_class(),
        character.initiative,
        dict(character.spell_slots or {}),
        dict(character.pact_magic_slots),
        [
            (
                w.name,
                w.calculate_total_attack_roll_bonus_int(character),
                w.calculate_damage_bonus_int(character),
            )
            for w in data.weapons
        ],
    )


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_build_and_invariants(name):
    data = type(ALL_BUILDS[name])().build()
    character = data.setup_character_stat_block()

    level = data.character_level
    assert 1 <= level <= 20
    assert character.get_proficiency_bonus() == PHB_PROFICIENCY_BONUS[level]
    assert character.calculate_hit_points() >= level
    assert all(1 <= character.get_ability_score(a) <= 30 for a in Ability)
    assert character.calculate_armor_class() >= 5
    assert data.character_name and data.character_subclass


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_rebuild_is_idempotent(name):
    builder = type(ALL_BUILDS[name])()
    first = builder.build()
    first_stats = _stats(first, first.setup_character_stat_block())

    # Same builder instance again, then a forced re-setup of the same sheet.
    second = builder.build()
    assert _stats(second, second.setup_character_stat_block()) == first_stats
    second._invalidate_cache()
    assert _stats(second, second.setup_character_stat_block()) == first_stats


# PHB spellcasting ability per class.
PHB_SPELLCASTING_ABILITY = {
    CharacterClass.ARTIFICER: Ability.INTELLIGENCE,
    CharacterClass.BARD: Ability.CHARISMA,
    CharacterClass.CLERIC: Ability.WISDOM,
    CharacterClass.DRUID: Ability.WISDOM,
    CharacterClass.PALADIN: Ability.CHARISMA,
    CharacterClass.RANGER: Ability.WISDOM,
    CharacterClass.SORCERER: Ability.CHARISMA,
    CharacterClass.WARLOCK: Ability.CHARISMA,
    CharacterClass.WIZARD: Ability.INTELLIGENCE,
}


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_single_class_caster_uses_class_ability(name):
    # Regression: build() used to overwrite the class's ability with the
    # highest raw mental score (7 Paladins ended up casting with Wisdom).
    data = type(ALL_BUILDS[name])().build()
    if len(data.level_per_class) != 1 or data.base_class not in (
        PHB_SPELLCASTING_ABILITY
    ):
        return
    assert data.spell_casting_ability == PHB_SPELLCASTING_ABILITY[data.base_class]
