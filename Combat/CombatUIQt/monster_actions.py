"""A monster's abilities as the combat UI uses them on its turn: to-hit bonus,
damage dice, save DC and how often it can be used, from the combat effects
and fields written on each (MonsterAbility.combat_effects, recharge, ...), so
that freeform abilities, structured ones and ones reloaded from a saved fight
(plain dicts) all work the same. Nothing here reads an ability's text:
generate_monsters.py writes the effects from it
(Combat/Tools/monster_effect_text.py, Notes/explicit-attributes-plan.md
Phase 4.3), and an older log's are read as it loads (upgrade_ability_keys)."""

import random
import re
from dataclasses import dataclass, field

from Core.Definitions import DamageType
from Model.Content.CombatEffect import CombatEffect, EffectRoll
from Model.Content.CombatModifiers import AttackKind
from Model.Creatures.MonsterAbilities import (
    MonsterCast,
    ability_field,
    stated_reach_and_range,
)
from Model.Creatures.MonsterAbilityText import ABILITY_FIELDS, name_alone

# The stat blocks don't record this; nearly every legendary creature has 3.
LEGENDARY_ACTIONS_PER_ROUND = 3

# The sections of a stat block shown on a monster's turn, as (key, title).
ACTION_SECTIONS = (
    ("actions", "Actions"),
    ("bonus_actions", "Bonus Actions"),
    ("reactions", "Reactions"),
    ("legendary_actions", "Legendary Actions"),
)

DAMAGE_TYPE_NAMES = {t.value.lower(): t.value for t in DamageType}
_MINUS_SIGNS = "−–"
_DICE = rf"\d+d\d+(?:\s*[+{_MINUS_SIGNS}-]\s*\d+)?"
DAMAGE = re.compile(
    rf"(?:\d+\s*\(\s*(?P<dice>{_DICE})\s*\)|(?P<bare>{_DICE})|(?P<flat>\d+))"
    r"\s+(?:(?P<type>[A-Za-z]+)(?P<or>\s+or\s+[A-Za-z]+)?\s+)?damage"
)
JOINED = re.compile(r",?\s*(?:plus|and)\s+")
# One kind of die in a roll: "2d6" is (2, 6).
DIE = re.compile(r"(\d+)d(\d+)")


@dataclass(frozen=True)
class DamageRoll:
    dice: str  # "2d6 + 3", or "4" for a flat amount
    damage_type: str | None  # None when the monster chooses it as it attacks


@dataclass(frozen=True)
class MonsterAction:
    name: str
    description: str
    to_hit: int | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    half_on_save: bool = False
    damage: tuple[DamageRoll, ...] = field(default_factory=tuple)
    recharge_on: int | None = None  # the lowest d6 that brings it back
    per_day: int | None = None
    legendary_cost: int = 0
    # What its first effect says for the GM (its rider, a save its hit
    # forces), shown as it hits.
    notes: tuple[str, ...] = ()
    # What its stat block says using it does (MonsterAbility.combat_effects),
    # one per way to use it, each a picker row; () for one that has nothing
    # to apply (Multiattack).
    effects: tuple[CombatEffect, ...] = ()
    # A structured attack's (reach_ft, range_ft, long_range_ft) fields
    # (stated_reach_and_range); None for a freeform one, read from its text.
    stated_range: tuple[int | None, int | None, int | None] | None = None
    # The spells it casts, and the other ability it makes or uses
    # (MonsterAbility's fields of those names).
    casts: tuple[MonsterCast, ...] = ()
    uses_ability: str = ""
    moves_first: bool = False

    @property
    def is_limited(self) -> bool:
        return self.recharge_on is not None or self.per_day is not None

    @property
    def attack_kind(self) -> AttackKind | None:
        """Whether its attack is melee or ranged, as its text starts ("Melee
        Attack Roll: +6", the 2014 "Ranged Weapon Attack: +4"); None when it
        isn't an attack or could be either ("Melee or Ranged Attack Roll")."""
        if self.to_hit is None:
            return None
        text = self.description.lstrip().lower()
        if text.startswith("melee or ranged"):
            return None
        if text.startswith("melee"):
            return AttackKind.MELEE
        if text.startswith("ranged"):
            return AttackKind.RANGED
        return None

    @property
    def is_rollable(self) -> bool:
        return self.to_hit is not None or bool(self.damage)

    @property
    def summary(self) -> str:
        """Its numbers, as they read on its button."""
        parts = []
        if self.to_hit is not None:
            parts.append(f"{self.to_hit:+d}")
        if self.save_ability is not None:
            parts.append(f"DC {self.save_dc or '?'} {self.save_ability[:3]}")
        parts += [
            f"{roll.dice} {roll.damage_type or '(type of its choice)'}"
            for roll in self.damage
        ]
        if self.half_on_save:
            parts.append("half on save")
        return "  ".join(parts)


