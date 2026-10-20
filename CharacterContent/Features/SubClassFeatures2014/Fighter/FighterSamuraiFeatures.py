from typing import Optional

from Core.Definitions import Ability, CharacterClass, Skill
from Model.Content.Feature import (
    FeatureUses,
    Feature,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import (
    SavingThrowProficiencyChoice,
    SkillBonus,
    SkillProficiencyChoice,
)
from Model.Ledger.LedgerWriter import LedgerWriter
from Utils import StringUtils
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class BonusProficiency(Feature):
    def __init__(self, skill: Optional[Skill] = None, language: Optional[str] = None):
        super().__init__(
            name="Bonus Proficiency",
            origin="Samurai Fighter Level 3",
            passive=True,
        )
        self._skill = skill
        self._language = language
        self._proficiency_choice = None
        if skill is not None:
            self._proficiency_choice = SkillProficiencyChoice(
                [skill],
                [Skill.HISTORY, Skill.INSIGHT, Skill.PERFORMANCE, Skill.PERSUASION],
                count=1,
                error_prefix="Samurai Bonus Proficiency",
            )

    def apply(self, ledger_writer: LedgerWriter):
        if self._proficiency_choice is not None:
            self._proficiency_choice.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        if self._skill is not None:
            return [Facts((("Skill proficiency", self._skill.value),))]
        if self._language is not None:
            return [Facts((("Language", self._language),))]
        return [
            Paragraph("Choose one:"),
            Facts(
                (
                    (
                        "Skill proficiency",
                        "History, Insight, Performance or Persuasion",
                    ),
                    ("Or a language", "One language of your choice"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain proficiency in one of the following skills of your choice: History, Insight, Performance, or Persuasion. Alternatively, you learn one language of your choice."
        if self._skill is not None:
            description += f"\nYou chose proficiency in {self._skill.value}."
        elif self._language is not None:
            description += f"\nYou chose the {self._language} language."
        return description


class FightingSpirit(Feature):
    def __init__(self):
        super().__init__(
            name="Fighting Spirit",
            origin="Samurai Fighter Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until End of Current Turn",
            ),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=3, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Bonus Action on your turn"),
                    (
                        "Effect",
                        "Advantage on weapon attack rolls until the end of the turn",
                    ),
                    ("Temporary HP", "5; 10 at Fighter level 10; 15 at 15"),
                    ("Uses", "Three per long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your intensity in battle can shield you and help you strike true. As a bonus action on your turn, you can give yourself advantage on all weapon attack rolls until the end of the current turn. When you do so, you also gain temporary hit points.\n"
            "The number of temporary hit points depends on your fighter level: 5 at 3rd level, 10 at 10th level, and 15 at 15th level.\n"
            "You can use this feature three times. You regain all expended uses of it when you finish a long rest."
        )
        level = character.get_class_level(CharacterClass.FIGHTER)
        description += f"\nRight now: {5 + 5 * (level >= 10) + 5 * (level >= 15)} temporary hit points."
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class ElegantCourtier(Feature):
    def __init__(self, alternate_saving_throw: Optional[Ability] = None):
        super().__init__(
            name="Elegant Courtier",
            origin="Samurai Fighter Level 7",
            usage_tags=["buff"],
        )
        self._alternate_saving_throw = alternate_saving_throw
        ability = (
            alternate_saving_throw
            if alternate_saving_throw is not None
            else Ability.WISDOM
        )
        self._proficiency_choice = SavingThrowProficiencyChoice(
            [ability],
            [Ability.WISDOM, Ability.INTELLIGENCE, Ability.CHARISMA],
            count=1,
            error_prefix="Elegant Courtier",
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._proficiency_choice.apply(ledger_writer)
        # "Whenever you make a Charisma (Persuasion) check, you gain a bonus
        # to the check equal to your Wisdom modifier."
        SkillBonus(Skill.PERSUASION, lambda cs: cs.get_wisdom_modifier()).apply(
            ledger_writer
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        saving_throw = (
            f"{self._alternate_saving_throw.value} (you already had Wisdom)"
            if self._alternate_saving_throw is not None
            else "Wisdom; if you already have it, Intelligence or Charisma (your choice)"
        )
        return [
            Paragraph(
                "Your discipline and attention to detail let you excel in social situations."
            ),
            Facts(
                (
                    ("Charisma (Persuasion)", "+ Wisdom modifier to the check"),
                    ("Saving throw proficiency", saving_throw),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your discipline and attention to detail allow you to excel in social situations. Whenever you make a Charisma (Persuasion) check, you gain a bonus to the check equal to your Wisdom modifier.\n"
            "Your self-control also causes you to gain proficiency in Wisdom saving throws. If you already have this proficiency, you instead gain proficiency in Intelligence or Charisma saving throws (your choice)."
        )
        if self._alternate_saving_throw is not None:
            description += f"\nYou already had Wisdom saving throw proficiency, so you chose {self._alternate_saving_throw.value} instead."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class TirelessSpirit(Feature):
    def __init__(self):
        super().__init__(name="Tireless Spirit", origin="Samurai Fighter Level 10")

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.INITIATIVE_ROLL

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You roll Initiative with no uses of Fighting Spirit left",
                    ),
                    ("Effect", "Regain one use"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you roll initiative and have no uses of Fighting Spirit remaining, you regain one use."
        return description


class RapidStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Rapid Strike",
            origin="Samurai Fighter Level 15",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Trade accuracy for swift strikes."),
            Facts(
                (
                    (
                        "Trigger",
                        "You take the Attack action on your turn and have Advantage on an attack roll against a target",
                    ),
                    (
                        "Effect",
                        "Forgo the Advantage to make an additional weapon attack against that target, as part of the same action",
                    ),
                    ("Frequency", "Once per turn"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You learn to trade accuracy for swift strikes. If you take the Attack action on your turn and have advantage on an attack roll against one of the targets, you can forgo the advantage for that roll to make an additional weapon attack against that target, as part of the same action. You can do so no more than once per turn."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class StrengthBeforeDeath(Feature):
    def __init__(self):
        super().__init__(
            name="Strength Before Death",
            origin="Samurai Fighter Level 18",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "Damage reduces you to 0 hit points"),
                    (
                        "Effect",
                        "Delay falling unconscious and take an extra turn right away",
                    ),
                    (
                        "During it",
                        "Damage at 0 hit points causes death saving throw failures as normal; three failures still kill you",
                    ),
                    (
                        "Afterwards",
                        "You fall unconscious if you're still at 0 hit points",
                    ),
                    ("Limit", "Once per long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your fighting spirit can delay the grasp of death. If you take damage that reduces you to 0 hit points, you can use your reaction to delay falling unconscious, and you can immediately take an extra turn. While you have 0 hit points during that extra turn, taking damage causes death saving throw failures as normal, and three death saving throw failures can still kill you. When the extra turn ends, you fall unconscious if you still have 0 hit points.\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
