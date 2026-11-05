"""Players' summons in the combat window (Combat/Summons.py,
Combat/CombatUIQt/summons_mixin.py): Dessie's Reanimated Companion and
Hanna's Drake Companion, as the Time Loop PR campaign has them. They're made
when they're summoned (with the feature's use, or a spell slot, and a choice:
the drake's Draconic Essence), take their turn right after their owner's, die
with their owner, can be dismissed, stay out from one encounter to the next
until a long rest, and can join a fight already summoned. Older logs (a hidden
companion prepared with each encounter, "companion_of", "<owner>'s Companion
(<type>)") still load and carry over."""

import dataclasses
import json
import shutil
from functools import cache
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

import Combat.PlayerLog as PlayerLog
import Combat.Scenarios as Scenarios
from CharacterContent.Features.SubClassFeatures.Artificer.ArtificerReanimatorFeatures import (
    ReanimatedCompanion,
)
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.player_view import _can_be_seen
from Combat.EncounterLogs import prepare_log, scenario_log_path
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.Scenario import CombatScenario
from Combat.Summons import (
    CHOICE_KEY,
    SOURCE_KEY,
    SUMMON_OF_KEY,
    SummonOption,
    carried_state,
    create,
    feature_summons,
    make_room,
    old_name,
    place_after_owners,
    upgrade_keys,
)
from Core.Definitions import DamageType
from Model.Content.Summons import SummonContext
from tests._combat_ui import qapp
from tests._snapshot_helpers import build

DESSIE_BUILD = "Y2024_Artificer_Reanimator_Dessie"
HANNA_BUILD = "Y2024_Ranger_Drakewarden_Hanna"
DRAKE = "Hanna's Drake Companion"
REANIMATED = "Dessie's Reanimated Companion"
# What logs from before each summon had its own name called them.
OLD_DRAKE = "Hanna's Companion (Drake Companion)"
OLD_REANIMATED = "Dessie's Companion (Reanimated Companion)"

DEN = CombatScenario(name="den", title="Den", combatants=lambda: [Tiger()])
LAIR = CombatScenario(name="lair", title="Lair", combatants=lambda: [Tiger()])
# Prepared as logs were before summons were made on demand: with a hidden
# companion for each player, under the old key and name.
OLD = CombatScenario(name="old", title="Old", combatants=lambda: [Tiger()])

TIME_LOOP_LOGS = [
    "time_loop_pr_drunk_oxe",
    "time_loop_pr_mira",
    "time_loop_pr_outside_the_gates",
    "time_loop_pr_square",
]


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


def _spec_of(sheet, feature_name: str):
    """(feature, spec) of sheet's summon feature called feature_name."""
    return next((f, s) for f, s in feature_summons(sheet) if f.name == feature_name)


def _old_style(char: dict, hidden: bool = True) -> dict:
    """char as logs from before summons were made on demand stored it."""
    old = {k: v for k, v in char.items() if not k.startswith("summon_")}
    old["companion_of"] = char[SUMMON_OF_KEY]
    if CHOICE_KEY in char:
        old["companion_choice"] = char[CHOICE_KEY]
    old["name"] = old_name(char[SUMMON_OF_KEY], char["combatant_type"])
    if hidden:
        old["hidden_from_players"] = True
    return old


def _old_companions() -> list[dict]:
    """The hidden companions an older log was prepared with."""
    made = []
    for sheet, feature_name in (
        (_sheet(DESSIE_BUILD), "Reanimated Companion"),
        (_sheet(HANNA_BUILD), "Drake Companion"),
    ):
        feature, spec = _spec_of(sheet, feature_name)
        (char,) = create(sheet, feature, spec, SummonContext(), set())
        made.append(_old_style(char))
    return made


def _ui(tmp_path) -> CombatAppQt:
    """The window for a campaign in tmp_path with DEN, LAIR and OLD
    prepared, on the party between encounters."""
    qapp()
    sheets = {cs.character_name: cs for cs in _party()}
    logs = tmp_path / "CombatLogs"
    for scenario in (DEN, LAIR, OLD):
        path = scenario_log_path(logs, scenario.name)
        if not path.exists():
            prepare_log(path, scenario, list(sheets), sheets=sheets)
            if scenario is OLD:
                data = json.loads(path.read_text(encoding="utf-8"))
                data["combatants"] = _old_companions() + data["combatants"]
                path.write_text(json.dumps(data, indent=2), encoding="utf-8")
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


