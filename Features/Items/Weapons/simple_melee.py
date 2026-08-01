from Core.Definitions import Ability
from .base import AbstractWeapon
from .enums import WeaponMastery, WeaponProperty, WeaponType, WeaponsDamageRolls, WeaponsDamageTypes


class Club(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Club"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D4
        self.weight = 2
        self.value = 0.1


class Dagger(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Dagger"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D4
        self.weight = 1
        self.value = 2


class Greatclub(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Greatclub"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 5
        self.value = 0.2


class Handaxe(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Handaxe"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.LIGHT, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 2
        self.value = 5


class Javelin(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Javelin"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.THROWN]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 2
        self.value = 0.5


class LightHammer(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Light Hammer"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.LIGHT, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D4
        self.weight = 2
        self.value = 2


class Mace(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Mace"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 4
        self.value = 5


class Quarterstaff(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Quarterstaff"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_8]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 4
        self.value = 0.2


class Sickle(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sickle"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D4
        self.weight = 2
        self.value = 1


class Spear(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Spear"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_8, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 3
        self.value = 1
