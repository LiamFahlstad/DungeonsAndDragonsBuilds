from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, TextIO

from Utils import DamageCalculator
from Core.Definitions import Ability, DiceRollCondition, Die, Skill
from Features.Core.SubFeatures import (
    AbilityScoreBonus,
    AddItemDescription,
    InitiativeRollCondition,
    ItemImprovement,
    Reskin,
    SetItemHomebrew,
    SetItemName,
    SetItemValue,
    SkillBonus,
    SubFeature,
)
from Features.Items.Items import Item, ItemCategory, ItemRarity
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


class WeaponProficiency(Enum):
    """A class's weapon proficiency grant, per its Weapon Proficiencies entry
    in SourceTexts/ClassTexts/<class>.txt. Most classes grant a broad
    category (simple and/or martial); Monk and Rogue additionally grant a
    property-restricted slice of martial weapons."""

    SIMPLE = "Simple weapons"
    MARTIAL = "Martial weapons"
    MARTIAL_LIGHT = "Martial weapons with the Light property"
    MARTIAL_FINESSE_OR_LIGHT = "Martial weapons with the Finesse or Light property"


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


# ──────────────────────────────────────────────────────────────────────────────
# WeaponSubFeature: composable modifiers applied to a weapon at construction
# time (e.g. a magic weapon variant, or a homebrew reskin). Mirrors
# Features.Core.SubFeatures.SubFeature, but its apply() mutates the weapon
# instance instead of the character stat block, since these improvements
# (attack/damage bonuses, damage die/type, properties, flavor text) are
# properties of the weapon itself, not of the wielder.
# ──────────────────────────────────────────────────────────────────────────────


class WeaponSubFeature(ItemImprovement):
    """Base class for weapon improvements. Override apply() to modify the weapon."""

    @abstractmethod
    def apply(self, weapon: "AbstractWeapon") -> None:
        pass


class SetAttackRollBonus(WeaponSubFeature):
    """Overrides the weapon's total attack roll bonus with a fixed value,
    ignoring ability modifier, proficiency, and any additive bonuses."""

    def __init__(self, value: int):
        self.value = value

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._attack_roll_override = self.value


class AddAttackRollBonus(WeaponSubFeature):
    """Adds a flat bonus to the weapon's attack roll."""

    def __init__(self, value: int, reason: str = "Bonus"):
        self.value = value
        self.reason = reason

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.attack_roll_bonuses.append((self.value, f"{self.value} ({self.reason})"))


class SetDamageRollBonus(WeaponSubFeature):
    """Overrides the weapon's damage bonus (the flat number added to the
    damage die), ignoring the ability modifier and any additive bonuses."""

    def __init__(self, value: int):
        self.value = value

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._damage_bonus_override = self.value


class AddDamageRollBonus(WeaponSubFeature):
    """Adds a flat bonus to the weapon's damage roll."""

    def __init__(self, value: int, reason: str = "Bonus"):
        self.value = value
        self.reason = reason

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.damage_roll_bonuses.append((self.value, f"{self.value} ({self.reason})"))


class SetDamageDie(WeaponSubFeature):
    """Overrides the weapon's damage die (e.g. upgrading a Longsword to 2d6)."""

    def __init__(self, damage_roll: WeaponsDamageRolls):
        self.damage_roll = damage_roll

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.damage_roll = self.damage_roll


class SetDamageType(WeaponSubFeature):
    """Overrides the weapon's damage type (e.g. a frost blade dealing Cold instead of Slashing)."""

    def __init__(self, damage_type: WeaponsDamageTypes):
        self.damage_type = damage_type

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.damage_type = self.damage_type


class AddWeaponProperty(WeaponSubFeature):
    """Adds a weapon property (e.g. Finesse, Reach) not already on the weapon."""

    def __init__(self, property: WeaponProperty):
        self.property = property

    def apply(self, weapon: "AbstractWeapon") -> None:
        if self.property not in weapon.properties:
            weapon.properties.append(self.property)


class AddExtraDamage(WeaponSubFeature):
    """Adds extra damage dice to the weapon's attack (e.g. a flaming blade's extra 1d6 Fire)."""

    def __init__(
        self,
        damage_roll: WeaponsDamageRolls,
        damage_type: WeaponsDamageTypes,
        note: Optional[str] = None,
    ):
        self.extra_damage = ExtraDamage(damage_roll=damage_roll, damage_type=damage_type, note=note)

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon.extra_damage.append(self.extra_damage)


