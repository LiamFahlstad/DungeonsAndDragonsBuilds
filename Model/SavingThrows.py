import attr

from Core.Definitions import Ability, DiceRollCondition, combine_roll_conditions
from Model.Bonuses import Bonuses
from Model.Contracts import Formula, StatView
from Model.Recorder import Recorder, records


@attr.s(frozen=True, auto_attribs=True)
class ConditionalProficiency:
    """Proficiency in `ability`; if the character already has it, in the
    first of `alternatives` they lack instead."""

    ability: Ability
    alternatives: tuple[Ability, ...]

    @property
    def choices(self) -> tuple[Ability, ...]:
        """Every ability it may grant, in order of preference."""
        return (self.ability, *self.alternatives)

    def sort_key(self) -> list[int]:
        """Its choices, by position in Ability order."""
        ability_order = list(Ability)
        return [ability_order.index(choice) for choice in self.choices]


class SavingThrows(Recorder):
    """Saving throw proficiencies, Advantage and bonuses.

    Merge rule: proficiency and Advantage are set unions ("or another one if
    you already have it" grants resolve against all the others, in Ability
    order), and bonuses sum (see Bonuses)."""

    def __init__(self):
        self._proficiencies: set[Ability] = set()
        self._advantages: set[Ability] = set()
        # Per-ability flat and formula-valued bonuses, each with a source
        # (see Model/Bonuses.py).
        self._bonuses: dict[Ability, Bonuses] = {}
        # "Proficiency in X; if you already have it, in Y instead" grants,
        # resolved on read - see _resolved_proficiencies.
        self._conditional_proficiencies: list[ConditionalProficiency] = []

    def is_proficient(self, ability: Ability) -> bool:
        return ability in self._resolved_proficiencies()

    @records
    def add_proficiency(self, ability: Ability) -> None:
        self._proficiencies.add(ability)

    @records
    def add_proficiency_or_alternative(
        self, ability: Ability, alternatives: list[Ability]
    ) -> None:
        """Proficiency in `ability`, or - if the character is proficient in it
        from anything else - in the first of `alternatives` they lack."""
        grant = ConditionalProficiency(ability, tuple(alternatives))
        self._conditional_proficiencies.append(grant)

    def _resolved_proficiencies(self) -> set[Ability]:
        """Every proficient ability. Conditional grants resolve against all
        the other grants, not just those applied before them, and in a fixed
        order, so the result doesn't depend on grant order."""
        proficient = set(self._proficiencies)
        grants = sorted(
            self._conditional_proficiencies, key=ConditionalProficiency.sort_key
        )
        for grant in grants:
            for choice in grant.choices:
                if choice not in proficient:
                    proficient.add(choice)
                    break
        return proficient

    def is_advantaged(self, ability: Ability) -> bool:
        return ability in self._advantages

    @records
    def add_advantage(self, ability: Ability) -> None:
        self._advantages.add(ability)

    def _bonuses_for(self, ability: Ability) -> Bonuses:
        return self._bonuses.setdefault(ability, Bonuses())

    @records
    def add_bonus(self, ability: Ability, bonus: int) -> None:
        self._bonuses_for(ability).add(bonus)

    @records
    def add_derived_bonus(self, ability: Ability, bonus: Formula) -> None:
        self._bonuses_for(ability).add_formula(bonus)

    def get_total_bonus(self, ability: Ability, view: StatView) -> int:
        """The flat bonus plus every formula-valued bonus, resolved against
        `view` (not the ability modifier or proficiency bonus - see
        modifier())."""
        bonuses = self._bonuses.get(ability)
        return bonuses.total(view) if bonuses is not None else 0

    # -- Resolvers: final values, worked out against the finished character --

    def modifier(self, ability: Ability, view: StatView) -> int:
        """Ability modifier, plus the proficiency bonus if proficient, plus
        every bonus."""
        proficiency = view.get_proficiency_bonus() if self.is_proficient(ability) else 0
        return (
            view.get_ability_modifier(ability)
            + proficiency
            + self.get_total_bonus(ability, view)
        )

    def roll_condition(self, ability: Ability, view: StatView) -> DiceRollCondition:
        """Advantage from any grant, Disadvantage from untrained armor
        (Strength and Dexterity saves); both cancel out."""
        conditions = set()
        if self.is_advantaged(ability):
            conditions.add(DiceRollCondition.ADVANTAGE)
        if view.has_untrained_armor_disadvantage(ability):
            conditions.add(DiceRollCondition.DISADVANTAGE)
        return combine_roll_conditions(conditions)
