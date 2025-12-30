import CharacterSheetCreator
from Features import OriginFeats
from Features.SpeciesFeatures import HalflingFeatures


def halfling_character_data(
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = HalflingFeatures.SPEED  # Given by your species
    data.size = HalflingFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(HalflingFeatures.Brave())
    data.add_feature(HalflingFeatures.Luck())
    data.add_feature(HalflingFeatures.HalflingNimbleness())
    data.add_feature(HalflingFeatures.NaturallyStealthy())

    return data
