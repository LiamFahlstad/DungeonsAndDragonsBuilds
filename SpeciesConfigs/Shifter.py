import CharacterSheetCreator
from Definitions import CreatureSize, Skill
from Features.SpeciesFeatures import ShifterFeatures
from SpeciesConfigs.SpeciesBuilder import SpeciesBuilder


class ShifterSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        skill: Skill,
        size: CreatureSize,
        shifter_form: ShifterFeatures.ShiftForm,
    ):
        super().__init__(
            name="Shifter",
        )
        self.skill = skill
        self.shifter_form = shifter_form
        assert size in [CreatureSize.MEDIUM, CreatureSize.SMALL]
        self.size = size

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = ShifterFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(ShifterFeatures.Darkvision(60))
        data.add_feature(ShifterFeatures.Shifting(self.shifter_form))
        data.add_feature(ShifterFeatures.BestialInstincts(self.skill))

        return data
