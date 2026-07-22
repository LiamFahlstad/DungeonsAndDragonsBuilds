from Builds import CharacterSheetCreator
from Core.Definitions import CreatureSize
from Features.SpeciesFeatures import DhampirFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class DhampirSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        character_level: int,
        size: CreatureSize,
    ):
        super().__init__(
            name="Dhampir",
        )
        self.character_level = character_level
        self.size = size

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = DhampirFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(DhampirFeatures.Darkvision())
        data.add_feature(DhampirFeatures.SpiderClimb(self.character_level))
        data.add_feature(DhampirFeatures.TraceOfUndeath())
        data.add_feature(DhampirFeatures.VampiricBite())

        return data
