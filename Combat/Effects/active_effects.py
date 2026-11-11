"""Lasting effects on a combatant: char["active_effects"], one plain dict per
effect (Notes/combat-effects-plan.md, Phase 3 and Decision 5), so undo and
log replay copy and save them like any other combatant state.

An effect is named like the badge it shows (a condition, "Bless", "Hexed",
a Wild Shape form), and says where it came from, how long it lasts, how it
ends and what its badge shows when hovered:

    {
        "name": "Frightened",
        "source": "Turn Undead",        # the spell, feature or action, if known
        "caster": "Brother Obmar",      # who gave it, if anyone
        "concentration": None,          # who concentrates on it, if anyone
        "duration": None,               # a timer or a turn edge (duration_entry)
        "repeat_save": None,            # a save at the end of each turn
        "tooltip": None,                # the badge's tooltip ...
        "tooltip_from": None,           # ... and what wrote it (TOOLTIP_FROM)
        "color": None,                  # the badge's colour
        "modifiers": [],                # what it does to rolls, AC and damage
        "linked": ["Charmed"],          # only on a spell's badge: see below
    }

`duration` is a timer, {"time_left": seconds, "duration": seconds,
"ticks_on": whose turn a round passes on}, or a turn edge, {"until": "start" |
"end", "of": whose turn, "turns_left": n, "text": what the card says}.
`repeat_save` is {"ability": "Wis", "dc": 13, "mode": "Normal",
"use_legendary_resistance": False, "also": [the other conditions it ends]}.
`modifiers` are the badge's, as its CombatCondition says them (Bless's
D20Bonus), each as Model/Content/CombatModifiers.modifier_to_dict writes it;
Combat/Effects/modifiers.py counts them while the badge is on.
`linked` is on a spell's own badge given beside the rules conditions it gave
("Friends" beside "Charmed"), so the card says which spell they're from: the
conditions it stands for. Taking the badge off takes them off, unless another
badge stands for them too, and taking the last of them off takes the badge
off (linked_badges_left_without, R125). A record without it links nothing.

A record lasts while it says something (a tooltip, a duration, a repeat save,
a concentration link or modifiers) and goes with its badge: ConditionsMixin
removes it with the condition. When a concentration ends, every effect linked
to it ends too (held_by_concentration), unless another running effect holds
its badge, which the link then names instead. Fight logs written before the record existed
kept the same things in seven keys of their own (OLD_KEYS); upgrade_old_keys
turns them into records, and is the only code that reads them. It also gives
a record from before `modifiers` existed none. Nothing here imports Qt."""

from collections.abc import Iterable
from typing import NotRequired, TypedDict

from Core.Rules import SECONDS_PER_ROUND
from Model.Content.CombatEffect import CombatEffect
from Model.Content.CombatModifiers import Modifier, modifier_to_dict

KEY = "active_effects"

# What wrote a badge's tooltip, lowest first. A tooltip is only replaced by
# one from the same or a higher kind: a spell's card stays over the notes
# typed for it, as it did when each kind had a map of its own.
CUSTOM = "custom"
FEATURE = "feature"
SPELL = "spell"
TOOLTIP_FROM = (CUSTOM, FEATURE, SPELL)

# The keys logs from before active_effects kept each part in.
_OLD_TIMERS = "timed_conditions"
_OLD_SAVES = "repeat_saves"
_OLD_TOOLTIPS = (
    ("spell_condition_descriptions", SPELL),
    ("feature_condition_descriptions", FEATURE),
    ("custom_condition_descriptions", CUSTOM),
)
_OLD_COLORS = ("spell_condition_colors", "feature_condition_colors")
OLD_KEYS = (
    _OLD_TIMERS,
    _OLD_SAVES,
    *(key for key, _ in _OLD_TOOLTIPS),
    *_OLD_COLORS,
)


class ActiveEffect(TypedDict):
    """One lasting effect on a combatant (see the module docstring)."""

    name: str
    source: str | None
    caster: str | None
    concentration: str | None
    duration: dict | None
    repeat_save: dict | None
    tooltip: str | None
    tooltip_from: str | None
    color: str | None
    modifiers: list[dict]
    linked: NotRequired[list[str]]


