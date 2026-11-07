"""What casting a spell rolls and does, as checked data rather than read from
its rules text: the entries of spells_<source>_mechanics.json, beside the
source JSON the SpellFactory loads. The combat UI's Custom Effect picker fills
its form from these (Combat/CombatUIQt/effect_options.py) and reads the text
only for a spell without one.

Only what the spell itself says is stored. The DC, attack bonus and
spellcasting modifier belong to whoever casts it, so they're worked out then.

An entry, every field optional:

    {
      "applicable": false,        # nothing for the Custom Effect form to apply
      "roll": "save",             # "save", "attack" or "none" (it just happens)
      "save": {"ability": "DEX", "half_on_success": true, "repeat": true},
      "damage": [{"dice": "8d6", "type": "Fire", "upcast": "1d6"}],
      "heal": {"dice": "2d8", "add_modifier": true, "upcast": "2d8"},
      "temp_hp": {"dice": "2d4 + 4", "upcast": "5"},   # or "heal", not both
      "condition": {"name": "Paralyzed", "until": ["end", "target"]},
      "badge": false,             # the spell's own name as a badge on the target
      "notes": ["..."]            # for the GM, about what the form can't say
    }

A damage entry can also have "add_modifier" (the caster's spellcasting
modifier is added), "choices" with "type": null (the caster picks the type),
and "cantrip" ({"5": "2d8", "11": "3d8", "17": "4d8"}: its dice once the
caster reaches each character level). A condition can have "alternatives".
"heal" is Hit Points regained and "temp_hp" Temporary Hit Points; the Custom
Effect form has one amount box, so an entry has at most one of them, and a
"temp_hp" upcast can be a flat number.
"""

import re
from dataclasses import dataclass
from typing import Any

from Core.Definitions import Condition, DamageType

ROLLS = ("save", "attack", "none")
SAVE_ABILITIES = ("STR", "DEX", "CON", "INT", "WIS", "CHA")
CANTRIP_LEVELS = ("5", "11", "17")
# "1d6", or "1d4 + 1" (Magic Missile's dart).
DICE = re.compile(r"\d+d\d+(?: [+-] \d+)?")
_UPCAST_DICE = re.compile(r"\d+d\d+")
_UPCAST_DICE_OR_NUMBER = re.compile(r"\d+d\d+|\d+")
_DICE_OR_NUMBER = re.compile(rf"{DICE.pattern}|\d+")
# ("start" or "end", "source" or "target"): "until the end of its next turn"
# is ("end", "target"), as the combat UI's EffectOption.until has it.
_UNTIL_EDGES = ("start", "end")
_UNTIL_WHOSE = ("source", "target")

_DAMAGE_TYPES = tuple(damage_type.value for damage_type in DamageType)
_CONDITIONS = tuple(condition.value for condition in Condition)


@dataclass(frozen=True)
class SaveSpec:
    ability: str  # short, as SAVE_ABILITIES has it
    half_on_success: bool = False
    # The target repeats it at the end of each of its turns, ending it on itself.
    repeat: bool = False


@dataclass(frozen=True)
class DamageSpec:
    dice: str
    damage_type: str | None  # None: the caster picks one of `choices`
    choices: tuple[str, ...] = ()
    add_modifier: bool = False
    upcast: str = ""  # what it gains per slot level above the spell's
    # A cantrip's dice from each character level on: ((5, "2d8"), ...).
    cantrip: tuple[tuple[int, str], ...] = ()


@dataclass(frozen=True)
class HealSpec:
    dice: str
    add_modifier: bool = False
    upcast: str = ""


@dataclass(frozen=True)
class ConditionSpec:
    name: str
    alternatives: tuple[str, ...] = ()
    until: tuple[str, str] | None = None


@dataclass(frozen=True)
class SpellMechanics:
    applicable: bool = True
    roll: str = "none"
    save: SaveSpec | None = None
    damage: tuple[DamageSpec, ...] = ()
    heal: HealSpec | None = None
    temp_hp: HealSpec | None = None
    condition: ConditionSpec | None = None
    badge: bool | None = None  # None: as the combat UI decides
    notes: tuple[str, ...] = ()


