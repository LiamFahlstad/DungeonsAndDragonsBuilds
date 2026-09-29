from typing import Optional

import Core.Definitions as Definitions
from Core.Definitions import Ability, DiceRollCondition, Skill, combine_roll_conditions
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
        self.bonuses = {}
        # Per-skill list of (bonus, source) pairs, used to show where each bonus comes from
        self.bonus_sources: dict[Skill, list[tuple[int, str]]] = {}
        if bonuses:
            for skill, bonus in bonuses.items():
                self.add_skill_bonus(skill, bonus)
        # Per-skill {condition: [reasons]} for every source of Advantage or
        # Disadvantage, so the effective condition can be worked out on read
        # (both cancel out) regardless of the order they were granted in.
        self._roll_condition_sources: dict[
            Skill, dict[DiceRollCondition, list[str]]
        ] = {}
        for skill, condition in (dice_roll_conditions or {}).items():
            self.set_roll_condition(skill, condition)
        # Per-skill abilities that replace the default one (e.g. "use Wisdom
        # for Arcana"). See get_skill_abilities.
        self._skill_ability_overrides: dict[Skill, list[Ability]] = {}

    def add_skill_proficiency(self, skill: Skill):
        self.proficiencies[skill] = True

    def add_skill_bonus(self, skill: Skill, bonus: int, source: str = "Other"):
        current_bonus = self.bonuses.get(skill, 0)
        self.bonuses[skill] = current_bonus + bonus
        self.bonus_sources.setdefault(skill, []).append((bonus, source))

    def get_bonus_sources(self, skill: Skill) -> list[tuple[int, str]]:
        return self.bonus_sources.get(skill, [])

    def add_skill_expertise(self, skill: Skill):
        """Expertise requires proficiency, but that proficiency may come from
        a feature applied later (another class builder, the species), so the
        requirement is checked by validate() once every feature has applied
        rather than here - granting expertise is order-insensitive."""
        self.expertise[skill] = True

    def validate(self) -> None:
        for skill, has_expertise in self.expertise.items():
            if has_expertise and not self.is_proficient(skill):
                raise ValueError(f"Cannot add expertise to unproficient skill: {skill}")

    def is_proficient(self, skill: Skill) -> bool:
        return self.proficiencies.get(skill, False)

    def has_expertise(self, skill: Skill) -> bool:
        return self.expertise.get(skill, False)

    def get_roll_condition(self, skill: Skill) -> DiceRollCondition:
        return combine_roll_conditions(self._roll_condition_sources.get(skill, {}))

    def get_roll_condition_sources(
        self, skill: Skill
    ) -> dict[DiceRollCondition, list[str]]:
        """{condition: [reasons]} for every recorded source (a copy)."""
        return {
            condition: list(reasons)
            for condition, reasons in self._roll_condition_sources.get(
                skill, {}
            ).items()
        }

    def set_roll_condition(
        self, skill: Skill, condition: DiceRollCondition, reason: Optional[str] = None
    ):
        """Add a source of Advantage/Disadvantage on a skill. Per the rules,
        having both cancels out to a straight roll no matter how many sources
        of each there are. A NEUTRAL source changes nothing."""
        if condition == DiceRollCondition.NEUTRAL:
            return
        reasons = self._roll_condition_sources.setdefault(skill, {}).setdefault(
            condition, []
        )
        if reason is not None:
            reasons.append(reason)

    def get_roll_condition_reasons(self, skill: Skill) -> list[str]:
        condition = self.get_roll_condition(skill)
        return list(self._roll_condition_sources.get(skill, {}).get(condition, []))

    def get_skill_abilities(self, skill: Skill) -> list[Ability]:
        """The abilities a check with `skill` may use: the default one, or every
        override granted for it (the character uses the best -
        CharacterStatBlock.get_skill_ability)."""
        return self._skill_ability_overrides.get(skill) or [
            self.get_default_skill_to_ability_mapping()[skill]
        ]

    def get_skill_ability(self, skill: Skill) -> Ability:
        abilities = self.get_skill_abilities(skill)
        if len(abilities) > 1:
            raise ValueError(
                f"{skill} has several ability overrides; the best one depends on "
                "ability scores - use CharacterStatBlock.get_skill_ability."
            )
        return abilities[0]

    def update_skill_to_ability(self, skill: Skill, ability: Ability):
        overrides = self._skill_ability_overrides.setdefault(skill, [])
        if ability not in overrides:
            overrides.append(ability)

    def reset_skill_to_ability(self, skill: Skill):
        self._skill_ability_overrides.pop(skill, None)

    def reset_all_skill_to_ability(self):
        self._skill_ability_overrides.clear()

    def get_default_skill_to_ability_mapping(self) -> dict[Skill, Ability]:
        return {
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


class ClassSkillsStatBlock(SkillsStatBlock):

    def __init__(
        self,
        character_class: Definitions.CharacterClass,
        allowed_skills: list[Skill],
        num_proficiencies: int,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        for skill, proficient in proficiencies.items():
            if proficient and skill not in allowed_skills:
                raise ValueError(f"Invalid skill for {character_class.value}: {skill}")

        proficient_counter = sum(
            1 for skill in allowed_skills if proficiencies.get(skill, False)
        )
        if proficient_counter != num_proficiencies:
            raise ValueError(
                f"{character_class.value} must be proficient in exactly {num_proficiencies} skills."
            )

        super().__init__(
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class PaladinSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.ATHLETICS,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.MEDICINE,
            Skill.PERSUASION,
            Skill.RELIGION,
        ]

        super().__init__(
            character_class=Definitions.CharacterClass.PALADIN,
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class FighterSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.ACROBATICS,
            Skill.ANIMAL_HANDLING,
            Skill.ATHLETICS,
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.PERSUASION,
            Skill.PERCEPTION,
            Skill.SURVIVAL,
        ]

        super().__init__(
            character_class=Definitions.CharacterClass.FIGHTER,
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class WarlockSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
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
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class RangerSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
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
            character_class=Definitions.CharacterClass.RANGER,
            allowed_skills=allowed_skills,
            num_proficiencies=3,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class WizardSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
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
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class BarbarianSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.ANIMAL_HANDLING,
            Skill.ATHLETICS,
            Skill.INTIMIDATION,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.SURVIVAL,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.BARBARIAN,
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class RogueSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.ACROBATICS,
            Skill.ATHLETICS,
            Skill.DECEPTION,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.INVESTIGATION,
            Skill.PERCEPTION,
            Skill.PERSUASION,
            Skill.SLEIGHT_OF_HAND,
            Skill.STEALTH,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.ROGUE,
            allowed_skills=allowed_skills,
            num_proficiencies=4,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class DruidSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.ARCANA,
            Skill.ANIMAL_HANDLING,
            Skill.INSIGHT,
            Skill.MEDICINE,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.RELIGION,
            Skill.SURVIVAL,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.DRUID,
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class ClericSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.MEDICINE,
            Skill.PERSUASION,
            Skill.RELIGION,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.CLERIC,
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class BardSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = list(Skill)
        super().__init__(
            character_class=Definitions.CharacterClass.BARD,
            allowed_skills=allowed_skills,
            num_proficiencies=3,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class SorcererSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.ARCANA,
            Skill.DECEPTION,
            Skill.INSIGHT,
            Skill.INTIMIDATION,
            Skill.PERSUASION,
            Skill.RELIGION,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.SORCERER,
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class MonkSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.ACROBATICS,
            Skill.ATHLETICS,
            Skill.HISTORY,
            Skill.INSIGHT,
            Skill.RELIGION,
            Skill.STEALTH,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.MONK,
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )


class ArtificerSkillsStatBlock(ClassSkillsStatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        allowed_skills = [
            Skill.ARCANA,
            Skill.HISTORY,
            Skill.INVESTIGATION,
            Skill.MEDICINE,
            Skill.NATURE,
            Skill.PERCEPTION,
            Skill.SLEIGHT_OF_HAND,
        ]
        super().__init__(
            character_class=Definitions.CharacterClass.ARTIFICER,
            allowed_skills=allowed_skills,
            num_proficiencies=2,
            proficiencies=proficiencies,
            bonuses=bonuses,
            dice_roll_conditions=dice_roll_conditions,
        )
