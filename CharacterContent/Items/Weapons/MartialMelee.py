from Core.Definitions import Ability
from .Base import AbstractWeapon
from .Enums import (
    WeaponMastery,
    WeaponProperty,
    WeaponType,
    WeaponDamageRolls,
    WeaponDamageTypes,
)
from .WeaponFamilies import (
    AxeGreater,
    AxeHeavy,
    AxeMassive,
    DaggerHeavy,
    DaggerMedium,
    HammerColossal,
    HammerHeavy,
    MaceHeavy,
    SpearGreater,
    SpearHeavy,
    SwordColossal,
    SwordHeavy,
)


class Battleaxe(AxeHeavy):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Battleaxe"
        self.mastery = WeaponMastery.TOPPLE
        self.is_homebrew = False


class Flail(MaceHeavy):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Flail"
        self.weight = 2
        self.value = 10
        self.is_homebrew = False


class Glaive(AxeGreater):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Glaive"
        self.properties = [
            WeaponProperty.HEAVY,
            WeaponProperty.REACH,
            WeaponProperty.TWO_HANDED,
        ]
        self.mastery = WeaponMastery.GRAZE
        self.is_homebrew = False


class Greataxe(AxeMassive):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Greataxe"
        self.is_homebrew = False


class Greatsword(SwordColossal):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Greatsword"
        self.mastery = WeaponMastery.GRAZE
        self.weight = 6
        self.value = 50
        self.is_homebrew = False


class Halberd(AxeGreater):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Halberd"
        self.properties = [
            WeaponProperty.HEAVY,
            WeaponProperty.REACH,
            WeaponProperty.TWO_HANDED,
        ]
        self.is_homebrew = False


class Lance(SpearGreater):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Lance"
        self.properties = [
            WeaponProperty.HEAVY,
            WeaponProperty.REACH,
            WeaponProperty.TWO_HANDED,
        ]
        self.is_homebrew = False


class Longsword(SwordHeavy):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Longsword"
        self.mastery = WeaponMastery.SAP
        self.weight = 3
        self.value = 15
        self.is_homebrew = False


class Maul(HammerColossal):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Maul"
        self.mastery = WeaponMastery.TOPPLE
        self.value = 10
        self.is_homebrew = False


class Morningstar(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Morningstar"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 4
        self.value = 15


class Pike(SpearGreater):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Pike"
        self.properties = [
            WeaponProperty.HEAVY,
            WeaponProperty.REACH,
            WeaponProperty.TWO_HANDED,
        ]
        self.mastery = WeaponMastery.PUSH
        self.weight = 18
        self.value = 5
        self.is_homebrew = False


class Rapier(DaggerHeavy):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Rapier"
        self.value = 25
        self.is_homebrew = False


class Scimitar(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Scimitar"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 3
        self.value = 25


class Shortsword(DaggerMedium):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Shortsword"
        self.mastery = WeaponMastery.VEX
        self.value = 25
        self.is_homebrew = False


class Trident(SpearHeavy):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Trident"
        self.properties = [WeaponProperty.THROWN, WeaponProperty.VERSATILE_10]
        self.value = 5
        self.is_homebrew = False


class Warhammer(HammerHeavy):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Warhammer"
        self.weight = 2
        self.is_homebrew = False


class WarPick(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "WarPick"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.SAP
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.PIERCING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 2
        self.value = 5


class Whip(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Whip"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.FINESSE, WeaponProperty.REACH]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D4
        self.weight = 3
        self.value = 2