class SetWeaponAbility(WeaponSubFeature):
    """Overrides which ability score is used for the weapon's attack and damage
    rolls (e.g. a Bladesinger using Intelligence instead of Strength/Dexterity),
    replacing the weapon's own ability - and any Finesse Str/Dex comparison -
    outright rather than only being considered as an alternative."""

    def __init__(self, ability: Ability):
        self.ability = ability

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._ability_override = self.ability


class AbstractWeapon(Item, ABC):
    """Abstract base class for weapons. Weapons are wearable items: their
    subfeatures only apply while worn/wielded (is_wearing).

    Two independent ways to attach behavior to a weapon:
    - `subfeatures=[...]` (list[SubFeature], defined in Features.Core.SubFeatures):
      character-affecting effects, applied to the wielder's stat block while
      worn - e.g. FlameTongueSword granting +1 Strength, the same mechanism
      RingOfIntelligence uses in Features.Items.Items.
    - `weapon_subfeatures=[...]` (list[WeaponSubFeature], defined below):
      weapon-only effects that modify the weapon itself (damage die/type,
      properties, attack/damage bonuses, ...) - not applicable to any other
      item type. See the WeaponSubFeature showcase further down."""

    # Required fields every base_stats() must set; declared here (with no
    # class-level value) purely so static type checkers know they exist.
    name: str
    ability: Ability
    properties: list[WeaponProperty]
    weapon_type: WeaponType
    damage_type: WeaponsDamageTypes
    damage_roll: WeaponsDamageRolls

    def __init__(
        self,
        player_is_proficient: bool = False,
        player_has_mastery: bool = False,
        attack_roll_bonuses: Optional[list[tuple[int, str]]] = None,
        ability: Optional[Ability] = None,
        is_wearing: bool = True,
        category: ItemCategory = ItemCategory.WEAPON,
        slots: int = 1,
        subfeatures: Optional[list[SubFeature]] = None,
        weapon_subfeatures: Optional[list[WeaponSubFeature]] = None,
    ):
        self.player_is_proficient = player_is_proficient
        self.player_has_mastery = player_has_mastery
        self.attack_roll_bonuses = attack_roll_bonuses if attack_roll_bonuses is not None else []
        self.damage_roll_bonuses: list[tuple[int, str]] = []

        # Ability/attack-roll/damage-bonus overrides live outside base_stats()
        # entirely: they're read directly by the bonus-calculation methods
        # below rather than composed into a weapon field.
        self._ability_override: Optional[Ability] = ability
        self._attack_roll_override: Optional[int] = None
        self._damage_bonus_override: Optional[int] = None

        # Defaults for the fields a concrete weapon's base_stats() may leave
        # unset; required fields (name, ability, properties, weapon_type,
        # damage_type, damage_roll) have no default and must always be set.
        self.mastery: Optional[WeaponMastery] = None
        self.description_text: str = ""
        self.extra_damage: list[ExtraDamage] = []
        self.weight: Optional[float] = None
        self.value: Optional[float] = None
        self.is_homebrew: bool = False
        self.rarity: ItemRarity = ItemRarity.COMMON
        self.requires_attunement: bool = False
        # Character-affecting SubFeatures innate to this weapon (e.g. the +1
        # to Strength granted just by owning a Flame Tongue Sword). Distinct
        # from WeaponSubFeature, which modifies the weapon itself, not the
        # wielder.
        self._innate_subfeatures: list[SubFeature] = []

        self.base_stats()

        for weapon_subfeature in weapon_subfeatures or []:
            self.add_weapon_improvement(weapon_subfeature)
        self.setup_improvements()

        super().__init__(
            name=self.name,
            rarity=self.rarity,
            requires_attunement=self.requires_attunement,
            category=category,
            weight=self.weight,
            slots=slots,
            description_text=self.description_text,
            subfeatures=self._innate_subfeatures + list(subfeatures or []),
            is_wearing=is_wearing,
            is_homebrew=self.is_homebrew,
            value=self.value,
        )

    @abstractmethod
    def base_stats(self) -> None:
        """Set this weapon's base (pre-improvement) attributes directly
        (self.name, self.ability, self.properties, ...). Called once during
        __init__, before any improvement is applied."""
        raise NotImplementedError("Subclasses must implement base_stats().")

    def add_weapon_improvement(self, weapon_subfeature: "WeaponSubFeature") -> None:
        """Attach a WeaponSubFeature - a weapon-only improvement (damage
        die/type, properties, attack/damage bonuses, ...) - to this weapon.
        Named for clarity alongside add_character_improvement(), which
        attaches an effect on the wielder instead."""
        self.add_improvement(weapon_subfeature)

    def _calculate_ability_modifier_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> tuple[int, str]:
        if self._ability_override is not None:
            ability = self._ability_override
            return character_stat_block.get_ability_modifier(ability), ability.value

        abilities_to_consider = set()
        abilities_to_consider.add(self.ability)

        if WeaponProperty.FINESSE in self.properties:
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
        if self._attack_roll_override is not None:
            return f"{self._attack_roll_override:+} (fixed)"
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
        if self._attack_roll_override is not None:
            return self._attack_roll_override
        attack_roll_bonus, _ = self._calculate_ability_modifier_bonus(
            character_stat_block
        )
        attack_roll_bonus += self._calculate_proficiency_damage_bonus(
            character_stat_block
        )
        for bonus, _ in self.attack_roll_bonuses:
            attack_roll_bonus += bonus
        return attack_roll_bonus

    def calculate_damage_bonus_int(
        self, character_stat_block: CharacterStatBlock
    ) -> int:
        """Flat bonus added to the damage die (ability modifier by default,
        or a fixed override), plus any additive damage-roll bonuses."""
        if self._damage_bonus_override is not None:
            return self._damage_bonus_override
        damage_bonus, _ = self._calculate_ability_modifier_bonus(character_stat_block)
        for bonus, _ in self.damage_roll_bonuses:
            damage_bonus += bonus
        return damage_bonus

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

    def write_to_file(self, character_stat_block: CharacterStatBlock, file: TextIO):
        pass  # HTML rendering is handled by write_weapons_to_file

    def write_damage_report(
        self,
        character_stat_block: CharacterStatBlock,
        file,
    ) -> None:
        attack_roll_die = DamageCalculator.Die.D20
        attack_roll_condition = DamageCalculator.DiceRollCondition.NEUTRAL
        attack_roll_bonus = self.calculate_total_attack_roll_bonus_int(
            character_stat_block
        )
        damage_die = Die.die_from_value(self.damage_roll.die_size)
        number_of_damage_dice = self.damage_roll.number_of_dice
        damage_condition = DamageCalculator.DiceRollCondition.NEUTRAL
        damage_bonus = self.calculate_damage_bonus_int(character_stat_block)

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


