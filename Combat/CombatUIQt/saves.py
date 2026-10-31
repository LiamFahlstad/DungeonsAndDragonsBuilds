"""Saving throws the combat UI rolls for its targets, for the Custom dialog's
effects: what each target adds, what the rules change about the roll, and damage
typed as dice, which is rolled once for everyone it hits."""

import random
import re
from dataclasses import dataclass, field

from Core.Rules import ability_modifier

from .amounts import AmountError, parse_damage
from .monster_actions import ability_text, roll_dice

# The saving throws, as (the name, the short name a combatant's scores use).
ABILITIES = (
    ("Strength", "STR"),
    ("Dexterity", "DEX"),
    ("Constitution", "CON"),
    ("Intelligence", "INT"),
    ("Wisdom", "WIS"),
    ("Charisma", "CHA"),
)
ROLL_MODES = ("Neutral", "Advantage", "Disadvantage")
DEFAULT_SAVE_DC = 13

# "You automatically fail Strength and Dexterity saving throws."
_AUTO_FAIL_CONDITIONS = ("Paralyzed", "Petrified", "Stunned", "Unconscious")
_AUTO_FAIL_ABILITIES = ("STR", "DEX")

_DICE = re.compile(r"\d+d[1-9]\d*")
_SPELL_SAVE_DC = re.compile(r"spell save DC\s+(\d+)")


@dataclass
class SaveResult:
    success: bool
    total: int | None  # None for an automatic failure, which rolls nothing
    note: str = ""  # why the roll wasn't a plain one


@dataclass
class CustomEffect:
    """What the Custom dialog applies to every target."""

    name: str = ""  # what the log calls it ("Fireball")
    condition: str = ""
    duration: dict | None = None
    notes: str = ""
    # Rolled once, for everyone: (amount, damage type) for each type.
    damage: list[tuple[int, str]] = field(default_factory=list)
    count_resistances: bool = True
    # What it costs the source.
    slot_level: int | None = None
    action_cost: str | None = None
    concentration: bool = False
    # The saving throw, if there is one. Without one, everyone is affected.
    ability: str | None = None
    dc: int = 0
    mode: str = "Neutral"
    half_on_save: bool = True
    use_legendary_resistance: bool = False
    # The condition ends on a save at the end of each of the target's turns.
    repeat_save: bool = False
    # Totals rolled at the table, by the combatant's id(); the rest are rolled.
    typed_totals: dict[int, int] = field(default_factory=dict)


def save_modifier(char: dict, ability: str) -> int:
    """What char adds to a saving throw of `ability` ("STR", ...): its saving
    throw if the stat block lists one, otherwise its ability modifier."""
    saving_throws = char.get("Saving Throws") or {}
    if ability in saving_throws:
        return saving_throws[ability]
    scores = char.get("Ability Scores") or {}
    return ability_modifier(scores[ability]) if ability in scores else 0


def _has_condition(char: dict, condition: str) -> bool:
    """Whether char has `condition`, also under a longer custom name, like
    "Restrained by vines"."""
    return any(
        name == condition or name.startswith(f"{condition} ")
        for name in char.get("conditions", [])
    )


def _roll_d20(mode: str) -> int:
    first, second = random.randint(1, 20), random.randint(1, 20)
    if mode == "Advantage":
        return max(first, second)
    return min(first, second) if mode == "Disadvantage" else first


def _with_conditions(char: dict, ability: str, mode: str) -> tuple[str, str]:
    """The roll mode once char's conditions count, and a note if they changed
    it. Restrained gives Disadvantage on Dexterity saves, and Advantage and
    Disadvantage cancel out however many of each there are."""
    if ability != "DEX" or not _has_condition(char, "Restrained"):
        return mode, ""
    if mode == "Advantage":
        return "Neutral", "Restrained cancels Advantage"
    return "Disadvantage", "Restrained: Disadvantage"


def roll_save(
    char: dict, ability: str, dc: int, mode: str, typed: int | None = None
) -> SaveResult:
    """Char's save against `dc`: `typed` is a total rolled at the table. A
    natural 1 or 20 is nothing special on a saving throw."""
    if ability in _AUTO_FAIL_ABILITIES:
        for condition in _AUTO_FAIL_CONDITIONS:
            if _has_condition(char, condition):
                return SaveResult(False, None, f"{condition}: automatic failure")
    if typed is not None:
        return SaveResult(typed >= dc, typed)
    mode, note = _with_conditions(char, ability, mode)
    if _has_condition(char, "Exhaustion"):
        # Its levels aren't tracked, so the GM has to take these off.
        note = ", ".join(filter(None, [note, "Exhaustion not counted: -2 a level"]))
    total = _roll_d20(mode) + save_modifier(char, ability)
    return SaveResult(total >= dc, total, note)


def is_immune_to(char: dict, condition: str) -> bool:
    """A monster's stat block lists its immunities, and a player's character
    knows theirs. Petrified also gives Immunity to the Poisoned condition."""
    if condition == "Poisoned" and _has_condition(char, "Petrified"):
        return True
    immunities = list(char.get("condition_immunities") or [])
    sheet = char.get("_stat_block")
    if sheet is not None:
        immunities += sheet.condition_immunities()
    return any(getattr(i, "value", i) == condition for i in immunities)


def known_save_dc(char: dict | None) -> int | None:
    """The save DC char's own spells use, if that's known: a player's from
    their character, a monster's from its Spellcasting text."""
    if char is None:
        return None
    sheet = char.get("_stat_block")
    if sheet is not None:
        if sheet.spell_casting_ability is None:
            return None
        return sheet.calculate_difficulty_class()
    for key in ("actions", "traits"):
        for ability in char.get(key) or []:
            match = _SPELL_SAVE_DC.search(ability_text(ability)[1])
            if match:
                return int(match.group(1))
    return None


def rolled_damage(text: str) -> list[tuple[int, str | None]]:
    """The damage typed, with any dice rolled ("8d6 fire", "28 fi", "2d6 + 3 fi
    + 1d4 co"). An effect's damage is rolled once, for everyone it hits. Raises
    AmountError if it can't be read."""
    rolled = _DICE.sub(lambda m: str(roll_dice(m.group(0))), text)
    return parse_damage(rolled, floor_at_zero=True)


def read_damage(
    text: str, chosen_type: str | None = None
) -> tuple[list[tuple[int, str]], str]:
    """Damage from the Custom dialog as (parts, what's wrong with it, if
    anything). With no type typed, it takes `chosen_type`, the dropdown's.
    Typing a type sets the dropdown, so a difference means it was changed after,
    and which is meant can't be known."""
    if not text.strip():
        return [], ""
    try:
        parts = rolled_damage(text)
    except AmountError as error:
        return [], f"Damage: {error}."
    named = next((damage_type for _, damage_type in parts if damage_type), None)
    if named and chosen_type and named != chosen_type:
        return [], f"The damage says {named}, the dropdown {chosen_type}."
    typed = [(amount, damage_type or chosen_type) for amount, damage_type in parts]
    complete = [(amount, damage_type) for amount, damage_type in typed if damage_type]
    if len(complete) != len(typed):
        return [], "Damage needs a type: pick one, or type 8d6 fire."
    return complete, ""
