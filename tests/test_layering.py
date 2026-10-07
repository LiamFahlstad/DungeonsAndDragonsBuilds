"""Imports only point down (Notes/engine-simplification-plan.md, section 2b).

Every project module belongs to a layer (LAYER_OF), and each layer may import
only the layers listed for it in MAY_IMPORT. On top of that:

- Nothing uses `if TYPE_CHECKING:`. A circular import gets removed, not hidden.
- Nothing uses `typing.cast` or the sheet writer's `_as(...)` to get a
  concrete type back: the folder structure should hand out concrete types.

Each rule starts with an allowlist of today's offenders. Every refactor step
that cleans a file removes it from its list: a file that is on a list but
already clean fails the test too, so the lists can't go stale. An allowlist
entry ending in "/" covers every file in that folder.
"""

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIPPED_DIRS = {
    ".claude",
    ".git",
    ".venv",
    "venv",
    "Output",
    "SourceTexts",
    "__pycache__",
}

# Module (dotted prefix) -> layer. The longest matching prefix wins, so a
# file can sit in a different layer than its folder (Model.Records).
LAYER_OF = {
    "Core": "core",
    "Utils": "helpers",
    "Model": "model",
    # Plain records the whole Model shares; they import only Core.
    "Model.Records": "records",
    "CharacterContent": "content",
    # The monster catalog: stat blocks that builds use for wild shapes and
    # companions. Data, not the combat engine.
    "Combat.Monsters": "creatures",
    "Builds": "builds",
    "Presentation": "presentation",
    "Combat": "combat",
    # Entry points and tooling may import anything.
    "RunBuildGroups": "apps",
    "RunCharacterCreator": "apps",
    "RunCharacterCreatorUI": "apps",
    "RunCombatSimulator": "apps",
    "RunItemSheets": "apps",
    "Scrapers": "apps",
    "tests": "apps",
}

_BELOW_BUILDS = {"core", "helpers", "records", "model", "content", "creatures"}

MAY_IMPORT = {
    "core": {"core"},
    "helpers": {"core", "helpers"},
    "records": {"core", "records"},
    "model": {"core", "helpers", "records", "model"},
    "content": {"core", "helpers", "records", "model", "content"},
    "creatures": {"core", "helpers", "records", "model", "creatures"},
    "builds": _BELOW_BUILDS | {"builds", "presentation"},
    "presentation": _BELOW_BUILDS | {"builds", "presentation"},
    "combat": _BELOW_BUILDS | {"builds", "presentation", "combat"},
    "apps": set(LAYER_OF.values()),
}

# (file or folder/, layer it imports but shouldn't) - today's offenders.
LAYER_ALLOWLIST: set[tuple[str, str]] = {
    # Content renders companion and wild shape stat blocks itself (Step 6
    # moves rendering out of content).
    ("CharacterContent/Features/ClassFeatures/Druid/WildShapeForms.py", "presentation"),
    (
        "CharacterContent/Features/ClassFeatures/Ranger/PrimalCompanions.py",
        "presentation",
    ),
    (
        "CharacterContent/Features/SubClassFeatures2014/Druid/DruidWildfireFeatures.py",
        "presentation",
    ),
    (
        "CharacterContent/Features/SubClassFeatures2014/Ranger/RangerDrakewardenFeatures.py",
        "presentation",
    ),
}

TYPE_CHECKING_ALLOWLIST: set[str] = set()

# Narrowing a value back to a concrete type (Steps 9 and 13 remove these).
CAST_ALLOWLIST: set[str] = {"Model/Recorder.py"}
AS_ALLOWLIST: set[str] = {"Presentation/CharacterSheetWriters.py"}

# Content that reads a character (features, items, tools, invocations)
# reads it through Model.View.CharacterView, never the concrete Character.
CONTENT_READERS = (
    "CharacterContent/Features/",
    "CharacterContent/Items/",
    "CharacterContent/ToolProficiencies/",
    "CharacterContent/Invocations/",
)
# The weapon base reads character.ledger until Step 10 moves that math
# to AttackProfile.
CHARACTER_IMPORT_ALLOWLIST: set[str] = {"CharacterContent/Items/Weapons/Base.py"}


def _project_files():
    for path in sorted(REPO.rglob("*.py")):
        relative = path.relative_to(REPO)
        if SKIPPED_DIRS.isdisjoint(relative.parts[:-1]):
            yield relative.as_posix(), path


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8", errors="ignore"))


def _module_name(relative_path: str) -> str:
    """The dotted name of a project file: Model/Skills.py is Model.Skills,
    and a package's __init__.py is the package itself."""
    parts = relative_path.removesuffix(".py").split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _layer(module: str) -> str | None:
    """The layer of a dotted module name, or None if it isn't ours (stdlib,
    third-party)."""
    best = None
    for prefix in LAYER_OF:
        if module == prefix or module.startswith(prefix + "."):
            if best is None or len(prefix) > len(best):
                best = prefix
    return LAYER_OF[best] if best is not None else None


def _is_module(dotted: str) -> bool:
    path = REPO.joinpath(*dotted.split("."))
    return path.with_suffix(".py").exists() or path.is_dir()


def _imported_modules(tree: ast.AST, own_module: str, is_package: bool) -> set[str]:
    """Every module imported anywhere in the file (also inside functions),
    as a dotted name. `from X import Y` counts as importing X.Y when Y is a
    module, so `from Presentation import Html` lands in Html's layer."""
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                package = own_module.split(".")
                if not is_package:
                    package = package[:-1]
                package = package[: len(package) - (node.level - 1)]
                base = ".".join([*package, base] if base else package)
            for alias in node.names:
                candidate = f"{base}.{alias.name}"
                modules.add(candidate if _is_module(candidate) else base)
    return modules


def _check_allowlist(offenders: set, allowlist: set, rule: str) -> None:
    new = sorted(offenders - allowlist)
    stale = sorted(allowlist - offenders)
    assert not new, f"{rule}: new offenders {new}"
    assert (
        not stale
    ), f"{rule}: these are clean now, remove them from the allowlist: {stale}"


def test_every_project_file_has_a_layer():
    """A new top-level folder or script must be placed in LAYER_OF, or its
    imports would go unchecked."""
    unplaced = [
        name for name, _ in _project_files() if _layer(_module_name(name)) is None
    ]
    assert not unplaced, f"Add these to LAYER_OF: {unplaced}"


def test_imports_point_down():
    offenders: set[tuple[str, str]] = set()
    for name, path in _project_files():
        own_module = _module_name(name)
        own_layer = _layer(own_module)
        assert own_layer is not None
        allowed = MAY_IMPORT[own_layer]
        imported = _imported_modules(
            _parse(path), own_module, is_package=name.endswith("__init__.py")
        )
        for module in imported:
            layer = _layer(module)
            if layer is not None and layer not in allowed:
                offenders.add((name, layer))

    collapsed = {(_allowlist_key(name, layer), layer) for name, layer in offenders}
    _check_allowlist(collapsed, LAYER_ALLOWLIST, "Layer imports")


def _allowlist_key(name: str, layer: str) -> str:
    """The folder entry that covers this offender, if there is one, so the
    stale check compares like with like; otherwise the file itself."""
    for entry, entry_layer in LAYER_ALLOWLIST:
        if entry_layer == layer and entry.endswith("/") and name.startswith(entry):
            return entry
    return name


def test_no_type_checking_blocks():
    offenders = set()
    for name, path in _project_files():
        source = path.read_text(encoding="utf-8", errors="ignore")
        # Cheap text filter first: the repo has big generated files.
        if "TYPE_CHECKING" in source and _uses_type_checking(ast.parse(source)):
            offenders.add(name)
    _check_allowlist(offenders, TYPE_CHECKING_ALLOWLIST, "TYPE_CHECKING")


def _uses_type_checking(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "TYPE_CHECKING":
            return True
        if isinstance(node, ast.Attribute) and node.attr == "TYPE_CHECKING":
            return True
        if isinstance(node, ast.ImportFrom) and any(
            alias.name == "TYPE_CHECKING" for alias in node.names
        ):
            return True
    return False


def test_content_reads_character_through_view():
    offenders = set()
    for name, path in _project_files():
        if not name.startswith(CONTENT_READERS):
            continue
        imported = _imported_modules(
            _parse(path), _module_name(name), is_package=name.endswith("__init__.py")
        )
        if "Model.Character" in imported:
            offenders.add(name)
    _check_allowlist(
        offenders, CHARACTER_IMPORT_ALLOWLIST, "Model.Character in content"
    )


# The Ledger's parts record facts typed with Core and Model.Records types
# only - never a content object - so they need no content type to name.
LEDGER_PARTS = (
    "AbilityIncreases",
    "AbilityRequirements",
    "ArmorClass",
    "Bonuses",
    "CarryingCapacity",
    "Defenses",
    "EquipmentTraining",
    "HitPoints",
    "Initiative",
    "Languages",
    "Recorder",
    "SavingThrows",
    "Senses",
    "Skills",
    "Speed",
    "Spellcasting",
    "WeaponBonuses",
    "WornArmor",
)
LEDGER_PART_MAY_IMPORT = (
    "Core",
    "Model.Records",
    "Model.View",
    "Model.Bonuses",
    "Model.Recorder",
)


def test_ledger_parts_record_facts_only():
    offenders = []
    for part in LEDGER_PARTS:
        name = f"Model/{part}.py"
        path = REPO / name
        imported = _imported_modules(_parse(path), _module_name(name), is_package=False)
        for module in imported:
            if _layer(module) is None:
                continue  # stdlib or third-party
            if not any(
                module == allowed or module.startswith(allowed + ".")
                for allowed in LEDGER_PART_MAY_IMPORT
            ):
                offenders.append((name, module))
    assert (
        not offenders
    ), f"Ledger parts may import only {LEDGER_PART_MAY_IMPORT}: {offenders}"


def test_no_cast():
    offenders = set()
    for name, path in _project_files():
        source = path.read_text(encoding="utf-8", errors="ignore")
        if "cast" in source and _uses_cast(ast.parse(source)):
            offenders.add(name)
    _check_allowlist(offenders, CAST_ALLOWLIST, "typing.cast")


def _uses_cast(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "typing":
            if any(alias.name == "cast" for alias in node.names):
                return True
        if isinstance(node, ast.Attribute) and node.attr == "cast":
            if isinstance(node.value, ast.Name) and node.value.id == "typing":
                return True
    return False


def test_no_as_narrowing():
    offenders = set()
    for name, path in _project_files():
        source = path.read_text(encoding="utf-8", errors="ignore")
        if "_as" in source and _uses_as(ast.parse(source)):
            offenders.add(name)
    _check_allowlist(offenders, AS_ALLOWLIST, "_as(...) narrowing")


def _uses_as(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_as":
            return True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "_as":
                return True
    return False
