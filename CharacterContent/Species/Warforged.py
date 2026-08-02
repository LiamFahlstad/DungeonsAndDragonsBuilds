from Builds import CharacterSheetAccumulator
from Core.Definitions import Skill
from CharacterContent.Features.SpeciesFeatures import WarForgedFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class WarforgedSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        skill: Skill,
    ):
        super().__init__(
            name="WarForged",
        )
        self.skill = skill

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = WarForgedFeatures.SPEED  # Given by your species
        data.size = WarForgedFeatures.SIZE  # Given by your species

        data.add_feature(WarForgedFeatures.ConstructResilience())
        data.add_feature(WarForgedFeatures.SentrysRest())
        data.add_feature(WarForgedFeatures.Tireless())
        data.add_feature(WarForgedFeatures.IntegratedProtection())
        data.add_feature(WarForgedFeatures.SpecializedDesign(self.skill))

        return data
