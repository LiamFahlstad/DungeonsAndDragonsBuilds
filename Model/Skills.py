from typing import TYPE_CHECKING, Optional

from Core.Definitions import Ability, DiceRollCondition, Skill, combine_roll_conditions
from Model.Bonuses import Bonuses, DerivedBonus
from Model.Recorder import Recorder, records

if TYPE_CHECKING:
    from Model.Character import Character


class Skills(Recorder):
    def __init__(
        self,
        proficiencies: Optional[dict[Skill, bool]] = None,
        expertise: Optional[dict[Skill, bool]] = None,
        bonuses: Optional[dict[Skill, int]] = None,
        dice_roll_conditions: Optional[dict[Skill, DiceRollCondition]] = None,
    ):
        self.proficiencies = proficiencies if proficiencies is not None else {}
        self.expertise = expertise if expertise is not None else {}
        # Per-skill flat and formula-valued bonuses, each with a source (see
        # Model/Bonuses.py).
        self._bonuses: dict[Skill, Bonuses] = {}
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

    @records
    def add_skill_proficiency(self, skill: Skill):
        self.proficiencies[skill] = True

    def _bonuses_for(self, skill: Skill) -> Bonuses:
        return self._bonuses.setdefault(skill, Bonuses())

    @records
    def add_skill_bonus(self, skill: Skill, bonus: int, source: str = "Other"):
        self._bonuses_for(skill).add(bonus, source)

    @records
    def add_derived_bonus(
        self, skill: Skill, bonus: DerivedBonus, source: str = "Other"
    ) -> None:
        self._bonuses_for(skill).add_formula(bonus, source)

    def get_total_bonus(self, skill: Skill, character: "Character") -> int:
        """The flat bonus plus every formula-valued bonus, resolved against
        `character` (not the ability modifier or proficiency bonus - see
        Character.get_skill_modifier)."""
        bonuses = self._bonuses.get(skill)
        return bonuses.total(character) if bonuses is not None else 0

    def get_all_bonus_sources(
        self, skill: Skill, character: "Character"
    ) -> list[tuple[int, str]]:
        bonuses = self._bonuses.get(skill)
        return bonuses.sources(character) if bonuses is not None else []

    @records
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

    @records
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
        Character.get_skill_ability)."""
        return self._skill_ability_overrides.get(skill) or [
            self.get_default_skill_to_ability_mapping()[skill]
        ]

    def get_skill_ability(self, skill: Skill) -> Ability:
        abilities = self.get_skill_abilities(skill)
        if len(abilities) > 1:
            raise ValueError(
                f"{skill} has several ability overrides; the best one depends on "
                "ability scores - use Character.get_skill_ability."
            )
        return abilities[0]

    @records
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
