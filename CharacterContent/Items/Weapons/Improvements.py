from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from Core.Definitions import Ability
from CharacterContent.Features.Core.Improvements import ItemImprovement
from .Enums import WeaponProperty, WeaponDamageRolls, WeaponDamageTypes

if TYPE_CHECKING:
    # AbstractWeapon is only used as a quoted forward-ref annotation below;
    # a real import would cycle with base.py (which needs ExtraDamage from
    # this module).
    from .Base import AbstractWeapon


@dataclass
class ExtraDamage:
    """Represents bonus damage added to a weapon attack."""
    damage_roll: "WeaponDamageRolls"
    damage_type: WeaponDamageTypes
    note: Optional[str] = None  # e.g. "chosen type, activate as bonus action"

    def format_damage(self) -> str:
        """Format as '1d6 Fire' or similar."""
        return f"{self.damage_roll.value} {self.damage_type.value}"


# ──────────────────────────────────────────────────────────────────────────────
# WeaponImprovement: composable modifiers applied to a weapon at construction
# time (e.g. a magic weapon variant, or a homebrew reskin). Mirrors
# CharacterContent.Features.Core.Improvements.CharacterImprovement, but its apply() mutates the weapon
# instance instead of the character stat block, since these improvements
# (attack/damage bonuses, damage die/type, properties, flavor text) are
# properties of the weapon itself, not of the wielder.
# ──────────────────────────────────────────────────────────────────────────────


class WeaponImprovement(ItemImprovement):
    """Base class for weapon improvements. Override apply() to modify the weapon."""

    @abstractmethod
    def apply(self, weapon: "AbstractWeapon") -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        # Renaming ItemImprovement.apply's generic `item` param to `weapon`
        # here (and to `armor` in ArmorImprovement) is intentional - it's
        # far more readable in every weapon-specific apply() below than a
        # generic `item` would be. Pyright's override check wants the exact
        # same parameter name, so it's silenced just for this one rule.
        pass


class SetAttackRollBonus(WeaponImprovement):
    """Overrides the weapon's total attack roll bonus with a fixed value,
    ignoring ability modifier, proficiency, and any additive bonuses."""

    def __init__(self, value: int):
        self.value = value

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._attack_roll_override = self.value


class AddAttackRollBonus(WeaponImprovement):
    """Adds a flat bonus to the weapon's attack roll."""

    def __init__(self, value: int, reason: str = "Bonus"):
        self.value = value
        self.reason = reason

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.attack_roll_bonuses.append((self.value, f"{self.value} ({self.reason})"))


class SetDamageRollBonus(WeaponImprovement):
    """Overrides the weapon's damage bonus (the flat number added to the
    damage die), ignoring the ability modifier and any additive bonuses."""

    def __init__(self, value: int):
        self.value = value

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._damage_bonus_override = self.value


class AddDamageRollBonus(WeaponImprovement):
    """Adds a flat bonus to the weapon's damage roll."""

    def __init__(self, value: int, reason: str = "Bonus"):
        self.value = value
        self.reason = reason

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.damage_roll_bonuses.append((self.value, f"{self.value} ({self.reason})"))


class SetDamageDie(WeaponImprovement):
    """Overrides the weapon's damage die (e.g. upgrading a Longsword to 2d6)."""

    def __init__(self, damage_roll: WeaponDamageRolls):
        self.damage_roll = damage_roll

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.damage_roll = self.damage_roll


class SetDamageType(WeaponImprovement):
    """Overrides the weapon's damage type (e.g. a frost blade dealing Cold instead of Slashing)."""

    def __init__(self, damage_type: WeaponDamageTypes):
        self.damage_type = damage_type

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.damage_type = self.damage_type


class AddWeaponProperty(WeaponImprovement):
    """Adds a weapon property (e.g. Finesse, Reach) not already on the weapon."""

    def __init__(self, property: WeaponProperty):
        self.property = property

    def apply(self, weapon: "AbstractWeapon") -> None:
        if self.property not in weapon.properties:
            weapon.properties.append(self.property)


class AddExtraDamage(WeaponImprovement):
    """Adds extra damage dice to the weapon's attack (e.g. a flaming blade's extra 1d6 Fire)."""

    def __init__(
        self,
        damage_roll: WeaponDamageRolls,
        damage_type: WeaponDamageTypes,
        note: Optional[str] = None,
    ):
        self.extra_damage = ExtraDamage(damage_roll=damage_roll, damage_type=damage_type, note=note)

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.extra_damage.append(self.extra_damage)


class SetWeaponAbility(WeaponImprovement):
    """Overrides which ability score is used for the weapon's attack and damage
    rolls (e.g. a Bladesinger using Intelligence instead of Strength/Dexterity),
    replacing the weapon's own ability - and any Finesse Str/Dex comparison -
    outright rather than only being considered as an alternative."""

    def __init__(self, ability: Ability):
        self.ability = ability

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._ability_override = self.ability
