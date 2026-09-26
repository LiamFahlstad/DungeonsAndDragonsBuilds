"""
Every registered build (RunCharacterCreator.BuildSelector) and every example
build (Builds/Examples) must build and produce a sane stat block. These are
broad smoke/invariant checks - they catch import errors, deleted classes and
rebuild side effects across all ~160 builds, not per-build numbers.

No sheet is written to Output/.
"""

import inspect
import sys

import pytest

from CharacterContent.Classes.BaseClasses import ClassBuilder
from Core.Definitions import Ability, CharacterClass, Skill
from RunCharacterCreator import BuildSelector, ExampleSelector

ALL_BUILDS = {**BuildSelector.builds(), **ExampleSelector.builds()}

BUILD_PARAMS = sorted(ALL_BUILDS)

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


def _all_features(features):
    for feature in features:
        yield feature
        yield from _all_features(feature.extensions)


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_every_feature_renders(name):
    # Descriptions are only evaluated when a sheet is written, so a broken
    # get_description (missing import, deleted helper) otherwise goes unseen.
    data = type(ALL_BUILDS[name])().build()
    character = data.setup_character_stat_block()
    for feature in _all_features(data.features):
        description = feature.get_description(character)
        assert description is None or isinstance(description, str), feature.name
        feature.get_table_description(character)
        feature.get_concise_description(character)


# Features that grant proficiency *and* Expertise: picking a skill you already
# have still gains the Expertise, so the overlap isn't wasted.
_EXPERTISE_GRANTING = {"BlessingsOfKnowledge"}


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_no_wasted_skill_proficiency(name, monkeypatch):
    # PHB: gaining a proficiency you already have from another source means
    # choosing a different one instead - a build shouldn't pick it twice.
    import inspect

    from CharacterContent.Features.Core.BaseFeatures import Feature
    from StatBlocks.SkillsStatBlock import SkillsStatBlock

    original = SkillsStatBlock.add_skill_proficiency
    wasted = []

    def recording(self, skill):
        if self.is_proficient(skill):
            source = next(
                (
                    type(frame.frame.f_locals["self"]).__name__
                    for frame in inspect.stack()[1:15]
                    if isinstance(frame.frame.f_locals.get("self"), Feature)
                ),
                "?",
            )
            if source not in _EXPERTISE_GRANTING:
                wasted.append((skill.name, source))
        return original(self, skill)

    monkeypatch.setattr(SkillsStatBlock, "add_skill_proficiency", recording)
    type(ALL_BUILDS[name])().build().setup_character_stat_block()
    assert wasted == []


def _class_builders(build):
    builders = []
    for value in vars(build).values():
        if isinstance(value, ClassBuilder.ClassBuilder):
            builders.append(value)
        elif isinstance(value, (list, tuple)):
            builders += [v for v in value if isinstance(v, ClassBuilder.ClassBuilder)]
    return builders


def _subclass_levels_defined(module) -> dict[int, str]:
    """{level: class name} for every SubclassLevelN builder in a subclass module."""
    levels = {}
    for name, cls in inspect.getmembers(module, inspect.isclass):
        if cls.__module__ != module.__name__:
            continue
        for base in cls.__mro__[1:]:
            suffix = base.__name__.removeprefix("SubclassLevel")
            if base.__name__.startswith("SubclassLevel") and suffix.isdigit():
                levels[int(suffix)] = name
                break
    return levels


@pytest.mark.parametrize("name", BUILD_PARAMS)
def test_no_subclass_level_is_skipped(name):
    # A subclass level missing from subclass_features_by_level is silently
    # skipped by BaseClassLevelFeatures.add_features, so the character loses
    # that level's features and always-prepared spells without any error.
    for class_builder in _class_builders(ALL_BUILDS[name]):
        subclass_levels = (
            class_builder.base_class_level_features.subclass_features_by_level
        )
        if not subclass_levels:
            continue
        module = sys.modules[type(next(iter(subclass_levels.values()))).__module__]
        missing = [
            (level, cls_name)
            for level, cls_name in sorted(_subclass_levels_defined(module).items())
            if level <= class_builder.base_class_level and level not in subclass_levels
        ]
        assert not missing, f"{name}: missing subclass levels {missing}"
