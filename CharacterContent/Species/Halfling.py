from Model.Grants import Grants
from CharacterContent.Features.SpeciesFeatures import HalflingFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class HalflingSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
    ):
        super().__init__(
            name="Halfling",
        )

    def _grant(self, data: Grants) -> None:
        data.base_speed = HalflingFeatures.SPEED  # Given by your species
        data.size = HalflingFeatures.SIZE  # Given by your species

        data.add_feature(HalflingFeatures.Brave())
        data.add_feature(HalflingFeatures.Luck())
        data.add_feature(HalflingFeatures.HalflingNimbleness())
        data.add_feature(HalflingFeatures.NaturallyStealthy())
