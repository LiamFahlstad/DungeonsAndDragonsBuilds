from Definitions import DiceRollCondition, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import InitiativeRollCondition, SkillRollCondition
from StatBlocks.CharacterStatBlock import CharacterStatBlock

FIGHTER_HIT_DIE = 10


class ImprovedCritical(Feature):
    def __init__(self):
        super().__init__(name="Improved Critical", origin="Champion Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your attack rolls with weapons and Unarmed Strikes can score a Critical Hit on a roll of 19 or 20 on the d20."
        return description


class RemarkableAthlete(Feature):
    def __init__(self):
        super().__init__(name="Remarkable Athlete", origin="Champion Fighter Level 3")
        self._initiative = InitiativeRollCondition(DiceRollCondition.ADVANTAGE)
        self._athletics = SkillRollCondition(
            Skill.ATHLETICS, DiceRollCondition.ADVANTAGE, reason="Remarkable Athlete"
        )

    def apply(self, character_stat_block: CharacterStatBlock) -> None:
        self._initiative.apply(character_stat_block)
        self._athletics.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Thanks to your athleticism, you have Advantage on Initiative rolls and Strength (Athletics) checks.\n"
            "In addition, immediately after you score a Critical Hit, you can move up to half your Speed without provoking Opportunity Attacks."
        )
        return description


class AdditionalFightingStyle(Feature):
    def __init__(self):
        super().__init__(
            name="Additional Fighting Style", origin="Champion Fighter Level 7"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain another Fighting Style feat of your choice."
        return description


class HeroicWarrior(Feature):
    def __init__(self):
        super().__init__(name="Heroic Warrior", origin="Champion Fighter Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The thrill of battle drives you toward victory. During combat, you can give yourself Heroic Inspiration whenever you start your turn without it."
        return description


class SuperiorCritical(Feature):
    def __init__(self):
        super().__init__(name="Superior Critical", origin="Champion Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your attack rolls with weapons and Unarmed Strikes can now score a Critical Hit on a roll of 18-20 on the d20."
        return description


class Survivor(Feature):
    def __init__(self):
        super().__init__(name="Survivor", origin="Champion Fighter Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You attain the pinnacle of resilience in battle, giving you these benefits.\n"
            "Defy Death. You have Advantage on Death Saving Throws. Moreover, when you roll 18-20 on a Death Saving Throw, you gain the benefit of rolling a 20 on it.\n"
            "Heroic Rally. At the start of each of your turns, you regain Hit Points equal to 5 plus your Constitution modifier if you are Bloodied and have at least 1 Hit Point."
        )
        return description
