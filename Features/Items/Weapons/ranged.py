from Core.Definitions import Ability
from .base import AbstractWeapon
from .enums import WeaponMastery, WeaponProperty, WeaponType, WeaponsDamageRolls, WeaponsDamageTypes


class Dart(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Dart"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.SIMPLE_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D4
        self.weight = 0.25
        self.value = 0.05


class LightCrossbow(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Light Crossbow"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.AMMUNITION, WeaponProperty.TWO_HANDED, WeaponProperty.LOADING]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.SIMPLE_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 5
        self.value = 25


class Shortbow(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Shortbow"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.AMMUNITION, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.SIMPLE_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 2
        self.value = 25


class Sling(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sling"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.AMMUNITION]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.SIMPLE_RANGED
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D4
        self.value = 0.1


class Blowgun(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Blowgun"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.AMMUNITION, WeaponProperty.LOADING]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D1
        self.weight = 1
        self.value = 10


class HandCrossbow(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Hand Crossbow"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.AMMUNITION, WeaponProperty.LIGHT, WeaponProperty.LOADING]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 3
        self.value = 75


class HeavyCrossbow(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Heavy Crossbow"
        self.ability = Ability.DEXTERITY
        self.properties = [
            WeaponProperty.AMMUNITION,
            WeaponProperty.HEAVY,
            WeaponProperty.LOADING,
            WeaponProperty.TWO_HANDED,
        ]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.MARTIAL_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D10
        self.weight = 18
        self.value = 50


class Longbow(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Longbow"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.AMMUNITION, WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.MARTIAL_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 2
        self.value = 50


class Musket(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Musket"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.AMMUNITION, WeaponProperty.LOADING, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.MARTIAL_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D12
        self.weight = 10
        self.value = 500


class Pistol(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Pistol"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.AMMUNITION, WeaponProperty.LOADING]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_RANGED
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D10
        self.weight = 3
        self.value = 250


### HOMEBREW WEAPONS