def weapon_matches_proficiency(
    weapon: AbstractWeapon, proficiency: WeaponProficiency
) -> bool:
    is_simple = weapon.weapon_type in (WeaponType.SIMPLE_MELEE, WeaponType.SIMPLE_RANGED)
    is_martial = weapon.weapon_type in (WeaponType.MARTIAL_MELEE, WeaponType.MARTIAL_RANGED)
    if proficiency == WeaponProficiency.SIMPLE:
        return is_simple
    if proficiency == WeaponProficiency.MARTIAL:
        return is_martial
    if proficiency == WeaponProficiency.MARTIAL_LIGHT:
        return is_martial and WeaponProperty.LIGHT in weapon.properties
    if proficiency == WeaponProficiency.MARTIAL_FINESSE_OR_LIGHT:
        return is_martial and (
            WeaponProperty.FINESSE in weapon.properties
            or WeaponProperty.LIGHT in weapon.properties
        )
    raise ValueError(f"Unhandled weapon proficiency: {proficiency}")


def is_proficient_with(
    weapon: AbstractWeapon, proficiencies: "set[WeaponProficiency] | list[WeaponProficiency]"
) -> bool:
    return any(weapon_matches_proficiency(weapon, p) for p in proficiencies)


class UnarmedStrike(AbstractWeapon):
    def __init__(
        self,
        ability: Optional[Ability] = None,
        damage_roll: Optional[WeaponsDamageRolls] = None,
        **kwargs,
    ):
        if ability is not None and ability not in (
            Ability.STRENGTH,
            Ability.DEXTERITY,
        ):
            raise ValueError("Unarmed Strike ability must be STR or DEX.")
        if kwargs.get("player_has_mastery"):
            raise ValueError("Unarmed Strike cannot have weapon mastery.")
        self.damage_roll = damage_roll
        super().__init__(ability=ability, **kwargs)

    def base_stats(self) -> None:
        self.name = "Unarmed Strike"
        self.ability = self._ability_override or Ability.STRENGTH
        self.properties = []
        self.mastery = None
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = self.damage_roll or WeaponsDamageRolls.D1
        self.description_text = (
            "You can replace one attack with a grapple or shove. Grapple: target within reach and no more than one size larger, requires a free hand; make an Athletics check contested by Athletics or Acrobatics; on success, the target’s speed becomes 0, you can move it at half speed, and you can release it at any time; it can repeat the check to escape and automatically fails if incapacitated. "
            "Shove: same limits and check; on success, either knock the target prone or push it 5 ft. "
        )


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


