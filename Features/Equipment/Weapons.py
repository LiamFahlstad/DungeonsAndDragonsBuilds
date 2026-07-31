from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional, TextIO

from Utils import DamageCalculator
from Core.Definitions import Ability, Die
from Features.Core.SubFeatures import AbilityScoreBonus, SubFeature
from Features.Items.Items import ItemCategory, ItemRarity, WearableItem
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
    weight: Optional[float] = None
    value: Optional[float] = None
    is_homebrew: bool = False
    rarity: ItemRarity = ItemRarity.COMMON
    requires_attunement: bool = False
    # Character-affecting SubFeatures innate to this weapon (e.g. the +1 to
    # Strength granted just by owning a Flame Tongue Sword). Distinct from
    # WeaponSubFeature below, which modifies the weapon itself, not the wielder.
    subfeatures: Optional[list[SubFeature]] = None


# ──────────────────────────────────────────────────────────────────────────────
# WeaponSubFeature: composable modifiers applied to a weapon at construction
# time (e.g. a magic weapon variant, or a homebrew reskin). Mirrors
# Features.Core.SubFeatures.SubFeature, but its apply() mutates the weapon
# instance instead of the character stat block, since these improvements
# (attack/damage bonuses, damage die/type, properties, flavor text) are
# properties of the weapon itself, not of the wielder.
# ──────────────────────────────────────────────────────────────────────────────


class WeaponSubFeature(ABC):
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
        weapon._damage_roll_override = self.damage_roll


class SetDamageType(WeaponSubFeature):
    """Overrides the weapon's damage type (e.g. a frost blade dealing Cold instead of Slashing)."""

    def __init__(self, damage_type: WeaponsDamageTypes):
        self.damage_type = damage_type

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._damage_type_override = self.damage_type


class AddWeaponProperty(WeaponSubFeature):
    """Adds a weapon property (e.g. Finesse, Reach) not already on the weapon."""

    def __init__(self, property: WeaponProperty):
        self.property = property

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._extra_properties.append(self.property)


class AddWeaponDescription(WeaponSubFeature):
    """Appends text to the weapon's additional description."""

    def __init__(self, text: str):
        self.text = text

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._description_additions.append(self.text)


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
        weapon._extra_damage_additions.append(self.extra_damage)


class SetWeaponName(WeaponSubFeature):
    """Overrides the weapon's display name."""

    def __init__(self, name: str):
        self.name = name

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._name_override = self.name


class SetWeaponDescription(WeaponSubFeature):
    """Overrides (replaces, rather than appends to) the weapon's description."""

    def __init__(self, text: str):
        self.text = text

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._description_override = self.text


class SetWeaponValue(WeaponSubFeature):
    """Overrides the weapon's GP value. Pass None to mark it unpriced (e.g. a
    unique magic item that no longer has a standard market price)."""

    def __init__(self, value: Optional[float]):
        self.value = value

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._value_override_set = True
        weapon._value_override = self.value


class SetHomebrew(WeaponSubFeature):
    """Flags the weapon as homebrew (or, with is_homebrew=False, as official)."""

    def __init__(self, is_homebrew: bool = True):
        self.is_homebrew = is_homebrew

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._is_homebrew_override = self.is_homebrew


class Reskin(WeaponSubFeature):
    """Convenience bundle for the common case of rebranding a base weapon as a
    new named variant: overrides its name and description, unsets its GP
    value (it's no longer standard equipment), and flags it as homebrew.
    Equivalent to combining SetWeaponName, SetWeaponDescription,
    SetWeaponValue(None), and SetHomebrew()."""

    def __init__(self, name: str, description: str, is_homebrew: bool = True):
        self.name = name
        self.description = description
        self.is_homebrew = is_homebrew

    def apply(self, weapon: "AbstractWeapon") -> None:
        SetWeaponName(self.name).apply(weapon)
        SetWeaponDescription(self.description).apply(weapon)
        SetWeaponValue(None).apply(weapon)
        SetHomebrew(self.is_homebrew).apply(weapon)


class SetWeaponAbility(WeaponSubFeature):
    """Overrides which ability score is used for the weapon's attack and damage
    rolls (e.g. a Bladesinger using Intelligence instead of Strength/Dexterity),
    replacing the weapon's own ability - and any Finesse Str/Dex comparison -
    outright rather than only being considered as an alternative."""

    def __init__(self, ability: Ability):
        self.ability = ability

    def apply(self, weapon: "AbstractWeapon") -> None:
        weapon._ability_override = self.ability


