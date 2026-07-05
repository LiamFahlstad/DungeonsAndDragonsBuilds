from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TextIO

import DamageCalculator
from Definitions import Ability, Die
from Features.Items.Items import Item
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

_WEAPON_PROPERTY_DESCRIPTIONS: dict = {}  # populated after class definition


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
        return _WEAPON_PROPERTY_DESCRIPTIONS[self]


_WEAPON_PROPERTY_DESCRIPTIONS = {
    WeaponProperty.AMMUNITION: "Use only with matching ammo; each attack expends 1. Drawing ammo is part of attack (need free hand for 1-handed). After combat, recover half (round down).",
    WeaponProperty.FINESSE: "Use Str or Dex (your choice) for attack and damage rolls; same mod for both.",
    WeaponProperty.HEAVY: "Disadvantage if Melee + Str < 13 or Ranged + Dex < 13.",
    WeaponProperty.LIGHT: "When you Attack with a Light weapon, you can Bonus Action attack with another Light weapon; no ability mod to that damage unless negative.",
    WeaponProperty.LOADING: "Can fire only 1 piece of ammo per Action/Bonus/Reaction, regardless of Extra Attack.",
    WeaponProperty.RANGE: "Range (normal/long). Attacks beyond normal = Disadvantage; beyond long = impossible.",
    WeaponProperty.REACH: "Adds +5 ft to reach for attacks and opportunity attacks.",
    WeaponProperty.THROWN: "Can throw weapon for ranged attack; use same ability mod as melee version.",
    WeaponProperty.TWO_HANDED: "Requires two hands to attack.",
    WeaponProperty.VERSATILE_8: "Can use one or two hands; if two-handed, use damage die shown in parentheses.",
    WeaponProperty.VERSATILE_10: "Can use one or two hands; if two-handed, use damage die shown in parentheses.",
    WeaponProperty.VERSATILE_12: "Can use one or two hands; if two-handed, use damage die shown in parentheses.",
}


_WEAPON_MASTERY_DESCRIPTIONS: dict = {}  # populated after class definition


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
        return _WEAPON_MASTERY_DESCRIPTIONS[self]


_WEAPON_MASTERY_DESCRIPTIONS = {
    WeaponMastery.CLEAVE: "When you hit a creature with a melee attack, you can make one extra melee attack with the same weapon against another creature within 5 ft of the first and in your reach. On a hit, deal weapon damage only (no mod unless negative). Once per turn.",
    WeaponMastery.GRAZE: "If you miss with an attack, deal damage equal to the ability modifier used for the attack (same damage type).",
    WeaponMastery.NICK: "When using a Light weapon's extra attack, you can make it during the Attack action instead of as a Bonus Action. Once per turn.",
    WeaponMastery.PUSH: "On a hit, you can push a Large or smaller target up to 10 ft away.",
    WeaponMastery.SAP: "On a hit, the target has Disadvantage on its next attack before your next turn starts.",
    WeaponMastery.SLOW: "On a hit that deals damage, reduce the target's Speed by 10 ft until your next turn. Multiple hits don't stack.",
    WeaponMastery.TOPPLE: "On a hit, the target makes a Con save (DC = 8 + attack mod + prof). Fail = Prone.",
    WeaponMastery.VEX: "On a hit that deals damage, you gain Advantage on your next attack against that creature before your next turn ends.",
}


class WeaponType(Enum):
    MARTIAL_MELEE = "Martial Melee"
    MARTIAL_RANGED = "Martial Ranged"
    SIMPLE_MELEE = "Simple Melee"
    SIMPLE_RANGED = "Simple Ranged"


class WeaponsDamageTypes(Enum):
    SLASHING = "Slashing"
    PIERCING = "Piercing"
    BLUDGEONING = "Bludgeoning"
    ACID = "Acid"
    COLD = "Cold"
    FIRE = "Fire"
    LIGHTNING = "Lightning"
    THUNDER = "Thunder"
    NECROTIC = "Necrotic"
    RADIANT = "Radiant"
    POISON = "Poison"
    PSYCHIC = "Psychic"
    FORCE = "Force"


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
class ExtraDamage:
    """Represents bonus damage added to a weapon attack."""
    damage_roll: "WeaponsDamageRolls"
    damage_type: WeaponsDamageTypes
    note: Optional[str] = None  # e.g. "chosen type, activate as bonus action"

    def format_damage(self) -> str:
        """Format as '1d6 Fire' or similar."""
        return f"{self.damage_roll.value} {self.damage_type.value}"


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
    extra_damage: Optional[list[ExtraDamage]] = None


