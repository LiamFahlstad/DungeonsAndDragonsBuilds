from abc import ABC, abstractmethod
from typing import Optional, TextIO
from Utils import DamageCalculator
from Core.Definitions import Ability, DiceRollCondition, Die
from CharacterContent.Features.Core.Improvements import ItemImprovement, CharacterImprovement
from CharacterContent.Items.Items import Item, ItemCategory, ItemRarity
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from .Enums import WeaponMastery, WeaponProficiency, WeaponProperty, WeaponType, WeaponsDamageRolls, WeaponsDamageTypes
from .Improvements import ExtraDamage


class AbstractWeapon(Item, ABC):
    """Abstract base class for weapons. Weapons are wearable items: their
    improvements only apply while worn/wielded (is_wearing).

    Two independent ways to attach behavior to a weapon:
    - `improvements=[...]` (list[CharacterImprovement], defined in CharacterContent.Features.Core.Improvements):
      character-affecting effects, applied to the wielder's stat block while
      worn - e.g. FlameTongueSword granting +1 Strength, the same mechanism
      RingOfIntelligence uses in CharacterContent.Items.Items.
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
        improvements: Optional[list[CharacterImprovement]] = None,
        weapon_improvements: Optional[list[ItemImprovement]] = None,
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
        self._damage_roll_arg: Optional[WeaponsDamageRolls] = damage_roll
        super().__init__(ability=ability, **kwargs)

    def base_stats(self) -> None:
        self.name = "Unarmed Strike"
        self.ability = self._ability_override or Ability.STRENGTH
        self.properties = []
        self.mastery = None
        self.weapon_type = WeaponType.MARTIAL_MELEE
        self.damage_type = WeaponsDamageTypes.BLUDGEONING
        self.damage_roll = self._damage_roll_arg or WeaponsDamageRolls.D1
        self.description_text = (
            "You can replace one attack with a grapple or shove. Grapple: target within reach and no more than one size larger, requires a free hand; make an Athletics check contested by Athletics or Acrobatics; on success, the target’s speed becomes 0, you can move it at half speed, and you can release it at any time; it can repeat the check to escape and automatically fails if incapacitated. "
            "Shove: same limits and check; on success, either knock the target prone or push it 5 ft. "
        )
