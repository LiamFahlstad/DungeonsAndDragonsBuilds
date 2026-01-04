from Definitions import Ability, DiceRollCondition, Skill
from Features.BaseFeatures import CharacterFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AbstractArmor(CharacterFeature):
    """An abstract class for armor features."""

    pass


class LeatherArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(11)
        character_stat_block.combat.change_armor_class_ability(Ability.DEXTERITY)


class StuddedLeatherArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.update_armor_class_base(12)
        character_stat_block.combat.change_armor_class_ability(Ability.DEXTERITY)


class ChainMailArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        str_score = character_stat_block.get_ability_score(Ability.STRENGTH)
        if str_score < 13:
            raise ValueError("Strength ability score needs to be above 13")

        character_stat_block.skills.dice_roll_conditions.update(
            {Skill.STEALTH: DiceRollCondition.DISADVANTAGE}
        )
        character_stat_block.combat.update_armor_class_base(16)
        character_stat_block.combat.change_armor_class_ability(None)


class ShieldArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.combat.increase_armor_class(2)
