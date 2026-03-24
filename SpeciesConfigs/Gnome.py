import CharacterSheetCreator
import Definitions
from Definitions import Ability
from Features.SpeciesFeatures import GnomeFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder
from Spells.Definitions import BardLevel0Spells, DruidLevel1Spells


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
        data.add_spell(
            DruidLevel1Spells.SPEAK_WITH_ANIMALS,
            self.spell_casting_ability,
            additional_ruling="You also always have the Speak with Animals spell prepared. You can cast it without a spell slot a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest. You can also use any spell slots you have to cast the spell.",
        )

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