class Nullblade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Antimagic Edge. When you attack with this weapon:\n"
            "    * Ignore AC bonuses granted by spells or magical effects.\n"
            "    * Ignore magical effects that cause attacks to miss (illusions, duplicates, displacement).\n"
            "    * Ignore disadvantage imposed by magical effects.\n"
            "The Nullblade counts as nonmagical for interactions with magical effects."
        )
        self.name = "Nullblade"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class Bloodletter(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Wounds from this blade refuse to close.\n"
            "On hit, the target must succeed on a CON save "
            "(DC = 8 + Proficiency Bonus + STR/DEX mod) or begin bleeding.\n"
            "A bleeding creature takes 1d4 damage at the start of each turn.\n"
            "It can repeat the save at the end of its turn, or the effect ends "
            "if it receives magical healing or an ally uses an action to staunch the wound."
        )
        self.name = "Bloodletter"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class HuntersHarpoon(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "On hit, you may tether the target (DEX save).\n"
            "While tethered, you may use a bonus action to pull the target 10 ft toward you."
        )
        self.name = "Hunter’s Harpoon"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.THROWN]
        self.mastery = WeaponMastery.SLOW
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.PIERCING
        self.damage_roll = WeaponsDamageRolls.D10
        self.description_text = description
        self.is_homebrew = True


class RicochetBlade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "On hit, you may bounce the attack to another creature within 5 ft.\n"
            "Make a new attack roll. The new target takes half damage (rounded down).\n"
            "The attack can bounce up to two times."
        )
        self.name = "Ricochet Blade"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.FINESSE]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D6
        self.description_text = description
        self.is_homebrew = True


class RampagingBlade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Momentum. Each time you hit without missing since your last turn, gain a stack.\n"
            "Each stack grants +1d4 damage (max 5 stacks).\n"
            "Stacks reset if you miss, go a full turn without hitting, or combat ends."
        )
        self.name = "Rampaging Blade"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class ElementalSword(AbstractWeapon):
    def base_stats(self) -> None:
        self.name = "Elemental Sword"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = (
            "As a bonus action, choose acid, cold, fire, lightning, or thunder. "
            "The weapon deals an extra 1d6 damage of the chosen type on hit."
        )
        self.extra_damage = [
            ExtraDamage(
                damage_roll=WeaponsDamageRolls.D6,
                damage_type=WeaponsDamageTypes.FIRE,
                note="chosen type, activate as bonus action",
            )
        ]
        self.is_homebrew = True


class BloodlustBlade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Predator’s Instinct. You have advantage on attack rolls against bloodied creatures.\n"
            "If a bloodied creature is visible and you attack another target, you have disadvantage.\n"
            "This never applies when targeting allies.\n"
            "A creature is bloodied when at half HP or lower."
        )
        self.name = "Bloodlust Blade"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


class CoinflipCutBlade(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "After you hit, flip a coin:\n"
            "Heads — deal +2d6 force damage.\n"
            "Tails — you take 1d6 force damage."
        )
        self.name = "Coinflip Cut"
        self.ability = Ability.DEXTERITY
        self.properties = [WeaponProperty.FINESSE]
        self.mastery = WeaponMastery.NICK
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D6
        self.description_text = description
        self.is_homebrew = True


class Sundersteel(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "Damage ignores resistance.\n"
            "Creatures immune to this damage instead take damage as if resistant."
        )
        self.name = "Sundersteel"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.HEAVY]
        self.mastery = WeaponMastery.CLEAVE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D12
        self.description_text = description
        self.is_homebrew = True


