"""
End-to-end tests for CharacterBuilder.build() and the resulting
CharacterSheetData / CharacterStatBlock.

The builders under test are the hand-written scenario builds in Builds/Tests/
(legacy scripts, not pytest files themselves). Each is built once per module.
"""

import pytest

from Builds.CharacterBuilder import CharacterBuilder
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Builds.Tests.MulticlassTest import MulticlassTestCharacterBuilder
from Builds.Tests.SpellSlotTestPaladin4Wizard3 import (
    SpellSlotTestPaladin4Wizard3CharacterBuilder,
)
from Builds.Tests.SpellSlotTestPaladin5 import SpellSlotTestPaladin5CharacterBuilder
from Builds.Tests.SpellSlotTestWizard3Warlock3 import (
    SpellSlotTestWizard3Warlock3CharacterBuilder,
)
from Builds.Tests.SpellSlotTestWizard5 import SpellSlotTestWizard5CharacterBuilder
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Items, Weapons
from Core.Definitions import Ability, CharacterClass, Skill

ALL_BUILDERS = [
    MulticlassTestCharacterBuilder,
    SpellSlotTestPaladin4Wizard3CharacterBuilder,
    SpellSlotTestPaladin5CharacterBuilder,
    SpellSlotTestWizard3Warlock3CharacterBuilder,
    SpellSlotTestWizard5CharacterBuilder,
]


@pytest.fixture(scope="module")
def built():
    """Build every scenario once: {builder_class: (sheet_data, stat_block)}."""
    results = {}
    for builder_class in ALL_BUILDERS:
        data = builder_class().build()
        results[builder_class] = (data, data.setup_character_stat_block())
    return results


class TestBuildBasics:
    @pytest.mark.parametrize("builder_class", ALL_BUILDERS)
    def test_build_returns_complete_sheet(self, built, builder_class):
        data, character = built[builder_class]
        assert isinstance(data, CharacterSheetData)
        assert data.character_name
        assert data.character_subclass
        assert data.base_class is not None
        assert data.features
        assert character is not None

    @pytest.mark.parametrize("builder_class", ALL_BUILDERS)
    def test_non_example_builds_not_flagged_as_example(self, built, builder_class):
        data, _ = built[builder_class]
        assert data.is_example is False

    def test_stat_block_is_cached(self, built):
        data, character = built[SpellSlotTestWizard5CharacterBuilder]
        assert data.setup_character_stat_block() is character

    def test_builder_is_character_builder(self):
        for builder_class in ALL_BUILDERS:
            assert issubclass(builder_class, CharacterBuilder)


class TestLevels:
    @pytest.mark.parametrize(
        "builder_class,expected_levels",
        [
            (SpellSlotTestWizard5CharacterBuilder, {CharacterClass.WIZARD: 5}),
            (SpellSlotTestPaladin5CharacterBuilder, {CharacterClass.PALADIN: 5}),
            (
                SpellSlotTestPaladin4Wizard3CharacterBuilder,
                {CharacterClass.PALADIN: 4, CharacterClass.WIZARD: 3},
            ),
            (
                SpellSlotTestWizard3Warlock3CharacterBuilder,
                {CharacterClass.WIZARD: 3, CharacterClass.WARLOCK: 3},
            ),
            (
                MulticlassTestCharacterBuilder,
                {CharacterClass.FIGHTER: 1, CharacterClass.WIZARD: 3},
            ),
        ],
    )
    def test_level_per_class(self, built, builder_class, expected_levels):
        data, _ = built[builder_class]
        assert data.level_per_class == expected_levels
        assert data.character_level == sum(expected_levels.values())

    def test_base_class_is_starter_class(self, built):
        data, _ = built[SpellSlotTestPaladin4Wizard3CharacterBuilder]
        assert data.base_class == CharacterClass.PALADIN

    @pytest.mark.parametrize(
        "builder_class,expected_bonus",
        [
            (MulticlassTestCharacterBuilder, 2),  # level 4
            (SpellSlotTestWizard5CharacterBuilder, 3),  # level 5
            (SpellSlotTestPaladin4Wizard3CharacterBuilder, 3),  # level 7
        ],
    )
    def test_proficiency_bonus_uses_total_level(
        self, built, builder_class, expected_bonus
    ):
        _, character = built[builder_class]
        assert character.get_proficiency_bonus() == expected_bonus


