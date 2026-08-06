import Core.Definitions as Definitions
from Core.Definitions import Ability

from .Base import AbstractArmor


class LeatherArmor(AbstractArmor):
    """Light armor made of hardened leather."""

    def base_stats(self) -> None:
        self.name = "Leather Armor"
        self.base_ac = 11
        self.ac_ability = Ability.DEXTERITY
        self.weight = 10
        self.value = 10
        self.armor_type = Definitions.ArmorType.LIGHT


class StuddedLeatherArmor(AbstractArmor):
    """Light armor of leather studded with metal."""

    def base_stats(self) -> None:
        self.name = "Studded Leather Armor"
        self.base_ac = 12
        self.ac_ability = Ability.DEXTERITY
        self.weight = 13
        self.value = 45
        self.armor_type = Definitions.ArmorType.LIGHT


class ChainShirtArmor(AbstractArmor):
    """Medium armor made of mail rings sewn into a shirt."""

    def base_stats(self) -> None:
        self.name = "Chain Shirt Armor"
        self.base_ac = 13
        self.ac_ability = Ability.DEXTERITY
        self.weight = 20
        self.value = 50
        self.armor_type = Definitions.ArmorType.MEDIUM


class ChainMailArmor(AbstractArmor):
    """Heavy armor made of interlocking metal rings."""

    def base_stats(self) -> None:
        self.name = "Chain Mail Armor"
        self.base_ac = 16
        self.ac_ability = None
        self.strength_requirement = 13
        self.stealth_disadvantage = True
        self.weight = 55
        self.value = 75
        self.armor_type = Definitions.ArmorType.HEAVY


class ShieldArmor(AbstractArmor):
    """A wooden or metal shield held in one hand."""

    def base_stats(self) -> None:
        self.name = "Shield"
        self.base_ac = 0
        self.ac_ability = None
        self.is_shield = True
        self.ac_bonus = 2
        self.weight = 6
        self.value = 10
        self.armor_type = Definitions.ArmorType.SHIELD


# ──────────────────────────────────────────────────────────────────────────────
# Magical Armor
# ──────────────────────────────────────────────────────────────────────────────
