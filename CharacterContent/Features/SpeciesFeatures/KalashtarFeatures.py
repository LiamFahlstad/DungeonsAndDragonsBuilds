from Core.Definitions import Ability, DamageType, Skill
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.Content.Improvements import DamageResistance, SavingThrowAdvantage
from Model.Ledger.LedgerWriter import LedgerWriter
from Utils import StringUtils
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts

SPEED = 30  # Given by your species


class DualMind(Feature):
    def __init__(self):
        super().__init__(
            name="Dual Mind",
            origin="Kalashtar Trait",
            passive=True,
            usage_tags=["buff"],
        )
        self._advantage = SavingThrowAdvantage([Ability.WISDOM, Ability.CHARISMA])

    def apply(self, ledger_writer: LedgerWriter):
        self._advantage.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Advantage", "On Wisdom and Charisma saving throws"),))]

    def get_description(self, character: CharacterView) -> str:
        return "You have Advantage on Wisdom and Charisma saving throws."


class MentalDiscipline(Feature):
    def __init__(self):
        super().__init__(
            name="Mental Discipline",
            origin="Kalashtar Trait",
            passive=True,
            usage_tags=["buff"],
        )
        self._resistance = DamageResistance(DamageType.PSYCHIC)

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [Facts((("Resistance", "Psychic damage"),))]

    def get_description(self, character: CharacterView) -> str:
        return "You have Resistance to Psychic damage."


class MindLink(Feature):
    def __init__(self):
        super().__init__(
            name="Mind Link",
            origin="Kalashtar Trait",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="1 Hour",
                range="10 Feet Per Character Level",
            ),
            usage_tags=["buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Telepathy", "Range of 10 feet x your character level"),
                    (
                        "Two-way link",
                        "While speaking telepathically to a creature, take a Magic action to let it reply telepathically for 1 hour, or until you end it with another Magic action",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        character_level = character.character_level
        range_feet = 10 * character_level
        return (
            f"You have telepathy with a range in feet equal to 10 times your level ({range_feet} feet). "
            "When you're using this trait to speak telepathically to a creature, you can take a Magic action "
            "to give that creature the ability to speak telepathically with you for 1 hour or until you take "
            "another Magic action to end this effect."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class SeveredFromDreams(Feature):
    def __init__(self):
        super().__init__(
            name="Severed from Dreams",
            origin="Kalashtar Trait",
            activation=FeatureActivation(duration="Until Next Long Rest"),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Dreamless", "You can't be targeted by the Dream spell"),
                    (
                        "Skill",
                        "After each Long Rest, gain proficiency in a skill of your choice until your next Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return (
            "You can't be the target of the Dream spell. "
            "In addition, when you finish a Long Rest, you gain proficiency in one skill of your choice. "
            "This proficiency lasts until you finish another Long Rest."
        )
