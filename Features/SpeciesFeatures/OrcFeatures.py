from Definitions import CreatureSize
from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(TextFeature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Orc Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 60 feet."


class AdrenalineRush(TextFeature):
    def __init__(self):
        super().__init__(
            name="Adrenaline Rush",
            origin="Orc Trait",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        text = (
            f"You can take the Dash action as a Bonus Action. When you do so, you gain a number of Temporary Hit Points equal to your Proficiency Bonus ({proficiency_bonus}).\n"
            f"You can use this trait a number of times equal to your Proficiency Bonus ({proficiency_bonus}), and you regain all expended uses when you finish a Short or Long Rest."
        )
        return text


class RelentlessEndurance(TextFeature):
    def __init__(self):
        super().__init__(
            name="Relentless Endurance",
            origin="Orc Trait",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = "When you are reduced to 0 Hit Points but not killed outright, you can drop to 1 Hit Point instead. Once you use this trait, you can't do so again until you finish a Long Rest."
        return text