def legendary_actions_left(char: dict) -> int:
    """How many legendary actions char can still use before its next turn."""
    if not char.get("legendary_actions"):
        return 0
    return char.get("legendary_actions_left", LEGENDARY_ACTIONS_PER_ROUND)


def is_spent(char: dict, action: MonsterAction) -> bool:
    """Whether char has used up a recharge or per-day action."""
    return char.get("spent_abilities", {}).get(action.name, 0) >= (action.per_day or 1)


def legendary_resistances_left(char: dict) -> int:
    return char.get("legendary_resistances_left", char.get("legendary_resistances", 0))


def ability_text(ability) -> tuple[str, str]:
    """(name, description) of a MonsterAbility, or of the dict it becomes in a
    saved combat log."""
    if isinstance(ability, dict):
        return ability.get("name", ""), ability.get("description", "")
    return ability.name, ability.description


def ability_effects(ability) -> tuple[CombatEffect, ...]:
    """The combat effects written on a MonsterAbility, or on the dict it
    becomes in a saved combat log."""
    if isinstance(ability, dict):
        return tuple(
            CombatEffect.from_dict(e) for e in ability.get("combat_effects", ())
        )
    return tuple(getattr(ability, "combat_effects", ()))


def parse_action(ability, legendary: bool = False) -> MonsterAction:
    """What an ability rolls and costs, from its combat effects and fields
    (MonsterAbility): its first effect's attack or save and damage, for the
    turn column's buttons, or for an attack whose hit forces a save, that
    save's (its HIT-triggered effect after it); a recharge, uses per day, a
    legendary action's cost; the spells it casts and the ability it uses."""
    name, description = ability_text(ability)
    effects = ability_effects(ability)
    first = effects[0] if effects else None
    save = None
    if first is not None and first.roll == EffectRoll.SAVE:
        save = first
    elif first is not None and first.roll == EffectRoll.ATTACK:
        save = next(
            (
                e
                for e in effects[1:]
                if e.roll == EffectRoll.SAVE
                and e.trigger is not None
                and e.trigger.after == name
            ),
            None,
        )
    return MonsterAction(
        name=name,
        description=description,
        to_hit=(
            first.attack_bonus
            if first is not None and first.roll == EffectRoll.ATTACK
            else None
        ),
        save_ability=save.save_ability.value if save and save.save_ability else None,
        save_dc=save.dc if save is not None else None,
        half_on_save=save.half_on_success if save is not None else False,
        damage=tuple(
            DamageRoll(d.dice, d.damage_type.value if d.damage_type else None)
            for d in (first.damage if first is not None else ())
        ),
        notes=first.notes if first is not None else (),
        effects=effects,
        recharge_on=ability_field(ability, "recharge"),
        per_day=ability_field(ability, "per_day"),
        legendary_cost=ability_field(ability, "legendary_cost") if legendary else 0,
        stated_range=stated_reach_and_range(ability),
        casts=ability_field(ability, "casts"),
        uses_ability=ability_field(ability, "uses_ability"),
        moves_first=ability_field(ability, "moves_first"),
    )


