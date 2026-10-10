"""Shared by the snapshot tests (test_build_snapshots.py) and the order
invariance tests (test_order_invariance.py): every build, the golden files,
the stats a build is compared on, and rendering a build's sheets to hashes.

Pages are captured in memory as they're written (CapturingSheetWriter) rather
than read back from disk: on Windows the antivirus scans a freshly written file
on its first open, which made reading pages back ~85% of the render time.

Set SNAPSHOT_DUMP_DIR=<dir> to also keep every page the snapshot test renders,
at <dir>/<build>/<mode>/<page>. Hashes only say *that* a page changed; a
`diff -r` between two dumps (say, one from the refactor-baseline tag and one
from the working tree) says *what* changed. Dump outside the repo.
"""

import hashlib
import io
import json
import os
import shutil
from pathlib import Path
from typing import Callable, Optional, TextIO

from Core.Definitions import Ability, Skill
from Presentation.FeatureCards import DescriptionMode
from Model.Character import Character
from RunCharacterCreator import BuildSelector, ExampleSelector
from Presentation.CharacterSheetWriters import (
    HtmlCharacterSheetWriter,
    get_output_folder,
)

ALL_BUILDS = {**BuildSelector.builds(), **ExampleSelector.builds()}
BUILD_PARAMS = sorted(ALL_BUILDS)

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"
STATS_PATH = SNAPSHOT_DIR / "build_stats.json"
HASHES_PATH = SNAPSHOT_DIR / "sheet_hashes.json"

UPDATE_SNAPSHOTS = os.environ.get("UPDATE_SNAPSHOTS") == "1"
SNAPSHOT_DUMP_DIR = os.environ.get("SNAPSHOT_DUMP_DIR")

SHEET_MODES: tuple[tuple[str, DescriptionMode], ...] = (
    ("full", None),
    ("concise", "concise"),
)


def build(name: str) -> Character:
    """A fresh Character for the build registered as `name`."""
    return ALL_BUILDS[name]().build()


def compute_stats(data: Character) -> dict:
    character = data.validate()
    return {
        "scores": [character.get_ability_score(a) for a in Ability],
        "ac": character.calculate_armor_class(),
        "hp": character.calculate_hit_points(),
        "init": character.calculate_initiative(),
        "init_roll": str(character.initiative_roll_condition),
        "speed": character.calculate_speed(),
        "skills": [character.get_skill_modifier(s) for s in Skill],
        "skill_abilities": [str(character.get_skill_ability(s)) for s in Skill],
        "skill_rolls": [
            f"{character.get_skill_roll_condition(s)}"
            f"{character.get_skill_roll_condition_reasons(s)}"
            for s in Skill
        ],
        "skill_sources": [
            sorted(
                f"{bonus.value}:{bonus.source}"
                for bonus in character.get_skill_bonus_sources(s)
            )
            for s in Skill
        ],
        "saves": [character.get_saving_throw_modifier(a) for a in Ability],
        "save_prof": [character.is_proficient_in_saving_throw(a) for a in Ability],
        "expertise": [character.has_expertise_in_skill(s) for s in Skill],
        "slots": sorted(character.spell_slots.items()) if character.spell_slots else [],
        "pact": sorted(character.pact_magic_slots.items()),
        "resist": sorted(
            (str(damage_type), sorted(sources))
            for damage_type, sources in character.damage_resistances().items()
        ),
        "immune": sorted(
            (str(damage_type), sorted(sources))
            for damage_type, sources in character.damage_immunities().items()
        ),
        "senses": sorted(
            (str(sense), rng) for sense, rng in character.senses().items()
        ),
        "weapons": [
            (
                weapon.name,
                weapon.calculate_total_attack_roll_bonus_int(character),
                weapon.calculate_damage_bonus_int(character),
            )
            for weapon in data.weapons
        ],
        "carry": character.get_carrying_capacity(),
    }


class _CapturedFile(io.BytesIO):
    """A page's bytes, handed to `on_close` when the page is closed."""

    def __init__(self, on_close: Callable[[bytes], None]):
        super().__init__()
        self._on_close = on_close

    def close(self) -> None:
        if not self.closed:
            self._on_close(self.getvalue())
        super().close()


class CapturingSheetWriter(HtmlCharacterSheetWriter):
    """Renders a sheet into `pages` ({path relative to the output folder:
    bytes}) instead of onto disk. The bytes are exactly what the real writer
    would write: same encoding, same newline translation."""

    def __init__(self, output_folder: Path):
        self._root = output_folder
        self.pages: dict[str, bytes] = {}

    def _open_page(self, path: str | Path) -> TextIO:
        name = Path(path).relative_to(self._root).as_posix()

        def keep(content: bytes) -> None:
            self.pages[name] = content

        return io.TextIOWrapper(_CapturedFile(keep), encoding="utf-8")


def render_and_hash(
    name: str,
    tmp_path: Path,
    prepare: Optional[Callable[[Character], Character]] = None,
    dump: bool = False,
) -> dict[str, dict[str, str]]:
    """Render `name` in full and concise mode and hash every page, per mode.
    `prepare` turns each freshly built Character into the one rendered
    (the order tests rebuild it from reordered sources). `dump` copies the pages to
    SNAPSHOT_DUMP_DIR, when that's set."""
    result = {}
    for mode_key, description_mode in SHEET_MODES:
        data = build(name)
        if prepare is not None:
            data = prepare(data)
        folder_name = os.path.basename(get_output_folder(data, description_mode))
        output_folder = tmp_path / folder_name
        writer = CapturingSheetWriter(output_folder)
        writer.write_character_sheet(
            data, description_mode=description_mode, output_folder=str(output_folder)
        )
        result[mode_key] = {
            page: hashlib.sha256(content).hexdigest()
            for page, content in sorted(writer.pages.items())
        }
        if dump and SNAPSHOT_DUMP_DIR:
            target_folder = Path(SNAPSHOT_DUMP_DIR) / name / mode_key
            shutil.rmtree(target_folder, ignore_errors=True)
            for page, content in writer.pages.items():
                target = target_folder / page
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
    return result


def sheet_differences(
    expected: dict[str, dict[str, str]], actual: dict[str, dict[str, str]]
) -> list[str]:
    """One line per mode whose pages differ (added, removed or changed)."""
    problems = []
    for mode_key, _description_mode in SHEET_MODES:
        expected_pages = expected.get(mode_key, {})
        actual_pages = actual.get(mode_key, {})
        added = sorted(set(actual_pages) - set(expected_pages))
        removed = sorted(set(expected_pages) - set(actual_pages))
        changed = sorted(
            page
            for page in set(actual_pages) & set(expected_pages)
            if actual_pages[page] != expected_pages[page]
        )
        if added or removed or changed:
            problems.append(
                f"{mode_key} mode: added pages {added}, removed pages {removed}, "
                f"changed pages {changed}"
            )
    return problems


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
