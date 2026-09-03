"""Regenerate Combat/Tools/monster_cr_distributions.html.

Imports every CR_*/monsters.py (official) and CR_*/monsters_homebrew.py
(homebrew) stat block, computes per-CR-tier means and standard deviations
(HP, AC, the six ability scores, attack roll bonus, damage per hit,
multiattack-aware damage per round, per-ability saving throw modifiers,
save DC, action economy, and defensive tags) from the *official* monsters
only, and writes a self-contained interactive HTML report:

  - a ridgeline (joyplot) chart per attribute showing the fitted normal
    distribution for each CR tier, with real stat blocks plotted as dots
  - a "power score" leaderboard: every monster (official AND homebrew) gets
    a 0-1 percentile score from how far its stats sit from its CR tier's
    fitted mean, in standard deviations

Homebrew monsters are scored against the official distributions but never
used to fit them -- so this is exactly the tool to check a new homebrew
monster against: does it look like it belongs at the CR you gave it?

Run from the repo root:
    python -m Combat.Tools.generate_monster_cr_distributions
Writes Combat/Tools/monster_cr_distributions.html
"""

import importlib
import inspect
import json
import re
import sys
from pathlib import Path

from Combat.Definitions import (
    ExtendedCombatantData,
    MeleeAttack,
    Multiattack,
    SavingThrowEffect,
)

MONSTERS_DIR = Path(__file__).resolve().parent.parent / "Monsters"
TEMPLATE_HTML = (
    Path(__file__).resolve().parent / "monster_cr_distributions_template.html"
)
OUTPUT_HTML = Path(__file__).resolve().parent / "monster_cr_distributions.html"

PLACEHOLDER = "__MONSTER_DATA_JSON__"

# `MeleeAttack` abilities carry structured attack_bonus/dice_type/dice_count/
# damage_bonus fields, so their to-hit and damage-per-hit are read straight
# off those (precise, possibly fractional, e.g. a D6.average() of 3.5) --
# see _ability_attack_value/_ability_damage_value below. Plain `MonsterAbility`
# entries (hand-written text, no structured fields) still fall back to
# regexing "Attack Roll: +N" / "Hit: N (...)" out of the free-text description.
_ATTACK_ROLL_RE = re.compile(r"Attack Roll:\s*([+-]\d+)")
_DAMAGE_HIT_RE = re.compile(r"Hit:\s*(\d+)")
_SAVE_DC_RE = re.compile(r"DC\s*(\d+)")
_ACTION_LIKE_FIELDS = (
    "actions",
    "bonus_actions",
    "reactions",
    "legendary_actions",
    "mythic_actions",
    "lair_actions",
)

# Leading count word/digit in a Multiattack's `attacks_text` (e.g. "two Rend
# attacks" -> 2, "three attacks, using ..." -> 3) -- see _multiattack_count.
# This is a heuristic over free text and only reads the first count it finds,
# so mixed phrasing like "one Bite attack and uses Antennae twice" under-counts
# (reads 1, not "however many attacks that implies"); good enough for a rough
# damage-per-round estimate, not exact.
_MULTIATTACK_COUNT_WORDS = {
    "once": 1,
    "one": 1,
    "twice": 2,
    "two": 2,
    "thrice": 3,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
}
_MULTIATTACK_COUNT_RE = re.compile(
    r"\b(" + "|".join(_MULTIATTACK_COUNT_WORDS) + r"|\d+)\b", re.IGNORECASE
)


def cr_key(cr: str) -> float:
    if "/" in cr:
        n, d = cr.split("/")
        return float(n) / float(d)
    return float(cr)


def _ability_attack_value(ability):
    if isinstance(ability, MeleeAttack):
        return float(ability.attack_bonus)
    m = _ATTACK_ROLL_RE.search(ability.description)
    return float(m.group(1)) if m else None