def new_effect(name: str) -> ActiveEffect:
    """An effect called `name` that says nothing yet."""
    return ActiveEffect(
        name=name,
        source=None,
        caster=None,
        concentration=None,
        duration=None,
        repeat_save=None,
        tooltip=None,
        tooltip_from=None,
        color=None,
        modifiers=[],
    )


def active_effects(char: dict) -> list[ActiveEffect]:
    """char's effects, in the order they were given (a timer given again
    goes last)."""
    return char.get(KEY) or []


def find_effect(char: dict, name: str) -> ActiveEffect | None:
    """char's effect called `name`, if it has one."""
    return next((e for e in active_effects(char) if e["name"] == name), None)


def effect_for(char: dict, name: str) -> ActiveEffect:
    """char's effect called `name`, made (last) if it has none."""
    effect = find_effect(char, name)
    if effect is None:
        effect = new_effect(name)
        char.setdefault(KEY, []).append(effect)
    return effect


def says_something(effect: ActiveEffect) -> bool:
    """Whether an effect still holds anything: a badge tooltip or colour, a
    duration, a repeat save, a concentration link, modifiers or linked
    conditions."""
    return bool(effect.get("modifiers") or effect.get("linked")) or any(
        effect[key] is not None
        for key in ("tooltip", "color", "duration", "repeat_save", "concentration")
    )


def badge_modifiers(
    effects: Iterable[CombatEffect] | None, badge: str
) -> tuple[Modifier, ...]:
    """What the badge `badge` does while it's on, as the first of `effects`
    (a spell's or feature's combat_effects(), None if it has none) that gives
    it says: Bless's D20Bonus."""
    for effect in effects or ():
        for condition in effect.conditions:
            if condition.name == badge:
                return condition.modifiers
    return ()


def give_modifiers(char: dict, name: str, modifiers: Iterable[Modifier]):
    """char's badge `name` gives `modifiers` while it's on. Giving none
    leaves those it has: a badge given again by hand keeps its spell's."""
    data = [modifier_to_dict(m) for m in modifiers]
    if data:
        effect_for(char, name)["modifiers"] = data


def remove_effect(char: dict, name: str):
    """char no longer has the effect called `name` (its badge came off)."""
    effects = [e for e in active_effects(char) if e["name"] != name]
    if effects:
        char[KEY] = effects
    else:
        char.pop(KEY, None)


def _prune(char: dict, name: str):
    """Drop the effect called `name` if nothing is left in it."""
    effect = find_effect(char, name)
    if effect is not None and not says_something(effect):
        remove_effect(char, name)


def describe(
    char: dict, name: str, tooltip: str, color: str | None, kind: str
) -> ActiveEffect:
    """Give the badge `name` on char `tooltip` (and `color`, if any), which
    `kind` (TOOLTIP_FROM) wrote. One from a lower kind than the tooltip it has
    is ignored; one from the same kind keeps the colour if it brings none."""
    effect = effect_for(char, name)
    rank = TOOLTIP_FROM.index(kind)
    had = effect["tooltip_from"]
    if had is not None and rank < TOOLTIP_FROM.index(had):
        return effect
    if had != kind or color is not None:
        effect["color"] = color
    effect["tooltip"] = tooltip
    effect["tooltip_from"] = kind
    return effect


def note_origin(
    char: dict, name: str, source: str | None = None, caster: str | None = None
):
    """Say what (`source`) and who (`caster`) gave char's effect `name`, if
    char has that effect. What isn't given is left as it was."""
    effect = find_effect(char, name)
    if effect is None:
        return
    if source:
        effect["source"] = source
    if caster:
        effect["caster"] = caster


def link_badge(char: dict, badge: str, conditions: Iterable[str]):
    """char's badge `badge` (a spell's name) stands for `conditions`, the
    rules conditions that spell gave it: one goes with the others."""
    linked = effect_for(char, badge).setdefault("linked", [])
    linked.extend(c for c in conditions if c not in linked and c != badge)


def linked_conditions(char: dict, badge: str) -> list[str]:
    """The conditions char's badge `badge` stands for (link_badge)."""
    effect = find_effect(char, badge)
    return list(effect.get("linked") or []) if effect is not None else []


