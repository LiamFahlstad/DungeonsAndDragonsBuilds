"""When a row of a source's combat effects is used (Notes/combat-effects-plan.md,
Phase 6): a hit, a miss, damage taken, dropping to 0 Hit Points, ... A row says
what, its trigger says when (principle 12). The combat simulator applies a
triggered row itself only when the rules say it happens and it can check every
gate; otherwise it asks the GM as it happens (Combat/Effects/triggers.py).

    CombatEffect(
        name="Hill's Tumble",
        conditions=(CombatCondition(Condition.PRONE),),
        trigger=CombatTrigger(
            TriggerEvent.HIT, needs_damage=True, largest_target=CreatureSize.LARGE
        ),
    )

As JSON (CombatEffect.to_dict), the fields not at their default, enums as
their values: {"event": "hit", "needs_damage": true, "largest_target": "Large"}.

A badge's turn triggers (AtTurnStart, AtTurnEnd) are modifiers instead
(CombatModifiers.py), and stay so (Q46)."""

from dataclasses import dataclass, fields
from enum import Enum, StrEnum
from typing import Any

from Core.Definitions import CreatureSize
from Model.Content.CombatModifiers import AttackKind


class TriggerEvent(StrEnum):
    """What happens in the fight that a row comes with. The simulator fires
    HIT and MISS (in every hit path: the Custom Effect dialog, the main
    window's attack roll and Damage fields, a monster's action button), and
    on the creature hit or damaged HIT_BY (as the hit lands, before its
    damage: Shield, Deflect Attacks) and TAKES_DAMAGE (after damage from a
    creature: Hellish Rebuke, Storm's Thunder); as damage lands, DROPS_TO_ZERO
    on the creature it would drop to 0 Hit Points (before it does: Relentless
    Endurance), REDUCES_TO_ZERO on the creature that dealt it (Dark One's
    Blessing), and BLOODIED on one it leaves Bloodied (Harvest Undead). As
    a fight starts, ROLLS_INITIATIVE on everyone in it (Uncanny Metabolism).
    USES after a row of the same source is picked and applied in the Custom
    Effect dialog, on each of its targets (Ice Knife's explosion after its
    shard). FAILS_SAVE as a save the dialog rolls fails (Indomitable). The
    others are data until a step needs them."""

    HIT = "hit"  # the owner hits
    MISS = "miss"  # the owner misses
    HIT_BY = "hit by"  # the owner is hit, before the damage
    TAKES_DAMAGE = "takes damage"  # the owner takes damage, after it
    BLOODIED = "bloodied"
    DROPS_TO_ZERO = "drops to 0"
    REDUCES_TO_ZERO = "reduces to 0"  # the owner reduces a creature to 0 HP
    FAILS_SAVE = "fails a save"
    ROLLS_INITIATIVE = "rolls initiative"
    CASTS_SPELL = "casts a spell"
    USES = "uses"  # the owner uses another row of the same source (`after`)


# The events made by an attack roll, which know its kind and whether it was
# a Critical Hit.
ATTACK_EVENTS = (TriggerEvent.HIT, TriggerEvent.MISS, TriggerEvent.HIT_BY)
# The events with another creature in them: the one hit, the attacker, the
# creature that dealt the damage, the one reduced to 0, the target of the row
# it comes after.
TARGET_EVENTS = (
    *ATTACK_EVENTS,
    TriggerEvent.TAKES_DAMAGE,
    TriggerEvent.REDUCES_TO_ZERO,
    TriggerEvent.USES,
)
# The events that can come after one row of the source in particular.
AFTER_EVENTS = (TriggerEvent.HIT, TriggerEvent.MISS, TriggerEvent.USES)
# Sizes, smallest first, to compare "a Large or smaller creature".
SIZES = tuple(CreatureSize)


class TriggerAim(StrEnum):
    """Who a triggered row goes on. TARGET: the other creature of what
    happened (the one hit). ANOTHER: one other creature near it, which the GM
    picks (Green-Flame Blade's fire "leaps from the target to a different
    creature"). ALSO_OTHERS: it and the creatures near it the GM adds (Ice
    Knife's explosion: "the target and each creature within 5 feet of it")."""

    TARGET = "target"
    ANOTHER = "another"
    ALSO_OTHERS = "also others"


