"""
Class features with mechanical effects (CharacterContent/Features/ClassFeatures),
checked against the 2024 PHB feature text.

apply_features() mirrors setup_character_stat_block's order: feature.apply,
then worn armor, then feature.apply_after_armor (for armor-conditional rules).
"""

import pytest

from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures
from CharacterContent.Features.ClassFeatures.Bard import BardFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Features.ClassFeatures.Ranger import RangerFeatures
from CharacterContent.Items import Armor
from Core.Definitions import Ability, CharacterClass, DiceRollCondition, Skill
from RunCharacterCreator import BuildSelector


def apply_features(character, features, armors=()):
    for feature in features:
        feature.apply(character)
    for armor in armors:
        armor.apply(character)
    for feature in features:
        feature.apply_after_armor(character)
    return character


class TestUnarmoredDefense:
    def test_barbarian_dex_plus_con(self, make_character):
        character = make_character(dexterity=14, constitution=16)
        apply_features(character, [BarbarianFeatures.UnarmoredDefense()])
        assert character.calculate_armor_class() == 10 + 2 + 3

    def test_barbarian_keeps_it_with_shield(self, make_character):
        character = make_character(dexterity=14, constitution=16)
        apply_features(
            character, [BarbarianFeatures.UnarmoredDefense()], [Armor.ShieldArmor()]
        )
        assert character.calculate_armor_class() == 10 + 2 + 3 + 2

    def test_armor_replaces_it(self, make_character):
        character = make_character(dexterity=14, constitution=16, strength=15)
        apply_features(
            character, [BarbarianFeatures.UnarmoredDefense()], [Armor.PlateArmor()]
        )
        assert character.calculate_armor_class() == 18

    def test_monk_dex_plus_wis(self, make_character):
        character = make_character(dexterity=16, wisdom=14)
        apply_features(character, [MonkFeatures.UnarmoredDefense()])
        assert character.calculate_armor_class() == 10 + 3 + 2


# 2024 Monk table: Unarmored Movement bonus by Monk level.
PHB_UNARMORED_MOVEMENT = {1: 0, 2: 10, 5: 10, 6: 15, 9: 15, 10: 20, 14: 25, 18: 30}


class TestUnarmoredMovement:
    @pytest.mark.parametrize("level,bonus", PHB_UNARMORED_MOVEMENT.items())
    def test_bonus_by_level(self, make_character, level, bonus):
        character = make_character(levels={CharacterClass.MONK: level})
        apply_features(character, [MonkFeatures.UnarmoredMovement()])
        assert character.combat.speed == 30 + bonus

    def test_lost_in_armor(self, make_character):
        character = make_character(levels={CharacterClass.MONK: 10})
        apply_features(
            character, [MonkFeatures.UnarmoredMovement()], [Armor.LeatherArmor()]
        )
        assert character.combat.speed == 30

    def test_lost_with_shield(self, make_character):
        character = make_character(levels={CharacterClass.MONK: 10})
        apply_features(
            character, [MonkFeatures.UnarmoredMovement()], [Armor.ShieldArmor()]
        )
        assert character.combat.speed == 30

    def test_armored_monk_build_regression(self):
        # Kagen (Rogue 1 / Monk 19) wears Leather Armor: no Unarmored Movement.
        data = BuildSelector.get_build("Y2024_Rogue_ShadowMonk_KagenVoidstep").build()
        assert data.setup_character_stat_block().combat.speed == 30


class TestHeavyArmorSpeedFeatures:
    @pytest.mark.parametrize(
        "feature_class",
        [BarbarianFeatures.FastMovementBonus, RangerFeatures.Roving],
        ids=["FastMovement", "Roving"],
    )
    @pytest.mark.parametrize(
        "armor,expected",
        [(None, 40), (Armor.BreastplateArmor, 40), (Armor.PlateArmor, 30)],
        ids=["unarmored", "medium", "heavy"],
    )
    def test_plus_ten_unless_heavy(
        self, make_character, feature_class, armor, expected
    ):
        character = make_character(strength=15)
        armors = [armor()] if armor else []
        apply_features(character, [feature_class()], armors)
        assert character.combat.speed == expected


class TestPrimalKnowledge:
    def test_grants_chosen_proficiency(self, make_character):
        character = make_character()
        apply_features(
            character, [BarbarianFeatures.PrimalKnowledgeSkillProficiency(Skill.NATURE)]
        )
        assert character.is_proficient_in_skill(Skill.NATURE)

    @pytest.mark.parametrize(
        "skill,ability",
        [
            (Skill.PERCEPTION, Ability.WISDOM),
            (Skill.NATURE, Ability.INTELLIGENCE),
            (Skill.ANIMAL_HANDLING, Ability.WISDOM),
            (Skill.INTIMIDATION, Ability.CHARISMA),
        ],
    )
    def test_skills_keep_normal_ability_outside_rage(
        self, make_character, skill, ability
    ):
        # Strength substitution is only while raging - not on the sheet.
        character = make_character()
        apply_features(
            character,
            [BarbarianFeatures.PrimalKnowledgeSkillProficiency(Skill.PERCEPTION)],
        )
        assert character.get_skill_ability(skill) == ability

    def test_skill_outside_pool_rejected(self):
        with pytest.raises(ValueError):
            BarbarianFeatures.PrimalKnowledgeSkillProficiency(Skill.ARCANA)


class TestOtherFeatures:
    def test_jack_of_all_trades_half_pb_rounded_down(self, make_character):
        character = make_character(levels={CharacterClass.BARD: 5})  # PB 3
        character.skills.add_skill_proficiency(Skill.PERFORMANCE)
        apply_features(character, [BardFeatures.JackOfAllTrades()])
        assert character.get_skill_modifier(Skill.ARCANA) == 1
        assert character.get_skill_modifier(Skill.PERFORMANCE) == 3

    @pytest.mark.parametrize("cha,bonus", [(16, 3), (10, 1), (8, 1)])
    def test_aura_of_protection_min_one(self, make_character, cha, bonus):
        character = make_character(charisma=cha)
        apply_features(character, [PaladinFeatures.AuraOfProtection()])
        for ability in Ability:
            base = character.get_ability_modifier(ability)
            assert character.get_saving_throw_modifier(ability) == base + bonus

    @pytest.mark.parametrize("wis,bonus", [(16, 3), (8, 1)])
    def test_thaumaturge_arcana_and_religion(self, make_character, wis, bonus):
        character = make_character(wisdom=wis)
        apply_features(character, [ClericFeatures.DivineOrderThaumaturge("Guidance")])
        assert character.get_skill_modifier(Skill.ARCANA) == bonus
        assert character.get_skill_modifier(Skill.RELIGION) == bonus
        assert character.get_skill_modifier(Skill.HISTORY) == 0

    def test_danger_sense_dex_save_advantage(self, make_character):
        character = make_character()
        apply_features(character, [BarbarianFeatures.DangerSense()])
        assert character.has_advantage_in_saving_throw(Ability.DEXTERITY)
        assert not character.has_advantage_in_saving_throw(Ability.WISDOM)

    def test_feral_instinct_initiative_advantage(self, make_character):
        character = make_character()
        apply_features(character, [BarbarianFeatures.FeralInstinct()])
        assert character.initiative_roll_condition == DiceRollCondition.ADVANTAGE

    def test_disciplined_survivor_all_saves(self, make_character):
        character = make_character()
        apply_features(character, [MonkFeatures.DisciplinedSurvivorSavingThrows()])
        assert all(character.is_proficient_in_saving_throw(a) for a in Ability)
