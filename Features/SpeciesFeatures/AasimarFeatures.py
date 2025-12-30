from Definitions import CreatureSize
from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class CelestialResistance(TextFeature):
    def __init__(self):
        super().__init__(name="Celestial Resistance", origin="Aasimar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Resistance to Necrotic damage and Radiant damage."


class Darkvision(TextFeature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Aasimar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 60 feet."


class LightBearer(TextFeature):
    def __init__(self):
        super().__init__(name="Light Bearer", origin="Aasimar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You know the Light cantrip. Charisma is your spellcasting ability for it."
        )


class HealingHands(TextFeature):
    def __init__(self):
        super().__init__(
            name="Healing Hands",
            origin="Aasimar Trait",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return f"As a Magic action, you touch a creature and roll a number of d4s equal to your Proficiency Bonus ({proficiency_bonus}). The creature regains a number of Hit Points equal to the total rolled. Once you use this trait, you can't use it again until you finish a Long Rest."


class CelestialRevelation(TextFeature):
    def __init__(self):
        super().__init__(name="Celestial Revelation", origin="Aasimar Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        text = (
            "Celestial Revelation. When you reach character level 3, you can transform as a Bonus Action using one of the options below (choose the option each time you transform). The transformation lasts for 1 minute or until you end it (no action required). Once you transform, you can’t do so again until you finish a Long Rest.\n"
            f"Once on each of your turns before the transformation ends, you can deal extra damage to one target when you deal damage to it with an attack or a spell. The extra damage equals your Proficiency Bonus ({proficiency_bonus}), and the extra damage’s type is either Necrotic for Necrotic Shroud or Radiant for Heavenly Wings and Inner Radiance.\n"
            "Here are the transformation options:\n"
            " * Heavenly Wings. Two spectral wings sprout from your back temporarily. Until the transformation ends, you have a Fly Speed equal to your Speed.\n"
            " * Inner Radiance. Searing light temporarily radiates from your eyes and mouth. For the duration, you shed Bright Light in a 10-foot radius and Dim Light for an additional 10 feet, and at the end of each of your turns, each creature within 10 feet of you takes Radiant damage equal to your Proficiency Bonus.\n"
            " * Necrotic Shroud. Your eyes briefly become pools of darkness, and flightless wings sprout from your back temporarily. Creatures other than your allies within 10 feet of you must succeed on a Charisma saving throw (DC 8 plus your Charisma modifier and Proficiency Bonus) or have the Frightened condition until the end of your next turn.\n"
        )
        return text