class AbstractWeapon(WearableItem):
    """Abstract base class for weapons. Weapons are wearable items: their
    subfeatures only apply while worn/wielded (is_wearing)."""

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
        improvements: Optional[list[WeaponSubFeature]] = None,
    ):
        self.player_is_proficient = player_is_proficient
        self.player_has_mastery = player_has_mastery
        self.attack_roll_bonuses = attack_roll_bonuses if attack_roll_bonuses is not None else []
        self.damage_roll_bonuses: list[tuple[int, str]] = []

        # Improvement state, populated below (from `ability`, the
        # `improvements` list, and setup_improvements()) and read by
        # stats()/the attack- and damage-bonus calculations.
        self._ability_override: Optional[Ability] = ability
        self._attack_roll_override: Optional[int] = None
        self._damage_bonus_override: Optional[int] = None
        self._damage_roll_override: Optional[WeaponsDamageRolls] = None
        self._damage_type_override: Optional[WeaponsDamageTypes] = None
        self._extra_properties: list[WeaponProperty] = []
        self._description_additions: list[str] = []
        self._extra_damage_additions: list[ExtraDamage] = []
        self._name_override: Optional[str] = None
        self._description_override: Optional[str] = None
        self._value_override_set: bool = False
        self._value_override: Optional[float] = None
        self._is_homebrew_override: Optional[bool] = None
        for improvement in improvements or []:
            self.add_improvement(improvement)
        self.setup_improvements()

        stats = self.stats()
        super().__init__(
            name=stats.name,
            rarity=stats.rarity,
            requires_attunement=stats.requires_attunement,
            category=category,
            weight=stats.weight,
            slots=slots,
            description_text=stats.additional_description or "",
            subfeatures=list(stats.subfeatures or []) + list(subfeatures or []),
            is_wearing=is_wearing,
            is_homebrew=stats.is_homebrew,
            value=stats.value,
        )

    def add_improvement(self, improvement: WeaponSubFeature) -> None:
        """Apply a single WeaponSubFeature to this weapon. This is the one
        access point for composing improvements, whether they come from the
        `improvements=` constructor list or from a subclass's
        setup_improvements() override."""
        improvement.apply(self)

    def setup_improvements(self) -> None:
        """Override to bake in this weapon's default improvements, e.g.:

            def setup_improvements(self) -> None:
                self.add_improvement(SetDamageType(WeaponsDamageTypes.COLD))

        Called once during __init__, after any improvements passed in via
        the constructor's `improvements=` list."""

    @abstractmethod
    def base_stats(self) -> WeaponsStats:
        raise NotImplementedError("Subclasses must implement base_stats().")

    def stats(self) -> WeaponsStats:
        """Effective stats: this weapon's base_stats() with any improvements
        (WeaponSubFeature passed to __init__) layered on top."""
        base = self.base_stats()
        if not (
            self._damage_roll_override
            or self._damage_type_override
            or self._extra_properties
            or self._description_additions
            or self._extra_damage_additions
            or self._name_override
            or self._description_override is not None
            or self._value_override_set
            or self._is_homebrew_override is not None
        ):
            return base

        properties = list(base.properties)
        for prop in self._extra_properties:
            if prop not in properties:
                properties.append(prop)

        if self._description_override is not None:
            additional_description = self._description_override
        else:
            additional_description = base.additional_description or ""
            for text in self._description_additions:
                additional_description = (
                    f"{additional_description}\n{text}" if additional_description else text
                )

        extra_damage = list(base.extra_damage or []) + self._extra_damage_additions

        return replace(
            base,
            name=self._name_override or base.name,
            properties=properties,
            damage_roll=self._damage_roll_override or base.damage_roll,
            damage_type=self._damage_type_override or base.damage_type,
            additional_description=additional_description or None,
            extra_damage=extra_damage or None,
            value=self._value_override if self._value_override_set else base.value,
            is_homebrew=(
                self._is_homebrew_override
                if self._is_homebrew_override is not None
                else base.is_homebrew
            ),
        )

    def _calculate_ability_modifier_bonus(
        self, character_stat_block: CharacterStatBlock
    ) -> tuple[int, str]:
        if self._ability_override is not None:
            ability = self._ability_override
            return character_stat_block.get_ability_modifier(ability), ability.value

        abilities_to_consider = set()
        abilities_to_consider.add(self.stats().ability)

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
    stats = weapon.stats()
    is_simple = stats.weapon_type in (WeaponType.SIMPLE_MELEE, WeaponType.SIMPLE_RANGED)
    is_martial = stats.weapon_type in (WeaponType.MARTIAL_MELEE, WeaponType.MARTIAL_RANGED)
    if proficiency == WeaponProficiency.SIMPLE:
        return is_simple
    if proficiency == WeaponProficiency.MARTIAL:
        return is_martial
    if proficiency == WeaponProficiency.MARTIAL_LIGHT:
        return is_martial and WeaponProperty.LIGHT in stats.properties
    if proficiency == WeaponProficiency.MARTIAL_FINESSE_OR_LIGHT:
        return is_martial and (
            WeaponProperty.FINESSE in stats.properties
            or WeaponProperty.LIGHT in stats.properties
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

    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Unarmed Strike",
            ability=self._ability_override or Ability.STRENGTH,
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
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Battleaxe",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=4,
            value=10,
        )


