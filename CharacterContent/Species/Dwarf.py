from Builds import CharacterSheetAccumulator
from CharacterContent.Features.SpeciesFeatures import DwarfFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class DwarfSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
    ):
        super().__init__(
            name="Dwarf",
        )

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = DwarfFeatures.SPEED  # Given by your species
        data.size = DwarfFeatures.SIZE  # Given by your species

        data.add_feature(DwarfFeatures.Darkvision())
        data.add_feature(DwarfFeatures.DwarvenResilience())
        data.add_feature(DwarfFeatures.DwarvenToughness())
        data.add_feature(DwarfFeatures.Stonecunning())

        return data
