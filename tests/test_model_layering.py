"""Imports only point down (Notes/model-refactor-plan.md, section 2a).

- Nothing uses `if TYPE_CHECKING:`. A circular import gets removed, not hidden.
- `Model/` never imports `CharacterContent`, `Builds` or `Utils`, not even for
  type hints. It names content only through Protocols.

Each rule starts with an allowlist of today's offenders. Every refactor step
that cleans a file removes it from the list: a file that is on the list but
already clean fails the test too, so the list can't go stale.
"""

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIPPED_DIRS = {".claude", ".git", ".venv", "venv", "Output", "SourceTexts"}

# Removed as Steps 3 and 4 of the plan clean them.
TYPE_CHECKING_ALLOWLIST = {
    "CharacterContent/Items/Weapons/Improvements.py",
    "CharacterContent/Spells/SpellFactory/Writer.py",
    "Model/ArmorClass.py",
    "Model/Bonuses.py",
    "Model/Character.py",
    "Model/HitPoints.py",
    "Model/Initiative.py",
    "Model/Inventory.py",
    "Model/SavingThrows.py",
    "Model/Skills.py",
    "Model/Speed.py",
    "Utils/BuildGroupSheetWriter.py",
}

# Removed as Step 4 of the plan cleans them.
MODEL_IMPORT_ALLOWLIST = {
    "Model/Character.py",
    "Model/Inventory.py",
}

FORBIDDEN_IN_MODEL = {"CharacterContent", "Builds", "Utils"}


def _project_files(root: Path = REPO):
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(REPO)
        if SKIPPED_DIRS.isdisjoint(relative.parts[:-1]):
            yield relative.as_posix(), path


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


def _imported_packages(tree: ast.AST) -> set[str]:
    """The top-level package of every import, anywhere in the module
    (including inside `if` blocks and functions)."""
    packages = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            packages.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            packages.add(node.module.split(".")[0])
    return packages


def _check_allowlist(offenders: set[str], allowlist: set[str], rule: str) -> None:
    new = sorted(offenders - allowlist)
    stale = sorted(allowlist - offenders)
    assert not new, f"{rule}: new offenders {new}"
    assert (
        not stale
    ), f"{rule}: these files are clean now, remove them from the allowlist: {stale}"


def test_no_type_checking_blocks():
    offenders = set()
    for name, path in _project_files():
        source = path.read_text(encoding="utf-8", errors="ignore")
        # Cheap text filter first: the repo has big generated files.
        if "TYPE_CHECKING" in source and _uses_type_checking(ast.parse(source)):
            offenders.add(name)
    _check_allowlist(offenders, TYPE_CHECKING_ALLOWLIST, "TYPE_CHECKING")


def test_model_imports_point_down():
    offenders = set()
    for name, path in _project_files(REPO / "Model"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if _imported_packages(tree) & FORBIDDEN_IN_MODEL:
            offenders.add(name)
    _check_allowlist(offenders, MODEL_IMPORT_ALLOWLIST, "Model imports")
