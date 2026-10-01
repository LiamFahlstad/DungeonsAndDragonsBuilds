"""
The Character model (Model/Character.py): one object holding the sources
and answering every query, with evaluation cached under a version key.
"""

import subprocess
import sys

import pytest

from Model.Character import Character
from Builds.Tests.SpellSlotTestPaladin5 import SpellSlotTestPaladin5CharacterBuilder
from CharacterContent.Features.Core.Improvements import (
    AbilityScoreBonus,
    SkillBonus,
    SkillProficiency,
)
from CharacterContent.Items import Items
from Core.Definitions import Ability, CharacterClass, Skill
from Model.Recorder import SealedError


def test_a_build_is_one_character():
    data = SpellSlotTestPaladin5CharacterBuilder().build()
    assert type(data) is Character
    assert data.validate() is data


class TestReEvaluatesAfterEveryKindOfChange:
    def test_assigning_a_field(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        before = data.calculate_speed()
        data.base_speed = data.base_speed + 10
        assert data.calculate_speed() == before + 10

    def test_changing_the_inventory_directly(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        before = data.calculate_armor_class()
        data.inventory.add_adventuring_gear(
            "Loot", items=[(Items.CloakOfProtection(), 1)]
        )
        assert data.calculate_armor_class() == before + 1

    def test_extending_a_feature_after_a_query(self):
        from CharacterContent.Features.SubClassFeatures2014.Cleric import (
            ClericForgeFeatures,
        )
        from Core.Definitions import DamageType
        from tests.test_all_builds import ALL_BUILDS

        data = type(ALL_BUILDS["Y2014DruidDreamsSomnaDriftwillowCharacterBuilder"])()
        data = data.build()
        assert not data.is_immune_to_damage(DamageType.FIRE)
        data.features[0].extend_feature(ClericForgeFeatures.SaintOfForgeAndFire())
        assert data.is_immune_to_damage(DamageType.FIRE)

    def test_evaluation_never_changes_the_base_scores(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        base = [data.base_abilities.get_score(a) for a in Ability]
        final = [data.get_ability_score(a) for a in Ability]
        data._changed()
        assert [data.get_ability_score(a) for a in Ability] == final
        assert [data.base_abilities.get_score(a) for a in Ability] == base


def test_requirements_are_checked_by_validate_not_by_queries(make_character):
    # STR/DEX 10: a Fighter/Wizard misses Fighter's multiclass prerequisite.
    character = make_character(
        levels={CharacterClass.FIGHTER: 1, CharacterClass.WIZARD: 1},
        intelligence=13,
    )
    assert character.calculate_hit_points() > 0
    with pytest.raises(ValueError, match="Multiclassing"):
        character.validate()


def test_model_package_imports_nothing_from_character_content():
    # CharacterContent imports the model (for Character and Effects), so the
    # model importing CharacterContent at load time would be an import cycle.
    code = (
        "import sys, pathlib, importlib; "
        "[importlib.import_module('Model.' + p.stem) "
        "for p in pathlib.Path('Model').glob('*.py') if p.stem != '__init__']; "
        "loaded = [m for m in sys.modules if m.startswith('CharacterContent')]; "
        "assert not loaded, loaded"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


class TestTheEvaluatedLedgerIsSealed:
    """Everything the Character answers comes from a Ledger it rebuilds from
    its sources, so a write into an evaluated part would be lost at the next
    rebuild. It raises instead."""

    def test_a_part_rejects_writes_after_evaluation(self, make_character):
        character = make_character()
        character.validate()
        with pytest.raises(SealedError):
            character.skills.add_skill_proficiency(Skill.STEALTH)
        with pytest.raises(SealedError):
            character.abilities.add_bonus(Ability.WISDOM, 2)

    def test_a_part_inside_a_part_is_sealed_too(self, make_character):
        character = make_character()
        character.add_effect(SkillBonus(Skill.ARCANA, 1, source="Test"))
        bonuses = character.skills._bonuses[Skill.ARCANA]
        with pytest.raises(SealedError):
            bonuses.add(1, "Test")

    def test_writing_a_score_on_the_evaluated_copy_raises(self, make_character):
        character = make_character(strength=10)
        character.validate()
        with pytest.raises(SealedError):
            character.abilities.strength = 18

    @pytest.mark.xfail(
        strict=True,
        reason="Step 5: base_abilities changed in place doesn't bump the "
        "version, so the cached evaluation goes stale. Step 5 makes "
        "base_abilities immutable.",
    )
    def test_changing_a_base_score_in_place_re_evaluates(self, make_character):
        character = make_character(strength=10)
        character.validate()
        character.base_abilities.strength = 18
        assert character.get_ability_score(Ability.STRENGTH) == 18


class TestAddEffect:
    def test_survives_re_evaluation(self, make_character):
        character = make_character()
        character.add_effect(SkillProficiency([Skill.STEALTH]))
        assert character.is_proficient_in_skill(Skill.STEALTH)
        # Any change to the sources rebuilds the Ledger; the effect is a
        # source, so it's recorded again.
        character.base_speed = 35
        assert character.calculate_speed() == 35
        assert character.is_proficient_in_skill(Skill.STEALTH)

    def test_is_a_change_to_the_sources(self, make_character):
        character = make_character(wisdom=10)
        assert character.get_ability_score(Ability.WISDOM) == 10
        character.add_effect(AbilityScoreBonus([(Ability.WISDOM, 2)], total=2))
        assert character.get_ability_score(Ability.WISDOM) == 12


def test_apply_order_change_re_evaluates(make_character):
    applied = []

    class _Recording:
        def __init__(self, label):
            self.label = label

        def apply(self, effects):
            applied.append(self.label)

    character = make_character()
    character.add_effect(_Recording("a"))
    character.add_effect(_Recording("b"))
    character.validate()
    assert applied == ["a", "b"]
    applied.clear()
    character._apply_order = lambda effects: effects[::-1]
    character.validate()
    assert applied == ["b", "a"]