@dataclass(frozen=True)
class CombatTrigger:
    """When a row is used. `optional`: the rules say "you can" (the GM is
    asked); False is "it happens". `after`: only after this other row of the
    same source hits ("Tree Club"). The gates the simulator checks: the
    attack's kind (`attacks`), the target's size (`largest_target`, "a Large
    or smaller creature"), damage dealt after Resistance and Immunity
    (`needs_damage`, "and deal damage to it"), a Critical Hit, once per turn,
    the owner's Reaction (`reaction`, or a row whose action is a Reaction:
    not offered once it's used, and spent as the row is), the other creature
    being an enemy of the owner (`enemy_only`: Dark One's Blessing's "you
    reduce an enemy to 0 Hit Points"). What only the GM can judge is a
    `when`, said as what follows "if": it always asks. `aim`: who it goes on
    (TriggerAim); any but TARGET asks, for the GM to pick."""

    event: TriggerEvent
    optional: bool = True
    after: str = ""
    attacks: AttackKind = AttackKind.ANY
    largest_target: CreatureSize | None = None
    needs_damage: bool = False
    critical_only: bool = False
    once_per_turn: bool = False
    reaction: bool = False
    enemy_only: bool = False
    when: str = ""
    aim: TriggerAim = TriggerAim.TARGET

    def __post_init__(self):
        # Text ("hit", "Large") is taken too, as JSON and logs have it.
        if self.event not in set(TriggerEvent):
            raise ValueError(
                f"event {self.event!r} is not one of {[e.value for e in TriggerEvent]}"
            )
        object.__setattr__(self, "event", TriggerEvent(self.event))
        if self.largest_target is not None:
            if self.largest_target not in set(CreatureSize):
                raise ValueError(
                    f"largest_target {self.largest_target!r} is not one of"
                    f" {[s.value for s in CreatureSize]}"
                )
            object.__setattr__(
                self, "largest_target", CreatureSize(self.largest_target)
            )
        if self.aim not in set(TriggerAim):
            raise ValueError(
                f"aim {self.aim!r} is not one of {[a.value for a in TriggerAim]}"
            )
        object.__setattr__(self, "aim", TriggerAim(self.aim))
        if self.aim is not TriggerAim.TARGET and self.event not in TARGET_EVENTS:
            raise ValueError(
                f"aim needs an event with another creature in it, not"
                f" {TriggerEvent(self.event).value!r}"
            )
        if not isinstance(self.attacks, AttackKind):
            raise ValueError(f"attacks is an AttackKind, got {self.attacks!r}")
        for name in (
            "optional",
            "needs_damage",
            "critical_only",
            "once_per_turn",
            "reaction",
            "enemy_only",
        ):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(
                    f"{name} is True or False, got {getattr(self, name)!r}"
                )
        if not isinstance(self.after, str) or not isinstance(self.when, str):
            raise ValueError("after and when are text")
        if self.after != self.after.strip() or self.when != self.when.strip():
            raise ValueError("after and when have no spaces around them")
        event = self.event
        if self.after and event not in AFTER_EVENTS:
            raise ValueError(
                f"after is for {[e.value for e in AFTER_EVENTS]} only, not {event.value!r}"
            )
        if event is TriggerEvent.USES and not self.after:
            raise ValueError("A 'uses' trigger names the row it comes after (after=)")
        if self.attacks is not AttackKind.ANY and event not in ATTACK_EVENTS:
            raise ValueError(f"attacks is for an attack's events, not {event.value!r}")
        if self.largest_target is not None and event not in TARGET_EVENTS:
            raise ValueError(
                f"largest_target needs an event with another creature in it,"
                f" not {event.value!r}"
            )
        if self.enemy_only and event not in TARGET_EVENTS:
            raise ValueError(
                f"enemy_only needs an event with another creature in it,"
                f" not {event.value!r}"
            )
        if self.needs_damage and event is not TriggerEvent.HIT:
            raise ValueError("needs_damage is for a 'hit' only")
        if self.critical_only and event not in (TriggerEvent.HIT, TriggerEvent.HIT_BY):
            raise ValueError("critical_only is for 'hit' and 'hit by' only")

    def to_dict(self) -> dict:
        """The trigger as plain data: the fields not at their default, enums
        as their values."""
        data: dict[str, Any] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value == field.default and field.name != "event":
                continue
            data[field.name] = value.value if isinstance(value, Enum) else value
        return data


TRIGGER_KEYS = tuple(field.name for field in fields(CombatTrigger))


def size_fits(size: str | None, largest: CreatureSize) -> bool | None:
    """Whether a creature of `size` (its card's "size", "Large") is `largest`
    or smaller; None when its size isn't known."""
    try:
        known = CreatureSize(size) if size else None
    except ValueError:
        known = None
    if known is None:
        return None
    return SIZES.index(known) <= SIZES.index(largest)


def trigger_problems(source: str, effects) -> list[str]:
    """What's wrong with the triggers of one source's combat effects (a
    spell's, a feature's, a monster ability's) that no row alone can tell: an
    `after` that names no other row of the source. A row's name is its own,
    or the source's when it has none."""
    names = [effect.name or source for effect in effects]
    problems = []
    for index, effect in enumerate(effects):
        trigger = getattr(effect, "trigger", None)
        if trigger is None or not trigger.after:
            continue
        others = [name for i, name in enumerate(names) if i != index]
        if trigger.after not in others:
            problems.append(
                f"{source!r}[{index}]: its trigger comes after {trigger.after!r},"
                f" which is no other row of {source!r} ({others or 'none'})"
            )
    return problems
