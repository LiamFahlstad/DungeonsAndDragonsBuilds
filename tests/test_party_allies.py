"""The party's allies (PartySpec.allies, Combat/PartyAllies.py): set up with the
party in every encounter, tracked from fight to fight like the players, and
the campaign a player log belongs to (Scenarios.pick_campaign)."""

import json
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QLineEdit, QPushButton

import Combat.PartyAllies as PartyAllies
import Combat.PlayerLog as PlayerLog
import Combat.Scenarios as Scenarios
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.rest import short_rest_dialog
from Combat.Definitions import Action
from Combat.Effects.active_effects import new_effect
from Combat.EncounterConfig import (
    CampaignSpec,
    CombatantSpec,
    EncounterSpec,
    PartySpec,
    validate,
)
from Combat.EncounterLogs import prepared_log
from Combat.Monsters.CR_0.monsters import Wolf
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.Scenario import CombatScenario
from Core.Definitions import DamageType
from tests._combat_ui import qapp

PARTY = PartySpec(allies=[CombatantSpec(Wolf, "Greypaw")])
# How the window names it: its name, then its stat block.
GREYPAW = "Greypaw (Wolf)"


def _encounter(id: str, players: list[str] | None = None) -> EncounterSpec:
    return EncounterSpec(
        id, id.title(), players=players, monsters=[CombatantSpec(Tiger)]
    )


DEN = CombatScenario.from_spec(_encounter("den"), PARTY)
LAIR = CombatScenario.from_spec(_encounter("lair"), PARTY)


def _campaign(party, encounters) -> CampaignSpec:
    return CampaignSpec("test", "Test", "", party=party, encounters=encounters)


# ---------------------------------------------------------------------------
# The config


def test_a_plain_list_is_a_party_of_just_those_members():
    spec = _campaign([], [])
    assert spec.party == PartySpec()
    assert spec.party_spec.id == "main_party"


def test_party_allies_need_names_of_their_own():
    party = PartySpec(
        id="Main Party",
        allies=[CombatantSpec(Wolf), CombatantSpec(Wolf, "Edmund")],
    )
    problems = validate(_campaign(party, []), ["Edmund"])
    assert any("party id 'Main Party' must be snake_case" in p for p in problems)
    assert any("party ally Wolf: needs a name" in p for p in problems)
    assert any("'Edmund': name used twice in the party" in p for p in problems)


def test_an_encounter_cant_reuse_a_party_allys_name():
    encounter = EncounterSpec("den", "Den", monsters=[CombatantSpec(Tiger, "Greypaw")])
    problems = validate(_campaign(PARTY, [encounter]), [])
    assert problems == [
        "encounter 'den': 'Greypaw' is a party ally's name; "
        "the encounter's own monsters and allies need others"
    ]


def test_players_name_party_members_and_allies_alike():
    with_ally = CombatScenario.from_spec(_encounter("den", ["Edmund", "grey"]), PARTY)
    without = CombatScenario.from_spec(_encounter("den", ["Edmund"]), PARTY)
    assert (
        validate(
            _campaign(PARTY, [_encounter("den", ["Edmund", "grey"])]),
            [
                "Edmund",
                "Clover",
            ],
        )
        == []
    )
    assert with_ally.members_taking_part(["Edmund", "Clover"]) == ["Edmund"]
    assert with_ally.party_allies_taking_part() == ["Greypaw"]
    assert without.party_allies_taking_part() == []
    assert DEN.party_allies_taking_part() == ["Greypaw"]
    # --difficulty counts them with the allies.
    assert [c.name for c in without.build_allies()] == []
    assert [c.name for c in DEN.build_allies()] == ["Greypaw"]


def test_an_entry_matching_a_member_and_an_ally_is_ambiguous():
    problems = validate(_campaign(PARTY, [_encounter("den", ["e"])]), ["Edmund"])
    assert len(problems) == 1 and "'e' matches" in problems[0]


def test_the_log_is_set_up_with_the_party_allies_first_and_marked():
    combatants = prepared_log(DEN, [])["combatants"]
    assert [c["name"] for c in combatants] == [GREYPAW, "Tiger"]
    greypaw, tiger = combatants
    assert PartyAllies.is_party_ally(greypaw) and greypaw["death_saves"]
    assert not PartyAllies.is_party_ally(tiger)


# ---------------------------------------------------------------------------
# How an ally is now, from the player log


