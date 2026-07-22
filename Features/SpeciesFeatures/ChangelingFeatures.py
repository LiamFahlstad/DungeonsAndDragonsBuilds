from Definitions import Skill
from Features.Core.BaseFeatures import Feature
from Features.Core.SubFeatures import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species


class ChangelingInstincts(Feature):
    VALID_SKILLS = [
        Skill.DECEPTION,
        Skill.INSIGHT,
        Skill.INTIMIDATION,
        Skill.PERFORMANCE,
        Skill.PERSUASION,
    ]

    def __init__(self, skills: list[Skill]):
        super().__init__(name="Changeling Instincts", origin="Changeling Trait")
        self._choice = SkillProficiencyChoice(
            skills, self.VALID_SKILLS, count=2, error_prefix="Changeling Instincts"
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if len(self._choice.skills) == 2:
            skill_text = f"{self._choice.skills[0].value} and {self._choice.skills[1].value}"
        else:
            skill_text = self._choice.skills[0].value
        return f"You have proficiency in the {skill_text} skills."


class ShapeShifter(Feature):
    def __init__(self):
        super().__init__(name="Shape-Shifter", origin="Changeling Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "As an action, you can shape-shift to change your appearance and your voice. "
            "You determine the specifics of the changes, including your coloration, hair length, and sex. "
            "You can also adjust your height and weight and can change your size between Medium and Small. "
            "You can make yourself appear as a member of another playable species, though none of your game statistics change. "
            "You can't duplicate the appearance of an individual you've never seen, and you must adopt a form that has the same basic arrangement of limbs that you have. "
            "This trait doesn't change your clothing and equipment.\n"
            "While shape-shifted with this trait, you have Advantage on Charisma checks.\n"
            "You stay in the new form until you take an action to revert to your true form."
        )
