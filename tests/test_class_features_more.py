"""
Class features under CharacterContent/Features/ClassFeatures for the classes NOT
covered by tests/test_class_features.py: Fighter, Rogue, Sorcerer, Warlock,
Wizard, Druid, Artificer, and (lightly) Psion.

The base classes in this engine follow the 2024 PHB, so expected values are
taken from the 2024 PHB class tables and cross-checked against each feature's
own get_description()/get_table_description() prose:

  - Fighter: Second Wind, Action Surge, Indomitable "Uses" columns.
  - Rogue: Sneak Attack dice column; Expertise/Slippery Mind rule text.
  - Sorcerer: Font of Magic ("Sorcery Points equal to Sorcerer level") and
    Metamagic "Options Known" column.
  - Wizard: Arcane Recovery ("combined level no more than half your Wizard
    level, round up").
  - Druid: Wild Shape "Uses" column.
  - Artificer: Tinker's Magic / Flash of Genius ("Intelligence modifier,
    minimum of once") - both features' own description text.

Warlock's Eldritch Invocations Known table is already transcribed and checked
in tests/test_spell_lists_invocations.py, so it is not repeated here. Psion
is homebrew/UA content with no official 2024 table for Psionic Energy Dice
counts, so only its documented (prose-stated) regain cadence is checked, not
any numeric progression.
"""

import pytest

from CharacterContent.Features.ClassFeatures.Artificer import ArtificerFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Features.ClassFeatures.Ranger import RangerFeatures
from CharacterContent.Features.ClassFeatures.Druid import DruidFeatures
from CharacterContent.Features.ClassFeatures.Fighter import FighterFeatures
from CharacterContent.Features.ClassFeatures.Psion import PsionFeatures
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures
from CharacterContent.Features.ClassFeatures.Sorcerer import SorcererFeatures
from CharacterContent.Features.ClassFeatures.Warlock import WarlockFeatures
from CharacterContent.Features.ClassFeatures.Wizard import WizardFeatures
from CharacterContent.Features.Core.BaseFeatures import RegainedOn
from Core.Definitions import Ability, CharacterClass, Skill


def apply_features(character, features):
    for feature in features:
        feature.apply(character)
    for feature in features:
        feature.apply_after_armor(character)
    return character


def xfail_bug(reason):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


def _expand_level_ranges(steps):
    """Turn get_resource_tiles()' compressed [("Lv 1-4", "1d6"), ...] steps
    back into a per-level dict, so the underlying table can be compared
    level-by-level against a hand-transcribed PHB table."""
    result = {}
    for level_range, value in steps:
        level_range = level_range.replace("Lv ", "")
        if "-" in level_range:
            start_str, end_str = level_range.split("-")
            start, end = int(start_str), int(end_str)
        else:
            start = end = int(level_range)
        for level in range(start, end + 1):
            result[level] = value
    return result


# ---------------------------------------------------------------------------
# Fighter (2024 PHB Fighter Features table)
# ---------------------------------------------------------------------------

# "Uses" column keyed by Fighter level, transcribed from the 2024 PHB.
PHB_2024_SECOND_WIND_USES = {1: 2, 2: 2, 3: 2, 4: 3, 9: 3, 10: 4, 15: 4, 20: 4}
PHB_2024_ACTION_SURGE_USES = {2: 1, 10: 1, 16: 1, 17: 2, 20: 2}
PHB_2024_INDOMITABLE_USES = {9: 1, 12: 1, 13: 2, 16: 2, 17: 3, 20: 3}


class TestFighterResourceUses:
    @pytest.mark.parametrize("level,expected", PHB_2024_SECOND_WIND_USES.items())
    def test_second_wind_uses_single_classed(self, make_character, level, expected):
        character = make_character(levels={CharacterClass.FIGHTER: level})
        assert FighterFeatures.SecondWind().number_of_uses(character) == expected

    @pytest.mark.parametrize("level,expected", PHB_2024_ACTION_SURGE_USES.items())
    def test_action_surge_uses_single_classed(self, make_character, level, expected):
        character = make_character(levels={CharacterClass.FIGHTER: level})
        assert FighterFeatures.ActionSurge().number_of_uses(character) == expected

    @pytest.mark.parametrize("level,expected", PHB_2024_INDOMITABLE_USES.items())
    def test_indomitable_uses_single_classed(self, make_character, level, expected):
        character = make_character(levels={CharacterClass.FIGHTER: level})
        assert FighterFeatures.Indomitable().number_of_uses(character) == expected

    def test_second_wind_regained_on_short_or_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.FIGHTER: 1})
        assert (
            FighterFeatures.SecondWind().regained_on(character)
            == RegainedOn.SHORT_OR_LONG_REST
        )

    def test_action_surge_regained_on_short_or_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.FIGHTER: 2})
        assert (
            FighterFeatures.ActionSurge().regained_on(character)
            == RegainedOn.SHORT_OR_LONG_REST
        )

    def test_indomitable_regained_on_long_rest_only(self, make_character):
        character = make_character(levels={CharacterClass.FIGHTER: 9})
        assert (
            FighterFeatures.Indomitable().regained_on(character) == RegainedOn.LONG_REST
        )


class TestFighterMulticlassResourceBug:
    """These Fighter features scale by *Fighter* class level, not total
    character level (they come from the Fighter class table specifically -
    the same way Sorcerer's Font of Magic keys off get_class_level(SORCERER)
    and Druid's Wild Shape keys off get_class_level(DRUID), not
    character_level). A Fighter who multiclasses gets the wrong use count."""

    def test_second_wind_uses_fighter_level_not_character_level(self, make_character):
        character = make_character(
            levels={CharacterClass.FIGHTER: 9, CharacterClass.WIZARD: 6}
        )
        assert FighterFeatures.SecondWind().number_of_uses(character) == 3

    def test_action_surge_uses_fighter_level_not_character_level(self, make_character):
        character = make_character(
            levels={CharacterClass.FIGHTER: 16, CharacterClass.CLERIC: 5}
        )
        assert FighterFeatures.ActionSurge().number_of_uses(character) == 1

    def test_indomitable_uses_fighter_level_not_character_level(self, make_character):
        character = make_character(
            levels={CharacterClass.FIGHTER: 9, CharacterClass.ROGUE: 8}
        )
        assert FighterFeatures.Indomitable().number_of_uses(character) == 1


# ---------------------------------------------------------------------------
# Rogue (2024 PHB)
# ---------------------------------------------------------------------------

# Sneak Attack damage dice column, transcribed from the 2024 PHB Rogue table.
PHB_2024_SNEAK_ATTACK_DICE = {
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 4,
    8: 4,
    9: 5,
    10: 5,
    11: 6,
    12: 6,
    13: 7,
    14: 7,
    15: 8,
    16: 8,
    17: 9,
    18: 9,
    19: 10,
    20: 10,
}


class TestRogueSneakAttack:
    def test_dice_progression_matches_phb_table(self, make_character):
        character = make_character(levels={CharacterClass.ROGUE: 1})
        tiles = RogueFeatures.SneakAttack().get_resource_tiles(character)
        assert len(tiles) == 1
        label, steps = tiles[0]
        assert label == "Sneak Attack Damage"
        dice_by_level = _expand_level_ranges(steps)
        for level, num_dice in PHB_2024_SNEAK_ATTACK_DICE.items():
            assert dice_by_level[level] == f"{num_dice}d6", f"Rogue level {level}"


class TestRogueExpertise:
    def test_doubles_proficiency_bonus_on_chosen_skills(self, make_character):
        character = make_character(
            levels={CharacterClass.ROGUE: 5}
        )  # proficiency bonus +3
        character.skills.add_skill_proficiency(Skill.STEALTH)
        character.skills.add_skill_proficiency(Skill.PERCEPTION)
        apply_features(
            character, [RogueFeatures.Expertise(Skill.STEALTH, Skill.PERCEPTION)]
        )
        dex_mod = character.get_ability_modifier(Ability.DEXTERITY)
        wis_mod = character.get_ability_modifier(Ability.WISDOM)
        assert character.get_skill_modifier(Skill.STEALTH) == dex_mod + 2 * 3
        assert character.get_skill_modifier(Skill.PERCEPTION) == wis_mod + 2 * 3

    def test_requires_prior_proficiency(self, make_character):
        # SkillExpertise.apply() raises if the skill isn't already proficient -
        # expertise can only double an existing proficiency bonus.
        character = make_character(levels={CharacterClass.ROGUE: 1})
        with pytest.raises(ValueError):
            apply_features(
                character,
                [RogueFeatures.Expertise(Skill.STEALTH, Skill.PERCEPTION)],
            )


class TestRogueCunningStrike:
    def test_dc_is_8_plus_dex_plus_proficiency(self, make_character):
        character = make_character(
            dexterity=16, levels={CharacterClass.ROGUE: 5}
        )  # DEX mod +3, proficiency bonus +3
        dc = RogueFeatures.CunningStrike().calculate_dc(character)
        assert dc == 8 + 3 + 3


class TestRogueSlipperyMind:
    def test_grants_wisdom_and_charisma_saving_throws(self, make_character):
        character = make_character(levels={CharacterClass.ROGUE: 15})
        apply_features(character, [RogueFeatures.SlipperyMind()])
        assert character.is_proficient_in_saving_throw(Ability.WISDOM)
        assert character.is_proficient_in_saving_throw(Ability.CHARISMA)
        assert not character.is_proficient_in_saving_throw(Ability.STRENGTH)
        assert not character.is_proficient_in_saving_throw(Ability.DEXTERITY)


# ---------------------------------------------------------------------------
# Sorcerer (2024 PHB)
# ---------------------------------------------------------------------------


class TestFontOfMagic:
    @pytest.mark.parametrize("level", [2, 3, 5, 9, 17, 20])
    def test_sorcery_points_equal_sorcerer_level(self, make_character, level):
        character = make_character(levels={CharacterClass.SORCERER: level})
        assert SorcererFeatures.FontOfMagic().number_of_uses(character) == level

    def test_regained_on_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.SORCERER: 2})
        assert (
            SorcererFeatures.FontOfMagic().regained_on(character)
            == RegainedOn.LONG_REST
        )


# 2024 PHB Sorcerer "Metamagic Options Known" column, transcribed by hand.
PHB_2024_METAMAGIC_OPTIONS_KNOWN = {
    2: 2,
    3: 2,
    9: 2,
    10: 4,
    11: 4,
    16: 4,
    17: 6,
    18: 6,
    20: 6,
}


class TestMetamagic:
    def test_options_known_progression_matches_phb_table(self, make_character):
        character = make_character(levels={CharacterClass.SORCERER: 2})
        tiles = SorcererFeatures.Metamagic().get_resource_tiles(character)
        label, steps = tiles[0]
        assert label == "Metamagic Options Known"
        options_by_level = _expand_level_ranges(steps)
        for level, expected in PHB_2024_METAMAGIC_OPTIONS_KNOWN.items():
            assert options_by_level[level] == str(expected), f"Sorcerer level {level}"


class TestInnateSorcery:
    def test_two_uses_regained_on_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.SORCERER: 1})
        feature = SorcererFeatures.InnateSorcery()
        assert feature.number_of_uses(character) == 2
        assert feature.regained_on(character) == RegainedOn.LONG_REST


# ---------------------------------------------------------------------------
# Warlock (2024 PHB) - Invocations Known table already covered in
# tests/test_spell_lists_invocations.py; only regain cadences tested here.
# ---------------------------------------------------------------------------


class TestWarlockRegainCadences:
    def test_pact_magic_slots_regain_on_short_or_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.WARLOCK: 1})
        assert (
            WarlockFeatures.RegainingSpellSlots().regained_on(character)
            == RegainedOn.SHORT_OR_LONG_REST
        )

    def test_magical_cunning_regains_on_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.WARLOCK: 2})
        assert (
            WarlockFeatures.MagicalCunning().regained_on(character)
            == RegainedOn.LONG_REST
        )

    def test_mystic_arcanum_regains_on_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.WARLOCK: 11})
        assert (
            WarlockFeatures.MysticArcanum().regained_on(character)
            == RegainedOn.LONG_REST
        )


# ---------------------------------------------------------------------------
# Wizard (2024 PHB)
# ---------------------------------------------------------------------------

# "Combined level equal to no more than half your Wizard level (round up)" -
# 2024 PHB Arcane Recovery text.
PHB_2024_ARCANE_RECOVERY_MAX_COMBINED = {
    1: 1,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    9: 5,
    10: 5,
    19: 10,
    20: 10,
}


class TestArcaneRecovery:
    @pytest.mark.parametrize(
        "level,expected", PHB_2024_ARCANE_RECOVERY_MAX_COMBINED.items()
    )
    def test_max_combined_slot_level_rounds_up(self, make_character, level, expected):
        character = make_character(levels={CharacterClass.WIZARD: level})
        table = dict(WizardFeatures.ArcaneRecovery().get_table_description(character))
        assert table["Maximum Slot Levels"] == f"Combined level ≤ {expected}"

    def test_regained_on_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.WIZARD: 1})
        assert (
            WizardFeatures.ArcaneRecovery().regained_on(character)
            == RegainedOn.LONG_REST
        )


