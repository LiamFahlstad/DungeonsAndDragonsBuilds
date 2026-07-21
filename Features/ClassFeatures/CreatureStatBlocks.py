from typing import Optional

from Combat.Definitions import ExtendedCombatantData
from Definitions import Ability, Skill
from StatBlocks.CharacterStatBlock import CharacterStatBlock

_ABILITY_BY_ABBR = {
    Ability.STRENGTH.short_name: Ability.STRENGTH,
    Ability.DEXTERITY.short_name: Ability.DEXTERITY,
    Ability.CONSTITUTION.short_name: Ability.CONSTITUTION,
    Ability.INTELLIGENCE.short_name: Ability.INTELLIGENCE,
    Ability.WISDOM.short_name: Ability.WISDOM,
    Ability.CHARISMA.short_name: Ability.CHARISMA,
}

_MENTAL_ABILITIES = (
    Ability.INTELLIGENCE.short_name,
    Ability.WISDOM.short_name,
    Ability.CHARISMA.short_name,
)


def _fmt_mod(modifier: int) -> str:
    return f"+{modifier}" if modifier >= 0 else str(modifier)


def _display(value) -> str:
    """Render an enum member (Skill/DamageType/Ability/...) or a plain value
    the same way — enums are str-mixins but f-string formatting them directly
    shows 'ClassName.MEMBER' rather than the value, so unwrap explicitly."""
    return value.value if hasattr(value, "value") else str(value)


def _row(label: str, value: str, value_class: str = "wsf-value-col") -> str:
    return f'<tr><td class="wsf-label-col">{label}</td><td class="{value_class}">{value}</td></tr>'


def _section_row(label: str) -> str:
    return f'<tr class="wsf-section"><th colspan="2">{label}</th></tr>'


def _entry_row(name: str, description: str) -> str:
    return f'<tr><td class="wsf-entry-name">{name}</td><td class="wsf-entry-desc">{description}</td></tr>'


def _monster_type_text(monster: ExtendedCombatantData) -> str:
    parts = []
    if monster.size:
        parts.append(_display(monster.size))
    if monster.monster_type:
        parts.append(monster.monster_type)
    text = " ".join(parts)
    if monster.alignment:
        alignment_text = _display(monster.alignment)
        text = f"{text}, {alignment_text}" if text else alignment_text
    return text


def _speed_text(monster: ExtendedCombatantData) -> str:
    parts = []
    if monster.speed_ground_ft is not None:
        parts.append(f"{monster.speed_ground_ft} ft.")
    if monster.speed_climb_ft is not None:
        parts.append(f"climb {monster.speed_climb_ft} ft.")
    if monster.speed_fly_ft is not None:
        parts.append(f"fly {monster.speed_fly_ft} ft.")
    text = ", ".join(parts)
    if monster.speed_special_rules:
        text = f"{text} ({monster.speed_special_rules})" if text else monster.speed_special_rules
    return text


