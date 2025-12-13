from enum import Enum
from typing import Optional
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Definitions import Ability
from Features.BaseFeatures import TextFeature
from Utils.CharacterSheetUtils import write_table
from dataclasses import dataclass, field
from abc import abstractmethod


class WeaponProperty(Enum):
    AMMUNITION = "Ammunition"
    FINESSE = "Finesse"
    HEAVY = "Heavy"
    LIGHT = "Light"
    LOADING = "Loading"
    RANGE = "Range"
    REACH = "Reach"
    THROWN = "Thrown"
    TWO_HANDED = "Two-handed"
    VERSATILE_8 = "Versatile (1d8)"
    VERSATILE_10 = "Versatile (1d10)"
    VERSATILE_12 = "Versatile (1d12)"

    @property
    def description(self):
        if self == WeaponProperty.AMMUNITION:
            return "Use only with matching ammo; each attack expends 1. Drawing ammo is part of attack (need free hand for 1-handed). After combat, recover half (round down)."
        if self == WeaponProperty.FINESSE:
            return "Use Str or Dex (your choice) for attack and damage rolls; same mod for both."
        if self == WeaponProperty.HEAVY:
            return "Disadvantage if Melee + Str < 13 or Ranged + Dex < 13."
        if self == WeaponProperty.LIGHT:
            return "When you Attack with a Light weapon, you can Bonus Action attack with another Light weapon; no ability mod to that damage unless negative."
        if self == WeaponProperty.LOADING:
            return "Can fire only 1 piece of ammo per Action/Bonus/Reaction, regardless of Extra Attack."
        if self == WeaponProperty.RANGE:
            return "Range (normal/long). Attacks beyond normal = Disadvantage; beyond long = impossible."
        if self == WeaponProperty.REACH:
            return "Adds +5 ft to reach for attacks and opportunity attacks."
        if self == WeaponProperty.THROWN:
            return "Can throw weapon for ranged attack; use same ability mod as melee version."
        if self == WeaponProperty.TWO_HANDED:
            return "Requires two hands to attack."
        if self in (
            WeaponProperty.VERSATILE_8,
            WeaponProperty.VERSATILE_10,
            WeaponProperty.VERSATILE_12,
        ):
            return "Can use one or two hands; if two-handed, use damage die shown in parentheses."

        raise ValueError(f"Weapon property '{self}' is not supported.")


class WeaponMastery(Enum):
    CLEAVE = "Cleave"
    GRAZE = "Graze"
    NICK = "Nick"
    PUSH = "Push"
    SAP = "Sap"
    SLOW = "Slow"
    TOPPLE = "Topple"
    VEX = "Vex"

    @property
    def description(self):
        if self == WeaponMastery.CLEAVE:
            return "When you hit a creature with a melee attack, you can make one extra melee attack with the same weapon against another creature within 5 ft of the first and in your reach. On a hit, deal weapon damage only (no mod unless negative). Once per turn."
        if self == WeaponMastery.GRAZE:
            return "If you miss with an attack, deal damage equal to the ability modifier used for the attack (same damage type)."
        if self == WeaponMastery.NICK:
            return "When using a Light weapon's extra attack, you can make it during the Attack action instead of as a Bonus Action. Once per turn."
        if self == WeaponMastery.PUSH:
            return "On a hit, you can push a Large or smaller target up to 10 ft away."
        if self == WeaponMastery.SAP:
            return "On a hit, the target has Disadvantage on its next attack before your next turn starts."
        if self == WeaponMastery.SLOW:
            return "On a hit that deals damage, reduce the target's Speed by 10 ft until your next turn. Multiple hits don't stack."
        if self == WeaponMastery.TOPPLE:
            return "On a hit, the target makes a Con save (DC = 8 + attack mod + prof). Fail = Prone."
        if self == WeaponMastery.VEX:
            return "On a hit that deals damage, you gain Advantage on your next attack against that creature before your next turn ends."

        raise ValueError(f"Weapon mastery '{self}' is not supported.")


class WeaponType(Enum):
    MARTIAL_MELEE = "Martial Melee"
    MARTIAL_RANGED = "Martial Ranged"
    SIMPLE_MELEE = "Simple Melee"
    SIMPLE_RANGED = "Simple Ranged"


class WeaponsDamageTypes(Enum):
    SLASHING = "Slashing"
    PIERCING = "Piercing"
    BLUDGEONING = "Bludgeoning"


