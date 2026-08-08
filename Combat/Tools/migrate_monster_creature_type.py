"""One-time migration (pass 3): turn ExtendedCombatantData's free-text
`monster_type` string ("Dragon (Metallic)", "Swarm of Tiny Beasts", ...) into
a `MonsterType` enum member plus a `monster_type_note` string for whatever
subtype/swarm qualifier doesn't fit the enum.

Same whole-keyword splice approach as migrate_monster_speed_type.py, since one
field becomes two. Safe to re-run: a file whose imports already include
`monster_type_note` is skipped.

Usage: python -m Combat.Tools.migrate_monster_creature_type
"""

import ast
import glob

from Combat.Tools.monster_enum_format import parse_creature_type


def _offset_index(text: str) -> list[int]:
    offsets = [0]
    for line in text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _node_span(node: ast.AST, line_starts: list[int]) -> tuple[int, int]:
    start = line_starts[node.lineno - 1] + node.col_offset
    end = line_starts[node.end_lineno - 1] + node.end_col_offset
    return start, end


def _monster_type_replacement(raw: str, report: dict, path: str) -> str:
    enum_name, note, flags = parse_creature_type(raw)
    for flag in flags:
        report.setdefault("creature_type_flags", []).append(f"{path}: {flag}")
    type_src = f"MonsterType.{enum_name}" if enum_name else "None"
    return f"monster_type={type_src}, monster_type_note={note!r}"


def migrate_file(path: str, report: dict) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if "monster_type_note" in text:
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
        is_direct_init = isinstance(func, ast.Name) and func.id == "ExtendedCombatantData"
        if not (is_super_init or is_direct_init):
            continue

        for kw in node.keywords:
            if kw.arg != "monster_type":
                continue
            try:
                current_value = ast.literal_eval(kw.value)
            except (ValueError, SyntaxError):
                report.setdefault("literal_eval_failed", []).append(f"{path}: {kw.arg}")
                continue
            if not isinstance(current_value, str):
                continue  # already migrated to an enum member (shouldn't happen given the guard above)

            new_src = _monster_type_replacement(current_value, report, path)
            start, end = _node_span(kw, line_starts)
            replacements.append((start, end, new_src))

    if not replacements:
        return False

    # Add MonsterType to the `from Combat.Definitions import ...` statement,
    # whatever names/formatting it currently has (an autoformatter reformats
    # this import per-file, so match it structurally via AST, not by literal text).
    combat_defs_import = next(
        (
            n for n in tree.body
            if isinstance(n, ast.ImportFrom) and n.module == "Combat.Definitions"
        ),
        None,
    )
    if combat_defs_import is not None:
        existing_names = {alias.name for alias in combat_defs_import.names}
        all_names = sorted(existing_names | {"MonsterType"})
        new_import_src = "from Combat.Definitions import (\n" + "".join(
            f"    {n},\n" for n in all_names
        ) + ")"
        start, end = _node_span(combat_defs_import, line_starts)
        replacements.append((start, end, new_import_src))
    else:
        report.setdefault("import_not_found", []).append(path)

    replacements.sort(key=lambda r: r[0], reverse=True)
    for start, end, new_src in replacements:
        text = text[:start] + new_src + text[end:]

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
