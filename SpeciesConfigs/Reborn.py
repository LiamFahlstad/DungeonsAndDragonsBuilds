from Builds import CharacterSheetCreator
from Core.Definitions import CreatureSize
from Features.SpeciesFeatures import RebornFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class RebornSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
    ):
        super().__init__(
            name="Reborn",
        )
        self.size = size

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = RebornFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(RebornFeatures.EscapedDeath())
        data.add_feature(RebornFeatures.Everlasting())
        data.add_feature(RebornFeatures.RebornKnowledge())
        data.add_feature(RebornFeatures.StrangeEndurance())

        return data
