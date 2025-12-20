import CharacterSheetCreator
import Definitions
from Features import GnomeFeatures
from Features import OriginFeats
from Spells.Definitions import BardLevel0Spells


def forest_gnome_character_data(
    skill_proficiency: Definitions.Skill,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = GnomeFeatures.SPEED  # Given by your species
    data.size = GnomeFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(GnomeFeatures.Darkvision())
    data.add_feature(GnomeFeatures.ForestGnomeSpeakWithAnimals(skill_proficiency))

    data.add_spell(BardLevel0Spells.MINOR_ILLUSION)

    return data


def rock_gnome_character_data(
    skill_proficiency: Definitions.Skill,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
) -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = GnomeFeatures.SPEED  # Given by your species
    data.size = GnomeFeatures.SIZE  # Given by your species
    data.add_feature(origin_feat)

    data.add_feature(GnomeFeatures.Darkvision())
    data.add_feature(GnomeFeatures.RockGnomePrestidigitation(skill_proficiency))

    data.add_spell(BardLevel0Spells.MENDING)
    data.add_spell(BardLevel0Spells.PRESTIDIGITATION)

    return data
