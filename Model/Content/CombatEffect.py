"""What one use of a spell, a feature or a monster's ability does in a fight,
so the combat simulator doesn't have to read it from the rules text. One
model for all three (Notes/combat-effects-plan.md):

- a feature says it in Python (Feature.combat_effects);
- a spell says it in Python, in its class in CharacterContent/Spells/
  SpellClasses (Spell.combat_effects);
- a monster's ability has it written on it (MonsterAbility.combat_effects).

to_dict() and from_dict() are what a fight's log keeps. The combat UI's Custom Effect picker fills its
form from these (Combat/CombatUIQt/effect_options.py).

What depends on who uses it is left blank and worked out then: the DC (a
feature's calculate_dc(), a spell's caster), the attack bonus, the
spellcasting modifier (`add_modifier`), the dice at the user's level
(`cantrip`) and at the slot cast with (`upcast`). A feature knows its
character, so it often works its numbers out itself; a spell can't. Whatever
else is left unset falls back to what the source says - a feature's
FeatureActivation and FeatureUses, a spell's casting time, duration and
Concentration, a monster ability's stat-block section and recharge. Most
effects only say what they roll and do:

    CombatEffect(
        name="Jolt to Life",
        roll=EffectRoll.SAVE,
        save_ability=Ability.DEXTERITY,
        half_on_success=True,
        damage=(CombatDamage("2d4", DamageType.LIGHTNING),),
        notes=("...",),
    )

Its conditions are what land on a target: on a failed save, on a hit, or on
every target when there's no roll. Each is a rules condition (Prone) or a
badge naming what the target has (Bardic Inspiration, Bless), which the
target's card can be clicked on to read. Nothing is put on a target unless
the effect says so.

Several uses (Command's options, Divine Spark's healing or harm) are several
effects, one picker row each. Several attacks or darts from one use
(Scorching Ray) are its `instances`. Damage only some targets take (Divine
Smite's extra 1d8 against a Fiend or an Undead) has a `when`.
"""

import re
from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Any

from Core.Definitions import Ability, Condition, DamageType
from Model.Content.ActionType import ActionType
from Model.Content.CombatModifiers import (
    MODIFIER_CLASSES,
    HasConditions,
    Modifier,
    modifier_from_dict,
    modifier_to_dict,
)

# "2d4", "1d8 + 3", or a flat "5".
DICE = re.compile(r"\d+d\d+(?: [+-] \d+)?|\d+")
# What a slot level above the spell's adds: dice ("1d6"), or for Hit Points
# also a number ("5": False Life).
_UPCAST_DICE = re.compile(r"\d+d\d+")
_UPCAST_DICE_OR_NUMBER = re.compile(r"\d+d\d+|\d+")
# The character levels a cantrip's dice grow at.
CANTRIP_LEVELS = (5, 11, 17)


class EffectRoll(StrEnum):
    """What one use rolls. A StrEnum, so it's its text ("save") in JSON, in
    logs and wherever it's compared with text."""

    SAVE = "save"  # each target saves
    ATTACK = "attack"  # the user rolls against each target's AC
    NONE = "none"  # it just happens, to every target


class TurnEdge(StrEnum):
    """Which edge of a turn a condition lasts until."""

    START = "start"
    END = "end"


class TurnOf(StrEnum):
    """Whose next turn a condition lasts until: the one who used it, or the
    target it landed on."""

    SOURCE = "source"
    TARGET = "target"


def _is_rules_condition(name: str) -> bool:
    """Whether `name` is a rules condition, or one under a longer name
    ("Restrained by vines"), as the combat simulator reads it."""
    return any(
        name == condition.value or name.startswith(f"{condition.value} ")
        for condition in Condition
    )


def with_bonus(dice: str, bonus: int) -> str:
    """`dice` plus a flat bonus, as an amount is written: "1d8 + 4",
    "1d8 - 1", or "1d8" for a bonus of 0."""
    if not bonus:
        return dice
    return f"{dice} {'+' if bonus > 0 else '-'} {abs(bonus)}"


