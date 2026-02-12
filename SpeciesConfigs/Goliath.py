import CharacterSheetCreator
from Features.SpeciesFeatures import GoliathFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class GoliathSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        giant_ancestry_type: GoliathFeatures.GiantAncestryType,
    ):
        self.giant_ancestry_type = giant_ancestry_type
        super().__init__(
            name="Goliath",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = GoliathFeatures.SPEED  # Given by your species
        data.size = GoliathFeatures.SIZE  # Given by your species

        data.add_feature(GoliathFeatures.GiantAncestry(self.giant_ancestry_type))
        data.add_feature(GoliathFeatures.LargeForm())
        data.add_feature(GoliathFeatures.PowerfulBuild())

        return data
