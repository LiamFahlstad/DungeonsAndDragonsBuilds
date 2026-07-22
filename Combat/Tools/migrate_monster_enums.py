"""One-time migration: rewrite existing Combat/Monsters/CR_*/monsters.py and
monsters_homebrew.py files to use the enum/dataclass-based ExtendedCombatantData
fields (Ability/Skill/DamageType/DamageTypeEntry/Condition/MonsterAbility)
instead of raw strings and dicts.

Splices new source text in place of each affected keyword argument's value
(using exact AST source positions), leaving everything else in the file --
formatting, comments, class ordering -- untouched. Safe to re-run: a file
whose imports already include DamageTypeEntry is skipped.

Usage: python Combat/Tools/migrate_monster_enums.py
"""

import ast
import glob

from Combat.Tools.monster_enum_format import (
    format_ability_list,
    format_ability_scores,
    format_condition_list,
    format_damage_entries,
    format_skills,
)

OLD_IMPORT = "from Combat.Definitions import ExtendedCombatantData"
NEW_IMPORT = """from Combat.Definitions import (
    Condition,
    DamageType,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterAbility,
    Skill,
)
from Core.Definitions import Ability"""

# kwarg name -> formatter. Formatters returning a tuple also report unmapped values.
_SIMPLE_FIELDS = {
    "ability_scores": format_ability_scores,
    "saving_throws": format_ability_scores,
}
_TUPLE_FIELDS = {
    "skills": format_skills,
    "damage_vulnerabilities": format_damage_entries,
    "damage_resistances": format_damage_entries,
    "damage_immunities": format_damage_entries,
    "condition_immunities": format_condition_list,
}
_ABILITY_LIST_FIELDS = (
    "traits",
    "actions",
    "bonus_actions",
    "reactions",
    "legendary_actions",
    "lair_actions",
    "mythic_actions",
)


def _offset_index(text: str) -> list[int]:
    """Return the absolute character offset of the start of each line (1-indexed access)."""
    offsets = [0]
    for line in text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _node_span(node: ast.AST, line_starts: list[int]) -> tuple[int, int]:
    start = line_starts[node.lineno - 1] + node.col_offset
    end = line_starts[node.end_lineno - 1] + node.end_col_offset
    return start, end


def migrate_file(path: str, report: dict) -> bool:
    """Returns True if the file was changed."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if "DamageTypeEntry" in text:
        return False  # already migrated

    tree = ast.parse(text, filename=path)
    line_starts = _offset_index(text)

    replacements: list[tuple[int, int, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_super_init = (
            isinstance(func, ast.Attribute)
            and func.attr == "__init__"
            and isinstance(func.value, ast.Call)
            and isinstance(func.value.func, ast.Name)
            and func.value.func.id == "super"
        )
        if not is_super_init:
            continue

        for kw in node.keywords:
            if kw.arg is None:
                continue
            try:
                current_value = ast.literal_eval(kw.value)
            except (ValueError, SyntaxError):
                report.setdefault("literal_eval_failed", []).append(f"{path}: {kw.arg}")
                continue

            new_src = None
            if kw.arg in _SIMPLE_FIELDS:
                new_src = _SIMPLE_FIELDS[kw.arg](current_value)
            elif kw.arg in _TUPLE_FIELDS:
                new_src, unmapped = _TUPLE_FIELDS[kw.arg](current_value)
                if unmapped:
                    report.setdefault("unmapped", []).append(
                        f"{path}: {kw.arg} -> {unmapped}"
                    )
            elif kw.arg in _ABILITY_LIST_FIELDS:
                new_src = format_ability_list(current_value)

            if new_src is not None:
                start, end = _node_span(kw.value, line_starts)
                replacements.append((start, end, new_src))

    if not replacements:
        return False

    # Splice from the end of the file backwards so earlier offsets stay valid.
    replacements.sort(key=lambda r: r[0], reverse=True)
    for start, end, new_src in replacements:
        text = text[:start] + new_src + text[end:]

    if OLD_IMPORT in text:
        count = text.count(OLD_IMPORT)
        if count != 1:
            report.setdefault("import_line_ambiguous", []).append(f"{path}: {count} occurrences")
        else:
            text = text.replace(OLD_IMPORT, NEW_IMPORT)
    else:
        report.setdefault("import_line_missing", []).append(path)

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return True


def main():
    files = sorted(
        glob.glob("Combat/Monsters/CR_*/monsters.py")
        + glob.glob("Combat/Monsters/CR_*/monsters_homebrew.py")
    )
    report: dict = {}
    changed = 0
    for path in files:
        try:
            if migrate_file(path, report):
                changed += 1
        except SyntaxError as e:
            report.setdefault("syntax_error", []).append(f"{path}: {e}")

    print(f"Migrated {changed}/{len(files)} files.")
    for category, items in report.items():
        print(f"\n{category} ({len(items)}):")
        for item in items:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
