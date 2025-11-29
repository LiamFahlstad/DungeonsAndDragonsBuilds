from Definitions import Ability, Skill, DiceRollCondition
import Definitions


class StatBlock:
    pass


class AbilitiesStatBlock(StatBlock):
    def __init__(
        self,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma

    def add_bonus(self, ability: Ability, bonus: int):
        if not isinstance(bonus, int):
            raise ValueError("Bonus must be an integer.")
        if ability == Ability.STRENGTH:
            self.strength += bonus
        elif ability == Ability.DEXTERITY:
            self.dexterity += bonus
        elif ability == Ability.CONSTITUTION:
            self.constitution += bonus
        elif ability == Ability.INTELLIGENCE:
            self.intelligence += bonus
        elif ability == Ability.WISDOM:
            self.wisdom += bonus
        elif ability == Ability.CHARISMA:
            self.charisma += bonus
        else:
            raise ValueError("Invalid ability.")

    def get_score(self, ability: Ability):
        return getattr(self, ability.name.lower())

    def get_modifier(self, ability: Ability):
        score = self.get_score(ability)
        return (score - 10) // 2


class SavingThrowsStatBlock(StatBlock):
    def __init__(
        self,
        proficiencies: dict[Ability, bool] = None,
        advantages: dict[Ability, bool] = None,
    ):
        self.proficiencies = proficiencies if proficiencies is not None else {}
        self.advantages = advantages if advantages is not None else {}

    def is_proficient(self, ability: Ability) -> bool:
        return self.proficiencies.get(ability, False)

    def is_advantaged(self, ability: Ability) -> bool:
        return self.advantages.get(ability, False)


class SkillsStatBlock(StatBlock):
    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: dict[Skill, int] = None,
        dice_roll_conditions: dict[Skill, DiceRollCondition] = None,
    ):
        self.proficiencies = proficiencies
        self.bonuses = bonuses if bonuses is not None else {}
        self.dice_roll_conditions = (
            dice_roll_conditions if dice_roll_conditions is not None else {}
        )

    def add_skill_proficiency(self, skill: Skill):
        self.proficiencies[skill] = True

    def is_proficient(self, skill: Skill) -> bool:
        return self.proficiencies.get(skill, False)

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


class CombatStatBlock(StatBlock):
    def __init__(self, hit_die: int, speed: int, size: Definitions.CreatureSize):
        self.hit_die = hit_die
        self.hit_points_bonus = 0
        self.speed = speed
        self.size = size
        self.armor_class_without_bonus = 10
        self.armor_class_bonus = 0
        self.initiative_bonus = 0  # Overridden during character creation
        self.weapons_masteries = []

    @property
    def average_hit_die(self) -> int:
        return (self.hit_die // 2) + 1

    @property
    def armor_class(self) -> int:
        return self.armor_class_without_bonus + self.armor_class_bonus

    @property
    def initiative(self) -> int:
        return self.initiative_bonus

    def calculate_hit_points(self, level: int, constitution_modifier: int) -> int:
        # First level: max hit die + constitution modifier
        hit_points = self.hit_die + constitution_modifier
        # Subsequent levels: average hit die + constitution modifier
        for _ in range(1, level):
            hit_points += self.average_hit_die + constitution_modifier
        return hit_points + self.hit_points_bonus


class StandardArrayAbilitiesStatBlock(AbilitiesStatBlock):
    def __init__(
        self,
        strength: int,
        dexterity: int,
        constitution: int,
        intelligence: int,
        wisdom: int,
        charisma: int,
    ):
        values_needed = {8, 10, 12, 13, 14, 15}
        provided_values = {
            strength,
            dexterity,
            constitution,
            intelligence,
            wisdom,
            charisma,
        }
        if values_needed != provided_values:
            raise ValueError(
                "StandardArrayAbilitiesStatBlock must use the standard array values: 15, 14, 13, 12, 10, 8"
            )
        super().__init__(
            strength, dexterity, constitution, intelligence, wisdom, charisma
        )


### PALADIN
class ClassSkillsStatBlock(SkillsStatBlock):
    """Paladin Skills Stat Block"""

    def __init__(
        self,
        character_class: Definitions.CharacterClass,
        excepted_skills: list[Skill],
        num_proficiencies: int,
        proficiencies: dict[Skill, bool],
        bonuses: dict[Skill, int] = None,
        dice_roll_conditions: dict[Skill, DiceRollCondition] = None,
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
        bonuses: dict[Skill, int] = None,
        dice_roll_conditions: dict[Skill, DiceRollCondition] = None,
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


class PaladinSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.WISDOM: True,
                Ability.CHARISMA: True,
            }
        )


### Fighter
class FighterSkillsStatBlock(ClassSkillsStatBlock):
    """Fighter Skills Stat Block"""

    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: dict[Skill, int] = None,
        dice_roll_conditions: dict[Skill, DiceRollCondition] = None,
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


class FighterSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.STRENGTH: True,
                Ability.CONSTITUTION: True,
            }
        )


### Warlock
class WarlockSkillsStatBlock(ClassSkillsStatBlock):
    """Warlock Skills Stat Block"""

    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: dict[Skill, int] = None,
        dice_roll_conditions: dict[Skill, DiceRollCondition] = None,
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


class WarlockSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.WISDOM: True,
                Ability.CHARISMA: True,
            }
        )


### Ranger
class RangerSkillsStatBlock(ClassSkillsStatBlock):
    """Ranger Skills Stat Block"""

    def __init__(
        self,
        proficiencies: dict[Skill, bool],
        bonuses: dict[Skill, int] = None,
        dice_roll_conditions: dict[Skill, DiceRollCondition] = None,
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


class RangerSavingThrowsStatBlock(SavingThrowsStatBlock):
    def __init__(self):
        super().__init__(
            proficiencies={
                Ability.STRENGTH: True,
                Ability.DEXTERITY: True,
            }
        )
