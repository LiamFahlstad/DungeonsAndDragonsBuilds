from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TextIO

import DamageCalculator
from Definitions import Ability, Die
from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils.TableUtils import write_table


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

    @property
    def number_of_dice(self) -> int:
        return int(self.value.split("d")[0])

    @property
    def die_size(self) -> int:
        return int(self.value.split("d")[1])


@dataclass
class WeaponsStats:
    name: str
    ability: Ability
    properties: list[WeaponProperty]
    weapon_type: WeaponType
    damage_type: WeaponsDamageTypes
    damage_roll: WeaponsDamageRolls
    mastery: Optional[WeaponMastery] = None
    additional_description: Optional[str] = None


@dataclass
class AbstractWeapon(TextFeature):
    """An abstract class for armor features."""

    player_is_proficient: bool = False
    player_has_mastery: bool = False
    attack_roll_bonuses: list[tuple[int, str]] = field(default_factory=list)
    ability: Optional[Ability] = None

    @property
    def name(self):
        return self.stats().name

    @property
    def description(self):
        return self.stats().additional_description

    @abstractmethod
    def stats(self) -> WeaponsStats:
        raise NotImplementedError("Subclasses must implement stats property.")

    def _calculate_ability_modifier_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> tuple[int, str]:
        abilities_to_consider = set()
        abilities_to_consider.add(self.stats().ability)
        if self.ability:
            abilities_to_consider.add(self.ability)

        if WeaponProperty.FINESSE in self.stats().properties:
            abilities_to_consider.add(Ability.STRENGTH)
            abilities_to_consider.add(Ability.DEXTERITY)

        best_ability_modifier = -9999
        best_ability = None
        for ability in abilities_to_consider:
            ability_modifier = character_stat_block.get_ability_modifier(ability)
            if ability_modifier > best_ability_modifier:
                best_ability_modifier = ability_modifier
                best_ability = ability.value

        if best_ability is None:
            raise ValueError("No valid ability found for weapon damage calculation.")

        return best_ability_modifier, best_ability

    def calculate_ability_modifier_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> str:
        ability_modifier, ability = self._calculate_ability_modifier_bonus(
            character_stat_block
        )
        return f"{ability_modifier} (ability mod: {ability})"

    def _calculate_proficiency_damage_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> int:
        if self.player_is_proficient:
            proficiency_bonus = character_stat_block.get_proficiency_bonus()
            return proficiency_bonus
        return 0

    def calculate_proficiency_damage_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> str:
        proficiency_bonus = self._calculate_proficiency_damage_bonus(
            character_stat_block
        )
        if proficiency_bonus > 0:
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
        for _, bonus in self.attack_roll_bonuses:
            attack_roll_bonus += f" + {bonus}"
        return attack_roll_bonus

    def calculate_total_attack_roll_bonus_int(
        self, character_stat_block: CharacterStatBlock
    ) -> int:
        attack_roll_bonus, _ = self._calculate_ability_modifier_bonus(
            character_stat_block
        )
        attack_roll_bonus += self._calculate_proficiency_damage_bonus(
            character_stat_block
        )
        for bonus, _ in self.attack_roll_bonuses:
            attack_roll_bonus += bonus
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
            description = prop.description
            # description = StringUtils.wrap_text(
            #     prop.description, max_sentence_length=100
            # )
            rows.append([f"Property '{prop.value}'", description])

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
            mastery_description = stats.mastery.description
            # mastery_description = StringUtils.wrap_text(
            #     mastery_description, max_sentence_length=100
            # )
            rows.append([f"Mastery '{stats.mastery.value}'", mastery_description])

        if stats.additional_description:
            # additional_description = StringUtils.wrap_text(
            #     stats.additional_description, max_sentence_length=100
            # )
            rows.append(["Additional Description", stats.additional_description])

        attack_roll_die = DamageCalculator.Die.D20
        attack_roll_condition = DamageCalculator.DiceRollCondition.NEUTRAL
        attack_roll_bonus = self.calculate_total_attack_roll_bonus_int(
            character_stat_block
        )
        damage_die = Die.die_from_value(stats.damage_roll.die_size)
        number_of_damage_dice = stats.damage_roll.number_of_dice
        damage_condition = DamageCalculator.DiceRollCondition.NEUTRAL
        damage_bonus, _ = self._calculate_ability_modifier_bonus(character_stat_block)

        # for ac in range(10, 21):
        #     probability_of_hit = DamageCalculator.probability_of_success(
        #         difficulty_class=ac,
        #         die=attack_roll_die,
        #         condition=attack_roll_condition,
        #         bonus=attack_roll_bonus,
        #     )

        #     avg_damage = DamageCalculator.calculate_average_damage(
        #         armor_class=ac,
        #         attack_roll_die=attack_roll_die,
        #         attack_roll_condition=attack_roll_condition,
        #         attack_roll_bonus=attack_roll_bonus,
        #         damage_die=damage_die,
        #         number_of_damage_dice=number_of_damage_dice,
        #         damage_condition=damage_condition,
        #         damage_bonus=damage_bonus,
        #     )
        #     rows.append(
        #         [
        #             f"AC: {ac}",
        #             f"Prob of Hit: {probability_of_hit:.2f}, Avg Dmg: {avg_damage:.2f}",
        #         ]
        #     )

        return rows

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        pass

    def write_to_file(
        self, character_stat_block: CharacterStatBlock, file: TextIO, html: bool = False
    ):
        headers = self.get_headers()
        rows = self.get_rows(character_stat_block)
        write_table(headers, rows, file)
        self.write_damage_report(
            character_stat_block=character_stat_block,
            file=file,
        )

    def write_damage_report(
        self,
        character_stat_block: CharacterStatBlock,
        file,
    ) -> None:
        stats = self.stats()
        attack_roll_die = DamageCalculator.Die.D20
        attack_roll_condition = DamageCalculator.DiceRollCondition.NEUTRAL
        attack_roll_bonus = self.calculate_total_attack_roll_bonus_int(
            character_stat_block
        )
        damage_die = Die.die_from_value(stats.damage_roll.die_size)
        number_of_damage_dice = stats.damage_roll.number_of_dice
        damage_condition = DamageCalculator.DiceRollCondition.NEUTRAL
        damage_bonus = character_stat_block.get_ability_modifier(stats.ability)

        DamageCalculator.damage_report(
            file=file,
            attack_roll_die=attack_roll_die,
            attack_roll_condition=attack_roll_condition,
            attack_roll_bonus=attack_roll_bonus,
            damage_die=damage_die,
            number_of_damage_dice=number_of_damage_dice,
            damage_condition=damage_condition,
            damage_bonus=damage_bonus,
        )


