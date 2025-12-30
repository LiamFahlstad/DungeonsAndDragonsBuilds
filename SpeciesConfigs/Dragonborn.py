import CharacterSheetCreator
from Features import OriginFeats
from Features.SpeciesFeatures import DragonbornFeatures


def forest_Dragonborn_character_data(
    dragon_ancestry_color: DragonbornFeatures.DragonColor,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = DragonbornFeatures.SPEED  # Given by your species
    data.size = DragonbornFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(DragonbornFeatures.Darkvision())
    data.add_feature(DragonbornFeatures.BreathWeapon(dragon_ancestry_color))
    data.add_feature(DragonbornFeatures.DamageResistance(dragon_ancestry_color))
    data.add_feature(DragonbornFeatures.DraconicFlight())

    return data
