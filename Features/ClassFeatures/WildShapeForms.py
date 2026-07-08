from typing import Type

from Combat.Definitions import ExtendedCombatantData
from Definitions import Ability, Skill
from StatBlocks.CharacterStatBlock import CharacterStatBlock

_ABILITY_BY_ABBR = {
    "Str": Ability.STRENGTH,
    "Dex": Ability.DEXTERITY,
    "Con": Ability.CONSTITUTION,
    "Int": Ability.INTELLIGENCE,
    "Wis": Ability.WISDOM,
    "Cha": Ability.CHARISMA,
}

# Retained per the "Game Statistics" rule: creature type, HP/Hit Dice, Int/Wis/Cha,
# class features, languages, and feats always stay the player's own, never the Beast's.
_RETAINED_MENTAL_ABILITIES = ("Int", "Wis", "Cha")


def _fmt_mod(modifier: int) -> str:
    return f"+{modifier}" if modifier >= 0 else str(modifier)


def format_wild_shape_form(
    monster_cls: Type[ExtendedCombatantData],
    character_stat_block: CharacterStatBlock,
) -> str:
    monster = monster_cls()
    lines = [f"    * {monster.combatant_type} (CR {monster.cr}, {monster.monster_type})"]

    ac_text = f"{monster.ac}" + (f" ({monster.ac_note})" if monster.ac_note else "")
    lines.append(f"        - Armor Class: {ac_text}")

    speed = monster.speed.strip().rstrip(",")
    if speed:
        lines.append(f"        - Speed: {speed}")

    physical_parts = []
    for abbr in ("Str", "Dex", "Con"):
        score = monster.ability_scores.get(abbr, 10)
        modifier = (score - 10) // 2
        physical_parts.append(f"{abbr} {score} ({_fmt_mod(modifier)})")
    lines.append("        - " + ", ".join(physical_parts))

    mental_parts = []
    for abbr in _RETAINED_MENTAL_ABILITIES:
        ability = _ABILITY_BY_ABBR[abbr]
        own_score = character_stat_block.get_ability_score(ability)
        own_modifier = character_stat_block.get_ability_modifier(ability)
        mental_parts.append(f"{abbr} {own_score} ({_fmt_mod(own_modifier)})")
    lines.append(
        "        - " + ", ".join(mental_parts) + " — yours, not the Beast's"
    )

    lines.append("        - Hit Points, Hit Dice, Languages, Class Features, and Feats: yours, not the Beast's")

    if monster.skills:
        skill_parts = []
        for skill_name, beast_bonus in monster.skills.items():
            try:
                own_bonus = character_stat_block.get_skill_modifier(Skill(skill_name))
            except ValueError:
                skill_parts.append(f"{skill_name} {_fmt_mod(beast_bonus)}")
                continue
            best = max(beast_bonus, own_bonus)
            source = "Beast's" if beast_bonus >= own_bonus else "yours"
            skill_parts.append(f"{skill_name} {_fmt_mod(best)} ({source})")
        lines.append("        - Skills: " + "; ".join(skill_parts))

    if monster.saving_throws:
        save_parts = []
        for abbr, beast_bonus in monster.saving_throws.items():
            ability = _ABILITY_BY_ABBR.get(abbr)
            if ability is None:
                save_parts.append(f"{abbr} {_fmt_mod(beast_bonus)}")
                continue
            own_bonus = character_stat_block.get_saving_throw_modifier(ability)
            best = max(beast_bonus, own_bonus)
            source = "Beast's" if beast_bonus >= own_bonus else "yours"
            save_parts.append(f"{abbr} {_fmt_mod(best)} ({source})")
        lines.append("        - Saving Throws: " + ", ".join(save_parts))

    if monster.senses:
        # Strip periods before commas (e.g. "60 ft., Passive...") so the feature
        # renderer's sentence-based bolding doesn't swallow the whole line.
        senses = monster.senses.replace(".,", ",")
        lines.append(f"        - Senses: {senses}")

    for attribute_name, label in (
        ("damage_vulnerabilities", "Vulnerabilities"),
        ("damage_resistances", "Resistances"),
        ("damage_immunities", "Damage Immunities"),
        ("condition_immunities", "Condition Immunities"),
    ):
        values = getattr(monster, attribute_name)
        if values:
            lines.append(f"        - {label}: {', '.join(values)}")

    for attribute_name, label in (
        ("traits", "Traits"),
        ("actions", "Actions"),
        ("bonus_actions", "Bonus Actions"),
        ("reactions", "Reactions"),
    ):
        entries = getattr(monster, attribute_name)
        if entries:
            lines.append(f"        - {label}:")
            for entry in entries:
                lines.append(f"            > {entry['name']}: {entry['description']}")

    return "\n".join(lines)
