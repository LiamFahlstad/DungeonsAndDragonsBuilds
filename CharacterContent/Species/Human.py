from Model.Grants import Grants
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

    def _grant(self, data: Grants) -> None:
        data.base_speed = HumanFeatures.SPEED  # Given by your species
        data.size = HumanFeatures.SIZE  # Given by your species

        data.add_feature(HumanFeatures.Resourceful())
        data.add_feature(HumanFeatures.Skillful(self.skill_proficiency))
        data.add_feature(HumanFeatures.Versatile())

        self.origin_feat.grant_to(data)
