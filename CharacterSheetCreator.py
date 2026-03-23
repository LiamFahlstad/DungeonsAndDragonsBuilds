import pathlib
from typing import Any, Optional, TextIO

import attr

import Definitions
import Utils.TableUtils as TableUtils
from Definitions import Ability, ApplyWhen, CharacterClass, Skill
from Features import Armor, OriginFeats
from Features.Armor import AbstractArmor
from Features.BaseFeatures import CharacterFeature, Feature
from Features.FightingStyles import (
    FightingStyle,
    FightStyleCharacterFeature,
    FightStyleWeaponFeature,
)
from Features.Weapons import AbstractWeapon, write_weapons_to_file
from Invocations.InvocationFactory import InvocationFactory
from Spells.SpellFactory import SpellFactory
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock


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
        for spell_name, spell_ability, _ in self.spells:

            if spell_name == old_spell:
                new_spell_ability = (
                    new_spell_ability
                    if new_spell_ability is not None
                    else spell_ability
                )
                new_spells.append((new_spell, new_spell_ability, new_additional_ruling))
                success = True
            else:
                new_spells.append((spell_name, spell_ability, new_additional_ruling))
        if not success:
            raise ValueError(f"Spell {old_spell} not found to replace.")
        self.spells = new_spells

    def add_invocation(self, invocation: str):
        self.invocations.append(invocation)

    def create_character_sheet(self):
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
        self._create_character_sheet()

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
        return f"Output/{slugify(self.character_name)}_{self.character_subclass.lower()}_level_{self.character_level}_character_sheet.html"

    def _write_general_info(self, character: CharacterStatBlock, file: TextIO):
        TableUtils.write_separator(file, "General Info")
        TableUtils.write_table(
            headers=["Field", "Value"],
            rows=[
                ["Name", character.name],
                ["Level", character.character_level],
                ["Starter Class", character.starter_class.value],
                [
                    "Level per Class",
                    ", ".join(
                        f"{cls.value}: {lvl}"
                        for cls, lvl in character.level_per_class.items()
                        if lvl > 0
                    ),
                ],
                ["Character Subclass", character.character_subclass],
                ["Proficiency Bonus", character.get_proficiency_bonus()],
            ],
            file=file,
        )
        file.write("\n")

    def _write_general_info_html(self, character: CharacterStatBlock, file: TextIO):
        file.write("<h2>General Info</h2>\n")

        file.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
        file.write("<tr><th>Field</th><th>Value</th></tr>\n")

        rows = [
            ("Name", character.name),
            ("Level", character.character_level),
            ("Starter Class", character.starter_class.value),
            (
                "Level per Class",
                ", ".join(
                    f"{cls.value}: {lvl}"
                    for cls, lvl in character.level_per_class.items()
                    if lvl > 0
                ),
            ),
            ("Character Subclass", character.character_subclass),
            ("Proficiency Bonus", character.get_proficiency_bonus()),
        ]

        for field, value in rows:
            file.write(f"<tr><td>{field}</td><td>{value}</td></tr>\n")

        file.write("</table>\n<br>\n")

    def _write_combat_stats(self, character: CharacterStatBlock, file: TextIO):
        TableUtils.write_separator(file, "Combat Stats")
        ac = character.calculate_armor_class()
        if Armor.ShieldArmor in [type(armor) for armor in self.armors]:
            ac = f"{ac} (with Shield) and {ac - 2} (without Shield)"
        TableUtils.write_table(
            headers=["Field", "Value"],
            rows=[
                ["Max Hit Points", character.calculate_hit_points()],
                ["Armor Class", ac],
                [
                    "Armor Proficiencies",
                    ", ".join(
                        sorted([atype.value for atype in self.armor_proficiencies])
                    ),
                ],
                ["Initiative", f"d20 + {character.initiative}"],
                ["Speed (ft)", character.combat.speed],
                ["Size", character.combat.size.value],
            ],
            file=file,
        )
        file.write("\n")

    def _write_combat_stats_html(self, character: CharacterStatBlock, file: TextIO):
        file.write("<h2>Combat Stats</h2>\n")

        ac = character.calculate_armor_class()
        if Armor.ShieldArmor in [type(armor) for armor in self.armors]:
            ac = f"{ac} (with Shield) and {ac - 2} (without Shield)"

        file.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
        file.write("<tr><th>Field</th><th>Value</th></tr>\n")

        rows = [
            ("Max Hit Points", character.calculate_hit_points()),
            ("Armor Class", ac),
            (
                "Armor Proficiencies",
                ", ".join(sorted([atype.value for atype in self.armor_proficiencies])),
            ),
            ("Initiative", f"d20 + {character.initiative}"),
            ("Speed (ft)", character.combat.speed),
            ("Size", character.combat.size.value),
        ]

        for field, value in rows:
            file.write(f"<tr><td>{field}</td><td>{value}</td></tr>\n")

        file.write("</table>\n<br>\n")

    def _write_abilities(self, character: CharacterStatBlock, file: TextIO):
        TableUtils.write_separator(file, "Abilities")
        headers = [
            "Ability",
            "Score",
            "Mod",
            "Saving Throw",
            "DC",
            "ATK Bonus",
        ]
        rows = []
        proficiency_bonus = character.get_proficiency_bonus()
        for ability in Ability:
            ability_mod = character.get_ability_modifier(ability)
            saving_throw_text = f"{ability_mod:+}"
            if character.is_proficient_in_saving_throw(ability):
                saving_throw_text += f" + {proficiency_bonus} (Proficient)"
            if character.has_advantage_in_saving_throw(ability):
                saving_throw_text += " (Advantage)"

            ability_dc = character.calculate_difficulty_class_for_ability(ability)
            ability_attack_bonus = character.calculate_attack_bonus_for_ability(ability)

            row = [
                ability.short_name,
                character.get_ability_score(ability),
                f"{ability_mod:+}",
                saving_throw_text,
                f"{ability_dc}",
                f"{ability_attack_bonus:+}",
            ]
            rows.append(row)
        TableUtils.write_table(
            headers,
            rows,
            file,
        )
        file.write("\n")

    def _write_abilities_html(self, character: CharacterStatBlock, file: TextIO):
        file.write("<h2>Abilities</h2>\n")

        headers = [
            "Ability",
            "Score",
            "Mod",
            "Saving Throw",
            "DC",
            "ATK Bonus",
        ]

        file.write("<table border='1' cellspacing='0' cellpadding='5'>\n")

        # Header row
        file.write("<tr>")
        for header in headers:
            file.write(f"<th>{header}</th>")
        file.write("</tr>\n")

        proficiency_bonus = character.get_proficiency_bonus()

        for ability in Ability:
            ability_mod = character.get_ability_modifier(ability)

            saving_throw_text = f"{ability_mod:+}"
            if character.is_proficient_in_saving_throw(ability):
                saving_throw_text += f" + {proficiency_bonus} (Proficient)"
            if character.has_advantage_in_saving_throw(ability):
                saving_throw_text += " (Advantage)"

            ability_dc = character.calculate_difficulty_class_for_ability(ability)
            ability_attack_bonus = character.calculate_attack_bonus_for_ability(ability)

            row = [
                ability.short_name,
                character.get_ability_score(ability),
                f"{ability_mod:+}",
                saving_throw_text,
                f"{ability_dc}",
                f"{ability_attack_bonus:+}",
            ]

            file.write("<tr>")
            for cell in row:
                file.write(f"<td>{cell}</td>")
            file.write("</tr>\n")

        file.write("</table>\n<br>\n")

    def _write_skills(self, character: CharacterStatBlock, file: TextIO):
        TableUtils.write_separator(file, "Skills")
        headers = [
            "Skill",
            "Modifier",
            "Proficient",
            "Ability",
            "Roll Condition",
            "Bonus (already included)",
        ]
        TableUtils.write_table(
            headers,
            [
                [
                    skill.value,
                    f"{character.get_skill_modifier(skill):+}",
                    "Yes" if character.is_proficient_in_skill(skill) else "No",
                    character.get_skill_ability(skill).value,
                    character.get_skill_roll_condition(skill).value,
                    f"{character.get_skill_bonus(skill):+}",
                ]
                for skill in Skill
            ],
            file,
        )
        file.write("\n")

    def _write_skills_html(self, character: CharacterStatBlock, file: TextIO):
        file.write("<h2>Skills</h2>\n")

        headers = [
            "Skill",
            "Modifier",
            "Proficient",
            "Ability",
            "Roll Condition",
            "Bonus (already included)",
        ]

        file.write("<table border='1' cellspacing='0' cellpadding='5'>\n")

        # Header row
        file.write("<tr>")
        for header in headers:
            file.write(f"<th>{header}</th>")
        file.write("</tr>\n")

        for skill in Skill:
            row = [
                skill.value,
                f"{character.get_skill_modifier(skill):+}",
                "Yes" if character.is_proficient_in_skill(skill) else "No",
                character.get_skill_ability(skill).value,
                character.get_skill_roll_condition(skill).value,
                f"{character.get_skill_bonus(skill):+}",
            ]

            file.write("<tr>")
            for cell in row:
                file.write(f"<td>{cell}</td>")
            file.write("</tr>\n")

        file.write("</table>\n<br>\n")

    def _write_features(self, character: CharacterStatBlock, file: TextIO):
        def sort_features(feat: Feature):
            if isinstance(feat, CharacterFeature):
                return (0, 0, feat.__class__.__name__)
            if "Level " in feat.origin:
                parts = feat.origin.split("Level ")
                try:
                    level_num = int(parts[1])
                except ValueError:
                    level_num = 0
                return (2, level_num, feat.name)
            return (1, 0, feat.name)

        if not all([isinstance(feat, CharacterFeature) for feat in self.features]):
            TableUtils.write_separator(file, "Features")
            sorted_features = sorted(self.features, key=sort_features)
            for feature in sorted_features:
                feature.write_to_file(character, file)
            file.write("\n")

    def _write_features_html(self, character: CharacterStatBlock, file: TextIO):
        def sort_features(feat: Feature):
            if isinstance(feat, CharacterFeature):
                return (0, 0, feat.__class__.__name__)
            if "Level " in feat.origin:
                parts = feat.origin.split("Level ")
                try:
                    level_num = int(parts[1])
                except ValueError:
                    level_num = 0
                return (2, level_num, feat.name)
            return (1, 0, feat.name)

        if not all([isinstance(feat, CharacterFeature) for feat in self.features]):
            file.write("<h2>Features</h2>\n")

            sorted_features = sorted(self.features, key=sort_features)

            file.write("<div>\n")
            for i, feature in enumerate(sorted_features):
                try:
                    # file.write("<pre>\n")  # preserves existing formatting
                    feature.write_to_file(character, file, html=True)
                    # file.write("</pre>\n")
                    if i < len(sorted_features) - 1:
                        file.write("<hr>\n")
                except NotImplementedError as e:
                    continue

            file.write("</div>\n<br>\n")

    def _write_weapons(self, character: CharacterStatBlock, file: TextIO):
        if not self.weapons:
            return

        TableUtils.write_separator(file, "Weapons")
        for weapon in self.weapons:
            if self.weapon_masteries:
                for mastery in self.weapon_masteries:
                    if isinstance(weapon, type(mastery)):
                        weapon.player_has_mastery = True
        write_weapons_to_file(self.weapons, character, file)
        file.write("\n")

    def _write_weapons_html(self, character: CharacterStatBlock, file: TextIO):
        if not self.weapons:
            return

        file.write("<h2>Weapons</h2>\n")

        for weapon in self.weapons:
            if self.weapon_masteries:
                for mastery in self.weapon_masteries:
                    if isinstance(weapon, type(mastery)):
                        weapon.player_has_mastery = True

        file.write("<pre>\n")
        write_weapons_to_file(self.weapons, character, file)
        file.write("</pre>\n<br>\n")

    def _write_fighting_styles(self, character: CharacterStatBlock, file: TextIO):
        if not self.fighting_styles:
            return

        TableUtils.write_separator(file, "Fighting Styles")
        for fighting_style in self.fighting_styles:
            fighting_style.write_to_file(file)
        file.write("\n")

    def _write_fighting_styles_html(self, character: CharacterStatBlock, file: TextIO):
        if not self.fighting_styles:
            return

        file.write("<h2>Fighting Styles</h2>\n")

        for style in self.fighting_styles:
            file.write("<pre>\n")
            style.write_to_file(file)
            file.write("</pre>\n")

        file.write("<br>\n")

    def _write_invocations(self, character: CharacterStatBlock, file: TextIO):
        if not self.invocations:
            return

        TableUtils.write_separator(file, "Invocations")

        invocations = [
            InvocationFactory.create(invocation_name)
            for invocation_name in self.invocations
        ]
        sorted_invocations = sorted(invocations, key=lambda s: (s.level, s.name))

        for invocation_index, invocation in enumerate(sorted_invocations):
            invocation.write_to_file(file)
            if invocation_index < len(self.invocations) - 1:
                file.write("-" * 40 + "\n")
        file.write("\n")

    def _write_invocations_html(self, character: CharacterStatBlock, file: TextIO):
        if not self.invocations:
            return

        file.write("<h2>Invocations</h2>\n")

        invocations = [
            InvocationFactory.create(invocation_name)
            for invocation_name in self.invocations
        ]
        sorted_invocations = sorted(invocations, key=lambda s: (s.level, s.name))

        for i, invocation in enumerate(sorted_invocations):
            file.write("<pre>\n")
            invocation.write_to_file(file)
            file.write("</pre>\n")

            if i < len(sorted_invocations) - 1:
                file.write("<hr>\n")  # replaces -----

        file.write("<br>\n")

    def _write_spell_slots(self, character: CharacterStatBlock, file: TextIO):
        if not character.spell_slots:
            return

        TableUtils.write_separator(file, "Spell Slots")
        character_spell_slots = character.get_spell_slots()
        headers = []
        row = []
        for level, slots in character_spell_slots.items():
            headers.append(f"Level {level}")
            row.append(slots)
        TableUtils.write_table(headers, [row], file)
        file.write("\n")

    def _write_spell_slots_html(self, character: CharacterStatBlock, file: TextIO):
        if not character.spell_slots:
            return

        file.write("<h2>Spell Slots</h2>\n")

        character_spell_slots = character.get_spell_slots()

        file.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
        file.write("<tr>")

        for level in character_spell_slots.keys():
            file.write(f"<th>Level {level}</th>")

        file.write("</tr>\n<tr>")

        for slots in character_spell_slots.values():
            file.write(f"<td>{slots}</td>")

        file.write("</tr>\n</table>\n<br>\n")

    def _write_spells(self, character: CharacterStatBlock, file: TextIO):
        if not self.spells:
            return

        TableUtils.write_separator(file, "Spells")

        spells = [
            SpellFactory.create(spell_name, spell_casting_ability, additional_ruling)
            for spell_name, spell_casting_ability, additional_ruling in self.spells
        ]
        sorted_spells = sorted(spells, key=lambda s: (s.level, s.name))

        for spell_index, spell in enumerate(sorted_spells):
            spell.write_to_file(file)
            if spell_index < len(self.spells) - 1:
                file.write("-" * 40 + "\n")
        file.write("\n")

    def _write_spells_html(self, character: CharacterStatBlock, file: TextIO):
        if not self.spells:
            return

        file.write("<h2>Spells</h2>\n")

        spells = [
            SpellFactory.create(spell_name, spell_casting_ability, additional_ruling)
            for spell_name, spell_casting_ability, additional_ruling in self.spells
        ]
        sorted_spells = sorted(spells, key=lambda s: (s.level, s.name))

        for i, spell in enumerate(sorted_spells):
            file.write("<pre>\n")
            spell.write_to_file(file, html=True)
            file.write("</pre>\n")

            if i < len(sorted_spells) - 1:
                file.write("<hr>\n")

        file.write("<br>\n")

    def _create_character_sheet(self):
        character = self.setup_character_stat_block()
        output_path = self.get_file_path()

        pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as file:
            if output_path.endswith(".html"):
                self._write_general_info_html(character, file)
                self._write_combat_stats_html(character, file)
                self._write_abilities_html(character, file)
                self._write_skills_html(character, file)
                self._write_features_html(character, file)
                self._write_weapons_html(character, file)
                self._write_fighting_styles_html(character, file)
                self._write_invocations_html(character, file)
                self._write_spell_slots_html(character, file)
                self._write_spells_html(character, file)
            elif output_path.endswith(".txt"):
                self._write_general_info(character, file)
                self._write_combat_stats(character, file)
                self._write_abilities(character, file)
                self._write_skills(character, file)
                self._write_features(character, file)
                self._write_weapons(character, file)
                self._write_fighting_styles(character, file)
                self._write_invocations(character, file)
                self._write_spell_slots(character, file)
                self._write_spells(character, file)
            else:
                raise ValueError("Output file must end with .txt or .html")

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


def slugify(name: str) -> str:
    """Convert a spell name into the URL-friendly format used by AideDD (no regex)."""
    # Lowercase and strip whitespace
    name = name.lower().strip()

    # Remove any non-alphanumeric characters except spaces and hyphens
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
    cleaned = "".join(ch for ch in name if ch in allowed_chars)

    # Replace spaces with hyphens
    return cleaned.replace(" ", "_")
