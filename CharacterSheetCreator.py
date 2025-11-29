from enum import Enum
import pathlib
from typing import Optional
from CharacterStatBlock import CharacterStatBlock
from Definitions import Ability, Skill, CharacterClass
import Definitions
import Scrapers.InvocationScrapers as InvocationScrapers
import Scrapers.SpellScraper as SpellScraper
from Features.Weapons import AbstractWeapon, WeaponMastery, write_weapons_to_file
from StatBlocks.CombatStatBlock import CombatStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
import Utils
from Features.FightingStyles import (
    FightingStyle,
    FightStyleCharacterFeature,
    FightStyleWeaponFeature,
)
from Features.BaseFeatures import Feature, CharacterFeature
import attr
from Features.Armor import AbstractArmor


@attr.dataclass
class CharacterSheetData:
    character_name: Optional[str] = None
    character_class: Optional[CharacterClass] = None
    character_subclass: Optional[str] = None
    level: Optional[int] = None
    abilities: Optional[AbilitiesStatBlock] = None
    skills: Optional[SkillsStatBlock] = None
    hit_die: Optional[int] = None
    speed: Optional[int] = None
    size: Optional[Definitions.CreatureSize] = None
    saving_throws: Optional[SavingThrowsStatBlock] = None
    features: list[Feature] = []
    invocations: list[str] = []
    spells: list[str] = []
    spell_casting_ability: Optional[Ability] = None
    spell_slots: dict[int, int] = attr.Factory(dict)
    armors: list[AbstractArmor] = []
    weapons: list[AbstractWeapon] = []
    weapon_mastery_choices: list[type[AbstractWeapon]] = []
    fighting_styles: list[FightingStyle] = []

    def add_feature(self, feature: Feature):
        self.features.append(feature)

    def add_armor(self, armor: AbstractArmor):
        self.armors.append(armor)

    def add_weapon(self, weapon: AbstractWeapon):
        self.weapons.append(weapon)

    def add_weapon_mastery(self, weapon_type: type[AbstractWeapon]):
        if not weapon_type:
            raise ValueError("weapon_type cannot be None.")
        self.weapon_mastery_choices.append(weapon_type)

    def add_fighting_style(self, fighting_style: FightingStyle):
        self.fighting_styles.append(fighting_style)

    def add_spell(self, spell: str):
        self.spells.append(spell)

    def add_invocation(self, invocation: str):
        self.invocations.append(invocation)

    def create_character_sheet(self):
        if any(
            field is None
            for field in [
                self.character_name,
                self.character_class,
                self.character_subclass,
                self.level,
                self.abilities,
                self.skills,
                self.hit_die,
                self.speed,
                self.size,
                self.saving_throws,
            ]
        ):
            raise ValueError(
                "All fields except weapon_mastery_choices and fighting_style must be set."
            )
        self._create_character_sheet()

    def _create_character_sheet(self):
        combat = CombatStatBlock(
            hit_die=self.hit_die,  # Paladin hit die is d10
            speed=self.speed,
            size=self.size,
        )
        character = CharacterStatBlock(
            name=self.character_name,
            character_class=self.character_class,
            character_subclass=self.character_subclass,
            level=self.level,
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

        output_path = f"Output/{slugify(self.character_name)}_{self.character_class.value.lower()}_level_{self.level}_character_sheet.txt"

        pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as file:
            character.save_character_to_file(file)

            if not all([isinstance(feat, CharacterFeature) for feat in self.features]):
                file.write("\n")
                Utils.write_separator(file, "Features")
                for feature in self.features:
                    feature.write_to_file(character, file)

            file.write("\n")

            Utils.write_separator(file, "Weapons")
            for weapon in self.weapons:
                if self.weapon_mastery_choices:
                    for mastery in self.weapon_mastery_choices:
                        if isinstance(weapon, mastery):
                            weapon.player_has_mastery = True
            write_weapons_to_file(self.weapons, character, file)

            if self.fighting_styles:
                file.write("\n")
                Utils.write_separator(file, "Fighting Styles")
                for fighting_style in self.fighting_styles:
                    fighting_style.write_to_file(file)

            if self.invocations:
                file.write("\n")
                Utils.write_separator(file, "Invocations")
                for invocation_index, invocation_name in enumerate(self.invocations):
                    invocation = InvocationScrapers.InvocationParser(invocation_name)
                    invocation.fetch()
                    invocation.write_to_file(file)
                    if invocation_index < len(self.invocations) - 1:
                        file.write("-" * 40 + "\n")

            if self.spells:
                file.write("\n")
                Utils.write_separator(file, "Spell Modifiers")
                character_spell_save_dc = character.calculate_spell_save_dc()
                character_spell_attack_bonus = character.calculate_spell_attack_bonus()
                file.write(f"Spell Save DC: {character_spell_save_dc}\n")
                file.write(f"Spell Attack Bonus: +{character_spell_attack_bonus}\n")

                file.write("\n")
                Utils.write_separator(file, "Spell Slots")
                character_spell_slots = character.get_spell_slots()
                for level, slots in character_spell_slots.items():
                    file.write(f"Level {level} Spell Slots: {slots}\n")

                file.write("\n")
                Utils.write_separator(file, "Spells")
                for spell_index, spell_name in enumerate(self.spells):
                    spell = SpellScraper.SpellParser(spell_name)
                    spell.fetch()
                    spell.write_to_file(file)
                    if spell_index < len(self.spells) - 1:
                        file.write("-" * 40 + "\n")


def slugify(name: str) -> str:
    """Convert a spell name into the URL-friendly format used by AideDD (no regex)."""
    # Lowercase and strip whitespace
    name = name.lower().strip()

    # Remove any non-alphanumeric characters except spaces and hyphens
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
    cleaned = "".join(ch for ch in name if ch in allowed_chars)

    # Replace spaces with hyphens
    return cleaned.replace(" ", "_")