def _ability_damage_value(ability):
    if isinstance(ability, MeleeAttack):
        return ability.dice_type.average(ability.dice_count) + ability.damage_bonus
    m = _DAMAGE_HIT_RE.search(ability.description)
    return float(m.group(1)) if m else None


def _ability_save_dc(ability):
    # A handful of summon stat blocks give a non-numeric dc like "equals
    # your spell save DC" (derived from the summoner, not a fixed stat) --
    # fall through to the regex path, which correctly finds nothing there.
    if isinstance(ability, SavingThrowEffect) and isinstance(ability.dc, (int, float)):
        return float(ability.dc)
    m = _SAVE_DC_RE.search(ability.description)
    return float(m.group(1)) if m else None


def _avg_ability_value(instance, value_fn):
    values = []
    for field in _ACTION_LIKE_FIELDS:
        for ability in getattr(instance, field, None) or []:
            v = value_fn(ability)
            if v is not None:
                values.append(v)
    return sum(values) / len(values) if values else None


def _multiattack_count(instance):
    """Total attacks-per-round implied by a Multiattack action's
    attacks_text (e.g. "two Rend attacks" -> 2), or None when there's no
    Multiattack action or its phrasing doesn't parse -- see the heuristic
    note by _MULTIATTACK_COUNT_WORDS above."""
    for ability in instance.actions or []:
        if isinstance(ability, Multiattack):
            m = _MULTIATTACK_COUNT_RE.search(ability.attacks_text)
            if not m:
                return None
            token = m.group(1).lower()
            return _MULTIATTACK_COUNT_WORDS.get(token) or (
                int(token) if token.isdigit() else None
            )
    return None


def _damage_per_round(instance):
    """Multiattack-aware damage estimate: average per-hit damage across the
    monster's attack actions, scaled by its Multiattack count when present
    (e.g. two Rend attacks averaging 9 damage each -> ~18/round). Falls back
    to the plain per-hit average (same as "dmg") when there's no parseable
    Multiattack action, so a single-attack monster's dpr equals its dmg."""
    avg_hit = _avg_ability_value(instance, _ability_damage_value)
    if avg_hit is None:
        return None
    count = _multiattack_count(instance)
    return avg_hit * count if count else avg_hit


_SAVE_ABILITIES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")


def _save_mods(instance):
    """Per-ability saving throw modifier for all six abilities: the listed
    stat-block value from `saving_throws` where the monster is proficient
    (e.g. {WIS: 0} for a Zombie's mediocre Wisdom save), otherwise the
    plain ability modifier floor((score - 10) / 2) -- so every monster gets
    a save mod for every ability, proficient or not. Returns a dict keyed
    by short ability name ("STR".."CHA"), values None only when the
    ability score itself is missing."""
    throws = instance.saving_throws or {}
    scores = instance.ability_scores or {}
    mods = {}
    for short in _SAVE_ABILITIES:
        if throws.get(short) is not None:
            mods[short] = throws[short]
        else:
            score = scores.get(short)
            mods[short] = (score - 10) // 2 if score is not None else None
    return mods


def _damage_type_count(entries) -> int:
    """Counts individual damage types across all entries, e.g. one entry
    covering [BLUDGEONING, PIERCING, SLASHING] counts as 3, not 1."""
    return sum(len(e.damage_types) for e in (entries or []))