@dataclass(frozen=True)
class CombatDamage:
    """Damage one use deals: dice and a type, or None with the types the user
    chooses from. A spell's damage can also grow: `upcast` per slot level
    above the spell's, `cantrip` from each of CANTRIP_LEVELS on, and
    `add_modifier` adds the caster's spellcasting ability modifier. Dice
    "0" with `add_modifier` is the modifier alone (Green-Flame Blade's
    fire "equal to your spellcasting ability modifier", before its
    cantrip dice)."""

    dice: str
    damage_type: DamageType | None
    choices: tuple[DamageType, ...] = ()
    upcast: str = ""
    # ((5, "2d8"), (11, "3d8"), (17, "4d8")): the dice once the user reaches
    # each character level.
    cantrip: tuple[tuple[int, str], ...] = ()
    add_modifier: bool = False
    # Taken only by a target this is true of, as the user judges, said as
    # what follows "if": "the target is a Fiend or an Undead". "" is every
    # target the damage hits.
    when: str = ""

    def __post_init__(self):
        if not DICE.fullmatch(self.dice):
            raise ValueError(f"{self.dice!r} is not dice like '2d4' or '1d8 + 3'")
        if self.damage_type is None and len(self.choices) < 2:
            raise ValueError("A damage type to choose needs two or more choices")
        if self.damage_type is not None and self.choices:
            raise ValueError("Choices are only for a damage type of None")
        if self.upcast and not _UPCAST_DICE.fullmatch(self.upcast):
            raise ValueError(f"upcast {self.upcast!r} is not dice like '1d6'")
        _check_cantrip(self.cantrip)


@dataclass(frozen=True)
class CombatHitPoints:
    """Hit Points each target regains, or Temporary Hit Points it gains:
    dice ("1d10 + 3", "5"), or "" for an amount the user types (Lay on Hands
    spends what it likes from a pool). `upcast` and `add_modifier` as for
    CombatDamage; Temporary Hit Points can upcast by a number. No dice with
    `add_modifier` is the modifier alone (Heroism's "Temporary Hit Points
    equal to your spellcasting ability modifier")."""

    dice: str = ""
    upcast: str = ""
    add_modifier: bool = False

    def __post_init__(self):
        if self.dice and not DICE.fullmatch(self.dice):
            raise ValueError(f"{self.dice!r} is not dice like '2d4 + 3'")
        if self.upcast and not _UPCAST_DICE_OR_NUMBER.fullmatch(self.upcast):
            raise ValueError(f"upcast {self.upcast!r} is not dice or a number")


@dataclass(frozen=True)
class CombatCondition:
    """What lands on a target, and for how long: `until` a turn's start or
    end, or `duration_seconds` (None: the source's own duration). "Until the
    end of its next turn" is until=(TurnEdge.END, TurnOf.TARGET).

    A badge (Bless, Shield of Faith) can say what it does to the target's
    rolls, AC and damage while it has it, in `modifiers`
    (Model/Content/CombatModifiers.py): Bless's D20Bonus, Shield of Faith's
    ArmorClass. A rules condition has its rules already
    (Model/Content/RulesConditions.py), so it takes none."""

    name: str
    until: tuple[TurnEdge, TurnOf] | None = None
    duration_seconds: int | None = None
    modifiers: tuple[Modifier, ...] = ()

    def __post_init__(self):
        # A rules condition can be given as itself (Condition.PRONE); it's
        # kept as its name, as a badge's is, so logs and the dialog see text.
        if isinstance(self.name, Condition):
            object.__setattr__(self, "name", self.name.value)
        if not self.name.strip():
            raise ValueError("A condition needs a name")
        if not isinstance(self.modifiers, tuple) or not all(
            isinstance(m, MODIFIER_CLASSES) for m in self.modifiers
        ):
            raise ValueError(
                f"modifiers is a tuple of modifiers, like (ArmorClass(2),),"
                f" not {self.modifiers!r}"
            )
        if self.modifiers and _is_rules_condition(self.name):
            raise ValueError(
                f"{self.name} is a rules condition: its modifiers are the rules'"
            )
        if any(isinstance(m, HasConditions) for m in self.modifiers):
            raise ValueError(
                "A badge gives a condition through `conditions`, not HasConditions"
            )
        if self.until is not None:
            # Text ("end", "target") is taken too, as JSON and logs have it.
            edge, whose = self.until
            if edge not in set(TurnEdge) or whose not in set(TurnOf):
                raise ValueError(
                    f"until must be ({'|'.join(TurnEdge)}, {'|'.join(TurnOf)}),"
                    f" got {self.until!r}"
                )
            object.__setattr__(self, "until", (TurnEdge(edge), TurnOf(whose)))


