from Builds import CharacterSheetAccumulator
import Core.Definitions as Definitions
from CharacterContent.Features.CharacterFeats import OriginFeats
from CharacterContent.Features.SpeciesFeatures import HumanFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class HumanSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        origin_feat: OriginFeats.OriginFeat,
        skill_proficiency: Definitions.Skill,
    ):
        self.origin_feat = origin_feat
        self.skill_proficiency = skill_proficiency
        super().__init__(
            name="Human",
        )

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = HumanFeatures.SPEED  # Given by your species
        data.size = HumanFeatures.SIZE  # Given by your species

        data.add_feature(HumanFeatures.Resourceful())
        data.add_feature(HumanFeatures.Skillful(self.skill_proficiency))
        data.add_feature(HumanFeatures.Versatile())

        data.add_origin_feat(self.origin_feat)

        return data
