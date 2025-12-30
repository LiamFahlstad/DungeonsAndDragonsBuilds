from Definitions import Ability, DiceRollCondition, Skill
from Features.BaseFeatures import CharacterFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AbstractArmor(CharacterFeature):
    """An abstract class for armor features."""

    pass


class LeatherArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        dex_mod = character_stat_block.get_ability_modifier(Ability.DEXTERITY)
        character_stat_block.combat.update_armor_class(11 + dex_mod, pick_max=True)


class StuddedLeatherArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        dex_mod = character_stat_block.get_ability_modifier(Ability.DEXTERITY)
        character_stat_block.combat.update_armor_class(
            12 + dex_mod,
            pick_max=True,
        )


class ChainMailArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        str_score = character_stat_block.get_ability_score(Ability.STRENGTH)
        if str_score < 13:
            raise ValueError("Strength ability score needs to be above 13")

        character_stat_block.skills.dice_roll_conditions.update(
            {Skill.STEALTH: DiceRollCondition.DISADVANTAGE}
        )
        character_stat_block.combat.update_armor_class(16, pick_max=True)


class ShieldArmor(AbstractArmor):
    def modify(self, character_stat_block: CharacterStatBlock):
        current_armor_class = character_stat_block.combat.armor_class
        character_stat_block.combat.update_armor_class(
            current_armor_class + 2, pick_max=True
        )