class TestWizardScholar:
    def test_grants_expertise_in_chosen_intelligence_skill(self, make_character):
        character = make_character(levels={CharacterClass.WIZARD: 2})
        character.skills.add_skill_proficiency(Skill.ARCANA)
        apply_features(character, [WizardFeatures.Scholar(Skill.ARCANA)])
        int_mod = character.get_ability_modifier(Ability.INTELLIGENCE)
        proficiency_bonus = character.get_proficiency_bonus()
        assert (
            character.get_skill_modifier(Skill.ARCANA)
            == int_mod + 2 * proficiency_bonus
        )

    def test_rejects_skill_outside_pool(self, make_character):
        with pytest.raises(ValueError):
            WizardFeatures.Scholar(Skill.PERSUASION)


# ---------------------------------------------------------------------------
# Druid (2024 PHB)
# ---------------------------------------------------------------------------

# Wild Shape "Uses" column, transcribed from the 2024 PHB Druid table.
PHB_2024_WILD_SHAPE_USES = {2: 2, 5: 2, 6: 3, 16: 3, 17: 4, 20: 4}


class TestWildShape:
    @pytest.mark.parametrize("level,expected", PHB_2024_WILD_SHAPE_USES.items())
    def test_uses_progression(self, make_character, level, expected):
        character = make_character(levels={CharacterClass.DRUID: level})
        feature = DruidFeatures.WildShape(known_forms=[])
        assert feature.number_of_uses(character) == expected

    def test_regained_on_short_or_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.DRUID: 2})
        feature = DruidFeatures.WildShape(known_forms=[])
        assert feature.regained_on(character) == RegainedOn.SHORT_OR_LONG_REST


class TestDruidMulticlassResourceBug:
    """Contrast with TestFighterMulticlassResourceBug: Wild Shape correctly
    keys off get_class_level(DRUID), so multiclassing doesn't distort it."""

    def test_wild_shape_uses_druid_level_not_character_level(self, make_character):
        character = make_character(
            levels={CharacterClass.DRUID: 6, CharacterClass.FIGHTER: 10}
        )  # Druid level 6 (tier: 3 uses), character level 16
        feature = DruidFeatures.WildShape(known_forms=[])
        assert feature.number_of_uses(character) == 3


class TestArchdruid:
    def test_regained_on_initiative_roll(self, make_character):
        character = make_character(levels={CharacterClass.DRUID: 20})
        assert (
            DruidFeatures.Archdruid().regained_on(character)
            == RegainedOn.INITIATIVE_ROLL
        )


class TestPrimalOrderMagician:
    def test_magician_grants_wisdom_based_arcana_and_nature_bonus(self, make_character):
        character = make_character(
            wisdom=16, intelligence=10, levels={CharacterClass.DRUID: 1}
        )  # WIS mod +3, INT mod +0
        apply_features(
            character,
            [DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.MAGICIAN)],
        )
        int_mod = character.get_ability_modifier(Ability.INTELLIGENCE)
        assert character.get_skill_modifier(Skill.ARCANA) == int_mod + 3
        assert character.get_skill_modifier(Skill.NATURE) == int_mod + 3


# ---------------------------------------------------------------------------
# Artificer (2024 rules)
# ---------------------------------------------------------------------------


