"""How the encounter log reads on the player link: by round, then by whose turn
it was, each line cut down to what a player skims for. Only events
may_read_log_line marked public are read, so this can reword them and add up
what they say, but it can't show more of the fight than they do."""

import re

from Combat.Definitions import Action, CombatStatus
from Combat.EncounterLogs import PUBLIC_KEY, TURN_PREFIX
from Combat.PlayerLog import is_round_key

_ATTACK = re.compile(
    r"(?:(.+)'s attack roll|Attack roll) of (.+?) (hits|misses) (.+?)"
    r"( \(critical hit\))?"
)
# What the page colors a line by, for the ones it isn't worked out for below.
_KINDS: dict[str, str] = {
    Action.ADD_CONDITION: "condition",
    Action.REMOVE_CONDITION: "minor",
    Action.ADD_SPELL_SLOT: "minor",
    Action.REMOVE_SPELL_SLOT: "minor",
    Action.DEATH_SAVE_FAIL: "down",
    Action.DEATH_SAVE_SUCCESS: "heal",
    Action.REVIVE: "heal",
}
# The lines an attack's damage can still join: anything else came between them.
_ATTACK_KINDS = {"hit", "crit", "miss", "damage", "bloodied"}


def _line(kind: str, text: str, amount: str = "") -> dict:
    return {"kind": kind, "text": text, "amount": amount}


def _attack_line(attack: re.Match[str], owner: str | None) -> dict:
    source, roll, verb, target, critical = attack.groups()
    kind = "miss" if verb == "misses" else "crit" if critical else "hit"
    verb = "crits" if critical else verb
    doer = f"{source} {verb}" if source and source != owner else verb.capitalize()
    return _line(kind, f"{doer} {target} ({roll})")


def _event_lines(event: dict, text: str, owner: str | None) -> list[dict]:
    """What the event `text`, its turn already taken off, shows as. Most of it
    is in `value`, so there's no name to mistake for the words around it: Bror
    isn't "Bror (Goblin Warrior)". The turn's heading already says who `owner`
    is. Losing Bloodied is no line at all: it comes of being healed or dropped,
    which have their own, and it reads like good news either way."""
    action, value = event.get("action", ""), event.get("value") or {}
    if isinstance(value, dict) and owner and value.get("source_name") == owner:
        text = text.replace(f" from {owner}", "", 1)
    if action == Action.DAMAGE:
        amount = f"{value['dmg']} {value['damage_type']}"
        text = text.replace(f" {value['dmg']} {value['damage_type']} damage", "")
        lines = [_line("damage", text, amount)]
        if value.get("knockout"):
            lines.append(_line("down", f"{value['target_name']} is down"))
        return lines
    if action == Action.HEAL:
        amount = f"+{value['heal']} HP"
        return [
            _line("heal", re.sub(rf"(?: with)? {value['heal']} HP", "", text), amount)
        ]
    if (
        isinstance(value, dict)
        and value.get("condition") == CombatStatus.BLOODIED.value
    ):
        if action == Action.REMOVE_CONDITION:
            return []
        if action == Action.ADD_CONDITION:
            return [_line("bloodied", text)]
    return [_line(_KINDS.get(action, "other"), text)]


def _add_damage(hit: dict, line: dict):
    hit["amount"] = (
        f"{hit['amount']} + {line['amount']}" if hit["amount"] else line["amount"]
    )


def _turn_lines(events: list[tuple[dict, str]], owner: str | None) -> list[dict]:
    """A turn's lines, in the order they happened. An attack's damage joins the
    line of the hit that dealt it, however many damage types it has, even if the
    GM rolled for several targets before entering the damage of any of them."""
    lines: list[dict] = []
    hits: dict[tuple[str | None, str], dict] = {}
    for event, text in events:
        attack = _ATTACK.fullmatch(text)
        if attack:
            line = _attack_line(attack, owner)
            lines.append(line)
            if line["kind"] != "miss":
                hits[attack[1], attack[4]] = line
            continue
        read = _event_lines(event, text, owner)
        hit = None
        if event.get("action") == Action.DAMAGE:
            value = event["value"]
            hit = hits.get((value["source_name"], value["target_name"]))
        if hit is not None:
            _add_damage(hit, read[0])
            read = read[1:]
        lines += read
        if any(line["kind"] not in _ATTACK_KINDS for line in read):
            hits.clear()
    return lines


def _digest(events: list[dict]) -> str:
    """A round at a glance, for when it's folded away: "54 damage · 15 healed · 2 down"."""
    damage = [e["value"] for e in events if e.get("action") == Action.DAMAGE]
    healed = sum(e["value"]["heal"] for e in events if e.get("action") == Action.HEAL)
    parts = [
        (sum(value["dmg"] for value in damage), "damage"),
        (healed, "healed"),
        (sum(1 for value in damage if value.get("knockout")), "down"),
    ]
    return " · ".join(f"{count} {word}" for count, word in parts if count)


def _short_names(chars: list[dict]) -> dict[str, str]:
    """The long names to shorten: a monster's type repeats its own name in
    "Goblin Boss 2 (Goblin Boss)", but "Katt (Goblin Boss)" needs it."""
    names = {}
    for char in chars:
        kind = char.get("combatant_type") or ""
        short = char["name"].removesuffix(f" ({kind})")
        if kind and short != char["name"] and kind.split()[0] in short.split():
            names[char["name"]] = short
    return names


def _shortened(text: str, names: dict[str, str]) -> str:
    for name, short in names.items():
        text = text.replace(name, short)
    return text


def _round_turns(events: list[dict], names: dict[str, str]) -> list[dict]:
    """The round's turns in order, a run of events with one owner making one."""
    runs: list[tuple[str | None, list[tuple[dict, str]]]] = []
    for event in events:
        found = TURN_PREFIX.fullmatch(event["text"])
        owner, text = found.groups() if found else (None, event["text"])
        if not runs or runs[-1][0] != owner:
            runs.append((owner, []))
        runs[-1][1].append((event, text))
    turns = []
    for owner, run in runs:
        lines = _turn_lines(run, owner)
        for line in lines:
            line["text"] = _shortened(line["text"], names)
        if lines:
            name = _shortened(owner, names) if owner else None
            turns.append({"name": name, "lines": lines})
    return turns


def public_log_rounds(data: dict, chars: list[dict]) -> list[dict]:
    """What players may read of the encounter log `data`, oldest round first. An
    event without PUBLIC_KEY stays private, plain text from an old log too. A
    round's own "--- Round 2 ---" line is its heading on the page. `chars` is
    only for their names."""
    names = _short_names(chars)
    log = []
    for number in sorted(int(k.split("_", 1)[1]) for k in filter(is_round_key, data)):
        events = [
            event
            for event in data[f"round_{number}"]
            if isinstance(event, dict)
            and event.get(PUBLIC_KEY)
            and event["text"] != f"--- Round {number} ---"
        ]
        turns = _round_turns(events, names)
        if turns:
            log.append({"round": number, "digest": _digest(events), "turns": turns})
    return log
