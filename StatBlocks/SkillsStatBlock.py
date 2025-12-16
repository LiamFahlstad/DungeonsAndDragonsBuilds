from typing import Optional
from Definitions import Ability, Skill, DiceRollCondition
import Definitions
from StatBlocks.StatBlock import StatBlock


class SkillsStatBlock(StatBlock):
    def __init__(
        self,
        proficiencies: Optional[dict[Skill, bool]] = None,
        expertise: Optional[dict[Skill, bool]] = None,
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        self.proficiencies = proficiencies if proficiencies is not None else {}
        self.expertise = expertise if expertise is not None else {}
        self.bonuses = bonuses if bonuses is not None else {}
        self.dice_roll_conditions = (
            dice_roll_conditions if dice_roll_conditions is not None else {}
        )

    def add_skill_proficiency(self, skill: Skill):
        self.proficiencies[skill] = True

    def add_skill_expertise(self, skill: Skill):
        if not self.is_proficient(skill):
            raise ValueError(f"Cannot add expertise to unproficient skill: {skill}")
        self.expertise[skill] = True

    def is_proficient(self, skill: Skill) -> bool:
        return self.proficiencies.get(skill, False)

    def has_expertise(self, skill: Skill) -> bool:
        return self.expertise.get(skill, False)

    def get_roll_condition(self, skill: Skill) -> DiceRollCondition:
        return self.dice_roll_conditions.get(skill, DiceRollCondition.NEUTRAL)

    def get_skill_ability(self, skill: Skill) -> Ability:
        skill_to_ability = {
            Skill.ACROBATICS: Ability.DEXTERITY,
            Skill.ANIMAL_HANDLING: Ability.WISDOM,
            Skill.ARCANA: Ability.INTELLIGENCE,
            Skill.ATHLETICS: Ability.STRENGTH,
            Skill.DECEPTION: Ability.CHARISMA,
            Skill.HISTORY: Ability.INTELLIGENCE,
            Skill.INSIGHT: Ability.WISDOM,
            Skill.INTIMIDATION: Ability.CHARISMA,
            Skill.INVESTIGATION: Ability.INTELLIGENCE,
            Skill.MEDICINE: Ability.WISDOM,
            Skill.NATURE: Ability.INTELLIGENCE,
            Skill.PERCEPTION: Ability.WISDOM,
            Skill.PERFORMANCE: Ability.CHARISMA,
            Skill.PERSUASION: Ability.CHARISMA,
            Skill.RELIGION: Ability.INTELLIGENCE,
            Skill.SLEIGHT_OF_HAND: Ability.DEXTERITY,
            Skill.STEALTH: Ability.DEXTERITY,
            Skill.SURVIVAL: Ability.WISDOM,
        }
        return skill_to_ability[skill]


class ClassSkillsStatBlock(SkillsStatBlock):
    """Paladin Skills Stat Block"""

    def __init__(
        self,
        character_class: Definitions.CharacterClass,
        excepted_skills: list[Skill],
        num_proficiencies: int,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        for skill, proficient in proficiencies.items():
            if proficient and skill not in excepted_skills:
                raise ValueError(f"Invalid skill for {character_class.value}: {skill}")

        proficient_counter = 0
        for skill in excepted_skills:
            if proficiencies.get(skill, False):
                proficient_counter += 1
        if proficient_counter != num_proficiencies:
            raise ValueError(
                f"{character_class.value} must be proficient in exactly {num_proficiencies} skills."
            )

        super().__init__(
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


### PALADIN
class PaladinSkillsStatBlock(ClassSkillsStatBlock):
    """Paladin Skills Stat Block"""

    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        excepted_skills = [
            Skill.ATHLETICS,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.MEDICINE,
            Skill.PERSUASION,
            Skill.RELIGION,
        ]

        super().__init__(
            character_class=Definitions.CharacterClass.PALADIN,
            excepted_skills=excepted_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class FighterSkillsStatBlock(ClassSkillsStatBlock):
    """Fighter Skills Stat Block"""

    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        excepted_skills = [
            Skill.ACROBATICS,
            Skill.ANIMAL_HANDLING,
            Skill.ATHLETICS,
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.PERCEPTION,
            Skill.SURVIVAL,
        ]

        super().__init__(
            character_class=Definitions.CharacterClass.FIGHTER,
            excepted_skills=excepted_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class WarlockSkillsStatBlock(ClassSkillsStatBlock):
    """Warlock Skills Stat Block"""

    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        excepted_skills = [
            Skill.ARCANA,
            Skill.DECEPTION,
            Skill.HISTORY,
            Skill.INTIMIDATION,
            Skill.INVESTIGATION,
            Skill.NATURE,
            Skill.RELIGION,
        ]

        super().__init__(
            character_class=Definitions.CharacterClass.WARLOCK,
            excepted_skills=excepted_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class RangerSkillsStatBlock(ClassSkillsStatBlock):
    """Ranger Skills Stat Block"""

    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        excepted_skills = [
            Skill.ANIMAL_HANDLING,
            Skill.ATHLETICS,
            Skill.INSIGHT,
            Skill.INVESTIGATION,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.STEALTH,
            Skill.SURVIVAL,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.WARLOCK,
            excepted_skills=excepted_skills,
            num_proficiencies=3,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class WizardSkillsStatBlock(ClassSkillsStatBlock):
    """Wizard Skills Stat Block"""

    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        excepted_skills = [
            Skill.ARCANA,
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.INVESTIGATION,
            Skill.MEDICINE,
            Skill.NATURE,
            Skill.RELIGION,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.WIZARD,
            excepted_skills=excepted_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )
