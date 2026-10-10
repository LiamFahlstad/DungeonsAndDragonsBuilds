from abc import abstractmethod
from typing import Optional
from Core.Definitions import Ability
from Model.Content.Improvements import ItemImprovement
from Model.Content.Armor import AbstractArmor


class ArmorImprovement(ItemImprovement):
    """Base class for armor improvements. Override apply() to modify the armor."""

    @abstractmethod
    def apply(self, armor: "AbstractArmor", /) -> None:
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
