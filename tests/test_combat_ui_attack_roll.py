"""The Attack roll field: a roll the GM types in is checked against the target's
AC and logged, and the Limited player view shows what the players learned from
it. Expected results come from the rules: an attack hits when the roll is at
least the AC, a natural 20 always hits and a natural 1 always misses."""

import pytest
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox

from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.attack_rolls import AttackRoll, parse_attack_roll
from Combat.CombatUIQt.monster_actions import MonsterAction
from Combat.EncounterLogs import prepare_log, scenario_log_path
from Combat.PlayerLog import is_round_key
from Combat.Scenario import CombatScenario
from Core.Definitions import DamageType
from tests._combat_ui import make_ui, qapp

TIGER_AC = 13
TIGER = CombatScenario(
    name="tiger_den",
    title="Tiger Den",
    combatants=lambda: [Tiger()],
    monster_summary=["Tiger"],
)


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


def _start(ui, *initiatives: int):
    for char, value in zip(ui.characters, initiatives):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()


def _bandit():
    bandit = Pirate()
    bandit.set_name("Bandit")
    return bandit


@pytest.fixture
def fight(tmp_path):
    """A Pirate attacking a 30 HP, AC 13 Tiger, on the Limited view, with a
    Bandit on hand."""
    ui = make_ui(tmp_path, [Pirate(), Tiger(), _bandit()])
    _start(ui, 15, 10, 5)
    ui.settings.limited_player_view = True
    pirate, tiger, bandit = ui.characters
    tiger["ac"] = TIGER_AC
    ui._select_character(pirate)
    ui._set_targets([tiger])
    ui.damage_type_combo.setCurrentIndex(
        ui.damage_type_combo.findData(DamageType.SLASHING.value)
    )
    return ui, pirate, tiger, bandit


def _roll(ui, text: str):
    ui.attack_roll_input.setText(text)
    ui.attack_roll_input.returnPressed.emit()


def _lines(ui) -> list[str]:
    data = ui._read_log()
    return [
        event["text"]
        for key in filter(is_round_key, data)
        for event in data[key]
        if "attack roll" in event["text"].lower()
    ]


def _details(ui, name: str) -> str:
    _, rows = ui._player_view_content()
    (row,) = [r for r in rows if r.name == name]
    return row.details.replace("\N{NO-BREAK SPACE}", " ")


def _ac_note(ui, name: str = "Tiger") -> str:
    """The row's details without its damage taken, which always comes first."""
    return " · ".join(_details(ui, name).split(" · ")[1:])


# ---------------------------------------------------------------------------
# Reading the field


@pytest.mark.parametrize(
    "text, expected",
    [
        ("17", AttackRoll(total=17)),
        (" 17 ", AttackRoll(total=17)),
        ("12+5", AttackRoll(total=17)),
        ("nat 20", AttackRoll(natural=20)),
        ("NAT20", AttackRoll(natural=20)),
        ("natural 1", AttackRoll(natural=1)),
        ("nat 2", None),
        ("", None),
        ("hit", None),
        ("17 fire", None),
        ("1d20", None),
    ],
)
def test_parse_attack_roll(text, expected):
    assert parse_attack_roll(text) == expected


# ---------------------------------------------------------------------------
# Hit or miss


@pytest.mark.parametrize(
    "roll, verb",
    [(TIGER_AC - 1, "misses"), (TIGER_AC, "hits"), (TIGER_AC + 1, "hits")],
)
def test_an_attack_hits_when_it_reaches_the_ac(fight, roll, verb):
    ui, *_ = fight
    _roll(ui, str(roll))
    assert _lines(ui) == [
        f"[Pirate's turn] Pirate's attack roll of {roll} {verb} Tiger"
    ]
    assert ui.attack_roll_input.text() == ""
    assert f"{roll} vs AC {TIGER_AC}" in ui._status_label.text()


def test_a_natural_20_hits_any_ac_and_is_a_critical_hit(fight):
    ui, _, tiger, _ = fight
    tiger["ac"] = 40
    _roll(ui, "nat 20")
    assert _lines(ui) == [
        "[Pirate's turn] Pirate's attack roll of natural 20 hits Tiger (critical hit)"
    ]