@dataclass(frozen=True)
class CombatInstances:
    """How many times one use rolls and deals its damage: Scorching Ray's
    three rays (one more per slot level above 2), Eldritch Blast's beams
    (two from character level 5, ...), each against one target or several.
    `noun` names one ("ray") for the picker's row."""

    count: int
    upcast: int = 0
    # ((5, 2), (11, 3), (17, 4)): the count once the user reaches each level.
    cantrip: tuple[tuple[int, int], ...] = ()
    noun: str = ""

    def __post_init__(self):
        if isinstance(self.count, bool) or self.count < 1:
            raise ValueError(f"count must be 1 or more, got {self.count!r}")
        if self.upcast < 0:
            raise ValueError(f"upcast can't be negative, got {self.upcast!r}")
        if self.cantrip and tuple(level for level, _ in self.cantrip) != CANTRIP_LEVELS:
            raise ValueError(
                f"cantrip needs one step at each of levels {CANTRIP_LEVELS}"
            )

    def at(self, char_level: int, levels_up: int) -> int:
        """The count for a user of char_level casting `levels_up` slot levels
        above the spell's."""
        count = self.count
        for level, step in self.cantrip:
            if char_level >= level:
                count = step
        return count + self.upcast * levels_up


@dataclass(frozen=True)
class CombatEffect:
    """One use in a fight: what it rolls, what it does to its targets and
    what it costs. See the module docstring."""

    # The picker's row and the log's name for it; "" is the source's name.
    # A source with several uses (Reanimator's Skill Set's Jolt to Life,
    # Command's options) names each.
    name: str = ""
    # SAVE: each target saves; ATTACK: the user rolls against each target's
    # AC; NONE: it just happens, to every target.
    roll: EffectRoll = EffectRoll.NONE
    save_ability: Ability | None = None
    dc: int | None = None  # None: the source's (a feature's calculate_dc())
    half_on_success: bool = False
    # A target repeats the save at the end of each of its turns, ending the
    # condition on itself.
    repeat_save: bool = False
    attack_bonus: int | None = None  # None: the user's spell attack bonus
    damage: tuple[CombatDamage, ...] = ()
    # Hit Points each target regains, or Temporary Hit Points it gains. Every
    # target gets them, whatever the roll. The form has one amount box, so
    # only one of damage, healing and temp_hp can be set: the rest go in the
    # notes.
    healing: CombatHitPoints | None = None
    temp_hp: CombatHitPoints | None = None
    # Each lands on every target that fails or is hit: Turn Undead's
    # Frightened and Incapacitated. They last the same time and end together.
    conditions: tuple[CombatCondition, ...] = ()
    # Rolls and damage repeated in one use; None is once.
    instances: CombatInstances | None = None
    # None: the source's action (a feature's FeatureActivation, a spell's
    # casting time). Set it when using it takes an action the source doesn't
    # say, like the casting of the spell a feature's use rides on.
    action_type: ActionType | None = None
    # True also holds Concentration; a spell's own Concentration counts anyway.
    concentration: bool = False
    # Whether it spends one of the feature's FeatureUses (if it has any).
    spends_use: bool = True
    # The spell it casts, if any: a condition it gives is that spell's badge,
    # and shows the spell when clicked.
    spell: str | None = None
    # For the user, about what the form can't do (moving, a choice, a rider).
    notes: tuple[str, ...] = ()

    def __post_init__(self):
        # Text ("save") is taken too, as JSON and logs have it.
        if self.roll not in set(EffectRoll):
            raise ValueError(f"roll {self.roll!r} is not one of {list(EffectRoll)}")
        object.__setattr__(self, "roll", EffectRoll(self.roll))
        if (self.roll is EffectRoll.SAVE) != (self.save_ability is not None):
            raise ValueError("A save_ability goes with a roll of 'save', and only then")
        if self.roll is not EffectRoll.SAVE and (
            self.half_on_success or self.repeat_save
        ):
            raise ValueError("half_on_success and repeat_save are for a 'save' only")
        if self.roll is not EffectRoll.SAVE and self.dc is not None:
            raise ValueError("A dc is for a 'save' only")
        if self.roll is not EffectRoll.ATTACK and self.attack_bonus is not None:
            raise ValueError("An attack_bonus is for an 'attack' only")
        if any(not note.strip() for note in self.notes):
            raise ValueError("A note can't be empty")
        names = [condition.name for condition in self.conditions]
        if len(names) != len(set(names)):
            raise ValueError(f"A condition is named twice: {names}")
        for field, points in (("healing", self.healing), ("temp_hp", self.temp_hp)):
            if points is not None and not isinstance(points, CombatHitPoints):
                raise ValueError(
                    f"{field} is a CombatHitPoints, like CombatHitPoints('2d4 + 3'),"
                    f" not {points!r}"
                )
        amounts = [
            bool(self.damage),
            self.healing is not None,
            self.temp_hp is not None,
        ]
        if sum(amounts) > 1:
            raise ValueError(
                "Only one of damage, healing and temp_hp: the rest go in notes"
            )

    def to_dict(self) -> dict:
        """The effect as plain data, leaving out what's at its default: what
        a spell's combat effects file holds, and from_dict reads back."""
        return _compact(self)

    @classmethod
    def from_dict(cls, data: Any, where: str = "a combat effect") -> "CombatEffect":
        """The effect `data` describes: what to_dict writes, or what a saved
        fight's log holds (dataclasses.asdict of it, every field written).
        ValueError naming `where` and the field when anything is unknown,
        missing or of the wrong kind."""
        return _Reader(where).effect(data)


