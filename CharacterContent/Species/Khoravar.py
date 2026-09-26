from Builds import CharacterSheetAccumulator
from Core.Definitions import Ability, CreatureSize, Skill
from CharacterContent.Features.SpeciesFeatures import KhoravarFeatures
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder
from CharacterContent.Spells.SpellLists import BardLevel0Spells


class KhoravarSpeciesBuilder(SpeciesBuilder):
    def __init__(
        self,
        size: CreatureSize,
        skill_versatility: Skill,
        spell_casting_ability: Ability,
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
        assert spell_casting_ability in [
            Ability.INTELLIGENCE,
            Ability.WISDOM,
            Ability.CHARISMA,
        ], "Fey Gift uses Intelligence, Wisdom, or Charisma."
        self.spell_casting_ability = spell_casting_ability

    def build(self) -> CharacterSheetAccumulator.CharacterSheetData:
        data = CharacterSheetAccumulator.CharacterSheetData()

        data.speed = KhoravarFeatures.SPEED  # Given by your species
        data.size = self.size  # Given by your species

        data.add_feature(KhoravarFeatures.Darkvision(60))
        data.add_feature(KhoravarFeatures.FeyAncestry())
        data.add_feature(KhoravarFeatures.FeyGift())
        data.add_cantrip(BardLevel0Spells.FRIENDS, self.spell_casting_ability)
        data.add_feature(KhoravarFeatures.LethargyResilience())
        data.add_feature(KhoravarFeatures.SkillVersatility(self.skill_versatility))

        return data
