import CharacterSheetCreator
from Features import DwarfFeatures
from Features import OriginFeats


def forest_Dwarf_character_data(
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = DwarfFeatures.SPEED  # Given by your species
    data.size = DwarfFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(DwarfFeatures.Darkvision())
    data.add_feature(DwarfFeatures.DwarvenResilience())
    data.add_feature(DwarfFeatures.DwarvenToughness())
    data.add_feature(DwarfFeatures.Stonecunning())

    return data