def _check_cantrip(steps: tuple[tuple[int, str], ...]) -> None:
    if not steps:
        return
    if tuple(level for level, _ in steps) != CANTRIP_LEVELS:
        raise ValueError(f"cantrip needs one step at each of levels {CANTRIP_LEVELS}")
    for _, dice in steps:
        if not _UPCAST_DICE.fullmatch(dice):
            raise ValueError(f"cantrip dice {dice!r} is not dice like '2d8'")


def _compact(value: Any) -> Any:
    """`value` as JSON-ready data: a dataclass as a dict without its default
    fields, enums as their values, a cantrip's steps as {"5": "2d8", ...},
    a modifier as modifier_to_dict writes it."""
    if isinstance(value, (Ability, DamageType, ActionType, StrEnum)):
        return value.value
    if isinstance(value, MODIFIER_CLASSES):
        return modifier_to_dict(value)
    if isinstance(
        value,
        (CombatEffect, CombatDamage, CombatHitPoints, CombatCondition, CombatInstances),
    ):
        data = {}
        for field in fields(value):
            item = getattr(value, field.name)
            if item == field.default:
                continue
            if field.name == "cantrip":
                data["cantrip"] = {str(level): step for level, step in item}
            else:
                data[field.name] = _compact(item)
        return data
    if isinstance(value, tuple):
        return [_compact(item) for item in value]
    return value


_DAMAGE_KEYS = tuple(f.name for f in fields(CombatDamage))
_HIT_POINTS_KEYS = tuple(f.name for f in fields(CombatHitPoints))
_CONDITION_KEYS = tuple(f.name for f in fields(CombatCondition))
_INSTANCES_KEYS = tuple(f.name for f in fields(CombatInstances))
# "condition": one condition, as logs before 2026-11-09 have it.
_EFFECT_KEYS = (*(f.name for f in fields(CombatEffect)), "condition")


