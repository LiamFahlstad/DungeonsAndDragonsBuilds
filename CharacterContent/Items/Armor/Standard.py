import Core.Definitions as Definitions
from Core.Definitions import Ability

from .Base import AbstractArmor


class PaddedArmor(AbstractArmor):
    """Light armor made of quilted layers of cloth and batting."""

    def base_stats(self) -> None:
        self.name = "Padded Armor"
        self.base_ac = 11
        self.ac_ability = Ability.DEXTERITY
        self.stealth_disadvantage = True
        self.weight = 8
        self.value = 5
        self.armor_type = Definitions.ArmorType.LIGHT


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


class HideArmor(AbstractArmor):
    """Medium armor made of thick furs and pelts."""

    def base_stats(self) -> None:
        self.name = "Hide Armor"
        self.base_ac = 12
        self.ac_ability = Ability.DEXTERITY
        self.weight = 12
        self.value = 10
        self.armor_type = Definitions.ArmorType.MEDIUM


class ChainShirtArmor(AbstractArmor):
    """Medium armor made of mail rings sewn into a shirt."""

    def base_stats(self) -> None:
        self.name = "Chain Shirt Armor"
        self.base_ac = 13
        self.ac_ability = Ability.DEXTERITY
        self.weight = 20
        self.value = 50
        self.armor_type = Definitions.ArmorType.MEDIUM


class ScaleMailArmor(AbstractArmor):
    """Medium armor of overlapping metal scales sewn to a backing."""

    def base_stats(self) -> None:
        self.name = "Scale Mail Armor"
        self.base_ac = 14
        self.ac_ability = Ability.DEXTERITY
        self.stealth_disadvantage = True
        self.weight = 45
        self.value = 50
        self.armor_type = Definitions.ArmorType.MEDIUM


class BreastplateArmor(AbstractArmor):
    """Medium armor of a fitted metal chestpiece over a leather harness."""

    def base_stats(self) -> None:
        self.name = "Breastplate"
        self.base_ac = 14
        self.ac_ability = Ability.DEXTERITY
        self.weight = 20
        self.value = 400
        self.armor_type = Definitions.ArmorType.MEDIUM


class HalfPlateArmor(AbstractArmor):
    """Medium armor of shaped metal plates covering most of the body."""

    def base_stats(self) -> None:
        self.name = "Half Plate Armor"
        self.base_ac = 15
        self.ac_ability = Ability.DEXTERITY
        self.stealth_disadvantage = True
        self.weight = 40
        self.value = 750
        self.armor_type = Definitions.ArmorType.MEDIUM


class RingMailArmor(AbstractArmor):
    """Heavy armor of leather with metal rings sewn into it."""

    def base_stats(self) -> None:
        self.name = "Ring Mail Armor"
        self.base_ac = 14
        self.ac_ability = None
        self.stealth_disadvantage = True
        self.weight = 40
        self.value = 30
        self.armor_type = Definitions.ArmorType.HEAVY


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


class SplintArmor(AbstractArmor):
    """Heavy armor of narrow vertical metal strips riveted to a leather backing."""

    def base_stats(self) -> None:
        self.name = "Splint Armor"
        self.base_ac = 17
        self.ac_ability = None
        self.strength_requirement = 15
        self.stealth_disadvantage = True
        self.weight = 60
        self.value = 200
        self.armor_type = Definitions.ArmorType.HEAVY


class PlateArmor(AbstractArmor):
    """Heavy armor of shaped, interlocking metal plates covering the entire body."""

    def base_stats(self) -> None:
        self.name = "Plate Armor"
        self.base_ac = 18
        self.ac_ability = None
        self.strength_requirement = 15
        self.stealth_disadvantage = True
        self.weight = 65
        self.value = 1500
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
