"""How the encounter log reads on the player link (public_log.py): by round and
turn, with each line cut down. tests/test_combat_ui_player_server.py covers what
players may read at all; this covers how what they may read is put."""

import json

from Combat.CombatUIQt.public_log import public_log_rounds
from Combat.Definitions import Action

PIRATE = "Pirate"
BOSS = "Goblin Boss 2 (Goblin Boss)"
BROR = "Bror (Goblin Warrior)"
CHARS = [
    {"name": PIRATE},
    {"name": BOSS, "combatant_type": "Goblin Boss"},
    {"name": BROR, "combatant_type": "Goblin Warrior"},
]


def _event(owner: str, text: str, **fields) -> dict:
    return {"text": f"[{owner}'s turn] {text}", "public": True, **fields}


def _attack(owner: str, source: str, roll: str, verb: str, target: str) -> dict:
    return _event(owner, f"{source}'s attack roll of {roll} {verb} {target}")


def _damage(
    owner: str,
    target: str,
    amount: int,
    kind: str = "Slashing",
    source: str | None = None,
    outcome: str | None = None,
    knockout: bool = False,
) -> dict:
    text = f"{target} takes {amount} {kind} damage"
    text += f" from {source}" if source else ""
    text += f" ({outcome})" if outcome else ""
    return _event(
        owner,
        text,
        action=Action.DAMAGE,
        value={
            "dmg": amount,
            "damage_type": kind,
            "source_name": source,
            "target_name": target,
            "outcome": outcome,
            "knockout": knockout,
        },
    )


def _condition(owner: str, target: str, verb: str, name: str, source=None) -> dict:
    action = Action.ADD_CONDITION if verb == "gains" else Action.REMOVE_CONDITION
    return _event(
        owner,
        f"{target} {verb} {name}" + (f" from {source}" if source else ""),
        action=action,
        value={"condition": name, "source_name": source, "target_name": target},
    )


def _heal(owner: str, target: str, amount: int, source: str) -> dict:
    return _event(
        owner,
        f"{target} heals {amount} HP from {source}",
        action=Action.HEAL,
        value={"heal": amount, "source_name": source, "target_name": target},
    )


def _rounds(*events: dict) -> list[dict]:
    return public_log_rounds({"round_1": list(events)}, CHARS)


def _shown(*events: dict) -> list[tuple[str, str, str]]:
    """Every line as (kind, text, amount), whichever turn it's under."""
    return [
        (line["kind"], line["text"], line["amount"])
        for round_ in _rounds(*events)
        for turn in round_["turns"]
        for line in turn["lines"]
    ]


def test_an_event_read_back_from_the_log_file_reads_the_same():
    """The file holds an action as plain text, not as an Action."""
    events = [
        _attack("Pirate", PIRATE, "18", "hits", "Tiger"),
        _damage("Pirate", "Tiger", 3, source=PIRATE, knockout=True),
        _heal("Clover", "Pirate", 12, "Clover"),
        _condition("Clover", "Pirate", "gains", "Bless", "Clover"),
        _condition("Clover", "Pirate", "loses", "Bloodied", "Clover"),
        _event("Clover", "Pirate fails", action=Action.DEATH_SAVE_FAIL, value=False),
    ]
    assert _rounds(*json.loads(json.dumps(events))) == _rounds(*events)
    assert [kind for kind, _, _ in _shown(*json.loads(json.dumps(events)))] == [
        "hit",
        "down",
        "heal",
        "condition",
        "down",
    ]


def test_a_run_of_one_owners_lines_is_one_turn():
    (round_,) = _rounds(
        _event("Pirate", "One"), _event("Pirate", "Two"), _event("Tiger", "Three")
    )
    assert [turn["name"] for turn in round_["turns"]] == ["Pirate", "Tiger"]
    assert len(round_["turns"][0]["lines"]) == 2


def test_a_line_outside_any_turn_has_no_heading():
    (round_,) = _rounds({"text": "Rocks fall", "public": True})
    assert round_["turns"][0]["name"] is None


