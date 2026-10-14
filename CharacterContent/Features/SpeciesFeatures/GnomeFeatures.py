from Core.Definitions import Ability, CreatureSize, Sense
from Model.Content.Feature import Feature, FeatureUses, RegainedOn, FeatureTarget
from Model.Content.Improvements import SavingThrowAdvantage, GrantSense
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import PROFICIENCY_BONUS_GAINED_AT, MAX_PROFICIENCY_BONUS
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph

SPEED = 30  # Given by your species
SIZE = CreatureSize.SMALL  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Gnome Trait", passive=True)
        self._sense = GrantSense(Sense.DARKVISION, 60)

    def apply(self, ledger_writer: LedgerWriter):
        self._sense.apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        return "You have Darkvision with a range of 60 feet."


class GnomishCunning(Feature):
    def __init__(self):
        super().__init__(
            name="Gnomish Cunning",
            origin="Gnome Trait",
            passive=True,
            usage_tags=["buff"],
        )
        self._advantage = SavingThrowAdvantage(
            [Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA]
        )

    def apply(self, ledger_writer: LedgerWriter) -> None:
        self._advantage.apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        return "You have Advantage on Intelligence, Wisdom, and Charisma saving throws."


class ForestGnomeSpeakWithAnimals(Feature):
    def __init__(self):
        super().__init__(
            name="Forest Gnome Speak with Animals",
            origin="Gnomish Lineage Forest Gnome Trait",
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=PROFICIENCY_BONUS_GAINED_AT,
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Facts(
                (
                    (
                        "Speak with Animals",
                        "Always prepared. Cast it without a spell slot Proficiency Bonus times per Long Rest, or with your spell slots.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        text = "You also always have the Speak with Animals spell prepared. You can cast it without a spell slot a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest. You can also use any spell slots you have to cast the spell."
        return text

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()


class RockGnomePrestidigitation(Feature):
    def __init__(self):
        super().__init__(
            name="Rock Gnome Prestidigitation",
            origin="Gnomish Lineage Rock Gnome Trait",
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "You know Mending and Prestidigitation, and you can build little clockwork devices."
            ),
            Facts(
                (
                    (
                        "Build",
                        "Spend 10 minutes casting Prestidigitation: a Tiny clockwork device (AC 5, 1 HP), such as a toy, fire starter or music box",
                    ),
                    (
                        "Function",
                        "Pick one Prestidigitation effect (and one option within it, e.g. ignite or extinguish, not both)",
                    ),
                    (
                        "Activate",
                        "You or another creature takes a Bonus Action to touch it",
                    ),
                    ("Limit", "Three devices at a time"),
                    (
                        "Lasts",
                        "8 hours, or until you dismantle it with a touch (Utilize action)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        return "You know the Mending and Prestidigitation cantrips. In addition, you can spend 10 minutes casting Prestidigitation to create a Tiny clockwork device (AC 5, 1 HP), such as a toy, fire starter, or music box. When you create the device, you determine its function by choosing one effect from Prestidigitation; the device produces that effect whenever you or another creature takes a Bonus Action to activate it with a touch. If the chosen effect has options within it, you choose one of those options for the device when you create it. For example, if you choose the spell's ignite-extinguish effect, you determine whether the device ignites or extinguishes fire; the device doesn't do both. You can have three such devices in existence at a time, and each falls apart 8 hours after its creation or when you dismantle it with a touch as a Utilize action."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT
