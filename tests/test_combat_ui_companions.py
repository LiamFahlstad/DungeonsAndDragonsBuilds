"""Players' companions in the combat window (Combat/Companions.py,
Combat/CombatUIQt/companions_mixin.py): Dessie's Reanimated Companion and
Hanna's Drake Companion, as the Time Loop PR campaign has them. They take
their turn right after their owner's, are summoned with the feature's use (or
a spell slot) and a choice (the drake's Draconic Essence), die with their
owner, stay out from one encounter to the next until a long rest, and can be
added to a fight prepared without them."""

import json
from functools import cache

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

import Combat.PlayerLog as PlayerLog
from CharacterContent.Features.SubClassFeatures.Artificer.ArtificerReanimatorFeatures import (
    ReanimatedCompanion,
)
from Combat.Companions import CHOICE_KEY, carried_state, place_after_owners
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.player_view import _can_be_seen
from Combat.EncounterLogs import prepare_log, scenario_log_path
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.PlayerCombatant import companions_of
from Combat.Scenario import CombatScenario
from Core.Definitions import DamageType
from tests._combat_ui import qapp
from tests._snapshot_helpers import build

DESSIE_BUILD = "Y2024_Artificer_Reanimator_Dessie"
HANNA_BUILD = "Y2024_Ranger_Drakewarden_Hanna"
DRAKE = "Hanna's Companion (Drake Companion)"
REANIMATED = "Dessie's Companion (Reanimated Companion)"

DEN = CombatScenario(name="den", title="Den", combatants=lambda: [Tiger()])
LAIR = CombatScenario(name="lair", title="Lair", combatants=lambda: [Tiger()])
# Prepared without the party's sheets, as logs were before companions.
OLD = CombatScenario(name="old", title="Old", combatants=lambda: [Tiger()])


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


@cache
def _sheet(build_name: str):
    return build(build_name)


def _party() -> list:
    return [_sheet(DESSIE_BUILD), _sheet(HANNA_BUILD)]


def _ui(tmp_path) -> CombatAppQt:
    """The window for a campaign in tmp_path with DEN, LAIR and OLD
    prepared, on the party between encounters."""
    qapp()
    sheets = {cs.character_name: cs for cs in _party()}
    logs = tmp_path / "CombatLogs"
    for scenario in (DEN, LAIR, OLD):
        path = scenario_log_path(logs, scenario.name)
        if not path.exists():
            with_sheets = None if scenario is OLD else sheets
            prepare_log(path, scenario, list(sheets), sheets=with_sheets)
    ui = CombatAppQt(
        [],
        _party(),
        combat_log_dir=logs,
        player_log_path=str(tmp_path / "PlayerLogs" / "main_party.json"),
        scenarios=[DEN, LAIR, OLD],
    )
    ui._build_window()
    return ui


def _char(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


def _start(ui, **initiatives: int):
    """Start the fight with these initiatives by name (the rest roll 10)."""
    for unit in ui._initiative_row_units():
        value = initiatives.get(unit[0]["name"], 10)
        ui._initiative_inputs[id(unit[0])].setText(str(value))
    ui._start_combat()


def _in_fight(tmp_path, scenario=DEN) -> CombatAppQt:
    ui = _ui(tmp_path)
    ui._load_encounter(scenario, restart=False)
    _start(ui, Hanna=15, Dessie=5)
    return ui


def _hit(ui, source, target, amount: int):
    ui._select_character(source)
    ui._select_target_character(target)
    slashing = ui.damage_type_combo.findData(DamageType.SLASHING.value)
    ui.damage_type_combo.setCurrentIndex(slashing)
    ui.damage_input.setText(str(amount))
    ui._apply_damage()


def _log_text(ui) -> str:
    assert ui.log_file is not None
    return ui.log_file.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Initiative


def test_companions_roll_no_initiative_and_go_right_after_their_owner(tmp_path):
    ui = _ui(tmp_path)
    ui._load_encounter(DEN, restart=False)
    drake, reanimated = _char(ui, DRAKE), _char(ui, REANIMATED)
    assert id(drake) not in ui._initiative_inputs
    assert id(reanimated) not in ui._initiative_inputs
    ui._roll_monster_initiative()  # rolls the Tiger only
    assert ui._initiative_inputs[id(_char(ui, "Tiger"))].text()
    _start(ui, Hanna=15, Tiger=10, Dessie=5)
    assert [c["name"] for c in ui.initiative_order] == [
        "Hanna",
        DRAKE,
        "Tiger",
        "Dessie",
        REANIMATED,
    ]


def test_place_after_owners_keeps_order_and_appends_an_ownerless_one():
    hanna, tiger = {"name": "Hanna"}, {"name": "Tiger"}
    drake = {"name": "Drake", "companion_of": "Hanna"}
    stray = {"name": "Stray", "companion_of": "Edmund"}
    order = place_after_owners([hanna, tiger], [drake, stray])
    assert [c["name"] for c in order] == ["Hanna", "Drake", "Tiger", "Stray"]


# ---------------------------------------------------------------------------
# Summoning


def test_summoning_the_drake_spends_the_use_and_takes_the_essence(tmp_path):
    ui = _in_fight(tmp_path)
    hanna, drake = _char(ui, "Hanna"), _char(ui, DRAKE)
    assert not _can_be_seen(drake)
    ui._summon_companion(drake, "Cold")
    assert _can_be_seen(drake)
    assert (drake["hp"], drake["max_hp"], drake[CHOICE_KEY]) == (20, 20, "Cold")
    # Draconic Essence: its immunity and Infused Strikes follow the choice.
    assert [e["damage_types"] for e in drake["damage_immunities"]] == [["Cold"]]
    (infused,) = drake["reactions"]
    assert "extra 1d6 Cold damage" in infused["description"]
    assert hanna["feature_uses_used"]["Drake Companion"] == 1
    assert "Hanna summons Hanna's Companion (Drake Companion) (Cold)" in _log_text(ui)


def test_summoning_again_spends_a_spell_slot_and_without_one_does_nothing(
    tmp_path,
):
    ui = _in_fight(tmp_path)
    hanna, drake = _char(ui, "Hanna"), _char(ui, DRAKE)
    ui._summon_companion(drake, "Fire")
    _hit(ui, _char(ui, "Tiger"), drake, 12)
    assert drake["hp"] == 8
    slots = hanna["spell_slots"][1]
    ui._summon_companion(drake, "Acid")  # a new drake, at full HP
    assert (drake["hp"], drake[CHOICE_KEY]) == (20, "Acid")
    assert hanna["spell_slots"][1] == slots - 1
    assert hanna["feature_uses_used"]["Drake Companion"] == 1

    hanna["spell_slots"] = {1: 0}
    _hit(ui, _char(ui, "Tiger"), drake, 5)
    ui._summon_companion(drake, "Poison")
    assert (drake["hp"], drake[CHOICE_KEY]) == (15, "Acid")
    assert "no spell slot left" in ui._status_label.text()


def test_enable_feature_summons_a_companion_with_no_choice_to_make(tmp_path):
    ui = _in_fight(tmp_path)
    dessie, reanimated = _char(ui, "Dessie"), _char(ui, REANIMATED)
    feature = next(
        f for f in dessie["_feature_objects"] if isinstance(f, ReanimatedCompanion)
    )
    ui._select_character(dessie)
    ui._apply_feature(feature)
    assert _can_be_seen(reanimated) and reanimated["hp"] == 20
    assert dessie["feature_uses_used"]["Reanimated Companion"] == 1
    assert CHOICE_KEY not in reanimated


def test_the_card_menus_offer_the_summon_with_its_cost(tmp_path):
    ui = _in_fight(tmp_path)

    def summon_texts(char):
        return [a.text() for a in ui._card_menu(char).actions() if "Summon" in a.text()]

    assert summon_texts(_char(ui, DRAKE)) == ["Summon Drake Companion (1 use left)"]
    assert summon_texts(_char(ui, "Hanna")) == ["Summon Drake Companion (1 use left)"]
    assert summon_texts(_char(ui, "Dessie")) == [
        "Summon Reanimated Companion (1 use left)"
    ]
    assert summon_texts(_char(ui, "Tiger")) == []
    ui._summon_companion(_char(ui, DRAKE), "Fire")
    assert summon_texts(_char(ui, DRAKE)) == ["Summon Drake Companion (a level 1 slot)"]


def test_the_drake_offers_every_draconic_essence():
    hanna = _sheet(HANNA_BUILD)
    (feature,) = [f for f in hanna.features if f.companion(hanna) is not None]
    assert feature.companion_choices(hanna) == [
        "Acid",
        "Cold",
        "Fire",
        "Lightning",
        "Poison",
    ]
    lightning, own = feature.companion(hanna, "Lightning"), feature.companion(hanna)
    assert lightning is not None and own is not None
    assert [e.damage_types for e in lightning.damage_immunities or []] == [
        [DamageType.LIGHTNING]
    ]
    # The build's own choice when none is made.
    assert [e.damage_types for e in own.damage_immunities or []] == [[DamageType.FIRE]]


# ---------------------------------------------------------------------------
# Dying with the owner


def test_a_companion_dies_with_its_owner_and_its_death_burst_goes_off(tmp_path):
    ui = _in_fight(tmp_path)
    dessie, reanimated = _char(ui, "Dessie"), _char(ui, REANIMATED)
    ui._summon_companion(reanimated, None)
    _hit(ui, _char(ui, "Tiger"), dessie, dessie["hp"])
    for _ in range(3):
        ui._apply_failed_death_save(dessie)
    assert ui._char_death_state(dessie) == "dead"
    assert reanimated["hp"] == 0
    assert (
        f"{REANIMATED} drops to 0 HP: Dessie died (its Death Burst goes off)"
        in _log_text(ui)
    )


def test_a_hidden_companion_isnt_killed_with_its_owner(tmp_path):
    ui = _in_fight(tmp_path)
    dessie, reanimated = _char(ui, "Dessie"), _char(ui, REANIMATED)
    _hit(ui, _char(ui, "Tiger"), dessie, dessie["hp"])
    for _ in range(3):
        ui._apply_failed_death_save(dessie)
    assert reanimated["hp"] == 20 and reanimated["hidden_from_players"]


# ---------------------------------------------------------------------------
# From one encounter to the next


def test_a_companion_that_is_out_stays_out_into_the_next_encounter(tmp_path):
    ui = _in_fight(tmp_path)
    ui._summon_companion(_char(ui, DRAKE), "Cold")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 6)
    ui._load_encounter(LAIR, restart=False)
    drake, reanimated = _char(ui, DRAKE), _char(ui, REANIMATED)
    assert (drake["hp"], drake[CHOICE_KEY]) == (14, "Cold")
    assert _can_be_seen(drake)
    assert [e["damage_types"] for e in drake["damage_immunities"]] == [["Cold"]]
    # Never summoned: still hidden, at full HP.
    assert reanimated["hidden_from_players"] and reanimated["hp"] == 20
    # And the use stays spent: the replay counts it.
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1


def test_a_drake_that_died_stays_gone_even_after_a_long_rest(tmp_path):
    ui = _in_fight(tmp_path)
    ui._summon_companion(_char(ui, DRAKE), "Cold")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 30)
    ui._load_encounter(LAIR, restart=False)
    drake = _char(ui, DRAKE)
    assert drake["hp"] == 0 and drake["hidden_from_players"]
    # It "remains until it is reduced to 0 hit points": the rest gives Hanna
    # her use back, but the drake has to be summoned again.
    ui.player_log_data["sessions"].append(PlayerLog.long_rest_entry())
    ui._load_encounter(LAIR, restart=False)
    drake = _char(ui, DRAKE)
    assert drake["hp"] == 0 and drake["hidden_from_players"]


def test_a_long_rest_rests_a_drake_but_ends_a_reanimated_companion(tmp_path):
    ui = _in_fight(tmp_path)
    ui._summon_companion(_char(ui, DRAKE), "Cold")
    ui._summon_companion(_char(ui, REANIMATED), None)
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 6)
    _hit(ui, _char(ui, "Tiger"), _char(ui, REANIMATED), 6)
    ui.player_log_data["sessions"].append(PlayerLog.long_rest_entry())
    ui._load_encounter(LAIR, restart=False)
    drake, reanimated = _char(ui, DRAKE), _char(ui, REANIMATED)
    # Still out, rested to full, with the Draconic Essence it was summoned with.
    assert _can_be_seen(drake)
    assert (drake["hp"], drake[CHOICE_KEY]) == (20, "Cold")
    # "It lasts until you finish a Long Rest."
    assert reanimated["hidden_from_players"] and reanimated["hp"] == 20


def test_carried_state():
    previous = {"hp": 7, "max_hp": 20, "temp_hp": 2, "conditions": ["Prone"]}
    assert carried_state(previous) == {
        "hp": 7,
        "temp_hp": 2,
        "conditions": ["Prone"],
        "hidden_from_players": False,
    }
    assert carried_state(previous, rested=True) == {
        "hp": 20,
        "temp_hp": 0,
        "conditions": [],
        "hidden_from_players": False,
    }
    assert carried_state({"hp": 0})["hidden_from_players"] is True