def _names(ui) -> list[str]:
    return [c["name"] for c in ui.characters]


def _turn(ui) -> str:
    """Whose turn it is."""
    char = ui._current_turn_character()
    assert char is not None
    return char["name"]


def _order(ui) -> list[str]:
    return [c["name"] for c in ui.initiative_order]


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


def _summon(ui, owner: str, choice: str | None = None):
    """owner (Hanna: her drake, Dessie: her Reanimated Companion) summons."""
    player = _char(ui, owner)
    name = {"Hanna": "Drake Companion", "Dessie": "Reanimated Companion"}[owner]
    feature, spec = _spec_of(player["_stat_block"], name)
    ui._summon(player, feature, spec, choice)


def _option(ui, label: str) -> SummonOption:
    return next(o for o in ui._already_summoned_options() if o.label == label)


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


def _menu_texts(ui, char) -> list[str]:
    return [a.text() for a in ui._card_menu(char).actions()]


# ---------------------------------------------------------------------------
# Initiative


def test_a_prepared_encounter_has_no_summons_until_theyre_summoned(tmp_path):
    ui = _ui(tmp_path)
    ui._load_encounter(DEN, restart=False)
    assert _names(ui) == ["Dessie", "Hanna", "Tiger"]
    saved = json.loads(_log_text(ui))
    assert [c["name"] for c in saved["combatants"]] == ["Tiger"]


def test_summons_roll_no_initiative_and_go_right_after_their_owner(tmp_path):
    ui = _ui(tmp_path)
    ui._load_encounter(DEN, restart=False)
    ui._add_already_summoned(_option(ui, f"{DRAKE} (Fire)"))
    ui._add_already_summoned(_option(ui, REANIMATED))
    drake, reanimated = _char(ui, DRAKE), _char(ui, REANIMATED)
    assert id(drake) not in ui._initiative_inputs
    assert id(reanimated) not in ui._initiative_inputs
    ui._roll_monster_initiative()  # rolls the Tiger only
    assert ui._initiative_inputs[id(_char(ui, "Tiger"))].text()
    _start(ui, Hanna=15, Tiger=10, Dessie=5)
    assert _order(ui) == ["Hanna", DRAKE, "Tiger", "Dessie", REANIMATED]


def test_place_after_owners_keeps_order_and_appends_an_ownerless_one():
    hanna, tiger = {"name": "Hanna"}, {"name": "Tiger"}
    drake = {"name": "Drake", "summon_of": "Hanna"}
    # An older log's key.
    old = {"name": "Old Drake", "companion_of": "Hanna"}
    stray = {"name": "Stray", "summon_of": "Edmund"}
    order = place_after_owners([hanna, tiger], [drake, old, stray])
    assert [c["name"] for c in order] == [
        "Hanna",
        "Drake",
        "Old Drake",
        "Tiger",
        "Stray",
    ]


# ---------------------------------------------------------------------------
# Summoning


def test_summoning_mid_fight_creates_the_drake_and_keeps_the_turn(tmp_path):
    ui = _in_fight(tmp_path)
    assert _order(ui) == ["Hanna", "Tiger", "Dessie"]
    ui._pass_turn()
    assert _turn(ui) == "Tiger"
    _summon(ui, "Hanna", "Cold")
    assert _order(ui) == ["Hanna", DRAKE, "Tiger", "Dessie"]
    assert _names(ui) == _order(ui)
    assert _turn(ui) == "Tiger"
    drake = _char(ui, DRAKE)
    assert _can_be_seen(drake)
    assert (drake["hp"], drake["max_hp"], drake[CHOICE_KEY]) == (20, 20, "Cold")
    # Level 3, Proficiency Bonus +2: 5 + 5 * 3 HP, AC 14 + 2, no wings yet.
    assert (drake["ac"], drake["speed_fly_ft"]) == (16, None)
    assert (drake[SUMMON_OF_KEY], drake[SOURCE_KEY]) == (
        "Hanna",
        "feature:Drake Companion",
    )
    assert (
        drake["summon_lifetime"],
        drake["summon_turn"],
        drake["summon_on_zero_hp"],
    ) == ("until dismissed", "after owner", "vanishes")
    # Draconic Essence: its immunity and Infused Strikes follow the choice.
    assert [e["damage_types"] for e in drake["damage_immunities"]] == [["Cold"]]
    (infused,) = drake["reactions"]
    assert "extra 1d6 Cold damage" in infused["description"]
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1
    assert f"Hanna summons {DRAKE} (Cold)" in _log_text(ui)
    saved = json.loads(_log_text(ui))
    assert DRAKE in [c["name"] for c in saved["combatants"]]


