from Core.Definitions import DiceRollCondition, FIGHTER_HIT_DIE, Skill
from Model.Content.Feature import Feature, FeatureTarget
from Model.Content.Improvements import InitiativeRollCondition, SkillRollCondition
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class ImprovedCritical(Feature):
    def __init__(self):
        super().__init__(name="Improved Critical", origin="Champion Fighter Level 3")

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Attacks", "Attack rolls with weapons and Unarmed Strikes"),
                    (
                        "Critical Hit",
                        "On a 19 or 20 on the d20 (18-20 from Fighter level 15, Superior Critical)",
                    ),
                )
            ),
        ]

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
            Skill.ATHLETICS, DiceRollCondition.ADVANTAGE
        )

    def apply(self, ledger_writer: LedgerWriter) -> None:
        self._initiative.apply(ledger_writer)
        self._athletics.apply(ledger_writer)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Advantage",
                        "On Initiative rolls and Strength (Athletics) checks",
                    ),
                    (
                        "After a Critical Hit",
                        "Immediately move up to half your Speed without provoking Opportunity Attacks",
                    ),
                )
            ),
        ]

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

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Feat", "Another Fighting Style feat of your choice"),))]

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

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("The thrill of battle drives you toward victory."),
            Facts(
                (
                    (
                        "When",
                        "During combat, you start your turn without Heroic Inspiration",
                    ),
                    ("Effect", "Give yourself Heroic Inspiration"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "The thrill of battle drives you toward victory. During combat, you can give yourself Heroic Inspiration whenever you start your turn without it."
        return description


class SuperiorCritical(Feature):
    def __init__(self):
        super().__init__(name="Superior Critical", origin="Champion Fighter Level 15")

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Critical Hit", "On a roll of 18-20 on the d20"),
                    ("Applies to", "Attack rolls with weapons and Unarmed Strikes"),
                )
            ),
        ]

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

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Defy Death",
                        "Advantage on Death Saving Throws, and a roll of 18-20 counts as a 20",
                    ),
                    (
                        "Heroic Rally",
                        "At the start of each of your turns, if you're Bloodied and have at least 1 Hit Point, regain 5 + Constitution modifier Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You attain the pinnacle of resilience in battle, giving you these benefits.\n"
            "Defy Death. You have Advantage on Death Saving Throws. Moreover, when you roll 18-20 on a Death Saving Throw, you gain the benefit of rolling a 20 on it.\n"
            "Heroic Rally. At the start of each of your turns, you regain Hit Points equal to 5 plus your Constitution modifier if you are Bloodied and have at least 1 Hit Point."
        )
        return description
