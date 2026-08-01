from Builds import CharacterSheetAccumulator
from Core.Definitions import CreatureSize, Skill
from CharacterContent.Features.SpeciesFeatures import KhoravarFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder


class KhoravarSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
        skill_versatility: Skill,
    ):
        super().__init__(
            name="Khoravar",
        )
        assert size in [
            CreatureSize.SMALL,
            CreatureSize.MEDIUM,
        ], "Khoravar can only be Small or Medium size."
        self.size = size
        self.skill_versatility = skill_versatility

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = KhoravarFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(KhoravarFeatures.Darkvision(60))
        data.add_feature(KhoravarFeatures.FeyAncestry())
        data.add_feature(KhoravarFeatures.FeyGift())
        data.add_feature(KhoravarFeatures.LethargyResilience())
        data.add_feature(KhoravarFeatures.SkillVersatility(self.skill_versatility))

        return data
