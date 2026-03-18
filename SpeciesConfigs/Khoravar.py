import CharacterSheetCreator
from Definitions import CreatureSize
from Features.SpeciesFeatures import KhoravarFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class KhoravarSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
    ):
        super().__init__(
            name="Khoravar",
        )
        assert size in [
            CreatureSize.SMALL,
            CreatureSize.MEDIUM,
        ], "Khoravar can only be Small or Medium size."
        self.size = size

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = KhoravarFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(KhoravarFeatures.Darkvision(60))
        data.add_feature(KhoravarFeatures.DwarvenResilience())
        data.add_feature(KhoravarFeatures.DwarvenToughness())
        data.add_feature(KhoravarFeatures.Stonecunning())

        return data
