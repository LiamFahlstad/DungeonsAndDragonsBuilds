import CharacterSheetCreator
from Definitions import CreatureSize
from Features.SpeciesFeatures import HexbloodFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class HexbloodSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
    ):
        super().__init__(
            name="Hexblood",
        )
        self.size = size

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = HexbloodFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(HexbloodFeatures.Darkvision())
        data.add_feature(HexbloodFeatures.EerieToken())
        data.add_feature(HexbloodFeatures.HexMagic())

        return data
