from Builds import CharacterSheetAccumulator
from Core.Definitions import Ability, CreatureSize
from CharacterContent.Features.SpeciesFeatures import HexbloodFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder
from CharacterContent.Spells.SpellLists import BardLevel1Spells, WarlockLevel1Spells


class HexbloodSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
        spell_casting_ability: Ability,
    ):
        super().__init__(
            name="Hexblood",
        )
        self.size = size
        assert spell_casting_ability in [
            Ability.INTELLIGENCE,
            Ability.WISDOM,
            Ability.CHARISMA,
        ], "Hex Magic uses Intelligence, Wisdom, or Charisma."
        self.spell_casting_ability = spell_casting_ability

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = HexbloodFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(HexbloodFeatures.Darkvision())
        data.add_feature(HexbloodFeatures.EerieToken())
        data.add_feature(HexbloodFeatures.HexMagic())
        data.add_spell(BardLevel1Spells.DISGUISE_SELF, self.spell_casting_ability)
        data.add_spell(WarlockLevel1Spells.HEX, self.spell_casting_ability)

        return data
