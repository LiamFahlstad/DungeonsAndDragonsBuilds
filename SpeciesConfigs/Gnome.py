import CharacterSheetCreator
from Features import OriginFeats
from Features.SpeciesFeatures import GnomeFeatures
from Spells.Definitions import BardLevel0Spells


def forest_gnome_character_data(
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = GnomeFeatures.SPEED  # Given by your species
    data.size = GnomeFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(GnomeFeatures.Darkvision())
    data.add_feature(GnomeFeatures.ForestGnomeSpeakWithAnimals())

    data.add_spell(BardLevel0Spells.MINOR_ILLUSION)

    return data


def rock_gnome_character_data(
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = GnomeFeatures.SPEED  # Given by your species
    data.size = GnomeFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(GnomeFeatures.Darkvision())
    data.add_feature(GnomeFeatures.RockGnomePrestidigitation())

    data.add_spell(BardLevel0Spells.MENDING)
    data.add_spell(BardLevel0Spells.PRESTIDIGITATION)

    return data