class VampiricEdge(AbstractWeapon):
    def base_stats(self) -> None:
        description = (
            "When you hit a creature, regain 1d4 hit points.\n"
            "You cannot regain more HP than the damage dealt."
        )
        self.name = "Vampiric Edge"
        self.ability = Ability.STRENGTH
        self.properties = []
        self.mastery = WeaponMastery.GRAZE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = description
        self.is_homebrew = True


# ──────────────────────────────────────────────────────────────────────────────
# WeaponSubFeature showcase: one weapon per improvement, demonstrating how
# `weapon_subfeatures=[...]` composes on top of a weapon's base_stats().
# ──────────────────────────────────────────────────────────────────────────────


class UnerringBlade(Longsword):
    """A Longsword variant demonstrating SetAttackRollBonus: attack rolls
    always use a fixed bonus, ignoring ability modifier, proficiency, and any
    additive bonuses."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(SetAttackRollBonus(7))
        self.add_weapon_improvement(
            Reskin(
                "Unerring Blade",
                "This blade's strikes are guided by fate: it always hits with a "
                "+7 bonus to attack rolls, ignoring your ability scores and proficiency.",
            )
        )


class MarksmansLongbow(Longbow):
    """A Longbow variant demonstrating AddAttackRollBonus: a flat bonus stacks
    on top of the normal attack roll."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddAttackRollBonus(2, "Marksman's Scope"))
        self.add_weapon_improvement(
            Reskin(
                "Marksman's Longbow",
                "A precision-crafted scope grants a +2 bonus to attack rolls with "
                "this bow, on top of the normal ability and proficiency bonuses.",
            )
        )


class Skullcrusher(Maul):
    """A Maul variant demonstrating SetDamageRollBonus: the damage bonus is
    fixed, ignoring ability modifier."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(SetDamageRollBonus(10))
        self.add_weapon_improvement(
            Reskin(
                "Skullcrusher",
                "Enchanted to strike with unwavering force, this maul always deals "
                "a +10 damage bonus, regardless of your Strength.",
            )
        )


class VenomfangDagger(Dagger):
    """A Dagger variant demonstrating AddDamageRollBonus: a flat bonus stacks
    on top of the normal damage bonus."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddDamageRollBonus(3, "Venom Coating"))
        self.add_weapon_improvement(
            Reskin(
                "Venomfang Dagger",
                "Coated in a potent, self-replenishing venom that adds +3 to every "
                "damage roll, on top of your normal ability modifier.",
            )
        )


class Colossustrike(Greatclub):
    """A Greatclub variant demonstrating SetDamageDie: the damage die is
    overridden to something larger than the base weapon's own die."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(SetDamageDie(WeaponsDamageRolls.D12x2))
        self.add_weapon_improvement(
            Reskin(
                "Colossustrike",
                "This oversized greatclub has been reinforced with iron bands, "
                "upgrading its damage die to 2d12.",
            )
        )


class FrostbrandBlade(Longsword):
    """A Longsword variant demonstrating SetDamageType: the damage type is
    overridden from the base weapon's."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(SetDamageType(WeaponsDamageTypes.COLD))
        self.add_weapon_improvement(
            Reskin(
                "Frostbrand Blade",
                "Forged from enchanted ice, this longsword deals Cold damage "
                "instead of Slashing damage.",
            )
        )


class LungingLongsword(Longsword):
    """A Longsword variant demonstrating AddWeaponProperty: a property is
    added on top of the base weapon's own list."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(AddWeaponProperty(WeaponProperty.REACH))
        self.add_weapon_improvement(
            Reskin(
                "Lunging Longsword",
                "A telescoping blade mechanism grants this longsword the Reach "
                "property, letting you strike foes 10 feet away.",
            )
        )


class LoremastersRapier(Rapier):
    """A Rapier variant demonstrating AddWeaponDescription: extra text is
    appended to the base weapon's description."""

    def setup_improvements(self) -> None:
        # SetItemName/SetItemValue/SetItemHomebrew individually here, rather
        # than the Reskin bundle, since Reskin's description would *replace*
        # rather than *append to* the base description below.
        self.add_weapon_improvement(SetItemName("Loremaster's Rapier"))
        self.add_weapon_improvement(SetItemValue(None))
        self.add_weapon_improvement(SetItemHomebrew())
        self.add_weapon_improvement(
            AddItemDescription("An inquisitive blade that whispers secrets to its wielder.")
        )
        self.add_weapon_improvement(
            AddItemDescription(
                "Once per long rest, you can ask the blade a question about a "
                "creature it has struck; it answers with a single true fact."
            )
        )


