import CharacterSheetCreator
from Definitions import Ability
from Features.SpeciesFeatures import GnomeFeatures
from Spells.Definitions import BardLevel0Spells


def forest_gnome_character_data() -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = GnomeFeatures.SPEED  # Given by your species
    data.size = GnomeFeatures.SIZE  # Given by your species

    data.add_feature(GnomeFeatures.Darkvision())
    data.add_feature(GnomeFeatures.ForestGnomeSpeakWithAnimals())

    data.add_spell(BardLevel0Spells.MINOR_ILLUSION)

    return data


def rock_gnome_character_data() -> CharacterSheetCreator.CharacterSheetData:

    data = CharacterSheetCreator.CharacterSheetData()

    data.speed = GnomeFeatures.SPEED  # Given by your species
    data.size = GnomeFeatures.SIZE  # Given by your species

    data.add_feature(GnomeFeatures.Darkvision())
    data.add_feature(GnomeFeatures.RockGnomePrestidigitation())

    data.add_spell(BardLevel0Spells.MENDING, Ability.INTELLIGENCE)
    data.add_spell(BardLevel0Spells.PRESTIDIGITATION, Ability.INTELLIGENCE)

    return data
