from Model.Character import Character
from CharacterContent.Features.SpeciesFeatures import OrcFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class OrcSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
    ):
        super().__init__(
            name="Orc",
        )

    def _grant(self, data: Character) -> None:
        data.base_speed = OrcFeatures.SPEED  # Given by your species
        data.size = OrcFeatures.SIZE  # Given by your species

        data.add_feature(OrcFeatures.Darkvision())
        data.add_feature(OrcFeatures.AdrenalineRush())
        data.add_feature(OrcFeatures.RelentlessEndurance())
