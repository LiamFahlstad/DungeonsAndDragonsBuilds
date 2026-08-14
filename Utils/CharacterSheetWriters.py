import pathlib
from typing import Literal, Optional, TextIO

import Core.Definitions as Definitions
from CharacterContent.Features.CombatFeatures.FightingStyles import FightingStyle
from CharacterContent.Features.Core.BaseFeatures import FEATURE_CARD_CSS, Feature
from CharacterContent.Invocations.InvocationFactory import InvocationFactory
from CharacterContent.Items import Armor, Items
from CharacterContent.Items.Weapons import (
    AbstractWeapon,
    UnarmedStrike,
    WeaponProficiency,
    write_weapons_to_file,
)
from CharacterContent.Items.Weapons.Writer import WEAPON_CARD_CSS
from CharacterContent.Spells.SpellFactory import SpellFactory
from CharacterContent.Spells.SpellFactory.Writer import SPELL_CARD_CSS
from CharacterContent.ToolProficiencies.Proficiencies import ToolProficiency
from Core.Definitions import Ability, DiceRollCondition, Die
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import DamageCalculator, Html
from Utils.CreatureStatBlocks import WILDSHAPE_CARD_CSS


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
    def _worn_tag(
        item: Items.Item, worn_label: str = "Worn", not_worn_label: str = "Not worn"
    ) -> str:
        """Chip showing worn state for wearable items; empty for everything else."""
        if item.is_wearing is None:
            return ""
        if item.is_wearing:
            return f" <span class='wtag wtag-worn'>{worn_label}</span>"
        return f" <span class='wtag wtag-not-worn'>{not_worn_label}</span>"

    @staticmethod
    def _format_class_level_history(character: CharacterStatBlock) -> str:
        def format_segment(start: int, end: int, character_class) -> str:
            level_label = str(start) if start == end else f"{start}-{end}"
            return f"{level_label}: {character_class.value}"

        return ", ".join(
            format_segment(start, end, character_class)
            for start, end, character_class in character.get_class_level_segments()
        )

    def _write_general_info(
        self, character: CharacterStatBlock, file: TextIO, experience_points: int = 0
    ):
        file.write("<h2>General Info</h2>\n")

        languages = ", ".join(
            language.value
            for language in sorted(character.languages, key=lambda lang: lang.value)
        )
        senses = ", ".join(
            f"{sense.value} {character.senses[sense]} ft."
            for sense in sorted(character.senses, key=lambda s: s.value)
        )

        rows = [
            ("Name", character.name, ""),
            ("Levels per class", self._format_class_level_history(character), ""),
            ("Subclass", character.character_subclass, ""),
            ("Prof. Bonus", character.get_proficiency_bonus(), ""),
            ("Languages", languages, ""),
            ("Senses", senses, ""),
            # Left blank (regardless of experience_points) so the player can
            # fill it in by hand; xp-cell widens the column to leave room.
            ("XP", "", "xp-cell"),
        ]

        file.write("<table class='stat-table'>\n<tr>")
        for field, _, css_class in rows:
            cls = f" class='{css_class}'" if css_class else ""
            file.write(f"<th{cls}>{field}</th>")
        file.write("</tr>\n<tr>")
        for _, value, css_class in rows:
            cls = f" class='{css_class}'" if css_class else ""
            file.write(f"<td{cls}>{value}</td>")
        file.write("</tr>\n</table>\n<br class='section-gap'>\n")

    def _write_combat_stats(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: set[WeaponProficiency],
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

        resistance_immunity_groups = []
        if character.damage_resistances:
            resistance_immunity_groups.append(
                "Resistant: "
                + ", ".join(
                    damage_type.value
                    for damage_type in sorted(
                        character.damage_resistances, key=lambda d: d.value
                    )
                )
            )
        if character.damage_immunities:
            resistance_immunity_groups.append(
                "Immune: "
                + ", ".join(
                    damage_type.value
                    for damage_type in sorted(
                        character.damage_immunities, key=lambda d: d.value
                    )
                )
            )
        if character.condition_immunities:
            resistance_immunity_groups.append(
                "Condition Immune: "
                + ", ".join(
                    condition.value
                    for condition in sorted(
                        character.condition_immunities, key=lambda c: c.value
                    )
                )
            )
        resistances_and_immunities = "; ".join(resistance_immunity_groups)

        rows = [
            ("Max HP", character.calculate_hit_points()),
            ("AC", ac),
            (
                "Armor Prof.",
                ", ".join(sorted([a.value for a in armor_proficiencies])),
            ),
            (
                "Weapon Prof.",
                ", ".join(sorted([wp.value for wp in weapon_proficiencies])),
            ),
            ("Initiative", initiative),
            ("Speed (ft)", character.combat.speed),
            ("Size", character.combat.size.value),
            ("Resistances / Immunities", resistances_and_immunities),
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

            tr_class = (
                "st-proficient"
                if character.is_proficient_in_saving_throw(ability)
                else ""
            )
            Html.write_table_row(file, row, tr_class)

        file.write("</table>\n<br>\n")

    def _write_spellcasting_headline(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        casting_abilities: list[Ability],
        include_probability_tables: bool = False,
    ):
        """Prominent Ability / Save DC / Attack modifier tiles, one row per
        spellcasting ability. The probability breakdown tables that follow
        are reference material, so they're rendered smaller and muted.
        """
        file.write("<div class='spell-headline'>\n")
        for ability in casting_abilities:
            dc = character.calculate_difficulty_class_for_ability(ability)
            attack_bonus = character.calculate_attack_bonus_for_ability(ability)
            file.write("<div class='spell-headline-group'>\n")
            file.write(
                "<div class='spell-stat-tile'>"
                "<span class='spell-stat-label'>Spellcasting Ability</span>"
                f"<span class='spell-stat-value spell-stat-ability'>{ability.value}</span>"
                "</div>\n"
            )
            file.write(
                "<div class='spell-stat-tile'>"
                "<span class='spell-stat-label'>Spell Save DC</span>"
                f"<span class='spell-stat-value'>{dc}</span>"
                "</div>\n"
            )
            file.write(
                "<div class='spell-stat-tile'>"
                "<span class='spell-stat-label'>Spell Attack Modifier</span>"
                f"<span class='spell-stat-value'>{attack_bonus:+}</span>"
                "</div>\n"
            )
            file.write("</div>\n")
        file.write("</div>\n")

        if include_probability_tables:
            file.write("<div class='spell-tables-secondary'>\n")
            file.write(
                "<p class='spell-tables-caption'>Save &amp; attack probability reference</p>\n"
            )
            self._write_save_dc_probabilities(character, file, casting_abilities)
            file.write("</div>\n")

    def _write_save_dc_probabilities(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        spellcasting_abilities: list[Ability],
    ):
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
            file.write(
                f"<tr><th class='dc-fail-dc-col'>DC {dc} ({abilities_label})</th>"
            )
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
        file.write(
            "<tr><th class='dc-fail-dc-col' colspan='2'>Spell Attack (Hit %)</th>"
        )
        for ac in ac_range:
            file.write(f"<th class='whit-ac'>AC {ac}</th>")
        file.write("</tr>\n")

        for attack_bonus in sorted(bonus_to_abilities.keys(), reverse=True):
            abilities_label = "/".join(bonus_to_abilities[attack_bonus])
            sign = "+" if attack_bonus >= 0 else ""
            bonus_label = f"{sign}{attack_bonus} ({abilities_label})"
            for i, (cond_label, condition) in enumerate(spell_attack_conditions):
                row_header = (
                    f"<th class='dc-fail-dc-col' rowspan='{len(spell_attack_conditions)}'>{bonus_label}</th>"
                    if i == 0
                    else ""
                )
                file.write(
                    f"<tr>{row_header}<th class='dc-fail-cond-col'>{cond_label}</th>"
                )
                for ac in ac_range:
                    prob = DamageCalculator.probability_of_success(
                        difficulty_class=ac,
                        die=Die.D20,
                        condition=condition,
                        bonus=attack_bonus,
                    )
                    pct = round(prob * 100)
                    pct_bucket = round(pct / 5) * 5
                    file.write(
                        f"<td class='whit-pct' data-pct='{pct_bucket}'>{pct}%</td>"
                    )
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
                    self._skill_modifier_breakdown(
                        character, skill, condition, reasons
                    ),
                    character.get_skill_ability(skill).value,
                ]
                Html.write_table_row(file, row, tr_class)

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
                    self._skill_modifier_breakdown(
                        character, best_skill, condition, reasons
                    ),
                    character.get_skill_ability(possible_skills[0]).value,
                ]
                Html.write_table_row(file, row, tr_class)

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
        followed by the roll condition and its reason, e.g. 'Disadvantage (Chain Mail)'.
        """
        terms: list[tuple[int, str]] = []
        proficiency_bonus = character.get_proficiency_bonus()
        if character.has_expertise_in_skill(skill):
            terms.append((proficiency_bonus, "proficiency"))
            terms.append((proficiency_bonus, "expertise"))
        elif character.is_proficient_in_skill(skill):
            terms.append((proficiency_bonus, "proficiency"))
        terms.extend(character.get_skill_bonus_sources(skill))

        breakdown = str(
            character.get_ability_modifier(character.get_skill_ability(skill))
        )
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
        self,
        character: CharacterStatBlock,
        file: TextIO,
        features: list[Feature],
        description_mode: Literal["table", "concise"] | None = None,
    ):
        text_features = [
            f
            for f in features
            if f.render_html_description(character, description_mode) is not None
        ]
        if not text_features:
            return

        file.write("<h2>Features</h2>\n")
        sorted_features = sorted(text_features, key=self._sort_features_key)

        file.write("<div class='features'>\n")
        for feature in sorted_features:
            feature.write_to_file(character, file, description_mode)
        file.write("</div>\n<br class='section-gap'>\n")

    def _write_weapons(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        include_probability_tables: bool = False,
    ):
        if not weapons:
            return

        self._apply_weapon_masteries(weapons, weapon_masteries)
        write_weapons_to_file(weapons, character, file, include_probability_tables)

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
            processed_body = Html.boxes_to_html(body)
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
            level_label = (
                f"Level {invocation.level}"
                if invocation.level
                else "No level requirement"
            )
            file.write("<div class='feature-card'>\n")
            file.write("<div class='feature-header'>\n")
            file.write(f"<span class='feature-name'>{invocation.name}</span>\n")
            file.write(f"<span class='feature-origin'>{level_label}</span>\n")
            file.write("</div>\n")
            file.write("<div class='feature-body'>\n")
            if invocation.prerequisite:
                file.write(
                    f"<p><strong>Prerequisite:</strong> {invocation.prerequisite}</p>\n"
                )
            processed_desc = Html.boxes_to_html(invocation.description)
            for para in processed_desc.split("\n"):
                if para.strip():
                    file.write(f"<p>{para.strip()}</p>\n")
            if invocation.source:
                file.write(f"<p class='inv-source'>{invocation.source}</p>\n")
            file.write("</div>\n")
            file.write("</div>\n")

        file.write("<br class='section-gap'>\n")

    def _write_pact_magic_slots(self, character: CharacterStatBlock, file: TextIO):
        if not character.pact_magic_slots:
            return
        file.write("<h2>Pact Magic Slots</h2>\n")
        Html.write_slot_table(
            character.pact_magic_slots, file, "Regained on: Short Rest or Long Rest"
        )
        file.write("<br class='section-gap'>\n")

    def _write_spell_slots(self, character: CharacterStatBlock, file: TextIO):
        if not character.spell_slots:
            return

        file.write("<h2>Spell Slots</h2>\n")
        Html.write_slot_table(
            character.get_spell_slots(), file, "Regained on: Long Rest"
        )
        file.write("<br class='section-gap'>\n")

    def _write_spells(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        spells: list[tuple[str, Ability, Optional[str]]],
        include_probability_tables: bool = False,
    ):
        if not spells:
            return

        file.write("<h2>Spells</h2>\n")
        casting_abilities = sorted(
            {ability for _, ability, _ in spells},
            key=lambda a: a.value,
        )
        self._write_spellcasting_headline(character, file, casting_abilities, include_probability_tables)
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
            for spell in group:
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
        carrying_capacity = character.get_carrying_capacity()
        file.write(
            f"<p><strong>Carrying Capacity ({carrying_capacity} slots):</strong></p>\n"
        )
        file.write("<table class='capacity-table'>\n")
        file.write("<tr>\n")
        for source, slots in character.get_carrying_capacity_sources():
            file.write(f"<th class='item-title'>{source} ({slots})</th>\n")
        file.write("</tr>\n")
        file.write("<tr>\n")
        for _source, slots in character.get_carrying_capacity_sources():
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
                    self._description_or_dash(armor.description_text),
                    armor.slots,
                )
                for armor in armors
            ]
            sections.append(("Armor", armor_rows))

        if weapons:
            weapon_rows = [
                (
                    f"{weapon.name}{self._worn_tag(weapon, 'Wielded', 'Not wielded')}",
                    self._description_or_dash(weapon.description_text),
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
                    item.description_text,
                    item.slots,
                )
                for item, quantity in sorted_items
            ]
            sections.append(("Other items", item_rows))

        for i, (title, rows) in enumerate(sections):
            if i > 0:
                file.write("<hr>")
            Html.write_slot_item_table(file, title, rows)

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

        headers = ["Tool", "Modifier", "Breakdown", "Ability", "Craft"]
        file.write("<table class='stat-table'>\n<tr>")
        for header in headers:
            file.write(f"<th>{header}</th>")
        file.write("</tr>\n")

        proficiency_bonus = character.get_proficiency_bonus()
        sorted_tool_proficiencies = sorted(tool_proficiencies, key=lambda x: x.name)
        for tool_proficiency in sorted_tool_proficiencies:
            ability_modifier = character.get_ability_modifier(tool_proficiency.ability)
            total = ability_modifier + proficiency_bonus
            breakdown = f"{ability_modifier} + {proficiency_bonus} (proficiency)"
            craft = (
                ", ".join(item.name for item in tool_proficiency.craftables)
                if tool_proficiency.craftables
                else "-"
            )
            row = [
                tool_proficiency.name,
                f"{total:+}",
                breakdown,
                tool_proficiency.ability.value,
                craft,
            ]
            Html.write_table_row(file, row, "st-proficient")

        file.write("</table>\n<br class='section-gap'>\n")

    def _get_css_style(self) -> str:
        return Html.render_style_block(
            Html.BASE_CHARACTER_SHEET_CSS,
            SPELL_CARD_CSS,
            WEAPON_CARD_CSS,
            WILDSHAPE_CARD_CSS,
            FEATURE_CARD_CSS,
        )

    def write_character_sheet(
        self,
        skill_config: Definitions.SkillConfig,
        character: CharacterStatBlock,
        output_path: str,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: set[WeaponProficiency],
        features: list[Feature],
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        fighting_styles: list[FightingStyle],
        invocations: list[str],
        spells: list[tuple[str, Ability, Optional[str]]],
        items: list[tuple[Items.Item, int]],
        tool_proficiencies: list[ToolProficiency],
        experience_points: int = 0,
        description_mode: Literal["table", "concise"] | None = None,
        include_probability_tables: bool = False,
    ):
        output_path_obj = pathlib.Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path_obj, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            file.write(
                f"<h1>{character.name} - Level {character.character_level} {character.base_class.value}</h1>\n"
            )
            self._write_general_info(character, file, experience_points)
            self._write_combat_stats(
                character, file, armors, armor_proficiencies, weapon_proficiencies
            )
            self._write_abilities(character, file)
            self._write_skills(character, file, skill_config)
            file.write("<div class='print-page-break'></div>\n")
            self._write_features(character, file, features, description_mode)
            self._write_weapons(character, file, weapons, weapon_masteries, include_probability_tables)
            self._write_fighting_styles(character, file, fighting_styles)
            self._write_invocations(character, file, invocations)
            self._write_pact_magic_slots(character, file)
            self._write_spell_slots(character, file)
            self._write_spells(character, file, spells, include_probability_tables)
            self._write_items(character, file, armors, weapons, items)
            self._write_tool_proficiencies(character, file, tool_proficiencies)
