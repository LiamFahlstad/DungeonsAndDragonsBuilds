from Builds import CharacterSheetAccumulator
from CharacterContent.Features.SpeciesFeatures import OrcFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class OrcSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
    ):
        super().__init__(
            name="Orc",
        )

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = OrcFeatures.SPEED  # Given by your species
        data.size = OrcFeatures.SIZE  # Given by your species

        data.add_feature(OrcFeatures.Darkvision())
        data.add_feature(OrcFeatures.AdrenalineRush())
        data.add_feature(OrcFeatures.RelentlessEndurance())

        return data
