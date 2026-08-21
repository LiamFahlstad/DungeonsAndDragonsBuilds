from Core.Definitions import Ability, DamageType, Skill
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import DamageResistance, SavingThrowAdvantage
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

SPEED = 30  # Given by your species


class DualMind(Feature):
    def __init__(self):
        super().__init__(name="Dual Mind", origin="Kalashtar Trait", skippable_in_concise=True, usage_tags=["buff"])
        self._advantage = SavingThrowAdvantage([Ability.WISDOM, Ability.CHARISMA])

    def apply(self, character_stat_block: CharacterStatBlock):
        self._advantage.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Advantage on Wisdom and Charisma saving throws."


class MentalDiscipline(Feature):
    def __init__(self):
        super().__init__(name="Mental Discipline", origin="Kalashtar Trait", skippable_in_concise=True, usage_tags=["buff"])
        self._resistance = DamageResistance(DamageType.PSYCHIC, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._resistance.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Resistance to Psychic damage."


class MindLink(Feature):
    def __init__(self):
        super().__init__(name="Mind Link", origin="Kalashtar Trait", action_type="action", duration="1 Hour", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        character_level = character_stat_block.character_level
        range_feet = 10 * character_level
        return (
            f"You have telepathy with a range in feet equal to 10 times your level ({range_feet} feet). "
            "When you're using this trait to speak telepathically to a creature, you can take a Magic action "
            "to give that creature the ability to speak telepathically with you for 1 hour or until you take "
            "another Magic action to end this effect."
        )


class SeveredFromDreams(Feature):
    def __init__(self):
        super().__init__(name="Severed from Dreams", origin="Kalashtar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You can't be the target of the Dream spell. "
            "In addition, when you finish a Long Rest, you gain proficiency in one skill of your choice. "
            "This proficiency lasts until you finish another Long Rest."
        )