def is_linked(char: dict, condition: str) -> bool:
    """Whether a badge on char stands for its `condition`."""
    return any(condition in (e.get("linked") or ()) for e in active_effects(char))


def linked_badges_left_without(char: dict, condition: str) -> list[str]:
    """char no longer has `condition`: no badge stands for it any more. The
    badges that stood for nothing else, which go with it."""
    emptied = []
    for effect in active_effects(char):
        linked = effect.get("linked")
        if linked and condition in linked:
            linked.remove(condition)
            if not linked:
                emptied.append(effect["name"])
    return emptied


def link_concentration(char: dict, name: str, concentrator: str):
    """char's effect `name` lasts while `concentrator` concentrates on it."""
    effect_for(char, name)["concentration"] = concentrator


def unlink_concentration(char: dict, name: str):
    """char's effect `name` no longer lasts only while someone concentrates
    (another effect that doesn't need Concentration holds its badge too)."""
    effect = find_effect(char, name)
    if effect is not None and effect["concentration"] is not None:
        effect["concentration"] = None
        _prune(char, name)


def held_by_concentration(
    chars: Iterable[dict], concentrator: str
) -> list[tuple[dict, ActiveEffect]]:
    """Every effect on `chars` that lasts while `concentrator` (a name)
    concentrates on it, with the combatant it's on."""
    return [
        (char, effect)
        for char in chars
        for effect in active_effects(char)
        if effect["concentration"] == concentrator
    ]


def duration_entry(
    duration: dict | None, source: str | None, target: str, turn: list[str]
) -> dict | None:
    """The `duration` an effect lasting `duration` (a Custom Condition
    duration: {"seconds": n}, or {"until": "start" | "end", "of": "source" |
    "target"}, or {"until": "end", "of": "current"}: the end of the turn
    being taken) on `target` (a name) has, given by `source` (a name, or None)
    during the turn of `turn` (names: [] outside combat). None when it lasts
    until removed, or until a turn of a source there isn't."""
    if duration is None:
        return None
    if "seconds" in duration:
        return {
            "time_left": duration["seconds"],
            "duration": duration["seconds"],
            "ticks_on": turn[0] if turn else None,
        }
    until = duration["until"]
    if duration["of"] == "current":
        # The end of the turn being taken now; outside combat there is none.
        if not turn:
            return None
        return {
            "until": "end",
            "of": turn[0],
            "turns_left": 1,
            "text": f"Until the end of {turn[0]}'s turn",
        }
    whose = source if duration["of"] == "source" else target
    if whose is None:
        return None
    # The end of `whose` next turn is the end of the one after this, if this
    # is their turn; the start of their next turn is always the first to come.
    taking_turn = whose in turn
    return {
        "until": until,
        "of": whose,
        "turns_left": 2 if until == "end" and taking_turn else 1,
        "text": f"Until the {until} of {whose}'s next turn",
    }


def set_duration(char: dict, name: str, duration: dict | None):
    """char's effect `name` lasts `duration` (duration_entry's), or until
    removed (None). A duration puts the effect last, as the card lists the
    timers in the order they were given."""
    if duration is None:
        effect = find_effect(char, name)
        if effect is not None:
            effect["duration"] = None
            _prune(char, name)
        return
    effect = effect_for(char, name)
    effect["duration"] = duration
    effects = active_effects(char)
    effects.remove(effect)
    effects.append(effect)


def timed_effects(char: dict) -> list[ActiveEffect]:
    """char's effects that end by themselves after a time or at a turn."""
    return [e for e in active_effects(char) if e["duration"] is not None]


def timers(char: dict) -> list[dict]:
    """What the card's Timed Conditions list shows: each timed effect's name
    with its duration's keys (a copy, to read)."""
    return [{"name": e["name"], **(e["duration"] or {})} for e in timed_effects(char)]


