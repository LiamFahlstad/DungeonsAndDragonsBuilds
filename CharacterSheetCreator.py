from typing import Any, Optional

import attr

import Definitions
from Definitions import Ability, ApplyWhen, CharacterClass
from Features import OriginFeats
from Features.Armor import AbstractArmor
from Features.BaseFeatures import Feature
from Features.FightingStyles import (
    FightingStyle,
    FightStyleCharacterFeature,
    FightStyleWeaponFeature,
)
from Features.Weapons import AbstractWeapon
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock
from Utils import CharaterSheetWriters


@attr.dataclass
class CharacterSheetData:
    character_name: Optional[str] = None
    character_subclass: Optional[str] = None
    starter_class: Optional[CharacterClass] = None
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
    _character_cached: Optional[CharacterStatBlock] = None

    @property
    def character_level(self) -> int:
        return sum(self.level_per_class.values())

    def add_feature(
        self, feature: Feature, apply_when: ApplyWhen = ApplyWhen.IMMEDIATE
    ):
        if apply_when == ApplyWhen.IMMEDIATE:
            self.features.insert(0, feature)
        elif apply_when == ApplyWhen.LAST:
            self.features.append(feature)
        else:
            raise ValueError(f"Unknown ApplyWhen value: {apply_when}")

    def add_origin_feat(self, origin_feat: OriginFeats.OriginFeat):
        self.add_feature(origin_feat)
        for spell in origin_feat.get_spells():
            self.add_spell(spell, origin_feat.get_spellcasting_ability())

    def get_features_by_type(self, feature_type: type) -> list[Any]:
        return [
            feature for feature in self.features if isinstance(feature, feature_type)
        ]

    def get_level_for_class(self, character_class: CharacterClass) -> int:
        return self.level_per_class.get(character_class, 0)

    def add_armor(self, armor: AbstractArmor):
        self.armors.append(armor)

    def add_weapon(self, weapon: AbstractWeapon):
        self.weapons.append(weapon)

    def add_weapon_mastery(self, weapon: AbstractWeapon):
        self.weapon_masteries.append(weapon)

    def add_armor_proficiency(self, armor_type: Definitions.ArmorType):
        self.armor_proficiencies.add(armor_type)

    def add_fighting_style(self, fighting_style: FightingStyle):
        self.fighting_styles.append(fighting_style)

    def add_spell(
        self,
        spell: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
    ):
        if spell_casting_ability is None:
            if self.spell_casting_ability is None:
                raise ValueError(
                    "Spell casting ability must be provided if not already set."
                )
            spell_casting_ability = self.spell_casting_ability

        if spell in [s[0] for s in self.spells]:
            raise ValueError(f"Spell {spell} already added.")
        self.spells.append((spell, spell_casting_ability, additional_ruling))

    def add_cantrip(
        self,
        cantrip: str,
        spell_casting_ability: Optional[Ability] = None,
        additional_ruling: Optional[str] = None,
    ):
        if spell_casting_ability is None:
            if self.spell_casting_ability is None:
                raise ValueError(
                    "Spell casting ability must be provided if not already set."
                )
            spell_casting_ability = self.spell_casting_ability
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
                new_spell_ability = (
                    new_spell_ability
                    if new_spell_ability is not None
                    else spell_ability
                )
                new_spells.append((new_spell, new_spell_ability, new_additional_ruling))
                success = True
            else:
                new_spells.append((spell_name, spell_ability, additional_ruling))
        if not success:
            raise ValueError(f"Spell {old_spell} not found to replace.")
        self.spells = new_spells

    def add_invocation(self, invocation: str):
        self.invocations.append(invocation)

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
                self.starter_class,
                self.saving_throws,
            ]
        ):
            raise ValueError(
                "All fields except weapon_masteries and fighting_styles must be set."
            )

        CharaterSheetWriters.HtmlCharacterSheetWriter().write_character_sheet(
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
        )

    def setup_character_stat_block(self) -> CharacterStatBlock:
        if self._character_cached is not None:
            return self._character_cached

        combat = CombatStatBlock(
            speed=self.speed,
            size=self.size,
        )
        character = CharacterStatBlock(
            name=self.character_name,
            character_subclass=self.character_subclass,
            starter_class=self.starter_class,
            level_per_class=self.level_per_class,
            abilities=self.abilities,
            skills=self.skills,
            combat=combat,
            saving_throws=self.saving_throws,
            spell_casting_ability=self.spell_casting_ability,
            spell_slots=self.spell_slots,
        )

        for feature in self.features:
            feature.modify(character)

        for armor in self.armors:
            armor.modify(character)

        for fighting_style in self.fighting_styles:
            if isinstance(fighting_style, FightStyleCharacterFeature):
                fighting_style.modify(character)
            elif isinstance(fighting_style, FightStyleWeaponFeature):
                fighting_style.modify(self.weapons)
        self._character_cached = character

        return character

    def get_ability_modifier(self, ability: Ability) -> int:
        character = self.setup_character_stat_block()
        return character.abilities.get_modifier(ability)

    def calculate_attack_bonus_for_ability(self, ability: Ability) -> int:
        character = self.setup_character_stat_block()
        return character.calculate_attack_bonus_for_ability(ability)

    def get_file_path(self) -> str:
        def slugify(name: str) -> str:
            """Convert a spell name into the URL-friendly format used by AideDD (no regex)."""
            # Lowercase and strip whitespace
            name = name.lower().strip()

            # Remove any non-alphanumeric characters except spaces and hyphens
            allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
            cleaned = "".join(ch for ch in name if ch in allowed_chars)

            # Replace spaces with hyphens
            return cleaned.replace(" ", "_")

        return f"Output/{slugify(self.character_name)}_{self.character_subclass.lower()}_level_{self.character_level}_character_sheet.html"

    def merge_with(self, other: "CharacterSheetData"):
        """Merge this CharacterSheetData with another, with the other taking precedence."""

        for attr in vars(self):
            other_value = getattr(other, attr)
            my_value = getattr(self, attr)

            if other_value not in (None, [], {}, ""):
                setattr(self, attr, other_value)

            if isinstance(my_value, list) and isinstance(other_value, list):
                combined_list = my_value + other_value
                setattr(self, attr, combined_list)

            if isinstance(my_value, dict) and isinstance(other_value, dict):
                combined_dict = my_value.copy()
                combined_dict.update(other_value)
                setattr(self, attr, combined_dict)

            if isinstance(my_value, set) and isinstance(other_value, set):
                combined_set = my_value.union(other_value)
                setattr(self, attr, combined_set)
