"""Players' summons in a fight, Qt-free (Notes/combat-ui-refactor-plan.md,
step 5.3, summons): whose summon a combatant is, which of a player's summons
a feature made, whether there's room for another, the summons a player could
have out before the fight, and the ones the last encounter left out that come
back in this one. The summons themselves (made, numbered, placed after their
owners, carried over) are Combat/Summons.py; the combat window logs what
happens to them and builds their menus (SummonsMixin)."""

from pathlib import Path

import Combat.PlayerLog as PlayerLog
from Combat.LogFiles import read_json
from Combat.Summons import (
    CHOICE_KEY,
    SummonOption,
    carried_state,
    create,
    feature_summons,
    is_out,
    keep_card,
    last_seen,
    make_room,
    mark,
    numbered,
    old_name,
    owner_name,
    place_after_owners,
    source_for,
    summon_name,
)
from Model.Character import Character
from Model.Content.Feature import Feature
from Model.Content.Summons import SummonContext, SummonLifetime, SummonSpec

from .fight import Fight
from .stats import _default_stats


def summon_owner(fight: Fight, char: dict) -> dict | None:
    """The player in the fight whose summon char is, if any."""
    name = owner_name(char)
    if name is None:
        return None
    return next(
        (c for c in fight.characters if c.get("_is_player") and c["name"] == name),
        None,
    )


def owner_summons(fight: Fight, owner: dict) -> list[dict]:
    return [c for c in fight.characters if owner_name(c) == owner["name"]]


def summon_source(
    fight: Fight, summon: dict
) -> tuple[dict, Character, Feature, SummonSpec] | None:
    """(owner, the owner's character, the feature that summons it, its
    SummonSpec)."""
    owner = summon_owner(fight, summon)
    sheet = owner.get("_stat_block") if owner is not None else None
    if owner is None or not isinstance(sheet, Character):
        return None
    found = source_for(sheet, summon)
    return None if found is None else (owner, sheet, *found)


def same_summons(
    fight: Fight, owner: dict, feature: Feature, spec: SummonSpec
) -> list[dict]:
    """owner's summons in the fight made by feature's spec, in the fight's
    order (oldest first)."""
    sheet = owner["_stat_block"]
    same = []
    for char in owner_summons(fight, owner):
        found = source_for(sheet, char)
        if found is not None and (found[0].name, found[1].name) == (
            feature.name,
            spec.name,
        ):
            same.append(char)
    return same


def room_for(
    fight: Fight, owner: dict, feature: Feature, spec: SummonSpec, ctx: SummonContext
) -> list[dict] | None:
    """Who summoning spec again now replaces ([]: nobody), or None when
    it can't be summoned while the ones out are (make_room)."""
    out = [c for c in same_summons(fight, owner, feature, spec) if is_out(c)]
    return make_room(out, spec, spec.count(owner["_stat_block"], ctx))


def already_summoned_options(fight: Fight) -> list[SummonOption]:
    """Add Combatant's "Already summoned...": each summon (with each of
    its choices) of each player in the fight."""
    options = []
    for player in fight.characters:
        sheet = player.get("_stat_block")
        if not player.get("_is_player") or not isinstance(sheet, Character):
            continue
        for feature, spec in feature_summons(sheet):
            for choice in spec.choices(sheet) or [None]:
                label = summon_name(player["name"], spec)
                if choice is not None:
                    label += f" ({choice})"
                options.append(SummonOption(label, player, feature, spec, choice))
    return options


def carry_summons_over(
    fight: Fight, player_log_file: Path, player_log_data: dict, log_path: Path
):
    """Start the fight of the encounter log at `log_path` (one not started
    yet) with the party's summons the last encounter left out, as it left
    them: their card (as it was built), Hit Points, conditions and choice.
    One dismissed or replaced since (Action.DISMISS) stays gone (last_seen).
    A long rest since ends a Reanimated Companion and rests a drake (its
    SummonSpec's lifetime). The played logs are the player log's sessions
    (player_log_data, the file at player_log_file)."""
    ref = PlayerLog.log_ref(player_log_file, log_path)
    # Each encounter log played, with whether a long rest came after it.
    played: list[tuple[dict, bool]] = []
    for session in player_log_data["sessions"]:
        if session.get("type") == PlayerLog.LONG_REST:
            played = [(data, True) for data, _ in played]
            continue
        if not session.get("log") or session["log"] == ref:
            continue
        path = PlayerLog.resolve_log(player_log_file, session["log"])
        if path.exists():
            played.append((read_json(path), False))
    taken = {c["name"] for c in fight.characters}
    new: list[dict] = []
    for owner in [c for c in fight.characters if c.get("_is_player")]:
        sheet = owner.get("_stat_block")
        if not isinstance(sheet, Character):
            continue
        for feature, spec in feature_summons(sheet):
            # Only one that lasts until dismissed outlasts a long rest.
            ends_on_long_rest = spec.lifetime is not SummonLifetime.UNTIL_DISMISSED
            logs = [(d, r) for d, r in played if not (r and ends_on_long_rest)]
            for name, aliases in _earlier_names(owner, sheet, feature, spec, logs):
                seen = last_seen(name, logs, aliases)
                if seen is None:
                    continue
                state = carried_state(*seen)
                if state["hidden_from_players"]:
                    continue  # not out: summoned again when it's wanted
                names = {name, *aliases}
                # An older log's hidden one, prepared with the encounter.
                here = next((c for c in fight.characters if c["name"] in names), None)
                if here is None:
                    ctx = SummonContext(choice=state.get(CHOICE_KEY))
                    here = create(sheet, feature, spec, ctx, taken)[0]
                    here["name"] = numbered(name, taken)
                    new.append(here)
                else:
                    mark(here, sheet, feature, spec)
                keep_card(here, seen[0])
                taken.add(here["name"])
                here.update(state)
                del here["hidden_from_players"]
    # Before the fight: there's no turn order yet.
    for char in new:
        char["stats"] = _default_stats()
    fight.characters[:] = place_after_owners(fight.characters, new)


def _earlier_names(
    owner: dict,
    sheet: Character,
    feature: Feature,
    spec: SummonSpec,
    logs: list[tuple[dict, bool]],
) -> list[tuple[str, tuple[str, ...]]]:
    """The names owner's summons of spec had in the encounter logs `logs`,
    as today's names, each with the names older logs gave it (the first's
    "<owner>'s Companion (<type>)")."""
    base = summon_name(owner["name"], spec)
    combatant_type = spec.build(sheet, SummonContext()).combatant_type
    legacy = old_name(owner["name"], combatant_type)
    names: list[str] = []
    for data, _ in logs:
        for char in data.get("combatants", []):
            if owner_name(char) != owner["name"]:
                continue
            found = source_for(sheet, char)
            if found is None or (found[0].name, found[1].name) != (
                feature.name,
                spec.name,
            ):
                continue
            name = base if char["name"] == legacy else char["name"]
            if name not in names:
                names.append(name)
    return [(name, (legacy,) if name == base else ()) for name in names]
