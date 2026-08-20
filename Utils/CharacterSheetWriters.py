import pathlib
from typing import Literal, Optional, TextIO

import Core.Definitions as Definitions
from Builds.EquipmentHandler import EquipmentEntry
from CharacterContent.Features.CombatFeatures.FightingStyles import FightingStyle
from CharacterContent.Features.Core.BaseFeatures import FEATURE_CARD_CSS, Feature, parse_feature_level
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
from StatBlocks.SkillsStatBlock import SkillsStatBlock
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
    def _feature_level(feat: Feature) -> int:
        """Level parsed from origin text (e.g. 'Monk Level 3', 'Necromancy
        Wizard Level 6') for bucketing into per-level feature pages. Features
        without a parseable level (background, species, origin feats) are
        bucketed under level 1, where they were granted."""
        origin = getattr(feat, "origin", "") or ""
        return parse_feature_level(origin)

    @staticmethod
    def _spell_level(spell: tuple[str, Ability, Optional[str], int]) -> int:
        """Class-relative level a spell/cantrip was granted on, mirroring
        _feature_level - see CharacterSheetData._current_grant_level."""
        return spell[3]

    @staticmethod
    def _write_nav(file: TextIO, current_path: str, pages: list[tuple[str, str]]):
        depth = current_path.count("/")
        prefix = "../" * depth
        file.write("<div class='page-nav'>\n")
        for label, path in pages:
            if path == current_path:
                file.write(f"<span class='page-nav-current'>{label}</span>\n")
            else:
                file.write(f"<a href='{prefix}{path}'>{label}</a>\n")
        file.write("</div>\n")

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

    def _write_status_section(self, file: TextIO):
        """Write pen-fillable status trackers: Inspiration, Death Saves, Conditions.

        The sheet is meant to be printed and marked by hand, so these are plain
        empty boxes (matching the .pen-box used for spell slots elsewhere) rather
        than interactive <input type='checkbox'> elements.
        """
        file.write("<div class='status-section'>\n")

        file.write("<div class='status-row'>\n")

        file.write("<span class='status-chip status-chip-inspiration'>")
        file.write("<span class='pen-box'></span>Inspiration</span>\n")

        file.write("<span class='status-chip status-chip-deathsave'>")
        file.write("<span class='status-chip-label'>Death Save &mdash; Success</span>")
        file.write("<span class='pen-box'></span>" * 3)
        file.write("</span>\n")

        file.write("<span class='status-chip status-chip-deathsave'>")
        file.write("<span class='status-chip-label'>Failure</span>")
        file.write("<span class='pen-box'></span>" * 3)
        file.write("</span>\n")

        file.write("</div>\n")

        file.write("<div class='conditions-row'>\n")
        for condition in Definitions.Condition.list_sorted():
            file.write(
                f"<span class='status-chip'><span class='pen-box'></span>{condition.value}</span>\n"
            )
        file.write("</div>\n")

        file.write("</div>\n")

    @staticmethod
    def _stat_tile(label: str, value, sub: str = "", hero: bool = False) -> str:
        classes = "stat-tile stat-tile-hero" if hero else "stat-tile"
        sub_html = f"<span class='stat-tile-sub'>{sub}</span>" if sub else ""
        return (
            f"<div class='{classes}'>"
            f"<span class='stat-tile-label'>{label}</span>"
            f"<span class='stat-tile-value'>{value}</span>"
            f"{sub_html}"
            "</div>\n"
        )

    @staticmethod
    def _stat_tile_hp(label: str, value) -> str:
        """Render HP tile with format: blank/max_hp for player to fill in current HP."""
        return (
            f"<div class='stat-tile stat-tile-hero'>"
            f"<span class='stat-tile-label'>{label}</span>"
            f"<span class='stat-tile-value'>"
            f"<span class='hp-blank'></span>"
            f"<span class='hp-slash'>/</span>{value}"
            f"</span>"
            "</div>\n"
        )

    def _write_overview(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: set[WeaponProficiency],
    ):
        """Character overview: large tiles for the stats checked constantly
        in play (HP above all, then AC/Initiative/Speed/Prof. Bonus), with
        everything else — class, proficiencies, languages, senses — as
        compact reference chips below. The player already knows their class;
        they don't already know today's HP total.
        """
        file.write("<h2>Overview</h2>\n")
        file.write("<div class='overview-section'>\n")

        ac = character.calculate_armor_class()
        ac_sub = f"w/o Shield {ac - 2}" if self._has_shield_armor(armors) else ""

        initiative_sub = ""
        if character.initiative_roll_condition in (
            Definitions.DiceRollCondition.ADVANTAGE,
            Definitions.DiceRollCondition.DISADVANTAGE,
        ):
            initiative_sub = character.initiative_roll_condition.value

        file.write("<div class='overview-tiles'>\n")
        file.write(
            self._stat_tile_hp("HP", character.calculate_hit_points())
        )
        file.write(self._stat_tile("AC", ac, sub=ac_sub))
        file.write(
            self._stat_tile(
                "Initiative", f"{character.initiative:+}", sub=initiative_sub
            )
        )
        file.write(self._stat_tile("Speed", f"{character.combat.speed} ft"))
        file.write(
            self._stat_tile("Prof. Bonus", f"{character.get_proficiency_bonus():+}")
        )
        file.write("</div>\n")

        languages = ", ".join(
            language.value
            for language in sorted(character.languages, key=lambda lang: lang.value)
        )
        senses = ", ".join(
            f"{sense.value} {character.senses[sense]} ft."
            for sense in sorted(character.senses, key=lambda s: s.value)
        )

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

        details = [
            ("Class", self._format_class_level_history(character)),
            ("Subclass", character.character_subclass),
            ("Size", character.combat.size.value),
            ("Armor Prof.", ", ".join(sorted(a.value for a in armor_proficiencies))),
            (
                "Weapon Prof.",
                ", ".join(sorted(wp.value for wp in weapon_proficiencies)),
            ),
            ("Languages", languages),
            ("Senses", senses),
            ("Resistances / Immunities", resistances_and_immunities),
        ]

        file.write("<div class='overview-details'>\n")
        for label, value in details:
            if not value:
                continue
            file.write(
                f"<span class='overview-detail'><span class='od-label'>{label}</span>{value}</span>\n"
            )
        # Left blank so the player can fill it in by hand.
        file.write(
            "<span class='overview-detail'><span class='od-label'>XP</span>"
            "<span class='xp-blank'></span></span>\n"
        )
        file.write("</div>\n")

        file.write("</div>\n<br class='section-gap'>\n")

    def _write_abilities(self, character: CharacterStatBlock, file: TextIO):
        """Ability tiles, not a table: the modifier is what gets added to
        rolls constantly, so it's the large number on each tile. The raw
        score is secondary (you rarely reference it directly), and Save —
        relevant on any saving throw — is a small footer line rather than
        its own column.
        """
        proficiency_bonus = character.get_proficiency_bonus()

        file.write("<div class='ability-tiles'>\n")

        for ability in Ability:
            ability_mod = character.get_ability_modifier(ability)
            proficient = character.is_proficient_in_saving_throw(ability)

            save_total = ability_mod + (proficiency_bonus if proficient else 0)
            saving_throw_text = f"{save_total:+}"
            if character.has_advantage_in_saving_throw(ability):
                saving_throw_text += " (Adv)"

            tile_class = "ability-tile st-proficient" if proficient else "ability-tile"
            file.write(f"<div class='{tile_class}'>\n")
            file.write(
                f"<span class='ability-tile-name'>{ability.short_name}</span>\n"
            )
            file.write(
                f"<span class='ability-tile-mod'>{ability_mod:+}</span>\n"
            )
            file.write(
                f"<span class='ability-tile-score'>{character.get_ability_score(ability)}</span>\n"
            )
            file.write(
                f"<span class='ability-tile-extra'>Save {saving_throw_text}</span>\n"
            )
            file.write("</div>\n")

        file.write("</div>\n")

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
        """Skill list, not a table: the modifier is bold and right-aligned
        since it's the number checked during play, while the arithmetic
        breakdown is a small muted line underneath for reference rather than
        its own column. Flows into two CSS columns so eighteen skills don't
        dominate the page height.
        """
        file.write("<div class='skills-columns'>\n")

        if skill_config == Definitions.SkillConfig.DEFAULT:
            for skill in Definitions.Skill.list_sorted():
                proficient = character.is_proficient_in_skill(skill)
                has_expertise = character.has_expertise_in_skill(skill)
                condition = character.get_skill_roll_condition(skill)
                reasons = character.get_skill_roll_condition_reasons(skill)
                self._write_skill_entry(
                    file,
                    name=skill.value,
                    ability=character.get_skill_ability(skill),
                    modifier_text=self._modifier_with_condition(
                        character.get_skill_modifier(skill), condition
                    ),
                    breakdown=self._skill_modifier_breakdown(
                        character, skill, condition, reasons
                    ),
                    proficient=proficient,
                    has_expertise=has_expertise,
                )

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

                # Breakdown follows the default skill that yields the best modifier
                best_skill = max(possible_skills, key=character.get_skill_modifier)
                condition = self._resolve_homebrew_roll_condition(roll_conditions)
                reasons = [
                    reason
                    for s in possible_skills
                    if character.get_skill_roll_condition(s) == condition
                    for reason in character.get_skill_roll_condition_reasons(s)
                ]
                self._write_skill_entry(
                    file,
                    name=skill.value,
                    ability=character.get_skill_ability(possible_skills[0]),
                    modifier_text=self._modifier_with_condition(
                        character.get_skill_modifier(best_skill), condition
                    ),
                    breakdown=self._skill_modifier_breakdown(
                        character, best_skill, condition, reasons
                    ),
                    proficient=proficient,
                    has_expertise=has_expertise,
                )

        file.write("</div>\n")

    @staticmethod
    def _write_skill_entry(
        file: TextIO,
        name: str,
        ability: Ability,
        modifier_text: str,
        breakdown: str,
        proficient: bool,
        has_expertise: bool,
    ) -> None:
        entry_class = "skill-entry"
        if has_expertise:
            entry_class += " st-expertise"
        elif proficient:
            entry_class += " st-proficient"

        expertise_badge = (
            "<span class='skill-expertise'>EXP</span>" if has_expertise else ""
        )

        file.write(f"<div class='{entry_class}'>\n")
        file.write("<div class='skill-entry-top'>\n")
        file.write(
            f"<span class='skill-name'>{name}"
            f"<span class='skill-ability-tag'>{ability.short_name}</span>"
            f"{expertise_badge}</span>\n"
        )
        file.write(f"<span class='skill-mod'>{modifier_text}</span>\n")
        file.write("</div>\n")
        file.write(f"<div class='skill-breakdown'>{breakdown}</div>\n")
        file.write("</div>\n")

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

    @staticmethod
    def _spell_prep_checkbox_class(character: CharacterStatBlock) -> bool:
        """Whether spell cards for this character should show a
        preparation checkbox (true for classes that prepare spells daily
        from a known list, rather than simply knowing a fixed set)."""
        prepared_caster_classes = {
            Definitions.CharacterClass.CLERIC,
            Definitions.CharacterClass.DRUID,
            Definitions.CharacterClass.WIZARD,
            Definitions.CharacterClass.PALADIN,
            Definitions.CharacterClass.ARTIFICER,
        }
        return character.base_class in prepared_caster_classes

    def _write_spell_cards(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        spells: list[tuple[str, Ability, Optional[str], int]],
    ):
        """Write the '<div class='spells'>' block of individual spell cards
        (grouped by spell level with a header per group) for the given
        subset of spells. Does not write the spellcasting headline or the
        surrounding <h2> - callers are responsible for those."""
        if not spells:
            return

        file.write("<div class='spells'>\n")

        created_spells = [
            SpellFactory.create(spell_name, spell_casting_ability, additional_ruling)
            for spell_name, spell_casting_ability, additional_ruling, _grant_level in spells
        ]
        sorted_spells = sorted(created_spells, key=lambda s: (s.level, s.name))

        show_prep_checkbox = self._spell_prep_checkbox_class(character)

        # Group by level and emit a level header before each group
        from itertools import groupby

        for level, group in groupby(sorted_spells, key=lambda s: s.level):
            level_label = "Cantrips" if level == 0 else f"Level {level} Spells"
            file.write(f"<h3 class='spell-level-header'>{level_label}</h3>\n")
            for spell in group:
                spell.write_to_file(file, show_preparation_checkbox=show_prep_checkbox)

        file.write("</div>\n")

    def _write_spells(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        spells: list[tuple[str, Ability, Optional[str], int]],
        include_probability_tables: bool = False,
    ):
        if not spells:
            return

        file.write("<h2>Spells</h2>\n")
        casting_abilities = sorted(
            {ability for _, ability, _, _ in spells},
            key=lambda a: a.value,
        )
        self._write_spellcasting_headline(character, file, casting_abilities, include_probability_tables)
        self._write_spell_cards(character, file, spells)
        file.write("<br class='section-gap'>\n")

    @staticmethod
    def _item_type_rarity_value(item: Items.Item, quantity: int = 1) -> tuple[str, str, str]:
        value = item.get_value_display()
        sell_value = item.get_sell_value_display()
        prefix = f"{quantity} x " if quantity != 1 else ""
        if value and sell_value:
            buy_amount = value.removesuffix(" GP")
            sell_amount = sell_value.removesuffix(" GP")
            price = f"{prefix}{buy_amount}/{sell_amount} GP"
        else:
            price = "-"
        return (
            item.category.value.title(),
            item.rarity.value.title(),
            price,
        )

    @staticmethod
    def _format_gold(value: float) -> str:
        return f"{int(value)} GP" if value == int(value) else f"{value:g} GP"

    def _acquisition_tag(
        self, item: Items.Item, entry: EquipmentEntry, is_starting_equipment: bool
    ) -> str:
        """Chip marking an adventuring-gear item as bought (with the amount
        paid) or found; omitted for Starting Equipment, where the concept
        doesn't apply - that gear's cost is already reflected in Starting
        Gold, not tracked per item."""
        if is_starting_equipment:
            return ""
        for purchased_item, price in entry.purchases:
            if purchased_item is item:
                price_display = self._format_gold(price)
                return f" <span class='wtag wtag-worn'>Paid: {price_display}</span>"
        return " <span class='wtag wtag-not-worn'>Found</span>"

    def _build_item_sections(
        self, entry: EquipmentEntry, is_starting_equipment: bool
    ) -> list[tuple[str, list[tuple[str, str, int, str, str, str]]]]:
        """(title, [(label, description, slots, type, rarity, price), ...])
        per non-empty Armor/Weapons/Other items table, in the same
        slot-table format. Rows are sorted by item type."""
        sections = []
        if entry.armors:
            sorted_armors = sorted(entry.armors, key=lambda a: (a.category.value, a.name))
            armor_rows = [
                (
                    f"{armor.name}{self._worn_tag(armor)}"
                    f"{self._acquisition_tag(armor, entry, is_starting_equipment)}",
                    self._description_or_dash(armor.description_text),
                    armor.slots,
                    *self._item_type_rarity_value(armor),
                )
                for armor in sorted_armors
            ]
            sections.append(("Armor", armor_rows))

        if entry.weapons:
            sorted_weapons = sorted(
                (w for w in entry.weapons if not isinstance(w, UnarmedStrike)),
                key=lambda w: (w.category.value, w.name),
            )
            weapon_rows = [
                (
                    f"{weapon.name}{self._worn_tag(weapon, 'Wielded', 'Not wielded')}"
                    f"{self._acquisition_tag(weapon, entry, is_starting_equipment)}",
                    self._description_or_dash(weapon.description_text),
                    weapon.slots,
                    *self._item_type_rarity_value(weapon),
                )
                for weapon in sorted_weapons
            ]
            if weapon_rows:
                sections.append(("Weapons", weapon_rows))

        if entry.items:
            sorted_items = sorted(entry.items, key=lambda x: (x[0].category.value, x[0].name))
            item_rows = [
                (
                    f"{item.name} ({quantity}){self._worn_tag(item)}"
                    f"{self._acquisition_tag(item, entry, is_starting_equipment)}",
                    item.description_text,
                    item.slots,
                    *self._item_type_rarity_value(item, quantity),
                )
                for item, quantity in sorted_items
            ]
            sections.append(("Other items", item_rows))

        return sections

    def _write_items(
        self,
        character: CharacterStatBlock,
        file: TextIO,
        equipment_entries: list[EquipmentEntry],
        starting_equipment_entry: Optional[EquipmentEntry],
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        include_probability_tables: bool = False,
    ):
        non_empty_entries = [
            entry
            for entry in equipment_entries
            if entry.armors or entry.weapons or entry.items or entry.gold
        ]
        if not non_empty_entries and not weapons:
            return

        file.write("<h2>Items</h2>\n")

        # Attack-card weapons are the first subsection within Items, ahead
        # of the wallet/carrying-capacity row and the equipment entries.
        self._write_weapons(
            character, file, weapons, weapon_masteries, include_probability_tables
        )

        if not non_empty_entries:
            file.write("<br class='section-gap'>\n")
            return

        # Wallet pinned to the left, carrying capacity (total + a compact
        # per-source pip breakdown) pinned to the right - keeps the row
        # tidy instead of one flat chip list wrapping unevenly.
        carrying_capacity = character.get_carrying_capacity()
        file.write("<div class='wallet-carry-row'>\n")
        file.write("<div class='wallet-block'>\n")
        if character.current_gold is not None:
            file.write(
                f"<span class='overview-detail'><span class='od-label'>Starting Gold</span>"
                f"{self._format_gold(character.current_gold)}</span>\n"
            )
        file.write(
            "<span class='overview-detail'><span class='od-label'>Current Gold</span>"
            "<span class='xp-blank'></span></span>\n"
        )
        file.write("</div>\n")
        file.write("<div class='carrying-block'>\n")
        file.write(
            f"<span class='overview-detail'><span class='od-label'>Carrying Capacity</span>"
            f"{carrying_capacity} slots</span>\n"
        )
        for source, slots in character.get_carrying_capacity_sources():
            slot_boxes = "<span class='slot-box'></span>" * slots
            file.write(
                f"<span class='carrying-source'><span class='cs-label'>{source} ({slots})</span>"
                f"<span class='slot-box-group'>{slot_boxes}</span></span>\n"
            )
        file.write("</div>\n")
        file.write("</div>\n")

        for entry in non_empty_entries:
            is_starting_equipment = entry is starting_equipment_entry
            file.write(f"<h3>{entry.label}</h3>\n")
            if entry.gold:
                sign = "+" if entry.gold > 0 else "-"
                file.write(
                    "<div class='overview-details'>\n"
                    f"<span class='overview-detail'><span class='od-label'>Gold</span>"
                    f"{sign}{self._format_gold(abs(entry.gold))}</span>\n"
                    "</div>\n"
                )

            sections = self._build_item_sections(entry, is_starting_equipment)
            for i, (title, rows) in enumerate(sections):
                if i > 0:
                    file.write("<hr>")
                Html.write_item_cards(file, title, rows)

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
        file.write("<div class='tool-list'>\n")

        proficiency_bonus = character.get_proficiency_bonus()
        sorted_tool_proficiencies = sorted(tool_proficiencies, key=lambda x: x.name)
        for tool_proficiency in sorted_tool_proficiencies:
            ability_modifier = character.get_ability_modifier(tool_proficiency.ability)
            total = ability_modifier + proficiency_bonus
            breakdown = f"{ability_modifier} + {proficiency_bonus} (proficiency)"
            craft = (
                ", ".join(item.name for item in tool_proficiency.craftables)
                if tool_proficiency.craftables
                else None
            )

            file.write("<div class='tool-entry st-proficient'>\n")
            file.write("<div class='tool-entry-top'>\n")
            file.write(
                f"<span class='tool-name'>{tool_proficiency.name}"
                f"<span class='skill-ability-tag'>{tool_proficiency.ability.short_name}</span></span>\n"
            )
            file.write(f"<span class='tool-mod'>{total:+}</span>\n")
            file.write("</div>\n")
            file.write(f"<div class='skill-breakdown'>{breakdown}</div>\n")
            if craft:
                file.write(f"<div class='tool-craft'><span class='glabel'>Craft</span> {craft}</div>\n")
            file.write("</div>\n")

        file.write("</div>\n<br class='section-gap'>\n")

    def _get_css_style(self) -> str:
        return Html.render_style_block(
            Html.BASE_CHARACTER_SHEET_CSS,
            SPELL_CARD_CSS,
            WEAPON_CARD_CSS,
            WILDSHAPE_CARD_CSS,
            FEATURE_CARD_CSS,
        )

    def write_character_sheet_pages(
        self,
        skill_config: Definitions.SkillConfig,
        character: CharacterStatBlock,
        output_folder: str,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: set[WeaponProficiency],
        features: list[Feature],
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        fighting_styles: list[FightingStyle],
        invocations: list[str],
        spells: list[tuple[str, Ability, Optional[str], int]],
        equipment_entries: list[EquipmentEntry],
        starting_equipment_entry: Optional[EquipmentEntry],
        tool_proficiencies: list[ToolProficiency],
        experience_points: int = 0,
        description_mode: Literal["table", "concise"] | None = None,
        include_probability_tables: bool = False,
    ):
        output_folder_obj = pathlib.Path(output_folder)
        output_folder_obj.mkdir(parents=True, exist_ok=True)
        (output_folder_obj / "features").mkdir(parents=True, exist_ok=True)

        text_features = [
            f
            for f in features
            if f.render_html_description(character, description_mode) is not None
        ]
        features_by_level: dict[int, list[Feature]] = {}
        for feature in text_features:
            features_by_level.setdefault(self._feature_level(feature), []).append(
                feature
            )

        spells_by_level: dict[int, list[tuple[str, Ability, Optional[str], int]]] = {}
        for spell in spells:
            spells_by_level.setdefault(self._spell_level(spell), []).append(spell)

        # Build a bucket of extensions (feature enhancements) that appear on their
        # own level pages as standalone cards. Skip extensions whose level <= parent
        # level (already nested on the parent's page via write_to_file's max_level filtering).
        extensions_by_level: dict[int, list[tuple[Feature, Feature]]] = {}
        for feature in features:  # Iterate full list, not just text_features
            parent_level = self._feature_level(feature)
            for extension in feature.extensions:
                ext_level = self._feature_level(extension)
                if ext_level <= parent_level:
                    continue  # Already shown nested on the parent's page
                if extension.render_html_description(character, description_mode) is None:
                    continue
                extensions_by_level.setdefault(ext_level, []).append((feature, extension))

        # A level page is needed for any level that grants a displayed
        # feature OR a spell/cantrip - a level that only grants spells
        # (no feature with a rendered description) would otherwise be
        # missed entirely.
        level_page_levels = sorted(set(features_by_level) | set(spells_by_level) | set(extensions_by_level))

        has_fighting_styles_page = bool(fighting_styles)
        non_empty_equipment_entries = [
            entry
            for entry in equipment_entries
            if entry.armors or entry.weapons or entry.items or entry.gold
        ]
        has_items_page = (
            bool(non_empty_equipment_entries) or bool(tool_proficiencies) or bool(weapons)
        )

        pages: list[tuple[str, str]] = [
            ("Character", "character.html"),
            ("Full Sheet", "full_character_sheet.html"),
        ]
        for level in level_page_levels:
            pages.append(
                (f"Level {level} Features", f"features/level_{level:02d}.html")
            )
        if has_fighting_styles_page:
            pages.append(("Fighting Styles", "fighting_styles.html"))
        if has_items_page:
            pages.append(("Items", "items.html"))

        self._write_character_page(
            output_folder_obj / "character.html",
            "character.html",
            pages,
            character,
            armors,
            armor_proficiencies,
            weapon_proficiencies,
            skill_config,
            invocations,
            spells,
            include_probability_tables,
        )

        self._write_full_page(
            output_folder_obj / "full_character_sheet.html",
            "full_character_sheet.html",
            pages,
            character,
            armors,
            armor_proficiencies,
            weapon_proficiencies,
            skill_config,
            text_features,
            description_mode,
            weapons,
            weapon_masteries,
            fighting_styles,
            invocations,
            spells,
            equipment_entries,
            starting_equipment_entry,
            tool_proficiencies,
            include_probability_tables,
        )

        for level in level_page_levels:
            page_path = f"features/level_{level:02d}.html"
            sorted_level_features = sorted(
                features_by_level.get(level, []), key=lambda f: getattr(f, "name", "")
            )
            level_spells = spells_by_level.get(level, [])
            level_extensions = extensions_by_level.get(level, [])
            self._write_features_page(
                output_folder_obj / page_path,
                page_path,
                pages,
                character,
                level,
                sorted_level_features,
                description_mode,
                level_spells,
                level_extensions,
            )

        if has_fighting_styles_page:
            self._write_fighting_styles_page(
                output_folder_obj / "fighting_styles.html",
                "fighting_styles.html",
                pages,
                character,
                fighting_styles,
            )

        if has_items_page:
            self._write_items_page(
                output_folder_obj / "items.html",
                "items.html",
                pages,
                character,
                equipment_entries,
                starting_equipment_entry,
                tool_proficiencies,
                weapons,
                weapon_masteries,
                include_probability_tables,
            )

    def _write_character_page(
        self,
        path: pathlib.Path,
        page_path: str,
        pages: list[tuple[str, str]],
        character: CharacterStatBlock,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: set[WeaponProficiency],
        skill_config: Definitions.SkillConfig,
        invocations: list[str],
        spells: list[tuple[str, Ability, Optional[str], int]],
        include_probability_tables: bool,
    ):
        with open(path, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(
                f"<h1>{character.name} - Level {character.character_level} "
                f"{character.base_class.value}</h1>\n"
            )
            self._write_status_section(file)
            self._write_overview(
                character, file, armors, armor_proficiencies, weapon_proficiencies
            )
            file.write("<h2>Abilities and Skills</h2>\n")
            file.write("<div class='section-row'>\n")
            file.write("<div class='section-col section-col-abilities'>\n")
            self._write_abilities(character, file)
            if spells:
                casting_abilities = sorted(
                    {ability for _, ability, _, _ in spells},
                    key=lambda a: a.value,
                )
                file.write("<br class='section-gap'>\n")
                self._write_spellcasting_headline(
                    character, file, casting_abilities, include_probability_tables
                )
            file.write("</div>\n")
            file.write("<div class='section-col section-col-skills'>\n")
            self._write_skills(character, file, skill_config)
            file.write("</div>\n")
            file.write("</div>\n")

            self._write_invocations(character, file, invocations)
            self._write_pact_magic_slots(character, file)
            self._write_spell_slots(character, file)

    def write_blank_character_template(self, output_folder: str):
        """Write a class-agnostic, unfilled version of character.html - the
        Overview/Abilities/Skills page - for a player who wants to print a
        blank sheet and fill it in by hand rather than generate one from a
        build. No CharacterStatBlock involved: every value is a blank
        fill-in line (see .blank-fill in Html.py) instead of computed data,
        and build-specific content (features, spellcasting, equipment) is
        skipped entirely since none of it applies until a character exists.
        """
        output_folder_obj = pathlib.Path(output_folder)
        output_folder_obj.mkdir(parents=True, exist_ok=True)
        path = output_folder_obj / "character.html"

        blank_skills = SkillsStatBlock()
        blank_sm = "<span class='blank-fill blank-fill-sm'></span>"

        with open(path, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            file.write(
                "<h1><span class='blank-fill blank-fill-xl'></span> - Level "
                "<span class='blank-fill blank-fill-sm'></span> "
                "<span class='blank-fill blank-fill-lg'></span></h1>\n"
            )
            self._write_status_section(file)

            # ── Overview ─────────────────────────────────────────────────
            file.write("<h2>Overview</h2>\n")
            file.write("<div class='overview-section'>\n")

            file.write("<div class='overview-tiles'>\n")
            file.write(self._stat_tile_hp("HP", blank_sm))
            file.write(self._stat_tile("AC", blank_sm))
            file.write(self._stat_tile("Initiative", blank_sm))
            file.write(self._stat_tile("Speed", f"{blank_sm} ft"))
            file.write(self._stat_tile("Prof. Bonus", blank_sm))
            file.write("</div>\n")

            file.write("<div class='overview-details'>\n")
            for label in (
                "Class",
                "Subclass",
                "Size",
                "Armor Prof.",
                "Weapon Prof.",
                "Languages",
                "Senses",
                "Resistances / Immunities",
            ):
                file.write(
                    f"<span class='overview-detail'><span class='od-label'>{label}</span>"
                    f"<span class='blank-fill blank-fill-lg'></span></span>\n"
                )
            file.write(
                "<span class='overview-detail'><span class='od-label'>XP</span>"
                "<span class='xp-blank'></span></span>\n"
            )
            file.write("</div>\n")

            file.write("</div>\n<br class='section-gap'>\n")

            # ── Abilities and Skills ─────────────────────────────────────
            file.write("<h2>Abilities and Skills</h2>\n")
            file.write("<div class='section-row'>\n")

            file.write("<div class='section-col section-col-abilities'>\n")
            file.write("<div class='ability-tiles'>\n")
            for ability in Ability:
                file.write("<div class='ability-tile'>\n")
                file.write(
                    f"<span class='ability-tile-name'>{ability.short_name}</span>\n"
                )
                file.write(f"<span class='ability-tile-mod'>{blank_sm}</span>\n")
                file.write(f"<span class='ability-tile-score'>{blank_sm}</span>\n")
                file.write(f"<span class='ability-tile-extra'>Save {blank_sm}</span>\n")
                file.write("</div>\n")
            file.write("</div>\n")

            # Spellcasting headline, placed with the abilities like on a
            # real character.html - shown generically in case the player
            # ends up a spellcaster, not tied to any specific ability.
            file.write("<br class='section-gap'>\n")
            file.write("<div class='spell-headline'>\n")
            file.write("<div class='spell-headline-group'>\n")
            file.write(
                "<div class='spell-stat-tile'>"
                "<span class='spell-stat-label'>Spellcasting Ability</span>"
                f"<span class='spell-stat-value spell-stat-ability'>{blank_sm}</span>"
                "</div>\n"
            )
            file.write(
                "<div class='spell-stat-tile'>"
                "<span class='spell-stat-label'>Spell Save DC</span>"
                f"<span class='spell-stat-value'>{blank_sm}</span>"
                "</div>\n"
            )
            file.write(
                "<div class='spell-stat-tile'>"
                "<span class='spell-stat-label'>Spell Attack Modifier</span>"
                f"<span class='spell-stat-value'>{blank_sm}</span>"
                "</div>\n"
            )
            file.write("</div>\n")
            file.write("</div>\n")

            file.write("</div>\n")

            file.write("<div class='section-col section-col-skills'>\n")
            file.write("<div class='skills-columns'>\n")
            for skill in Definitions.Skill.list_sorted():
                ability = blank_skills.get_skill_ability(skill)
                file.write("<div class='skill-entry'>\n")
                file.write("<div class='skill-entry-top'>\n")
                file.write(
                    f"<span class='skill-name'>{skill.value}"
                    f"<span class='skill-ability-tag'>{ability.short_name}</span></span>\n"
                )
                file.write(f"<span class='skill-mod'>{blank_sm}</span>\n")
                file.write("</div>\n")
                file.write(
                    "<div class='skill-breakdown'>"
                    "<span class='pen-box'></span> Proficient &nbsp; "
                    "<span class='pen-box'></span> Expertise"
                    "</div>\n"
                )
                file.write("</div>\n")
            file.write("</div>\n")
            file.write("</div>\n")

            file.write("</div>\n")

            # Blank Spell Slots table, levels 1-9 with a generic 4 boxes
            # each - shown in case the player ends up a spellcaster, since
            # real slot counts depend on class/level neither of which a
            # blank template has.
            file.write("<h2>Spell Slots</h2>\n")
            Html.write_slot_table(
                {level: 4 for level in range(1, 10)}, file, "Regained on: Long Rest"
            )

    def _write_full_page(
        self,
        path: pathlib.Path,
        page_path: str,
        pages: list[tuple[str, str]],
        character: CharacterStatBlock,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: set[WeaponProficiency],
        skill_config: Definitions.SkillConfig,
        text_features: list[Feature],
        description_mode: Literal["table", "concise"] | None,
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        fighting_styles: list[FightingStyle],
        invocations: list[str],
        spells: list[tuple[str, Ability, Optional[str], int]],
        equipment_entries: list[EquipmentEntry],
        starting_equipment_entry: Optional[EquipmentEntry],
        tool_proficiencies: list[ToolProficiency],
        include_probability_tables: bool,
    ):
        """Aggregated single-file sheet with every section, same content as
        the split pages combined — kept alongside them so the player can
        still print (or view) the whole character at once when they want to,
        while the split pages remain the ones that don't need reprinting on
        every level-up."""
        with open(path, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(
                f"<h1>{character.name} - Level {character.character_level} "
                f"{character.base_class.value}</h1>\n"
            )
            self._write_status_section(file)
            self._write_overview(
                character, file, armors, armor_proficiencies, weapon_proficiencies
            )
            file.write("<h2>Abilities and Skills</h2>\n")
            file.write("<div class='section-row'>\n")
            file.write("<div class='section-col section-col-abilities'>\n")
            self._write_abilities(character, file)
            file.write("</div>\n")
            file.write("<div class='section-col section-col-skills'>\n")
            self._write_skills(character, file, skill_config)
            file.write("</div>\n")
            file.write("</div>\n")
            file.write("<div class='print-page-break'></div>\n")

            if text_features:
                file.write("<h2>Features</h2>\n")
                sorted_features = sorted(text_features, key=self._sort_features_key)
                file.write("<div class='features'>\n")
                for feature in sorted_features:
                    feature.write_to_file(character, file, description_mode)
                file.write("</div>\n<br class='section-gap'>\n")

            self._write_fighting_styles(character, file, fighting_styles)
            self._write_invocations(character, file, invocations)
            self._write_pact_magic_slots(character, file)
            self._write_spell_slots(character, file)
            self._write_spells(character, file, spells, include_probability_tables)
            self._write_items(
                character,
                file,
                equipment_entries,
                starting_equipment_entry,
                weapons,
                weapon_masteries,
                include_probability_tables,
            )
            self._write_tool_proficiencies(character, file, tool_proficiencies)

    def _write_features_page(
        self,
        path: pathlib.Path,
        page_path: str,
        pages: list[tuple[str, str]],
        character: CharacterStatBlock,
        level: int,
        level_features: list[Feature],
        description_mode: Literal["table", "concise"] | None,
        level_spells: list[tuple[str, Ability, Optional[str], int]],
        level_extensions: list[tuple[Feature, Feature]] | None = None,
    ):
        if level_extensions is None:
            level_extensions = []

        with open(path, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(f"<h1>{character.name} - Level {level} Features</h1>\n")
            file.write("<div class='features'>\n")
            for feature in level_features:
                feature.write_to_file(character, file, description_mode, max_level=level)
            for parent, extension in sorted(level_extensions, key=lambda pe: pe[1].name):
                extension.write_extension_card_to_file(character, file, parent.name, description_mode)
            file.write("</div>\n")

            if level_spells:
                file.write("<h2>Spells Gained</h2>\n")
                self._write_spell_cards(character, file, level_spells)
                file.write("<br class='section-gap'>\n")

    def _write_fighting_styles_page(
        self,
        path: pathlib.Path,
        page_path: str,
        pages: list[tuple[str, str]],
        character: CharacterStatBlock,
        fighting_styles: list[FightingStyle],
    ):
        with open(path, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(f"<h1>{character.name} - Fighting Styles</h1>\n")
            self._write_fighting_styles(character, file, fighting_styles)

    def _write_items_page(
        self,
        path: pathlib.Path,
        page_path: str,
        pages: list[tuple[str, str]],
        character: CharacterStatBlock,
        equipment_entries: list[EquipmentEntry],
        starting_equipment_entry: Optional[EquipmentEntry],
        tool_proficiencies: list[ToolProficiency],
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        include_probability_tables: bool,
    ):
        with open(path, "w", encoding="utf-8") as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(f"<h1>{character.name} - Items</h1>\n")
            self._write_items(
                character,
                file,
                equipment_entries,
                starting_equipment_entry,
                weapons,
                weapon_masteries,
                include_probability_tables,
            )
            self._write_tool_proficiencies(character, file, tool_proficiencies)

    def write_item_sheet(
        self,
        title: str,
        output_path: str,
        armors: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[AbstractWeapon]] = None,
        items: Optional[list[tuple[Items.Item, int]]] = None,
    ):
        """Generate a standalone item sheet HTML page showing a fixed set of
        items (armor/weapons/other) without character context or mechanics."""
        if armors is None:
            armors = []
        if weapons is None:
            weapons = []
        if items is None:
            items = []

        entry = EquipmentEntry(label=title, armors=armors, weapons=weapons, items=items)

        output_file = pathlib.Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as file:
            file.write(Html.render_style_block(Html.BASE_CHARACTER_SHEET_CSS))
            file.write(f"<h1>{title}</h1>\n")

            sections = self._build_item_sections(entry, is_starting_equipment=True)
            for i, (section_title, rows) in enumerate(sections):
                if i > 0:
                    file.write("<hr>")
                Html.write_item_cards(file, section_title, rows)
