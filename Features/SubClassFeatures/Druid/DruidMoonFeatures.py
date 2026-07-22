
from Core.Definitions import Ability, DRUID_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class CircleForms(Feature):
    def __init__(self):
        super().__init__(name="Circle Forms", origin="Circle of the Moon Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can channel lunar magic when you assume a Wild Shape form, granting you the benefits below.\n"
            "Challenge Rating. The maximum Challenge Rating for the form equals your Druid level divided by 3 (round down).\n"
            "Armor Class. Until you leave the form, your AC equals 13 plus your Wisdom modifier if that total is higher than the Beast's AC.\n"
            "Temporary Hit Points. You gain a number of Temporary Hit Points equal to three times your Druid level."
        )
        return description


class CircleOfTheMoonSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Circle of the Moon Spells", origin="Circle of the Moon Druid Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Druid level specified in the Circle of the Moon Spells table, you thereafter always have the listed spells prepared.\n"
            "In addition, you can cast the spells from this feature while you're in a Wild Shape form."
        )
        return description


class ImprovedCircleForms(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Circle Forms", origin="Circle of the Moon Druid Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "While in a Wild Shape form, you gain the following benefits.\n"
            "Lunar Radiance. Each of your attacks in a Wild Shape form can deal its normal damage type or Radiant damage. You make this choice each time you hit with those attacks.\n"
            "Increased Toughness. You can add your Wisdom modifier to your Constitution saving throws."
        )
        return description


class MoonlightStep(Feature):
    def __init__(self):
        super().__init__(
            name="Moonlight Step", origin="Circle of the Moon Druid Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_modifier = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wisdom_modifier)
        description = (
            "You magically transport yourself, reappearing amid a burst of moonlight. As a Bonus Action, you teleport up to 30 feet to an unoccupied space you can see, and you have Advantage on the next attack roll you make before the end of this turn.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest. You can also regain uses by expending a level 2+ spell slot for each use you want to restore (no action required)."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class LunarForm(Feature):
    def __init__(self):
        super().__init__(name="Lunar Form", origin="Circle of the Moon Druid Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The power of the moon suffuses you, granting you the following benefits.\n"
            "Improved Lunar Radiance. Once per turn, you can deal an extra 2d10 Radiant damage to a target you hit with a Wild Shape form's attack.\n"
            "Shared Moonlight. Whenever you use Moonlight Step, you can also teleport one willing creature. That creature must be within 10 feet of you, and you teleport it to an unoccupied space you can see within 10 feet of your destination space."
        )
        return description