def test_a_natural_1_misses_any_ac(fight):
    ui, _, tiger, _ = fight
    tiger["ac"] = 1
    _roll(ui, "nat 1")
    assert _lines(ui) == [
        "[Pirate's turn] Pirate's attack roll of natural 1 misses Tiger"
    ]


def test_a_players_ac_is_the_number_they_have_now(fight):
    ui, pirate, tiger, _ = fight
    tiger["ac"] = "18 (with Shield) and 16 (without Shield)"
    _roll(ui, "17")
    assert _lines(ui) == ["[Pirate's turn] Pirate's attack roll of 17 misses Tiger"]


def test_a_target_with_no_ac_cant_be_checked(fight):
    ui, _, tiger, _ = fight
    tiger["ac"] = None
    _roll(ui, "17")
    assert _lines(ui) == [
        "[Pirate's turn] Pirate's attack roll of 17 can't be checked against Tiger"
    ]
    assert ui._status_label.text() == "Tiger has no AC to check"
    assert _ac_note(ui) == ""


def test_a_hit_goes_on_to_the_damage_field_and_a_miss_stays(fight, monkeypatch):
    ui, *_ = fight
    focused = []
    monkeypatch.setattr(ui, "_focus_damage_input", lambda: focused.append(True))
    _roll(ui, str(TIGER_AC - 1))
    assert not focused
    _roll(ui, str(TIGER_AC))
    assert focused


@pytest.mark.parametrize(
    "text, reason",
    [
        ("", "no attack roll"),
        ("  ", "no attack roll"),
        ("banana", "'banana' isn't an attack roll"),
    ],
)
def test_a_roll_it_cant_read_changes_nothing_and_says_why(fight, text, reason):
    ui, *_ = fight
    _roll(ui, text)
    assert reason in ui._status_label.text()
    assert _lines(ui) == []
    assert ui.attack_roll_input.text() == text
    assert not ui.history


def test_a_roll_with_no_target_says_so(fight):
    ui, *_ = fight
    ui._set_targets([])
    _roll(ui, "17")
    assert "pick a target" in ui._status_label.text()
    assert ui.attack_roll_input.text() == "17"


def test_each_target_gets_its_own_check(fight):
    ui, _, tiger, bandit = fight
    bandit["ac"] = 19
    ui._set_targets([tiger, bandit])
    _roll(ui, "15")
    assert _lines(ui) == [
        "[Pirate's turn] Pirate's attack roll of 15 hits Tiger",
        "[Pirate's turn] Pirate's attack roll of 15 misses Bandit (Pirate)",
    ]
    assert _ac_note(ui, "Tiger") == "AC ≤ 15"
    assert _ac_note(ui, "Bandit (Pirate)") == "AC > 15"


def test_a_roll_left_in_the_field_is_gone_next_turn(fight):
    ui, *_ = fight
    ui.attack_roll_input.setText("17")
    ui._advance_turn()
    assert ui.attack_roll_input.text() == ""


def test_undoing_next_turn_brings_the_roll_back(fight):
    ui, *_ = fight
    ui.attack_roll_input.setText("17")
    ui._advance_turn()
    ui._undo_last()
    assert ui.attack_roll_input.text() == "17"


def test_undoing_a_roll_is_one_step(fight):
    ui, *_ = fight
    _roll(ui, "10")
    assert len(ui.history) == 1
    ui._undo_last()
    assert _lines(ui) == []
    assert _ac_note(ui) == ""
    assert ui.attack_roll_input.text() == "10"


def test_a_monsters_action_clears_a_roll_left_in_the_field(fight):
    """It rolled its own attack, so a second verdict on it would be wrong."""
    ui, *_ = fight
    ui.attack_roll_input.setText("2")
    ui._roll_action(MonsterAction("Bite", "A bite.", to_hit=5))
    assert ui.attack_roll_input.text() == ""


def test_a_mixed_roll_leaves_only_the_targets_it_hit(fight):
    """Or the damage typed next would land on the ones it missed as well."""
    ui, _, tiger, bandit = fight
    bandit["ac"] = 19
    tiger_hp, bandit_hp = tiger["hp"], bandit["hp"]
    ui._set_targets([tiger, bandit])
    _roll(ui, "15")
    assert ui.target_characters == [tiger]

    ui.damage_input.setText("7")
    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == tiger_hp - 7
    assert bandit["hp"] == bandit_hp