class _Reader:
    """Reads one effect's data, saying where and which field when it's wrong."""

    def __init__(self, where: str):
        self.where = where

    def fail(self, field: str, problem: str):
        raise ValueError(f"Invalid combat effect of {self.where}, {field}: {problem}")

    def mapping(self, value: Any, field: str, allowed: tuple[str, ...]) -> dict:
        if not isinstance(value, dict):
            self.fail(field, f"expected an object, got {value!r}")
        unknown = sorted(set(value) - set(allowed))
        if unknown:
            self.fail(field, f"unknown key(s) {unknown}, known: {list(allowed)}")
        return value

    def kind(self, value: Any, field: str, types: tuple[type, ...], default=None):
        """`value` if it's one of `types` (None gives `default`). A bool isn't
        an int here."""
        if value is None:
            return default
        if isinstance(value, bool) and bool not in types:
            self.fail(field, f"expected {types[0].__name__}, got {value!r}")
        if not isinstance(value, types):
            self.fail(field, f"expected {types[0].__name__}, got {value!r}")
        return value

    def enum(self, value: Any, field: str, enum_type):
        if value is None:
            return None
        try:
            return enum_type(value)
        except ValueError:
            known = [member.value for member in enum_type]
            self.fail(field, f"{value!r} is not one of {known}")

    def strings(self, value: Any, field: str) -> tuple[str, ...]:
        if value is None:
            return ()
        if not isinstance(value, (list, tuple)) or not all(
            isinstance(item, str) for item in value
        ):
            self.fail(field, f"expected a list of text, got {value!r}")
        return tuple(value)

    def build(self, field: str, make, **kwargs):
        """make(**kwargs), with its own checks' ValueError saying where."""
        try:
            return make(**kwargs)
        except (ValueError, TypeError) as error:
            self.fail(field, str(error))

    def cantrip(self, value: Any, field: str, step_type: type = str) -> tuple:
        """{"5": step, "11": step, "17": step}, or a log's [[5, step], ...],
        each step a `step_type` (dice, or a count)."""
        if not value:
            return ()
        if isinstance(value, dict):
            pairs = list(value.items())
        elif isinstance(value, (list, tuple)):
            pairs = [tuple(pair) for pair in value]
        else:
            self.fail(
                field, f"expected {{'5': ..., '11': ..., '17': ...}}, got {value!r}"
            )
        steps = []
        for level, step in pairs:
            if not str(level).isdigit() or type(step) is not step_type:
                self.fail(
                    field, f"expected {{'5': ..., '11': ..., '17': ...}}, got {value!r}"
                )
            steps.append((int(level), step))
        return tuple(sorted(steps))

    def damage(self, value: Any, field: str) -> CombatDamage:
        data = self.mapping(value, field, _DAMAGE_KEYS)
        choices = self.strings(data.get("choices"), f"{field}.choices")
        return self.build(
            field,
            CombatDamage,
            dice=self.kind(data.get("dice"), f"{field}.dice", (str,), ""),
            damage_type=self.enum(
                data.get("damage_type"), f"{field}.damage_type", DamageType
            ),
            choices=tuple(
                self.enum(choice, f"{field}.choices", DamageType) for choice in choices
            ),
            upcast=self.kind(data.get("upcast"), f"{field}.upcast", (str,), ""),
            cantrip=self.cantrip(data.get("cantrip"), f"{field}.cantrip"),
            add_modifier=self.kind(
                data.get("add_modifier"), f"{field}.add_modifier", (bool,), False
            ),
            when=self.kind(data.get("when"), f"{field}.when", (str,), ""),
        )

    def hit_points(self, value: Any, field: str) -> CombatHitPoints | None:
        if value is None:
            return None
        if isinstance(value, str):  # how logs before 2026-11-08 kept it
            return self.build(field, CombatHitPoints, dice=value)
        data = self.mapping(value, field, _HIT_POINTS_KEYS)
        return self.build(
            field,
            CombatHitPoints,
            dice=self.kind(data.get("dice"), f"{field}.dice", (str,), ""),
            upcast=self.kind(data.get("upcast"), f"{field}.upcast", (str,), ""),
            add_modifier=self.kind(
                data.get("add_modifier"), f"{field}.add_modifier", (bool,), False
            ),
        )

    def condition(self, value: Any, field: str) -> CombatCondition:
        data = self.mapping(value, field, _CONDITION_KEYS)
        until = data.get("until")
        if until is not None:
            if not isinstance(until, (list, tuple)) or len(until) != 2:
                self.fail(f"{field}.until", f"expected [edge, whose], got {until!r}")
            until = (until[0], until[1])
        return self.build(
            field,
            CombatCondition,
            name=self.kind(data.get("name"), f"{field}.name", (str,), ""),
            until=until,
            duration_seconds=self.kind(
                data.get("duration_seconds"), f"{field}.duration_seconds", (int,)
            ),
            modifiers=self.modifiers(data.get("modifiers"), f"{field}.modifiers"),
        )

    def modifiers(self, value: Any, field: str) -> tuple[Modifier, ...]:
        """A condition's modifiers; none in data from before they existed."""
        if value is None:
            return ()
        if not isinstance(value, (list, tuple)):
            self.fail(field, f"expected a list, got {value!r}")
        return tuple(
            modifier_from_dict(item, f"{self.where}, {field}[{index}]")
            for index, item in enumerate(value)
        )

    def conditions(self, data: dict) -> tuple[CombatCondition, ...]:
        """Its "conditions", or the one "condition" an older log has."""
        if data.get("condition") is not None:
            if data.get("conditions"):
                self.fail("condition", "give 'conditions' or 'condition', not both")
            return (self.condition(data["condition"], "condition"),)
        value = data.get("conditions") or []
        if not isinstance(value, (list, tuple)):
            self.fail("conditions", f"expected a list, got {value!r}")
        return tuple(
            self.condition(item, f"conditions[{index}]")
            for index, item in enumerate(value)
        )

    def instances(self, value: Any) -> CombatInstances | None:
        if value is None:
            return None
        data = self.mapping(value, "instances", _INSTANCES_KEYS)
        return self.build(
            "instances",
            CombatInstances,
            count=self.kind(data.get("count"), "instances.count", (int,), 0),
            upcast=self.kind(data.get("upcast"), "instances.upcast", (int,), 0),
            cantrip=self.cantrip(data.get("cantrip"), "instances.cantrip", int),
            noun=self.kind(data.get("noun"), "instances.noun", (str,), ""),
        )

    def effect(self, value: Any) -> CombatEffect:
        data = self.mapping(value, "effect", _EFFECT_KEYS)
        damage = data.get("damage") or []
        if not isinstance(damage, (list, tuple)):
            self.fail("damage", f"expected a list, got {damage!r}")
        return self.build(
            "effect",
            CombatEffect,
            name=self.kind(data.get("name"), "name", (str,), ""),
            roll=self.enum(data.get("roll"), "roll", EffectRoll) or EffectRoll.NONE,
            save_ability=self.enum(data.get("save_ability"), "save_ability", Ability),
            dc=self.kind(data.get("dc"), "dc", (int,)),
            half_on_success=self.kind(
                data.get("half_on_success"), "half_on_success", (bool,), False
            ),
            repeat_save=self.kind(
                data.get("repeat_save"), "repeat_save", (bool,), False
            ),
            attack_bonus=self.kind(data.get("attack_bonus"), "attack_bonus", (int,)),
            damage=tuple(
                self.damage(part, f"damage[{index}]")
                for index, part in enumerate(damage)
            ),
            healing=self.hit_points(data.get("healing"), "healing"),
            temp_hp=self.hit_points(data.get("temp_hp"), "temp_hp"),
            conditions=self.conditions(data),
            instances=self.instances(data.get("instances")),
            action_type=self.enum(data.get("action_type"), "action_type", ActionType),
            concentration=self.kind(
                data.get("concentration"), "concentration", (bool,), False
            ),
            spends_use=self.kind(data.get("spends_use"), "spends_use", (bool,), True),
            spell=self.kind(data.get("spell"), "spell", (str,)),
            notes=self.strings(data.get("notes"), "notes"),
        )