@dataclass
class AbstractWeapon(Item):
    """Abstract base class for weapons, inheriting from Item for shared inventory mechanics."""

    player_is_proficient: bool = False
    player_has_mastery: bool = False
    attack_roll_bonuses: list[tuple[int, str]] = field(default_factory=list)
    ability: Optional[Ability] = None

    def __post_init__(self):
        """Initialize Item base class fields when dataclass is instantiated."""
        # Dataclass fields set via __init__, but Item fields need explicit setting
        if not hasattr(self, 'rarity'):
            self.rarity = "common"
        if not hasattr(self, 'requires_attunement'):
            self.requires_attunement = False
        if not hasattr(self, 'category'):
            self.category = "weapon"
        if not hasattr(self, 'weight'):
            self.weight = None
        if not hasattr(self, 'slots'):
            self.slots = 1
        if not hasattr(self, 'description_text'):
            self.description_text = ""
        if not hasattr(self, 'subfeatures'):
            self.subfeatures = []
        # Set origin (for display) to weapon category
        self.origin = "weapon"

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
        attack_roll_bonus = self.calculate_ability_modifier_bonus(character_stat_block)
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

    def get_description(
        self, character_stat_block: CharacterStatBlock
    ) -> Optional[str]:
        return None

    def calculate_hit_probabilities(
        self,
        character_stat_block: CharacterStatBlock,
        condition: DamageCalculator.DiceRollCondition = DamageCalculator.DiceRollCondition.NEUTRAL,
    ) -> list[tuple[int, float]]:
        """Return hit probability for each AC from 10 to 25 (inclusive)."""
        attack_roll_bonus = self.calculate_total_attack_roll_bonus_int(
            character_stat_block
        )
        results = []
        for ac in range(10, 26):
            prob = DamageCalculator.probability_of_success(
                difficulty_class=ac,
                die=DamageCalculator.Die.D20,
                condition=condition,
                bonus=attack_roll_bonus,
            )
            results.append((ac, prob))
        return results

    def apply(self, character_stat_block: CharacterStatBlock):
        """Apply weapon's Item subfeatures (inherited from Item)."""
        super().apply(character_stat_block)

    def write_to_file(self, character_stat_block: CharacterStatBlock, file: TextIO):
        pass  # HTML rendering is handled by write_weapons_to_file

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
        super().__post_init__()  # Initialize Item fields
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
        return WeaponsStats(
            name="Elemental Sword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            additional_description=(
                "As a bonus action, choose acid, cold, fire, lightning, or thunder. "
                "The weapon deals an extra 1d6 damage of the chosen type on hit."
            ),
            extra_damage=[
                ExtraDamage(
                    damage_roll=WeaponsDamageRolls.D6,
                    damage_type=WeaponsDamageTypes.FIRE,
                    note="chosen type, activate as bonus action"
                )
            ],
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


# ──────────────────────────────────────────────────────────────────────────────
# Magical Weapons
# ──────────────────────────────────────────────────────────────────────────────


class FlameTongueSword(AbstractWeapon):
    """A magical sword wreathed in flames, dealing extra fire damage on hit."""

    def __post_init__(self):
        super().__post_init__()
        self.rarity = "rare"
        self.requires_attunement = True
        # Add +1 to ability scores (from SubFeature)
        from Features.Core.SubFeatures import AbilityScoreBonus

        self.subfeatures = [
            AbilityScoreBonus([(Ability.STRENGTH, 1)], total=1, error_prefix="Flame Tongue Sword bonus")
        ]

    def stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Flame Tongue Sword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            additional_description=(
                "This sword is wreathed in magical flames. "
                "It deals an extra 2d6 fire damage on a hit. "
                "Requires attunement (rare)."
            ),
            extra_damage=[
                ExtraDamage(
                    damage_roll=WeaponsDamageRolls.D6x2,
                    damage_type=WeaponsDamageTypes.FIRE,
                    note="magical flames"
                )
            ],
        )


### Utility functions


