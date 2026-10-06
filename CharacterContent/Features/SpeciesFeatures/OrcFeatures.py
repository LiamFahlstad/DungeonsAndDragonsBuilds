from Core.Definitions import CreatureSize, Sense
from CharacterContent.Features.Core.BaseFeatures import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from CharacterContent.Features.Core.Improvements import GrantSense
from Model.Character import Character
from Model.Effects import Effects
from Core.Rules import MAX_PROFICIENCY_BONUS

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Orc Trait")
        self._sense = GrantSense(Sense.DARKVISION, 120, self.name)

    def apply(self, effects: Effects):
        self._sense.apply(effects)

    def get_description(self, character: Character) -> str:
        return "You have Darkvision with a range of 120 feet."


class AdrenalineRush(Feature):
    def __init__(self):
        super().__init__(
            name="Adrenaline Rush",
            origin="Orc Trait",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["heal"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                current_formula="Current amount: equal to your proficiency bonus.",
            ),
        )

    def get_description(self, character: Character) -> str:
        text = (
            "You can take the Dash action as a Bonus Action. When you do so, you gain a number of Temporary Hit Points equal to your Proficiency Bonus.\n"
            "You can use this trait, and you regain all expended uses when you finish a Short or Long Rest."
        )
        return text

    def regained_on(self, character: Character) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character: Character) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def number_of_uses(self, character: Character) -> int:
        return character.get_proficiency_bonus()


class RelentlessEndurance(Feature):
    def __init__(self):
        super().__init__(
            name="Relentless Endurance",
            origin="Orc Trait",
            usage_tags=["heal"],
        )

    def get_description(self, character: Character) -> str:
        text = "When you are reduced to 0 Hit Points but not killed outright, you can drop to 1 Hit Point instead. Once you use this trait, you can't do so again until you finish a Long Rest."
        return text
