from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiencies", origin="College of Swords Bard Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you join the College of Swords at 3rd level, you gain proficiency with medium armor and the scimitar.\n"
            "\n"
            "If you're proficient with a simple or martial melee weapon, you can use it as a spellcasting focus for your bard spells."
        )
        return description


class BladeFlourish(Feature):
    def __init__(self):
        super().__init__(name="Blade Flourish", origin="College of Swords Bard Level 3", activation=FeatureActivation(duration="Until Start of Next Turn"), usage_tags=["damage", "buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, you learn to conduct impressive displays of martial prowess and speed.\n"
            "\n"
            "Whenever you take the Attack action on your turn, your walking speed increases by 10 feet until the end of the turn, and if a weapon attack that you make as part of this action hits a creature, you can use one of the following Blade Flourish options of your choice. You can use only one Blade Flourish option per turn.\n"
            "\n"
            "Defensive Flourish. You can expend one use of your Bardic Inspiration to cause the weapon to deal extra damage to the target you hit. The damage equals the number you roll on the Bardic Inspiration die. You also add the number rolled to your AC until the start of your next turn.\n"
            "\n"
            "Slashing Flourish. You can expend one use of your Bardic Inspiration to cause the weapon to deal extra damage to the target you hit and to any other creature of your choice that you can see within 5 feet of you. The damage equals the number you roll on the Bardic Inspiration die.\n"
            "\n"
            "Mobile Flourish. You can expend one use of your Bardic Inspiration to cause the weapon to deal extra damage to the target you hit. The damage equals the number you roll on the Bardic Inspiration die. You can also push the target up to 5 feet away from you, plus a number of feet equal to the number you roll on that die. You can then immediately use your reaction to move up to your walking speed to an unoccupied space within 5 feet of the target."
        )
        return description


class ExtraAttack(Feature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="College of Swords Bard Level 6", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 6th level, you can attack twice, instead of once, whenever you take the Attack action on your turn."
        )
        return description


class MastersFlourish(Feature):
    def __init__(self):
        super().__init__(name="Master's Flourish", origin="College of Swords Bard Level 14", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 14th level, whenever you use a Blade Flourish option, you can roll a d6 and use it instead of expending a Bardic Inspiration die."
        )
        return description