def extract_module(cr_folder: Path, filename: str, errors: list[str]) -> list[dict]:
    module_stem = filename[:-3]  # strip ".py"
    module_file = cr_folder / filename
    if not module_file.exists():
        return []
    module_name = f"Combat.Monsters.{cr_folder.name}.{module_stem}"
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        errors.append(f"{module_name}: import failed: {e}")
        return []

    out = []
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ != module_name:
            continue
        if not issubclass(obj, ExtendedCombatantData):
            continue
        try:
            instance = obj()
        except Exception as e:
            errors.append(f"{module_name}.{name}: instantiation failed: {e}")
            continue

        abilities = instance.ability_scores or {}
        hp_formula = getattr(instance, "hp_formula", "") or ""
        # A handful of "scaling summon" stat blocks (Ranger Beast Master
        # companions, Find Familiar spirits, etc.) use hp=0 with an empty
        # hp_formula as a placeholder because their real HP is derived from
        # the summoner's level elsewhere. That's not a real fixed stat, so
        # exclude it from HP specifically (AC/ability scores are still
        # fixed and valid).
        hp_value = instance.hp if hp_formula.strip() else None
        save_mods = _save_mods(instance)
        out.append(
            {
                "name": instance.combatant_type,
                "cr": instance.cr,
                "hp": hp_value,
                "ac": instance.ac,
                "str": abilities.get("STR"),
                "dex": abilities.get("DEX"),
                "con": abilities.get("CON"),
                "int": abilities.get("INT"),
                "wis": abilities.get("WIS"),
                "cha": abilities.get("CHA"),
                "atk": _avg_ability_value(instance, _ability_attack_value),
                "dmg": _avg_ability_value(instance, _ability_damage_value),
                "dpr": _damage_per_round(instance),
                "strsave": save_mods["STR"],
                "dexsave": save_mods["DEX"],
                "consave": save_mods["CON"],
                "intsave": save_mods["INT"],
                "wissave": save_mods["WIS"],
                "chasave": save_mods["CHA"],
                "dc": _avg_ability_value(instance, _ability_save_dc),
                "condimm": len(instance.condition_immunities or []),
                "dmgimm": _damage_type_count(instance.damage_immunities),
                "dmgres": _damage_type_count(instance.damage_resistances),
                "dmgvuln": _damage_type_count(instance.damage_vulnerabilities),
                "actions": len(instance.actions or []),
                "bonusact": len(instance.bonus_actions or []),
                "speed": instance.speed_ground_ft,
            }
        )
    return out


def extract_all() -> tuple[dict, list[str]]:
    cr_folders = sorted(
        (p for p in MONSTERS_DIR.iterdir() if p.is_dir() and p.name.startswith("CR_")),
        key=lambda p: int(p.name.split("_")[1]),
    )

    errors: list[str] = []
    monsters: list[dict] = []
    homebrew: list[dict] = []
    for cr_folder in cr_folders:
        monsters.extend(extract_module(cr_folder, "monsters.py", errors))
        homebrew.extend(extract_module(cr_folder, "monsters_homebrew.py", errors))

    # cr_order drives the distribution rows, so it's derived from official
    # monsters only -- a homebrew-only CR tier doesn't get a fitted curve,
    # it just falls back to "insufficient data" for that tier.
    cr_order = sorted({m["cr"] for m in monsters}, key=cr_key)

    return {"monsters": monsters, "homebrew": homebrew, "cr_order": cr_order}, errors


def main() -> None:
    data, errors = extract_all()

    print(
        f"Extracted {len(data['monsters'])} official monsters, "
        f"{len(data['homebrew'])} homebrew monsters, "
        f"{len(data['cr_order'])} CR tiers",
        file=sys.stderr,
    )
    if errors:
        print(f"{len(errors)} errors:", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)

    if not TEMPLATE_HTML.exists():
        raise SystemExit(
            f"Template not found: {TEMPLATE_HTML}\n"
            "This holds the report's HTML/CSS/JS shell with a "
            f"{PLACEHOLDER} marker where the monster data gets spliced in. "
            "It should be checked in alongside this script."
        )

    template = TEMPLATE_HTML.read_text(encoding="utf-8")
    payload = json.dumps(data, separators=(",", ":"))

    pattern = re.compile(re.escape(PLACEHOLDER))
    output, n = pattern.subn(lambda _m: payload, template)
    if n != 1:
        raise SystemExit(
            f"Expected exactly one {PLACEHOLDER} marker in the template, found {n}."
        )

    OUTPUT_HTML.write_text(output, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML} ({len(output):,} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