class _Reader:
    """Reads one spell's entry, saying which spell and field when it's wrong."""

    def __init__(self, spell_name: str):
        self.spell_name = spell_name

    def fail(self, field: str, problem: str) -> None:
        raise ValueError(
            f"Invalid mechanics for spell {self.spell_name!r}, {field}: {problem}"
        )

    def mapping(
        self, value: Any, field: str, allowed: tuple[str, ...]
    ) -> dict[str, Any]:
        if not isinstance(value, dict):
            self.fail(field, f"expected an object, got {value!r}")
        unknown = sorted(set(value) - set(allowed))
        if unknown:
            self.fail(field, f"unknown key(s) {unknown}")
        return value

    def flag(self, data: dict, key: str, field: str, default: bool = False) -> bool:
        value = data.get(key, default)
        if not isinstance(value, bool):
            self.fail(f"{field}.{key}", f"expected true or false, got {value!r}")
        return value

    def one_of(self, value: Any, field: str, allowed: tuple[str, ...]) -> str:
        if value not in allowed:
            self.fail(field, f"{value!r} is not one of {list(allowed)}")
        return value

    def dice(self, value: Any, field: str, pattern: re.Pattern[str] = DICE) -> str:
        if not isinstance(value, str) or not pattern.fullmatch(value):
            self.fail(field, f"{value!r} is not dice like '2d6'")
        return value

    def strings(self, value: Any, field: str) -> tuple[str, ...]:
        if not isinstance(value, list) or not all(
            isinstance(item, str) and item for item in value
        ):
            self.fail(field, f"expected a list of text, got {value!r}")
        return tuple(value)

    def save(self, value: Any) -> SaveSpec:
        data = self.mapping(value, "save", ("ability", "half_on_success", "repeat"))
        return SaveSpec(
            ability=self.one_of(data.get("ability"), "save.ability", SAVE_ABILITIES),
            half_on_success=self.flag(data, "half_on_success", "save"),
            repeat=self.flag(data, "repeat", "save"),
        )

    def damage(self, value: Any, field: str) -> DamageSpec:
        keys = ("dice", "type", "choices", "add_modifier", "upcast", "cantrip")
        data = self.mapping(value, field, keys)
        damage_type = data.get("type")
        choices = self.strings(data.get("choices", []), f"{field}.choices")
        for choice in choices:
            self.one_of(choice, f"{field}.choices", _DAMAGE_TYPES)
        if damage_type is None:
            if len(choices) < 2:
                self.fail(field, "a type to choose needs two or more 'choices'")
        else:
            self.one_of(damage_type, f"{field}.type", _DAMAGE_TYPES)
            if choices:
                self.fail(field, "'choices' is only for a 'type' of null")
        upcast = data.get("upcast", "")
        if upcast:
            self.dice(upcast, f"{field}.upcast", _UPCAST_DICE)
        return DamageSpec(
            dice=self.dice(data.get("dice"), f"{field}.dice"),
            damage_type=damage_type,
            choices=choices,
            add_modifier=self.flag(data, "add_modifier", field),
            upcast=upcast,
            cantrip=self.cantrip(data.get("cantrip", {}), f"{field}.cantrip"),
        )

    def cantrip(self, value: Any, field: str) -> tuple[tuple[int, str], ...]:
        data = self.mapping(value, field, CANTRIP_LEVELS)
        if data and set(data) != set(CANTRIP_LEVELS):
            self.fail(field, f"needs all of levels {list(CANTRIP_LEVELS)}")
        return tuple(
            (int(level), self.dice(data[level], f"{field}.{level}", _UPCAST_DICE))
            for level in CANTRIP_LEVELS
            if level in data
        )

    def heal(self, value: Any, field: str = "heal") -> HealSpec:
        data = self.mapping(value, field, ("dice", "add_modifier", "upcast"))
        # Temporary Hit Points are often a number: "You gain 5 Temporary Hit
        # Points", "5 additional Temporary Hit Points for each slot level".
        temporary = field == "temp_hp"
        upcast = data.get("upcast", "")
        if upcast:
            pattern = _UPCAST_DICE_OR_NUMBER if temporary else _UPCAST_DICE
            self.dice(upcast, f"{field}.upcast", pattern)
        return HealSpec(
            dice=self.dice(
                data.get("dice"),
                f"{field}.dice",
                _DICE_OR_NUMBER if temporary else DICE,
            ),
            add_modifier=self.flag(data, "add_modifier", field),
            upcast=upcast,
        )

    def condition(self, value: Any) -> ConditionSpec:
        data = self.mapping(value, "condition", ("name", "alternatives", "until"))
        alternatives = self.strings(
            data.get("alternatives", []), "condition.alternatives"
        )
        for alternative in alternatives:
            self.one_of(alternative, "condition.alternatives", _CONDITIONS)
        until = data.get("until")
        if until is not None:
            if not isinstance(until, list) or len(until) != 2:
                self.fail("condition.until", f"expected [edge, whose], got {until!r}")
            self.one_of(until[0], "condition.until", _UNTIL_EDGES)
            self.one_of(until[1], "condition.until", _UNTIL_WHOSE)
            until = (until[0], until[1])
        return ConditionSpec(
            name=self.one_of(data.get("name"), "condition.name", _CONDITIONS),
            alternatives=alternatives,
            until=until,
        )


_ENTRY_KEYS = (
    "applicable",
    "roll",
    "save",
    "damage",
    "heal",
    "temp_hp",
    "condition",
    "badge",
    "notes",
)


def parse_mechanics(spell_name: str, value: Any) -> SpellMechanics:
    """A spell's mechanics entry, checked: ValueError naming the spell and the
    field when anything in it is unknown, missing or of the wrong kind."""
    read = _Reader(spell_name)
    data = read.mapping(value, "entry", _ENTRY_KEYS)
    roll = read.one_of(data.get("roll", "none"), "roll", ROLLS)
    save = read.save(data["save"]) if "save" in data else None
    if (roll == "save") != (save is not None):
        read.fail("save", "a 'save' goes with a 'roll' of \"save\", and only then")
    damage_list = data.get("damage", [])
    if not isinstance(damage_list, list):
        read.fail("damage", f"expected a list, got {damage_list!r}")
    if "heal" in data and "temp_hp" in data:
        read.fail("temp_hp", "one of 'heal' and 'temp_hp': put the other in notes")
    badge = data.get("badge")
    if badge is not None and not isinstance(badge, bool):
        read.fail("badge", f"expected true or false, got {badge!r}")
    return SpellMechanics(
        applicable=read.flag(data, "applicable", "entry", default=True),
        roll=roll,
        save=save,
        damage=tuple(
            read.damage(entry, f"damage[{index}]")
            for index, entry in enumerate(damage_list)
        ),
        heal=read.heal(data["heal"]) if "heal" in data else None,
        temp_hp=read.heal(data["temp_hp"], "temp_hp") if "temp_hp" in data else None,
        condition=read.condition(data["condition"]) if "condition" in data else None,
        badge=badge,
        notes=read.strings(data.get("notes", []), "notes"),
    )
