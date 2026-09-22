from Core.Definitions import Ability
from .Base import AbstractWeapon
from .Enums import WeaponMastery, WeaponProperty, WeaponType, WeaponDamageRolls, WeaponDamageTypes

### WEAPON FAMILIES (homebrew: Sword/Axe/Mace/Hammer/Spear, each spanning 1d4-2d6.
### Light/Medium are Simple Melee; Heavy/Greater/Massive/Colossal are Martial Melee.
### Properties/mastery are consistent within each family across all six tiers.
### Canonical weapons in SimpleMelee.py/MartialMelee.py that mechanically match a
### family+tier inherit from these classes instead of AbstractWeapon directly.


class SwordLight(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sword Light"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D4
        self.weight = 1
        self.value = 10
        self.is_homebrew = True


class SwordMedium(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sword Medium"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 3
        self.value = 20
        self.is_homebrew = True


class SwordHeavy(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sword Heavy"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 4
        self.value = 30
        self.is_homebrew = True


class SwordGreater(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sword Greater"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D10
        self.weight = 5
        self.value = 40
        self.is_homebrew = True


class SwordMassive(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sword Massive"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D12
        self.weight = 6
        self.value = 50
        self.is_homebrew = True


class SwordColossal(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sword Colossal"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D6x2
        self.weight = 7
        self.value = 65
        self.is_homebrew = True


class AxeLight(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Axe Light"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.LIGHT, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D4
        self.weight = 1
        self.value = 3
        self.is_homebrew = True


class AxeMedium(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Axe Medium"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.THROWN]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 2
        self.value = 6
        self.is_homebrew = True


class AxeHeavy(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Axe Heavy"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 4
        self.value = 10
        self.is_homebrew = True


class AxeGreater(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Axe Greater"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D10
        self.weight = 6
        self.value = 20
        self.is_homebrew = True


class AxeMassive(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Axe Massive"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D12
        self.weight = 7
        self.value = 30
        self.is_homebrew = True


class AxeColossal(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Axe Colossal"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D6x2
        self.weight = 8
        self.value = 40
        self.is_homebrew = True


class MaceLight(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Mace Light"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D4
        self.weight = 2
        self.value = 1
        self.is_homebrew = True


class MaceMedium(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Mace Medium"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 4
        self.value = 5
        self.is_homebrew = True


class MaceHeavy(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Mace Heavy"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 5
        self.value = 8
        self.is_homebrew = True


class MaceGreater(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Mace Greater"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY]
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D10
        self.weight = 6
        self.value = 12
        self.is_homebrew = True


class MaceMassive(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Mace Massive"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D12
        self.weight = 8
        self.value = 18
        self.is_homebrew = True


class MaceColossal(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Mace Colossal"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D6x2
        self.weight = 10
        self.value = 25
        self.is_homebrew = True


class HammerLight(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Hammer Light"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.LIGHT, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D4
        self.weight = 2
        self.value = 2
        self.is_homebrew = True


class HammerMedium(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Hammer Medium"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.THROWN]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 3
        self.value = 6
        self.is_homebrew = True


class HammerHeavy(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Hammer Heavy"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 4
        self.value = 15
        self.is_homebrew = True


class HammerGreater(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Hammer Greater"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D10
        self.weight = 6
        self.value = 20
        self.is_homebrew = True


class HammerMassive(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Hammer Massive"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D12
        self.weight = 8
        self.value = 25
        self.is_homebrew = True


class HammerColossal(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Hammer Colossal"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D6x2
        self.weight = 10
        self.value = 30
        self.is_homebrew = True


class SpearLight(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Spear Light"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D4
        self.weight = 1
        self.value = 1
        self.is_homebrew = True


class SpearMedium(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Spear Medium"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.THROWN, WeaponProperty.VERSATILE_8]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 3
        self.value = 1
        self.is_homebrew = True


class SpearHeavy(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Spear Heavy"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 4
        self.value = 10
        self.is_homebrew = True


class SpearGreater(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Spear Greater"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.REACH, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D10
        self.weight = 6
        self.value = 10
        self.is_homebrew = True


class SpearMassive(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Spear Massive"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.REACH, WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D12
        self.weight = 7
        self.value = 20
        self.is_homebrew = True


class SpearColossal(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Spear Colossal"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.REACH, WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D6x2
        self.weight = 8
        self.value = 25
        self.is_homebrew = True


### DAGGER FAMILY (homebrew: finesse piercing blades - Dagger/Shortsword/Rapier
### shaped, the one real size progression 5e2024 canon has for this shape.
### Unlike the five families above, this one does NOT span the full 1d4-2d6
### range - it stops at Heavy (1d8), since bigger than that stops being a
### thrusting blade. Light is Simple Melee (like Dagger); Medium and Heavy are
### Martial Melee (like Shortsword and Rapier). Light/Medium keep the Light
### property (Nick mastery requires it); Heavy loses Light as the blade grows
### too big to conceal or off-hand (matching the real Rapier, which uses Vex
### mastery instead - canon confirms Vex does not require Light).


class DaggerLight(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Dagger Light"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D4
        self.weight = 1
        self.value = 5
        self.is_homebrew = True


class DaggerMedium(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Dagger Medium"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 2
        self.value = 15
        self.is_homebrew = True


class DaggerHeavy(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Dagger Heavy"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 2
        self.value = 20
        self.is_homebrew = True
