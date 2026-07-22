from Core.Definitions import Ability, Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import AbilityScoreBonus, SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class FreeBackgroundAbilityBonus(Feature):
    """Also add either [+1, +1, +1] OR [+2, +1] to any abilities."""

    def __init__(self, bonuses: list[tuple[Ability, int]]):
        self._bonus = AbilityScoreBonus(bonuses, total=3, error_prefix="Free Background Ability Bonus")
        super().__init__(name="Free Background Ability Bonus", origin="Background")

    def apply(self, character_stat_block: CharacterStatBlock):
        self._bonus.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        choices = "\n".join(
            f"    * {ability.value} +{bonus}" for ability, bonus in self._bonus.bonuses
        )
        return (
            "Your background grants an Ability Score bonus: either +1 to three different abilities "
            "or +2 to one ability and +1 to another, totaling +3.\n"
            "Choices:\n"
            f"{choices}"
        )


class FreeBackgroundSkillProficiency(Feature):
    """Also add proficiency in two skills of your choice."""

    def __init__(self, skills: list[Skill]):
        self._choice = SkillProficiencyChoice(
            skills,
            list(Skill),
            count=2,
            error_prefix="Free Background Skill Proficiency",
        )
        super().__init__(name="Free Background Skill Proficiency", origin="Background")

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        choices = "\n".join(f"    * {skill.value}" for skill in self._choice.skills)
        return (
            "Your background grants proficiency in two skills of your choice.\n"
            "Choices:\n"
            f"{choices}"
        )
