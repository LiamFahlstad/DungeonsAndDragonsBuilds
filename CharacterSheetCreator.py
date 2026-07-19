from typing import Any, Optional

import attr

import Definitions
from Definitions import Ability, ApplyWhen, CharacterClass
from Features.CharacterFeats import OriginFeats
from Features.Combat.FightingStyles import (
    FightingStyle,
    FightStyleModifier,
    FightStyleWeaponFeature,
)
from Features.Core.BaseFeatures import Feature
from Features.Equipment.Armor import AbstractArmor
from Features.Equipment.Weapons import AbstractWeapon
from Features.Items import Items
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock
from ToolProficiencies.ToolProficiencies import ToolProficiency
from Utils import CharacterSheetWriters

# Scalar values merge_with treats as "not set": an incoming value equal to one
# of these never overwrites an existing value. 0 is included so that e.g. a
# builder that never touched experience_points (int, default 0) cannot reset
# XP accumulated by an earlier builder. All enums used in sheet fields are str
# enums with non-empty values, so none of them compare equal to "" or 0.
_MERGE_EMPTY_VALUES = (None, [], {}, "", 0)


@attr.dataclass
class CharacterSheetData:
    character_name: Optional[str] = None
    character_subclass: Optional[str] = None
    base_class: Optional[CharacterClass] = None
    level_per_class: dict[CharacterClass, int] = attr.Factory(dict)
    abilities: Optional[AbilitiesStatBlock] = None
    skills: Optional[SkillsStatBlock] = None
    speed: Optional[int] = None
    size: Optional[Definitions.CreatureSize] = None
    saving_throws: Optional[SavingThrowsStatBlock] = None

    features: list[Feature] = attr.Factory(list)
    invocations: list[str] = attr.Factory(list)
    spells: list[tuple[str, Ability, Optional[str]]] = attr.Factory(list)
    spell_casting_ability: Optional[Ability] = None

    spell_slots: dict[int, int] = attr.Factory(dict)

    armors: list[AbstractArmor] = attr.Factory(list)
    weapons: list[AbstractWeapon] = attr.Factory(list)
    weapon_masteries: list[AbstractWeapon] = attr.Factory(list)
    fighting_styles: list[FightingStyle] = attr.Factory(list)
    armor_proficiencies: set[Definitions.ArmorType] = attr.Factory(set)
    items: list[tuple[Items.Item, int]] = attr.Factory(list)  # (item_name, quantity)
    tool_proficiencies: list[ToolProficiency] = attr.Factory(list)
    experience_points: int = 0
    _character_cached: Optional[CharacterStatBlock] = None

    # Records (apply_when, feature) in the order add_feature was called.
    # Unlike `features` (ordered for display - newest IMMEDIATE feature
    # first), this drives the order features are applied to the
    # CharacterStatBlock: all IMMEDIATE features first, then all LAST
    # features, each group preserving call order - so a later builder's
    # (e.g. a multiclass dip's) IMMEDIATE features never apply ahead of an
    # earlier builder's LAST features. A plain (non-underscore) field so
    # merge_with's generic list-concat combines it across builders/species
    # in the order they were merged in.
    feature_apply_order: list[tuple[ApplyWhen, Feature]] = attr.Factory(list)

    @property
    def character_level(self) -> int:
        return sum(self.level_per_class.values())

    def _invalidate_cache(self):
        """Drop the cached CharacterStatBlock; any mutation after
        setup_character_stat_block() must call this so the next setup call
        rebuilds instead of returning stale state."""
        self._character_cached = None

    def add_feature(
        self, feature: Feature, apply_when: ApplyWhen = ApplyWhen.IMMEDIATE
    ):
        self._invalidate_cache()
        if apply_when == ApplyWhen.IMMEDIATE:
            self.features.insert(0, feature)
        elif apply_when == ApplyWhen.LAST:
            self.features.append(feature)
        else:
            raise ValueError(f"Unknown ApplyWhen value: {apply_when}")
        self.feature_apply_order.append((apply_when, feature))

    def remove_features(self, should_remove) -> None:
        """Remove every feature for which `should_remove(feature)` is true,
        keeping `features` and `feature_apply_order` consistent."""
        self._invalidate_cache()
        self.features = [f for f in self.features if not should_remove(f)]
        self.feature_apply_order = [
            (when, f) for when, f in self.feature_apply_order if not should_remove(f)
        ]

    def add_origin_feat(self, origin_feat: OriginFeats.OriginFeat):
        self.add_feature(origin_feat)
        for spell in origin_feat.get_spells():
            self.add_spell(spell, origin_feat.get_spell_casting_ability())

    def get_features_by_type(self, feature_type: type) -> list[Any]:
        return [
            feature for feature in self.features if isinstance(feature, feature_type)
        ]

    def get_level_for_class(self, character_class: CharacterClass) -> int:
        return self.level_per_class.get(character_class, 0)

    def add_armor(self, armor: AbstractArmor):
        self._invalidate_cache()
        self.armors.append(armor)

    def add_weapon(self, weapon: AbstractWeapon):
        self._invalidate_cache()
        self.weapons.append(weapon)

    def add_weapon_mastery(self, weapon: AbstractWeapon):
        self._invalidate_cache()
        self.weapon_masteries.append(weapon)

    def add_armor_proficiency(self, armor_type: Definitions.ArmorType):
        self._invalidate_cache()
        self.armor_proficiencies.add(armor_type)

    def add_fighting_style(self, fighting_style: FightingStyle):
        self._invalidate_cache()
        self.fighting_styles.append(fighting_style)

    def add_spell(
        self,
        spell: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
    ):
        spell_casting_ability = self._resolve_spell_casting_ability(
            spell_casting_ability
        )

        if spell in [s[0] for s in self.spells]:
            raise ValueError(f"Spell {spell} already added.")
        self._invalidate_cache()
        self.spells.append((spell, spell_casting_ability, additional_ruling))

    def add_cantrip(
        self,
        cantrip: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
    ):
        spell_casting_ability = self._resolve_spell_casting_ability(
            spell_casting_ability
        )
        if cantrip in [s[0] for s in self.spells]:
            raise ValueError(f"Cantrip {cantrip} already added.")
        self._invalidate_cache()
        self.spells.append((cantrip, spell_casting_ability, additional_ruling))

    def replace_spells(self, replace_spells: dict[str, str]):
        for old_spell, new_spell in replace_spells.items():
            self.replace_spell(old_spell, new_spell)

    def replace_spell(
        self,
        old_spell: str,
        new_spell: str,
        new_spell_ability: Optional[Ability] = None,
        new_additional_ruling: Optional[str] = None,
    ):
        new_spells = []
        success = False
        for spell_name, spell_ability, additional_ruling in self.spells:
            if spell_name == old_spell:
                new_spells.append(
                    (
                        new_spell,
                        new_spell_ability or spell_ability,
                        (
                            new_additional_ruling
                            if new_additional_ruling is not None
                            else additional_ruling
                        ),
                    )
                )
                success = True
            else:
                new_spells.append((spell_name, spell_ability, additional_ruling))
        if not success:
            raise ValueError(f"Spell {old_spell} not found to replace.")
        self._invalidate_cache()
        self.spells = new_spells

    def add_invocation(self, invocation: str):
        self._invalidate_cache()
        self.invocations.append(invocation)

    def add_item(self, item: Items.Item, quantity: int = 1):
        self._invalidate_cache()
        for i, (existing_item, existing_quantity) in enumerate(self.items):
            if type(existing_item) is type(item):
                self.items[i] = (existing_item, existing_quantity + quantity)
                return
        self.items.append((item, quantity))

    def add_tool_proficiency(self, tool_proficiency: ToolProficiency):
        if tool_proficiency not in self.tool_proficiencies:
            self._invalidate_cache()
            self.tool_proficiencies.append(tool_proficiency)
        else:
            raise ValueError(f"Tool proficiency {tool_proficiency} already added.")

    def create_character_sheet(
        self, skill_config: Definitions.SkillConfig = Definitions.SkillConfig.DEFAULT
    ):
        if any(
            field is None
            for field in [
                self.character_name,
                self.character_subclass,
                self.abilities,
                self.skills,
                self.speed,
                self.size,
                self.base_class,
                self.saving_throws,
            ]
        ):
            raise ValueError(
                "All fields except weapon_masteries and fighting_styles must be set."
            )

        CharacterSheetWriters.HtmlCharacterSheetWriter().write_character_sheet(
            skill_config=skill_config,
            character=self.setup_character_stat_block(),
            output_path=self.get_file_path(),
            armors=self.armors,
            armor_proficiencies=self.armor_proficiencies,
            features=self.features,
            weapons=self.weapons,
            weapon_masteries=self.weapon_masteries,
            fighting_styles=self.fighting_styles,
            invocations=self.invocations,
            spells=self.spells,
            items=self.items,
            tool_proficiencies=self.tool_proficiencies,
            experience_points=self.experience_points,
        )

    def setup_character_stat_block(self) -> CharacterStatBlock:
        if self._character_cached is not None:
            return self._character_cached

        # Validate one-armor rule: at most one worn non-shield armor
        worn_body_armors = [
            armor for armor in self.armors if not armor.is_shield and armor.is_wearing
        ]
        if len(worn_body_armors) > 1:
            armor_names = ", ".join(armor.name for armor in worn_body_armors)
            raise ValueError(
                f"Character cannot wear multiple armors at once. "
                f"Conflicting armors: {armor_names}. "
                f"(Shields do not count toward this limit.)"
            )

        combat = CombatStatBlock(
            speed=self.speed,
            size=self.size,
        )
        character = CharacterStatBlock(
            name=self.character_name,
            character_subclass=self.character_subclass,
            base_class=self.base_class,
            level_per_class=self.level_per_class,
            abilities=self.abilities,
            skills=self.skills,
            combat=combat,
            saving_throws=self.saving_throws,
            spell_casting_ability=self.spell_casting_ability,
            spell_slots=self.spell_slots,
        )

        # Apply every IMMEDIATE feature (in call order) before any LAST
        # feature, regardless of which builder contributed it - so features
        # from a starter/multiclass builder never interleave out of order
        # (e.g. a later builder's expertise pick always applies after an
        # earlier builder's prerequisite skill proficiency, and no LAST
        # feature jumps ahead of an IMMEDIATE one from another builder).
        for apply_when in (ApplyWhen.IMMEDIATE, ApplyWhen.LAST):
            for when, feature in self.feature_apply_order:
                if when == apply_when:
                    feature.apply(character)

        for armor in self.armors:
            armor.apply(character)

        for weapon in self.weapons:
            weapon.apply(character)

        for item, _quantity in self.items:
            item.apply(character)

        for fighting_style in self.fighting_styles:
            if isinstance(fighting_style, FightStyleModifier):
                fighting_style.apply(character)
            elif isinstance(fighting_style, FightStyleWeaponFeature):
                fighting_style.apply(self.weapons)
        self._character_cached = character

        return character

    def get_ability_modifier(self, ability: Ability) -> int:
        character = self.setup_character_stat_block()
        return character.abilities.get_modifier(ability)

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        character = self.setup_character_stat_block()
        return character.calculate_attack_bonus_for_ability(ability)

    def get_file_path(self) -> str:
        return (
            f"Output/{self._slugify_name(self.character_name)}_"
            f"{self.character_subclass.lower()}_level_{self.character_level}_character_sheet.html"
        )

    def merge_with(self, other: "CharacterSheetData"):
        """Merge another CharacterSheetData into this one.

        Merge rules, by field kind:
        - lists (features, spells, weapons, feature_apply_order, ...) are
          concatenated, preserving each side's internal order with `other`'s
          entries after `self`'s;
        - dicts (level_per_class, spell_slots) are combined with `other`'s
          entries winning on key collisions. For level_per_class this means a
          later builder redeclaring an existing class states that class's
          final total level (e.g. a starter Paladin 1 resumed by a Paladin 19
          builder ends at 19, not 20);
        - sets (armor_proficiencies) are combined with set union;
        - scalars are overwritten only when `other`'s value is actually set
          (see _MERGE_EMPTY_VALUES), so an untouched default never erases an
          earlier builder's value.
        """
        self._invalidate_cache()

        for field_name in vars(self):
            if field_name.startswith("_"):
                continue
            other_value = getattr(other, field_name)
            my_value = getattr(self, field_name)

            if isinstance(my_value, list) and isinstance(other_value, list):
                setattr(self, field_name, my_value + other_value)
                continue

            if isinstance(my_value, dict) and isinstance(other_value, dict):
                combined_dict = my_value.copy()
                combined_dict.update(other_value)
                setattr(self, field_name, combined_dict)
                continue

            if isinstance(my_value, set) and isinstance(other_value, set):
                setattr(self, field_name, my_value.union(other_value))
                continue

            if other_value not in _MERGE_EMPTY_VALUES:
                setattr(self, field_name, other_value)

    def _resolve_spell_casting_ability(
        self, spell_casting_ability: Optional[Ability]
    ) -> Ability:
        if spell_casting_ability is not None:
            return spell_casting_ability
        if self.spell_casting_ability is None:
            raise ValueError(
                "Spell casting ability must be provided if not already set."
            )
        return self.spell_casting_ability

    @staticmethod
    def _slugify_name(name: str) -> str:
        """Convert a character name into the filename format used for output sheets."""
        name = name.lower().strip()
        allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
        cleaned = "".join(ch for ch in name if ch in allowed_chars)
        return cleaned.replace(" ", "_")
