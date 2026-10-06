from typing import Optional

from Core.Definitions import Ability, DiceRollCondition, Skill, combine_roll_conditions
from Core.Rules import EXPERTISE_MULTIPLIER
from Model.Bonuses import OTHER_SOURCE, Bonuses
from Model.Records.SourcedValue import SourcedValue
from Model.Contracts import StatView, Value
from Model.Recorder import Recorder, records


class Skills(Recorder):
    """Skill proficiencies, expertise, bonuses, roll conditions and ability
    overrides.

    Merge rule: proficiency, expertise and ability overrides are set unions,
    bonuses sum (see Bonuses), and Advantage and Disadvantage cancel. Reads
    list reasons sorted and abilities in Ability order."""

    def __init__(self):
        self._proficiencies: set[Skill] = set()
        self._expertise: set[Skill] = set()
        # Per-skill flat and formula-valued bonuses, each with a source (see
        # Model/Bonuses.py).
        self._bonuses: dict[Skill, Bonuses] = {}
        # Per-skill {condition: [reasons]} for every source of Advantage or
        # Disadvantage, so the effective condition can be worked out on read
        # (both cancel out) regardless of the order they were granted in.
        self._roll_condition_sources: dict[
            Skill, dict[DiceRollCondition, list[str]]
        ] = {}
        # Per-skill abilities that replace the default one (e.g. "use Wisdom
        # for Arcana"). See get_skill_abilities.
        self._skill_ability_overrides: dict[Skill, set[Ability]] = {}

    @records
    def add_skill_proficiency(self, skill: Skill):
        self._proficiencies.add(skill)

    def _bonuses_for(self, skill: Skill) -> Bonuses:
        return self._bonuses.setdefault(skill, Bonuses())

    @records
    def add_skill_bonus(self, skill: Skill, bonus: Value, source: str = OTHER_SOURCE):
        self._bonuses_for(skill).add(bonus, source)

    def get_total_bonus(self, skill: Skill, view: StatView) -> int:
        """The flat bonus plus every formula-valued bonus, resolved against
        `view` (not the ability modifier or proficiency bonus - see
        Character.get_skill_modifier)."""
        bonuses = self._bonuses.get(skill)
        return bonuses.total(view) if bonuses is not None else 0

    def get_all_bonus_sources(self, skill: Skill, view: StatView) -> list[SourcedValue]:
        bonuses = self._bonuses.get(skill)
        return bonuses.sources(view) if bonuses is not None else []

    @records
    def add_skill_expertise(self, skill: Skill):
        """Expertise requires proficiency, but that proficiency may come from
        a feature applied later (another class builder, the species), so the
        requirement is checked by validate() once every feature has applied
        rather than here - granting expertise is order-insensitive."""
        self._expertise.add(skill)

    def validate(self) -> None:
        for skill in Skill:
            if skill in self._expertise and not self.is_proficient(skill):
                raise ValueError(f"Cannot add expertise to unproficient skill: {skill}")

    def is_proficient(self, skill: Skill) -> bool:
        return skill in self._proficiencies

    def has_expertise(self, skill: Skill) -> bool:
        return skill in self._expertise

    def _recorded_roll_condition_sources(
        self, skill: Skill
    ) -> dict[DiceRollCondition, list[str]]:
        """{condition: [reasons]} for every recorded source (a copy), with
        conditions in DiceRollCondition order and reasons sorted."""
        recorded = self._roll_condition_sources.get(skill, {})
        return {
            condition: sorted(recorded[condition])
            for condition in DiceRollCondition
            if condition in recorded
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

    def get_skill_abilities(self, skill: Skill) -> list[Ability]:
        """The abilities a check with `skill` may use: the default one, or every
        override granted for it (see ability()), in Ability order."""
        overrides = self._skill_ability_overrides.get(skill)
        if not overrides:
            return [self.default_ability(skill)]
        return [ability for ability in Ability if ability in overrides]

    # ── Resolvers: final values, worked out against the finished character ──

    UNTRAINED_ARMOR_REASON = "Untrained armor"

    def ability(self, skill: Skill, view: StatView) -> Ability:
        """The ability a check with `skill` uses: the best of
        get_skill_abilities(). Ties go to the first in Ability order, so
        grant order never decides."""
        return max(self.get_skill_abilities(skill), key=view.get_ability_modifier)

    def modifier(self, skill: Skill, view: StatView) -> int:
        """Ability modifier, plus the proficiency bonus (twice with
        expertise), plus every bonus."""
        if self.has_expertise(skill):
            proficiency = EXPERTISE_MULTIPLIER * view.get_proficiency_bonus()
        elif self.is_proficient(skill):
            proficiency = view.get_proficiency_bonus()
        else:
            proficiency = 0
        ability_modifier = view.get_ability_modifier(self.ability(skill, view))
        return ability_modifier + proficiency + self.get_total_bonus(skill, view)

    def roll_condition_sources(
        self, skill: Skill, view: StatView
    ) -> dict[DiceRollCondition, list[str]]:
        """Every recorded source of Advantage/Disadvantage, plus Disadvantage
        from untrained armor when the check uses Strength or Dexterity."""
        sources = self._recorded_roll_condition_sources(skill)
        if view.has_untrained_armor_disadvantage(self.ability(skill, view)):
            sources.setdefault(DiceRollCondition.DISADVANTAGE, []).append(
                self.UNTRAINED_ARMOR_REASON
            )
        return sources

    def roll_condition(self, skill: Skill, view: StatView) -> DiceRollCondition:
        return combine_roll_conditions(self.roll_condition_sources(skill, view))

    def roll_condition_reasons(self, skill: Skill, view: StatView) -> list[str]:
        """The reasons behind the effective roll condition."""
        condition = self.roll_condition(skill, view)
        return self.roll_condition_sources(skill, view).get(condition, [])

    @records
    def update_skill_to_ability(self, skill: Skill, ability: Ability):
        self._skill_ability_overrides.setdefault(skill, set()).add(ability)

    @staticmethod
    def default_ability(skill: Skill) -> Ability:
        """The ability a check with `skill` uses without any override."""
        return DEFAULT_SKILL_ABILITIES[skill]


DEFAULT_SKILL_ABILITIES: dict[Skill, Ability] = {
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
