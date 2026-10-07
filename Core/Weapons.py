"""Weapon rules: the enums (properties, masteries, types, proficiency categories
and kinds, damage types and damage rolls), WeaponTraits - the facts about a
weapon that rules and bonuses check - and which weapons a proficiency covers.
The weapons themselves are in CharacterContent/Items/Weapons/, which
re-exports the enums for build files."""

from enum import Enum
from typing import Optional

import attr


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
    MARTIAL_MELEE_NOT_HEAVY_OR_TWO_HANDED = (
        "Melee Martial weapons without the Two-Handed or Heavy property"
    )
    # Single weapon kinds (College of Swords, Bracers of Archery).
    SCIMITAR = "Scimitar"
    LONGBOW = "Longbow"
    SHORTBOW = "Shortbow"


class WeaponDamageTypes(Enum):
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


class WeaponDamageRolls(Enum):
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


@attr.s(frozen=True, auto_attribs=True)
class WeaponTraits:
    """The facts about a weapon that proficiency rules and wielder bonuses
    check (Archery: "Ranged weapons"; Bracers of Archery: "the Longbow and
    Shortbow"). Every weapon exposes its own (AbstractWeapon.traits)."""

    weapon_type: WeaponType
    properties: frozenset[WeaponProperty]
    # The weapon's own kind, for the few a proficiency names on its own
    # (Scimitar, Longbow, Shortbow); None for every other weapon.
    kind: Optional[WeaponProficiency] = None
    is_unarmed_strike: bool = False

    @property
    def is_simple(self) -> bool:
        return self.weapon_type in (WeaponType.SIMPLE_MELEE, WeaponType.SIMPLE_RANGED)

    @property
    def is_martial(self) -> bool:
        return self.weapon_type in (WeaponType.MARTIAL_MELEE, WeaponType.MARTIAL_RANGED)

    @property
    def is_melee(self) -> bool:
        return self.weapon_type in (WeaponType.SIMPLE_MELEE, WeaponType.MARTIAL_MELEE)

    @property
    def is_ranged(self) -> bool:
        return self.weapon_type in (WeaponType.SIMPLE_RANGED, WeaponType.MARTIAL_RANGED)


# Proficiencies that name one kind of weapon rather than a category.
_SINGLE_WEAPON_PROFICIENCIES = (
    WeaponProficiency.SCIMITAR,
    WeaponProficiency.LONGBOW,
    WeaponProficiency.SHORTBOW,
)


def weapon_matches_proficiency(
    traits: WeaponTraits, proficiency: WeaponProficiency
) -> bool:
    """Whether `proficiency` covers a weapon with these traits."""
    properties = traits.properties
    if proficiency == WeaponProficiency.SIMPLE:
        return traits.is_simple
    if proficiency == WeaponProficiency.MARTIAL:
        return traits.is_martial
    if proficiency == WeaponProficiency.MARTIAL_LIGHT:
        return traits.is_martial and WeaponProperty.LIGHT in properties
    if proficiency == WeaponProficiency.MARTIAL_FINESSE_OR_LIGHT:
        return traits.is_martial and (
            WeaponProperty.FINESSE in properties or WeaponProperty.LIGHT in properties
        )
    if proficiency == WeaponProficiency.MARTIAL_MELEE_NOT_HEAVY_OR_TWO_HANDED:
        return (
            traits.weapon_type == WeaponType.MARTIAL_MELEE
            and WeaponProperty.HEAVY not in properties
            and WeaponProperty.TWO_HANDED not in properties
        )
    if proficiency in _SINGLE_WEAPON_PROFICIENCIES:
        return traits.kind == proficiency
    raise ValueError(f"Unhandled weapon proficiency: {proficiency}")
