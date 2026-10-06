import html
import pathlib
from enum import Enum
from typing import Collection, Literal, Optional, Sequence, TextIO, TypeVar

import Core.Definitions as Definitions
from Model.Inventory import EquipmentEntry
from CharacterContent.Features.CombatFeatures.FightingStyles import FightingStyle
from CharacterContent.Features.Core.BaseFeatures import FEATURE_CARD_CSS, Feature
from CharacterContent.Invocations.InvocationFactory import InvocationFactory
from CharacterContent.Items import Armor, Items
from CharacterContent.Items.Armor.Writer import ARMOR_CARD_CSS, write_armors_to_file
from CharacterContent.Items.Weapons import (
    AbstractWeapon,
    UnarmedStrike,
    WeaponProficiency,
    write_weapons_reference_to_file,
    write_weapons_to_file,
)
from CharacterContent.Items.Weapons.Writer import WEAPON_CARD_CSS
from CharacterContent.Spells.SpellFactory import SpellFactory
from CharacterContent.Spells.SpellFactory.Writer import (
    SPELL_CARD_CSS,
    write_spell_to_file,
)
from CharacterContent.ToolProficiencies.Proficiencies import ToolProficiency
from Core.Definitions import Ability, DiceRollCondition, Die
from Model.Character import Character
from Model.Records.SourcedValue import SourcedValue
from Model.Spells import SpellGrant
from Model.Skills import Skills
from Utils import DamageCalculator, Html
from Utils.CreatureStatBlocks import WILDSHAPE_CARD_CSS

T = TypeVar("T")


def _as(value: object, kind: type[T]) -> T:
    """`value`, checked to be a `kind`. The Model holds features and gear
    only through the Protocols in Model/Sources.py, but the sheet renders
    the concrete classes, so this is where it gets them back. Anything else
    is a bug, hence raising rather than skipping."""
    if not isinstance(value, kind):
        raise TypeError(f"Expected a {kind.__name__}, got {type(value).__name__}")
    return value


def get_output_folder(
    data: "Character",
    description_mode: Literal["table", "concise"] | None = None,
) -> str:
    if data.character_name is None:
        raise ValueError("Character name must be set to generate file path.")
    if data.character_subclass is None:
        raise ValueError("Character subclass must be set to generate file path.")
    if data.base_class is None:
        raise ValueError("Base class must be set to generate file path.")
    example_prefix = "example_" if data.is_example else ""
    mode_suffix = f"_{description_mode}" if description_mode else ""
    return (
        f"Output/{example_prefix}{data.base_class.lower()}_"
        f"{data.character_subclass.lower().replace(' / ', '_')}_"
        f"{_slugify_name(data.character_name)}{mode_suffix}"
    )


def _slugify_name(name: str) -> str:
    """Convert a character name into the filename format used for output sheets."""
    name = name.lower().strip()
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 -"
    cleaned = "".join(ch for ch in name if ch in allowed_chars)
    return cleaned.replace(" ", "_")


