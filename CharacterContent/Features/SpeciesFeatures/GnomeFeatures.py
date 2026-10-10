from Core.Definitions import Ability, CreatureSize, Sense
from Model.Content.Feature import Feature, FeatureUses, RegainedOn, FeatureTarget
from Model.Content.Improvements import SavingThrowAdvantage, GrantSense
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_PROFICIENCY_BONUS
from Model.View import CharacterView

SPEED = 30  # Given by your species
SIZE = CreatureSize.SMALL  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(
            name="Darkvision", origin="Gnome Trait", skippable_in_concise=True
        )
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
            skippable_in_concise=True,
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
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        text = "You also always have the Speak with Animals spell prepared. You can cast it without a spell slot, and you regain all expended uses when you finish a Long Rest. You can also use any spell slots you have to cast the spell."
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

    def get_description(self, character: CharacterView) -> str:
        return "Prestidigitation to create a Tiny clockwork device (AC 5,1 HP), such as a toy, fire starter, or music box. When you create the device, you determine its function by choosing one effect from Prestidigitation; the device produces that effect whenever you or another creature takes a Bonus Action to activate it with a touch. If the chosen effect has options within it, you choose one of those options for the device when you create it. For example, if you choose the spell's ignite-extinguish effect, you determine whether the device ignites or extinguishes fire; the device doesn't do both. You can have three such devices in existence at a time, and each falls apart 8 hours after its creation or when you dismantle it with a touch as a Utilize action."

    def get_concise_description(self, character: CharacterView) -> str:
        return (
            "Create a Tiny clockwork device (AC 5, 1 HP) that mimics one Prestidigitation effect, activated by Bonus Action and touch. "
            "You can have 3 at a time; each lasts 8 hours or until dismantled."
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT
