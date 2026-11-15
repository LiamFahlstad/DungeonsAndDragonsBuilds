"""Token-cheap access to the Map Painter's code and its painted maps.

    python .claude/skills/map-painter/map_tool.py index [--grep WORD]   # every class/def of the painter's files, file:line + first doc line
    python .claude/skills/map-painter/map_tool.py maps                  # every painted map: campaign, encounter, size, what's painted
    python .claude/skills/map-painter/map_tool.py show <encounter|path> # one map as ASCII (a 17 KB JSON is ~1 KB here)
    python .claude/skills/map-painter/map_tool.py paint <encounter|path> <layer> <value> <cells>...
    python .claude/skills/map-painter/map_tool.py start <encounter|path> <name> <cell>|-

Cells are named as on the map ("C7"; a block "C7:F9"). Layers for paint:
ground (open|wall|difficult|water), height (feet), light (bright|dim|dark),
object (a preset name, or none). The index is read from the code each run
(ast), so it's never stale."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from Combat.Arena.geometry import Cell  # noqa: E402
from Combat.Arena.maps import MapDesign, read_map, write_map  # noqa: E402
from Combat.Arena.terrain import (  # noqa: E402
    DARK,
    DIFFICULT,
    DIM,
    GROUNDS,
    LIGHTS,
    OBJECT_PRESETS,
    WALL,
    WATER,
)

# The painter's code, and in shared files only the parts that are the painter's.
FILES: dict[str, set[str] | None] = {
    "Combat/Arena/terrain.py": None,
    "Combat/Arena/maps.py": None,
    "Combat/CombatUIQt/map_painter.py": None,
    "Combat/Arena/arena.py": {
        "ArenaSettings",
        "standable",
        "height_of",
        "copy",
        "to_dict",
        "from_dict",
        "has_climb_speed",
        "reachable",
        "fits_at",
        "distance_ft",
        "distance_to_cell_ft",
    },
    "Combat/Arena/geometry.py": {"between", "edges", "with_height"},
    "Combat/CombatUIQt/arena_view.py": {"draw_terrain", "_draw_object", "show_rows"},
    "Combat/CombatUIQt/arena_mixin.py": {
        "_place_on_arena",
        "_distance_note",
        "_arena_distance",
        "_move_combatant",
        "_remind_lasting_areas",
        "hazards_under",
        "obscured_text",
    },
    "Combat/CombatUIQt/logging_mixin.py": {"_load_log_from_path"},
    "Combat/CombatUIQt/undo.py": {"UndoPoint", "capture", "restore", "changed_since"},
    "Combat/CombatUIQt/window_mixin.py": None,  # filtered by --grep only
    "tests/test_arena_terrain.py": None,
    "tests/test_combat_ui_map_painter.py": None,
}
_WINDOW_WORDS = ("Map Painter", "_map_painter")


def _shown(path: Path) -> str:
    """The path from the repo root when it's in the repo."""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _first_line(node) -> str:
    doc = ast.get_docstring(node) or ""
    return doc.strip().splitlines()[0] if doc.strip() else ""


