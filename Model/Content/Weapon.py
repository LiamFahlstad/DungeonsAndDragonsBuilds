from abc import ABC, abstractmethod
from enum import Enum
from typing import Iterable, NamedTuple, Optional
from Utils import DamageCalculator
from Core.Definitions import Ability, DiceRollCondition
from Model.Content.Improvements import ItemImprovement, CharacterImprovement
from Model.Content.Item import Item, ItemCategory, ItemRarity
from Model.View import CharacterView
from Core.Weapons import (
    WeaponMastery,
    WeaponProficiency,
    WeaponProperty,
    WeaponTraits,
    WeaponType,
    WeaponDamageRolls,
    WeaponDamageTypes,
    weapon_matches_proficiency,
)
from Model.Content.ExtraDamage import ExtraDamage


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
    - `improvements=[...]` (list[CharacterImprovement], defined in Model.Content.Improvements):
      character-affecting effects, applied to the wielder's stat block while
      worn - e.g. FlameTongueSword granting +1 Strength, the same mechanism
      RingOfIntellect uses in CharacterContent.Items.Items.
    - `weapon_improvements=[...]` (list[ItemImprovement], defined below and in
      Model.Content.Improvements): typically a WeaponImprovement - a
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

    # The weapon's own kind, for the few a proficiency names on its own
    # (Scimitar, Longbow, Shortbow). Magic versions subclass those, so
    # they inherit it.
    kind: Optional[WeaponProficiency] = None
    is_unarmed_strike = False

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
        self, character: CharacterView
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

    def calculate_ability_modifier_bonus(self, character: CharacterView) -> str:
        ability_modifier, ability = self._calculate_ability_modifier_bonus(character)
        return f"{ability_modifier} (ability mod: {ability})"

    @property
    def traits(self) -> WeaponTraits:
        """The facts proficiency rules and wielder bonuses check."""
        return WeaponTraits(
            weapon_type=self.weapon_type,
            properties=frozenset(self.properties),
            kind=self.kind,
            is_unarmed_strike=self.is_unarmed_strike,
        )

    def is_proficient(self, character: CharacterView) -> bool:
        """Whether the wielder is proficient with this weapon: an explicit
        player_is_proficient override (e.g. Unarmed Strike), or any weapon
        proficiency recorded on the stat block - worked out on read, so it
        doesn't matter when the proficiency or the weapon was added."""
        return self.player_is_proficient or character.is_proficient_with_weapon(
            self.traits
        )

    def has_mastery(self, weapon_masteries: "list[AbstractWeapon]") -> bool:
        """Whether the wielder can use this weapon's mastery property: an
        explicit player_has_mastery, or a chosen Weapon Mastery of the same
        kind of weapon. Worked out on read, so the weapon is never changed."""
        return self.player_has_mastery or any(
            type(self) is type(mastery) for mastery in weapon_masteries
        )

    def attack_roll_condition(self, character: CharacterView) -> DiceRollCondition:
        """Disadvantage when the attack uses Strength or Dexterity while
        wearing armor the wielder lacks training with (2024 PHB)."""
        _, ability_name = self._calculate_ability_modifier_bonus(character)
        if character.has_untrained_armor_disadvantage(Ability(ability_name)):
            return DiceRollCondition.DISADVANTAGE
        return DiceRollCondition.NEUTRAL

    def _calculate_proficiency_damage_bonus(self, character: CharacterView) -> int:
        if self.is_proficient(character):
            proficiency_bonus = character.get_proficiency_bonus()
            return proficiency_bonus
        return 0

    def calculate_proficiency_damage_bonus(self, character: CharacterView) -> str:
        proficiency_bonus = self._calculate_proficiency_damage_bonus(character)
        if proficiency_bonus > 0:
            return f"{proficiency_bonus} (Proficient)"
        return "0 (Not Proficient)"

    def get_attack_roll_bonuses(
        self, character: CharacterView
    ) -> list[tuple[int, str]]:
        """This weapon's own attack roll bonuses (e.g. a +1 weapon), then the
        wielder's that apply to it (e.g. the Archery fighting style) - those
        are recorded on the stat block, never written into the weapon."""
        return self.attack_roll_bonuses + character.get_weapon_attack_bonuses(
            self.traits
        )

    def get_damage_roll_bonuses(
        self, character: CharacterView
    ) -> list[tuple[int, str]]:
        """Damage roll counterpart of get_attack_roll_bonuses."""
        return self.damage_roll_bonuses + character.get_weapon_damage_bonuses(
            self.traits
        )

    def calculate_total_attack_roll_bonus(self, character: CharacterView) -> str:
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

    def _ability_modifier_part(self, character: CharacterView) -> BonusPart:
        modifier, ability_name = self._calculate_ability_modifier_bonus(character)
        short_name = Ability(ability_name).short_name.title()
        return BonusPart(modifier, f"{short_name} Mod", from_stats=True)

    def get_attack_roll_breakdown(self, character: CharacterView) -> list[BonusPart]:
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

    def get_damage_roll_breakdown(self, character: CharacterView) -> list[BonusPart]:
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

    def calculate_total_attack_roll_bonus_int(self, character: CharacterView) -> int:
        return sum(part.value for part in self.get_attack_roll_breakdown(character))

    def calculate_damage_bonus_int(self, character: CharacterView) -> int:
        """Flat bonus added to the damage die (ability modifier by default,
        or a fixed override), plus any additive damage-roll bonuses."""
        return sum(part.value for part in self.get_damage_roll_breakdown(character))

    def get_description(self, character: CharacterView) -> Optional[str]:
        # Weapons render as weapon cards (Presentation/WeaponCards.py), not
        # as feature cards.
        return None

    def calculate_hit_probabilities(
        self,
        character: CharacterView,
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


def is_proficient_with(
    weapon: AbstractWeapon,
    proficiencies: Iterable[WeaponProficiency],
) -> bool:
    traits = weapon.traits
    return any(weapon_matches_proficiency(traits, p) for p in proficiencies)
