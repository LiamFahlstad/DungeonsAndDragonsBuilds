from Definitions import CreatureSize
from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class Darkvision(TextFeature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(name="Darkvision", origin="Orc Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class FiendishLegacy(TextFeature):
    def __init__(self, cantrip: str, spell_1: str, spell_2: str):
        self.cantrip = cantrip
        self.spell_1 = spell_1
        self.spell_2 = spell_2
        super().__init__(name="Fiendish Legacy", origin="Tiefling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = f"You also know the '{self.cantrip}' cantrip.\n"
        if character_stat_block.character_level >= 3:
            text += f"You can cast the '{self.spell_1}' without expending a spell slot once per Long Rest.\n"
        if character_stat_block.character_level >= 5:
            text += f"You can cast the '{self.spell_2}' without expending a spell slot once per Long Rest.\n"
        return text


class OtherworldlyPresence(TextFeature):
    def __init__(self):
        super().__init__(name="Otherworldly Presence", origin="Tiefling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You know the Thaumaturgy cantrip. When you cast it with this trait."
