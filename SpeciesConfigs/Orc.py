import CharacterSheetCreator
from Features import OriginFeats
from Features.SpeciesFeatures import OrcFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class OrcSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        origin_feat: OriginFeats.OriginFeat,
    ):
        self.origin_feat = origin_feat
        super().__init__(
            name="Orc",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = OrcFeatures.SPEED  # Given by your species
        data.size = OrcFeatures.SIZE  # Given by your species
        data.add_feature(self.origin_feat)

        data.add_feature(OrcFeatures.Darkvision())
        data.add_feature(OrcFeatures.AdrenalineRush())
        data.add_feature(OrcFeatures.RelentlessEndurance())

        return data
