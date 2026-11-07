"""Saving throws and attack rolls the combat UI rolls for its targets, for the
Custom dialog's effects: what each target adds, what the rules change about the
roll, and damage typed as dice, which is rolled once for everyone it hits."""

import random
import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from Core.Rules import SPELL_SAVE_DC_BASE, ability_modifier

from .amounts import AmountError, parse_damage
from .attack_rolls import AttackRoll, rolled_attack
from .monster_actions import (
    DIE,
    DamageRoll,
    MonsterAction,
    ability_text,
    parse_action,
    roll_dice,
)

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
DEFAULT_ATTACK_BONUS = 0
# How the Custom dialog decides who an effect lands on.
SAVING_THROW = "Saving throw"
ATTACK_ROLL = "Attack roll"

# "You automatically fail Strength and Dexterity saving throws."
_AUTO_FAIL_CONDITIONS = ("Paralyzed", "Petrified", "Stunned", "Unconscious")
_AUTO_FAIL_ABILITIES = ("STR", "DEX")

_DICE = re.compile(r"\d+d[1-9]\d*")
_SPELL_SAVE_DC = re.compile(r"spell save DC\s+(\d+)")
_SPELL_ATTACK = re.compile(r"([+-]\d+) to hit with spell attacks")


# What the Custom dialog's amount box is: damage, Hit Points regained, or
# Temporary Hit Points.
DAMAGE_AMOUNT = "Damage"
HEALING = "Healing"
TEMP_HP = "Temp HP"
AMOUNT_KINDS = (DAMAGE_AMOUNT, HEALING, TEMP_HP)

# What an EffectOption is, which decides what using it counts as.
MONSTER_ACTION = "monster action"
WEAPON = "weapon"
SPELL = "spell"
FEATURE = "feature"


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
    # The same with its dice rolled twice over, for a critical hit.
    critical_damage: list[tuple[int, str]] = field(default_factory=list)
    count_resistances: bool = True
    # Hit Points regained, and Temporary Hit Points given, rolled once for
    # everyone. Every target gets them, whatever the roll.
    healing: int = 0
    temp_hp: int = 0
    # What it costs the source.
    slot_level: int | None = None
    action_cost: str | None = None
    concentration: bool = False
    # The attack roll, if it's one instead of a saving throw: what the source
    # adds, and the rolls made at the table, by the combatant's id().
    attack_bonus: int | None = None
    typed_attacks: dict[int, AttackRoll] = field(default_factory=dict)
    # The saving throw, if there is one. Without one or an attack roll, everyone
    # is affected.
    ability: str | None = None
    dc: int = 0
    mode: str = "Neutral"  # for the attack roll too
    half_on_save: bool = True
    use_legendary_resistance: bool = False
    # The condition ends on a save at the end of each of the target's turns.
    repeat_save: bool = False
    # Totals rolled at the table, by the combatant's id(); the rest are rolled.
    typed_totals: dict[int, int] = field(default_factory=dict)
    # What it was picked as in the dialog (effect_options.py), if it was: the
    # source uses it up (a spell cast, a feature's use, a monster's recharge)
    # along with the rest. Defined below, as effect_options needs this module.
    pick: "EffectOption | None" = None


@dataclass(frozen=True)
class EffectOption:
    """One thing the picker lists, and what picking it fills in. A None dc or
    bonus keeps the dialog's value; anything else empty clears that field."""

    name: str
    kind: str
    row_name: str = ""  # its name in its row, if that says more
    summary: str = ""  # its numbers, for its row
    tooltip: str = ""  # its rules text
    note: str = ""  # what the GM should check
    roll: str = SAVING_THROW
    ability: str | None = None
    dc: int | None = None
    bonus: int | None = None
    half_on_save: bool = False
    repeat_save: bool = False
    rolls: tuple[DamageRoll, ...] = ()
    condition: str = ""
    duration_seconds: int | None = None
    # A duration that's a turn instead: ("start" or "end", "source" or
    # "target"), as CUSTOM_CONDITION_DURATIONS has it. It comes first.
    until: tuple[str, str] | None = None
    slot_level: int | None = None
    action_cost: str | None = None
    concentration: bool = False
    # A monster's action, which TurnPanelMixin spends, and whether it can't be
    # used now (spent, or more legendary actions than are left).
    monster_action: MonsterAction | None = None
    is_unavailable: bool = False
    # Whether using it counts against the feature's uses.
    counts_uses: bool = False
    # The feature whose uses and stats it counts against, when one of its
    # uses has a name of its own (Jolt to Life, of Reanimator's Skill Set).
    feature_name: str = ""
    # The spell a feature's use casts (Favored Enemy's Hunter's Mark): its
    # condition is that spell's badge.
    spell_name: str = ""
    # What each of `rolls` gains per slot level above spell_level, "" for none:
    # dice, or a flat number (False Life's 5 Temporary Hit Points).
    upcast: tuple[str, ...] = ()
    # What `rolls` are: damage (with types), or Hit Points regained or
    # Temporary Hit Points given (without).
    amount_kind: str = DAMAGE_AMOUNT
    spell_level: int = 0
    # A spell filled in from its checked mechanics file, or a feature from its
    # own combat_effects(), not read from its text.
    is_curated: bool = False

    @property
    def row_text(self) -> str:
        name = self.row_name or self.name
        return f"{name}  {self.summary}" if self.summary else name

    @property
    def damage(self) -> str:
        return self.damage_at(self.slot_level)

    def damage_at(self, slot_level: int | None) -> str:
        """The Damage box's text, with a spell cast using a slot of slot_level
        (None: at its own level)."""
        levels_up = max((slot_level or self.spell_level) - self.spell_level, 0)
        if not levels_up or not self.upcast:
            return damage_text(self.rolls)
        return damage_text(
            with_dice(roll, dice, levels_up) if dice else roll
            for roll, dice in zip(self.rolls, self.upcast)
        )

    @property
    def is_tracked(self) -> bool:
        """Whether using it counts for something, with nothing else to apply."""
        action = self.monster_action
        if action is not None:
            return action.is_limited or bool(action.legendary_cost)
        if self.kind == FEATURE:
            # One used, not one that's always on, like Tough or Darkvision.
            return self.counts_uses or self.action_cost is not None
        return self.kind == SPELL


