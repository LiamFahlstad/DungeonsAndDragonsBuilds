"""
The Character model (StatBlocks/Character.py): one object holding the sources
and answering every query, with evaluation cached under a version key.
"""

import subprocess
import sys

import pytest

from Builds.CharacterSheetAccumulator import CharacterSheetData
from Builds.Tests.SpellSlotTestPaladin5 import SpellSlotTestPaladin5CharacterBuilder
from CharacterContent.Items import Items
from Core.Definitions import Ability, CharacterClass
from StatBlocks.Character import Character
from StatBlocks.CharacterStatBlock import CharacterStatBlock


def test_sheet_data_and_stat_block_are_the_character():
    assert CharacterSheetData is Character
    assert CharacterStatBlock is Character
    data = SpellSlotTestPaladin5CharacterBuilder().build()
    assert data.setup_character_stat_block() is data


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
    # CharacterContent imports the model (as CharacterStatBlock), so the model
    # importing CharacterContent at load time would be an import cycle.
    code = (
        "import sys, StatBlocks.Character, StatBlocks.CharacterStatBlock; "
        "loaded = [m for m in sys.modules if m.startswith('CharacterContent')]; "
        "assert not loaded, loaded"
    )
    subprocess.run([sys.executable, "-c", code], check=True)
