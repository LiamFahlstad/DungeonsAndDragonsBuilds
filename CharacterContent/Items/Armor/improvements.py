from abc import abstractmethod
from typing import Optional
from Core.Definitions import Ability
from CharacterContent.Features.Core.Improvements import ItemImprovement
from .base import AbstractArmor


class ArmorImprovement(ItemImprovement):
    """Base class for armor improvements. Override apply() to modify the armor."""

    @abstractmethod
    def apply(self, armor: "AbstractArmor") -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        # Renaming ItemImprovement.apply's generic `item` param to `armor`
        # here (and to `weapon` in WeaponImprovement) is intentional - it's
        # far more readable in every armor-specific apply() below than a
        # generic `item` would be. Pyright's override check wants the exact
        # same parameter name, so it's silenced just for this one rule.
        pass


class SetArmorClassBase(ArmorImprovement):
    """Overrides the armor's base AC and ability modifier outright."""

    def __init__(self, base: int, ability: Optional[Ability]):
        self.base = base
        self.ability = ability

    def apply(self, armor: "AbstractArmor") -> None:
        armor.base_ac = self.base
        armor.ac_ability = self.ability


class AddArmorClassBonus(ArmorImprovement):
    """Adds a flat bonus to the armor's AC, stacking on top of its own ac_bonus."""

    def __init__(self, value: int, reason: str = "Bonus"):
        self.value = value
        self.reason = reason

    def apply(self, armor: "AbstractArmor") -> None:
        armor.ac_bonus += self.value


class SetStrengthRequirement(ArmorImprovement):
    """Overrides the armor's Strength requirement. Pass None to remove any requirement."""

    def __init__(self, min_score: Optional[int]):
        self.min_score = min_score

    def apply(self, armor: "AbstractArmor") -> None:
        armor.strength_requirement = self.min_score


class SetStealthDisadvantage(ArmorImprovement):
    """Overrides whether the armor imposes stealth disadvantage."""

    def __init__(self, value: bool = True):
        self.value = value

    def apply(self, armor: "AbstractArmor") -> None:
        armor.stealth_disadvantage = self.value