def damage_text(rolls: Iterable[DamageRoll]) -> str:
    """Rolls as the Damage box reads them: "2d6 + 3 Slashing + 1d4 Fire". A
    type to choose is left off, for the GM to give."""
    return " + ".join(
        f"{roll.dice} {roll.damage_type}" if roll.damage_type else roll.dice
        for roll in rolls
    )


def with_dice(roll: DamageRoll, dice: str, times: int) -> DamageRoll:
    """Roll with `times` more of dice: more of the same die, or added on. A
    flat number is added on ("2d4 + 4" with 5 twice is "2d4 + 4 + 10")."""
    if "d" not in dice:
        return DamageRoll(f"{roll.dice} + {int(dice) * times}", roll.damage_type)
    count, sides = map(int, dice.split("d"))
    first = DIE.search(roll.dice)
    if first is not None and int(first[2]) == sides:
        more = int(first[1]) + count * times
        text = f"{roll.dice[:first.start()]}{more}d{sides}{roll.dice[first.end():]}"
    else:
        text = f"{roll.dice} + {count * times}d{sides}"
    return DamageRoll(text, roll.damage_type)


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


def roll_attack(bonus: int, mode: str) -> AttackRoll:
    """An attack roll for a source that adds `bonus`."""
    return rolled_attack(_roll_d20(mode), bonus)


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
    return _number_in_stat_block(char, _SPELL_SAVE_DC)


def known_spell_attack_bonus(char: dict | None) -> int | None:
    """What char adds to its spell attacks, if that's known: a player's from
    their character, a monster's from its Spellcasting text."""
    if char is None:
        return None
    sheet = char.get("_stat_block")
    if sheet is not None:
        if sheet.spell_casting_ability is None:
            return None
        return sheet.calculate_attack_bonus()
    bonus = _number_in_stat_block(char, _SPELL_ATTACK)
    if bonus is None:
        # Many stat blocks give only the DC. It's 8 + the same modifier and
        # Proficiency Bonus the attack adds, so the attack is the DC - 8.
        dc = _number_in_stat_block(char, _SPELL_SAVE_DC)
        bonus = None if dc is None else dc - SPELL_SAVE_DC_BASE
    return bonus


def known_attack_bonus(char: dict | None) -> int | None:
    """known_spell_attack_bonus, or else a monster's first attack: it has no
    other to go on."""
    bonus = known_spell_attack_bonus(char)
    if bonus is not None or char is None or char.get("_stat_block") is not None:
        return bonus
    attacks = map(parse_action, char.get("actions") or [])
    return next((a.to_hit for a in attacks if a.to_hit is not None), None)


def _number_in_stat_block(char: dict, pattern: re.Pattern[str]) -> int | None:
    """The first match of `pattern` in char's actions and traits."""
    for key in ("actions", "traits"):
        for ability in char.get(key) or []:
            match = pattern.search(ability_text(ability)[1])
            if match:
                return int(match.group(1))
    return None


def rolled_damage(text: str, critical: bool = False) -> list[tuple[int, str | None]]:
    """The damage typed, with any dice rolled ("8d6 fire", "28 fi", "2d6 + 3 fi
    + 1d4 co"), twice over for a critical hit. An effect's damage is rolled
    once, for everyone it hits. Raises AmountError if it can't be read."""
    rolled = _DICE.sub(lambda m: str(roll_dice(m.group(0), critical)), text)
    return parse_damage(rolled, floor_at_zero=True)


def read_damage(
    text: str, chosen_type: str | None = None, critical: bool = False
) -> tuple[list[tuple[int, str]], str]:
    """Damage from the Custom dialog as (parts, what's wrong with it, if
    anything). With no type typed, it takes `chosen_type`, the dropdown's.
    Typing a type sets the dropdown, so a difference means it was changed after,
    and which is meant can't be known."""
    if not text.strip():
        return [], ""
    try:
        parts = rolled_damage(text, critical)
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


def read_hit_points(text: str, kind: str) -> tuple[int, str]:
    """Hit Points regained or Temporary Hit Points (`kind`, HEALING or
    TEMP_HP) from the Custom dialog, with any dice rolled once, as (amount,
    what's wrong with it, if anything). 0 for nothing typed."""
    if not text.strip():
        return 0, ""
    try:
        parts = rolled_damage(text)
    except AmountError as error:
        return 0, f"{kind}: {error}."
    if any(damage_type for _, damage_type in parts):
        return 0, f"{kind} has no damage type: type 2d8 + 3, or a total."
    return sum(amount for amount, _ in parts), ""
