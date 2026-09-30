from typing import TYPE_CHECKING, Iterable

from Core.Definitions import DiceRollCondition, combine_roll_conditions
from StatBlocks.Bonuses import Bonuses, DerivedBonus

if TYPE_CHECKING:
    from StatBlocks.CharacterStatBlock import CharacterStatBlock


class Initiative:
    """Every source of an initiative bonus or roll condition. The character
    combines the bonus total with the Dexterity modifier (for the initiative
    score) and the roll condition with untrained-armor Disadvantage (neither
    is this part's concern - see CharacterStatBlock.calculate_initiative() /
    .initiative_roll_condition)."""

    def __init__(self):
        self.proficiency = False
        self.bonuses = Bonuses()
        self._roll_conditions: set[DiceRollCondition] = set()

    def add_proficiency(self) -> None:
        self.proficiency = True

    def add_roll_condition(self, condition: DiceRollCondition) -> None:
        self._roll_conditions.add(condition)

    def add_bonus(self, bonus: int) -> None:
        self.bonuses.add(bonus)

    def add_derived_bonus(self, bonus: DerivedBonus) -> None:
        self.bonuses.add_formula(bonus)

    def total(self, proficiency_bonus: int, character: "CharacterStatBlock") -> int:
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