def _played(tmp_path: Path, name: str, **greypaw) -> dict:
    """A player-log entry for an encounter log in which Greypaw was left as
    `greypaw` says (an 11 HP wolf)."""
    char = {"name": "Greypaw", "hp": 11, "max_hp": 11, "conditions": []}
    char.update(greypaw)
    path = tmp_path / "CombatLogs" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"combatants": [char]}), encoding="utf-8")
    return {"type": PlayerLog.ENCOUNTER, "log": f"../CombatLogs/{name}.json"}


def _short_rest(heal: int) -> dict:
    event = {"character": "Greypaw", "action": Action.HEAL, "value": {"heal": heal}}
    return {"type": PlayerLog.SHORT_REST, "events": [event]}


def _state(tmp_path, sessions, skip=None):
    log = tmp_path / "PlayerLogs" / "main_party.json"
    return PartyAllies.ally_state("Greypaw", sessions, log, skip_log=skip)


def _left(tmp_path, sessions) -> dict:
    """_state for sessions that do leave the ally changed."""
    state = _state(tmp_path, sessions)
    assert state is not None
    return state


def test_an_ally_is_as_the_last_fight_left_it(tmp_path):
    sessions = [
        _played(tmp_path, "one", hp=3),
        _played(tmp_path, "two", hp=5, conditions=["Prone", "Poisoned"]),
    ]
    assert _state(tmp_path, sessions) == {"hp": 5, "conditions": ["Prone", "Poisoned"]}
    # Not counting the encounter being opened.
    assert _state(tmp_path, sessions, skip="../CombatLogs/two.json") == {
        "hp": 3,
        "conditions": [],
    }


def test_conditions_ending_on_a_timer_or_a_save_stay_in_the_fight(tmp_path):
    played = _played(
        tmp_path,
        "one",
        hp=5,
        conditions=["Prone", "Frightened", "Restrained"],
        active_effects=[
            {**new_effect("Frightened"), "duration": {"time_left": 6}},
            {
                **new_effect("Restrained"),
                "repeat_save": {
                    "ability": "WIS",
                    "dc": 13,
                    "mode": "Neutral",
                    "use_legendary_resistance": False,
                    "also": [],
                },
            },
        ],
    )
    assert _left(tmp_path, [played])["conditions"] == ["Prone"]


def test_a_short_rest_heals_an_ally_up_to_its_maximum(tmp_path):
    played = _played(tmp_path, "one", hp=2)
    assert _left(tmp_path, [played, _short_rest(4)])["hp"] == 6
    assert _left(tmp_path, [played, _short_rest(40)])["hp"] == 11


def test_a_short_rest_gets_a_downed_ally_back_up(tmp_path):
    played = _played(
        tmp_path, "one", hp=0, conditions=["Unconscious"], death_saves_fail=2
    )
    state = _left(tmp_path, [played, _short_rest(3)])
    assert (state["hp"], state["conditions"], state["death_saves_fail"]) == (3, [], 0)


def test_a_long_rest_brings_an_ally_back_to_full(tmp_path):
    played = _played(tmp_path, "one", hp=2, legendary_resistances_left=0)
    assert _state(tmp_path, [played, PlayerLog.long_rest_entry()]) is None
    # And the next fight after it counts again.
    again = _played(tmp_path, "two", hp=7)
    assert _left(tmp_path, [played, PlayerLog.long_rest_entry(), again])["hp"] == 7


def test_apply_state_keeps_hit_points_within_the_maximum():
    char = {"name": "Greypaw", "hp": 11, "max_hp": 9}
    PartyAllies.apply_state(char, {"hp": 11})
    assert char["hp"] == 9


# ---------------------------------------------------------------------------
# In the window


def _ui(tmp_path) -> CombatAppQt:
    qapp()
    ui = CombatAppQt(
        [],
        [],
        combat_log_dir=tmp_path / "CombatLogs",
        player_log_path=str(tmp_path / "PlayerLogs" / "main_party.json"),
        scenarios=[DEN, LAIR],
        party_allies=PARTY.allies,
    )
    ui._build_window()
    return ui


