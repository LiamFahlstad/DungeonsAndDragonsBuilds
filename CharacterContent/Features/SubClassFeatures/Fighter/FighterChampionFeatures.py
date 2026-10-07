from Core.Definitions import DiceRollCondition, FIGHTER_HIT_DIE, Skill
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureTarget
from CharacterContent.Features.Core.Improvements import (
    InitiativeRollCondition,
    SkillRollCondition,
)
from Model.Effects import Effects
from Model.View import CharacterView


class ImprovedCritical(Feature):
    def __init__(self):
        super().__init__(name="Improved Critical", origin="Champion Fighter Level 3")

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = "Your attack rolls with weapons and Unarmed Strikes can score a Critical Hit on a roll of 19 or 20 on the d20."
        return description


class RemarkableAthlete(Feature):
    def __init__(self):
        super().__init__(
            name="Remarkable Athlete",
            origin="Champion Fighter Level 3",
            usage_tags=["buff"],
        )
        self._initiative = InitiativeRollCondition(DiceRollCondition.ADVANTAGE)
        self._athletics = SkillRollCondition(
            Skill.ATHLETICS, DiceRollCondition.ADVANTAGE, reason="Remarkable Athlete"
        )

    def apply(self, effects: Effects) -> None:
        self._initiative.apply(effects)
        self._athletics.apply(effects)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
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

    def get_description(self, character: CharacterView) -> str:
        description = "You gain another Fighting Style feat of your choice."
        return description


class HeroicWarrior(Feature):
    def __init__(self):
        super().__init__(
            name="Heroic Warrior",
            origin="Champion Fighter Level 10",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = "The thrill of battle drives you toward victory. During combat, you can give yourself Heroic Inspiration whenever you start your turn without it."
        return description


class SuperiorCritical(Feature):
    def __init__(self):
        super().__init__(name="Superior Critical", origin="Champion Fighter Level 15")

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = "Your attack rolls with weapons and Unarmed Strikes can now score a Critical Hit on a roll of 18-20 on the d20."
        return description


class Survivor(Feature):
    def __init__(self):
        super().__init__(
            name="Survivor",
            origin="Champion Fighter Level 18",
            usage_tags=["buff", "heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You attain the pinnacle of resilience in battle, giving you these benefits.\n"
            "Defy Death. You have Advantage on Death Saving Throws. Moreover, when you roll 18-20 on a Death Saving Throw, you gain the benefit of rolling a 20 on it.\n"
            "Heroic Rally. At the start of each of your turns, you regain Hit Points equal to 5 plus your Constitution modifier if you are Bloodied and have at least 1 Hit Point."
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        from Core.Definitions import Ability

        con_modifier = character.get_constitution_modifier()
        return [
            ("Defy Death", "Advantage on Death Saving Throws; rolls 18-20 count as 20"),
            (
                "Heroic Rally",
                f"Start of turn: regain 5 + {con_modifier} HP (if Bloodied and HP ≥ 1)",
            ),
        ]