def tick(
    duration: dict,
    ended: set[str],
    started: set[str],
    new_round: bool,
    in_order: set[str],
) -> bool:
    """Count `duration` down as the turn passes from the combatants called
    `ended` to those called `started` (`new_round` when that begins a round;
    `in_order` are the names in the turn order). Returns whether it ran
    out."""
    if "time_left" in duration:
        # A round passes on the turn it was given in, or at the round's start
        # if that combatant has no turn (any more).
        ticks_on = duration.get("ticks_on")
        if ticks_on in started or (new_round and ticks_on not in in_order):
            duration["time_left"] = max(duration["time_left"] - SECONDS_PER_ROUND, 0)
        return duration["time_left"] == 0
    boundary = ended if duration["until"] == "end" else started
    if duration["of"] in boundary:
        duration["turns_left"] -= 1
    return duration["turns_left"] <= 0


def set_repeat_save(
    char: dict,
    name: str,
    ability: str,
    dc: int,
    mode: str,
    use_legendary_resistance: bool,
    also: list[str],
):
    """char repeats an `ability` save against `dc` at the end of each of its
    turns, ending `name` and the conditions `also` on a success."""
    effect_for(char, name)["repeat_save"] = {
        "ability": ability,
        "dc": dc,
        "mode": mode,
        "use_legendary_resistance": use_legendary_resistance,
        "also": list(also),
    }


def drop_repeat_save(char: dict, name: str):
    """char no longer has a repeat save to end `name`."""
    effect = find_effect(char, name)
    if effect is not None and effect["repeat_save"] is not None:
        effect["repeat_save"] = None
        _prune(char, name)


def repeat_saves(char: dict) -> list[ActiveEffect]:
    """char's effects that a save at the end of its turn can end."""
    return [e for e in active_effects(char) if e["repeat_save"] is not None]


def ending_conditions(char: dict) -> set[str]:
    """The conditions on char (a combatant dict, as a log of any age has it)
    that end on a timer, at a turn or on a save: fight state, which doesn't
    carry into the next fight."""
    effects = active_effects(upgrade_old_keys(dict(char)))
    ending = {e["name"] for e in effects if e["duration"] is not None}
    for effect in effects:
        if effect["repeat_save"] is not None:
            ending |= {effect["name"], *effect["repeat_save"].get("also", ())}
    return ending


def upgrade_old_keys(char: dict) -> dict:
    """`char` (a combatant dict, or a player's saved fight state) with the
    keys logs used before active_effects (OLD_KEYS) turned into its effects,
    in place. The effects read as the old keys did: the card's timers in the
    old timers' order, and each badge's tooltip and colour as the card
    picked them from the old maps (a spell's over a feature's over a custom
    note). A record from before `modifiers` existed (3.1's) gets none, on a
    copy of it."""
    if any("modifiers" not in e for e in char.get(KEY) or []):
        char[KEY] = [{**e, "modifiers": e.get("modifiers", [])} for e in char[KEY]]
    if not any(key in char for key in OLD_KEYS):
        return char
    if KEY in char:
        char[KEY] = [dict(e) for e in char[KEY]]
    # Read as leniently as the old readers did: an entry may lack a key.
    for entry in char.pop(_OLD_TIMERS, None) or []:
        if entry.get("name") is not None:
            duration = {k: v for k, v in entry.items() if k != "name"}
            effect_for(char, entry["name"])["duration"] = duration
    for entry in char.pop(_OLD_SAVES, None) or []:
        if entry.get("condition") is not None:
            effect_for(char, entry["condition"])["repeat_save"] = {
                "ability": entry.get("ability"),
                "dc": entry.get("dc"),
                "mode": entry.get("mode"),
                "use_legendary_resistance": entry.get(
                    "use_legendary_resistance", False
                ),
                "also": list(entry.get("also", [])),
            }
    tooltips = [(char.pop(key, None) or {}, kind) for key, kind in _OLD_TOOLTIPS]
    colors = [char.pop(key, None) or {} for key in _OLD_COLORS]
    names = dict.fromkeys(
        name for mapping in [m for m, _ in tooltips] + colors for name in mapping
    )
    for name in names:
        tooltip, kind = next(
            ((m[name], k) for m, k in tooltips if m.get(name)), (None, None)
        )
        color = next((m[name] for m in colors if m.get(name)), None)
        if tooltip is None and color is None:
            continue
        effect = effect_for(char, name)
        effect["tooltip"] = tooltip
        effect["tooltip_from"] = kind
        effect["color"] = color
    if not char.get(KEY):
        char.pop(KEY, None)
    return char
