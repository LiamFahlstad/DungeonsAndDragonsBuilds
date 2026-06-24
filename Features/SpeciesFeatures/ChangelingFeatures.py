from Definitions import Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species


class ChangelingInstincts(CharacterFeature):
    VALID_SKILLS = [
        Skill.DECEPTION,
        Skill.INSIGHT,
        Skill.INTIMIDATION,
        Skill.PERFORMANCE,
        Skill.PERSUASION,
    ]

    def __init__(self, skills: list[Skill]):
        assert len(skills) == 2, "Changeling Instincts requires exactly two skills."
        for skill in skills:
            assert skill in self.VALID_SKILLS, (
                f"Invalid skill for Changeling Instincts: {skill}. "
                f"Valid choices are: Deception, Insight, Intimidation, Performance, or Persuasion."
            )
        self.skills = skills

    def validate(self, character_stat_block: CharacterStatBlock):
        for skill in self.skills:
            assert not character_stat_block.skills.is_proficient(skill), (
                f"Character already has proficiency in {skill}."
            )

    def modify(self, character_stat_block: CharacterStatBlock):
        self.validate(character_stat_block)
        for skill in self.skills:
            character_stat_block.skills.add_skill_proficiency(skill)


class ShapeShifter(TextFeature):
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
