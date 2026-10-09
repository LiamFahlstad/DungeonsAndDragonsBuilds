from Core.Definitions import CreatureSize
from CharacterContent.Features.SpeciesFeatures import DhampirFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder, SpeciesGrants


class DhampirSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
    ):
        super().__init__(
            name="Dhampir",
        )
        self.size = size

    def _grant(self, data: SpeciesGrants) -> None:
        data.base_speed = DhampirFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(DhampirFeatures.Darkvision())
        data.add_feature(DhampirFeatures.SpiderClimb(data.character_level))
        data.add_feature(DhampirFeatures.TraceOfUndeath())
        data.add_feature(DhampirFeatures.VampiricBite())
