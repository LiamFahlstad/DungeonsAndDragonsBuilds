from Core.Definitions import Ability, FIGHTER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class SuperiorityDice(Feature):
    def __init__(self):
        self.maneuvers = []
        super().__init__(
            name="Superiority Dice", origin="Battle Master Fighter Level 3"
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

        str_mod = character_stat_block.get_ability_modifier(Ability.STRENGTH)
        dex_mod = character_stat_block.get_ability_modifier(Ability.DEXTERITY)
        saving_throw = (
            8 + max(str_mod, dex_mod) + character_stat_block.get_proficiency_bonus()
        )
        base_text = (
            f"These are {superiority_die}s, and you can expend them to fuel your maneuvers.\n"
            "You regain all expended superiority dice when you finish a short or long rest.\n"
            f"Number of Superiority Dice: {number_of_superiority_die}\n"
            f"If a maneuver requires a saving throw, the DC equals {saving_throw}.\n"
            f"Maneuvers:"
        )

        return StringUtils.add_boxes(
            base_text, number_of_superiority_die, regain_all_on="short or long rest"
        )


class CombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Combat Superiority", origin="Battle Master Fighter Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your experience on the battlefield has refined your fighting techniques. You learn maneuvers that are fueled by special dice called Superiority Dice.\n"
            "Maneuvers. You learn three maneuvers of your choice from the “Maneuver Options” section later in this subclass’s description. Many maneuvers enhance an attack in some way. You can use only one maneuver per attack.\n"
            "You learn two additional maneuvers of your choice when you reach Fighter levels 7, 10, and 15. Each time you learn new maneuvers, you can also replace one maneuver you know with a different one.\n"
            "Superiority Dice. You have four Superiority Dice, which are d8s. A Superiority Die is expended when you use it. You regain all expended Superiority Dice when you finish a Short or Long Rest.\n"
            "You gain an additional Superiority Die when you reach Fighter levels 7 (five dice total) and 15 (six dice total).\n"
            "Saving Throws. If a maneuver requires a saving throw, the DC equals 8 plus your Strength or Dexterity modifier (your choice) and Proficiency Bonus."
        )
        return description


class StudentOfWar(Feature):
    def __init__(self):
        super().__init__(name="Student of War", origin="Battle Master Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with one type of Artisan’s Tools of your choice, and you gain proficiency in one skill of your choice from the skills available to Fighters at level 1."
        return description


class KnowYourEnemy(Feature):
    def __init__(self):
        super().__init__(name="Know Your Enemy", origin="Battle Master Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can discern certain strengths and weaknesses of a creature you can see within 30 feet of yourself; you know whether that creature has any Immunities, Resistances, or Vulnerabilities, and if the creature has any, you know what they are.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest. You can also restore a use of the feature by expending one Superiority Die (no action required)."
        )
        return description


class ImprovedCombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Combat Superiority", origin="Battle Master Fighter Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Superiority Die becomes a d10."
        return description


class Relentless(Feature):
    def __init__(self):
        super().__init__(name="Relentless", origin="Battle Master Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Once per turn, when you use a maneuver, you can roll 1d8 and use the number rolled instead of expending a Superiority Die."
        return description


class UltimateCombatSuperiority(Feature):
    def __init__(self):
        super().__init__(
            name="Ultimate Combat Superiority", origin="Battle Master Fighter Level 18"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Superiority Die becomes a d12."
        return description