class StormcallerMace(Mace):
    """A Mace variant demonstrating AddExtraDamage: bonus damage dice are
    layered on top of the base weapon's."""

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(
            AddExtraDamage(
                WeaponsDamageRolls.D6,
                WeaponsDamageTypes.LIGHTNING,
                note="crackles with static charge",
            )
        )
        self.add_weapon_improvement(
            Reskin(
                "Stormcaller Mace",
                "Crackling with pent-up static, this mace deals an extra 1d6 "
                "Lightning damage on every hit.",
            )
        )


# ──────────────────────────────────────────────────────────────────────────────
# Magical Weapons
# ──────────────────────────────────────────────────────────────────────────────


class FlameTongueSword(AbstractWeapon):
    """A magical sword wreathed in flames, dealing extra fire damage on hit."""

    def base_stats(self) -> None:
        self.name = "Flame Tongue Sword"
        self.ability = Ability.STRENGTH
        self.properties = [WeaponProperty.VERSATILE_10]
        self.mastery = WeaponMastery.TOPPLE
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.SLASHING
        self.damage_roll = WeaponsDamageRolls.D8
        self.description_text = (
            "This sword is wreathed in magical flames. "
            "It deals an extra 2d6 fire damage on a hit. "
            "Requires attunement (rare)."
        )
        self.extra_damage = [
            ExtraDamage(
                damage_roll=WeaponsDamageRolls.D6x2,
                damage_type=WeaponsDamageTypes.FIRE,
                note="magical flames",
            )
        ]
        self.rarity = ItemRarity.RARE
        self.requires_attunement = True
        self.add_character_improvement(
            AbilityScoreBonus(
                [(Ability.STRENGTH, 1)], total=1, error_prefix="Flame Tongue Sword bonus"
            )
        )


class SkirmishersShortsword(Shortsword):
    """A magical Shortsword demonstrating a character-affecting subfeature
    (`_innate_subfeatures`, i.e. the weapon's own `subfeatures=` - the same
    mechanism RingOfIntelligence uses) rather than a WeaponSubFeature: it
    hones the wielder's own footwork, not the blade itself."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.UNCOMMON
        self.add_character_improvement(
            SkillBonus(Skill.ACROBATICS, 2, source="Skirmisher's Shortsword")
        )

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(
            Reskin(
                "Skirmisher's Shortsword",
                "This lightweight blade trains its wielder's footwork. "
                "While wielding it, you gain a +2 bonus to Dexterity (Acrobatics) checks.",
            )
        )


class VanguardsSpear(Spear):
    """A magical Spear demonstrating a different character-affecting
    subfeature (InitiativeRollCondition): it keeps its wielder a half-step
    ahead of danger, granting Advantage on Initiative rolls rather than
    changing anything about the spear's own attack or damage."""

    def base_stats(self) -> None:
        super().base_stats()
        self.rarity = ItemRarity.UNCOMMON
        self.add_character_improvement(InitiativeRollCondition(DiceRollCondition.ADVANTAGE))

    def setup_improvements(self) -> None:
        self.add_weapon_improvement(
            Reskin(
                "Vanguard's Spear",
                "This spear hums with a restless energy, sharpening its wielder's "
                "reflexes. While wielding it, you have Advantage on Initiative rolls.",
            )
        )


### Utility functions


_DAMAGE_TYPE_CSS_CLASS = {
    WeaponsDamageTypes.SLASHING: "wtag-dmg-slashing",
    WeaponsDamageTypes.PIERCING: "wtag-dmg-piercing",
    WeaponsDamageTypes.BLUDGEONING: "wtag-dmg-bludgeoning",
    WeaponsDamageTypes.ACID: "wtag-dmg-acid",
    WeaponsDamageTypes.COLD: "wtag-dmg-cold",
    WeaponsDamageTypes.FIRE: "wtag-dmg-fire",
    WeaponsDamageTypes.LIGHTNING: "wtag-dmg-lightning",
    WeaponsDamageTypes.THUNDER: "wtag-dmg-thunder",
    WeaponsDamageTypes.NECROTIC: "wtag-dmg-necrotic",
    WeaponsDamageTypes.RADIANT: "wtag-dmg-radiant",
    WeaponsDamageTypes.POISON: "wtag-dmg-poison",
    WeaponsDamageTypes.PSYCHIC: "wtag-dmg-psychic",
    WeaponsDamageTypes.FORCE: "wtag-dmg-force",
}


