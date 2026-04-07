import pathlib
from abc import ABC, abstractmethod
from typing import Optional, TextIO

import Definitions
import Utils.TableUtils as TableUtils
from Definitions import Ability, Skill
from Features import Armor
from Features.BaseFeatures import CharacterFeature, Feature
from Features.FightingStyles import FightingStyle
from Features.Weapons import AbstractWeapon, write_weapons_to_file
from Invocations.InvocationFactory import InvocationFactory
from Items import Items
from Spells.SpellFactory import SpellFactory
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class CharacterSheetWriter(ABC):

    @abstractmethod
    def _write_general_info(self, character: CharacterStatBlock, file: TextIO):
        pass

    @abstractmethod
    def _write_combat_stats(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
    ):
        pass

    @abstractmethod
    def _write_abilities(self, character: CharacterStatBlock, file: TextIO):
        pass

    @abstractmethod
    def _write_skills(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        skill_config: Definitions.SkillConfig,
    ):
        pass

    @abstractmethod
    def _write_features(
        self, character: CharacterStatBlock, file: TextIO, features: list[Feature]
    ):
        pass

    @abstractmethod
    def _write_weapons(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
    ):
        pass

    @abstractmethod
    def _write_fighting_styles(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        fighting_styles: list[FightingStyle],
    ):
        pass

    @abstractmethod
    def _write_invocations(
        self, character: CharacterStatBlock, file: TextIO, invocations: list[str]
    ):
        pass

    @abstractmethod
    def _write_spell_slots(self, character: CharacterStatBlock, file: TextIO):
        pass

    @abstractmethod
    def _write_spells(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        spells: list[tuple[str, Ability, Optional[str]]],
    ):
        pass


class TextCharacterSheetWriter(CharacterSheetWriter):
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

    def _write_combat_stats(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
    ):
        TableUtils.write_separator(file, "Combat Stats")
        ac = character.calculate_armor_class()
        if Armor.ShieldArmor in [type(armor) for armor in armors]:
            ac = f"{ac} (with Shield) and {ac - 2} (without Shield)"
        TableUtils.write_table(
            headers=["Field", "Value"],
            rows=[
                ["Max Hit Points", character.calculate_hit_points()],
                ["Armor Class", ac],
                [
                    "Armor Proficiencies",
                    ", ".join(sorted([atype.value for atype in armor_proficiencies])),
                ],
                ["Initiative", f"d20 + {character.initiative}"],
                ["Speed (ft)", character.combat.speed],
                ["Size", character.combat.size.value],
            ],
            file=file,
        )
        file.write("\n")

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

    def _write_skills(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        skill_config: Definitions.SkillConfig,
    ):
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

    def _write_features(
        self, character: CharacterStatBlock, file: TextIO, features: list[Feature]
    ):
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

        if not all([isinstance(feat, CharacterFeature) for feat in features]):
            TableUtils.write_separator(file, "Features")
            sorted_features = sorted(features, key=sort_features)
            for feature in sorted_features:
                feature.write_to_file(character, file)
            file.write("\n")

    def _write_weapons(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
    ):
        if not weapons:
            return

        TableUtils.write_separator(file, "Weapons")
        for weapon in weapons:
            if weapon_masteries:
                for mastery in weapon_masteries:
                    if isinstance(weapon, type(mastery)):
                        weapon.player_has_mastery = True
        write_weapons_to_file(weapons, character, file)
        file.write("\n")

    def _write_fighting_styles(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        fighting_styles: list[FightingStyle],
    ):
        if not fighting_styles:
            return

        TableUtils.write_separator(file, "Fighting Styles")
        for fighting_style in fighting_styles:
            fighting_style.write_to_file(file)
        file.write("\n")

    def _write_invocations(
        self, character: CharacterStatBlock, file: TextIO, invocations: list[str]
    ):
        if not invocations:
            return

        TableUtils.write_separator(file, "Invocations")

        created_invocations = [
            InvocationFactory.create(invocation_name) for invocation_name in invocations
        ]
        sorted_invocations = sorted(
            created_invocations, key=lambda s: (s.level, s.name)
        )

        for invocation_index, invocation in enumerate(sorted_invocations):
            invocation.write_to_file(file)
            if invocation_index < len(sorted_invocations) - 1:
                file.write("-" * 40 + "\n")
        file.write("\n")

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

    def _write_spells(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        spells: list[tuple[str, Ability, Optional[str]]],
    ):
        if not spells:
            return

        TableUtils.write_separator(file, "Spells")

        created_spells = [
            SpellFactory.create(spell_name, spell_casting_ability, additional_ruling)
            for spell_name, spell_casting_ability, additional_ruling in spells
        ]
        sorted_spells = sorted(created_spells, key=lambda s: (s.level, s.name))

        for spell_index, spell in enumerate(sorted_spells):
            spell.write_to_file(file)
            if spell_index < len(created_spells) - 1:
                file.write("-" * 40 + "\n")
        file.write("\n")