class WeaponsDamageRolls(Enum):
    D1 = "1d1"
    D4 = "1d4"
    D6 = "1d6"
    D8 = "1d8"
    D10 = "1d10"
    D12 = "1d12"
    D20 = "1d20"
    D6x2 = "2d6"
    D8x2 = "2d8"
    D10x2 = "2d10"
    D12x2 = "2d12"


@dataclass
class WeaponsStats:
    name: str
    ability: Ability
    properties: list[WeaponProperty]
    mastery: WeaponMastery
    weapon_type: WeaponType
    damage_type: WeaponsDamageTypes
    damage_roll: WeaponsDamageRolls


@dataclass
class AbstractWeapon(TextFeature):
    """An abstract class for armor features."""

    player_is_proficient: bool = False
    player_has_mastery: bool = False
    bonus_attack_damages: list[str] = field(default_factory=list)

    @abstractmethod
    def stats(self) -> WeaponsStats:
        raise NotImplementedError("Subclasses must implement stats property.")

    def calculate_ability_modifier_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> str:
        if WeaponProperty.FINESSE in self.stats().properties:
            str_mod = character_stat_block.get_ability_modifier(Ability.STRENGTH)
            dex_mod = character_stat_block.get_ability_modifier(Ability.DEXTERITY)
            ability = (
                Ability.STRENGTH.value
                if str_mod >= dex_mod
                else Ability.DEXTERITY.value
            )
            ability_modifier = max(str_mod, dex_mod)
        else:
            ability_modifier = character_stat_block.get_ability_modifier(
                self.stats().ability
            )
            ability = self.stats().ability.value
        return f"{ability_modifier} (ability mod: {ability})"

    def calculate_proficiency_damage_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> str:
        if self.player_is_proficient:
            proficiency_bonus = character_stat_block.get_proficiency_bonus()
            return f"{proficiency_bonus} (Proficient)"
        return "0 (Not Proficient)"

    def calculate_total_attack_roll_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> str:
        attack_roll_bonus = (
            f"{self.calculate_ability_modifier_bonus(character_stat_block)}"
        )
        attack_roll_bonus += (
            f" + {self.calculate_proficiency_damage_bonus(character_stat_block)}"
        )
        for bonus in self.bonus_attack_damages:
            attack_roll_bonus += f" + {bonus}"
        return attack_roll_bonus

    def get_headers(self) -> list[str]:
        return ["Field", "Value"]

    def get_rows(self, character_stat_block: CharacterStatBlock) -> list[list[str]]:
        stats = self.stats()
        rows = []
        rows.append(["Name", stats.name])
        rows.append(["Type", stats.weapon_type.value])
        rows.append(["DamageType", stats.damage_type.value])

        for prop in stats.properties:
            rows.append([f"Property '{prop.value}'", prop.description])

        rows.append(["Proficient", "Yes" if self.player_is_proficient else "No"])

        attack_roll_bonus = self.calculate_total_attack_roll_bonus(character_stat_block)
        rows.append(["AttackRoll", f"1d20 + {attack_roll_bonus}"])

        ability_modifier_bonus = self.calculate_ability_modifier_bonus(
            character_stat_block
        )
        rows.append(
            ["DamageRoll", f"{stats.damage_roll.value} + {ability_modifier_bonus}"]
        )

        if self.player_has_mastery:
            rows.append([f"Mastery '{stats.mastery.value}'", stats.mastery.description])

        return rows

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        pass

    def write_to_file(self, character_stat_block: CharacterStatBlock, file):
        headers = self.get_headers()
        rows = self.get_rows(character_stat_block)
        write_table(headers, rows, file)