def test_conditions_ending_on_a_timer_or_a_save_arent_carried():
    previous = {
        "hp": 7,
        "conditions": ["Poisoned", "Frightened", "Prone"],
        "timed_conditions": [{"name": "Poisoned", "time_left": 6}],
        "repeat_saves": [{"condition": "Frightened"}],
    }
    assert carried_state(previous)["conditions"] == ["Prone"]


# ---------------------------------------------------------------------------
# Review fixes


def test_a_reanimated_companion_cant_be_made_while_its_out(tmp_path):
    ui = _in_fight(tmp_path)
    dessie, reanimated = _char(ui, "Dessie"), _char(ui, REANIMATED)
    ui._summon_companion(reanimated, None)
    _hit(ui, _char(ui, "Tiger"), reanimated, 5)
    slots = dict(dessie["spell_slots"])
    ui._summon_companion(reanimated, None)
    assert reanimated["hp"] == 15 and dessie["spell_slots"] == slots
    assert "still out" in ui._status_label.text()
    menu = [a.text() for a in ui._card_menu(reanimated).actions()]
    assert not any("Summon" in text for text in menu)
    # Once it's gone, a spell slot makes another.
    reanimated["hp"] = 0
    ui._summon_companion(reanimated, None)
    assert reanimated["hp"] == 20
    assert dessie["spell_slots"][1] == slots[1] - 1


def test_a_slot_paid_summon_isnt_replayed_as_a_use(tmp_path):
    ui = _in_fight(tmp_path)
    drake = _char(ui, DRAKE)
    ui._summon_companion(drake, "Fire")
    ui._summon_companion(drake, "Cold")  # with a spell slot
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1
    ui._load_encounter(LAIR, restart=False)
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1


def test_a_companion_that_dies_with_its_owner_isnt_bloodied(tmp_path):
    ui = _in_fight(tmp_path)
    dessie, reanimated = _char(ui, "Dessie"), _char(ui, REANIMATED)
    ui._summon_companion(reanimated, None)
    _hit(ui, _char(ui, "Tiger"), reanimated, 12)
    assert "Bloodied" in reanimated["conditions"]
    _hit(ui, _char(ui, "Tiger"), dessie, dessie["hp"])
    for _ in range(3):
        ui._apply_failed_death_save(dessie)
    assert reanimated["hp"] == 0 and "Bloodied" not in reanimated["conditions"]


# ---------------------------------------------------------------------------
# A fight prepared without them


def test_add_combatant_adds_a_missing_companion_after_its_owner(tmp_path):
    ui = _in_fight(tmp_path, scenario=OLD)
    assert [c["name"] for c in ui.characters if c.get("companion_of")] == []
    missing = ui._missing_party_companions()
    # In the window's order: Hanna (initiative 15) before Dessie (5).
    assert [name for name, _ in missing] == [DRAKE, REANIMATED]
    ui._add_party_companion(missing[0][1])
    order = [c["name"] for c in ui.initiative_order]
    assert order[order.index("Hanna") + 1] == DRAKE
    drake = _char(ui, DRAKE)
    assert drake["hidden_from_players"] and drake["companion_of"] == "Hanna"
    assert [name for name, _ in ui._missing_party_companions()] == [REANIMATED]
    saved = json.loads(_log_text(ui))
    assert DRAKE in [c["name"] for c in saved["combatants"]]


def test_adding_a_companion_mid_fight_keeps_whoevers_turn_it_is(tmp_path):
    ui = _in_fight(tmp_path, scenario=OLD)
    assert [c["name"] for c in ui.initiative_order] == ["Hanna", "Tiger", "Dessie"]
    ui._pass_turn()
    assert ui._current_turn_character()["name"] == "Tiger"
    (drake,) = [sb for name, sb in ui._missing_party_companions() if name == DRAKE]
    ui._add_party_companion(drake)
    assert [c["name"] for c in ui.initiative_order] == [
        "Hanna",
        DRAKE,
        "Tiger",
        "Dessie",
    ]
    assert ui._current_turn_character()["name"] == "Tiger"


def test_companions_of_marks_the_owner():
    (drake,) = companions_of(_sheet(HANNA_BUILD))
    assert (drake.companion_of, drake.hidden_from_players) == ("Hanna", True)