def test_two_summons_of_one_owner_get_their_own_names(tmp_path):
    hanna = _sheet(HANNA_BUILD)
    feature, spec = _spec_of(hanna, "Drake Companion")
    (second,) = create(hanna, feature, spec, SummonContext(), {DRAKE, "Tiger"})
    assert second["name"] == f"{DRAKE} 2"
    # A source that makes two at once numbers them too, and so does the window.
    pair = dataclasses.replace(spec, count=lambda *_: 2, max_out=None)
    made = create(hanna, feature, pair, SummonContext(), set())
    assert [c["name"] for c in made] == [DRAKE, f"{DRAKE} 2"]
    ui = _in_fight(tmp_path)
    option = _option(ui, f"{DRAKE} (Acid)")
    ui._add_already_summoned(dataclasses.replace(option, spec=pair))
    ui._add_already_summoned(dataclasses.replace(option, spec=pair))
    assert _order(ui) == [
        "Hanna",
        DRAKE,
        f"{DRAKE} 2",
        f"{DRAKE} 3",
        f"{DRAKE} 4",
        "Tiger",
        "Dessie",
    ]


def test_summoning_the_drake_again_replaces_it_and_without_a_slot_does_nothing(
    tmp_path,
):
    ui = _in_fight(tmp_path)
    hanna = _char(ui, "Hanna")
    _summon(ui, "Hanna", "Fire")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 12)
    assert _char(ui, DRAKE)["hp"] == 8
    slots = hanna["spell_slots"][1]
    _summon(ui, "Hanna", "Acid")  # a new drake, at full HP, the old one gone
    assert [c["name"] for c in ui._owner_summons(hanna)] == [DRAKE]
    drake = _char(ui, DRAKE)
    assert (drake["hp"], drake[CHOICE_KEY]) == (20, "Acid")
    assert _order(ui) == ["Hanna", DRAKE, "Tiger", "Dessie"]
    assert hanna["spell_slots"][1] == slots - 1
    assert hanna["feature_uses_used"]["Drake Companion"] == 1
    assert f"{DRAKE} vanishes: Hanna summons another" in _log_text(ui)

    hanna["spell_slots"] = {1: 0}
    _hit(ui, _char(ui, "Tiger"), drake, 5)
    _summon(ui, "Hanna", "Poison")
    assert (_char(ui, DRAKE)["hp"], _char(ui, DRAKE)[CHOICE_KEY]) == (15, "Acid")
    assert "no spell slot left" in ui._status_label.text()


def test_enable_feature_summons_a_companion_with_no_choice_to_make(tmp_path):
    ui = _in_fight(tmp_path)
    dessie = _char(ui, "Dessie")
    feature = next(
        f for f in dessie["_feature_objects"] if isinstance(f, ReanimatedCompanion)
    )
    ui._select_character(dessie)
    ui._apply_feature(feature)
    reanimated = _char(ui, REANIMATED)
    assert _can_be_seen(reanimated) and reanimated["hp"] == 20
    assert dessie["feature_uses_used"]["Reanimated Companion"] == 1
    assert CHOICE_KEY not in reanimated
    assert _order(ui)[-1] == REANIMATED


