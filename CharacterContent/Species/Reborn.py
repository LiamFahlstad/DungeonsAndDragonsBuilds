from Builds import CharacterSheetAccumulator
from Core.Definitions import CreatureSize, DamageType, Skill
from CharacterContent.Features.SpeciesFeatures import RebornFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class RebornSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
        knowledge_skill: Skill,
        strange_endurance: DamageType,
    ):
        super().__init__(
            name="Reborn",
        )
        self.size = size
        self.knowledge_skill = knowledge_skill
        self.strange_endurance = strange_endurance

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = RebornFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(RebornFeatures.EscapedDeath())
        data.add_feature(RebornFeatures.Everlasting())
        data.add_feature(RebornFeatures.RebornKnowledge())
        data.add_feature(RebornFeatures.RebornKnowledgeSkill(self.knowledge_skill))
        data.add_feature(RebornFeatures.StrangeEndurance(self.strange_endurance))

        return data