def test_a_roll_that_misses_them_all_keeps_them_for_the_next_roll(fight):
    ui, _, tiger, bandit = fight
    ui._set_targets([tiger, bandit])
    bandit["ac"] = 19
    _roll(ui, "5")
    assert ui.target_characters == [tiger, bandit]


# ---------------------------------------------------------------------------
# With the damage typed as well


def _roll_with_damage(ui, roll: str, amount: str = "7"):
    ui.attack_roll_input.setText(roll)
    ui.damage_input.setText(amount)
    ui.damage_input.returnPressed.emit()


def test_a_hit_deals_the_damage_typed_with_it_as_one_undo(fight):
    ui, _, tiger, _ = fight
    hp = tiger["hp"]
    _roll_with_damage(ui, "17")
    assert tiger["hp"] == hp - 7
    assert len(_lines(ui)) == 1
    assert ui.attack_roll_input.text() == ui.damage_input.text() == ""
    assert len(ui.history) == 1

    ui._undo_last()
    assert tiger["hp"] == hp
    assert _lines(ui) == []
    assert _ac_note(ui) == ""
    assert ui.attack_roll_input.text() == "17"
    assert ui.damage_input.text() == "7"


def test_a_miss_deals_nothing_until_its_applied_again(fight):
    """Some damage lands on a miss, like the Graze mastery's."""
    ui, _, tiger, _ = fight
    hp = tiger["hp"]
    _roll_with_damage(ui, "9")
    assert tiger["hp"] == hp
    assert "no damage applied" in ui._status_label.text()
    assert ui.damage_input.text() == "7"
    assert ui.attack_roll_input.text() == ""

    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == hp - 7
    assert len(_lines(ui)) == 1


def test_only_the_targets_hit_take_the_damage(fight):
    ui, _, tiger, bandit = fight
    bandit["ac"] = 19
    tiger_hp, bandit_hp = tiger["hp"], bandit["hp"]
    ui._set_targets([tiger, bandit])
    _roll_with_damage(ui, "15")
    assert tiger["hp"] == tiger_hp - 7
    assert bandit["hp"] == bandit_hp


def test_the_status_still_says_how_it_went_after_the_damage(fight):
    ui, *_ = fight
    _roll_with_damage(ui, "17")
    assert ui._status_label.text() == f"Tiger: 17 vs AC {TIGER_AC}, hit"


def test_the_status_says_who_was_hit_and_missed_after_the_damage(fight):
    ui, _, tiger, bandit = fight
    bandit["ac"] = 19
    ui._set_targets([tiger, bandit])
    _roll_with_damage(ui, "15")
    assert ui._status_label.text() == (
        f"Tiger: 15 vs AC {TIGER_AC}, hit; Bandit (Pirate): 15 vs AC 19, miss"
    )


def test_a_miss_says_the_roll_as_well(fight):
    ui, *_ = fight
    _roll_with_damage(ui, "9")
    assert ui._status_label.text().startswith(f"Tiger: 9 vs AC {TIGER_AC}, miss")


def test_a_target_with_no_ac_still_takes_the_damage(fight):
    """The GM asked for it, and nothing says it missed."""
    ui, _, tiger, _ = fight
    tiger["ac"] = None
    hp = tiger["hp"]
    _roll_with_damage(ui, "17")
    assert tiger["hp"] == hp - 7


def test_a_roll_works_with_half_on_a_save(fight):
    ui, _, tiger, bandit = fight
    bandit["ac"] = 19
    tiger_hp, bandit_hp = tiger["hp"], bandit["hp"]
    ui._set_targets([tiger, bandit])
    ui._saved_targets = [tiger, bandit]
    _roll_with_damage(ui, "15", "8")
    assert tiger["hp"] == tiger_hp - 4
    assert bandit["hp"] == bandit_hp


def test_a_bad_roll_stops_the_damage(fight):
    ui, _, tiger, _ = fight
    hp = tiger["hp"]
    _roll_with_damage(ui, "banana")
    assert tiger["hp"] == hp
    assert ui.damage_input.text() == "7"
    assert "isn't an attack roll" in ui._status_label.text()


def test_damage_with_no_roll_works_as_ever(fight):
    ui, _, tiger, _ = fight
    hp = tiger["hp"]
    ui.damage_input.setText("7")
    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == hp - 7
    assert _lines(ui) == []


# ---------------------------------------------------------------------------
# What the players learn on the Limited view


@pytest.mark.parametrize(
    "rolls, note",
    [
        ((), ""),
        ((10,), "AC > 10"),
        ((17,), "AC ≤ 17"),
        ((10, 17), "10 < AC ≤ 17"),
        ((17, 10), "10 < AC ≤ 17"),
        # Only the best of what's known is said.
        ((10, 11), "AC > 11"),
        ((11, 10), "AC > 11"),
        ((17, 15), "AC ≤ 15"),
        ((15, 17), "AC ≤ 15"),
        ((10, 11, 15, 17), "11 < AC ≤ 15"),
        # 12 missed and 13 hit, so it can only be 13.
        ((12, 13), "AC = 13"),
    ],
)
def test_limited_says_what_the_rolls_have_shown(fight, rolls, note):
    ui, *_ = fight
    for roll in rolls:
        _roll(ui, str(roll))
    assert _ac_note(ui) == note


def test_a_natural_roll_shows_nothing_about_the_ac(fight):
    """A natural 20 hits a 40 AC, and that's no reason to think it's 20 or less."""
    ui, *_ = fight
    _roll(ui, "nat 20")
    _roll(ui, "nat 1")
    assert _ac_note(ui) == ""


def test_the_note_goes_after_the_damage_taken_and_before_the_speed(fight):
    ui, _, tiger, _ = fight
    tiger["speed_ground_ft"] = 40
    _roll(ui, "10")
    assert _details(ui, "Tiger") == "0 damage taken · AC > 10 · Speed 40 ft."


def test_informative_shows_the_ac_itself_and_no_note(fight):
    ui, *_ = fight
    _roll(ui, "10")
    ui.settings.limited_player_view = False
    details = _details(ui, "Tiger")
    assert f"AC {TIGER_AC}" in details
    assert "AC >" not in details


def test_players_see_nothing_of_the_ac_in_the_log(fight):
    """The Limited view's phones read this line."""
    ui, *_ = fight
    _roll(ui, str(TIGER_AC))
    (round_log,) = ui._public_log()
    assert round_log["turns"] == [
        {
            "name": "Pirate",
            "lines": [
                {"kind": "hit", "text": f"Hits Tiger ({TIGER_AC})", "amount": ""}
            ],
        }
    ]


def test_a_roll_at_a_hidden_monster_stays_out_of_the_players_log(fight):
    ui, _, tiger, _ = fight
    tiger["conditions"].append("Invisible")
    _roll(ui, "17")
    assert _lines(ui) == ["[Pirate's turn] Pirate's attack roll of 17 hits Tiger"]
    assert ui._public_log() == []


def test_each_member_of_a_group_has_its_own_note(tmp_path):
    def tiger(name):
        combatant = Tiger()
        combatant.set_name(name)
        combatant.initiative_group = "Tigers"
        return combatant

    ui = make_ui(tmp_path, [Pirate(), tiger("One"), tiger("Two")])
    _start(ui, 15, 9)
    ui.settings.limited_player_view = True
    pirate, one, two = ui.characters
    one["ac"] = two["ac"] = TIGER_AC
    ui._select_character(pirate)
    ui._set_targets([two])
    _roll(ui, "10")

    _, rows = ui._player_view_content()
    assert [h.name.replace("\N{NO-BREAK SPACE}", " ") for h in rows[1].health] == [
        "One (Tiger) · 0 damage taken",
        "Two (Tiger) · 0 damage taken · AC > 10",
    ]


def test_a_hidden_attackers_roll_shows_the_players_nothing(fight):
    """It isn't in their log either, so a note would give the attack away."""
    ui, _, tiger, bandit = fight
    bandit["conditions"].append("Invisible")
    ui._select_character(bandit)
    _roll(ui, "17")
    assert len(_lines(ui)) == 1
    assert _ac_note(ui) == ""


def test_a_roll_at_a_hidden_monster_still_counts(fight):
    """The players made that roll, so it's on the row once they can see it."""
    ui, _, tiger, _ = fight
    tiger["conditions"].append("Invisible")
    _roll(ui, "17")
    tiger["conditions"].remove("Invisible")
    assert _ac_note(ui) == "AC ≤ 17"


# ---------------------------------------------------------------------------
# Cover: +2 AC for Half Cover and +5 for Three-Quarters, the best one counting


@pytest.mark.parametrize(
    "states, misses, hits",
    [
        (["Half Cover"], TIGER_AC + 1, TIGER_AC + 2),
        (["Three-Quarters Cover"], TIGER_AC + 4, TIGER_AC + 5),
        (["Half Cover", "Three-Quarters Cover"], TIGER_AC + 4, TIGER_AC + 5),
        (["Hidden"], TIGER_AC - 1, TIGER_AC),
    ],
)
def test_cover_adds_to_the_ac(fight, states, misses, hits):
    ui, _, tiger, _ = fight
    tiger["visibility_states"] = states
    _roll(ui, str(misses))
    _roll(ui, str(hits))
    first, second = [line.split("] ")[1] for line in _lines(ui)]
    assert first == f"Pirate's attack roll of {misses} misses Tiger"
    assert second == f"Pirate's attack roll of {hits} hits Tiger"


def test_the_status_says_the_ac_with_cover(fight):
    ui, _, tiger, _ = fight
    tiger["visibility_states"] = ["Half Cover"]
    _roll(ui, "14")
    assert ui._status_label.text() == "Tiger: 14 vs AC 15 with cover, miss"


def test_a_natural_20_ignores_cover_too(fight):
    ui, _, tiger, _ = fight
    tiger["visibility_states"] = ["Three-Quarters Cover"]
    tiger["ac"] = 40
    _roll(ui, "nat 20")
    assert "hits Tiger (critical hit)" in _lines(ui)[0]


def test_a_note_made_in_cover_is_about_the_ac_without_it(fight):
    """A hit on 15 through Half Cover shows AC + 2 is at most 15. It has to go
    on being true when the Tiger comes out, and agree with rolls made then."""
    ui, _, tiger, _ = fight
    tiger["visibility_states"] = ["Half Cover"]
    _roll(ui, "15")
    assert _ac_note(ui) == "AC ≤ 13"
    tiger["visibility_states"] = []
    _roll(ui, "12")
    assert _ac_note(ui) == "AC = 13"


def test_a_miss_in_cover_is_about_the_ac_without_it_too(fight):
    ui, _, tiger, _ = fight
    tiger["visibility_states"] = ["Half Cover"]
    _roll(ui, "14")
    assert _ac_note(ui) == "AC > 12"


# ---------------------------------------------------------------------------
# Across fights


def _campaign_ui(tmp_path) -> CombatAppQt:
    qapp()
    logs = tmp_path / "CombatLogs"
    prepare_log(scenario_log_path(logs, TIGER.name), TIGER, [])
    ui = CombatAppQt([], [], combat_log_dir=logs, scenarios=[TIGER])
    ui._build_window()
    ui._load_encounter(TIGER, restart=False)
    _start(ui, 12)
    ui.settings.limited_player_view = True
    tiger = ui.characters[0]
    tiger["ac"] = TIGER_AC
    ui._select_character(tiger)
    ui._set_targets([tiger])
    _roll(ui, "10")
    QApplication.processEvents()
    return ui


def test_a_continued_fight_keeps_what_the_rolls_showed(tmp_path):
    ui = _campaign_ui(tmp_path)
    ui._load_encounter(TIGER, restart=False)
    QApplication.processEvents()
    assert _ac_note(ui) == "AC > 10"


def test_a_restarted_fight_forgets_what_the_rolls_showed(tmp_path):
    ui = _campaign_ui(tmp_path)
    ui._load_encounter(TIGER, restart=True)
    _start(ui, 12)
    QApplication.processEvents()
    assert _ac_note(ui) == ""
