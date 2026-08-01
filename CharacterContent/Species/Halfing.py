from Builds import CharacterSheetCreator
from CharacterContent.Features.SpeciesFeatures import HalflingFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class HalflingSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
    ):
        super().__init__(
            name="Halfling",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = HalflingFeatures.SPEED  # Given by your species
        data.size = HalflingFeatures.SIZE  # Given by your species

        data.add_feature(HalflingFeatures.Brave())
        data.add_feature(HalflingFeatures.Luck())
        data.add_feature(HalflingFeatures.HalflingNimbleness())
        data.add_feature(HalflingFeatures.NaturallyStealthy())

        return data
