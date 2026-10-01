from typing import TYPE_CHECKING, Iterable

from Core.Definitions import DiceRollCondition, combine_roll_conditions
from Model.Bonuses import Bonuses, DerivedBonus
from Model.Recorder import Recorder, records

if TYPE_CHECKING:
    from Model.Character import Character


class Initiative(Recorder):
    """Every source of an initiative bonus or roll condition. The character
    combines the bonus total with the Dexterity modifier (for the initiative
    score) and the roll condition with untrained-armor Disadvantage (neither
    is this part's concern - see Character.calculate_initiative() /
    .initiative_roll_condition)."""

    def __init__(self):
        self.proficiency = False
        self.bonuses = Bonuses()
        self._roll_conditions: set[DiceRollCondition] = set()

    @records
    def add_proficiency(self) -> None:
        self.proficiency = True

    @records
    def add_roll_condition(self, condition: DiceRollCondition) -> None:
        self._roll_conditions.add(condition)

    @records
    def add_bonus(self, bonus: int) -> None:
        self.bonuses.add(bonus)

    @records
    def add_derived_bonus(self, bonus: DerivedBonus) -> None:
        self.bonuses.add_formula(bonus)

    def total(self, proficiency_bonus: int, character: "Character") -> int:
        """The bonus total (not the ability modifier): the full proficiency
        bonus if proficient, plus every flat and formula-valued bonus."""
        proficiency = proficiency_bonus if self.proficiency else 0
        return proficiency + self.bonuses.total(character)

    def roll_condition(
        self, extra: Iterable[DiceRollCondition] = ()
    ) -> DiceRollCondition:
        """This part's own roll condition combined with `extra` sources (e.g.
        untrained-armor Disadvantage) - combined together, not one after the
        other, so two sources that would each cancel out on their own still
        cancel correctly when combined with `extra`."""
        return combine_roll_conditions(self._roll_conditions | set(extra))
