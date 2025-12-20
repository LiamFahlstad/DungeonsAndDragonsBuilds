import CharacterSheetCreator
from Features import GoliathFeatures
from Features import OriginFeats


def goliath_character_data(
    giant_ancestry_type: GoliathFeatures.GiantAncestryType,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = GoliathFeatures.SPEED  # Given by your species
    data.size = GoliathFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(GoliathFeatures.GiantAncestry(giant_ancestry_type))
    data.add_feature(GoliathFeatures.LargeForm())
    data.add_feature(GoliathFeatures.PowerfulBuild())

    return data
