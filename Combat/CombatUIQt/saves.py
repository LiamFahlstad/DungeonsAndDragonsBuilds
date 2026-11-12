"""Saving throws and attack rolls the combat UI rolls for its targets, for the
Custom dialog's effects: what each target adds, what the rules change about the
roll, and damage typed as dice, which is rolled once for everyone it hits."""

import random
import re
from collections.abc import Iterable
from dataclasses import dataclass, field

from Combat.Effects.modifiers import (
    HitPlan,
    RollPlan,
    immune_to_condition,
    save_plan,
)
from Core.Rules import SPELL_SAVE_DC_BASE, ability_modifier
from Model.Content.CombatEffect import CombatRegain
from Model.Content.CombatModifiers import Modifier
from Model.Content.CombatTriggers import CombatTrigger

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

# Between the conditions one effect gives, in the Condition box: "Frightened
# + Incapacitated". Each lands on every target, and they end together.
CONDITION_JOINER = " + "


def condition_names(text: str) -> list[str]:
    """The conditions a Condition box's text names, in order."""
    return [name.strip() for name in text.split(CONDITION_JOINER) if name.strip()]


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
    # The picker row it was made with, kept on a Times copy, which drops the
    # pick: what a hit triggers comes `after` a row by name (Tree Club).
    row: str = ""
    # Whether the attack is made with a weapon (EffectOption.weapon_attack),
    # None when that isn't known; and whether its damage is a total rolled at
    # the table, to which a hit's extra damage isn't added (Decision 4).
    weapon_attack: bool | None = None
    typed_damage: bool = False
    # A hit's extra damage rolled at the table (plan principle 13), by the
    # target's id() and then by what gives it ("Gabriel's Hunter's Mark"):
    # added as it is, even to a typed damage total; the rest are rolled.
    typed_extras: dict[int, dict[str, int]] = field(default_factory=dict)
    # A badge's Hit Point maximum rolled at the table (Heroes' Feast's 2d10,
    # its upcast in it), by the target's id(); the rest are rolled (8.6).
    typed_hit_point_maximum: dict[int, int] = field(default_factory=dict)
    # Whether each target with a Shield wields it (the attack rows' Shield
    # box), by its id(): it's set so before the attack, and stays so.
    shields: dict[int, bool] = field(default_factory=dict)

    @property
    def conditions(self) -> list[str]:
        """Each condition it gives: `condition` can name several, joined by
        CONDITION_JOINER ("Frightened + Incapacitated")."""
        return condition_names(self.condition)


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
    # A spell, feature or monster ability filled in from its combat effects,
    # not read from its text.
    is_described: bool = False
    # How many times one use rolls and deals its damage (Scorching Ray's
    # rays), and how many more per slot level above spell_level.
    instances: int = 1
    instances_upcast: int = 0
    # What the badges it gives do while they're on, by badge: (("Bless",
    # (D20Bonus(...),)),), as its CombatCondition says.
    badge_modifiers: tuple[tuple[str, tuple[Modifier, ...]], ...] = ()
    # The conditions it ends on each target its conditions would land on
    # (CombatEffect.ends_conditions: Lay on Hands' Poisoned).
    ends_conditions: tuple[str, ...] = ()
    # It goes on its user alone, whoever is targeted (CombatEffect.targets_self).
    targets_self: bool = False
    # How many creatures it may target, and how many more per slot level
    # above the spell's (CombatEffect.targets); None: not said.
    target_count: int | None = None
    target_upcast: int = 0
    # Whether its attack roll is made with a weapon, for extra damage that
    # only a weapon attack deals (Divine Favor): a weapon's is, an Unarmed
    # Strike's isn't, and None when it can't be told (a spell can grant a
    # weapon attack, a monster's attack doesn't say).
    weapon_attack: bool | None = None
    # When it's used, as its CombatEffect says (Hill's Tumble: as its owner
    # hits): Combat/Effects/triggers.py offers it then.
    trigger: CombatTrigger | None = None
    # Dice it takes off the damage of the hit it answers (Deflect Attacks),
    # rolled by the window as that hit lands (CombatEffect.damage_reduction).
    damage_reduction: str = ""
    # The Hit Points its user drops to instead of 0, asked as damage would
    # drop them to 0 (CombatEffect.drops_to: Relentless Endurance's 1).
    drops_to: int = 0
    # Expended uses of its user's features it gives back (CombatEffect.regains:
    # Uncanny Metabolism's Focus Points).
    regains: tuple[CombatRegain, ...] = ()
    # Rerolls the failed save it answers with this bonus (Indomitable's
    # Fighter level); None: it doesn't (CombatEffect.reroll_save).
    reroll_save: int | None = None

    def modifiers_for(self, badge: str) -> tuple[Modifier, ...]:
        """What the badge `badge` it gives does while it's on: none for a
        badge named otherwise (one typed over in the dialog)."""
        return next((m for name, m in self.badge_modifiers if name == badge), ())

    def instances_at(self, slot_level: int | None) -> int:
        """The count with a spell cast using a slot of slot_level (None: at its
        own level)."""
        levels_up = max((slot_level or self.spell_level) - self.spell_level, 0)
        return self.instances + self.instances_upcast * levels_up

    def targets_at(self, slot_level: int | None) -> int | None:
        """How many creatures it may target with a spell cast using a slot of
        slot_level (None: at its own level); None when it doesn't say."""
        if self.target_count is None:
            return None
        levels_up = max((slot_level or self.spell_level) - self.spell_level, 0)
        return self.target_count + self.target_upcast * levels_up

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


