from Definitions import CreatureSize
from Features.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class FiendishResistance(Feature):
    def __init__(self, damage_type: str):
        self.damage_type = damage_type
        super().__init__(name="Fiendish Resistance", origin="Tiefling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Resistance to {self.damage_type} damage."


class Darkvision(Feature):
    def __init__(self, distance: int):
        self.distance = distance
        super().__init__(name="Darkvision", origin="Tiefling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Darkvision with a range of {self.distance} feet."


class FiendishLegacy(Feature):
    def __init__(self, cantrip: str, spell_1: str | None, spell_2: str | None):
        self.cantrip = cantrip
        self.spell_1 = spell_1
        self.spell_2 = spell_2
        super().__init__(name="Fiendish Legacy", origin="Tiefling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = f"You also know the '{self.cantrip}' cantrip.\n"
        if self.spell_1 is not None and character_stat_block.character_level >= 3:
            text += f"You can cast the '{self.spell_1}' without expending a spell slot once per Long Rest.\n"
        if self.spell_2 is not None and character_stat_block.character_level >= 5:
            text += f"You can cast the '{self.spell_2}' without expending a spell slot once per Long Rest.\n"
        return text


class OtherworldlyPresence(Feature):
    def __init__(self):
        super().__init__(name="Otherworldly Presence", origin="Tiefling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You know the Thaumaturgy cantrip. When you cast it with this trait, the spell uses the same spellcasting ability you use for your Fiendish Legacy trait."