def _write_single_weapon(
    weapon: AbstractWeapon,
    character_stat_block: CharacterStatBlock,
    file: TextIO,
):
    stats = weapon.stats()

    attack_bonus_int = weapon.calculate_total_attack_roll_bonus_int(
        character_stat_block
    )
    attack_bonus_str = f"{attack_bonus_int:+}"

    ability_mod, ability_name = weapon._calculate_ability_modifier_bonus(
        character_stat_block
    )
    damage_roll_str = f"{stats.damage_roll.value} {ability_mod:+} ({ability_name})"

    # Add extra damage if present
    if stats.extra_damage:
        extra_damages = " + ".join(ed.format_damage() for ed in stats.extra_damage)
        damage_roll_str += f" + {extra_damages}"

    proficient_label = "Proficient" if weapon.player_is_proficient else "Not proficient"

    prop_names = (
        ", ".join(p.value for p in stats.properties) if stats.properties else "—"
    )

    mastery_label = ""
    if stats.mastery:
        mastery_label = stats.mastery.value
        if weapon.player_has_mastery:
            mastery_label += " ✓"

    file.write("<table class='weapon-card'>\n")

    # ── Weapon name header ──────────────────────────────────────────────────
    file.write(f"<tr><th class='weapon-name' colspan='2'>{stats.name}</th></tr>\n")

    # ── Quick-stats row ─────────────────────────────────────────────────────
    # Two cells: left = type/category info, right = roll info
    type_cell = (
        f"{stats.weapon_type.value}"
        f"<span class='wsep'>·</span>"
        f"{stats.damage_type.value}"
        f"<span class='wsep'>·</span>"
        f"{proficient_label}"
    )
    roll_cell = (
        f"<span class='wlabel'>Attack</span> 1d20 {attack_bonus_str}"
        f"<span class='wsep'>·</span>"
        f"<span class='wlabel'>Damage</span> {damage_roll_str}"
    )
    file.write(
        f"<tr class='weapon-quickstats'>"
        f"<td class='wqs-left'>{type_cell}</td>"
        f"<td class='wqs-right'>{roll_cell}</td>"
        f"</tr>\n"
    )

    # ── Hit probability row ─────────────────────────────────────────────────
    conditions = [
        ("Normal", DamageCalculator.DiceRollCondition.NEUTRAL),
        ("Adv.", DamageCalculator.DiceRollCondition.ADVANTAGE),
        ("Disadv.", DamageCalculator.DiceRollCondition.DISADVANTAGE),
    ]
    hit_probs_normal = weapon.calculate_hit_probabilities(character_stat_block)
    inner_header = "".join(
        f"<th class='whit-ac'>{ac}</th>" for ac, _ in hit_probs_normal
    )
    inner_rows = ""
    for label, cond in conditions:
        hit_probs = weapon.calculate_hit_probabilities(character_stat_block, condition=cond)
        cells = "".join(
            f"<td class='whit-pct' data-pct='{round(round(prob * 100) / 5) * 5}'>{prob * 100:.0f}%</td>"
            for _, prob in hit_probs
        )
        inner_rows += f"<tr><td class='whit-cond-label'>{label}</td>{cells}</tr>"
    inner_table = (
        f"<table class='whit-inner'>"
        f"<tr><th class='whit-cond-label'></th>{inner_header}</tr>"
        f"{inner_rows}"
        f"</table>"
    )
    file.write(
        f"<tr class='weapon-hit-row'>"
        f"<td class='wlabel-col'>Hit % by AC</td>"
        f"<td class='whit-cell'>{inner_table}</td>"
        f"</tr>\n"
    )

    # ── Properties row ──────────────────────────────────────────────────────
    if stats.properties or mastery_label:
        tags_html = ""
        for prop in stats.properties:
            tags_html += f"<span class='wtag'>{prop.value}</span> "
        if mastery_label:
            mastery_cls = (
                "wtag wtag-mastery"
                if weapon.player_has_mastery
                else "wtag wtag-mastery-inactive"
            )
            tags_html += f"<span class='{mastery_cls}'>Mastery: {mastery_label}</span>"
        file.write(
            f"<tr class='weapon-tags-row'>"
            f"<td class='wlabel-col'>Properties</td>"
            f"<td class='wtags-cell'>{tags_html.strip()}</td>"
            f"</tr>\n"
        )

    # ── Per-property descriptions ────────────────────────────────────────────
    for prop in stats.properties:
        prop_desc_processed = StringUtils.boxes_to_html(prop.description)
        prop_desc_html = prop_desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-prop-row'>"
            f"<td class='wprop-label'>{prop.value}</td>"
            f"<td class='wprop-desc'>{prop_desc_html}</td>"
            f"</tr>\n"
        )

    # ── Mastery description (only if the player has mastery) ────────────────
    if stats.mastery and weapon.player_has_mastery:
        mastery_desc_processed = StringUtils.boxes_to_html(stats.mastery.description)
        mastery_desc_html = mastery_desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-mastery-row'>"
            f"<td class='wmastery-label'>Mastery — {stats.mastery.value}</td>"
            f"<td class='wmastery-desc'>{mastery_desc_html}</td>"
            f"</tr>\n"
        )

    # ── Additional description ───────────────────────────────────────────────
    if stats.additional_description:
        # Replace newlines with <br> for HTML display
        desc_processed = StringUtils.boxes_to_html(stats.additional_description)
        desc_html = desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-addl-row'>"
            f"<td class='wlabel-col'>Notes</td>"
            f"<td class='waddl-desc'>{desc_html}</td>"
            f"</tr>\n"
        )

    file.write("</table>\n")


def write_weapons_to_file(
    weapons: list[AbstractWeapon],
    character_stat_block: CharacterStatBlock,
    file: TextIO,
):
    if not weapons:
        return

    file.write("<div class='weapons'>\n")
    file.write("<h2>Weapons</h2>\n")

    for i, weapon in enumerate(weapons):
        if i > 0:
            file.write("<div class='weapon-gap'></div>\n")
        _write_single_weapon(weapon, character_stat_block, file)

    file.write("</div>\n")
