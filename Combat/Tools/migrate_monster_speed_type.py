"""One-time migration (pass 2): split ExtendedCombatantData's single `speed`
string into speed_ground_ft/speed_fly_ft/speed_climb_ft/speed_special_rules,
and split `monster_type` into monster_type/alignment/size.

Unlike migrate_monster_enums.py (which replaces one kwarg's *value*), this
replaces a whole `keyword` node (`arg=value`) with several new keywords,
since one field becomes many. Splices by exact AST source position, same
safety approach as pass 1. Safe to re-run: a file whose imports already
include `speed_ground_ft` is skipped.

Usage: python -m Combat.Tools.migrate_monster_speed_type
"""

import ast
import glob

from Combat.Tools.monster_enum_format import parse_monster_type, parse_speed


def _offset_index(text: str) -> list[int]:
    offsets = [0]
    for line in text.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _node_span(node: ast.AST, line_starts: list[int]) -> tuple[int, int]:
    start = line_starts[node.lineno - 1] + node.col_offset
    end = line_starts[node.end_lineno - 1] + node.end_col_offset
    return start, end


def _speed_replacement(raw: str, report: dict, path: str) -> str:
    ground, fly, climb, special, flags = parse_speed(raw)
    for flag in flags:
        report.setdefault("speed_flags", []).append(f"{path}: {flag}")
    return (
        f"speed_ground_ft={ground!r}, speed_fly_ft={fly!r}, "
        f"speed_climb_ft={climb!r}, speed_special_rules={special!r}"
    )


def _monster_type_replacement(raw: str, report: dict, path: str) -> str:
    size_name, monster_type_text, alignment_name, flags = parse_monster_type(raw)
    for flag in flags:
        report.setdefault("monster_type_flags", []).append(f"{path}: {flag}")
    size_src = f"Size.{size_name}" if size_name else "None"
    alignment_src = f"Alignment.{alignment_name}" if alignment_name else "None"
    return f"size={size_src}, monster_type={monster_type_text!r}, alignment={alignment_src}"


def migrate_file(path: str, report: dict) -> bool:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if "speed_ground_ft" in text:
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
            if kw.arg not in ("speed", "monster_type"):
                continue
            try:
                current_value = ast.literal_eval(kw.value)
            except (ValueError, SyntaxError):
                report.setdefault("literal_eval_failed", []).append(f"{path}: {kw.arg}")
                continue

            if kw.arg == "speed":
                new_src = _speed_replacement(current_value, report, path)
            else:
                new_src = _monster_type_replacement(current_value, report, path)

            start, end = _node_span(kw, line_starts)
            replacements.append((start, end, new_src))

    if not replacements:
        return False

    # Add Size/Alignment to the `from Combat.Definitions import ...` statement,
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
        all_names = sorted(existing_names | {"Size", "Alignment"})
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
