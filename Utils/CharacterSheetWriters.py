import pathlib
import re
from typing import Optional, TextIO

import DamageCalculator
import Definitions
from Definitions import Ability, Die, DiceRollCondition
from Features.Equipment import Armor
from Features.Core.BaseFeatures import Feature
from Features.Combat.FightingStyles import FightingStyle
from Features.Equipment.Weapons import AbstractWeapon, UnarmedStrike, write_weapons_to_file
from Invocations.InvocationFactory import InvocationFactory
from Features.Items import Items
from Spells.SpellFactory import SpellFactory
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from ToolProficiencies.ToolProficiencies import ToolProficiency
from Utils import StringUtils


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
                level_num = int(parts[1].split()[0])
            except (ValueError, IndexError):
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
    def _write_table_row(file: TextIO, cells: list, tr_class: str = ""):
        cls = f" class='{tr_class}'" if tr_class else ""
        file.write(f"<tr{cls}>")
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

    @staticmethod
    def _write_slot_item_table(file: TextIO, title: str, rows: list[tuple[str, str, int]]):
        """Inventory table with slot cost, carry quantity, and left-behind tracking."""
        file.write("<table class='item-table'>\n")
        file.write("<tr>\n")
        file.write(f"<th class='item-title'>{title}</th>\n")
        file.write("<th class='item-title item-col-narrow'>Slots</th>\n")
        file.write("<th class='item-title item-col-carry'>Carry</th>\n")
        file.write("<th class='item-title item-col-leftbehind'>Left Behind</th>\n")
        file.write("</tr>\n")

        for label, description, slots in rows:
            plain_label = re.sub(r"<span[^>]*>.*?</span>", "", label)
            plain_label = re.sub(r"<[^>]*>", "", plain_label).strip()
            leftbehind_id = plain_label.replace(" ", "_").replace("(", "").replace(")", "") + "_leftbehind"
            file.write("<tr>\n")
            file.write(f"<td class='item-entry'><strong>{label}</strong><br/>{description}</td>\n")
            file.write(f"<td style='text-align: center;'>{slots}</td>\n")
            file.write("<td></td>\n")
            file.write(f"<td class='item-leftbehind'><input type='checkbox' id='{leftbehind_id}_check' name='{leftbehind_id}_check'/></td>\n")
            file.write("</tr>\n")

        file.write("</table>\n")

    @staticmethod
    def _worn_tag(item: Items.Item, worn_label: str = "Worn", not_worn_label: str = "Not worn") -> str:
        """Chip showing worn state for wearable items; empty for everything else."""
        if not isinstance(item, Items.WearableItem):
            return ""
        if item.is_wearing:
            return f" <span class='wtag wtag-worn'>{worn_label}</span>"
        return f" <span class='wtag wtag-not-worn'>{not_worn_label}</span>"

    def _write_general_info(self, character: CharacterStatBlock, file: TextIO, experience_points: int = 0):
        file.write("<h2>General Info</h2>\n")

        rows = [
            ("Name", character.name),
            ("Level", character.character_level),
            ("Class", character.base_class.value),
            (
                "Multiclass",
                ", ".join(
                    f"{cls.value}: {lvl}"
                    for cls, lvl in character.level_per_class.items()
                    if lvl > 0
                ),
            ),
            ("Subclass", character.character_subclass),
            ("Prof. Bonus", character.get_proficiency_bonus()),
            ("XP", experience_points),
        ]

        file.write("<table class='stat-table'>\n<tr>")
        for field, _ in rows:
            file.write(f"<th>{field}</th>")
        file.write("</tr>\n<tr>")
        for _, value in rows:
            file.write(f"<td>{value}</td>")
        file.write("</tr>\n</table>\n<br class='section-gap'>\n")

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
            ac = f"{ac} (w/ Shield) / {ac - 2}"

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
        file.write("</tr>\n</table>\n<br class='section-gap'>\n")

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

            tr_class = "st-proficient" if character.is_proficient_in_saving_throw(ability) else ""
            self._write_table_row(file, row, tr_class)

        file.write("</table>\n<br>\n")

    def _write_save_dc_probabilities(self, character: CharacterStatBlock, file: TextIO, spellcasting_abilities: list[Ability]):
        save_bonuses = range(-3, 13)

        dc_to_abilities: dict[int, list[str]] = {}
        for ability in spellcasting_abilities:
            dc = character.calculate_difficulty_class_for_ability(ability)
            dc_to_abilities.setdefault(dc, []).append(ability.short_name)

        file.write("<table class='dc-fail-table'>\n")
        file.write("<tr><th class='dc-fail-dc-col'>DC (Fail %)</th>")
        for bonus in save_bonuses:
            sign = "+" if bonus >= 0 else ""
            file.write(f"<th class='whit-ac'>{sign}{bonus}</th>")
        file.write("</tr>\n")

        for dc in sorted(dc_to_abilities.keys(), reverse=True):
            abilities_label = "/".join(dc_to_abilities[dc])
            file.write(f"<tr><th class='dc-fail-dc-col'>DC {dc} ({abilities_label})</th>")
            for bonus in save_bonuses:
                prob_success = DamageCalculator.probability_of_success(
                    difficulty_class=dc,
                    die=Die.D20,
                    condition=DiceRollCondition.NEUTRAL,
                    bonus=bonus,
                )
                pct = round((1 - prob_success) * 100)
                pct_bucket = round(pct / 5) * 5
                file.write(f"<td class='whit-pct' data-pct='{pct_bucket}'>{pct}%</td>")
            file.write("</tr>\n")

        file.write("</table>\n")

        # ── Spell attack hit % table ────────────────────────────────────────
        ac_range = range(10, 26)

        bonus_to_abilities: dict[int, list[str]] = {}
        for ability in spellcasting_abilities:
            attack_bonus = character.calculate_attack_bonus_for_ability(ability)
            bonus_to_abilities.setdefault(attack_bonus, []).append(ability.short_name)

        spell_attack_conditions = [
            ("Normal", DiceRollCondition.NEUTRAL),
            ("Adv.", DiceRollCondition.ADVANTAGE),
            ("Disadv.", DiceRollCondition.DISADVANTAGE),
        ]

        file.write("<table class='dc-fail-table'>\n")
        file.write("<tr><th class='dc-fail-dc-col'>Spell Attack (Hit %)</th><th class='dc-fail-dc-col'></th>")
        for ac in ac_range:
            file.write(f"<th class='whit-ac'>AC {ac}</th>")
        file.write("</tr>\n")

        for attack_bonus in sorted(bonus_to_abilities.keys(), reverse=True):
            abilities_label = "/".join(bonus_to_abilities[attack_bonus])
            sign = "+" if attack_bonus >= 0 else ""
            bonus_label = f"{sign}{attack_bonus} ({abilities_label})"
            for i, (cond_label, condition) in enumerate(spell_attack_conditions):
                row_header = f"<th class='dc-fail-dc-col'>{bonus_label if i == 0 else ''}</th>"
                file.write(f"<tr>{row_header}<th class='dc-fail-dc-col'>{cond_label}</th>")
                for ac in ac_range:
                    prob = DamageCalculator.probability_of_success(
                        difficulty_class=ac,
                        die=Die.D20,
                        condition=condition,
                        bonus=attack_bonus,
                    )
                    pct = round(prob * 100)
                    pct_bucket = round(pct / 5) * 5
                    file.write(f"<td class='whit-pct' data-pct='{pct_bucket}'>{pct}%</td>")
                file.write("</tr>\n")

        file.write("</table>\n")

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
            "Breakdown",
            "Ability",
        ]

        file.write("<table class='stat-table'>\n")

        file.write("<tr>")
        for header in headers:
            file.write(f"<th>{header}</th>")
        file.write("</tr>\n")

        if skill_config == Definitions.SkillConfig.DEFAULT:
            for skill in Definitions.Skill.list_sorted():
                proficient = character.is_proficient_in_skill(skill)
                has_expertise = character.has_expertise_in_skill(skill)

                if has_expertise:
                    tr_class = "st-expertise"
                elif proficient:
                    tr_class = "st-proficient"
                else:
                    tr_class = ""

                condition = character.get_skill_roll_condition(skill)
                reasons = character.get_skill_roll_condition_reasons(skill)
                row = [
                    skill.value,
                    self._modifier_with_condition(
                        character.get_skill_modifier(skill), condition
                    ),
                    self._skill_modifier_breakdown(character, skill, condition, reasons),
                    character.get_skill_ability(skill).value,
                ]
                self._write_table_row(file, row, tr_class)

        if skill_config == Definitions.SkillConfig.HOMEBREW:
            for skill in Definitions.HomeBrewSkill.list_sorted():
                possible_skills = Definitions.SkillConfig.map_homebrew_to_default(skill)
                roll_conditions = set(
                    character.get_skill_roll_condition(s) for s in possible_skills
                )
                proficient = any(
                    character.is_proficient_in_skill(s) for s in possible_skills
                )
                has_expertise = any(
                    character.has_expertise_in_skill(s) for s in possible_skills
                )

                if has_expertise:
                    tr_class = "st-expertise"
                elif proficient:
                    tr_class = "st-proficient"
                else:
                    tr_class = ""

                # Breakdown follows the default skill that yields the best modifier
                best_skill = max(possible_skills, key=character.get_skill_modifier)
                condition = self._resolve_homebrew_roll_condition(roll_conditions)
                reasons = [
                    reason
                    for s in possible_skills
                    if character.get_skill_roll_condition(s) == condition
                    for reason in character.get_skill_roll_condition_reasons(s)
                ]
                row = [
                    skill.value,
                    self._modifier_with_condition(
                        character.get_skill_modifier(best_skill), condition
                    ),
                    self._skill_modifier_breakdown(character, best_skill, condition, reasons),
                    character.get_skill_ability(possible_skills[0]).value,
                ]
                self._write_table_row(file, row, tr_class)

        file.write("</table>\n<br>\n")

    @staticmethod
    def _modifier_with_condition(
        modifier: int, condition: Definitions.DiceRollCondition
    ) -> str:
        """Modifier with the roll condition in parentheses, e.g. '+5 (Advantage)'."""
        if condition == Definitions.DiceRollCondition.NEUTRAL:
            return f"{modifier:+}"
        return f"{modifier:+} ({condition.value})"

    @staticmethod
    def _skill_modifier_breakdown(
        character: CharacterStatBlock,
        skill: Definitions.Skill,
        condition: Definitions.DiceRollCondition = Definitions.DiceRollCondition.NEUTRAL,
        condition_reasons: Optional[list[str]] = None,
    ) -> str:
        """Modifier as a sum of its parts, e.g. '2 + 3 (proficiency) + 1 (Ring of X)',
        followed by the roll condition and its reason, e.g. 'Disadvantage (Chain Mail)'."""
        terms: list[tuple[int, str]] = []
        proficiency_bonus = character.get_proficiency_bonus()
        if character.has_expertise_in_skill(skill):
            terms.append((proficiency_bonus, "proficiency"))
            terms.append((proficiency_bonus, "expertise"))
        elif character.is_proficient_in_skill(skill):
            terms.append((proficiency_bonus, "proficiency"))
        terms.extend(character.get_skill_bonus_sources(skill))

        breakdown = str(character.get_ability_modifier(character.get_skill_ability(skill)))
        for value, label in terms:
            sign = "+" if value >= 0 else "-"
            breakdown += f" {sign} {abs(value)} ({label})"

        if condition != Definitions.DiceRollCondition.NEUTRAL:
            condition_text = condition.value
            if condition_reasons:
                condition_text += f" ({', '.join(condition_reasons)})"
            breakdown += f", {condition_text}"
        return breakdown

    def _write_features(
        self, character: CharacterStatBlock, file: TextIO, features: list[Feature]
    ):
        text_features = [f for f in features if f.get_description(character) is not None]
        if not text_features:
            return

        file.write("<h2>Features</h2>\n")
        sorted_features = sorted(text_features, key=self._sort_features_key)

        file.write("<div>\n")
        for feature in sorted_features:
            feature.write_to_file(character, file)
        file.write("</div>\n<br class='section-gap'>\n")

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
            desc = style.description().strip()
            if ": " in desc:
                name, body = desc.split(": ", 1)
            else:
                name, body = "Fighting Style", desc
            processed_body = StringUtils.boxes_to_html(body)
            file.write("<div class='feature-card'>\n")
            file.write("<div class='feature-header'>\n")
            file.write(f"<span class='feature-name'>{name}</span>\n")
            file.write("</div>\n")
            file.write("<div class='feature-body'>\n")
            file.write(f"<p>{processed_body}</p>\n")
            file.write("</div>\n")
            file.write("</div>\n")

        file.write("<br class='section-gap'>\n")

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

        for invocation in sorted_invocations:
            level_label = f"Level {invocation.level}" if invocation.level else "No level requirement"
            file.write("<div class='feature-card'>\n")
            file.write("<div class='feature-header'>\n")
            file.write(f"<span class='feature-name'>{invocation.name}</span>\n")
            file.write(f"<span class='feature-origin'>{level_label}</span>\n")
            file.write("</div>\n")
            file.write("<div class='feature-body'>\n")
            if invocation.prerequisite:
                file.write(f"<p><strong>Prerequisite:</strong> {invocation.prerequisite}</p>\n")
            processed_desc = StringUtils.boxes_to_html(invocation.description)
            for para in processed_desc.split("\n"):
                if para.strip():
                    file.write(f"<p>{para.strip()}</p>\n")
            if invocation.source:
                file.write(f"<p class='inv-source'>{invocation.source}</p>\n")
            file.write("</div>\n")
            file.write("</div>\n")

        file.write("<br class='section-gap'>\n")

    @staticmethod
    def _write_slot_table(slots: dict[int, int], file: TextIO, reset_label: str):
        file.write("<table class='stat-table'>\n")
        file.write("<tr>")
        for level in slots:
            file.write(f"<th>Level {level}</th>")
        file.write("</tr>\n<tr>")
        for count in slots.values():
            boxes_html = (
                '<div class="slot-box-group">'
                + '<span class="slot-box"></span>' * count
                + "</div>"
            )
            file.write(f"<td>{boxes_html}</td>")
        file.write("</tr>\n</table>\n")
        file.write(f"<span class='slot-reset-label'>{reset_label}</span>\n")

    def _write_pact_magic_slots(self, character: CharacterStatBlock, file: TextIO):
        if not character.pact_magic_slots:
            return
        file.write("<h2>Pact Magic Slots</h2>\n")
        self._write_slot_table(
            character.pact_magic_slots, file, "Regained on: Short Rest or Long Rest"
        )
        file.write("<br class='section-gap'>\n")

    def _write_spell_slots(self, character: CharacterStatBlock, file: TextIO):
        if not character.spell_slots:
            return

        file.write("<h2>Spell Slots</h2>\n")
        self._write_slot_table(
            character.get_spell_slots(), file, "Regained on: Long Rest"
        )
        file.write("<br class='section-gap'>\n")

    def _write_spells(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        spells: list[tuple[str, Ability, Optional[str]]],
    ):
        if not spells:
            return

        file.write("<h2>Spells</h2>\n")
        casting_abilities = sorted(
            {ability for _, ability, _ in spells},
            key=lambda a: a.value,
        )
        label = "Spellcasting Abilities" if len(casting_abilities) > 1 else "Spellcasting Ability"
        abilities_str = ", ".join(a.value for a in casting_abilities)
        file.write(f"<p><strong>{label}:</strong> {abilities_str}</p>\n")
        self._write_save_dc_probabilities(character, file, casting_abilities)
        file.write("<div class='spells'>\n")

        created_spells = [
            SpellFactory.create(spell_name, spell_casting_ability, additional_ruling)
            for spell_name, spell_casting_ability, additional_ruling in spells
        ]
        sorted_spells = sorted(created_spells, key=lambda s: (s.level, s.name))

        # Determine if character is a prepared-caster class
        prepared_caster_classes = {
            Definitions.CharacterClass.CLERIC,
            Definitions.CharacterClass.DRUID,
            Definitions.CharacterClass.WIZARD,
            Definitions.CharacterClass.PALADIN,
            Definitions.CharacterClass.ARTIFICER,
        }
        show_prep_checkbox = character.base_class in prepared_caster_classes

        # Group by level and emit a level header before each group
        from itertools import groupby
        for level, group in groupby(sorted_spells, key=lambda s: s.level):
            level_label = "Cantrips" if level == 0 else f"Level {level} Spells"
            file.write(f"<h3 class='spell-level-header'>{level_label}</h3>\n")
            for i, spell in enumerate(group):
                if i > 0:
                    file.write("<div class='spell-gap'></div>\n")
                spell.write_to_file(file, show_preparation_checkbox=show_prep_checkbox)

        file.write("</div>\n")
        file.write("<br class='section-gap'>\n")

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

        # Write carrying capacity: one checkbox per slot, one column per source
        if items:
            carrying_capacity = character.get_carrying_capacity()
            file.write(f"<p><strong>Carrying Capacity ({carrying_capacity} slots):</strong></p>\n")
            file.write("<table class='capacity-table'>\n")
            file.write("<tr>\n")
            for source, slots in character.carrying_capacity_sources:
                file.write(f"<th class='item-title'>{source} ({slots})</th>\n")
            file.write("</tr>\n")
            file.write("<tr>\n")
            for _source, slots in character.carrying_capacity_sources:
                slot_boxes = "<span class='slot-box'></span>" * slots
                file.write(f"<td><span class='slot-box-group'>{slot_boxes}</span></td>\n")
            file.write("</tr>\n")
            file.write("</table>\n")

        # Each section renders in the same slot-table format:
        # (title, [(label, description, slots), ...])
        sections = []
        if armors:
            armor_rows = [
                (
                    f"{armor.name}{self._worn_tag(armor)}",
                    self._description_or_dash(armor.description),
                    armor.slots,
                )
                for armor in armors
            ]
            sections.append(("Armor", armor_rows))

        if weapons:
            weapon_rows = [
                (
                    f"{weapon.name}{self._worn_tag(weapon, 'Wielded', 'Not wielded')}",
                    self._description_or_dash(weapon.description),
                    weapon.slots,
                )
                for weapon in weapons
                if not isinstance(weapon, UnarmedStrike)
            ]
            if weapon_rows:
                sections.append(("Weapons", weapon_rows))

        if items:
            sorted_items = sorted(items, key=lambda x: x[0].name)
            item_rows = [
                (
                    f"{item.name} ({quantity}){self._worn_tag(item)}",
                    item.description(),
                    item.slots,
                )
                for item, quantity in sorted_items
            ]
            sections.append(("Other items", item_rows))

        for i, (title, rows) in enumerate(sections):
            if i > 0:
                file.write("<hr>")
            self._write_slot_item_table(file, title, rows)

        file.write("<br class='section-gap'>\n")

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

        file.write("<br class='section-gap'>\n")

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
            font-size: 14px;
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

        h1 {
            color: #3a2c1c;
            border-bottom: 3px solid #9a7040;
            padding-bottom: 0.2em;
            margin: 0 0 1rem 0;
            font-size: 1.6rem;
            letter-spacing: 0.02em;
        }

        h2 {
            color: #3a2c1c;
            border-bottom: 2px solid #9a7040;
            padding-bottom: 0.12em;
            margin: 1.1rem 0 0.4rem 0;
            font-size: 1.2rem;
            letter-spacing: 0.02em;
        }

        ul, ol {
            margin: 0.5em 0 0.5em 1.2em;
        }

        @media print {
            body {
                padding: 0;
                font-size: 10pt;
            }

            div {
                max-width: 100%;
            }

            h1, h2, h3 {
                page-break-after: avoid;
            }

            p, pre, ul, ol {
                page-break-inside: auto;
            }

            .page-break {
                display: none;
            }

            /* Collapse inter-section <br> gaps (but not content line breaks) */
            br.section-gap {
                display: none;
            }

            h1 {
                margin: 0 0 0.3rem 0;
            }

            h2 {
                margin: 0.3em 0 0.1em;
            }

            table.stat-table {
                margin-bottom: 0.4rem;
            }

            table.stat-table th,
            table.stat-table td {
                padding: 3px 6px;
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
            margin: 0 0 0.75rem 0;
        }

        table.stat-table th,
        table.stat-table td {
            border: 1px solid #c4b49a;
            padding: 5px 10px;
            vertical-align: middle;
            text-align: left;
        }

        table.stat-table th {
            color: #3a2c1c;
            font-weight: 700;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            white-space: nowrap;
            border-bottom: 2px solid #3a2c1c;
        }

        table.stat-table tr.st-proficient td {
            color: #2e6e3e;
        }

        table.stat-table tr.st-proficient td:first-child {
            font-weight: 700;
        }

        table.stat-table tr.st-expertise td {
            color: #8a6200;
        }

        table.stat-table tr.st-expertise td:first-child {
            font-weight: 700;
        }

        /* Expertise badge styling */
        .skill-expertise {
            display: inline-block;
            border: 1px solid #d4a747;
            color: #8a6200;
            padding: 0 5px;
            border-radius: 3px;
            font-weight: 700;
            font-size: 0.85em;
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

        .slot-reset-label {
            display: block;
            font-size: 0.75em;
            font-style: italic;
            color: #666;
            margin-top: 0.1em;
            margin-bottom: 0.4em;
        }

        /* Item and tool proficiency tables */
        .item-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 8px;
            font-size: 0.85rem;
            margin: 0.25rem 0;
        }

        .item-table td, .item-table th {
            border: 1px solid var(--border-color);
            padding: 3px 5px;
            vertical-align: top;
        }

        .item-title {
            color: #3a6e4a;
            font-size: 0.78rem;
            font-weight: 700;
            text-align: left;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            border-bottom: 2px solid #6a9a7a !important;
        }

        .item-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
        }

        .item-value {
            width: auto;
        }

        /* Carrying capacity: one column of slot checkboxes per source */
        .capacity-table {
            border-collapse: collapse;
            font-size: 0.85rem;
            margin: 0.25rem 0 0.5rem 0;
        }

        .capacity-table th,
        .capacity-table td {
            border: 1px solid var(--border-color);
            padding: 4px 8px;
            text-align: center;
            vertical-align: middle;
        }

        .capacity-table .slot-box-group {
            flex-wrap: wrap;
            max-width: 12em;
        }

        /* Item inventory rows: name + description, wraps normally */
        .item-entry strong {
            color: #3a6e4a;
        }

        .item-col-narrow {
            width: 3em;
            text-align: center;
        }

        .item-col-carry {
            width: 4.5em;
            text-align: center;
        }

        .item-col-leftbehind {
            width: 9em;
        }

        .item-leftbehind input[type='checkbox'] {
            vertical-align: middle;
        }

        /* Individual item rows styled as cards */
        .item-table tr:not(:first-child) td {
            border: 2px solid #a4c8b0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
            padding: 5px 7px;
        }

        .item-table tr:not(:first-child) td:first-child {
            border-radius: 4px 0 0 4px;
        }

        .item-table tr:not(:first-child) td:last-child {
            border-radius: 0 4px 4px 0;
        }

        /* ── Spell cards ──────────────────────────────────────────────────── */
        .spells {
            max-width: 100%;
        }

        /* Level section header */
        h3.spell-level-header {
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #4a5568;
            margin: 0.8rem 0 0.3rem 0;
            padding: 0;
            border-bottom: 1px solid #c8ccd8;
        }

        /* Gap between consecutive spell cards */
        .spell-gap {
            height: 0;
            max-width: none;
            margin: 0;
            padding: 0;
            border-bottom: none;
            display: none;
        }

        /* Each spell is its own bordered card table */
        table.spell-card {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            border: 2px solid #a8c4d8;
            border-radius: 4px;
            margin: 0 0 8px 0;
            table-layout: auto;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        }

        table.spell-card td,
        table.spell-card th {
            border: 1px solid var(--border-color);
            padding: 3px 7px;
            vertical-align: top;
        }

        /* Add bottom border to spell rows for clearer separation within card */
        table.spell-card tr {
            border-bottom: 1px solid #ddd;
        }

        table.spell-card tr:last-child {
            border-bottom: none;
        }

        /* Spell name — full-width header row */
        .spell-name {
            color: #3a5a7a;
            font-size: 1rem;
            font-weight: 700;
            text-align: left;
            letter-spacing: 0.02em;
            padding: 4px 7px;
            border-bottom: 2px solid #6888a8;
        }

        /* Quick-stats row — two cells side by side */
        tr.spell-quickstats td {
            font-size: 0.82rem;
            white-space: normal;
            padding: 3px 7px;
        }

        .sqs-left {
            width: 50%;
        }

        .sqs-right {
            width: 50%;
        }

        /* Inline label within quick-stats */
        .slabel {
            font-weight: 600;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-right: 2px;
        }

        /* Bullet separator between quick-stat items */
        .ssep {
            color: #aaa;
            margin: 0 5px;
        }

        /* Description rows */
        tr.spell-desc-row td,
        tr.spell-higher-row td {
            font-size: 0.8rem;
            padding: 3px 7px;
        }

        .sdesc-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .sdesc-text {
            color: #333;
        }

        /* Higher-level row gets a subtle accent */
        tr.spell-higher-row td {
            font-style: italic;
            color: #3a5a7a;
        }

        /* Concentration chip — gold */
        .stag {
            display: inline-block;
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 0.72rem;
            font-weight: 600;
            margin-left: 5px;
            vertical-align: middle;
            white-space: nowrap;
        }

        .stag-concentration {
            border: 1px solid #c8a227;
            color: #7a5c00;
        }

        /* Ritual chip — teal */
        .stag-ritual {
            border: 1px solid #2a9d8f;
            color: #1a5f58;
        }

        /* ── Weapon cards ─────────────────────────────────────────────── */
        .weapons {
            max-width: 100%;
        }

        /* Gap between consecutive weapon cards */
        .weapon-gap {
            display: none;
        }

        /* Each weapon is its own bordered card table */
        table.weapon-card {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            border: 2px solid #d4a0a0;
            border-radius: 4px;
            margin: 0 0 8px 0;
            table-layout: auto;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        }

        table.weapon-card td,
        table.weapon-card th {
            border: 1px solid var(--border-color);
            padding: 3px 7px;
            vertical-align: top;
        }

        /* Weapon name — full-width header row */
        .weapon-name {
            color: #8a4a4a;
            font-size: 1rem;
            font-weight: 700;
            text-align: left;
            letter-spacing: 0.02em;
            padding: 4px 7px;
            border-bottom: 2px solid #a06060;
        }

        /* Quick-stats row — two cells side by side */
        tr.weapon-quickstats td {
            font-size: 0.82rem;
            white-space: normal;
            padding: 3px 7px;
        }

        .wqs-left {
            width: 40%;
        }

        .wqs-right {
            width: 60%;
        }

        /* Inline label within quick-stats */
        .wlabel {
            font-weight: 600;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-right: 2px;
        }

        /* Bullet separator between quick-stat items */
        .wsep {
            color: #aaa;
            margin: 0 5px;
        }

        /* Properties tag row */
        tr.weapon-tags-row td {
            padding: 3px 7px;
            font-size: 0.82rem;
        }

        .wlabel-col {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .wtags-cell {
            padding: 3px 7px;
        }

        /* Individual property/tag chips */
        .wtag {
            display: inline-block;
            border: 1px solid #c8ccd8;
            border-radius: 3px;
            padding: 1px 6px;
            font-size: 0.78rem;
            margin-right: 4px;
            margin-bottom: 2px;
            white-space: nowrap;
        }

        /* Mastery chip — active (player has it) */
        .wtag-mastery {
            border-color: #9abb9a;
            color: #3a6e3a;
            font-weight: 600;
        }

        /* Mastery chip — inactive (weapon has it but player doesn't) */
        .wtag-mastery-inactive {
            border-color: #ccc;
            color: #999;
            font-style: italic;
        }

        /* Wearable item chip — currently worn */
        .wtag-worn {
            border-color: #9abb9a;
            color: #3a6e3a;
            font-weight: 600;
        }

        /* Wearable item chip — carried but not worn */
        .wtag-not-worn {
            border-color: #ccc;
            color: #999;
            font-style: italic;
        }

        /* Per-property description rows */
        tr.weapon-prop-row td {
            font-size: 0.8rem;
            padding: 2px 7px;
        }

        .wprop-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: var(--muted-color);
        }

        .wprop-desc {
            color: #444;
        }

        /* Mastery description row */
        tr.weapon-mastery-row td {
            font-size: 0.8rem;
            padding: 2px 7px;
        }

        .wmastery-label {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: #3a6e3a;
        }

        .wmastery-desc {
            color: #3a3a3a;
        }

        /* Additional description row */
        tr.weapon-addl-row td {
            font-size: 0.82rem;
            padding: 3px 7px;
            font-style: italic;
        }

        .waddl-desc {
            color: #333;
        }

        /* ── Wild Shape form cards ────────────────────────────────────────── */
        table.wildshape-card {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            border: 2px solid #8fae6e;
            border-radius: 4px;
            margin: 0.4rem 0 8px 0;
            table-layout: auto;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        }

        table.wildshape-card td,
        table.wildshape-card th {
            border: 1px solid var(--border-color);
            padding: 3px 7px;
            vertical-align: top;
        }

        .wsf-name {
            color: #4a6b32;
            font-size: 1rem;
            font-weight: 700;
            text-align: left;
            letter-spacing: 0.02em;
            padding: 4px 7px;
            border-bottom: 2px solid #6f9a4a;
        }

        .wsf-name .wsf-subtitle {
            font-size: 0.78rem;
            font-weight: 400;
            font-style: italic;
            color: var(--muted-color);
            margin-left: 0.5em;
        }

        .wsf-label-col {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: var(--muted-color);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .wsf-value-col {
            padding: 3px 7px;
        }

        /* Section divider row, e.g. "Actions", "Traits" */
        tr.wsf-section th {
            background: #eef3e6;
            color: #4a6b32;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            text-align: left;
            padding: 2px 7px;
        }

        .wsf-entry-name {
            font-weight: 600;
            white-space: nowrap;
            width: 1%;
            color: #444;
        }

        .wsf-entry-desc {
            color: #333;
        }

        /* Notes about stats retained from the player rather than the Beast */
        .wsf-retained {
            font-style: italic;
            color: var(--muted-color);
        }

        /* ── Feature cards ───────────────────────────────────────────────── */
        .feature-card {
            border: 1px solid #b89060;
            border-radius: 4px;
            overflow: hidden;
            margin: 0 0 0.55rem 0;
            max-width: none;
            padding: 0;
        }

        .feature-header {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 0.8rem;
            padding: 5px 10px;
            border-bottom: 2px solid #9a7040;
            max-width: none;
            margin: 0;
        }

        .feature-name {
            font-size: 1rem;
            font-weight: 700;
            color: #4a3020;
            letter-spacing: 0.02em;
        }

        .feature-origin {
            font-size: 0.75rem;
            color: #9a7040;
            font-style: italic;
            white-space: nowrap;
            flex-shrink: 0;
        }

        .feature-body {
            padding: 0.4rem 0.7rem;
            font-size: 0.88rem;
            max-width: none;
            margin: 0;
        }

        .feature-body p {
            margin: 0.3em 0;
        }

        .feature-body ul,
        .feature-body ol {
            margin: 0.3em 0 0.3em 1.2em;
        }

        /* Feature upgrade blocks (nested inside .feature-body) */
        .feature-upgrade {
            margin-top: 0.5rem;
            border-left: 3px solid #9abbe0;
            border-radius: 0 3px 3px 0;
            padding: 0.3rem 0.6rem;
            max-width: none;
        }

        .feature-upgrade-label {
            display: block;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #3a6090;
            margin-bottom: 0.15rem;
        }

        .feature-upgrade-body {
            font-size: 0.85rem;
            color: #333;
            max-width: none;
            margin: 0;
            padding: 0;
        }

        .inv-source {
            font-size: 0.75em;
            color: #999;
            font-style: italic;
            margin-top: 0.35em;
        }

        /* ── Weapon hit-probability row ──────────────────────────────────── */
        tr.weapon-hit-row td {
            padding: 3px 7px;
            vertical-align: middle;
        }

        /* Inner table that holds the AC columns */
        table.whit-inner {
            border-collapse: collapse;
            font-size: 0.75rem;
            width: 100%;
        }

        td.whit-cond-label, th.whit-cond-label {
            font-size: 0.7rem;
            font-weight: 600;
            color: #555;
            white-space: nowrap;
            padding: 2px 5px;
            text-align: right;
            border: none;
        }

        th.whit-ac {
            color: #3a2c1c;
            font-weight: 700;
            text-align: center;
            padding: 2px 5px;
            border: 1px solid #5a4030;
            white-space: nowrap;
            min-width: 2.4em;
            font-size: 0.72rem;
            letter-spacing: 0.03em;
        }

        td.whit-pct {
            text-align: center;
            padding: 2px 5px;
            border: 1px solid #ddd;
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
        }

        /* Colour-code the probability cells: green → yellow → red */
        td.whit-pct[data-pct="100"],
        td.whit-pct[data-pct="95"],
        td.whit-pct[data-pct="90"],
        td.whit-pct[data-pct="85"],
        td.whit-pct[data-pct="80"] {
            color: #155724;
            font-weight: 600;
        }

        td.whit-pct[data-pct="75"],
        td.whit-pct[data-pct="70"],
        td.whit-pct[data-pct="65"],
        td.whit-pct[data-pct="60"] {
            color: #856404;
            font-weight: 600;
        }

        td.whit-pct[data-pct="55"],
        td.whit-pct[data-pct="50"],
        td.whit-pct[data-pct="45"],
        td.whit-pct[data-pct="40"] {
            color: #b35900;
            font-weight: 600;
        }

        td.whit-pct[data-pct="35"],
        td.whit-pct[data-pct="30"],
        td.whit-pct[data-pct="25"],
        td.whit-pct[data-pct="20"],
        td.whit-pct[data-pct="15"],
        td.whit-pct[data-pct="10"],
        td.whit-pct[data-pct="5"],
        td.whit-pct[data-pct="0"] {
            color: #b02a37;
            font-weight: 600;
        }

        /* ── Spell save DC fail-probability table ────────────────────────── */
        table.dc-fail-table {
            border-collapse: collapse;
            font-size: 0.75rem;
            margin: 0 0 0.75rem 0;
        }

        table.dc-fail-table th.dc-fail-dc-col {
            color: #3a2c1c;
            font-weight: 700;
            font-size: 0.72rem;
            text-align: left;
            padding: 2px 8px;
            border: 1px solid #5a4030;
            white-space: nowrap;
            letter-spacing: 0.03em;
        }

        /* Spell school colors — preserved in print */
        span[style*="color:"] {
            print-color-adjust: exact;
            -webkit-print-color-adjust: exact;
        }

        /* Spell preparation checkbox */
        .spell-prep-checkbox {
            display: inline-block;
            width: 1.2em;
            height: 1.2em;
            border: 1.5px solid #3a5a7a;
            box-sizing: border-box;
            border-radius: 2px;
            vertical-align: middle;
            margin-right: 0.3em;
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
        experience_points: int = 0,
    ):
        output_path_obj = pathlib.Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path_obj, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            file.write(
                f"<h1>{character.name} - Level {character.character_level} {character.base_class.value}</h1>\n"
            )
            self._write_general_info(character, file, experience_points)
            self._write_combat_stats(character, file, armors, armor_proficiencies)
            self._write_abilities(character, file)
            self._write_skills(character, file, skill_config)
            file.write("<div class='print-page-break'></div>\n")
            self._write_features(character, file, features)
            self._write_weapons(character, file, weapons, weapon_masteries)
            self._write_fighting_styles(character, file, fighting_styles)
            self._write_invocations(character, file, invocations)
            self._write_pact_magic_slots(character, file)
            self._write_spell_slots(character, file)
            self._write_spells(character, file, spells)
            self._write_items(character, file, armors, weapons, items)
            self._write_tool_proficiencies(character, file, tool_proficiencies)