@dataclass
class UnarmedStrike(AbstractWeapon):
    ability: Optional[Ability] = None
    damage_roll: Optional[WeaponsDamageRolls] = None

    def __post_init__(self):
        if self.ability is not None and self.ability not in (
            Ability.STRENGTH,
            Ability.DEXTERITY,
        ):
            raise ValueError("Unarmed Strike ability must be STR or DEX.")
        if self.player_has_mastery:
            raise ValueError("Unarmed Strike cannot have weapon mastery.")

    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Unarmed Strike",
            ability=self.ability or Ability.STRENGTH,
            properties=[],
            mastery=None,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=self.damage_roll or WeaponsDamageRolls.D1,
            additional_description=(
                "You can replace one attack with a grapple or shove. Grapple: target within reach and no more than one size larger, requires a free hand; make an Athletics check contested by Athletics or Acrobatics; on success, the target’s speed becomes 0, you can move it at half speed, and you can release it at any time; it can repeat the check to escape and automatically fails if incapacitated. "
                "Shove: same limits and check; on success, either knock the target prone or push it 5 ft. "
            ),
        )


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


### HOMEBREW WEAPONS


class Nullblade(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "Antimagic Edge. When you attack with this weapon:\n"
            "    * Ignore AC bonuses granted by spells or magical effects.\n"
            "    * Ignore magical effects that cause attacks to miss (illusions, duplicates, displacement).\n"
            "    * Ignore disadvantage imposed by magical effects.\n"
            "The Nullblade counts as nonmagical for interactions with magical effects."
        )
        return WeaponsStats(
            name="Nullblade",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            additional_description=description,
        )


class Bloodletter(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "Wounds from this blade refuse to close.\n"
            "On hit, the target must succeed on a CON save "
            "(DC = 8 + Proficiency Bonus + STR/DEX mod) or begin bleeding.\n"
            "A bleeding creature takes 1d4 damage at the start of each turn.\n"
            "It can repeat the save at the end of its turn, or the effect ends "
            "if it receives magical healing or an ally uses an action to staunch the wound."
        )
        return WeaponsStats(
            name="Bloodletter",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            additional_description=description,
        )


class HuntersHarpoon(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "On hit, you may tether the target (DEX save).\n"
            "While tethered, you may use a bonus action to pull the target 10 ft toward you."
        )
        return WeaponsStats(
            name="Hunter’s Harpoon",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.THROWN],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D10,
            additional_description=description,
        )


class RicochetBlade(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "On hit, you may bounce the attack to another creature within 5 ft.\n"
            "Make a new attack roll. The new target takes half damage (rounded down).\n"
            "The attack can bounce up to two times."
        )
        return WeaponsStats(
            name="Ricochet Blade",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.FINESSE],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D6,
            additional_description=description,
        )


