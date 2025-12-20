import CharacterSheetCreator
from Features import AasimarFeatures
from Features import OriginFeats
from Spells.Definitions import SorcererLevel0Spells


def aasimar_character_data(
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = AasimarFeatures.SPEED  # Given by your species
    data.size = AasimarFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(AasimarFeatures.Darkvision())
    data.add_feature(AasimarFeatures.CelestialResistance())
    data.add_feature(AasimarFeatures.LightBearer())
    data.add_cantrip(SorcererLevel0Spells.LIGHT)
    data.add_feature(AasimarFeatures.HealingHands())
    if data.character_level >= 3:
        data.add_feature(AasimarFeatures.CelestialRevelation())

    return data