class TestSpellSlots:
    @pytest.mark.parametrize(
        "builder_class,expected_slots",
        [
            # Full caster 5.
            (SpellSlotTestWizard5CharacterBuilder, {1: 4, 2: 3, 3: 2}),
            # Half caster 5 -> caster level 3.
            (SpellSlotTestPaladin5CharacterBuilder, {1: 4, 2: 2}),
            # Paladin 4 (-> 2) + Wizard 3 -> caster level 5 (PHB multiclass example).
            (SpellSlotTestPaladin4Wizard3CharacterBuilder, {1: 4, 2: 3, 3: 2}),
            # Warlock levels don't count toward shared slots.
            (SpellSlotTestWizard3Warlock3CharacterBuilder, {1: 4, 2: 2}),
            # Fighter (non-Eldritch-Knight) adds nothing.
            (MulticlassTestCharacterBuilder, {1: 4, 2: 2}),
        ],
    )
    def test_spell_slots(self, built, builder_class, expected_slots):
        _, character = built[builder_class]
        assert character.get_spell_slots() == expected_slots

    def test_warlock_pact_magic_slots_separate(self, built):
        _, character = built[SpellSlotTestWizard3Warlock3CharacterBuilder]
        assert character.pact_magic_slots == {2: 2}

    def test_non_warlock_has_no_pact_magic(self, built):
        _, character = built[SpellSlotTestWizard5CharacterBuilder]
        assert character.pact_magic_slots == {}


class TestAbilitiesAndDerivedStats:
    def test_background_and_asi_bonuses_applied(self, built):
        # Paladin 5: STR 15 +2 background; CHA 14 +1 background +2 ASI.
        _, character = built[SpellSlotTestPaladin5CharacterBuilder]
        assert character.get_ability_score(Ability.STRENGTH) == 17
        assert character.get_ability_score(Ability.CHARISMA) == 17

    @pytest.mark.parametrize(
        "builder_class,expected_ability",
        [
            (SpellSlotTestWizard5CharacterBuilder, Ability.INTELLIGENCE),
            (SpellSlotTestPaladin5CharacterBuilder, Ability.CHARISMA),
        ],
    )
    def test_spell_casting_ability(self, built, builder_class, expected_ability):
        data, _ = built[builder_class]
        assert data.spell_casting_ability == expected_ability

    def test_spell_save_dc(self, built):
        # 8 + prof 3 + CHA mod 3.
        _, character = built[SpellSlotTestPaladin5CharacterBuilder]
        assert character.calculate_difficulty_class() == 14

    def test_skill_modifier_with_proficiency(self, built):
        # Athletics: STR mod 3 + prof 3.
        _, character = built[SpellSlotTestPaladin5CharacterBuilder]
        assert character.is_proficient_in_skill(Skill.ATHLETICS)
        assert character.get_skill_modifier(Skill.ATHLETICS) == 6

    def test_class_saving_throw_proficiencies(self, built):
        _, character = built[SpellSlotTestPaladin5CharacterBuilder]
        assert character.is_proficient_in_saving_throw(Ability.WISDOM)
        assert character.is_proficient_in_saving_throw(Ability.CHARISMA)
        assert not character.is_proficient_in_saving_throw(Ability.STRENGTH)


class TestHitPoints:
    def test_single_class_hit_points(self, built):
        # Wizard 5, CON 13 (+1): 6+1 at level 1, then 4 * (4+1).
        _, character = built[SpellSlotTestWizard5CharacterBuilder]
        assert character.calculate_hit_points() == 27

    def test_multiclass_hit_points_with_tough(self, built):
        # Paladin 4 / Wizard 3, CON 14 (+2):
        #   Paladin: 10+2 + 3 * (6+2) = 36
        #   Wizard:  3 * (4+2)        = 18
        #   Tough:   2 * 7            = 14
        _, character = built[SpellSlotTestPaladin4Wizard3CharacterBuilder]
        assert character.calculate_hit_points() == 68


class TestRebuildIsIdempotent:
    """Building or re-deriving the stat block must not change the result."""

    def test_same_builder_built_twice(self):
        builder = SpellSlotTestPaladin5CharacterBuilder()
        first = builder.build().setup_character_stat_block()
        first_scores = {a: first.get_ability_score(a) for a in Ability}
        second = builder.build().setup_character_stat_block()
        assert {a: second.get_ability_score(a) for a in Ability} == first_scores

    def test_setup_after_mutation(self):
        data = SpellSlotTestPaladin5CharacterBuilder().build()
        before = data.setup_character_stat_block().get_ability_score(Ability.STRENGTH)
        data.add_item(Items.Torch(), 1)
        after = data.setup_character_stat_block().get_ability_score(Ability.STRENGTH)
        assert after == before

    def test_archery_does_not_stack_on_rebuild(self):
        data = SpellSlotTestWizard5CharacterBuilder().build()
        bow = Weapons.Longbow()
        data.add_weapon(bow)
        data.add_fighting_style(FightingStyles.Archery())
        data.setup_character_stat_block()
        data.add_item(Items.Torch(), 1)
        data.setup_character_stat_block()
        assert sum(b for b, _ in bow.attack_roll_bonuses) == 2