def test_the_card_menus_offer_the_summon_with_its_cost_and_dismiss(tmp_path):
    ui = _in_fight(tmp_path)

    def summon_texts(char):
        return [t for t in _menu_texts(ui, char) if "Summon" in t or t == "Dismiss"]

    assert summon_texts(_char(ui, "Hanna")) == ["Summon Drake Companion (1 use left)"]
    assert summon_texts(_char(ui, "Dessie")) == [
        "Summon Reanimated Companion (1 use left)"
    ]
    assert summon_texts(_char(ui, "Tiger")) == []
    _summon(ui, "Hanna", "Fire")
    assert summon_texts(_char(ui, DRAKE)) == [
        "Summon Drake Companion (a level 1 slot)",
        "Dismiss",
    ]
    assert summon_texts(_char(ui, "Hanna")) == [
        "Summon Drake Companion (a level 1 slot)"
    ]


def test_the_drake_offers_every_draconic_essence():
    hanna = _sheet(HANNA_BUILD)
    (spec,) = [s for f in hanna.features for s in f.summons(hanna)]
    assert spec.choices(hanna) == ["Acid", "Cold", "Fire", "Lightning", "Poison"]
    lightning = spec.build(hanna, SummonContext(choice="Lightning"))
    own = spec.build(hanna, SummonContext())
    assert lightning is not None and own is not None
    assert [e.damage_types for e in lightning.damage_immunities or []] == [
        [DamageType.LIGHTNING]
    ]
    # The build's own choice when none is made.
    assert [e.damage_types for e in own.damage_immunities or []] == [[DamageType.FIRE]]


def test_a_reanimated_companion_cant_be_made_while_its_out(tmp_path):
    ui = _in_fight(tmp_path)
    dessie = _char(ui, "Dessie")
    _summon(ui, "Dessie")
    reanimated = _char(ui, REANIMATED)
    _hit(ui, _char(ui, "Tiger"), reanimated, 5)
    slots = dict(dessie["spell_slots"])
    _summon(ui, "Dessie")
    assert reanimated["hp"] == 15 and dessie["spell_slots"] == slots
    assert [c["name"] for c in ui._owner_summons(dessie)] == [REANIMATED]
    assert "still out" in ui._status_label.text()
    # Greyed out on both cards.
    for char in (reanimated, dessie):
        menu = ui._card_menu(char)
        (entry,) = [a for a in menu.actions() if "Summon" in a.text()]
        assert entry.text() == "Summon Reanimated Companion (one is already out)"
        assert not entry.isEnabled()
    # Once it's dead (its body stays), a spell slot makes another.
    reanimated["hp"] = 0
    _summon(ui, "Dessie")
    assert [c["name"] for c in ui._owner_summons(dessie)] == [
        REANIMATED,
        f"{REANIMATED} 2",
    ]
    assert _char(ui, f"{REANIMATED} 2")["hp"] == 20
    assert dessie["spell_slots"][1] == slots[1] - 1


def test_a_slot_paid_summon_isnt_replayed_as_a_use(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Fire")
    _summon(ui, "Hanna", "Cold")  # with a spell slot
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1
    ui._load_encounter(LAIR, restart=False)
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1


# ---------------------------------------------------------------------------
# Dismissing


def test_dismissing_a_summon_takes_it_out_and_undo_brings_it_back(tmp_path):
    ui = _in_fight(tmp_path)
    ui._pass_turn()  # the Tiger's turn
    _summon(ui, "Hanna", "Cold")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 4)
    assert "Dismiss" in _menu_texts(ui, _char(ui, DRAKE))
    ui._dismiss_summon(_char(ui, DRAKE))
    assert DRAKE not in _names(ui) and DRAKE not in _order(ui)
    assert _turn(ui) == "Tiger"
    assert ui.target_characters == []
    assert f"Hanna dismisses {DRAKE}" in _log_text(ui)
    saved = json.loads(_log_text(ui))
    assert DRAKE not in [c["name"] for c in saved["combatants"]]

    ui._undo_last()
    assert _order(ui) == ["Hanna", DRAKE, "Tiger", "Dessie"]
    assert _char(ui, DRAKE)["hp"] == 16
    assert _turn(ui) == "Tiger"
    assert "dismisses" not in _log_text(ui)