class HtmlCharacterSheetWriter(CharacterSheetWriter):

    def _write_general_info(self, character: CharacterStatBlock, file: TextIO):
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

    def _write_combat_stats(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
    ):
        file.write("<h2>Combat Stats</h2>\n")

        ac = character.calculate_armor_class()
        if Armor.ShieldArmor in [type(armor) for armor in armors]:
            ac = f"{ac} (with Shield) and {ac - 2} (without Shield)"

        file.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
        file.write("<tr><th>Field</th><th>Value</th></tr>\n")

        initiative = f"d20 + {character.initiative}"
        if character.initiative_proficiency:
            initiative += f" ({character.abilities.get_modifier(Ability.DEXTERITY)} dex modifier + {character.get_proficiency_bonus()} Proficiency Bonus)"

        if character.initiative_roll_condition in (
            Definitions.DiceRollCondition.ADVANTAGE,
            Definitions.DiceRollCondition.DISADVANTAGE,
        ):
            initiative += f" ({character.initiative_roll_condition.value})"

        rows = [
            ("Max Hit Points", character.calculate_hit_points()),
            ("Armor Class", ac),
            (
                "Armor Proficiencies",
                ", ".join(sorted([atype.value for atype in armor_proficiencies])),
            ),
            ("Initiative", initiative),
            ("Speed (ft)", character.combat.speed),
            ("Size", character.combat.size.value),
        ]

        for field, value in rows:
            file.write(f"<tr><td>{field}</td><td>{value}</td></tr>\n")

        file.write("</table>\n<br>\n")

    def _write_abilities(self, character: CharacterStatBlock, file: TextIO):
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

    def _write_skills(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        skill_config: Definitions.SkillConfig,
    ):
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

        if skill_config == Definitions.SkillConfig.DEFAULT:
            for skill in Definitions.Skill.list_sorted():
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

        if skill_config == Definitions.SkillConfig.HOMEBREW:
            for skill in Definitions.HomeBrewSkill.list_sorted():
                possible_skills = Definitions.SkillConfig.map_homebrew_to_default(skill)
                skill_modifier = max(
                    character.get_skill_modifier(s) for s in possible_skills
                )
                proficient = any(
                    character.is_proficient_in_skill(s) for s in possible_skills
                )
                roll_conditions = set(
                    character.get_skill_roll_condition(s) for s in possible_skills
                )
                if Definitions.DiceRollCondition.ADVANTAGE in roll_conditions:
                    roll_condition = Definitions.DiceRollCondition.ADVANTAGE
                elif Definitions.DiceRollCondition.NEUTRAL in roll_conditions:
                    roll_condition = Definitions.DiceRollCondition.NEUTRAL
                else:
                    roll_condition = Definitions.DiceRollCondition.DISADVANTAGE
                skill_bonus = max(character.get_skill_bonus(s) for s in possible_skills)
                row = [
                    skill.value,
                    f"{skill_modifier:+}",
                    "Yes" if proficient else "No",
                    character.get_skill_ability(possible_skills[0]).value,
                    roll_condition.value,
                    f"{skill_bonus:+}",
                ]

                file.write("<tr>")
                for cell in row:
                    file.write(f"<td>{cell}</td>")
                file.write("</tr>\n")

        file.write("</table>\n<br>\n")

    def _write_features(
        self, character: CharacterStatBlock, file: TextIO, features: list[Feature]
    ):
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

        if not all([isinstance(feat, CharacterFeature) for feat in features]):
            file.write("<h2>Features</h2>\n")

            sorted_features = sorted(features, key=sort_features)

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

    def _write_weapons(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
    ):
        if not weapons:
            return

        for weapon in weapons:
            if weapon_masteries:
                for mastery in weapon_masteries:
                    if isinstance(weapon, type(mastery)):
                        weapon.player_has_mastery = True

        # file.write("<pre>\n")
        write_weapons_to_file(weapons, character, file, html=True)
        # file.write("</pre>\n<br>\n")

    def _write_fighting_styles(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        fighting_styles: list[FightingStyle],
    ):
        if not fighting_styles:
            return

        file.write("<h2>Fighting Styles</h2>\n")

        for style in fighting_styles:
            # file.write("<pre>\n")
            style.write_to_file(file)
            # file.write("</pre>\n")

        file.write("<br>\n")

    def _write_invocations(
        self, character: CharacterStatBlock, file: TextIO, invocations: list[str]
    ):
        if not invocations:
            return

        file.write("<h2>Invocations</h2>\n")

        created_invocations = [
            InvocationFactory.create(invocation_name) for invocation_name in invocations
        ]
        sorted_invocations = sorted(
            created_invocations, key=lambda s: (s.level, s.name)
        )

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

    def _write_spells(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        spells: list[tuple[str, Ability, Optional[str]]],
    ):
        if not spells:
            return

        file.write("<h2>Spells</h2>\n")

        created_spells = [
            SpellFactory.create(spell_name, spell_casting_ability, additional_ruling)
            for spell_name, spell_casting_ability, additional_ruling in spells
        ]
        sorted_spells = sorted(created_spells, key=lambda s: (s.level, s.name))

        for i, spell in enumerate(sorted_spells):
            spell.write_to_file(file, html=True)

            if i < len(sorted_spells) - 1:
                file.write("<hr>\n")

        file.write("<br>\n")

    def _write_items(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        armors: list[Armor.AbstractArmor],
        weapons: list[AbstractWeapon],
        items: list[tuple[Items.Item, int]],
    ):
        if not items and not armors and not weapons:
            return

        file.write("<h2>Items</h2>\n")

        # Reuse spell table styling
        file.write(
            """
        <style>
        .item-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0.25rem 0;
        }

        .item-table td, .item-table th {
            border: 1px solid #ddd;
            padding: 3px 5px;
            vertical-align: top;
        }

        .item-title {
            font-size: 1rem;
            text-align: left;
            background: #f5f5f5;
            font-weight: 600;
        }

        .item-label {
            font-weight: 600;
            white-space: nowrap;
            background: #fafafa;
            width: 1%;
        }

        .item-value {
            width: auto;
        }
        </style>
        """
        )

        def start_table(title: str):
            file.write("<table class='item-table'>\n")
            file.write(
                f"""
            <tr>
                <th class='item-title' colspan='2'>{title}</th>
            </tr>
            """
            )

        def end_table():
            file.write("</table>\n")

        def row(label, value):
            file.write("<tr>")
            file.write(f"<td class='item-label'>{label}</td>")
            file.write(f"<td class='item-value'>{value}</td>")
            file.write("</tr>\n")

        # --- Armors ---
        if armors:
            start_table("Weapons")
            for armor in armors:
                description = armor.description if armor.description else "-"
                row(armor.name, description)
            end_table()

        # --- Weapons ---
        file.write("<hr>")
        if weapons:
            start_table("Armors")
            for weapon in weapons:
                description = weapon.description if weapon.description else "-"
                row(weapon.name, description)
            end_table()

        # --- Other Items ---
        file.write("<hr>")
        if items:
            sorted_items = sorted(items, key=lambda x: x[0].name)

            start_table("Other items")
            for item, quantity in sorted_items:
                row(f"{item.name} ({quantity})", item.description())
            end_table()

        file.write("<br>\n")

    def _get_css_style(self) -> str:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

        :root {
            --text-color: #222;
            --muted-color: #555;
            --border-color: #ddd;
        }

        html {
            font-size: 14px; /* ↓ smaller base size */
        }

        body {
            font-family: "EB Garamond", Garamond, "Times New Roman", serif;
            line-height: 1.5;
            color: var(--text-color);
            margin: 0;
            padding: 1.5rem;
        }

        div {
            max-width: 700px;
            margin: 0 auto;
            padding: 0 0.5rem;
        }

        p {
            margin: 0.5em 0;
        }

        /* Pre blocks - lighter + tighter */
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: inherit;
            background: #fafafa;
            padding: 0.5rem;
            border: 1px solid var(--border-color);
            border-radius: 3px;
            font-size: 0.9rem;
        }

        ul, ol {
            margin: 0.5em 0 0.5em 1.2em;
        }

        /* Print tweaks (LESS aggressive) */
        @media print {
            body {
                padding: 0;
                font-size: 10pt; /* ↓ smaller print size */
            }

            div {
                max-width: 100%;
            }

            /* Only avoid breaking headings from next line */
            h1, h2, h3 {
                page-break-after: avoid;
            }

            /* Allow content to flow naturally */
            p, pre, ul, ol {
                page-break-inside: auto;
            }

            /* Remove forced page breaks entirely */
            .page-break {
                display: none;
            }
        }
        </style>
        """

    def write_character_sheet(
        self,
        skill_config: Definitions.SkillConfig,
        character: CharacterStatBlock,
        output_path: str,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        features: list[Feature],
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        fighting_styles: list[FightingStyle],
        invocations: list[str],
        spells: list[tuple[str, Ability, Optional[str]]],
        items: list[tuple[Items.Item, int]],  # (item_name, quantity)
    ):
        output_path_obj = pathlib.Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path_obj.with_suffix(".html"), "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            file.write(
                f"<h1>{character.name} - Level {character.character_level} {character.starter_class.value}</h1>\n"
            )
            self._write_general_info(character, file)
            self._write_combat_stats(character, file, armors, armor_proficiencies)
            self._write_abilities(character, file)
            self._write_skills(character, file, skill_config)
            self._write_features(character, file, features)
            self._write_weapons(character, file, weapons, weapon_masteries)
            self._write_fighting_styles(character, file, fighting_styles)
            self._write_invocations(character, file, invocations)
            self._write_spell_slots(character, file)
            self._write_spells(character, file, spells)
            self._write_items(character, file, armors, weapons, items)