def index(grep: str | None):
    for rel, wanted in FILES.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        lines = []
        if rel.endswith("window_mixin.py"):
            for number, line in enumerate(text.splitlines(), 1):
                if any(word in line for word in _WINDOW_WORDS):
                    lines.append(f"  {number}: {line.strip()}")
        else:
            for node in ast.walk(ast.parse(text)):
                if not isinstance(
                    node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    continue
                if wanted is not None and node.name not in wanted:
                    continue
                kind = "class" if isinstance(node, ast.ClassDef) else "def"
                lines.append(
                    f"  {node.lineno}: {kind} {node.name} - {_first_line(node)}"
                )
            lines.sort(key=lambda l: int(l.split(":")[0]))
        if grep:
            lines = [l for l in lines if grep.lower() in l.lower()]
        if lines:
            print(rel)
            print("\n".join(lines))


def _map_files() -> list[Path]:
    return sorted((ROOT / "Combat" / "Campaigns").glob("*/Maps/*.json"))


def _resolve(target: str) -> Path:
    path = Path(target)
    if path.suffix == ".json":
        return path if path.is_absolute() else ROOT / path
    found = [p for p in _map_files() if p.stem == target]
    if len(found) == 1:
        return found[0]
    if found:
        sys.exit(f"{target} is in several campaigns: {[str(p) for p in found]}")
    campaigns = sorted((ROOT / "Combat" / "Campaigns").glob("*/encounters.py"))
    for config in campaigns:  # a new map for an encounter id that exists
        if re.search(rf'id="{re.escape(target)}"', config.read_text(encoding="utf-8")):
            return config.parent / "Maps" / f"{target}.json"
    sys.exit(f"No map or encounter named {target!r}")


def _counts(design: MapDesign) -> str:
    spots = design.settings.terrain.cells.values()
    parts = [
        f"{sum(s.ground == g for s in spots)} {g}"
        for g in (WALL, DIFFICULT, WATER)
        if any(s.ground == g for s in spots)
    ]
    if any(s.height_ft for s in spots):
        parts.append(f"{sum(bool(s.height_ft) for s in spots)} raised/lowered")
    if any(s.light != "bright" for s in spots):
        parts.append(f"{sum(s.light != 'bright' for s in spots)} dim/dark")
    things = sorted({s.thing.name for s in spots if s.thing is not None})
    if things:
        parts.append("objects: " + ", ".join(things))
    return "; ".join(parts) or "nothing painted"


def list_maps():
    for path in _map_files():
        design = read_map(path)
        if design is None:
            continue
        s = design.settings
        print(
            f"{path.parent.parent.name}/{path.stem}: {s.width}x{s.height}"
            f" ({_counts(design)}); {len(design.starts)} starts"
        )


_GROUND_CH = {WALL: "#", DIFFICULT: ":", WATER: "~"}


def show(target: str):
    path = _resolve(target)
    design = read_map(path)
    if design is None:
        sys.exit(f"No map at {path}")
    s, t = design.settings, design.settings.terrain
    shape = s.distance_rule.shape
    starts = {cell: name for name, cell in design.starts.items()}
    letters = {}
    for spot in t.cells.values():
        if spot.thing is not None and spot.thing.name not in letters:
            letters[spot.thing.name] = "abcdefghijklmnopqrstuvwxyz"[len(letters) % 26]
    print(f"{_shown(path)}: {s.width}x{s.height} cells of {s.cell_ft} ft., {s.rule}")
    cols = [shape.labels(Cell(c, 0))[0] for c in range(s.width)]
    print("    " + "".join(f"{c[-1]}" for c in cols))
    heights = False
    for r in range(s.height):
        row = []
        for c in range(s.width):
            cell = Cell(c, r)
            spot = t.at(cell)
            ch = "."
            if spot.ground in _GROUND_CH:
                ch = _GROUND_CH[spot.ground]
            if spot.thing is not None:
                ch = letters[spot.thing.name]
            if cell in starts:
                ch = "@"
            if spot.light == DARK and ch == ".":
                ch = " "
            elif spot.light == DIM and ch == ".":
                ch = ","
            heights |= bool(spot.height_ft)
            row.append(ch)
        print(f"{r + 1:>3} " + "".join(row))
    print("Legend: . open  # wall  : difficult  ~ water  , dim  (space) dark  @ start")
    for name, letter in letters.items():
        thing = next(
            x.thing for x in t.cells.values() if x.thing and x.thing.name == name
        )
        print(f"  {letter} {thing.describe()}")
    if heights:
        print("Heights (ft., blank = 0):")
        for r in range(s.height):
            row = [t.height(Cell(c, r)) for c in range(s.width)]
            if any(row):
                print(f"{r + 1:>3} " + " ".join(f"{h:>3}" if h else "  ." for h in row))
    for name, cell in design.starts.items():
        print(f"  start {name}: {shape.cell_name(cell)}")


def _cell(name: str) -> Cell:
    match = re.fullmatch(r"([A-Za-z]+)(\d+)", name)
    if not match:
        sys.exit(f"Not a cell name: {name!r} (like C7)")
    col = 0
    for ch in match.group(1).upper():
        col = col * 26 + ord(ch) - ord("A") + 1
    return Cell(col - 1, int(match.group(2)) - 1)


def _cells(specs: list[str], design: MapDesign) -> list[Cell]:
    shape = design.settings.distance_rule.shape
    cells = []
    for spec in specs:
        a, _, b = spec.partition(":")
        cells += shape.between(_cell(a), _cell(b or a))
    return cells


def _load(target: str) -> tuple[Path, MapDesign]:
    path = _resolve(target)
    return path, read_map(path) or MapDesign()


def paint(target: str, layer: str, value: str, specs: list[str]):
    path, design = _load(target)
    terrain = design.settings.terrain
    if layer == "ground" and value in GROUNDS:
        change = {"ground": value}
    elif layer == "light" and value in LIGHTS:
        change = {"light": value}
    elif layer == "height" and re.fullmatch(r"-?\d+", value):
        change = {"height_ft": int(value)}
    elif layer == "object":
        preset = next(
            (p for p in OBJECT_PRESETS if p.name.lower() == value.lower()), None
        )
        if preset is None and value != "none":
            sys.exit(f"Presets: {', '.join(p.name for p in OBJECT_PRESETS)}, or none")
        change = {"thing": preset}
    else:
        sys.exit(f"Bad layer/value {layer} {value}: see the module docstring")
    cells = [c for c in _cells(specs, design) if design.settings.on_map(c)]
    changed = sum(terrain.change(cell, **change) for cell in cells)
    write_map(path, design)
    print(f"{changed} of {len(cells)} cells changed in {_shown(path)}")


def start(target: str, name: str, spec: str):
    path, design = _load(target)
    if spec == "-":
        design.starts.pop(name, None)
    else:
        design.starts[name] = _cell(spec)
    write_map(path, design)
    print(f"{name}: {spec} in {_shown(path)}")


def main(argv: list[str]):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # "Kivi Jätti" on a cp1252 console
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    command, rest = argv[0], argv[1:]
    if command == "index":
        grep = rest[rest.index("--grep") + 1] if "--grep" in rest else None
        index(grep)
    elif command == "maps":
        list_maps()
    elif command == "show" and len(rest) == 1:
        show(rest[0])
    elif command == "paint" and len(rest) >= 4:
        paint(rest[0], rest[1], rest[2], rest[3:])
    elif command == "start" and len(rest) == 3:
        start(*rest)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
