import pathlib
from typing import Optional, TextIO

import Definitions
from Definitions import Ability
from Features import Armor
from Features.BaseFeatures import CharacterFeature, Feature
from Features.FightingStyles import FightingStyle
from Features.Weapons import AbstractWeapon, write_weapons_to_file
from Invocations.InvocationFactory import InvocationFactory
from Items import Items
from Spells.SpellFactory import SpellFactory
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from ToolProficiencies.ToolProficiencies import ToolProficiency


class HtmlCharacterSheetWriter:
    @staticmethod
    def _has_shield_armor(armors: list[Armor.AbstractArmor]) -> bool:
        return any(type(armor) is Armor.ShieldArmor for armor in armors)

    @staticmethod
    def _sort_features_key(feat: Feature):
        feat_name = getattr(feat, "name", feat.__class__.__name__)
        feat_origin = getattr(feat, "origin", "")
        if "Level " in feat_origin:
            parts = feat_origin.split("Level ")
            try:
                level_num = int(parts[1])
            except ValueError:
                level_num = 0
            return (1, level_num, feat_name)
        return (0, 0, feat_name)

    @staticmethod
    def _apply_weapon_masteries(
        weapons: list[AbstractWeapon], weapon_masteries: list[AbstractWeapon]
    ):
        if not weapon_masteries:
            return

        mastery_types = {type(mastery) for mastery in weapon_masteries}
        for weapon in weapons:
            if type(weapon) in mastery_types:
                weapon.player_has_mastery = True

    @staticmethod
    def _write_table_row(file: TextIO, cells: list):
        file.write("<tr>")
        for cell in cells:
            file.write(f"<td>{cell}</td>")
        file.write("</tr>\n")

    @staticmethod
    def _description_or_dash(description: str | None) -> str:
        return description if description else "-"

    @staticmethod
    def _resolve_homebrew_roll_condition(
        roll_conditions: set,
    ) -> "Definitions.DiceRollCondition":
        if Definitions.DiceRollCondition.ADVANTAGE in roll_conditions:
            return Definitions.DiceRollCondition.ADVANTAGE
        if Definitions.DiceRollCondition.NEUTRAL in roll_conditions:
            return Definitions.DiceRollCondition.NEUTRAL
        return Definitions.DiceRollCondition.DISADVANTAGE

    @staticmethod
    def _write_separated(items: list, write_fn, file: TextIO):
        for i, item in enumerate(items):
            write_fn(item, file)
            if i < len(items) - 1:
                file.write("<hr>\n")

    @staticmethod
    def _write_item_table(file: TextIO, title: str, rows: list[tuple[str, str]]):
        file.write("<table class='item-table'>\n")
        file.write("<tr>\n")
        file.write(f"<th class='item-title' colspan='2'>{title}</th>\n")
        file.write("</tr>\n")

        for label, value in rows:
            file.write("<tr>")
            file.write(f"<td class='item-label'>{label}</td>")
            file.write(f"<td class='item-value'>{value}</td>")
            file.write("</tr>\n")

        file.write("</table>\n")

    def _write_general_info(self, character: CharacterStatBlock, file: TextIO):
        file.write("<h2>General Info</h2>\n")

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

        file.write("<table class='stat-table'>\n<tr>")
        for field, _ in rows:
            file.write(f"<th>{field}</th>")
        file.write("</tr>\n<tr>")
        for _, value in rows:
            file.write(f"<td>{value}</td>")
        file.write("</tr>\n</table>\n<br>\n")

    def _write_combat_stats(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
    ):
        file.write("<h2>Combat Stats</h2>\n")

        ac = character.calculate_armor_class()
        if self._has_shield_armor(armors):
            ac = f"{ac} (with Shield) and {ac - 2} (without Shield)"

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
                ", ".join(sorted([a.value for a in armor_proficiencies])),
            ),
            ("Initiative", initiative),
            ("Speed (ft)", character.combat.speed),
            ("Size", character.combat.size.value),
        ]

        file.write("<table class='stat-table'>\n<tr>")
        for field, _ in rows:
            file.write(f"<th>{field}</th>")
        file.write("</tr>\n<tr>")
        for _, value in rows:
            file.write(f"<td>{value}</td>")
        file.write("</tr>\n</table>\n<br>\n")

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

        file.write("<table class='stat-table'>\n")

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

            self._write_table_row(file, row)

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

        file.write("<table class='stat-table'>\n")

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
                self._write_table_row(file, row)

        if skill_config == Definitions.SkillConfig.HOMEBREW:
            for skill in Definitions.HomeBrewSkill.list_sorted():
                possible_skills = Definitions.SkillConfig.map_homebrew_to_default(skill)
                roll_conditions = set(
                    character.get_skill_roll_condition(s) for s in possible_skills
                )
                row = [
                    skill.value,
                    f"{max(character.get_skill_modifier(s) for s in possible_skills):+}",
                    (
                        "Yes"
                        if any(
                            character.is_proficient_in_skill(s) for s in possible_skills
                        )
                        else "No"
                    ),
                    character.get_skill_ability(possible_skills[0]).value,
                    self._resolve_homebrew_roll_condition(roll_conditions).value,
                    f"{max(character.get_skill_bonus(s) for s in possible_skills):+}",
                ]
                self._write_table_row(file, row)

        file.write("</table>\n<br>\n")

    def _write_features(
        self, character: CharacterStatBlock, file: TextIO, features: list[Feature]
    ):
        text_features = [f for f in features if not isinstance(f, CharacterFeature)]
        if not text_features:
            return

        file.write("<h2>Features</h2>\n")
        sorted_features = sorted(text_features, key=self._sort_features_key)

        file.write("<div>\n")
        for i, feature in enumerate(sorted_features):
            feature.write_to_file(character, file)
            if i < len(sorted_features) - 1:
                file.write("<hr>\n")
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

        self._apply_weapon_masteries(weapons, weapon_masteries)
        write_weapons_to_file(weapons, character, file)

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
            style.write_to_file(file)

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
                file.write("<hr>\n")

        file.write("<br>\n")

    def _write_spell_slots(self, character: CharacterStatBlock, file: TextIO):
        if not character.spell_slots:
            return

        file.write("<h2>Spell Slots</h2>\n")

        character_spell_slots = character.get_spell_slots()

        file.write("<table class='stat-table'>\n")
        file.write("<tr>")

        for level in character_spell_slots.keys():
            file.write(f"<th>Level {level}</th>")

        file.write("</tr>\n<tr>")

        for slots in character_spell_slots.values():
            boxes_html = (
                '<div class="slot-box-group">'
                + '<span class="slot-box"></span>' * slots
                + "</div>"
            )
            file.write(f"<td>{boxes_html}</td>")

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

        self._write_separated(
            sorted_spells, lambda spell, f: spell.write_to_file(f), file
        )

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

        sections = []
        if armors:
            armor_rows = [
                (armor.name, self._description_or_dash(armor.description))
                for armor in armors
            ]
            sections.append(("Armor", armor_rows))

        if weapons:
            weapon_rows = [
                (weapon.name, self._description_or_dash(weapon.description))
                for weapon in weapons
            ]
            sections.append(("Weapons", weapon_rows))

        if items:
            sorted_items = sorted(items, key=lambda x: x[0].name)
            item_rows = [
                (f"{item.name} ({quantity})", item.description())
                for item, quantity in sorted_items
            ]
            sections.append(("Other items", item_rows))

        for i, (title, rows) in enumerate(sections):
            if i > 0:
                file.write("<hr>")
            self._write_item_table(file, title, rows)

        file.write("<br>\n")

    def _write_tool_proficiencies(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        tool_proficiencies: Optional[list[ToolProficiency]],
    ):
        if not tool_proficiencies:
            return

        file.write("<h2>Tool Proficiencies</h2>\n")

        sorted_tool_proficiencies = sorted(tool_proficiencies, key=lambda x: x.name)
        proficiency_rows = [
            (tool_proficiency.name, tool_proficiency.description())
            for tool_proficiency in sorted_tool_proficiencies
        ]
        self._write_item_table(file, "Other Tool Proficiencies", proficiency_rows)

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

            br {
                display: none;
            }

            h2 {
                margin: 0.8em 0 0.15em;
            }

            table.stat-table {
                margin-bottom: 0.8rem;
            }
        }

        /* Forces a page break before the element in print/PDF */
        .print-page-break {
            break-before: page;
        }

        /* Side-by-side section layout — overrides the global div rule */
        .section-row {
            display: flex;
            gap: 1.5rem;
            align-items: flex-start;
            max-width: none;
            margin: 0;
            padding: 0;
        }

        .section-col {
            flex: 1;
            min-width: 0;
            max-width: none;
            margin: 0;
            padding: 0;
        }

        .section-col table.stat-table {
            width: 100%;
        }

        /* Stat tables: general info, combat, abilities, skills, spell slots */
        table.stat-table {
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0 0 0.5rem 0;
        }

        table.stat-table th,
        table.stat-table td {
            border: 1px solid var(--border-color);
            padding: 3px 8px;
            vertical-align: top;
            text-align: left;
        }

        table.stat-table th {
            background: #f5f5f5;
            font-weight: 600;
        }

        /* Spell slot checkboxes */
        .slot-box {
            display: inline-block;
            width: 1.6em;
            height: 1.6em;
            border: 1px solid currentColor;
            box-sizing: border-box;
            border-radius: 0.2em;
            vertical-align: middle;
        }

        .slot-box-group {
            display: inline-flex;
            gap: 0.5em;
            align-items: center;
            margin: 0.35em 0;
        }

        /* Item and tool proficiency tables */
        .item-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0.25rem 0;
        }

        .item-table td, .item-table th {
            border: 1px solid var(--border-color);
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

        /* Spell tables */
        .spell-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0.25rem 0;
        }

        .spell-table td, .spell-table th {
            border: 1px solid var(--border-color);
            padding: 3px 5px;
            vertical-align: top;
        }

        .spell-title {
            font-size: 1rem;
            text-align: left;
            background: #f5f5f5;
            font-weight: 600;
        }

        .spell-label {
            font-weight: 600;
            white-space: nowrap;
            background: #fafafa;
            padding: 2px 4px;
            width: 1%;
        }

        .spell-value {
            width: auto;
            padding: 2px 5px;
        }

        /* Weapon tables */
        .weapons {
            max-width: 100%;
        }

        .weapon-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0.25rem 0 0.75rem 0;
            table-layout: auto;
        }

        .weapon-table th,
        .weapon-table td {
            border: 1px solid var(--border-color);
            padding: 3px 5px;
            vertical-align: top;
        }

        .weapon-title {
            font-size: 1rem;
            text-align: left;
            background: #f5f5f5;
            font-weight: 600;
            padding: 4px 6px;
        }

        .weapon-first-col {
            font-weight: 600;
            white-space: nowrap;
            background: #fafafa;
            width: 1%;
            padding: 2px 4px;
        }

        .weapon-cell {
            padding: 2px 5px;
        }

        .weapon-separator td {
            border: none;
            padding: 2px 0;
            height: 6px;
        }

        .weapon-separator hr {
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 2px 0;
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
        items: list[tuple[Items.Item, int]],
        tool_proficiencies: list[ToolProficiency],
    ):
        output_path_obj = pathlib.Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path_obj, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            file.write(
                f"<h1>{character.name} - Level {character.character_level} {character.starter_class.value}</h1>\n"
            )
            self._write_general_info(character, file)
            self._write_combat_stats(character, file, armors, armor_proficiencies)
            self._write_abilities(character, file)
            self._write_skills(character, file, skill_config)
            file.write("<div class='print-page-break'></div>\n")
            self._write_features(character, file, features)
            self._write_weapons(character, file, weapons, weapon_masteries)
            self._write_fighting_styles(character, file, fighting_styles)
            self._write_invocations(character, file, invocations)
            self._write_spell_slots(character, file)
            self._write_spells(character, file, spells)
            self._write_items(character, file, armors, weapons, items)
            self._write_tool_proficiencies(character, file, tool_proficiencies)