def _char(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


def _fight(ui, scenario):
    ui._load_encounter(scenario, restart=False)
    # Distinct rolls: a tie opens the tie-break dialog.
    for roll, unit in enumerate(ui._initiative_row_units(), start=10):
        ui._initiative_inputs[id(unit[0])].setText(str(roll))
    ui._start_combat()


def _hit_greypaw(ui, amount: int):
    ui._select_character(_char(ui, "Tiger"))
    ui._select_target_character(_char(ui, GREYPAW))
    slashing = ui.damage_type_combo.findData(DamageType.SLASHING.value)
    ui.damage_type_combo.setCurrentIndex(slashing)
    ui.damage_input.setText(str(amount))
    ui._apply_damage()


def test_an_ally_joins_the_next_fight_as_the_last_one_left_it(tmp_path):
    ui = _ui(tmp_path)
    _fight(ui, DEN)
    full = _char(ui, GREYPAW)["max_hp"]
    _hit_greypaw(ui, 5)
    ui._load_encounter(LAIR, restart=False)
    assert _char(ui, GREYPAW)["hp"] == full - 5
    # A long rest brings it back to full.
    ui.player_log_data["sessions"].append(PlayerLog.long_rest_entry())
    ui._load_encounter(LAIR, restart=False)
    assert _char(ui, GREYPAW)["hp"] == full


def test_an_ally_at_0_hp_is_dying_not_dead_and_stays_down(tmp_path):
    ui = _ui(tmp_path)
    _fight(ui, DEN)
    _hit_greypaw(ui, 99)
    assert ui._char_death_state(_char(ui, GREYPAW)) == "dying"
    ui._load_encounter(LAIR, restart=False)
    assert _char(ui, GREYPAW)["hp"] == 0


def test_between_encounters_and_a_short_rest_have_the_allies(tmp_path):
    ui = _ui(tmp_path)
    _fight(ui, DEN)
    full = _char(ui, GREYPAW)["max_hp"]
    _hit_greypaw(ui, 5)
    ui._leave_encounter()
    greypaw = _char(ui, GREYPAW)
    assert greypaw["hp"] == full - 5 and id(greypaw) in ui._card_widgets
    # Hurt again between encounters: that's logged, and counts from here on.
    ui._select_character(greypaw)
    ui._select_target_character(greypaw)
    ui.damage_input.setText("1 slashing")
    ui._apply_damage()
    assert [c["name"] for c in _ui(tmp_path).characters] == [GREYPAW]
    assert _char(_ui(tmp_path), GREYPAW)["hp"] == full - 6

    def heal_greypaw():
        dialog = short_rest_dialog(ui)
        (heal_input,) = dialog.findChildren(QLineEdit)
        heal_input.setText("3")
        apply = next(
            b
            for b in dialog.findChildren(QPushButton)
            if b.text() == "Apply Short Rest"
        )
        apply.click()

    ui._record_short_rest(heal_greypaw)
    (greypaw,) = ui._party_allies_now()
    assert greypaw["hp"] == full - 3
    ui._load_encounter(LAIR, restart=False)
    assert _char(ui, GREYPAW)["hp"] == full - 3


# ---------------------------------------------------------------------------
# Which campaign a player log belongs to

TIME_LOOP_LOG = "Combat/Campaigns/TimeLoopPR/PlayerLogs/main_party.json"
CURSE_LOG = "Combat/Campaigns/CurseOfTheLich/PlayerLogs/main_party.json"


def test_a_player_log_picks_its_campaign():
    """The bug: --player-log alone ran the default campaign's party."""
    assert Scenarios.pick_campaign(player_log=TIME_LOOP_LOG).name == "time_loop_pr"
    assert Scenarios.pick_campaign(player_log=CURSE_LOG).name == "curse_of_the_lich"
    campaign = Scenarios.CAMPAIGNS["time_loop_pr"]
    assert campaign.default_player_log.resolve() == Path(TIME_LOOP_LOG).resolve()


def test_a_player_log_of_another_campaign_is_refused():
    with pytest.raises(ValueError, match="'time_loop_pr''s party log"):
        Scenarios.pick_campaign(campaign="curse_of_the_lich", player_log=TIME_LOOP_LOG)
    with pytest.raises(ValueError, match="'curse_of_the_lich''s party log"):
        Scenarios.pick_campaign(scenario="time_loop_pr_square", player_log=CURSE_LOG)


def test_a_player_log_kept_elsewhere_runs_the_campaign_asked_for(tmp_path):
    elsewhere = tmp_path / "party.json"
    assert Scenarios.pick_campaign(player_log=elsewhere).name == (
        Scenarios.DEFAULT_CAMPAIGN
    )
    assert (
        Scenarios.pick_campaign(campaign="time_loop_pr", player_log=elsewhere).name
        == "time_loop_pr"
    )