class Flail(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Flail",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=2,
            value=10,
        )


class Glaive(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=6,
            value=20,
        )


class Greataxe(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Greataxe",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.CLEAVE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D12,
            weight=7,
            value=30,
        )


class Greatsword(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Greatsword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.GRAZE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D6x2,
            weight=6,
            value=50,
        )


class Halberd(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=6,
            value=20,
        )


class Lance(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=6,
            value=10,
        )


class Longsword(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Longsword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=3,
            value=15,
        )


class Maul(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Maul",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D6x2,
            weight=10,
            value=10,
        )


class Morningstar(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Morningstar",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=4,
            value=15,
        )


class Pike(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=18,
            value=5,
        )


class Rapier(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Rapier",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.FINESSE],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=2,
            value=25,
        )


class Scimitar(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Scimitar",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.FINESSE, WeaponProperty.LIGHT],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D6,
            weight=3,
            value=25,
        )


class Shortsword(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Shortsword",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.FINESSE, WeaponProperty.LIGHT],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
            weight=2,
            value=25,
        )


class Trident(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Trident",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.THROWN, WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=4,
            value=5,
        )


class Warhammer(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Warhammer",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.PUSH,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=2,
            value=15,
        )


class WarPick(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="WarPick",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_10],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=2,
            value=5,
        )


class Whip(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Whip",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.FINESSE, WeaponProperty.REACH],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.MARTIAL_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D4,
            weight=3,
            value=2,
        )


class Club(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Club",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.LIGHT],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D4,
            weight=2,
            value=0.1,
        )


class Dagger(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=1,
            value=2,
        )


class Greatclub(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Greatclub",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.HEAVY, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.PUSH,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D8,
            weight=5,
            value=0.2,
        )


class Handaxe(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Handaxe",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.LIGHT, WeaponProperty.THROWN],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D6,
            weight=2,
            value=5,
        )


class Javelin(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Javelin",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.THROWN],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
            weight=2,
            value=0.5,
        )


class LightHammer(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Light Hammer",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.LIGHT, WeaponProperty.THROWN],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D4,
            weight=2,
            value=2,
        )


class Mace(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Mace",
            ability=Ability.STRENGTH,
            properties=[],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D6,
            weight=4,
            value=5,
        )


class Quarterstaff(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Quarterstaff",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_8],
            mastery=WeaponMastery.TOPPLE,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D6,
            weight=4,
            value=0.2,
        )


class Sickle(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Sickle",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.LIGHT],
            mastery=WeaponMastery.NICK,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.SLASHING,
            damage_roll=WeaponsDamageRolls.D4,
            weight=2,
            value=1,
        )


class Spear(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Spear",
            ability=Ability.STRENGTH,
            properties=[WeaponProperty.VERSATILE_8, WeaponProperty.THROWN],
            mastery=WeaponMastery.SAP,
            weapon_type=WeaponType.SIMPLE_MELEE,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
            weight=3,
            value=1,
        )


class Dart(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Dart",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.FINESSE, WeaponProperty.THROWN],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.SIMPLE_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D4,
            weight=0.25,
            value=0.05,
        )


class LightCrossbow(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=5,
            value=25,
        )


class Shortbow(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Shortbow",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.AMMUNITION, WeaponProperty.TWO_HANDED],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.SIMPLE_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D6,
            weight=2,
            value=25,
        )


class Sling(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Sling",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.AMMUNITION],
            mastery=WeaponMastery.SLOW,
            weapon_type=WeaponType.SIMPLE_RANGED,
            damage_type=WeaponsDamageTypes.BLUDGEONING,
            damage_roll=WeaponsDamageRolls.D4,
            value=0.1,
        )


class Blowgun(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Blowgun",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.AMMUNITION, WeaponProperty.LOADING],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D1,
            weight=1,
            value=10,
        )


class HandCrossbow(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=3,
            value=75,
        )


class HeavyCrossbow(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=18,
            value=50,
        )


class Longbow(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=2,
            value=50,
        )


class Musket(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            weight=10,
            value=500,
        )