class RampagingBlade(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "Momentum. Each time you hit without missing since your last turn, gain a stack.\n"
            "Each stack grants +1d4 damage (max 5 stacks).\n"
            "Stacks reset if you miss, go a full turn without hitting, or combat ends."
        )
        return WeaponsStats(
            name="Rampaging Blade",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.CLEAVE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            additional_description=description,
        )


class ElementalSword(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "As a bonus action, choose acid, cold, fire, lightning, or thunder.\n"
            "The weapon deals an extra 1d6 damage of the chosen type on hit."
        )
        return WeaponsStats(
            name="Elemental Sword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            additional_description=description,
        )


class BloodlustBlade(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "Predator’s Instinct. You have advantage on attack rolls against bloodied creatures.\n"
            "If a bloodied creature is visible and you attack another target, you have disadvantage.\n"
            "This never applies when targeting allies.\n"
            "A creature is bloodied when at half HP or lower."
        )
        return WeaponsStats(
            name="Bloodlust Blade",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            additional_description=description,
        )


class CoinflipCutBlade(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "After you hit, flip a coin:\n"
            "Heads — deal +2d6 force damage.\n"
            "Tails — you take 1d6 force damage."
        )
        return WeaponsStats(
            name="Coinflip Cut",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.FINESSE],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D6,
            additional_description=description,
        )


class Sundersteel(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "Damage ignores resistance.\n"
            "Creatures immune to this damage instead take damage as if resistant."
        )
        return WeaponsStats(
            name="Sundersteel",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY],
            mastery=WeaponMastery.CLEAVE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D12,
            additional_description=description,
        )


class VampiricEdge(AbstractWeapon):
    def stats(self) -> WeaponsStats:
        description = (
            "When you hit a creature, regain 1d4 hit points.\n"
            "You cannot regain more HP than the damage dealt."
        )
        return WeaponsStats(
            name="Vampiric Edge",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            additional_description=description,
        )


### Utility functions


def write_weapons_to_file(
    weapons: list[AbstractWeapon],
    character_stat_block: CharacterStatBlock,
    file: TextIO,
    html: bool = False,
):
    if not weapons:
        return
    headers: list[str] = weapons[0].get_headers()
    rows: list[list[str]] = []
    for i, weapon in enumerate(weapons):
        rows.extend(weapon.get_rows(character_stat_block))
        if i < len(weapons) - 1:
            rows.append([])  # Add a separator row between weapons
    if html:
        write_weapons_to_file_html(weapons, character_stat_block, file)
    else:
        write_table(headers, rows, file)


def write_weapons_to_file_html(
    weapons: list[AbstractWeapon],
    character_stat_block: CharacterStatBlock,
    file: TextIO,
):
    if not weapons:
        return

    headers: list[str] = weapons[0].get_headers()
    rows: list[list[str]] = []

    for i, weapon in enumerate(weapons):
        rows.extend(weapon.get_rows(character_stat_block))
        if i < len(weapons) - 1:
            rows.append([])  # separator row

    # --- Styling aligned with spells ---
    file.write(
        """
    <style>
    .weapons {
        max-width: 100%;
    }

    .weapon-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        margin: 0.25rem 0 0.75rem 0;
        table-layout: auto;
    }

    .weapon-table th,
    .weapon-table td {
        border: 1px solid #ddd;
        padding: 3px 5px;
        vertical-align: top;
    }

    .weapon-title {
        font-size: 1rem;
        text-align: left;
        background: #f5f5f5;
        font-weight: 600;
        padding: 4px 6px;
    }

    /* FIRST COLUMN = as tight as possible */
    .weapon-first-col {
        font-weight: 600;
        white-space: nowrap;
        background: #fafafa;
        width: 1%;
        padding: 2px 4px;
    }

    .weapon-cell {
        padding: 2px 5px;
    }

    .weapon-separator td {
        border: none;
        padding: 2px 0;
        height: 6px;
    }

    .weapon-separator hr {
        border: none;
        border-top: 1px solid #ddd;
        margin: 2px 0;
    }
    </style>
    """
    )

    file.write("<div class='weapons'>\n")
    file.write("<h2>Weapons</h2>\n")

    file.write("<table class='weapon-table'>\n")

    # Header row
    file.write("<tr>")
    for i, header in enumerate(headers):
        cls = "weapon-first-col" if i == 0 else "weapon-cell"
        file.write(f"<th class='{cls}'>{header}</th>")
    file.write("</tr>\n")

    # Data rows
    for row in rows:
        if not row:
            file.write(
                "<tr class='weapon-separator'><td colspan='999'><hr></td></tr>\n"
            )
            continue

        file.write("<tr>")
        for i, cell in enumerate(row):
            if i == 0:
                file.write(f"<td class='weapon-first-col'>{cell}</td>")
            else:
                file.write(f"<td class='weapon-cell'>{cell}</td>")
        file.write("</tr>\n")

    file.write("</table>\n")
    file.write("</div>\n")