class Battleaxe(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Battleaxe",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Flail(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Flail",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Glaive(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Glaive",
            ability=Ability.STRENGTH,
            properties=[
                WeaponProperty.HEAVY,
                WeaponProperty.REACH,
                WeaponProperty.TWO_HANDED,
            ],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D10,
        )


class Greataxe(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Greataxe",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.CLEAVE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D12,
        )


class Greatsword(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Greatsword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D6x2,
        )


class Halberd(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Halberd",
            ability=Ability.STRENGTH,
            properties=[
                WeaponProperty.HEAVY,
                WeaponProperty.REACH,
                WeaponProperty.TWO_HANDED,
            ],
            mastery=WeaponMastery.CLEAVE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D10,
        )


class Lance(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Lance",
            ability=Ability.STRENGTH,
            properties=[
                WeaponProperty.HEAVY,
                WeaponProperty.REACH,
                WeaponProperty.TWO_HANDED,
            ],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D10,
        )


class Longsword(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Longsword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Maul(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Maul",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D6x2,
        )


class Morningstar(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Morningstar",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Pike(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Pike",
            ability=Ability.STRENGTH,
            properties=[
                WeaponProperty.HEAVY,
                WeaponProperty.REACH,
                WeaponProperty.TWO_HANDED,
            ],
            mastery=WeaponMastery.PUSH,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D10,
        )


class Rapier(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Rapier",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.FINESSE],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Scimitar(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Scimitar",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.FINESSE, WeaponProperty.LIGHT],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class Shortsword(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Shortsword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.FINESSE, WeaponProperty.LIGHT],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class Trident(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Trident",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.THROWN, WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Warhammer(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Warhammer",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.PUSH,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class WarPick(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="WarPick",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Whip(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Whip",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.FINESSE, WeaponProperty.REACH],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D4,
        )


class Club(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Club",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.LIGHT],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D4,
        )


class Dagger(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Dagger",
            ability=Ability.STRENGTH,
            properties=[
                WeaponProperty.FINESSE,
                WeaponProperty.LIGHT,
                WeaponProperty.THROWN,
            ],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D4,
        )


class Greatclub(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Greatclub",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.PUSH,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Handaxe(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Handaxe",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.LIGHT, WeaponProperty.THROWN],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class Javelin(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Javelin",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.THROWN],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class LightHammer(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Light Hammer",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.LIGHT, WeaponProperty.THROWN],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D4,
        )


class Mace(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Mace",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class Quarterstaff(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Quarterstaff",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_8],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class Sickle(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Sickle",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.LIGHT],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D4,
        )


class Spear(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Spear",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_8, WeaponProperty.THROWN],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class Dart(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Dart",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.FINESSE, WeaponProperty.THROWN],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.SIMPLE_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D4,
        )


class LightCrossbow(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Light Crossbow",
            ability=Ability.DEXTERITY,
            properties=[
                WeaponProperty.AMMUNITION,
                WeaponProperty.TWO_HANDED,
                WeaponProperty.LOADING,
            ],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.SIMPLE_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Shortbow(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Shortbow",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.AMMUNITION, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.SIMPLE_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class Sling(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Sling",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.AMMUNITION],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.SIMPLE_RANGED,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D4,
        )


class Blowgun(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Blowgun",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.AMMUNITION, WeaponProperty.LOADING],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D1,
        )


class HandCrossbow(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Hand Crossbow",
            ability=Ability.DEXTERITY,
            properties=[
                WeaponProperty.AMMUNITION,
                WeaponProperty.LIGHT,
                WeaponProperty.LOADING,
            ],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
        )


class HeavyCrossbow(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Heavy Crossbow",
            ability=Ability.DEXTERITY,
            properties=[
                WeaponProperty.AMMUNITION,
                WeaponProperty.HEAVY,
                WeaponProperty.LOADING,
                WeaponProperty.TWO_HANDED,
            ],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.MARTIAL_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D10,
        )


class Longbow(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Longbow",
            ability=Ability.DEXTERITY,
            properties=[
                WeaponProperty.AMMUNITION,
                WeaponProperty.HEAVY,
                WeaponProperty.TWO_HANDED,
            ],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.MARTIAL_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
        )


class Musket(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Musket",
            ability=Ability.DEXTERITY,
            properties=[
                WeaponProperty.AMMUNITION,
                WeaponProperty.LOADING,
                WeaponProperty.TWO_HANDED,
            ],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.MARTIAL_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D12,
        )


class Pistol(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Pistol",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.AMMUNITION, WeaponProperty.LOADING],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D10,
        )


def write_weapons_to_file(
    weapons: list[AbstractWeapon], character_stat_block: CharacterStatBlock, file
):
    if not weapons:
        return
    headers = weapons[0].get_headers()
    rows = []
    for i, weapon in enumerate(weapons):
        rows.extend(weapon.get_rows(character_stat_block))
        if i < len(weapons) - 1:
            rows.append([])  # Add a separator row between weapons
    write_table(headers, rows, file)