class HtmlCharacterSheetWriter:
    def _open_page(self, path: str | pathlib.Path) -> TextIO:
        """Every page is written through this. The snapshot tests override it
        to capture pages in memory (tests/_snapshot_helpers.py): reading a
        freshly written file back costs ~13 ms on Windows, because the
        antivirus scans it on first open."""
        return open(path, "w", encoding="utf-8")

    @staticmethod
    def _has_shield_armor(armors: list[Armor.AbstractArmor]) -> bool:
        return any(type(armor) is Armor.ShieldArmor for armor in armors)

    @staticmethod
    def _sort_features_key(character: Character, feat: Feature) -> tuple:
        """Full-sheet order: species, background and origin-feat features
        first, then class and subclass features by level; within that, the
        sheet's one order (Character.feature_sort_key)."""
        stamp = character.stamp_of(feat)
        passive, *rest = character.feature_sort_key(feat)
        leveled = stamp.kind.is_class_level
        return (passive, leveled, stamp.level if leveled else 0, *rest)

    @staticmethod
    def _feature_level(character: Character, feat: Feature) -> int:
        """The class-relative level `feat` was granted at (its stamp), which
        decides the level page it's listed on. Species, background and
        origin-feat features are stamped level 1."""
        return character.stamp_of(feat).level

    @staticmethod
    def _spell_level(spell: SpellGrant) -> int:
        """Class-relative level a spell/cantrip was granted on, mirroring
        _feature_level - stamped by the builder's Grants scope."""
        return spell.grant_level

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
    def _format_class_level_history(character: Character) -> str:
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
        character: Character,
        file: TextIO,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: Collection[Enum],
        character_subclass: Optional[str],
        size: Definitions.CreatureSize,
    ):
        """Character overview: large tiles for the stats checked constantly
        in play (HP above all, then AC/Initiative/Speed/Prof. Bonus), with
        everything else — class, proficiencies, languages, senses — as
        compact reference chips below. The player already knows their class;
        they don't already know today's HP total.
        """
        file.write("<h2>Overview</h2>\n")
        for warning in character.warnings:
            file.write(f"<p class='sheet-warning'>⚠ {html.escape(warning)}</p>\n")
        file.write("<div class='overview-section'>\n")

        ac = character.calculate_armor_class()
        ac_sub = (
            f"w/o Shield {character.calculate_armor_class(ignore_shield=True)}"
            if self._has_shield_armor(armors)
            else ""
        )

        initiative_sub = ""
        if character.initiative_roll_condition in (
            Definitions.DiceRollCondition.ADVANTAGE,
            Definitions.DiceRollCondition.DISADVANTAGE,
        ):
            initiative_sub = character.initiative_roll_condition.value

        file.write("<div class='overview-tiles'>\n")
        file.write(self._stat_tile_hp("HP", character.calculate_hit_points()))
        file.write(self._stat_tile("AC", ac, sub=ac_sub))
        file.write(
            self._stat_tile(
                "Initiative",
                f"{character.calculate_initiative():+}",
                sub=initiative_sub,
            )
        )
        file.write(self._stat_tile("Speed", f"{character.calculate_speed()} ft"))
        file.write(
            self._stat_tile("Prof. Bonus", f"{character.get_proficiency_bonus():+}")
        )
        file.write("</div>\n")

        languages = ", ".join(
            language.value
            for language in sorted(
                character.ledger.languages.known, key=lambda lang: lang.value
            )
        )
        senses = ", ".join(
            f"{sense.value} {character.ledger.senses.ranges[sense]} ft."
            for sense in sorted(character.ledger.senses.ranges, key=lambda s: s.value)
        )

        resistance_immunity_groups = []
        if character.ledger.defenses.damage_resistances:
            resistance_immunity_groups.append(
                "Resistant: "
                + ", ".join(
                    damage_type.value
                    for damage_type in sorted(
                        character.ledger.defenses.damage_resistances,
                        key=lambda d: d.value,
                    )
                )
            )
        if character.ledger.defenses.damage_immunities:
            resistance_immunity_groups.append(
                "Immune: "
                + ", ".join(
                    damage_type.value
                    for damage_type in sorted(
                        character.ledger.defenses.damage_immunities,
                        key=lambda d: d.value,
                    )
                )
            )
        if character.ledger.defenses.condition_immunities:
            resistance_immunity_groups.append(
                "Condition Immune: "
                + ", ".join(
                    condition.value
                    for condition in sorted(
                        character.ledger.defenses.condition_immunities,
                        key=lambda c: c.value,
                    )
                )
            )
        resistances_and_immunities = "; ".join(resistance_immunity_groups)

        details = [
            ("Class", self._format_class_level_history(character)),
            ("Subclass", character_subclass),
            ("Size", size.value),
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

    def _write_abilities(self, character: Character, file: TextIO):
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
            save_condition = character.get_saving_throw_roll_condition(ability)
            if save_condition == Definitions.DiceRollCondition.ADVANTAGE:
                saving_throw_text += " (Adv)"
            elif save_condition == Definitions.DiceRollCondition.DISADVANTAGE:
                saving_throw_text += " (Dis)"

            tile_class = "ability-tile st-proficient" if proficient else "ability-tile"
            file.write(f"<div class='{tile_class}'>\n")
            file.write(f"<span class='ability-tile-name'>{ability.short_name}</span>\n")
            file.write(f"<span class='ability-tile-mod'>{ability_mod:+}</span>\n")
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
        character: Character,
        file: TextIO,
        casting_abilities: list[Ability],
        include_probability_tables: bool = False,
    ):
        """Prominent Ability / Save DC / Attack roll tiles, one row per
        spellcasting ability. DC and attack are written as formulas ("8 + Cha
        Mod + Proficiency Bonus"), like weapon attacks, rather than resolved
        numbers. The probability breakdown tables that follow are reference
        material, so they're rendered smaller and muted.
        """
        file.write("<div class='spell-headline'>\n")
        for ability in casting_abilities:
            stats = f"{ability.short_name.title()} Mod + Proficiency Bonus"
            dc_formula = f"8 + {stats}"
            if character.spell_save_dc_bonus:
                sign = "-" if character.spell_save_dc_bonus < 0 else "+"
                dc_formula += f" {sign} {abs(character.spell_save_dc_bonus)} (bonus)"
            attack_formula = f"1d20 + {stats}"
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
                f"<span class='spell-stat-value spell-stat-formula'>{dc_formula}</span>"
                "</div>\n"
            )
            file.write(
                "<div class='spell-stat-tile'>"
                "<span class='spell-stat-label'>Spell Attack Roll</span>"
                f"<span class='spell-stat-value spell-stat-formula'>{attack_formula}</span>"
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
        character: Character,
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
        character: Character,
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
        character: Character,
        skill: Definitions.Skill,
        condition: Definitions.DiceRollCondition = Definitions.DiceRollCondition.NEUTRAL,
        condition_reasons: Optional[list[str]] = None,
    ) -> str:
        """Modifier as a sum of its parts, e.g. '2 + 3 (proficiency) + 1 (Ring of X)',
        followed by the roll condition and its reason, e.g. 'Disadvantage (Chain Mail)'.
        """
        terms: list[SourcedValue] = []
        proficiency_bonus = character.get_proficiency_bonus()
        if character.has_expertise_in_skill(skill):
            terms.append(SourcedValue(proficiency_bonus, "proficiency"))
            terms.append(SourcedValue(proficiency_bonus, "expertise"))
        elif character.is_proficient_in_skill(skill):
            terms.append(SourcedValue(proficiency_bonus, "proficiency"))
        terms.extend(character.get_skill_bonus_sources(skill))

        breakdown = str(
            character.get_ability_modifier(character.get_skill_ability(skill))
        )
        for term in terms:
            sign = "+" if term.value >= 0 else "-"
            breakdown += f" {sign} {abs(term.value)} ({term.source})"

        if condition != Definitions.DiceRollCondition.NEUTRAL:
            condition_text = condition.value
            if condition_reasons:
                condition_text += f" ({', '.join(condition_reasons)})"
            breakdown += f", {condition_text}"
        return breakdown

    def _write_weapons(
        self,
        character: Character,
        file: TextIO,
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        include_probability_tables: bool = False,
        name_tags: Optional[list[str]] = None,
    ):
        if not weapons:
            return

        write_weapons_to_file(
            weapons,
            character,
            file,
            include_probability_tables,
            weapon_masteries=weapon_masteries,
            name_tags=name_tags,
        )

    def _write_fighting_styles(
        self,
        character: Character,
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
        self, character: Character, file: TextIO, invocations: list[str]
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

    def _write_pact_magic_slots(
        self, character: Character, file: TextIO, heading: str = "h2"
    ):
        """`heading` is the tag for the title - h2 as a section of its own,
        h3 as a subsection at the top of the Spells section."""
        if not character.pact_magic_slots:
            return
        file.write(f"<{heading}>Pact Magic Slots</{heading}>\n")
        reset_label = "Regained on: Short Rest or Long Rest"
        # Every slot up to level 20, each marked with the level it's gained
        # at, so the sheet keeps working as the character levels up.
        progression = character.get_slot_progression()
        if progression is not None and progression.pact_magic_slots:
            Html.write_pact_slot_progression(
                progression.pact_magic_slots,
                progression.pact_magic_slot_levels,
                character.character_level,
                file,
                reset_label,
            )
        else:
            Html.write_slot_table(character.pact_magic_slots, file, reset_label)
        file.write("<br class='section-gap'>\n")

    def _write_spell_slots(
        self, character: Character, file: TextIO, heading: str = "h2"
    ):
        """`heading` is the tag for the title - h2 as a section of its own,
        h3 as a subsection at the top of the Spells section."""
        if not character.spell_slots:
            return

        file.write(f"<{heading}>Spell Slots</{heading}>\n")
        reset_label = "Regained on: Long Rest"
        # Every slot up to level 20, each marked with the level it's gained
        # at, so the sheet keeps working as the character levels up. A fixed
        # table of slots (e.g. a companion's) has no progression to show.
        progression = character.get_slot_progression()
        if progression is not None and progression.spell_slots:
            Html.write_slot_progression_table(
                progression.spell_slots, file, reset_label
            )
        else:
            Html.write_slot_table(character.get_spell_slots(), file, reset_label)
        file.write("<br class='section-gap'>\n")

    def _write_spell_cards(
        self,
        character: Character,
        file: TextIO,
        spells: list[SpellGrant],
    ):
        """Write the '<div class='spells'>' block of individual spell cards
        (grouped by spell level with a header per group) for the given
        subset of spells. Does not write the spellcasting headline or the
        surrounding <h2> - callers are responsible for those."""
        if not spells:
            return

        file.write("<div class='spells'>\n")

        created_spells = []
        for entry in spells:
            created_spells.append(
                SpellFactory.create(
                    entry.name, entry.ability, entry.ruling, entry.source
                )
            )
        sorted_spells = sorted(created_spells, key=lambda s: (s.level, s.name))

        # Group by level and emit a level header before each group
        from itertools import groupby

        for level, group in groupby(sorted_spells, key=lambda s: s.level):
            level_label = "Cantrips" if level == 0 else f"Level {level} Spells"
            file.write(f"<h3 class='spell-level-header'>{level_label}</h3>\n")
            for spell in group:
                write_spell_to_file(spell, file)

        file.write("</div>\n")

    def _write_spells(
        self,
        character: Character,
        file: TextIO,
        spells: list[SpellGrant],
        include_probability_tables: bool = False,
    ):
        if not spells and not character.spell_slots and not character.pact_magic_slots:
            return

        file.write("<h2 class='print-page-break'>Spells</h2>\n")
        # Slots lead the Spells section rather than standing as sections of
        # their own.
        self._write_pact_magic_slots(character, file, heading="h3")
        self._write_spell_slots(character, file, heading="h3")
        if not spells:
            return

        casting_abilities = sorted(
            {spell.ability for spell in spells},
            key=lambda a: a.value,
        )
        # Own subheading, so the headline and spell cards don't read as a
        # continuation of the slot tables above them.
        file.write("<h3>Spellcasting</h3>\n")
        self._write_spellcasting_headline(
            character, file, casting_abilities, include_probability_tables
        )
        self._write_spell_cards(character, file, spells)
        file.write("<br class='section-gap'>\n")

    @staticmethod
    def _format_gold(value: float) -> str:
        return f"{int(value)} GP" if value == int(value) else f"{value:g} GP"

    def _ownership_tags(
        self,
        item: Items.Item,
        entry: EquipmentEntry,
        starting_equipment_entry: Optional[EquipmentEntry],
    ) -> str:
        """Chips attached to an owned item's name saying where it came from:
        the label of the equipment entry it was added in, plus whether it
        was bought (with the amount paid) or found. Starting Equipment gets
        only its label - that gear's cost is already reflected in Starting
        Gold, not tracked per item."""
        tags = f" <span class='wtag'>{entry.label}</span>"
        if entry is starting_equipment_entry:
            return tags
        for purchased_item, price in entry.purchases:
            if purchased_item is item:
                price_display = self._format_gold(price)
                return (
                    tags + f" <span class='wtag wtag-worn'>Paid: {price_display}</span>"
                )
        return tags + " <span class='wtag wtag-not-worn'>Found</span>"

    @staticmethod
    def _collect_gear(entries: list[EquipmentEntry]) -> tuple[
        list[tuple[Armor.AbstractArmor, EquipmentEntry]],
        list[tuple[AbstractWeapon, EquipmentEntry]],
        list[tuple[Items.Item, int, EquipmentEntry]],
    ]:
        """Every entry's armor, weapons and other items pooled into one list
        per category, each paired with the entry it came from and sorted by
        item type then name. Unarmed Strike and currency are left out."""
        armors = sorted(
            (
                (_as(armor, Armor.AbstractArmor), entry)
                for entry in entries
                for armor in entry.armors
            ),
            key=lambda x: (x[0].category.value, x[0].name),
        )
        weapons = sorted(
            (
                (_as(weapon, AbstractWeapon), entry)
                for entry in entries
                for weapon in entry.weapons
                if not isinstance(weapon, UnarmedStrike)
            ),
            key=lambda x: (x[0].category.value, x[0].name),
        )
        items = sorted(
            (
                (item, quantity, entry)
                for entry in entries
                for gear, quantity in entry.items
                if (item := _as(gear, Items.Item)).category
                != Items.ItemCategory.CURRENCY
            ),
            key=lambda x: (x[0].category.value, x[0].name),
        )
        return armors, weapons, items

    def _build_item_sections(
        self,
        entries: list[EquipmentEntry],
        starting_equipment_entry: Optional[EquipmentEntry],
        show_ownership: bool = True,
        exclude_item_ids: Collection[int] = frozenset(),
    ) -> list[tuple[str, list[tuple[str, str, int, str, str, str]]]]:
        """(title, [(label, description, slots, type, rarity, price), ...])
        per non-empty Armor/Weapons/Other items table, in the same
        slot-table format, pooling every entry's gear. With
        `show_ownership`, each label carries where the item came from.
        Other items whose id is in `exclude_item_ids` (tools already shown
        in the Tools section) are left out."""
        armors, weapons, items = self._collect_gear(entries)
        items = [x for x in items if id(x[0]) not in exclude_item_ids]

        def ownership(item, entry) -> str:
            if not show_ownership:
                return ""
            return self._ownership_tags(item, entry, starting_equipment_entry)

        sections = []
        armor_rows = [
            (
                f"{armor.name}{Html.attunement_tag(armor)}{ownership(armor, entry)}",
                self._description_or_dash(armor.description_text),
                armor.slots,
                *Html.item_type_rarity_price(armor),
            )
            for armor, entry in armors
        ]
        if armor_rows:
            sections.append(("Armor", armor_rows))

        weapon_rows = [
            (
                f"{weapon.name}{Html.attunement_tag(weapon)}{ownership(weapon, entry)}",
                self._description_or_dash(weapon.description_text),
                weapon.slots,
                *Html.item_type_rarity_price(weapon),
            )
            for weapon, entry in weapons
        ]
        if weapon_rows:
            sections.append(("Weapons", weapon_rows))

        item_rows = [
            (
                f"{item.name} ({quantity}){Html.attunement_tag(item)}"
                f"{ownership(item, entry)}",
                item.description_text,
                item.slots,
                *Html.item_type_rarity_price(item),
            )
            for item, quantity, entry in items
        ]
        if item_rows:
            sections.append(("Other items", item_rows))

        return sections

    def _write_items(
        self,
        character: Character,
        file: TextIO,
        equipment_entries: list[EquipmentEntry],
        starting_equipment_entry: Optional[EquipmentEntry],
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        current_gold: Optional[float],
        tool_proficiencies: Sequence[ToolProficiency] = (),
        include_probability_tables: bool = False,
        write_heading: bool = True,
    ):
        """`write_heading` False leaves out the "Items" heading, for the
        items page, whose own title already says Items."""
        non_empty_entries = [
            entry
            for entry in equipment_entries
            if entry.armors or entry.weapons or entry.items or entry.gold
        ]
        if not non_empty_entries and not weapons and not tool_proficiencies:
            return

        if write_heading:
            file.write("<h2 class='print-page-break'>Items</h2>\n")
        file.write("<div class='items-section'>\n")

        if non_empty_entries:
            self._write_wallet_and_carrying(
                character, file, non_empty_entries, current_gold
            )

        self._write_item_sections(
            file,
            non_empty_entries,
            starting_equipment_entry,
            character=character,
            character_weapons=weapons,
            weapon_masteries=weapon_masteries,
            include_probability_tables=include_probability_tables,
            tool_proficiencies=tool_proficiencies,
        )

        file.write("</div>\n")
        file.write("<br class='section-gap'>\n")

    def _write_wallet_and_carrying(
        self,
        character: Character,
        file: TextIO,
        entries: list[EquipmentEntry],
        current_gold: Optional[float],
    ):
        # Wallet pinned to the left, carrying capacity (total + a compact
        # per-source pip breakdown) pinned to the right - keeps the row
        # tidy instead of one flat chip list wrapping unevenly.
        file.write("<h3>Wealth &amp; Carrying Capacity</h3>\n")
        carrying_capacity = character.get_carrying_capacity()
        file.write("<div class='wallet-carry-row'>\n")
        file.write("<div class='wallet-block'>\n")
        if current_gold is not None:
            file.write(
                f"<span class='overview-detail'><span class='od-label'>Starting Gold</span>"
                f"{self._format_gold(current_gold)}</span>\n"
            )
        # Gold gained or spent per equipment entry - the entries don't get
        # their own headings, so their gold sits with the wallet.
        for entry in entries:
            if entry.gold:
                sign = "+" if entry.gold > 0 else "-"
                file.write(
                    f"<span class='overview-detail'><span class='od-label'>{entry.label}</span>"
                    f"{sign}{self._format_gold(abs(entry.gold))}</span>\n"
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
        for source in character.get_carrying_capacity_sources():
            slot_boxes = "<span class='slot-box'></span>" * source.value
            file.write(
                f"<span class='carrying-source'><span class='cs-label'>{source.source} ({source.value})</span>"
                f"<span class='slot-box-group'>{slot_boxes}</span></span>\n"
            )
        file.write("</div>\n")
        file.write("</div>\n")

    def _write_item_sections(
        self,
        file: TextIO,
        entries: list[EquipmentEntry],
        starting_equipment_entry: Optional[EquipmentEntry],
        character: Optional[Character] = None,
        character_weapons: Sequence[AbstractWeapon] = (),
        weapon_masteries: Sequence[AbstractWeapon] = (),
        include_probability_tables: bool = False,
        tool_proficiencies: Sequence[ToolProficiency] = (),
    ):
        """One Armor, one Weapons and (character sheets) one Tools section,
        then one Other items section of gear cards, pooling every entry's
        gear. Each section opens with its own heading (styled in
        Html.BASE_CHARACTER_SHEET_CSS), so no separator is drawn between
        them. Shared by item sheets and character sheets so both present
        items identically.

        Without a `character` (item sheets) armor and weapons render as
        rules-reference cards. With one (character sheets), weapons render
        as attack cards resolved against that character - including the
        ones in `character_weapons` that aren't items, like Unarmed Strike
        - and every card's name carries where it came from, instead of each
        entry getting its own sections."""
        show_ownership = character is not None
        armors, weapons, items = self._collect_gear(entries)

        if armors:
            armor_tags = [
                (
                    self._ownership_tags(armor, entry, starting_equipment_entry)
                    if show_ownership
                    else ""
                )
                for armor, entry in armors
            ]
            write_armors_to_file([armor for armor, _ in armors], file, armor_tags)

        if character is not None:
            # Weapons the character has that no entry holds (Unarmed
            # Strike) lead the section, ahead of the owned ones.
            owned_ids = {id(weapon) for weapon, _ in weapons}
            innate_weapons = [w for w in character_weapons if id(w) not in owned_ids]
            if innate_weapons or weapons:
                weapon_tags = [""] * len(innate_weapons) + [
                    self._ownership_tags(weapon, entry, starting_equipment_entry)
                    for weapon, entry in weapons
                ]
                self._write_weapons(
                    character,
                    file,
                    innate_weapons + [weapon for weapon, _ in weapons],
                    list(weapon_masteries),
                    include_probability_tables,
                    weapon_tags,
                )
        elif weapons:
            write_weapons_reference_to_file([weapon for weapon, _ in weapons], file)

        tool_item_ids: set[int] = set()
        if character is not None and tool_proficiencies:
            tool_item_ids = self._write_tools(
                character, file, tool_proficiencies, items, starting_equipment_entry
            )

        consumable_item_ids = self._write_scrolls_and_potions(
            file,
            [x for x in items if id(x[0]) not in tool_item_ids],
            starting_equipment_entry,
            show_ownership,
        )

        for section_title, rows in self._build_item_sections(
            entries,
            starting_equipment_entry,
            show_ownership,
            tool_item_ids | consumable_item_ids,
        ):
            if section_title != "Other items":
                continue  # armor/weapons are rendered as cards above
            Html.write_item_cards(file, section_title, rows)

    def _write_scrolls_and_potions(
        self,
        file: TextIO,
        items: list[tuple[Items.Item, int, EquipmentEntry]],
        starting_equipment_entry: Optional[EquipmentEntry],
        show_ownership: bool,
    ) -> set[int]:
        """Scrolls and Potions sections of gear cards, laid out for what
        each is used for: a scroll's spell (level, school, casting time,
        range, duration, save DC/attack bonus, text), a potion's effect.
        Returns the ids of the items written, so Other items can leave them
        out."""
        sections = [
            ("Scrolls", Items.ItemCategory.SCROLL, self._write_scroll_body),
            ("Potions", Items.ItemCategory.POTION, self._write_potion_body),
        ]
        written_ids: set[int] = set()
        for title, category, write_body in sections:
            group = [x for x in items if x[0].category == category]
            if not group:
                continue
            file.write(f"<h3>{title}</h3>\n")
            file.write("<div class='gear-list'>\n")
            for item, quantity, entry in group:
                label = f"{item.name} ({quantity}){Html.attunement_tag(item)}"
                if show_ownership:
                    label += self._ownership_tags(item, entry, starting_equipment_entry)
                file.write("<div class='gear-entry'>\n")
                Html.write_gear_header(
                    file,
                    f"<span class='gear-name'>{label}</span>",
                    Html.carrying_checkbox_id(label),
                    item.slots,
                )
                write_body(file, item)
                file.write("</div>\n")
                written_ids.add(id(item))
            file.write("</div>\n")
        return written_ids

    @staticmethod
    def _write_scroll_body(file: TextIO, scroll: Items.Item):
        spell = getattr(scroll, "spell", None)
        if spell is None:
            # A generic Spell Scroll, with no one spell to lay out.
            Html.write_gear_meta_line(file, *Html.item_type_rarity_price(scroll))
            if scroll.description_text:
                file.write(f"<div class='gear-desc'>{scroll.description_text}</div>\n")
            return

        # The meta line leads with the spell's level and school in place of
        # a "Scroll" type label the section heading already gives.
        level = "Cantrip" if spell.level == 0 else f"Level {spell.level}"
        _, rarity, price = Html.item_type_rarity_price(scroll)
        Html.write_gear_meta_line(file, f"{level} {spell.school}", rarity, price)
        Html.write_gear_line(
            file,
            ("Cast", spell.casting_time),
            ("Range", spell.range),
            ("Duration", spell.duration),
        )
        Html.write_gear_line(
            file,
            ("Save DC", str(scroll.save_dc)),
            ("Attack", f"{scroll.attack_bonus:+}"),
        )
        # A scroll always casts at its own level, so the spell's upcasting
        # paragraph doesn't apply and is left out.
        paragraphs = [
            paragraph
            for paragraph in spell.description.split("\n")
            if not paragraph.startswith(
                ("Using a Higher-Level Spell Slot", "At Higher Levels")
            )
        ]
        description = Html.boxes_to_html("\n".join(paragraphs)).replace("\n", "<br>")
        file.write(f"<div class='gear-desc'>{description}</div>\n")

    @staticmethod
    def _write_potion_body(file: TextIO, potion: Items.Item):
        # The meta line keeps the plain type ("Potion") - unlike a scroll's
        # spell, a potion has no kind worth leading with.
        Html.write_gear_meta_line(file, *Html.item_type_rarity_price(potion))
        # A potion's description opens with what drinking it does; any
        # further lines are details (how long it lasts, what it looks like).
        effect, _, details = (potion.description_text or "").partition("\n")
        if effect:
            Html.write_gear_line(file, ("Effect", effect))
        if details:
            details_html = details.replace("\n", "<br>")
            file.write(f"<div class='gear-desc'>{details_html}</div>\n")

    def _write_tools(
        self,
        character: Character,
        file: TextIO,
        tool_proficiencies: Sequence[ToolProficiency],
        owned_items: list[tuple[Items.Item, int, EquipmentEntry]],
        starting_equipment_entry: Optional[EquipmentEntry],
    ) -> set[int]:
        """Tools section: one gear card per tool proficiency, with the
        tool item's type, rarity, cost and slots alongside the check
        formula and what the tool lets you Utilize and Craft. A tool
        the character owns carries where it came from; one they don't is
        marked "Not owned". Returns the ids of the owned tool items, so
        Other items can leave them out."""
        file.write("<h3>Tools</h3>\n")
        file.write("<div class='gear-list'>\n")

        used_item_ids: set[int] = set()
        for tool in sorted(tool_proficiencies, key=lambda t: t.name):
            item = tool.make_item()
            owned = next(
                (
                    (owned_item, entry)
                    for owned_item, _, entry in owned_items
                    if item is not None
                    and type(owned_item) is type(item)
                    and id(owned_item) not in used_item_ids
                ),
                None,
            )

            name_html = (
                f"<span class='gear-name'>{tool.name}"
                f"<span class='skill-ability-tag'>{tool.ability.short_name}</span>"
            )
            file.write("<div class='gear-entry'>\n")
            if owned is not None:
                item, entry = owned
                used_item_ids.add(id(item))
                name_html += (
                    f"{Html.attunement_tag(item)}"
                    f"{self._ownership_tags(item, entry, starting_equipment_entry)}</span>"
                )
            else:
                name_html += " <span class='wtag wtag-not-worn'>Not owned</span></span>"
            # Carrying checkbox like every other item card - also on a tool
            # not owned yet, for when the character picks one up.
            Html.write_gear_header(
                file,
                name_html,
                Html.carrying_checkbox_id(tool.name),
                item.slots if item is not None else 0,
            )
            if item is not None:
                Html.write_gear_meta_line(file, *Html.item_type_rarity_price(item))

            # How the check bonus is made up, worded like weapon attack rolls
            # ("1d20 + Dex Mod + Proficiency Bonus").
            check_formula = (
                f"1d20 + {tool.ability.short_name.title()} Mod + Proficiency Bonus"
            )
            Html.write_gear_line(file, ("Check", check_formula))
            Html.write_gear_line(file, ("Utilize", tool.utilize_text()))
            if tool.craftables:
                Html.write_gear_line(file, ("Craft", tool.craft_text()))
            # No item description: a tool item's is only "Ability: ...
            # Utilize: ...", which the Check/Utilize lines already say.
            file.write("</div>\n")

        file.write("</div>\n")
        return used_item_ids

    def _get_css_style(self) -> str:
        return Html.render_style_block(
            Html.BASE_CHARACTER_SHEET_CSS,
            SPELL_CARD_CSS,
            WEAPON_CARD_CSS,
            ARMOR_CARD_CSS,
            WILDSHAPE_CARD_CSS,
            FEATURE_CARD_CSS,
        )

    def write_character_sheet(
        self,
        data: "Character",
        skill_config: Definitions.SkillConfig = Definitions.SkillConfig.DEFAULT,
        description_mode: Literal["table", "concise"] | None = None,
        include_probability_tables: bool = False,
        output_folder: Optional[str] = None,
    ) -> None:
        """Render every page of `data`'s character sheet. `output_folder`
        overrides the default `get_output_folder(data, description_mode)`
        path - tests use this to render into a tmp directory instead of
        `Output/`."""
        # `validate()` is the single validation entry point: the required
        # fields (e.g. "Character name must be set."), then skill/save
        # requirements and multiclass ability prerequisites against every
        # effect.
        character = data.validate()
        if output_folder is None:
            output_folder = get_output_folder(data, description_mode)
        armors = [_as(a, Armor.AbstractArmor) for a in data.armors]
        armor_proficiencies = character.ledger.equipment_training.armor_training
        weapon_proficiencies = character.ledger.equipment_training.weapon_proficiencies
        features = [_as(f, Feature) for f in data.top_level_features()]
        weapons = [_as(w, AbstractWeapon) for w in data.weapons]
        weapon_masteries = [_as(w, AbstractWeapon) for w in data.weapon_masteries]
        fighting_styles = [_as(s, FightingStyle) for s in data.fighting_styles]
        invocations = data.invocations
        spells = data.spells
        equipment_entries = data.inventory.equipment_entries
        starting_equipment_entry = data.inventory.starting_equipment_entry
        tool_proficiencies = character.ledger.equipment_training.tool_proficiencies
        # Identity, gold and size live on the sheet data, not the stat block -
        # see Model/ClassLevels.py.
        character_name = data.character_name
        character_subclass = data.character_subclass
        base_class = data.base_class
        current_gold = data.inventory.current_gold
        size = data.size
        assert character_name is not None and base_class is not None
        assert size is not None

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
            features_by_level.setdefault(self._feature_level(data, feature), []).append(
                feature
            )

        spells_by_level: dict[int, list[SpellGrant]] = {}
        for spell in spells:
            spells_by_level.setdefault(self._spell_level(spell), []).append(spell)

        # Build a bucket of extensions (feature enhancements) that appear on their
        # own level pages as standalone cards. Skip extensions whose level <= parent
        # level (already nested on the parent's page via write_to_file's max_level filtering).
        extensions_by_level: dict[int, list[tuple[Feature, Feature]]] = {}
        for feature in features:  # Iterate full list, not just text_features
            parent_level = self._feature_level(data, feature)
            for extension in [_as(e, Feature) for e in data.extensions_of(feature)]:
                ext_level = self._feature_level(data, extension)
                if ext_level <= parent_level:
                    continue  # Already shown nested on the parent's page
                if (
                    extension.render_html_description(character, description_mode)
                    is None
                ):
                    continue
                extensions_by_level.setdefault(ext_level, []).append(
                    (feature, extension)
                )

        # A level page is needed for any level that grants a displayed
        # feature OR a spell/cantrip - a level that only grants spells
        # (no feature with a rendered description) would otherwise be
        # missed entirely.
        level_page_levels = sorted(
            set(features_by_level) | set(spells_by_level) | set(extensions_by_level)
        )

        has_fighting_styles_page = bool(fighting_styles)
        non_empty_equipment_entries = [
            entry
            for entry in equipment_entries
            if entry.armors or entry.weapons or entry.items or entry.gold
        ]
        has_items_page = (
            bool(non_empty_equipment_entries)
            or bool(tool_proficiencies)
            or bool(weapons)
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
            character_name,
            base_class,
            character_subclass,
            size,
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
            character_name,
            base_class,
            character_subclass,
            size,
            current_gold,
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
                features_by_level.get(level, []), key=data.feature_sort_key
            )
            level_spells = spells_by_level.get(level, [])
            level_extensions = extensions_by_level.get(level, [])
            self._write_features_page(
                output_folder_obj / page_path,
                page_path,
                pages,
                character,
                character_name,
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
                character_name,
                fighting_styles,
            )

        if has_items_page:
            self._write_items_page(
                output_folder_obj / "items.html",
                "items.html",
                pages,
                character,
                character_name,
                current_gold,
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
        character: Character,
        character_name: str,
        base_class: Definitions.CharacterClass,
        character_subclass: Optional[str],
        size: Definitions.CreatureSize,
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: Collection[Enum],
        skill_config: Definitions.SkillConfig,
        invocations: list[str],
        spells: list[SpellGrant],
        include_probability_tables: bool,
    ):
        with self._open_page(path) as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(
                f"<h1>{character_name} - Level {character.character_level} "
                f"{base_class.value}</h1>\n"
            )
            self._write_status_section(file)
            self._write_overview(
                character,
                file,
                armors,
                armor_proficiencies,
                weapon_proficiencies,
                character_subclass,
                size,
            )
            file.write("<h2>Abilities and Skills</h2>\n")
            file.write("<div class='section-row'>\n")
            file.write("<div class='section-col section-col-abilities'>\n")
            self._write_abilities(character, file)
            if spells:
                casting_abilities = sorted(
                    {spell.ability for spell in spells},
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
        build. No Character involved: every value is a blank
        fill-in line (see .blank-fill in Html.py) instead of computed data,
        and build-specific content (features, spellcasting, equipment) is
        skipped entirely since none of it applies until a character exists.
        """
        output_folder_obj = pathlib.Path(output_folder)
        output_folder_obj.mkdir(parents=True, exist_ok=True)
        path = output_folder_obj / "character.html"

        blank_sm = "<span class='blank-fill blank-fill-sm'></span>"

        with self._open_page(path) as file:
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
                ability = Skills.default_ability(skill)
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
        character: Character,
        character_name: str,
        base_class: Definitions.CharacterClass,
        character_subclass: Optional[str],
        size: Definitions.CreatureSize,
        current_gold: Optional[float],
        armors: list[Armor.AbstractArmor],
        armor_proficiencies: set[Definitions.ArmorType],
        weapon_proficiencies: Collection[Enum],
        skill_config: Definitions.SkillConfig,
        text_features: list[Feature],
        description_mode: Literal["table", "concise"] | None,
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        fighting_styles: list[FightingStyle],
        invocations: list[str],
        spells: list[SpellGrant],
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
        with self._open_page(path) as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(
                f"<h1>{character_name} - Level {character.character_level} "
                f"{base_class.value}</h1>\n"
            )
            self._write_status_section(file)
            self._write_overview(
                character,
                file,
                armors,
                armor_proficiencies,
                weapon_proficiencies,
                character_subclass,
                size,
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

            # Features, Spells and Items each start on a new page (their
            # headings carry the break); without Features, whatever follows
            # Abilities and Skills still starts on a fresh page.
            if text_features:
                file.write("<h2 class='print-page-break'>Features</h2>\n")
                sorted_features = sorted(
                    text_features, key=lambda f: self._sort_features_key(character, f)
                )
                file.write("<div class='features'>\n")
                for feature in sorted_features:
                    feature.write_to_file(character, file, description_mode)
                file.write("</div>\n<br class='section-gap'>\n")
            else:
                file.write("<div class='print-page-break'></div>\n")

            self._write_fighting_styles(character, file, fighting_styles)
            self._write_invocations(character, file, invocations)
            self._write_spells(character, file, spells, include_probability_tables)
            self._write_items(
                character,
                file,
                equipment_entries,
                starting_equipment_entry,
                weapons,
                weapon_masteries,
                current_gold,
                tool_proficiencies,
                include_probability_tables,
            )

    def _write_features_page(
        self,
        path: pathlib.Path,
        page_path: str,
        pages: list[tuple[str, str]],
        character: Character,
        character_name: str,
        level: int,
        level_features: list[Feature],
        description_mode: Literal["table", "concise"] | None,
        level_spells: list[SpellGrant],
        level_extensions: list[tuple[Feature, Feature]] | None = None,
    ):
        if level_extensions is None:
            level_extensions = []

        with self._open_page(path) as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(f"<h1>{character_name} - Level {level} Features</h1>\n")
            file.write("<div class='features'>\n")
            for feature in level_features:
                feature.write_to_file(
                    character, file, description_mode, max_level=level
                )
            sorted_level_extensions = sorted(
                level_extensions,
                key=lambda pe: (
                    character.feature_sort_key(pe[1]),
                    character.feature_sort_key(pe[0]),
                ),
            )
            for parent, extension in sorted_level_extensions:
                extension.write_extension_card_to_file(
                    character, file, parent.name, description_mode
                )
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
        character: Character,
        character_name: str,
        fighting_styles: list[FightingStyle],
    ):
        with self._open_page(path) as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(f"<h1>{character_name} - Fighting Styles</h1>\n")
            self._write_fighting_styles(character, file, fighting_styles)

    def _write_items_page(
        self,
        path: pathlib.Path,
        page_path: str,
        pages: list[tuple[str, str]],
        character: Character,
        character_name: str,
        current_gold: Optional[float],
        equipment_entries: list[EquipmentEntry],
        starting_equipment_entry: Optional[EquipmentEntry],
        tool_proficiencies: list[ToolProficiency],
        weapons: list[AbstractWeapon],
        weapon_masteries: list[AbstractWeapon],
        include_probability_tables: bool,
    ):
        with self._open_page(path) as file:
            file.write(self._get_css_style())
            self._write_nav(file, page_path, pages)
            file.write(f"<h1>{character_name} - Items</h1>\n")
            self._write_items(
                character,
                file,
                equipment_entries,
                starting_equipment_entry,
                weapons,
                weapon_masteries,
                current_gold,
                tool_proficiencies,
                include_probability_tables,
                write_heading=False,
            )

    def write_item_sheet(
        self,
        title: str,
        output_path: str,
        armors: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[AbstractWeapon]] = None,
        items: Optional[list[tuple[Items.Item, int]]] = None,
    ):
        """Generate a standalone item sheet HTML page showing a fixed set of
        items (armor/weapons/other) without character context or mechanics.
        Armor and weapons render as rules-reference cards (AC/attack/damage
        formulas, properties, restrictions) rather than the generic
        label/description/price row used for other items, since those are
        the two categories a player actually rolls dice against."""
        if armors is None:
            armors = []
        if weapons is None:
            weapons = []
        if items is None:
            items = []

        entry = EquipmentEntry(
            label=title, armors=list(armors), weapons=list(weapons), items=list(items)
        )

        output_file = pathlib.Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with self._open_page(output_file) as file:
            file.write(
                Html.render_style_block(
                    Html.BASE_CHARACTER_SHEET_CSS, WEAPON_CARD_CSS, ARMOR_CARD_CSS
                )
            )
            file.write(f"<h1>{title}</h1>\n")

            file.write("<div class='items-section'>\n")
            self._write_item_sections(file, [entry], starting_equipment_entry=entry)
            file.write("</div>\n")
