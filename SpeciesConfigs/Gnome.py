import CharacterSheetCreator
import Definitions
from Definitions import Ability
from Features.SpeciesFeatures import GnomeFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder
from Spells.Definitions import BardLevel0Spells


class ForestGnomeSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        spell_casting_ability: Definitions.Ability,
    ):
        self.spell_casting_ability = spell_casting_ability
        super().__init__(
            name="Forest Gnome",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = GnomeFeatures.SPEED  # Given by your species
        data.size = GnomeFeatures.SIZE  # Given by your species

        data.add_feature(GnomeFeatures.Darkvision())
        data.add_feature(GnomeFeatures.ForestGnomeSpeakWithAnimals())

        data.add_spell(BardLevel0Spells.MINOR_ILLUSION, self.spell_casting_ability)

        return data


class RockGnomeSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
    ):
        super().__init__(
            name="Rock Gnome",
        )

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = GnomeFeatures.SPEED  # Given by your species
        data.size = GnomeFeatures.SIZE  # Given by your species

        data.add_feature(GnomeFeatures.Darkvision())
        data.add_feature(GnomeFeatures.RockGnomePrestidigitation())

        data.add_spell(BardLevel0Spells.MENDING, Ability.INTELLIGENCE)
        data.add_spell(BardLevel0Spells.PRESTIDIGITATION, Ability.INTELLIGENCE)

        return data