def format_creature_stat_block(
    monster: ExtendedCombatantData,
    character_stat_block: Optional[CharacterStatBlock] = None,
    retain_mental_abilities: bool = False,
) -> str:
    """Render an ExtendedCombatantData instance as an HTML stat-block table.

    retain_mental_abilities: True for Wild Shape (the player retains their own
    creature type, HP/Hit Dice, Int/Wis/Cha, class features, languages, and feats
    per the "Game Statistics" rule). False for standalone creatures (e.g. a Primal
    Companion), which use their own full stat block with no player overrides.
    """
    rows = [
        f'<tr><th class="wsf-name" colspan="2">{monster.combatant_type}'
        f'<span class="wsf-subtitle">CR {monster.cr} &middot; {_monster_type_text(monster)}</span></th></tr>'
    ]

    ac_text = f"{monster.ac}" + (f" ({monster.ac_note})" if monster.ac_note else "")
    rows.append(_row("Armor Class", ac_text))

    speed = _speed_text(monster)
    if speed:
        rows.append(_row("Speed", speed))

    physical_parts = []
    for abbr in (
        Ability.STRENGTH.short_name,
        Ability.DEXTERITY.short_name,
        Ability.CONSTITUTION.short_name,
    ):
        score = monster.ability_scores.get(abbr, 10)
        modifier = (score - 10) // 2
        physical_parts.append(f"{abbr} {score} ({_fmt_mod(modifier)})")
    rows.append(_row("Str / Dex / Con", ", ".join(physical_parts)))

    if retain_mental_abilities and character_stat_block is not None:
        mental_parts = []
        for abbr in _MENTAL_ABILITIES:
            ability = _ABILITY_BY_ABBR[abbr]
            own_score = character_stat_block.get_ability_score(ability)
            own_modifier = character_stat_block.get_ability_modifier(ability)
            mental_parts.append(f"{abbr} {own_score} ({_fmt_mod(own_modifier)})")
        rows.append(
            _row(
                "Int / Wis / Cha",
                ", ".join(mental_parts) + " &mdash; yours, not the Beast's",
                value_class="wsf-value-col wsf-retained",
            )
        )
        rows.append(
            _row(
                "HP, Hit Dice, Languages, Class Features, Feats",
                "Yours, not the Beast's",
                value_class="wsf-value-col wsf-retained",
            )
        )
    else:
        mental_parts = []
        for abbr in _MENTAL_ABILITIES:
            score = monster.ability_scores.get(abbr, 10)
            modifier = (score - 10) // 2
            mental_parts.append(f"{abbr} {score} ({_fmt_mod(modifier)})")
        rows.append(_row("Int / Wis / Cha", ", ".join(mental_parts)))

        hp_text = f"{monster.hp}" + (f" ({monster.hp_formula})" if monster.hp_formula else "")
        rows.append(_row("Hit Points", hp_text))

        if monster.languages:
            rows.append(_row("Languages", monster.languages))

    if monster.skills:
        skill_parts = []
        for skill_name, beast_bonus in monster.skills.items():
            skill_label = _display(skill_name)
            own_bonus = None
            if retain_mental_abilities and character_stat_block is not None:
                try:
                    own_bonus = character_stat_block.get_skill_modifier(Skill(skill_name))
                except ValueError:
                    own_bonus = None
            if own_bonus is None:
                skill_parts.append(f"{skill_label} {_fmt_mod(beast_bonus)}")
                continue
            best = max(beast_bonus, own_bonus)
            source = "Beast's" if beast_bonus >= own_bonus else "yours"
            skill_parts.append(f"{skill_label} {_fmt_mod(best)} ({source})")
        rows.append(_row("Skills", "; ".join(skill_parts)))

    if monster.saving_throws:
        save_parts = []
        for abbr, beast_bonus in monster.saving_throws.items():
            ability = _ABILITY_BY_ABBR.get(abbr)
            own_bonus = None
            if ability is not None and retain_mental_abilities and character_stat_block is not None:
                own_bonus = character_stat_block.get_saving_throw_modifier(ability)
            if own_bonus is None:
                save_parts.append(f"{abbr} {_fmt_mod(beast_bonus)}")
                continue
            best = max(beast_bonus, own_bonus)
            source = "Beast's" if beast_bonus >= own_bonus else "yours"
            save_parts.append(f"{abbr} {_fmt_mod(best)} ({source})")
        rows.append(_row("Saving Throws", ", ".join(save_parts)))

    if monster.senses:
        # Strip periods before commas (e.g. "60 ft., Passive...") so downstream
        # sentence-based bolding heuristics elsewhere on the sheet aren't tripped up.
        senses = monster.senses.replace(".,", ",")
        rows.append(_row("Senses", senses))

    for attribute_name, label in (
        ("damage_vulnerabilities", "Vulnerabilities"),
        ("damage_resistances", "Resistances"),
        ("damage_immunities", "Damage Immunities"),
    ):
        entries = getattr(monster, attribute_name)
        if entries:
            parts = []
            for e in entries:
                text = ", ".join(_display(t) for t in e.damage_types)
                if e.note:
                    text = f"{text} {e.note}" if text else e.note
                parts.append(text)
            rows.append(_row(label, "; ".join(parts)))

    if monster.condition_immunities:
        rows.append(
            _row(
                "Condition Immunities",
                ", ".join(_display(c) for c in monster.condition_immunities),
            )
        )

    for attribute_name, label in (
        ("traits", "Traits"),
        ("actions", "Actions"),
        ("bonus_actions", "Bonus Actions"),
        ("reactions", "Reactions"),
    ):
        entries = getattr(monster, attribute_name)
        if entries:
            rows.append(_section_row(label))
            for entry in entries:
                rows.append(_entry_row(entry.name, entry.description))

    return '<table class="wildshape-card">' + "".join(rows) + "</table>"
