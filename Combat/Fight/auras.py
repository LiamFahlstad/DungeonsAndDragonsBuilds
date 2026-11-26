"""Auras and Pack Tactics, with no Qt (Notes/combat-effects-plan.md, step
9.4): always-on modifiers that depend on where creatures stand, which the
battle map's distances settle, and which are only noted for the GM where it
can't (a creature off the map, the map not in use: plan principle 8).

- An aura (Feature.aura: Aura of Protection) gives its owner's allies
  within its radius its modifiers, while its owner isn't Incapacitated or
  dead: "The aura is inactive while you have the Incapacitated condition."
  Of several auras of one feature, the best counts: "a creature can benefit
  from only one Aura of Protection at a time; the creature chooses which".
  They ride a copy of the creature a roll is made for (with_auras), as the
  map's cover does (Fight.covered), and modifiers_on reads them.
- Pack Tactics (a stat block's trait): "Advantage on an attack roll against
  a creature if at least one of the [creature]'s allies is within 5 feet of
  the creature and the ally doesn't have the Incapacitated condition."
"""

from collections.abc import Callable, Iterable
from dataclasses import replace

from Combat.Effects.always_on import features_of
from Combat.Effects.modifiers import AURAS_KEY, has_condition
from Combat.Effects.triggers import on_party_side
from Core.Definitions import Condition
from Model.Content.CombatModifiers import (
    D20Mode,
    D20Test,
    Modifier,
    RollMode,
)

from .health import DEAD, death_state

Distance = Callable[[dict, dict], int | None]

PACK_TACTICS = "Pack Tactics"
PACK_TACTICS_FT = 5


def _active(char: dict) -> bool:
    """Whether char can give what its aura or presence gives: alive and not
    Incapacitated."""
    return death_state(char) != DEAD and not has_condition(
        char, Condition.INCAPACITATED
    )


def _allies(a: dict, b: dict) -> bool:
    return on_party_side(a) == on_party_side(b)


def _value(modifier: Modifier) -> int:
    """How much a modifier gives, to keep the best of several auras."""
    amount = getattr(modifier, "amount", "0")
    return int(amount) if amount.lstrip("+-").isdigit() else 0


def aura_modifiers(
    char: dict, characters: Iterable[dict], distance: Distance
) -> list[tuple[str, Modifier]]:
    """What the auras of char's allies give it, by label ("Edmund's Aura of
    Protection"): counted within the aura's radius, a `when` for the GM
    where the distance isn't known; the best of one feature's auras."""
    best: dict[str, tuple[int, list[tuple[str, Modifier]]]] = {}
    for owner in characters:
        if not _allies(owner, char) or not _active(owner):
            continue
        sheet = owner.get("_stat_block")
        for feature in features_of(owner):
            hook = getattr(feature, "aura", None)
            aura = hook(sheet) if hook is not None else None
            if aura is None or (owner is char and not aura.owner_too):
                continue
            feet = 0 if owner is char else distance(owner, char)
            if feet is not None and feet > aura.radius_ft:
                continue
            label = f"{owner['name']}'s {feature.name}"
            when = (
                ""
                if feet is not None
                else f"it's within {aura.radius_ft} feet of {owner['name']}"
            )
            given = [(label, _with_when(modifier, when)) for modifier in aura.modifiers]
            # Counted beats only noted, then the bigger bonus.
            score = (feet is not None) * 1000 + sum(_value(m) for m in aura.modifiers)
            if feature.name not in best or score > best[feature.name][0]:
                best[feature.name] = (score, given)
    return [pair for _, given in best.values() for pair in given]


def _with_when(modifier: Modifier, when: str) -> Modifier:
    """`modifier` noted for the GM to judge (`when`), if there's one."""
    return replace(modifier, when=when) if when else modifier  # type: ignore[call-arg]


def with_auras(char: dict, auras: list[tuple[str, Modifier]]) -> dict:
    """Char as a roll for it reads it, with what auras give it: a copy to
    read, never to change (as with_cover is)."""
    if not auras:
        return char
    return {**char, AURAS_KEY: auras}


def has_pack_tactics(char: dict) -> bool:
    return any(
        str(
            t.get("name") if isinstance(t, dict) else getattr(t, "name", "")
        ).startswith(PACK_TACTICS)
        for t in char.get("traits") or ()
    )


def pack_tactics(
    attacker: dict | None,
    target: dict | None,
    characters: Iterable[dict],
    distance: Distance,
) -> list[tuple[str, Modifier]]:
    """Pack Tactics' Advantage on attacker's attack roll against target, by
    label: counted with an active ally of attacker within 5 feet of target,
    a `when` for the GM where an ally's distance isn't known, nothing with
    no such ally."""
    if attacker is None or target is None or not has_pack_tactics(attacker):
        return []
    unknown = False
    for ally in characters:
        if ally is attacker or ally is target:
            continue
        if not _allies(ally, attacker) or not _active(ally):
            continue
        feet = distance(ally, target)
        if feet is None:
            unknown = True
        elif feet <= PACK_TACTICS_FT:
            advantage = D20Mode((D20Test.ATTACK_ROLL,), RollMode.ADVANTAGE)
            label = f"{PACK_TACTICS} ({ally['name']} {feet} ft. from the target)"
            return [(label, advantage)]
    if not unknown:
        return []
    when = (
        f"an ally of it without the Incapacitated condition is within"
        f" {PACK_TACTICS_FT} feet of the target"
    )
    noted = D20Mode((D20Test.ATTACK_ROLL,), RollMode.ADVANTAGE, when=when)
    return [(PACK_TACTICS, noted)]
