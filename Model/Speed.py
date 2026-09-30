from typing import TYPE_CHECKING

from Model.Bonuses import Bonuses, DerivedBonus

if TYPE_CHECKING:
    from Model.Character import Character


class Speed:
    """Base walking speed plus every bonus to it (flat or formula-valued -
    see Bonuses), e.g. "+10 feet while you aren't wearing Heavy armor"."""

    def __init__(self, base: int):
        self.base = base
        self.bonuses = Bonuses()

    def add_bonus(self, bonus: int) -> None:
        self.bonuses.add(bonus)

    def add_derived_bonus(self, bonus: DerivedBonus) -> None:
        self.bonuses.add_formula(bonus)

    def total(self, character: "Character") -> int:
        return self.base + self.bonuses.total(character)
