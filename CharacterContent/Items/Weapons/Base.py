from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable, NamedTuple, Optional, TextIO
from Utils import DamageCalculator
from Core.Definitions import Ability, DiceRollCondition, Die
from CharacterContent.Features.Core.Improvements import (
    ItemImprovement,
    CharacterImprovement,
)
from CharacterContent.Items.Items import Item, ItemCategory, ItemRarity
from Model.Character import Character
from Core.Weapons import (
    WeaponMastery,
    WeaponProficiency,
    WeaponProperty,
    WeaponType,
    WeaponDamageRolls,
    WeaponDamageTypes,
)
from .ExtraDamage import ExtraDamage


class BonusPart(NamedTuple):
    """One part of a weapon's attack or damage roll bonus. A `from_stats`
    part (ability modifier, proficiency bonus) comes from the wielder's
    stats and is written by name ("Dex Mod"); any other part is a flat
    bonus written as its value and source ("2 (Archery Fighting Style)")."""

    value: int
    label: str
    from_stats: bool = False


class AbstractWeapon(Item, ABC):
    """Abstract base class for weapons. Weapons are wearable items: their
    improvements only apply while worn/wielded (is_wearing).

    Two independent ways to attach behavior to a weapon:
    - `improvements=[...]` (list[CharacterImprovement], defined in CharacterContent.Features.Core.Improvements):
      character-affecting effects, applied to the wielder's stat block while
      worn - e.g. FlameTongueSword granting +1 Strength, the same mechanism
      RingOfIntellect uses in CharacterContent.Items.Items.
    - `weapon_improvements=[...]` (list[ItemImprovement], defined below and in
      CharacterContent.Features.Core.Improvements): typically a WeaponImprovement - a
      weapon-only effect that modifies the weapon itself (damage die/type,
      properties, attack/damage bonuses, ...), not applicable to any other
      item type - but also accepts the generic ItemImprovements (Reskin,
      SetItemName, ...). See the WeaponImprovement showcase further down."""

    # Required fields every base_stats() must set; declared here (with no
    # class-level value) purely so static type checkers know they exist.
    name: str
    ability: Ability
    properties: list[WeaponProperty]
    weapon_type: WeaponType
    damage_type: WeaponDamageTypes
    damage_roll: WeaponDamageRolls

    def __init__(
        self,
        player_is_proficient: bool = False,
        player_has_mastery: bool = False,
        attack_roll_bonuses: Optional[list[tuple[int, str]]] = None,
        ability: Optional[Ability] = None,
        is_wearing: bool = True,
        category: ItemCategory = ItemCategory.WEAPON,
        slots: int = 1,
        improvements: Optional[list[CharacterImprovement]] = None,
        weapon_improvements: Optional[list[ItemImprovement]] = None,
    ):
        self.player_is_proficient = player_is_proficient
        self.player_has_mastery = player_has_mastery
        self.attack_roll_bonuses = (
            attack_roll_bonuses if attack_roll_bonuses is not None else []
        )
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
        # Character-affecting CharacterImprovements innate to this weapon (e.g. the +1
        # to Strength granted just by owning a Flame Tongue Sword). Distinct
        # from WeaponImprovement, which modifies the weapon itself, not the
        # wielder.
        self.character_improvements: list[CharacterImprovement] = []

        self.base_stats()

        for weapon_improvement in weapon_improvements or []:
            self.add_weapon_improvement(weapon_improvement)
        self.setup_improvements()

        super().__init__(
            name=self.name,
            rarity=self.rarity,
            requires_attunement=self.requires_attunement,
            category=category,
            weight=self.weight,
            slots=slots,
            description_text=self.description_text,
            improvements=self.character_improvements + list(improvements or []),
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

    def add_weapon_improvement(self, weapon_improvement: ItemImprovement) -> None:
        """Attach an ItemImprovement to this weapon - typically a
        WeaponImprovement (a weapon-only improvement: damage die/type,
        properties, attack/damage bonuses, ...), but also accepts the
        generic ones (Reskin, SetItemName, ...) since those apply to any
        item. Named for clarity alongside add_character_improvement(),
        which attaches an effect on the wielder instead."""
        self.add_improvement(weapon_improvement)

    def _calculate_ability_modifier_bonus(
        self, character: Character
    ) -> tuple[int, str]:
        if self._ability_override is not None:
            ability = self._ability_override
            return character.get_ability_modifier(ability), ability.value

        abilities_to_consider = {self.ability}

        if WeaponProperty.FINESSE in self.properties:
            abilities_to_consider.add(Ability.STRENGTH)
            abilities_to_consider.add(Ability.DEXTERITY)

        # Ties (e.g. equal Strength/Dexterity on a Finesse weapon) keep the
        # first ability in Ability declaration order - iterating a set of
        # Ability members directly would pick arbitrarily, since Ability
        # inherits str and str hashing is randomized per process.
        order = list(Ability)
        best_ability_modifier = -9999
        best_ability = None
        for ability in sorted(abilities_to_consider, key=order.index):
            ability_modifier = character.get_ability_modifier(ability)
            if ability_modifier > best_ability_modifier:
                best_ability_modifier = ability_modifier
                best_ability = ability.value

        if best_ability is None:
            raise ValueError("No valid ability found for weapon damage calculation.")

        return best_ability_modifier, best_ability

    def calculate_ability_modifier_bonus(self, character: Character) -> str:
        ability_modifier, ability = self._calculate_ability_modifier_bonus(character)
        return f"{ability_modifier} (ability mod: {ability})"

    def is_proficient(self, character: Character) -> bool:
        """Whether the wielder is proficient with this weapon: an explicit
        player_is_proficient override (e.g. Unarmed Strike), or any weapon
        proficiency recorded on the stat block - worked out on read, so it
        doesn't matter when the proficiency or the weapon was added."""
        return self.player_is_proficient or is_proficient_with(
            self, character.ledger.equipment_training.weapon_proficiencies
        )

    def has_mastery(self, weapon_masteries: "list[AbstractWeapon]") -> bool:
        """Whether the wielder can use this weapon's mastery property: an
        explicit player_has_mastery, or a chosen Weapon Mastery of the same
        kind of weapon. Worked out on read, so the weapon is never changed."""
        return self.player_has_mastery or any(
            type(self) is type(mastery) for mastery in weapon_masteries
        )

    def attack_roll_condition(self, character: Character) -> DiceRollCondition:
        """Disadvantage when the attack uses Strength or Dexterity while
        wearing armor the wielder lacks training with (2024 PHB)."""
        _, ability_name = self._calculate_ability_modifier_bonus(character)
        if character.has_untrained_armor_disadvantage(Ability(ability_name)):
            return DiceRollCondition.DISADVANTAGE
        return DiceRollCondition.NEUTRAL

    def _calculate_proficiency_damage_bonus(self, character: Character) -> int:
        if self.is_proficient(character):
            proficiency_bonus = character.get_proficiency_bonus()
            return proficiency_bonus
        return 0

    def calculate_proficiency_damage_bonus(self, character: Character) -> str:
        proficiency_bonus = self._calculate_proficiency_damage_bonus(character)
        if proficiency_bonus > 0:
            return f"{proficiency_bonus} (Proficient)"
        return "0 (Not Proficient)"

    def get_attack_roll_bonuses(self, character: Character) -> list[tuple[int, str]]:
        """This weapon's own attack roll bonuses (e.g. a +1 weapon), then the
        wielder's that apply to it (e.g. the Archery fighting style) - those
        are recorded on the stat block, never written into the weapon."""
        return (
            self.attack_roll_bonuses
            + character.ledger.weapon_bonuses.attack_bonuses(self)
        )

    def get_damage_roll_bonuses(self, character: Character) -> list[tuple[int, str]]:
        """Damage roll counterpart of get_attack_roll_bonuses."""
        return (
            self.damage_roll_bonuses
            + character.ledger.weapon_bonuses.damage_bonuses(self)
        )

    def calculate_total_attack_roll_bonus(self, character: Character) -> str:
        if self._attack_roll_override is not None:
            return f"{self._attack_roll_override:+} (fixed)"
        attack_roll_bonus = self.calculate_ability_modifier_bonus(character)
        attack_roll_bonus += f" + {self.calculate_proficiency_damage_bonus(character)}"
        for _, bonus in self.get_attack_roll_bonuses(character):
            attack_roll_bonus += f" + {bonus}"
        return attack_roll_bonus

    @staticmethod
    def _bonus_source(value: int, label: str) -> str:
        """The source named in a bonus label - "Archery Fighting Style" out
        of "2 (Archery Fighting Style)" - or the whole label when it isn't
        in that "<value> (<source>)" shape."""
        prefix = f"{value} ("
        if label.startswith(prefix) and label.endswith(")"):
            return label[len(prefix) : -1]
        return label

    def _ability_modifier_part(self, character: Character) -> BonusPart:
        modifier, ability_name = self._calculate_ability_modifier_bonus(character)
        short_name = Ability(ability_name).short_name.title()
        return BonusPart(modifier, f"{short_name} Mod", from_stats=True)

    def get_attack_roll_breakdown(self, character: Character) -> list[BonusPart]:
        """Each part of the attack roll bonus: ability modifier, proficiency
        bonus (when proficient), then every flat bonus. A fixed override is
        its single part. Sums to calculate_total_attack_roll_bonus_int."""
        if self._attack_roll_override is not None:
            return [BonusPart(self._attack_roll_override, "fixed")]
        parts = [self._ability_modifier_part(character)]
        proficiency_bonus = self._calculate_proficiency_damage_bonus(character)
        if proficiency_bonus:
            parts.append(
                BonusPart(proficiency_bonus, "Proficiency Bonus", from_stats=True)
            )
        parts += [
            BonusPart(bonus, self._bonus_source(bonus, label))
            for bonus, label in self.get_attack_roll_bonuses(character)
        ]
        return parts

    def get_damage_roll_breakdown(self, character: Character) -> list[BonusPart]:
        """Each part of the flat bonus added to the damage die: ability
        modifier, then every flat bonus. A fixed override is its single
        part. Sums to calculate_damage_bonus_int."""
        if self._damage_bonus_override is not None:
            return [BonusPart(self._damage_bonus_override, "fixed")]
        parts = [self._ability_modifier_part(character)]
        parts += [
            BonusPart(bonus, self._bonus_source(bonus, label))
            for bonus, label in self.get_damage_roll_bonuses(character)
        ]
        return parts

    def calculate_total_attack_roll_bonus_int(self, character: Character) -> int:
        return sum(part.value for part in self.get_attack_roll_breakdown(character))

    def calculate_damage_bonus_int(self, character: Character) -> int:
        """Flat bonus added to the damage die (ability modifier by default,
        or a fixed override), plus any additive damage-roll bonuses."""
        return sum(part.value for part in self.get_damage_roll_breakdown(character))

    def get_description(self, character: Character) -> Optional[str]:
        return None

    def calculate_hit_probabilities(
        self,
        character: Character,
        condition: DamageCalculator.DiceRollCondition = DamageCalculator.DiceRollCondition.NEUTRAL,
    ) -> list[tuple[int, float]]:
        """Return hit probability for each AC from 10 to 25 (inclusive)."""
        attack_roll_bonus = self.calculate_total_attack_roll_bonus_int(character)
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

    def write_to_file(self, character: Character, file: TextIO):
        pass  # HTML rendering is handled by write_weapons_to_file

    def write_damage_report(
        self,
        character: Character,
        file,
    ) -> None:
        attack_roll_die = DamageCalculator.Die.D20
        attack_roll_condition = DamageCalculator.DiceRollCondition.NEUTRAL
        attack_roll_bonus = self.calculate_total_attack_roll_bonus_int(character)
        damage_die = Die.die_from_value(self.damage_roll.die_size)
        number_of_damage_dice = self.damage_roll.number_of_dice
        damage_condition = DamageCalculator.DiceRollCondition.NEUTRAL
        damage_bonus = self.calculate_damage_bonus_int(character)

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


def weapon_matches_proficiency(weapon: AbstractWeapon, proficiency: Enum) -> bool:
    is_simple = weapon.weapon_type in (
        WeaponType.SIMPLE_MELEE,
        WeaponType.SIMPLE_RANGED,
    )
    is_martial = weapon.weapon_type in (
        WeaponType.MARTIAL_MELEE,
        WeaponType.MARTIAL_RANGED,
    )
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
    if proficiency == WeaponProficiency.MARTIAL_MELEE_NOT_HEAVY_OR_TWO_HANDED:
        return (
            weapon.weapon_type == WeaponType.MARTIAL_MELEE
            and WeaponProperty.HEAVY not in weapon.properties
            and WeaponProperty.TWO_HANDED not in weapon.properties
        )
    if proficiency in _SINGLE_WEAPON_PROFICIENCIES:
        # By class name, so magic versions (subclasses) match too - importing
        # the weapon modules here would be circular.
        kind = _SINGLE_WEAPON_PROFICIENCIES[proficiency]
        return any(cls.__name__ == kind for cls in type(weapon).__mro__)
    raise ValueError(f"Unhandled weapon proficiency: {proficiency}")


_SINGLE_WEAPON_PROFICIENCIES: dict[Enum, str] = {
    WeaponProficiency.SCIMITAR: "Scimitar",
    WeaponProficiency.LONGBOW: "Longbow",
    WeaponProficiency.SHORTBOW: "Shortbow",
}


def is_proficient_with(
    weapon: AbstractWeapon,
    proficiencies: Iterable[Enum],
) -> bool:
    return any(weapon_matches_proficiency(weapon, p) for p in proficiencies)


class UnarmedStrike(AbstractWeapon):
    def __init__(
        self,
        ability: Optional[Ability] = None,
        damage_roll: Optional[WeaponDamageRolls] = None,
        **kwargs,
    ):
        if ability is not None and ability not in (
            Ability.STRENGTH,
            Ability.DEXTERITY,
        ):
            raise ValueError("Unarmed Strike ability must be STR or DEX.")
        if kwargs.get("player_has_mastery"):
            raise ValueError("Unarmed Strike cannot have weapon mastery.")
        self._damage_roll_arg: Optional[WeaponDamageRolls] = damage_roll
        super().__init__(ability=ability, **kwargs)

    def base_stats(self) -> None:
        self.name = "Unarmed Strike"
        self.ability = self._ability_override or Ability.STRENGTH
        self.properties = []
        self.mastery = None
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponDamageTypes.BLUDGEONING
        self.damage_roll = self._damage_roll_arg or WeaponDamageRolls.D1
        self.description_text = (
            "You can replace one attack with a grapple or shove. Grapple: target within reach and no more than one size larger, requires a free hand; make an Athletics check contested by Athletics or Acrobatics; on success, the target’s speed becomes 0, you can move it at half speed, and you can release it at any time; it can repeat the check to escape and automatically fails if incapacitated. "
            "Shove: same limits and check; on success, either knock the target prone or push it 5 ft. "
        )
