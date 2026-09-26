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
    AxeMedium,
    DaggerLight,
    HammerLight,
    MaceLight,
    MaceMedium,
    SpearMedium,
)


class Club(MaceLight):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Club"
        self.mastery = WeaponMastery.SLOW
        self.value = 0.1
        self.is_homebrew = False


class Dagger(DaggerLight):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Dagger"
        self.properties = [
            WeaponProperty.FINESSE,
            WeaponProperty.LIGHT,
            WeaponProperty.THROWN,
        ]
        self.value = 2
        self.is_homebrew = False


class Greatclub(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Greatclub"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED]
        self.mastery = WeaponMastery.PUSH
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D8
        self.weight = 5
        self.value = 0.2


class Handaxe(AxeMedium):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Handaxe"
        self.properties = [WeaponProperty.LIGHT, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.VEX
        self.value = 5
        self.is_homebrew = False


class Javelin(SpearMedium):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Javelin"
        self.properties = [WeaponProperty.THROWN]
        self.mastery = WeaponMastery.SLOW
        self.weight = 2
        self.value = 0.5
        self.is_homebrew = False


class LightHammer(HammerLight):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Light Hammer"
        self.mastery = WeaponMastery.NICK
        self.is_homebrew = False


class Mace(MaceMedium):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Mace"
        self.is_homebrew = False


class Quarterstaff(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Quarterstaff"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_8]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = WeaponDamageRolls.D6
        self.weight = 4
        self.value = 0.2


class Sickle(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Sickle"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.LIGHT]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.SIMPLE_MELEE
        self.damage_type = WeaponDamageTypes.SLASHING
        self.damage_roll = WeaponDamageRolls.D4
        self.weight = 2
        self.value = 1


class Spear(SpearMedium):
    def base_stats(self) -> None:
        super().base_stats()
        self.name = "Spear"
        self.properties = [WeaponProperty.VERSATILE_8, WeaponProperty.THROWN]
        self.mastery = WeaponMastery.SAP
        self.is_homebrew = False
