from Builds import CharacterSheetCreator
from Core.Definitions import CreatureSize, Skill
from CharacterContent.Features.SpeciesFeatures import LupinFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class LupinSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
        werewolf_instincts_skill: Skill,
    ):
        super().__init__(
            name="Lupin",
        )
        self.size = size
        self.werewolf_instincts_skill = werewolf_instincts_skill

    def build(self) -> CharacterSheetCreator.CharacterSheetData:
        data = CharacterSheetCreator.CharacterSheetData()

        data.speed = LupinFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(LupinFeatures.Darkvision())
        data.add_feature(LupinFeatures.FeralPounce())
        data.add_feature(LupinFeatures.Howl())
        data.add_feature(LupinFeatures.WerewolfInstincts(self.werewolf_instincts_skill))

        return data