def tidy_dice(dice: str) -> str:
    dice = re.sub(f"[{_MINUS_SIGNS}]", "-", dice)
    return re.sub(r"\s*([+-])\s*", r" \1 ", dice.strip())


def monster_actions(char: dict) -> list[tuple[str, list[MonsterAction]]]:
    """char's stat-block sections that have anything in them, parsed."""
    return [
        (
            title,
            [
                parse_action(ability, legendary=key == "legendary_actions")
                for ability in char[key]
            ],
        )
        for key, title in ACTION_SECTIONS
        if char.get(key)
    ]


def start_of_turn_traits(char: dict) -> list[tuple[str, str]]:
    """char's traits that do something at the start of its turn, as (name,
    the sentence saying what: its `at_turn_start`)."""
    found = []
    for trait in char.get("traits") or []:
        sentence = ability_field(trait, "at_turn_start")
        if sentence:
            found.append((ability_text(trait)[0], sentence))
    return found


ABILITY_SECTIONS = (
    "traits",
    "actions",
    "bonus_actions",
    "reactions",
    "legendary_actions",
    "lair_actions",
    "mythic_actions",
)


def picker_names(char) -> set[str]:
    """The names, lowercased and without their "(Recharge ...)", of the
    abilities the picker knows by name, which another can use (its action
    sections' and the traits with combat effects written on them).
    `char` is a combat dict or a stat block."""

    def get(key):
        if isinstance(char, dict):
            return char.get(key) or []
        return getattr(char, key, None) or []

    abilities = [a for key, _ in ACTION_SECTIONS for a in get(key)]
    abilities += [t for t in get("traits") if ability_effects(t)]
    return {name_alone(ability_text(a)[0]).lower() for a in abilities}


def upgrade_ability_keys(char: dict) -> dict:
    """A monster's combat dict from a log saved before its abilities had
    their fields (recharge, uses, cost, casts, turn start) or combat effects,
    with them read from their text once, in place
    (Combat/Tools/monster_effect_text.py). A log leaves out the fields at
    their defaults and an ability's effects when it has none
    (EncounterLogs._encode), so an ability dict without them is read: for a
    stat block that gives what it had, as its fields and effects say what
    its text does (tests/test_monster_ability_text.py,
    tests/test_monster_effect_text.py). One with any is left as it is."""
    from Combat.Tools.monster_effect_text import (
        read_ability_effects,
        read_ability_fields,
    )

    for section in ABILITY_SECTIONS:
        for ability in char.get(section) or []:
            if not isinstance(ability, dict):
                continue
            if not any(k in ability for k in ABILITY_FIELDS):
                read = read_ability_fields(char, ability, section)
                for key, value in read.items():
                    if key == "casts":
                        value = [vars(cast) for cast in value]
                    ability[key] = value
            if "combat_effects" not in ability:
                effects = read_ability_effects(ability, section)
                if effects:
                    ability["combat_effects"] = [e.to_dict() for e in effects]
    return char


def roll_dice(dice: str, critical: bool = False) -> int:
    """Roll "2d6 + 3" or a flat "4"; a critical hit rolls the dice twice over."""
    total = 0
    position = 0
    for match in DIE.finditer(dice):
        count, sides = int(match.group(1)), int(match.group(2))
        total += sum(
            random.randint(1, sides) for _ in range(count * (2 if critical else 1))
        )
        position = match.end()
    rest = dice[position:].replace(" ", "")
    return total + int(rest) if rest else total


def first_number(value) -> int | None:
    """The number an AC starts with: a monster's is a number, a player's a
    text like "18 (with Shield) and 16 (without Shield)"."""
    match = re.match(r"\s*(\d+)", str(value))
    return int(match.group(1)) if match else None
