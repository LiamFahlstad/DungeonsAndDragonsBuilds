from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn
from CharacterContent.Features.Core.Improvements import (
    GrantSense,
    HitPointsPerLevelBonus,
)
from Core.Definitions import MAX_PROFICIENCY_BONUS, CreatureSize, Sense
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(
            name="Darkvision", origin="Dwarf Trait", skippable_in_concise=True
        )
        self._sense = GrantSense(Sense.DARKVISION, 120, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._sense.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 120 feet."


class DwarvenResilience(Feature):
    def __init__(self):
        super().__init__(
            name="Dwarven Resilience", origin="Dwarf Trait", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Resistance to Poison damage. You also have Advantage on saving throws you make to avoid or end the Poisoned condition."


class DwarvenToughness(Feature):
    def __init__(self):
        super().__init__(
            name="Dwarven Toughness",
            origin="Dwarf Trait",
            skippable_in_concise=True,
            usage_tags=["heal"],
        )
        self._hp = HitPointsPerLevelBonus(1)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._hp.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You gain an additional Hit Point for each level you gain."


class Stonecunning(Feature):
    def __init__(self):
        super().__init__(
            name="Stonecunning",
            origin="Dwarf Trait",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="10 Minutes", range="60 Feet"),
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                current_formula="Current amount: equal to your proficiency bonus.",
            ),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "As a Bonus Action, you gain Tremorsense with a range of 60 feet for 10 minutes. You must be on a stone surface or touching a stone surface to use this Tremorsense. The stone can be natural or worked.\n"
            "You can use this Bonus Action a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )
        return text

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
