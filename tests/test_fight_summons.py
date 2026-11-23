"""Players' summons in a fight without the combat window
(Combat/Fight/summons.py, Notes/combat-ui-refactor-plan.md step 5.3): whose
summon a combatant is, whether there's room for another, what Add
Combatant's "Already summoned..." offers, and the summons an earlier
encounter left out coming back in the next one (until a long rest, for one
that doesn't last until dismissed). Hanna's Drake Companion (one at a time:
another replaces it) and Dessie's Reanimated Companion (none beside it while
it's out), as the Time Loop PR campaign has them."""

import json
from functools import cache

from Combat.EncounterLogs import LogJSONEncoder
from Combat.Fight.fight import Fight
from Combat.Fight.summons import (
    already_summoned_options,
    carry_summons_over,
    owner_summons,
    room_for,
    same_summons,
    summon_owner,
    summon_source,
)
from Combat.PlayerCombatant import combatant_from_character
from Combat.PlayerLog import LONG_REST, log_ref
from Combat.Summons import CHOICE_KEY, create, feature_summons
from Model.Character import Character
from Model.Content.Summons import SummonContext
from tests._snapshot_helpers import build

DRAKE = "Hanna's Drake Companion"
REANIMATED = "Dessie's Reanimated Companion"


@cache
def _sheet(build_name: str) -> Character:
    return build(build_name)


def _player(build_name: str) -> dict:
    return combatant_from_character(_sheet(build_name))


def _party() -> Fight:
    return Fight(
        characters=[
            _player("Y2024_Artificer_Reanimator_Dessie"),
            _player("Y2024_Ranger_Drakewarden_Hanna"),
        ]
    )


def _member(fight: Fight, name: str) -> dict:
    return next(c for c in fight.characters if c["name"] == name)


def _summoned(fight: Fight, owner: str, feature_name: str, choice=None) -> dict:
    """owner's summon of feature_name, made and put in the fight."""
    player = _member(fight, owner)
    feature, spec = _spec(player, feature_name)
    taken = {c["name"] for c in fight.characters}
    (summon,) = create(
        player["_stat_block"], feature, spec, SummonContext(choice=choice), taken
    )
    fight.characters.append(summon)
    return summon


def _spec(player: dict, feature_name: str):
    return next(
        (f, s)
        for f, s in feature_summons(player["_stat_block"])
        if f.name == feature_name
    )


def test_a_summon_knows_its_owner_and_where_it_came_from():
    fight = _party()
    drake = _summoned(fight, "Hanna", "Drake Companion", "Cold")
    hanna = _member(fight, "Hanna")
    assert summon_owner(fight, drake) is hanna
    assert summon_owner(fight, hanna) is None
    assert owner_summons(fight, hanna) == [drake]
    found = summon_source(fight, drake)
    assert found is not None
    owner, sheet, feature, spec = found
    assert (owner, feature.name) == (hanna, "Drake Companion")
    assert same_summons(fight, hanna, feature, spec) == [drake]


def test_another_drake_replaces_the_one_out():
    fight = _party()
    hanna = _member(fight, "Hanna")
    feature, spec = _spec(hanna, "Drake Companion")
    assert room_for(fight, hanna, feature, spec, SummonContext()) == []
    drake = _summoned(fight, "Hanna", "Drake Companion", "Cold")
    assert room_for(fight, hanna, feature, spec, SummonContext()) == [drake]


def test_no_reanimated_companion_beside_the_one_out():
    fight = _party()
    dessie = _member(fight, "Dessie")
    feature, spec = _spec(dessie, "Reanimated Companion")
    _summoned(fight, "Dessie", "Reanimated Companion")
    assert room_for(fight, dessie, feature, spec, SummonContext()) is None


def test_already_summoned_offers_each_summon_with_each_choice():
    labels = [o.label for o in already_summoned_options(_party())]
    assert labels == [
        REANIMATED,
        f"{DRAKE} (Acid)",
        f"{DRAKE} (Cold)",
        f"{DRAKE} (Fire)",
        f"{DRAKE} (Lightning)",
        f"{DRAKE} (Poison)",
    ]


def _played(tmp_path, summons: list[dict], *, long_rest_after: bool) -> tuple:
    """A player log in tmp_path whose one played encounter left `summons`
    out (and a long rest after it, if asked); returns (its path, its data,
    the next encounter's log path)."""
    player_log = tmp_path / "PlayerLogs" / "main_party.json"
    logs = tmp_path / "CombatLogs"
    logs.mkdir()
    den = logs / "den.json"
    den.write_text(
        json.dumps({"combatants": summons}, cls=LogJSONEncoder), encoding="utf-8"
    )
    sessions: list[dict] = [{"log": log_ref(player_log, den)}]
    if long_rest_after:
        sessions.append({"type": LONG_REST})
    return player_log, {"sessions": sessions}, logs / "lair.json"


def test_the_summons_left_out_come_back_as_they_were_after_their_owners(tmp_path):
    earlier = _party()
    drake = _summoned(earlier, "Hanna", "Drake Companion", "Cold")
    drake["hp"] = 9
    reanimated = _summoned(earlier, "Dessie", "Reanimated Companion")
    player_log, data, lair = _played(
        tmp_path, [drake, reanimated], long_rest_after=False
    )
    fight = _party()
    carry_summons_over(fight, player_log, data, lair)
    assert [c["name"] for c in fight.characters] == [
        "Dessie",
        REANIMATED,
        "Hanna",
        DRAKE,
    ]
    carried = _member(fight, DRAKE)
    assert (carried["hp"], carried[CHOICE_KEY]) == (9, "Cold")
    assert carried["stats"]["damage_dealt"] == 0


def test_a_long_rest_ends_a_reanimated_companion_and_rests_a_drake(tmp_path):
    earlier = _party()
    drake = _summoned(earlier, "Hanna", "Drake Companion", "Cold")
    drake["hp"] = 9
    reanimated = _summoned(earlier, "Dessie", "Reanimated Companion")
    player_log, data, lair = _played(
        tmp_path, [drake, reanimated], long_rest_after=True
    )
    fight = _party()
    carry_summons_over(fight, player_log, data, lair)
    assert [c["name"] for c in fight.characters] == ["Dessie", "Hanna", DRAKE]
    carried = _member(fight, DRAKE)
    assert carried["hp"] == carried["max_hp"]