def _roll_d20(mode: str) -> int:
    first, second = random.randint(1, 20), random.randint(1, 20)
    if mode == "Advantage":
        return max(first, second)
    return min(first, second) if mode == "Disadvantage" else first


def roll_bonuses(plan: RollPlan) -> tuple[int, tuple[str, ...]]:
    """What `plan`'s bonuses add to a roll made here, their dice rolled, and
    the notes saying so: "Bless: +3 (1d4)", "Half Cover: +2"."""
    total = 0
    notes = []
    for label, amount in plan.bonuses:
        sign = -1 if amount.startswith("-") else 1
        dice = amount.lstrip("+-")
        rolled = sign * roll_dice(dice)
        total += rolled
        shown = f"{rolled:+d} ({amount})" if "d" in dice else f"{rolled:+d}"
        notes.append(f"{label}: {shown}")
    return total, tuple(notes)


def roll_save(
    char: dict,
    ability: str,
    dc: int,
    mode: str,
    typed: int | None = None,
    *,
    one_die_if_straight: bool = False,
) -> SaveResult:
    """Char's save against `dc`: `typed` is a total rolled at the table. A
    natural 1 or 20 is nothing special on a saving throw. Its modifiers
    count (Combat/Effects): an automatic failure beats any total, and a
    rolled one takes the mode they give and adds their bonuses (Bless's
    1d4, rolled after the d20; cover's +2 to a Dexterity save).
    `one_die_if_straight`: a straight roll throws one d20, not two, as a
    monster's Concentration save always has, so its dice stay as they were."""
    plan = save_plan(char, ability, mode, typed=typed is not None)
    if plan.auto_fail:
        return SaveResult(False, None, plan.auto_fail)
    if typed is not None:
        return SaveResult(typed >= dc, typed, ", ".join(plan.notes))
    if one_die_if_straight and plan.mode == "Neutral":
        d20 = random.randint(1, 20)
    else:
        d20 = _roll_d20(plan.mode)
    total = d20 + save_modifier(char, ability)
    added, bonus_notes = roll_bonuses(plan)
    total += added
    return SaveResult(total >= dc, total, ", ".join((*plan.notes, *bonus_notes)))


def save_reminder(char: dict, ability: str) -> RollPlan:
    """What char's modifiers do to its save of `ability`, for the GM to roll
    it that way at the table."""
    return save_plan(char, ability, "Neutral")


def roll_attack(bonus: int, mode: str) -> AttackRoll:
    """An attack roll for a source that adds `bonus`."""
    return rolled_attack(_roll_d20(mode), bonus)


def roll_planned_attack(
    bonus: int, plan: RollPlan
) -> tuple[AttackRoll, tuple[str, ...]]:
    """An attack roll for a source that adds `bonus`, made as `plan` says:
    its mode, and its bonuses rolled and added (Bless's 1d4). Also the
    notes on how it was rolled."""
    d20 = _roll_d20(plan.mode)
    added, bonus_notes = roll_bonuses(plan)
    return rolled_attack(d20, bonus + added), (*plan.notes, *bonus_notes)


def roll_extra_damage(
    plan: HitPlan, critical: bool = False
) -> tuple[list[tuple[int, str]], tuple[str, ...]]:
    """What `plan`'s extra damage adds to a hit, its dice rolled (twice over
    for a Critical Hit, as the rules roll all of an attack's damage dice),
    as (amount, damage type) parts, and the lines saying so: "Gabriel's
    Hunter's Mark: +4 Force (1d6)". Nothing is rolled for a plan without
    any, so a fight without them throws the dice it always did. A total
    rolled at the table (`plan.at_table`) is added as it is, critical or
    not: "+4 Force (rolled at the table)"."""
    parts = []
    lines = []
    for label, amount, damage_type in plan.extras:
        if label in plan.at_table:
            parts.append((int(amount), damage_type))
            lines.append(f"{label}: +{amount} {damage_type} (rolled at the table)")
            continue
        rolled = roll_dice(amount, critical)
        parts.append((rolled, damage_type))
        die = DIE.fullmatch(amount)
        if die is None:
            how = ""
        elif critical:
            how = f" ({int(die[1]) * 2}d{die[2]}, critical hit)"
        else:
            how = f" ({amount})"
        lines.append(f"{label}: +{rolled} {damage_type}{how}")
    return parts, tuple(lines)


def with_extra_damage(
    damage: list[tuple[int, str]], extra: list[tuple[int, str]]
) -> list[tuple[int, str]]:
    """A hit's damage with `extra` added: to its part of the same type, so
    Resistance halves that type's damage once, as one instance (Rules
    Glossary, Resistance), or as a part of its own type, last."""
    if not extra:
        return damage
    totals: dict[str, int] = {}
    for amount, damage_type in [*damage, *extra]:
        totals[damage_type] = totals.get(damage_type, 0) + amount
    return [(amount, damage_type) for damage_type, amount in totals.items()]


def is_immune_to(char: dict, condition: str) -> bool:
    """A monster's stat block lists its immunities, and a player's character
    knows theirs. A condition can give one too: Petrified, to Poisoned."""
    if immune_to_condition(char, condition):
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
