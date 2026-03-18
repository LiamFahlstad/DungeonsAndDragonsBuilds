import CharacterSheetCreator
from Definitions import Skill
from Features.SpeciesFeatures import WarForgedFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class WarForgedSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        skill: Skill,
    ):
        super().__init__(
            name="WarForged",
        )
        self.skill = skill

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = WarForgedFeatures.SPEED  # Given by your species
        data.size = WarForgedFeatures.SIZE  # Given by your species

        data.add_feature(WarForgedFeatures.ConstructResilience())
        data.add_feature(WarForgedFeatures.SentrysRest())
        data.add_feature(WarForgedFeatures.Tireless())
        data.add_feature(WarForgedFeatures.IntegratedProtection())
        data.add_feature(WarForgedFeatures.SpecializedDesign(self.skill))

        return data
