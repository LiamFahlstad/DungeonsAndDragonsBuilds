from typing import TYPE_CHECKING

from Model.Bonuses import Bonuses, DerivedBonus
from Model.Recorder import Recorder, records

if TYPE_CHECKING:
    from Model.Character import Character


class Speed(Recorder):
    """Base walking speed plus every bonus to it (flat or formula-valued -
    see Bonuses), e.g. "+10 feet while you aren't wearing Heavy armor".

    Merge rule: sum."""

    def __init__(self, base: int):
        self.base = base
        self.bonuses = Bonuses()

    @records
    def add_bonus(self, bonus: int) -> None:
        self.bonuses.add(bonus)

    @records
    def add_derived_bonus(self, bonus: DerivedBonus) -> None:
        self.bonuses.add_formula(bonus)

    def total(self, character: "Character") -> int:
        return self.base + self.bonuses.total(character)
