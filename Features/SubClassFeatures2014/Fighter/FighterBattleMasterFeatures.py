from Core.Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class CombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Combat Superiority", origin="Battle Master Fighter Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if character_stat_block.character_level < 7:
            number_of_superiority_die = 4
        elif character_stat_block.character_level < 15:
            number_of_superiority_die = 5
        else:
            number_of_superiority_die = 6

        if character_stat_block.character_level < 10:
            superiority_die = "1d8"
        elif character_stat_block.character_level < 18:
            superiority_die = "1d10"
        else:
            superiority_die = "1d12"

        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        str_mod = character_stat_block.get_ability_modifier(Ability.STRENGTH)
        dex_mod = character_stat_block.get_ability_modifier(Ability.DEXTERITY)
        maneuver_save_dc = 8 + proficiency_bonus + max(str_mod, dex_mod)

        description = (
            "When you choose this archetype at 3rd level, you learn maneuvers that are fueled by special dice called superiority dice.\n"
            "\n"
            "Maneuvers. You learn three maneuvers of your choice. Many maneuvers enhance an attack in some way. You can use only one maneuver per attack. You learn two additional maneuvers of your choice at 7th, 10th, and 15th level. Each time you learn new maneuvers, you can also replace one maneuver you know with a different one.\n"
            "\n"
            f"Superiority Dice. You have {number_of_superiority_die} superiority dice, which are {superiority_die}s. A superiority die is expended when you use it. You regain all of your expended superiority dice when you finish a short or long rest. You gain another superiority die at 7th level and one more at 15th level.\n"
            "\n"
            f"Saving Throws. Some of your maneuvers require your target to make a saving throw to resist the maneuver's effects. Maneuver save DC = 8 + your proficiency bonus + your Strength or Dexterity modifier (your choice) = {maneuver_save_dc}\n"
            "\n"
            "Maneuvers:"
        )
        return StringUtils.add_boxes(
            description, number_of_superiority_die, regain_all_on="short or long rest"
        )


class StudentOfWar(Feature):
    def __init__(self):
        super().__init__(name="Student of War", origin="Battle Master Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 3rd level, you gain proficiency with one type of artisan's tools of your choice."
        return description


class KnowYourEnemy(Feature):
    def __init__(self):
        super().__init__(name="Know Your Enemy", origin="Battle Master Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 7th level, if you spend at least 1 minute observing or interacting with another creature outside combat, you can learn certain information about its capabilities compared to your own. The DM tells you if the creature is your equal, superior, or inferior in regard to two of the following characteristics of your choice:\n"
            "    * Strength score\n"
            "    * Dexterity score\n"
            "    * Constitution score\n"
            "    * Armor Class\n"
            "    * Current hit points\n"
            "    * Total class levels, if any\n"
            "    * Fighter class levels, if any"
        )
        return description


class ImprovedCombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Combat Superiority", origin="Battle Master Fighter Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 10th level, your superiority dice turn into d10s."
        return description


class Relentless(Feature):
    def __init__(self):
        super().__init__(name="Relentless", origin="Battle Master Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 15th level, when you roll initiative and have no superiority dice remaining, you regain 1 superiority die."
        return description


class GreaterCombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Combat Superiority", origin="Battle Master Fighter Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 18th level, your superiority dice turn into d12s."
        return description
