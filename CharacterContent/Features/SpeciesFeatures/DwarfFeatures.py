from Core.Definitions import CreatureSize, Sense
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import HitPointsPerLevelBonus, GrantSense
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(Feature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Dwarf Trait", skippable_in_concise=True)
        self._sense = GrantSense(Sense.DARKVISION, 120, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._sense.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 120 feet."


class DwarvenResilience(Feature):
    def __init__(self):
        super().__init__(name="Dwarven Resilience", origin="Dwarf Trait", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Resistance to Poison damage. You also have Advantage on saving throws you make to avoid or end the Poisoned condition."


class DwarvenToughness(Feature):
    def __init__(self):
        super().__init__(name="Dwarven Toughness", origin="Dwarf Trait", skippable_in_concise=True, usage_tags=["heal"])
        self._hp = HitPointsPerLevelBonus(1)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._hp.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You gain an additional Hit Point for each level you gain."


class Stonecunning(Feature):
    def __init__(self):
        super().__init__(name="Stonecunning", origin="Dwarf Trait", action_type="bonus_action", duration="10 Minutes")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        text = (
            "As a Bonus Action, you gain Tremorsense with a range of 60 feet for 10 minutes. You must be on a stone surface or touching a stone surface to use this Tremorsense. The stone can be natural or worked.\n"
            f"You can use this Bonus Action a number of times equal to your Proficiency Bonus ({proficiency_bonus}), and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(text, proficiency_bonus, max_box_count=6, current_formula="Current amount: equal to your proficiency bonus.")
