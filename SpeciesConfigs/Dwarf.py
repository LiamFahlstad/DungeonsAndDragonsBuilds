import CharacterSheetCreator
from Features import OriginFeats
from Features.SpeciesFeatures import DwarfFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class DwarfSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        origin_feat: OriginFeats.OriginFeat,
    ):
        self.origin_feat = origin_feat
        super().__init__(
            name="Dwarf",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = DwarfFeatures.SPEED  # Given by your species
        data.size = DwarfFeatures.SIZE  # Given by your species
        data.add_feature(self.origin_feat)

        data.add_feature(DwarfFeatures.Darkvision())
        data.add_feature(DwarfFeatures.DwarvenResilience())
        data.add_feature(DwarfFeatures.DwarvenToughness())
        data.add_feature(DwarfFeatures.Stonecunning())

        return data