def test_dismissing_the_summon_whose_turn_it_is_passes_it_on(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    ui._pass_turn()
    assert _turn(ui) == DRAKE
    ui._dismiss_summon(_char(ui, DRAKE))
    assert _turn(ui) == "Tiger"


# ---------------------------------------------------------------------------
# Dying with the owner


def test_a_summon_dies_with_its_owner_and_its_death_burst_goes_off(tmp_path):
    ui = _in_fight(tmp_path)
    dessie = _char(ui, "Dessie")
    _summon(ui, "Dessie")
    _hit(ui, _char(ui, "Tiger"), dessie, dessie["hp"])
    for _ in range(3):
        ui._apply_failed_death_save(dessie)
    assert ui._char_death_state(dessie) == "dead"
    assert _char(ui, REANIMATED)["hp"] == 0
    assert (
        f"{REANIMATED} drops to 0 HP: Dessie died (its Death Burst goes off)"
        in _log_text(ui)
    )


def test_a_summon_that_dies_with_its_owner_isnt_bloodied(tmp_path):
    ui = _in_fight(tmp_path)
    dessie = _char(ui, "Dessie")
    _summon(ui, "Dessie")
    reanimated = _char(ui, REANIMATED)
    _hit(ui, _char(ui, "Tiger"), reanimated, 12)
    assert "Bloodied" in reanimated["conditions"]
    _hit(ui, _char(ui, "Tiger"), dessie, dessie["hp"])
    for _ in range(3):
        ui._apply_failed_death_save(dessie)
    assert reanimated["hp"] == 0 and "Bloodied" not in reanimated["conditions"]


# ---------------------------------------------------------------------------
# From one encounter to the next


def test_a_summon_that_is_out_stays_out_into_the_next_encounter(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 6)
    ui._load_encounter(LAIR, restart=False)
    assert _names(ui) == ["Dessie", "Hanna", DRAKE, "Tiger"]
    drake = _char(ui, DRAKE)
    assert (drake["hp"], drake[CHOICE_KEY], drake[SUMMON_OF_KEY]) == (
        14,
        "Cold",
        "Hanna",
    )
    assert _can_be_seen(drake)
    assert [e["damage_types"] for e in drake["damage_immunities"]] == [["Cold"]]
    # No initiative of its own, here either.
    assert id(drake) not in ui._initiative_inputs
    # And the use stays spent: the replay counts it.
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1


def test_a_drake_that_died_stays_gone_even_after_a_long_rest(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 30)
    ui._load_encounter(LAIR, restart=False)
    assert DRAKE not in _names(ui)
    # It "remains until it is reduced to 0 hit points": the rest gives Hanna
    # her use back, but the drake has to be summoned again.
    ui.player_log_data["sessions"].append(PlayerLog.long_rest_entry())
    ui._load_encounter(LAIR, restart=False)
    assert DRAKE not in _names(ui)


def test_a_long_rest_rests_a_drake_but_ends_a_reanimated_companion(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    _summon(ui, "Dessie")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 6)
    _hit(ui, _char(ui, "Tiger"), _char(ui, REANIMATED), 6)
    ui.player_log_data["sessions"].append(PlayerLog.long_rest_entry())
    ui._load_encounter(LAIR, restart=False)
    # Still out, rested to full, with the Draconic Essence it was summoned with.
    drake = _char(ui, DRAKE)
    assert _can_be_seen(drake)
    assert (drake["hp"], drake[CHOICE_KEY]) == (20, "Cold")
    # "It lasts until you finish a Long Rest."
    assert REANIMATED not in _names(ui)


def _played_old_log(ui, tmp_path) -> Path:
    """A log played before summons had their own names, listed in the
    player log: Hanna's drake (Cold) left out at 9 HP, under the old name and
    key; Dessie's companion never summoned."""
    reanimated, drake = _old_companions()
    drake = dict(drake, hp=9, companion_choice="Cold")
    del drake["hidden_from_players"]
    path = tmp_path / "CombatLogs" / "played_before.json"
    data = {
        "encounter": "played_before",
        "players": ["Dessie", "Hanna"],
        "round_number": 1,
        "combatants": [reanimated, drake],
        "round_1": [{"text": f"Hanna summons {OLD_DRAKE} (Cold)"}],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert ui.player_log_file is not None
    ui.player_log_data["sessions"].append(
        {
            "type": PlayerLog.ENCOUNTER,
            "scenario": "played_before",
            "log": PlayerLog.log_ref(ui.player_log_file, path),
        }
    )
    return path


def test_a_summon_carries_over_from_a_log_with_the_old_name_and_key(tmp_path):
    ui = _ui(tmp_path)
    _played_old_log(ui, tmp_path)
    ui._load_encounter(LAIR, restart=False)
    assert _names(ui) == ["Dessie", "Hanna", DRAKE, "Tiger"]
    drake = _char(ui, DRAKE)
    assert (drake["hp"], drake[CHOICE_KEY], drake[SUMMON_OF_KEY]) == (
        9,
        "Cold",
        "Hanna",
    )
    assert "companion_of" not in drake and "companion_choice" not in drake
    assert drake[SOURCE_KEY] == "feature:Drake Companion"
    assert [e["damage_types"] for e in drake["damage_immunities"]] == [["Cold"]]
    # The next one finds it under its new name.
    _start(ui, Hanna=15, Dessie=5)
    _hit(ui, _char(ui, "Tiger"), drake, 4)
    ui._load_encounter(DEN, restart=False)
    assert _char(ui, DRAKE)["hp"] == 5
    assert [c["name"] for c in ui._owner_summons(_char(ui, "Hanna"))] == [DRAKE]


def test_carrying_over_into_an_old_log_reveals_its_hidden_companion(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    ui._load_encounter(OLD, restart=False)
    # No second drake beside the one the log was prepared with.
    hanna = _char(ui, "Hanna")
    (drake,) = ui._owner_summons(hanna)
    assert drake["name"] == OLD_DRAKE and _can_be_seen(drake)
    assert (drake["hp"], drake[CHOICE_KEY], drake[SUMMON_OF_KEY]) == (
        20,
        "Cold",
        "Hanna",
    )
    # Dessie's was never summoned: still hidden, so not out.
    assert _char(ui, OLD_REANIMATED)["hidden_from_players"]


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
    # An older log's choice key.
    assert carried_state({"hp": 3, "companion_choice": "Acid"})[CHOICE_KEY] == "Acid"


def test_conditions_ending_on_a_timer_or_a_save_arent_carried():
    previous = {
        "hp": 7,
        "conditions": ["Poisoned", "Frightened", "Prone"],
        "timed_conditions": [{"name": "Poisoned", "time_left": 6}],
        "repeat_saves": [{"condition": "Frightened"}],
    }
    assert carried_state(previous)["conditions"] == ["Prone"]


def test_upgrade_keys_renames_an_older_logs_keys():
    old = {"name": OLD_DRAKE, "companion_of": "Hanna", "companion_choice": "Fire"}
    assert upgrade_keys(old) == {
        "name": OLD_DRAKE,
        SUMMON_OF_KEY: "Hanna",
        CHOICE_KEY: "Fire",
    }


def test_make_room():
    hanna = _sheet(HANNA_BUILD)
    dessie = _sheet(DESSIE_BUILD)
    _, drake = _spec_of(hanna, "Drake Companion")
    _, reanimated = _spec_of(dessie, "Reanimated Companion")
    old, newer = {"name": "a"}, {"name": "b"}
    assert make_room([], drake, 1) == []
    assert make_room([old], drake, 1) == [old]
    assert make_room([], reanimated, 1) == []
    assert make_room([old], reanimated, 1) is None
    two = dataclasses.replace(drake, max_out=2)
    assert make_room([old], two, 1) == []
    assert make_room([old, newer], two, 1) == [old]
    assert make_room([old, newer], dataclasses.replace(drake, max_out=None), 5) == []


# ---------------------------------------------------------------------------
# Already summoned, and older logs


def test_already_summoned_adds_one_at_full_hp_spending_nothing(tmp_path):
    ui = _in_fight(tmp_path)
    hanna, dessie = _char(ui, "Hanna"), _char(ui, "Dessie")
    labels = [o.label for o in ui._already_summoned_options()]
    # In the window's order: Hanna (initiative 15) before Dessie (5).
    assert labels == [
        f"{DRAKE} (Acid)",
        f"{DRAKE} (Cold)",
        f"{DRAKE} (Fire)",
        f"{DRAKE} (Lightning)",
        f"{DRAKE} (Poison)",
        REANIMATED,
    ]
    ui._pass_turn()
    slots = dict(hanna["spell_slots"])
    ui._add_already_summoned(_option(ui, f"{DRAKE} (Lightning)"))
    assert _order(ui) == ["Hanna", DRAKE, "Tiger", "Dessie"]
    assert _turn(ui) == "Tiger"
    drake = _char(ui, DRAKE)
    assert (drake["hp"], drake[CHOICE_KEY]) == (20, "Lightning")
    assert _can_be_seen(drake)
    assert "Drake Companion" not in hanna.get("feature_uses_used", {})
    assert hanna["spell_slots"] == slots
    assert f"{DRAKE} joins the fight, already summoned" in _log_text(ui)
    # Dessie's, once; a second one isn't possible while it's out.
    ui._add_already_summoned(_option(ui, REANIMATED))
    ui._add_already_summoned(_option(ui, REANIMATED))
    assert [c["name"] for c in ui._owner_summons(dessie)] == [REANIMATED]
    assert "Not added" in ui._status_label.text()


def test_an_old_logs_hidden_companions_load_and_arent_out(tmp_path):
    ui = _in_fight(tmp_path, scenario=OLD)
    drake, reanimated = _char(ui, OLD_DRAKE), _char(ui, OLD_REANIMATED)
    for char, owner in ((drake, "Hanna"), (reanimated, "Dessie")):
        assert char[SUMMON_OF_KEY] == owner and "companion_of" not in char
        assert char["hidden_from_players"] and not _can_be_seen(char)
    # No rows of their own; after their owners once the fight's on.
    assert _order(ui) == ["Hanna", OLD_DRAKE, "Tiger", "Dessie", OLD_REANIMATED]
    # A hidden one isn't killed with its owner.
    dessie = _char(ui, "Dessie")
    _hit(ui, _char(ui, "Tiger"), dessie, dessie["hp"])
    for _ in range(3):
        ui._apply_failed_death_save(dessie)
    assert reanimated["hp"] == 20 and reanimated["hidden_from_players"]
    # Summoning the drake makes a new one in the hidden one's place.
    _summon(ui, "Hanna", "Acid")
    assert _order(ui) == ["Hanna", DRAKE, "Tiger", "Dessie", OLD_REANIMATED]
    assert _char(ui, DRAKE)[CHOICE_KEY] == "Acid"


@cache
def _time_loop_party() -> list:
    return Scenarios.SCENARIO_CAMPAIGNS[TIME_LOOP_LOGS[0]].players()


@pytest.mark.parametrize("name", TIME_LOOP_LOGS)
def test_the_time_loop_logs_load(tmp_path, name):
    campaign = Scenarios.SCENARIO_CAMPAIGNS[name]
    scenario = Scenarios.SCENARIOS[name]
    committed = scenario_log_path(campaign.folder / "CombatLogs", name)
    text = committed.read_text(encoding="utf-8")
    assert '"summon_of"' in text and '"companion_of"' not in text
    path = scenario_log_path(tmp_path, name)
    shutil.copyfile(committed, path)
    qapp()
    ui = CombatAppQt(
        combatants=[],
        character_sheets=_time_loop_party(),
        combat_log_dir=tmp_path,
        log_path=path,
        scenario_name=name,
        scenarios=[scenario],
    )
    ui._build_window()
    ui._open_encounter_log(path, restart=False)
    # The Square was played (Dessie summoned hers); the others weren't yet.
    assert ui.phase == ("COMBAT" if name == "time_loop_pr_square" else "INITIATIVE")
    hanna, dessie = _char(ui, "Hanna"), _char(ui, "Dessie")
    assert [c["name"] for c in ui._owner_summons(hanna)] == [OLD_DRAKE]
    assert [c["name"] for c in ui._owner_summons(dessie)] == [OLD_REANIMATED]
    # The cards' menus work out what each one is.
    assert "Dismiss" in _menu_texts(ui, _char(ui, OLD_DRAKE))
    assert "Summon Drake Companion (1 use left)" in _menu_texts(ui, hanna)
    reanimated = _char(ui, OLD_REANIMATED)
    assert _can_be_seen(reanimated) == (name == "time_loop_pr_square")
