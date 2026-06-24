import CharacterSheetCreator
from Definitions import CreatureSize, Skill
from Features.SpeciesFeatures import ChangelingFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class ChangelingSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
        instinct_skills: list[Skill],
    ):
        super().__init__(
            name="Changeling",
        )
        self.size = size
        self.instinct_skills = instinct_skills

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = ChangelingFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(ChangelingFeatures.ChangelingInstincts(self.instinct_skills))
        data.add_feature(ChangelingFeatures.ShapeShifter())

        return data
