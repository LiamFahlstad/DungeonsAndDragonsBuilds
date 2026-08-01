from Core.Definitions import Ability
from .Base import AbstractWeapon
from .Enums import WeaponMastery, WeaponProperty, WeaponType, WeaponsDamageRolls, WeaponsDamageTypes


class Battleaxe(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Battleaxe"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 4
        self.value = 10


class Flail(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Flail"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 2
        self.value = 10


class Glaive(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Glaive"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.REACH, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D10
        self.weight = 6
        self.value = 20


class Greataxe(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Greataxe"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D12
        self.weight = 7
        self.value = 30


class Greatsword(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Greatsword"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D6x2
        self.weight = 6
        self.value = 50


class Halberd(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Halberd"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.REACH, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D10
        self.weight = 6
        self.value = 20


class Lance(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Lance"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.REACH, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D10
        self.weight = 6
        self.value = 10


class Longsword(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Longsword"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 3
        self.value = 15


class Maul(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Maul"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D6x2
        self.weight = 10
        self.value = 10


class Morningstar(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Morningstar"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 4
        self.value = 15


class Pike(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Pike"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.REACH, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D10
        self.weight = 18
        self.value = 5


class Rapier(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Rapier"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 2
        self.value = 25


class Scimitar(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Scimitar"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 3
        self.value = 25


class Shortsword(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Shortsword"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.VEX
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D6
        self.weight = 2
        self.value = 25


class Trident(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Trident"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.THROWN, WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 4
        self.value = 5


class Warhammer(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Warhammer"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 2
        self.value = 15


class WarPick(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "WarPick"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D8
        self.weight = 2
        self.value = 5


class Whip(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Whip"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.REACH]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D4
        self.weight = 3
        self.value = 2
