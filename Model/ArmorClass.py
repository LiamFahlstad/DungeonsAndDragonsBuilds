from dataclasses import dataclass
from typing import Optional

from Core.Definitions import Ability
from Core.Rules import UNARMORED_AC_BASE
from Model.Bonuses import Bonuses
from Model.View import CharacterView, Value
from Model.Recorder import Recorder, records


@dataclass(frozen=True)
class ArmorClassFormula:
    """One way to calculate base AC: `base` + the summed modifiers of
    `abilities`, capped at `ability_modifier_cap` (None = uncapped).

    A character with several formulas uses the best one that applies (the
    rules let you pick one), so granting another never overwrites anything:
    - is_armor: worn body armor. While any is worn, only armor formulas apply
      - it replaces every "while you aren't wearing armor" formula.
    - allows_shield: False for formulas that stop working while a Shield is
      wielded (Monk's Unarmored Defense).
    """

    base: int
    abilities: frozenset[Ability]
    ability_modifier_cap: Optional[int] = None
    is_armor: bool = False
    allows_shield: bool = True


# Everyone's AC without armor or a feature: 10 + Dexterity modifier.
UNARMORED_ARMOR_CLASS = ArmorClassFormula(
    base=UNARMORED_AC_BASE, abilities=frozenset({Ability.DEXTERITY})
)


class ArmorClass(Recorder):
    """Every AC formula and AC bonus. What's worn (Model.WornArmor) and
    the wielder's ability modifiers and Shield training aren't this part's
    concern, so total() reads them through the view.

    Merge rule: the best applicable formula (only its value is used, so the
    order formulas were granted in can't matter), plus the sum of bonuses
    and Shield bonuses."""

    def __init__(self):
        self.armor_class_formulas: list[ArmorClassFormula] = [UNARMORED_ARMOR_CLASS]
        self.bonuses = Bonuses()
        # A wielded Shield's AC bonus; only counts with Shield training.
        self._shield_bonuses: list[int] = []

    @records
    def add_armor_class_formula(self, formula: ArmorClassFormula) -> None:
        self.armor_class_formulas.append(formula)

    @records
    def add_bonus(self, bonus: Value) -> None:
        self.bonuses.add(bonus)

    @records
    def add_shield_bonus(self, armor_class_bonus: int) -> None:
        """A wielded Shield's AC bonus (only counts with Shield training)."""
        self._shield_bonuses.append(armor_class_bonus)

    def get_applicable_armor_class_formulas(
        self, is_wielding_shield: bool
    ) -> list[ArmorClassFormula]:
        armor = [formula for formula in self.armor_class_formulas if formula.is_armor]
        if armor:
            return armor
        return [
            formula
            for formula in self.armor_class_formulas
            if formula.allows_shield or not is_wielding_shield
        ]

    def total(self, view: CharacterView, ignore_shield: bool = False) -> int:
        """The best applicable AC formula plus every AC bonus. ignore_shield:
        the AC with the Shield set aside (its bonus gone, and formulas it
        disables - Monk's Unarmored Defense - available again). A Shield's
        bonus only counts with Shield training."""
        is_wielding_shield = view.is_wielding_shield and not ignore_shield
        has_shield_training = view.has_shield_training
        formulas = self.get_applicable_armor_class_formulas(is_wielding_shield)
        base = max(self._from_formula(formula, view) for formula in formulas)
        bonus = self.bonuses.total(view)
        shield = (
            sum(self._shield_bonuses)
            if is_wielding_shield and has_shield_training
            else 0
        )
        return base + bonus + shield

    def _from_formula(self, formula: ArmorClassFormula, view: CharacterView) -> int:
        ability_modifier = sum(
            view.get_ability_modifier(ability) for ability in formula.abilities
        )
        if formula.ability_modifier_cap is not None:
            ability_modifier = min(ability_modifier, formula.ability_modifier_cap)
        return formula.base + ability_modifier