class Pistol(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
        return WeaponsStats(
            name="Pistol",
            ability=Ability.DEXTERITY,
            properties=[WeaponProperty.AMMUNITION, WeaponProperty.LOADING],
            mastery=WeaponMastery.VEX,
            weapon_type=WeaponType.MARTIAL_RANGED,
            damage_type=WeaponsDamageTypes.PIERCING,
            damage_roll=WeaponsDamageRolls.D10,
            weight=3,
            value=250,
        )


### HOMEBREW WEAPONS


class Nullblade(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class Bloodletter(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class HuntersHarpoon(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class RicochetBlade(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class RampagingBlade(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class ElementalSword(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class BloodlustBlade(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class CoinflipCutBlade(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class Sundersteel(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


class VampiricEdge(AbstractWeapon):
    def base_stats(self) -> WeaponsStats:
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
            is_homebrew=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# WeaponSubFeature showcase: one weapon per improvement, demonstrating how
# `improvements=[...]` composes on top of a weapon's base_stats().
# ──────────────────────────────────────────────────────────────────────────────


class UnerringBlade(Longsword):
    """A Longsword variant demonstrating SetAttackRollBonus: attack rolls
    always use a fixed bonus, ignoring ability modifier, proficiency, and any
    additive bonuses."""

    def setup_improvements(self) -> None:
        self.add_improvement(SetAttackRollBonus(7))
        self.add_improvement(
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
        self.add_improvement(AddAttackRollBonus(2, "Marksman's Scope"))
        self.add_improvement(
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
        self.add_improvement(SetDamageRollBonus(10))
        self.add_improvement(
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
        self.add_improvement(AddDamageRollBonus(3, "Venom Coating"))
        self.add_improvement(
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
        self.add_improvement(SetDamageDie(WeaponsDamageRolls.D12x2))
        self.add_improvement(
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
        self.add_improvement(SetDamageType(WeaponsDamageTypes.COLD))
        self.add_improvement(
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
        self.add_improvement(AddWeaponProperty(WeaponProperty.REACH))
        self.add_improvement(
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
        # SetWeaponName/SetWeaponValue/SetHomebrew individually here, rather
        # than the Reskin bundle, since Reskin's description would *replace*
        # rather than *append to* the base description below.
        self.add_improvement(SetWeaponName("Loremaster's Rapier"))
        self.add_improvement(SetWeaponValue(None))
        self.add_improvement(SetHomebrew())
        self.add_improvement(
            AddWeaponDescription("An inquisitive blade that whispers secrets to its wielder.")
        )
        self.add_improvement(
            AddWeaponDescription(
                "Once per long rest, you can ask the blade a question about a "
                "creature it has struck; it answers with a single true fact."
            )
        )


class StormcallerMace(Mace):
    """A Mace variant demonstrating AddExtraDamage: bonus damage dice are
    layered on top of the base weapon's."""

    def setup_improvements(self) -> None:
        self.add_improvement(
            AddExtraDamage(
                WeaponsDamageRolls.D6,
                WeaponsDamageTypes.LIGHTNING,
                note="crackles with static charge",
            )
        )
        self.add_improvement(
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

    def base_stats(self) -> WeaponsStats:
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
            rarity=ItemRarity.RARE,
            requires_attunement=True,
            subfeatures=[
                AbilityScoreBonus(
                    [(Ability.STRENGTH, 1)], total=1, error_prefix="Flame Tongue Sword bonus"
                )
            ],
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
    stats = weapon.stats()

    attack_bonus_int = weapon.calculate_total_attack_roll_bonus_int(
        character_stat_block
    )
    attack_bonus_str = f"{attack_bonus_int:+}"

    damage_bonus_int = weapon.calculate_damage_bonus_int(character_stat_block)
    if weapon._damage_bonus_override is not None:
        damage_bonus_label = "fixed"
    else:
        _, damage_bonus_label = weapon._calculate_ability_modifier_bonus(character_stat_block)
    damage_roll_str = f"{stats.damage_roll.value} {damage_bonus_int:+} ({damage_bonus_label})"

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
    wielded_tag = ""
    if not isinstance(weapon, UnarmedStrike):
        if weapon.is_wearing:
            wielded_tag = " <span class='wtag wtag-worn'>Wielded</span>"
        else:
            wielded_tag = " <span class='wtag wtag-not-worn'>Not wielded</span>"
    file.write(f"<tr><th class='weapon-name' colspan='2'>{stats.name}{wielded_tag}</th></tr>\n")

    # ── Quick-stats row ─────────────────────────────────────────────────────
    # Two cells: left = type/category info, right = roll info
    type_cell = (
        f"{stats.weapon_type.value}"
        f"<span class='wsep'>·</span>"
        f"{proficient_label}"
    )
    damage_type_class = _DAMAGE_TYPE_CSS_CLASS.get(stats.damage_type, "")
    damage_type_tag = f" <span class='wtag {damage_type_class}'>{stats.damage_type.value}</span>"
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