def test_a_private_event_is_left_out_of_the_turns_and_the_digest():
    private = dict(_damage("Pirate", "Tiger", 50, source=PIRATE), public=False)
    (round_,) = _rounds(private, _damage("Pirate", "Tiger", 3, source=PIRATE))
    assert round_["digest"] == "3 damage"
    assert len(round_["turns"][0]["lines"]) == 1


def test_a_round_of_only_lines_that_show_as_nothing_isnt_listed():
    assert _rounds(_condition("Pirate", "Tiger", "loses", "Bloodied")) == []


def test_damage_puts_its_amount_in_a_column_of_its_own():
    assert _shown(_damage("Pirate", "Tiger", 3, source=PIRATE)) == [
        ("damage", "Tiger takes", "3 Slashing")
    ]


def test_someone_elses_damage_says_whose_and_the_outcome_stays():
    assert _shown(_damage("Pirate", "Tiger", 3, source="Clover", outcome="saved")) == [
        ("damage", "Tiger takes from Clover (saved)", "3 Slashing")
    ]


def test_a_source_is_only_dropped_when_it_is_exactly_the_turns_owner():
    """A turn's owner can be the start of someone else's name."""
    assert _shown(_damage("Bror", "Tiger", 3, source=BROR)) == [
        ("damage", "Tiger takes from Bror (Goblin Warrior)", "3 Slashing")
    ]


def test_a_knockout_gets_a_line_of_its_own_and_counts_in_the_digest():
    event = _damage("Pirate", "Tiger", 3, source=PIRATE, knockout=True)
    assert _shown(event) == [
        ("damage", "Tiger takes", "3 Slashing"),
        ("down", "Tiger is down", ""),
    ]
    assert _rounds(event)[0]["digest"] == "3 damage · 1 down"


def test_a_heal_puts_its_amount_in_a_column_of_its_own():
    assert _shown(_heal("Clover", "Pirate", 12, "Clover")) == [
        ("heal", "Pirate heals", "+12 HP")
    ]


def test_regaining_consciousness_keeps_its_words():
    event = _event(
        "Clover",
        "Pirate regains consciousness with 5 HP from Clover",
        action=Action.HEAL,
        value={"heal": 5, "source_name": "Clover", "target_name": "Pirate"},
    )
    assert _shown(event) == [("heal", "Pirate regains consciousness", "+5 HP")]


def test_a_hit_and_its_damage_are_one_line():
    assert _shown(
        _attack("Pirate", PIRATE, "18", "hits", "Tiger"),
        _damage("Pirate", "Tiger", 3, source=PIRATE),
    ) == [("hit", "Hits Tiger (18)", "3 Slashing")]


def test_every_type_of_a_hits_damage_joins_it():
    assert _shown(
        _attack("Pirate", PIRATE, "18", "hits", "Tiger"),
        _damage("Pirate", "Tiger", 3, source=PIRATE),
        _damage("Pirate", "Tiger", 2, "Poison", source=PIRATE),
    ) == [("hit", "Hits Tiger (18)", "3 Slashing + 2 Poison")]


def test_a_hit_on_two_targets_keeps_each_ones_damage_apart():
    assert _shown(
        _attack("Pirate", PIRATE, "18", "hits", "Tiger"),
        _attack("Pirate", PIRATE, "18", "hits", "Bear"),
        _damage("Pirate", "Tiger", 3, source=PIRATE),
        _damage("Pirate", "Bear", 4, source=PIRATE),
    ) == [
        ("hit", "Hits Tiger (18)", "3 Slashing"),
        ("hit", "Hits Bear (18)", "4 Slashing"),
    ]


def test_damage_after_something_else_happened_isnt_the_hits():
    assert _shown(
        _attack("Pirate", PIRATE, "18", "hits", "Tiger"),
        _event("Pirate", "Pirate casts Magic Missile"),
        _damage("Pirate", "Tiger", 3, "Force", source=PIRATE),
    ) == [
        ("hit", "Hits Tiger (18)", ""),
        ("other", "Pirate casts Magic Missile", ""),
        ("damage", "Tiger takes", "3 Force"),
    ]


def test_a_hit_doesnt_take_damage_from_someone_else():
    assert _shown(
        _attack("Pirate", PIRATE, "18", "hits", "Tiger"),
        _damage("Pirate", "Tiger", 3, source="Clover"),
    ) == [
        ("hit", "Hits Tiger (18)", ""),
        ("damage", "Tiger takes from Clover", "3 Slashing"),
    ]


def test_a_knockout_from_a_hit_still_says_so():
    assert _shown(
        _attack("Pirate", PIRATE, "18", "hits", "Tiger"),
        _damage("Pirate", "Tiger", 3, source=PIRATE, knockout=True),
    ) == [("hit", "Hits Tiger (18)", "3 Slashing"), ("down", "Tiger is down", "")]


def test_a_miss_and_a_critical_hit_say_so():
    critical = _event(
        "Pirate", "Pirate's attack roll of natural 20 hits Tiger (critical hit)"
    )
    assert _shown(_attack("Pirate", PIRATE, "9", "misses", "Tiger"), critical) == [
        ("miss", "Misses Tiger (9)", ""),
        ("crit", "Crits Tiger (natural 20)", ""),
    ]


def test_an_attack_outside_its_makers_turn_says_whose():
    assert _shown(_attack("Tiger", PIRATE, "18", "hits", "Tiger")) == [
        ("hit", "Pirate hits Tiger (18)", "")
    ]


def test_an_attack_that_cant_be_checked_keeps_its_words():
    text = "Pirate's attack roll of 17 can't be checked against Tiger"
    assert _shown(_event("Pirate", text)) == [("other", text, "")]


def test_gaining_a_condition_loses_its_source_on_that_sources_turn():
    assert _shown(_condition("Clover", "Pirate", "gains", "Bless", "Clover")) == [
        ("condition", "Pirate gains Bless", "")
    ]


def test_losing_bloodied_is_no_line_but_gaining_it_is_a_quiet_one():
    assert _shown(
        _condition("Pirate", "Tiger", "gains", "Bloodied", PIRATE),
        _condition("Pirate", "Tiger", "loses", "Bloodied", PIRATE),
    ) == [("bloodied", "Tiger gains Bloodied", "")]


def test_bloodied_between_a_hit_and_more_of_its_damage_doesnt_split_them():
    assert _shown(
        _attack("Pirate", PIRATE, "18", "hits", "Tiger"),
        _damage("Pirate", "Tiger", 3, source=PIRATE),
        _condition("Pirate", "Tiger", "gains", "Bloodied", PIRATE),
        _damage("Pirate", "Tiger", 2, "Poison", source=PIRATE),
    ) == [
        ("hit", "Hits Tiger (18)", "3 Slashing + 2 Poison"),
        ("bloodied", "Tiger gains Bloodied", ""),
    ]


def test_a_monsters_type_goes_when_its_name_already_says_it():
    (round_,) = _rounds(_damage(BOSS, "Pirate", 3, source=BOSS))
    assert round_["turns"][0]["name"] == "Goblin Boss 2"


def test_a_monsters_type_stays_when_its_name_doesnt_say_it():
    (round_,) = _rounds(_event(BROR, "Bror (Goblin Warrior) growls"))
    assert round_["turns"][0]["name"] == BROR
    assert round_["turns"][0]["lines"][0]["text"] == "Bror (Goblin Warrior) growls"


def test_the_digest_adds_up_a_round():
    (round_,) = _rounds(
        _damage("Pirate", "Tiger", 3, source=PIRATE, knockout=True),
        _damage("Tiger", "Pirate", 4, source="Tiger"),
        _heal("Clover", "Pirate", 12, "Clover"),
    )
    assert round_["digest"] == "7 damage · 12 healed · 1 down"


def test_a_round_with_no_numbers_has_no_digest():
    assert _rounds(_event("Pirate", "Pirate ponders"))[0]["digest"] == ""
