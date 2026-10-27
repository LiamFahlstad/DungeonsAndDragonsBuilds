"""What a multiclass build actually came out as, to check against the 2024 rules.

Usage (from the repo root):
    python .claude/skills/multiclass-builds/multiclass_report.py Builds/Characters/<File>.py

Builds the file's CharacterBuilder, runs Character.validate() (which enforces the
13+ multiclass prerequisites) and prints:
  levels       which class each character level went to, in order, and the subclass shown
  per class    each class's level and the class features it granted, by class level
  proficiency  saving throws (starting class only), armor training, weapon proficiencies,
               and whether each carried weapon is proficient
  combat       HP, AC, weapon masteries, fighting styles
  spells       spellcasting ability, shared slots and Pact Magic slots
  notes        multiclass grants the engine doesn't model (the skill choices)
Exit code 1 when validate() fails.
"""

import argparse
import importlib
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from Builds.CharacterBuilder import is_build_class  # noqa: E402
from Core.Definitions import Ability, CharacterClass  # noqa: E402
from Model.Records.GrantStamp import GrantKind  # noqa: E402

# 2024 PHB: multiclassing into these grants one skill (Bard: also an instrument),
# which ClassProficiencies.MulticlassProficiencies doesn't model.
UNMODELLED_SKILL_CHOICE = {
    CharacterClass.ARTIFICER,
    CharacterClass.BARD,
    CharacterClass.RANGER,
    CharacterClass.ROGUE,
}


def load_builder(build_file: str):
    path = Path(build_file).resolve().relative_to(ROOT)
    module_name = ".".join(path.with_suffix("").parts)
    module = importlib.import_module(module_name)
    builders = [v for v in vars(module).values() if is_build_class(v, module_name)]
    if len(builders) != 1:
        sys.exit(f"Expected one CharacterBuilder in {build_file}, found {builders}")
    return builders[0]


def class_segments(character) -> str:
    return ", ".join(
        f"{cls.value} {start}" if start == end else f"{cls.value} {start}-{end}"
        for start, end, cls in character.get_class_level_segments()
    )


def report(build_file: str) -> int:
    character = load_builder(build_file)().build()
    failed = False
    try:
        character.validate()
        validation = "ok"
    except ValueError as error:
        validation = f"FAIL {error}"
        failed = True

    print(f"== {character.character_name} ({build_file})")
    print(f"validate     {validation}")
    print(
        f"levels       character level {character.character_level}: {class_segments(character)}"
    )
    print(f"subclass     {character.character_subclass}")

    by_class: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    for grant in character.feature_grants:
        stamp = grant.stamp
        if stamp.kind in (GrantKind.CLASS, GrantKind.SUBCLASS):
            by_class[stamp.granted_by][stamp.level].append(grant.feature.name)
    for cls, level in character.level_per_class.items():
        print(f"{cls.value} {level}")
        for granted_by, levels in by_class.items():
            if granted_by != cls.value and not granted_by.startswith(cls.value):
                continue
            for class_level in sorted(levels):
                print(f"  L{class_level:<2} {', '.join(levels[class_level])}")

    saves = [a.value for a in Ability if character.is_proficient_in_saving_throw(a)]
    print(
        f"saves        {', '.join(saves)} (starting class {character.base_class.value})"
    )
    print(
        f"armor        {', '.join(sorted(a.value for a in character.armor_training()))}"
    )
    print(
        f"weapons      {', '.join(sorted(p.value for p in character.weapon_proficiencies()))}"
    )
    for weapon in character.weapons:
        if weapon.is_unarmed_strike:
            continue
        proficient = (
            "proficient" if weapon.is_proficient(character) else "NOT proficient"
        )
        print(f"  {weapon.name}: {proficient}")

    ac = character.calculate_armor_class()
    print(f"hp / ac      {character.calculate_hit_points()} / {ac}")
    print(
        f"masteries    {', '.join(w.name for w in character.weapon_masteries) or '-'}"
    )
    print(
        f"styles       {', '.join(type(s).__name__ for s in character.fighting_styles) or '-'}"
    )
    ability = character.spell_casting_ability
    print(f"casting      {ability.value if ability else '-'}")
    print(
        f"slots        {character.spell_slots or '-'}  pact {character.pact_magic_slots or '-'}"
    )

    for cls in character.level_per_class:
        if cls != character.base_class and cls in UNMODELLED_SKILL_CHOICE:
            print(
                f"note         multiclassing into {cls.value} grants a skill "
                "proficiency the engine doesn't model - add it by hand if the player took it"
            )
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("build_files", nargs="+")
    args = parser.parse_args()
    return max(report(f) for f in args.build_files)


if __name__ == "__main__":
    sys.exit(main())
