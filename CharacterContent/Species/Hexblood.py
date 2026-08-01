from Builds import CharacterSheetAccumulator
from Core.Definitions import CreatureSize
from CharacterContent.Features.SpeciesFeatures import HexbloodFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class HexbloodSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
    ):
        super().__init__(
            name="Hexblood",
        )
        self.size = size

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = HexbloodFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(HexbloodFeatures.Darkvision())
        data.add_feature(HexbloodFeatures.EerieToken())
        data.add_feature(HexbloodFeatures.HexMagic())

        return data