def _write_single_weapon(
    weapon: AbstractWeapon,
    character_stat_block: CharacterStatBlock,
    file: TextIO,
):
    attack_bonus_int = weapon.calculate_total_attack_roll_bonus_int(
        character_stat_block
    )
    attack_bonus_str = f"{attack_bonus_int:+}"

    damage_bonus_int = weapon.calculate_damage_bonus_int(character_stat_block)
    if weapon._damage_bonus_override is not None:
        damage_bonus_label = "fixed"
    else:
        _, damage_bonus_label = weapon._calculate_ability_modifier_bonus(character_stat_block)
    damage_roll_str = f"{weapon.damage_roll.value} {damage_bonus_int:+} ({damage_bonus_label})"

    # Add extra damage if present
    if weapon.extra_damage:
        extra_damages = " + ".join(ed.format_damage() for ed in weapon.extra_damage)
        damage_roll_str += f" + {extra_damages}"

    proficient_label = "Proficient" if weapon.player_is_proficient else "Not proficient"

    prop_names = (
        ", ".join(p.value for p in weapon.properties) if weapon.properties else "—"
    )

    mastery_label = ""
    if weapon.mastery:
        mastery_label = weapon.mastery.value
        if weapon.player_has_mastery:
            mastery_label += " ✓"

    file.write("<table class='weapon-card'>\n")

    # ── Weapon name header ──────────────────────────────────────────────────
    wielded_tag = ""
    if not isinstance(weapon, UnarmedStrike):
        if weapon.is_wearing:
            wielded_tag = " <span class='wtag wtag-worn'>Wielded</span>"
        else:
            wielded_tag = " <span class='wtag wtag-not-worn'>Not wielded</span>"
    file.write(f"<tr><th class='weapon-name' colspan='2'>{weapon.name}{wielded_tag}</th></tr>\n")

    # ── Quick-stats row ─────────────────────────────────────────────────────
    # Two cells: left = type/category info, right = roll info
    type_cell = (
        f"{weapon.weapon_type.value}"
        f"<span class='wsep'>·</span>"
        f"{proficient_label}"
    )
    damage_type_class = _DAMAGE_TYPE_CSS_CLASS.get(weapon.damage_type, "")
    damage_type_tag = f" <span class='wtag {damage_type_class}'>{weapon.damage_type.value}</span>"
    roll_cell = (
        f"<span class='wlabel'>Attack</span> 1d20 {attack_bonus_str}"
        f"<span class='wsep'>·</span>"
        f"<span class='wlabel'>Damage</span> {damage_roll_str}{damage_type_tag}"
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
    if weapon.properties or mastery_label:
        tags_html = ""
        for prop in weapon.properties:
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
    for prop in weapon.properties:
        prop_desc_processed = StringUtils.boxes_to_html(prop.description)
        prop_desc_html = prop_desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-prop-row'>"
            f"<td class='wprop-label'>{prop.value}</td>"
            f"<td class='wprop-desc'>{prop_desc_html}</td>"
            f"</tr>\n"
        )

    # ── Mastery description (only if the player has mastery) ────────────────
    if weapon.mastery and weapon.player_has_mastery:
        mastery_desc_processed = StringUtils.boxes_to_html(weapon.mastery.description)
        mastery_desc_html = mastery_desc_processed.replace("\n", "<br>")
        file.write(
            f"<tr class='weapon-mastery-row'>"
            f"<td class='wmastery-label'>Mastery — {weapon.mastery.value}</td>"
            f"<td class='wmastery-desc'>{mastery_desc_html}</td>"
            f"</tr>\n"
        )

    # ── Additional description ───────────────────────────────────────────────
    if weapon.description_text:
        # Replace newlines with <br> for HTML display
        desc_processed = StringUtils.boxes_to_html(weapon.description_text)
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
