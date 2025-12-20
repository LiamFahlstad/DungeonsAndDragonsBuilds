import CharacterSheetCreator
from Features.SpeciesFeatures import OrcFeatures
from Features import OriginFeats


def orc_character_data(
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = OrcFeatures.SPEED  # Given by your species
    data.size = OrcFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(OrcFeatures.Darkvision())
    data.add_feature(OrcFeatures.AdrenalineRush())
    data.add_feature(OrcFeatures.RelentlessEndurance())

    return data
