"""How far an attack reaches, checked on the battle map, with no Qt
(Notes/combat-arena-plan.md, step 20).

The rules (Player's Handbook, Making an Attack; Rules Glossary, Reach and
Range):

- A melee attack reaches 5 feet, 10 with a Reach weapon, or as far as a stat
  block's "reach 10 ft." says.
- A ranged attack has a normal and a long range ("Range (80/320)"): it has
  Disadvantage past the normal range and can't reach past the long one. A
  spell's attack has only its range.
- "Ranged Attacks in Close Combat": a ranged attack roll has Disadvantage
  while the attacker is within 5 feet of an enemy that can see it and
  doesn't have the Incapacitated condition.

On the map (Decision 31): what has Disadvantage is counted into the roll;
an attack past its reach or range is warned about, not refused, as an area
aimed past its range is (Decision 19). A weapon that's both (a Dagger, which
can be thrown) is a melee attack within its reach and a thrown one past it.
Whether the enemy close by can see the attacker is counted from the map's
sight (Combat/Arena/senses.py, step 28): one that can't (Blinded, the
attacker Invisible or in Darkness to it) imposes nothing, and says so.

The check also carries the map's `Sight` of the two (whether each sees the
other), which attack_plan counts (Invisible's, Heavily Obscured's)."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Iterable

from Combat.Arena.arena import ArenaSettings, distance_ft
from Combat.Arena.senses import sees
from Combat.Effects.modifiers import has_condition
from Combat.Effects.sight import NO_SIGHT, Sight
from Combat.Effects.triggers import on_party_side
from Core.Definitions import Condition
from Core.Weapons import WEAPON_RANGES_FT, WeaponProperty
from Model.Content.CombatModifiers import D20Mode, D20Test, RollMode

# Rules Glossary, Reach: 5 feet, 10 with a Reach weapon.
MELEE_REACH_FT = 5
REACH_WEAPON_FT = 10
# "Ranged Attacks in Close Combat": an enemy within 5 feet.
CLOSE_COMBAT_FT = 5

_REACH = re.compile(r"\breach (\d+) ?ft", re.IGNORECASE)
_RANGE = re.compile(r"\brange (\d+)(?:/(\d+))? ?ft", re.IGNORECASE)
_RANGED_SPELL = re.compile(r"\branged spell attack", re.IGNORECASE)
_MELEE_SPELL = re.compile(r"\bmelee spell attack", re.IGNORECASE)


@dataclass(frozen=True)
class AttackRange:
    """How far an attack goes: a melee one's `reach_ft`, a ranged one's
    `normal_ft` and `long_ft` (None: nothing past normal, as a spell's), or
    both for one that can be either (a thrown Dagger, a monster's "Melee or
    Ranged Attack Roll"). `what` names it in the notes."""

    reach_ft: int | None = None
    normal_ft: int | None = None
    long_ft: int | None = None
    what: str = ""

    @property
    def range_text(self) -> str:
        """ "80/320 ft.", "120 ft." for a spell; "" with no range."""
        if self.normal_ft is None:
            return ""
        far = f"/{self.long_ft}" if self.long_ft else ""
        return f"{self.normal_ft}{far} ft."

    @property
    def text(self) -> str:
        """ "reach 5 ft.", "range 80/320 ft.", "reach 5 ft. or range
        20/60 ft."."""
        parts = []
        if self.reach_ft is not None:
            parts.append(f"reach {self.reach_ft} ft.")
        if self.normal_ft is not None:
            parts.append(f"range {self.range_text}")
        return " or ".join(parts)


def stated_range(
    stated: tuple[int | None, int | None, int | None] | None, name: str = ""
) -> AttackRange | None:
    """The AttackRange of a structured attack's (reach_ft, range_ft,
    long_range_ft) fields (MonsterAbilities.stated_reach_and_range); None
    for an ability without them."""
    if stated is None:
        return None
    reach, normal, far = stated
    return AttackRange(reach_ft=reach, normal_ft=normal, long_ft=far, what=name)


def monster_action_range(action, name: str = "") -> AttackRange | None:
    """A stat block's attack's reach and range (a MonsterAction): its
    fields, for a MeleeAttack, RangedAttack or MeleeOrRangedAttack; else
    read from a freeform ability's text (action_range)."""
    found = stated_range(getattr(action, "stated_range", None), name)
    if found is not None:
        return found
    return action_range(action.description, name)


def action_range(description: str, name: str = "") -> AttackRange | None:
    """A freeform stat block attack's reach and range, from its text
    ("Melee Attack Roll: +6, reach 10 ft.", "Ranged Attack Roll: +4, range
    80/320 ft."); None when it says neither. A structured attack has them
    as fields (monster_action_range)."""
    reach = _REACH.search(description or "")
    ranged = _RANGE.search(description or "")
    if reach is None and ranged is None:
        return None
    return AttackRange(
        reach_ft=int(reach[1]) if reach else None,
        normal_ft=int(ranged[1]) if ranged else None,
        long_ft=int(ranged[2]) if ranged and ranged[2] else None,
        what=name,
    )


def _table_range(weapon) -> tuple[int, int] | None:
    for kind in type(weapon).__mro__:
        if kind.__name__ in WEAPON_RANGES_FT:
            return WEAPON_RANGES_FT[kind.__name__]
    return None


def weapon_range(weapon) -> AttackRange | None:
    """A player's weapon's reach and range: a melee weapon's reach (10 feet
    with Reach), a ranged one's range from the Weapons table
    (WEAPON_RANGES_FT), and both for a Thrown melee weapon. None for a
    ranged weapon whose range isn't known (a magic one of its own)."""
    properties = getattr(weapon, "properties", None) or ()
    name = getattr(weapon, "name", "")
    traits = getattr(weapon, "traits", None)
    ranged = bool(traits is not None and traits.is_ranged)
    table = _table_range(weapon)
    if ranged:
        if table is None:
            return None
        return AttackRange(normal_ft=table[0], long_ft=table[1], what=name)
    reach = REACH_WEAPON_FT if WeaponProperty.REACH in properties else MELEE_REACH_FT
    thrown = WeaponProperty.THROWN in properties and table is not None
    return AttackRange(
        reach_ft=reach,
        normal_ft=table[0] if thrown and table else None,
        long_ft=table[1] if thrown and table else None,
        what=name,
    )


def spell_attack_range(
    range_ft: int | None, text: str, name: str = ""
) -> AttackRange | None:
    """A spell's attack: a "ranged spell attack" reaches its range
    (`range_ft`, the spell's), a "melee spell attack" 5 feet; None for
    neither, or a ranged one with no range in feet (Self, Sight)."""
    if _RANGED_SPELL.search(text or ""):
        if range_ft is None:
            return None
        return AttackRange(normal_ft=range_ft, what=name)
    if _MELEE_SPELL.search(text or ""):
        return AttackRange(reach_ft=MELEE_REACH_FT, what=name)
    return None


@dataclass(frozen=True)
class RangeCheck:
    """What the map says of an attack's range: why it has Disadvantage
    (labels, each counted as one: "Long range, 90 ft. away"), what the GM
    should know (`notes`: an enemy close by that doesn't see the attacker)
    and what it can't do (`warnings`: past its reach or range); and whether
    each of the two sees the other (`sight`, for attack_plan)."""

    disadvantages: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    sight: Sight = NO_SIGHT

    @property
    def modifiers(self) -> list[tuple[str, D20Mode]]:
        """Its Disadvantages as (label, modifier) for attack_plan."""
        mode = D20Mode((D20Test.ATTACK_ROLL,), RollMode.DISADVANTAGE)
        return [(label, mode) for label in self.disadvantages]


NO_RANGE_CHECK = RangeCheck()


def _close_enemies(
    attacker: dict, chars: Iterable[dict], settings: ArenaSettings
) -> tuple[list[str], list[str]]:
    """The enemies within 5 feet of attacker that impose Disadvantage on its
    ranged attack, and a note for each that doesn't, as it can't see the
    attacker (senses.sees)."""
    chars = list(chars)
    counted, unseen = [], []
    for other in chars:
        if other is attacker or on_party_side(other) == on_party_side(attacker):
            continue
        hp = other.get("hp")
        if isinstance(hp, (int, float)) and hp <= 0:
            continue
        if has_condition(other, Condition.INCAPACITATED):
            continue
        feet = distance_ft(attacker, other, settings)
        if feet is None or feet > CLOSE_COMBAT_FT:
            continue
        seen = sees(other, attacker, chars, settings)
        if seen.can is False:
            unseen.append(
                f"Ranged attack within 5 ft. of {other['name']}: no Disadvantage,"
                f" it doesn't see the attacker ({seen.why})"
            )
        else:
            counted.append(other["name"])
    return counted, unseen


def attack_sight(
    attacker: dict | None,
    target: dict | None,
    chars: Iterable[dict],
    settings: ArenaSettings,
) -> Sight:
    """Whether attacker sees target and target sees attacker on the map
    (senses.sees); NO_SIGHT without either, or for the same one."""
    if attacker is None or target is None or attacker is target:
        return NO_SIGHT
    chars = list(chars)
    return Sight(
        sees(attacker, target, chars, settings), sees(target, attacker, chars, settings)
    )


def check_attack_range(
    attack: AttackRange | None,
    attacker: dict | None,
    target: dict | None,
    chars: Iterable[dict],
    settings: ArenaSettings,
) -> RangeCheck:
    """What attacker's `attack` against target has from the map (see the
    module), with the two's sight (attack_sight): no more without an attack,
    an attacker or a target, or with either off the map."""
    chars = list(chars)
    found = _range_check(attack, attacker, target, chars, settings)
    sight = attack_sight(attacker, target, chars, settings)
    return replace(found, sight=sight) if sight != NO_SIGHT else found


def _range_check(
    attack: AttackRange | None,
    attacker: dict | None,
    target: dict | None,
    chars: list[dict],
    settings: ArenaSettings,
) -> RangeCheck:
    """check_attack_range's reach and range."""
    if attack is None or attacker is None or target is None or attacker is target:
        return NO_RANGE_CHECK
    feet = distance_ft(attacker, target, settings)
    if feet is None:
        return NO_RANGE_CHECK
    name = target["name"]
    if attack.reach_ft is not None and feet <= attack.reach_ft:
        return NO_RANGE_CHECK  # a melee attack within its reach
    if attack.normal_ft is None:
        reach = attack.reach_ft or MELEE_REACH_FT
        return RangeCheck(
            warnings=(f"{name} is {feet} ft. away, past the {reach} ft. reach",)
        )
    disadvantages: list[str] = []
    warnings: list[str] = []
    farthest = attack.long_ft or attack.normal_ft
    if feet > farthest:
        warnings.append(
            f"{name} is {feet} ft. away, past its {attack.range_text} range"
        )
    elif feet > attack.normal_ft:
        disadvantages.append(f"Long range, {feet} ft. of {attack.range_text}")
    counted, unseen = _close_enemies(attacker, chars, settings)
    if counted:
        disadvantages.append(f"Ranged attack within 5 ft. of {', '.join(counted)}")
    return RangeCheck(tuple(disadvantages), tuple(unseen), tuple(warnings))


def spell_range_warning(
    range_ft: int | None,
    caster: dict | None,
    target: dict | None,
    settings: ArenaSettings,
) -> str:
    """ "Tiger is 70 ft. away, past the spell's 60 ft. range", for a spell
    aimed at a creature; "" within it, or when it can't be told."""
    if range_ft is None or caster is None or target is None or caster is target:
        return ""
    feet = distance_ft(caster, target, settings)
    if feet is None or feet <= range_ft:
        return ""
    return f"{target['name']} is {feet} ft. away, past the spell's {range_ft} ft. range"