class TestArtificerIntelligenceScaledResources:
    """Both features' own description text says 'a number of times equal to
    your Intelligence modifier (minimum of once)'."""

    @pytest.mark.parametrize(
        "feature_cls", [ArtificerFeatures.TinkersMagic, ArtificerFeatures.FlashofGenius]
    )
    def test_uses_equal_int_modifier_when_positive(self, make_character, feature_cls):
        character = make_character(
            intelligence=18, levels={CharacterClass.ARTIFICER: 1}
        )  # INT mod +4
        assert feature_cls().number_of_uses(character) == 4

    @pytest.mark.parametrize(
        "feature_cls", [ArtificerFeatures.TinkersMagic, ArtificerFeatures.FlashofGenius]
    )
    def test_uses_regained_on_long_rest(self, make_character, feature_cls):
        character = make_character(levels={CharacterClass.ARTIFICER: 1})
        assert feature_cls().regained_on(character) == RegainedOn.LONG_REST

    def test_tinkers_magic_minimum_one_use_at_zero_modifier(self, make_character):
        character = make_character(
            intelligence=10, levels={CharacterClass.ARTIFICER: 1}
        )
        assert ArtificerFeatures.TinkersMagic().number_of_uses(character) == 1

    def test_flash_of_genius_minimum_one_use_at_negative_modifier(self, make_character):
        character = make_character(intelligence=8, levels={CharacterClass.ARTIFICER: 7})
        assert ArtificerFeatures.FlashofGenius().number_of_uses(character) == 1

    def test_flash_of_genius_table_description_does_clamp_to_minimum_one(
        self, make_character
    ):
        # get_table_description() (the rendered sheet value) gets this right;
        # only number_of_uses() (the resource-tracking value) has the bug above.
        character = make_character(intelligence=8, levels={CharacterClass.ARTIFICER: 7})
        table = dict(ArtificerFeatures.FlashofGenius().get_table_description(character))
        assert table["Uses"] == "1 per Long Rest"


# ---------------------------------------------------------------------------
# Psion - homebrew/UA content, no official 2024 table to check numeric
# progressions against. Only the documented (prose-stated) regain cadences
# are checked.
# ---------------------------------------------------------------------------


class TestPsionRegainCadences:
    # Psion has no CharacterClass enum member (Core/Definitions.py only
    # defines PSION_HIT_DIE) - it isn't wired into level_per_class at all, so
    # these regained_on() checks use a plain character; none of them read
    # class level.
    def test_psionic_power_dice_regain_on_short_or_long_rest(self, make_character):
        character = make_character()
        assert (
            PsionFeatures.PsionicPower().regained_on(character)
            == RegainedOn.SHORT_OR_LONG_REST
        )

    def test_psionic_restoration_regains_on_long_rest(self, make_character):
        character = make_character()
        assert (
            PsionFeatures.PsionicRestoration().regained_on(character)
            == RegainedOn.LONG_REST
        )

    def test_psionic_reserves_regains_on_initiative_roll(self, make_character):
        character = make_character()
        assert (
            PsionFeatures.PsionicReserves().regained_on(character)
            == RegainedOn.INITIATIVE_ROLL
        )


class TestClassTableResourcesUseClassLevel:
    """2024 PHB class tables key these resources off that class's own level,
    so dipping into another class must not raise them."""

    @pytest.mark.parametrize(
        "cleric_level, other_levels, expected",
        [
            (2, 0, 2),
            (6, 0, 3),
            (18, 0, 4),
            (5, 13, 2),  # Cleric 5 / Fighter 13: character level 18, still 2 uses
            (17, 3, 3),  # Cleric 17 / Fighter 3: character level 20, not yet 4
        ],
    )
    def test_cleric_channel_divinity(
        self, make_character, cleric_level, other_levels, expected
    ):
        levels = {CharacterClass.CLERIC: cleric_level}
        if other_levels:
            levels[CharacterClass.FIGHTER] = other_levels
        character = make_character(levels=levels)
        assert ClericFeatures.ChannelDivinity().number_of_uses(character) == expected

    @pytest.mark.parametrize(
        "paladin_level, other_levels, expected",
        [(3, 0, 2), (11, 0, 3), (10, 5, 2)],  # Paladin 10 / Sorcerer 5: 2 uses
    )
    def test_paladin_channel_divinity(
        self, make_character, paladin_level, other_levels, expected
    ):
        levels = {CharacterClass.PALADIN: paladin_level}
        if other_levels:
            levels[CharacterClass.SORCERER] = other_levels
        character = make_character(levels=levels)
        assert PaladinFeatures.ChannelDivinity().number_of_uses(character) == expected

    @pytest.mark.parametrize(
        "ranger_level, other_levels, expected",
        # 2024 Ranger table, Favored Enemy: 2/3/4/5/6 at levels 1/5/9/13/17
        [(1, 0, 2), (5, 0, 3), (9, 0, 4), (13, 0, 5), (17, 0, 6), (4, 10, 2)],
    )
    def test_ranger_favored_enemy(
        self, make_character, ranger_level, other_levels, expected
    ):
        levels = {CharacterClass.RANGER: ranger_level}
        if other_levels:
            levels[CharacterClass.ROGUE] = other_levels
        character = make_character(levels=levels)
        assert RangerFeatures.FavoredEnemy().number_of_uses(character) == expected
