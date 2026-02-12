import CharacterSheetCreator
from Features.SpeciesFeatures import AasimarFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder
from Spells.Definitions import SorcererLevel0Spells


class AasimarSpeciesBuilder(SpeciesBuilder):
    def __init__(self, character_level: int):
        self.character_level = character_level
        super().__init__(
            name="Aasimar",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = AasimarFeatures.SPEED  # Given by your species
        data.size = AasimarFeatures.SIZE  # Given by your species

        data.add_feature(AasimarFeatures.Darkvision())
        data.add_feature(AasimarFeatures.CelestialResistance())
        data.add_feature(AasimarFeatures.LightBearer())
        data.add_cantrip(SorcererLevel0Spells.LIGHT)
        data.add_feature(AasimarFeatures.HealingHands())
        if self.character_level >= 3:
            data.add_feature(AasimarFeatures.CelestialRevelation())

        return data
