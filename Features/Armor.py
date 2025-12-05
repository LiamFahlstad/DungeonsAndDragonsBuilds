from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, Skill, DiceRollCondition
from Features.BaseFeatures import CharacterFeature


class AbstractArmor(CharacterFeature):
    """An abstract class for armor features."""

    pass


class LeatherArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.armor_class_without_bonus = 11
        dex_mod = character_stat_block.get_ability_modifier(Ability.DEXTERITY)
        character_stat_block.combat.armor_class_bonus += dex_mod


class StuddedLeatherArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.armor_class_without_bonus = 12
        dex_mod = character_stat_block.get_ability_modifier(Ability.DEXTERITY)
        character_stat_block.combat.armor_class_bonus += dex_mod


class ChainMailArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        str_score = character_stat_block.get_ability_score(Ability.STRENGTH)
        if str_score < 13:
            raise ValueError("Strength ability score needs to be above 13")

        character_stat_block.skills.dice_roll_conditions.update(
            {Skill.STEALTH: DiceRollCondition.DISADVANTAGE}
        )
        character_stat_block.combat.armor_class_without_bonus = 16


class ShieldArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.armor_class_bonus += 2
