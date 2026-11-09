"""Players' summons in the combat window (Combat/Summons.py,
Combat/CombatUIQt/summons_mixin.py): Dessie's Reanimated Companion and
Hanna's Drake Companion, as the Time Loop PR campaign has them. They're made
when they're summoned (paid with the feature's use, or a spell slot, as their
SummonSpec's costs allow, and with a choice: the drake's Draconic Essence),
take their turn right after their owner's (or, rolling their own initiative,
where their roll puts them), die with their owner, can be dismissed, stay out
from one encounter to the next until a long rest (with the card they were
built with), and can join a fight already summoned. Summoning and dismissing
are logged (Action.SUMMON, Action.DISMISS), and one dismissed isn't brought
back. Older logs (a hidden companion prepared with each encounter,
"companion_of", "<owner>'s Companion (<type>)", no summon actions) still load
and carry over."""

import dataclasses
import json
import random
from functools import cache
from pathlib import Path

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

import Combat.PlayerLog as PlayerLog
from CharacterContent.Features.SubClassFeatures.Artificer.ArtificerReanimatorFeatures import (
    ReanimatedCompanion,
)
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.player_view import _can_be_seen
from Combat.Definitions import Action
from Combat.Effects.active_effects import KEY as ACTIVE_EFFECTS
from Combat.Effects.active_effects import new_effect
from Combat.EncounterLogs import prepare_log, scenario_log_path
from Combat.Monsters.CR_0.monsters import Owl
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.PlayerLog import is_round_key
from Combat.Scenario import CombatScenario
from Combat.Summons import (
    CHOICE_KEY,
    ON_ZERO_HP_KEY,
    SOURCE_KEY,
    SPEC_KEY,
    SUMMON_OF_KEY,
    VANISHED_REASON,
    SummonOption,
    SummonPayment,
    carried_state,
    cost_options,
    create,
    dismissed,
    feature_summons,
    last_seen,
    make_room,
    old_name,
    place_after_owners,
    upgrade_keys,
)
from Core.Definitions import DamageType
from Model.Content.Summons import (
    OnZeroHp,
    SummonContext,
    SummonCost,
    SummonSpec,
    SummonTurn,
)
from tests._combat_ui import answer_out_of_resources, qapp
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
CAVE = CombatScenario(name="cave", title="Cave", combatants=lambda: [Tiger()])
# Prepared as logs were before summons were made on demand: with a hidden
# companion for each player, under the old key and name.
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
    """The window for a campaign in tmp_path with DEN, LAIR, CAVE and OLD
    prepared, on the party between encounters."""
    qapp()
    sheets = {cs.character_name: cs for cs in _party()}
    logs = tmp_path / "CombatLogs"
    for scenario in (DEN, LAIR, CAVE, OLD):
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
        scenarios=[DEN, LAIR, CAVE, OLD],
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


def _submenu(menu, text: str):
    """The submenu of `menu` whose entry reads `text`."""
    (action,) = [a for a in menu.actions() if a.text() == text]
    submenu = action.menu()
    assert submenu is not None, text
    return submenu


def _events(ui, action: Action | None = None) -> list[dict]:
    """The encounter log's events, in order (only `action`'s when given)."""
    data = json.loads(_log_text(ui))
    keys = sorted((k for k in data if is_round_key(k)), key=lambda k: int(k[6:]))
    events = [e for k in keys for e in data[k]]
    return [e for e in events if action is None or e.get("action") == action]


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
    # One of hers that rolls its own initiative isn't skipped over: it isn't
    # part of her turn.
    own = {"name": "Owl", "summon_of": "Hanna", "summon_turn": "own initiative"}
    order = place_after_owners([hanna, own, tiger], [drake])
    assert [c["name"] for c in order] == ["Hanna", "Drake", "Owl", "Tiger"]


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


def test_summoning_the_drake_again_replaces_it_and_without_a_slot_asks(
    tmp_path, monkeypatch
):
    answer_out_of_resources(monkeypatch)  # Summoning again is another Action.
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
    asked = answer_out_of_resources(monkeypatch, yes=False)
    _summon(ui, "Hanna", "Poison")
    assert (_char(ui, DRAKE)["hp"], _char(ui, DRAKE)[CHOICE_KEY]) == (15, "Acid")
    assert "Drake Companion: no use of Drake Companion and no spell slot left" in (
        asked[0]
    )
    assert "out of resources" in ui._status_label.text()
    # Yes summons it unpaid: nothing more is spent.
    answer_out_of_resources(monkeypatch, yes=True)
    _summon(ui, "Hanna", "Poison")
    assert (_char(ui, DRAKE)["hp"], _char(ui, DRAKE)[CHOICE_KEY]) == (20, "Poison")
    assert hanna["spell_slots"] == {1: 0}
    assert hanna["feature_uses_used"]["Drake Companion"] == 1


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

    # The use first; a level 1 slot (their only level) pays too.
    assert summon_texts(_char(ui, "Hanna")) == [
        "Summon Drake Companion (1 use left)",
        "Summon Drake Companion using…",
    ]
    assert summon_texts(_char(ui, "Dessie")) == [
        "Summon Reanimated Companion (1 use left)",
        "Summon Reanimated Companion using…",
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


def test_a_reanimated_companion_cant_be_made_while_its_out(tmp_path, monkeypatch):
    answer_out_of_resources(
        monkeypatch
    )  # Summoning again is another Action this round.
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
    # The refused one logged nothing.
    assert [e["value"]["names"] for e in _events(ui, Action.SUMMON)] == [
        [REANIMATED],
        [f"{REANIMATED} 2"],
    ]


def test_a_slot_paid_summon_isnt_replayed_as_a_use(tmp_path, monkeypatch):
    answer_out_of_resources(
        monkeypatch
    )  # Summoning again is another Action this round.
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


def test_a_summon_made_between_encounters_joins_the_next_fight(tmp_path):
    ui = _ui(tmp_path)
    assert ui.phase == "PARTY"
    _summon(ui, "Hanna", "Cold")
    assert _names(ui) == ["Dessie", "Hanna", DRAKE] and ui.initiative_order == []
    assert len(_events(ui, Action.SUMMON)) == 1
    # Still out when the window is opened again, and in the next fight.
    assert DRAKE in _names(_ui(tmp_path))
    ui._load_encounter(LAIR, restart=False)
    assert _names(ui) == ["Dessie", "Hanna", DRAKE, "Tiger"]
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1


def test_a_summon_left_out_by_a_fight_is_there_between_encounters(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 6)
    ui._leave_encounter()
    assert _names(ui) == ["Dessie", "Hanna", DRAKE]
    assert _char(ui, DRAKE)["hp"] == 14


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
    reanimated, _ = _old_companions()
    hanna = _sheet(HANNA_BUILD)
    feature, spec = _spec_of(hanna, "Drake Companion")
    (cold,) = create(hanna, feature, spec, SummonContext(choice="Cold"), set())
    drake = dict(_old_style(cold, hidden=False), hp=9)
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
        ACTIVE_EFFECTS: [
            {**new_effect("Poisoned"), "duration": {"time_left": 6}},
            {
                **new_effect("Frightened"),
                "repeat_save": {
                    "ability": "WIS",
                    "dc": 13,
                    "mode": "Neutral",
                    "use_legendary_resistance": False,
                    "also": [],
                },
            },
        ],
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


# ---------------------------------------------------------------------------
# Paying for a summon (SummonSpec.costs)


def _drake_owner(**state) -> tuple[dict, object, object, object]:
    """(an owner dict for Hanna with `state`, her sheet, the Drake Companion
    feature, its spec)."""
    hanna = _sheet(HANNA_BUILD)
    feature, spec = _spec_of(hanna, "Drake Companion")
    owner = {"name": "Hanna", "feature_uses_used": {}, "spell_slots": {}}
    owner.update(state)
    return owner, hanna, feature, spec


def test_the_drakes_costs_are_its_use_then_any_slot_lowest_first():
    # "you can't do so again until you finish a long rest, unless you expend
    # a spell slot of 1st level or higher": the use first, then each slot.
    owner, hanna, feature, spec = _drake_owner(
        spell_slots={1: 2, 2: 1, 3: 0}, pact_slots={2: 1}
    )
    options = cost_options(owner, hanna, feature, spec)
    assert options == [
        SummonPayment(feature_use="Drake Companion", uses_left=1, own_use=True),
        SummonPayment(slot_level=1),
        SummonPayment(slot_level=2),
        SummonPayment(slot_level=2, pact=True),
    ]
    assert [o.text for o in options] == [
        "1 use left",
        "a level 1 slot",
        "a level 2 slot",
        "a level 2 Pact Magic slot",
    ]
    # The use spent: the lowest slot is the cheapest way left.
    owner["feature_uses_used"] = {"Drake Companion": 1}
    assert cost_options(owner, hanna, feature, spec)[0] == SummonPayment(slot_level=1)
    # Nothing left to pay with.
    owner.update(spell_slots={1: 0}, pact_slots={})
    assert cost_options(owner, hanna, feature, spec) == []


def test_a_cost_can_be_a_minimum_slot_another_features_use_or_nothing():
    owner, hanna, feature, spec = _drake_owner(spell_slots={1: 2, 3: 1})
    second = dataclasses.replace(spec, costs=(SummonCost(spell_slot=2),))
    assert cost_options(owner, hanna, feature, second) == [SummonPayment(slot_level=3)]
    # Favored Enemy has 2 uses at Ranger level 3; Hanna has no Wild Shape.
    other = dataclasses.replace(
        spec,
        costs=(SummonCost(feature_use="Wild Shape"), SummonCost("Favored Enemy")),
    )
    (option,) = cost_options(owner, hanna, feature, other)
    assert option == SummonPayment(feature_use="Favored Enemy", uses_left=2)
    assert option.text == "a Favored Enemy use, 2 uses left"
    free = dataclasses.replace(spec, costs=())
    assert cost_options(owner, hanna, feature, free) == [SummonPayment()]
    assert SummonPayment().text == "free"


def test_the_card_menu_pays_with_a_slot_instead_of_the_use(tmp_path):
    ui = _in_fight(tmp_path)
    hanna = _char(ui, "Hanna")
    slots = hanna["spell_slots"][1]
    using = _submenu(ui._card_menu(hanna), "Summon Drake Companion using…")
    assert [a.text() for a in using.actions()] == ["a level 1 slot"]
    cold = _submenu(using, "a level 1 slot")
    (action,) = [a for a in cold.actions() if a.text() == "Cold"]
    action.trigger()
    assert _char(ui, DRAKE)[CHOICE_KEY] == "Cold"
    assert hanna["spell_slots"][1] == slots - 1
    assert "Drake Companion" not in hanna.get("feature_uses_used", {})
    # The use is still there to pay for the next one.
    assert "Summon Drake Companion (1 use left)" in _menu_texts(ui, hanna)


def test_a_way_to_pay_thats_gone_asks_first(tmp_path, monkeypatch):
    ui = _in_fight(tmp_path)
    hanna = _char(ui, "Hanna")
    feature, spec = _spec_of(hanna["_stat_block"], "Drake Companion")
    asked = answer_out_of_resources(monkeypatch, yes=False)
    ui._summon(hanna, feature, spec, "Fire", SummonPayment(slot_level=2))
    assert DRAKE not in _names(ui)
    assert "can't pay with a level 2 slot" in asked[0]
    assert _events(ui, Action.SUMMON) == []


# ---------------------------------------------------------------------------
# Logging: Action.SUMMON and Action.DISMISS


def test_summoning_and_dismissing_are_logged_on_the_owner(tmp_path, monkeypatch):
    answer_out_of_resources(
        monkeypatch
    )  # Summoning again is another Action this round.
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")  # her use
    _summon(ui, "Hanna", "Fire")  # a level 1 slot; the Cold one goes
    ui._dismiss_summon(_char(ui, DRAKE))
    ui._add_already_summoned(_option(ui, REANIMATED))
    drake = "feature:Drake Companion"
    logged = [
        (e["action"], e["character"], e["value"])
        for e in _events(ui)
        if e.get("action") in (Action.SUMMON, Action.DISMISS)
    ]
    assert logged == [
        (
            Action.SUMMON,
            "Hanna",
            {"source": drake, "choice": "Cold", "slot": None, "names": [DRAKE]},
        ),
        (
            Action.DISMISS,
            "Hanna",
            {
                "source": drake,
                "choice": "Cold",
                "slot": None,
                "names": [DRAKE],
                "replaced": True,
            },
        ),
        (
            Action.SUMMON,
            "Hanna",
            {"source": drake, "choice": "Fire", "slot": 1, "names": [DRAKE]},
        ),
        (
            Action.DISMISS,
            "Hanna",
            {"source": drake, "choice": "Fire", "slot": 1, "names": [DRAKE]},
        ),
        (
            Action.SUMMON,
            "Dessie",
            {
                "source": "feature:Reanimated Companion",
                "choice": None,
                "slot": None,
                "names": [REANIMATED],
                "before_combat": True,
            },
        ),
    ]
    # What paid is still logged on its own, before the summon.
    actions = [
        e["action"]
        for e in _events(ui)
        if e.get("character") == "Hanna" and e.get("action")
    ]
    assert actions == [
        Action.ENABLE_FEATURE,
        Action.SUMMON,
        Action.REMOVE_SPELL_SLOT,
        Action.DISMISS,
        Action.SUMMON,
        Action.DISMISS,
    ]
    # Players read it: the summons were out when it was logged.
    assert all(e.get("public") for e in _events(ui, Action.SUMMON))


def test_undoing_a_summon_takes_its_log_line_back(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    ui._undo_last()
    assert DRAKE not in _names(ui)
    assert _events(ui, Action.SUMMON) == []
    assert _events(ui, Action.ENABLE_FEATURE) == []


def test_dismissed_reads_an_encounter_logs_dismiss_events():
    data = {
        "round_1": [
            {"text": "x", "action": "dismiss", "value": {"names": ["A", "B"]}},
            {"text": "y", "action": "summon", "value": {"names": ["C"]}},
        ],
        "round_2": [{"text": "older line"}],
        "round_number": 2,
    }
    assert dismissed(data) == {"A", "B"}
    # An older log has none.
    assert dismissed({"round_1": [{"text": "Hanna summons it"}]}) == set()


def test_last_seen_forgets_a_summon_a_later_log_dismissed():
    out = {"name": DRAKE, "hp": 12}
    dismiss = {"action": "dismiss", "value": {"names": [DRAKE]}, "text": "x"}
    first = {"combatants": [out]}
    later = {"combatants": [], "round_1": [dismiss]}
    assert last_seen(DRAKE, [(first, False)]) == (out, False)
    assert last_seen(DRAKE, [(first, False), (later, False)]) is None
    # Not in a later log, and not dismissed there: still the earlier one.
    assert last_seen(DRAKE, [(first, False), ({"combatants": []}, True)]) == (
        out,
        False,
    )
    # Dismissed, then summoned again in that log.
    again = {"name": DRAKE, "hp": 20}
    both = {"combatants": [again], "round_1": [dismiss]}
    assert last_seen(DRAKE, [(first, False), (both, False)]) == (again, False)


# ---------------------------------------------------------------------------
# Replaying the logs into the next encounter


def test_a_dismissed_summon_isnt_brought_back_from_an_earlier_encounter(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    _summon(ui, "Dessie")
    ui._load_encounter(LAIR, restart=False)
    assert DRAKE in _names(ui) and REANIMATED in _names(ui)
    _start(ui, Hanna=15, Dessie=5)
    ui._dismiss_summon(_char(ui, DRAKE))
    ui._load_encounter(CAVE, restart=False)
    # The Den left it out, but the Lair dismissed it; Dessie's is still out.
    assert DRAKE not in _names(ui)
    assert _can_be_seen(_char(ui, REANIMATED))


def test_a_summon_dismissed_and_summoned_again_is_still_out(tmp_path, monkeypatch):
    answer_out_of_resources(
        monkeypatch
    )  # Summoning again is another Action this round.
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    ui._dismiss_summon(_char(ui, DRAKE))
    _summon(ui, "Hanna", "Acid")
    ui._load_encounter(LAIR, restart=False)
    assert _char(ui, DRAKE)[CHOICE_KEY] == "Acid"


def test_a_carried_summon_keeps_its_card_until_its_summoned_again(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    # The Den's log holds the drake as it was built: here as if Hanna's
    # sheet had changed since (fewer Hit Points, a lower AC).
    assert ui.log_file is not None
    data = json.loads(_log_text(ui))
    (logged,) = [c for c in data["combatants"] if c["name"] == DRAKE]
    logged.update(hp=15, max_hp=15, ac=15)
    ui.log_file.write_text(json.dumps(data), encoding="utf-8")
    ui._load_encounter(LAIR, restart=False)
    drake = _char(ui, DRAKE)
    assert (drake["hp"], drake["max_hp"], drake["ac"]) == (15, 15, 15)
    # Summoning it again builds it from her sheet as it is now.
    _start(ui, Hanna=15, Dessie=5)
    _summon(ui, "Hanna", "Cold")
    drake = _char(ui, DRAKE)
    assert (drake["hp"], drake["max_hp"], drake["ac"]) == (20, 20, 16)


# ---------------------------------------------------------------------------
# Two summons on one owner, and a summon with its own initiative

OWL = "Hanna's Owl Familiar"


@pytest.fixture
def owl(monkeypatch):
    """Hanna's Alert feat also summons an owl that rolls its own initiative,
    for free: a stand-in for Find Familiar (2024: "It rolls its own
    Initiative and acts on its own turn"), which no feature has yet."""
    hanna = _sheet(HANNA_BUILD)
    alert = next(f for f in hanna.iter_features_with_extensions() if f.name == "Alert")
    spec = SummonSpec(
        name="Owl Familiar",
        build=lambda sheet, ctx: Owl(),
        turn=SummonTurn.OWN_INITIATIVE,
    )
    monkeypatch.setattr(alert, "summons", lambda sheet: [spec])
    return alert, spec


def _d20(monkeypatch, roll: int):
    """Every d20 rolls `roll`."""
    monkeypatch.setattr(random, "randint", lambda a, b: roll)


def test_one_owner_can_have_two_summons_out(tmp_path, owl, monkeypatch):
    answer_out_of_resources(
        monkeypatch
    )  # Summoning again is another Action this round.
    alert, spec = owl
    ui = _in_fight(tmp_path)  # Hanna 15, Tiger 10, Dessie 5
    hanna = _char(ui, "Hanna")
    _summon(ui, "Hanna", "Cold")
    _d20(monkeypatch, 2)  # 2 + the owl's Dex 13 (+1): last
    ui._summon(hanna, alert, spec, None)
    assert [c["name"] for c in ui._owner_summons(hanna)] == [DRAKE, OWL]
    assert _order(ui) == ["Hanna", DRAKE, "Tiger", "Dessie", OWL]
    owl_char = _char(ui, OWL)
    assert (owl_char["hp"], owl_char[SOURCE_KEY]) == (1, "feature:Alert")
    # Free: it spends nothing.
    assert hanna["feature_uses_used"] == {"Drake Companion": 1}
    # Each one is summoned from the owner's card; each card dismisses its own.
    texts = _menu_texts(ui, hanna)
    # Labelled by what it summons, not by the feature (Alert).
    assert "Summon Owl Familiar (free)" in texts
    assert "Summon Drake Companion (a level 1 slot)" in texts
    # Summoning the drake again replaces only the drake.
    _summon(ui, "Hanna", "Fire")
    assert [c["name"] for c in ui._owner_summons(hanna)] == [DRAKE, OWL]
    assert _char(ui, DRAKE)[CHOICE_KEY] == "Fire"
    ui._dismiss_summon(_char(ui, DRAKE))
    assert [c["name"] for c in ui._owner_summons(hanna)] == [OWL]
    # Both carry over: the owl (out) with a row of its own, the drake not.
    _summon(ui, "Hanna", "Acid")
    ui._load_encounter(LAIR, restart=False)
    assert {c["name"] for c in ui._owner_summons(_char(ui, "Hanna"))} == {DRAKE, OWL}
    assert id(_char(ui, OWL)) in ui._initiative_inputs
    assert id(_char(ui, DRAKE)) not in ui._initiative_inputs


def test_an_own_initiative_summon_rolls_with_the_monsters_before_the_fight(
    tmp_path, owl, monkeypatch
):
    ui = _ui(tmp_path)
    ui._load_encounter(DEN, restart=False)
    ui._add_already_summoned(_option(ui, OWL))
    ui._add_already_summoned(_option(ui, f"{DRAKE} (Fire)"))
    owl_char, tiger = _char(ui, OWL), _char(ui, "Tiger")
    # A row of its own; the drake goes after Hanna.
    assert id(owl_char) in ui._initiative_inputs
    assert id(_char(ui, DRAKE)) not in ui._initiative_inputs
    _d20(monkeypatch, 11)
    ui._roll_monster_initiative()
    # 11 + Dex 13's +1, and the Tiger's own; the players roll their own.
    assert ui._initiative_inputs[id(owl_char)].text() == "12"
    assert ui._initiative_inputs[id(tiger)].text()
    assert not ui._initiative_inputs[id(_char(ui, "Hanna"))].text()
    _start(ui, Hanna=15, Tiger=10, Dessie=5, **{OWL: 12})
    assert _order(ui) == ["Hanna", DRAKE, OWL, "Tiger", "Dessie"]
    assert _names(ui) == _order(ui)


def test_an_own_initiative_summon_dismissed_before_the_fight_loses_its_row(
    tmp_path, owl
):
    ui = _ui(tmp_path)
    ui._load_encounter(DEN, restart=False)
    ui._add_already_summoned(_option(ui, OWL))
    owl_char = _char(ui, OWL)
    ui._dismiss_summon(owl_char)
    assert id(owl_char) not in ui._initiative_inputs
    for unit in ui._initiative_row_units():
        ui._initiative_inputs[id(unit[0])].setText("10")
    ui._check_start_button()
    assert ui._start_combat_btn.isEnabled()
    _start(ui, Hanna=15, Tiger=10, Dessie=5)
    assert _order(ui) == ["Hanna", "Tiger", "Dessie"]


@pytest.mark.parametrize(
    "d20, order",
    [
        # 12 + 1 = 13: before the Tiger (10).
        (12, ["Hanna", OWL, "Tiger", "Dessie"]),
        # 9 + 1 = 10, a tie with the Tiger: after it.
        (9, ["Hanna", "Tiger", OWL, "Dessie"]),
        # 19 + 1 = 20: first, before Hanna (15).
        (19, [OWL, "Hanna", "Tiger", "Dessie"]),
    ],
)
def test_an_own_initiative_summon_rolls_when_summoned_in_the_fight(
    tmp_path, owl, monkeypatch, d20, order
):
    alert, spec = owl
    ui = _in_fight(tmp_path)
    ui._pass_turn()
    assert _turn(ui) == "Tiger"
    _d20(monkeypatch, d20)
    ui._summon(_char(ui, "Hanna"), alert, spec, None)
    assert _order(ui) == order
    assert _names(ui) == order
    assert _turn(ui) == "Tiger"
    (event,) = _events(ui, Action.SUMMON)
    assert event["value"]["initiative"] == {OWL: d20 + 1}
    assert f"Hanna summons {OWL} (initiative {d20 + 1})" in event["text"]


def test_an_own_initiative_summon_goes_last_when_no_roll_is_known(
    tmp_path, owl, monkeypatch
):
    """A fight continued from its log has its turn order but not the rolls,
    not even the players' from when it was started in this window."""
    alert, spec = owl
    ui = _in_fight(tmp_path)
    _hit(ui, _char(ui, "Hanna"), _char(ui, "Tiger"), 3)  # a round to continue
    ui._save_fight_state()
    assert ui.log_file is not None
    ui._load_log_from_path(str(ui.log_file))
    _d20(monkeypatch, 11)  # 12 would go before the Tiger's 10
    ui._summon(_char(ui, "Hanna"), alert, spec, None)
    assert _order(ui) == ["Hanna", "Tiger", "Dessie", OWL]


# ---------------------------------------------------------------------------
# 0 Hit Points: a drake vanishes, a Reanimated Companion's body stays


def _vanished(ui) -> list[dict]:
    """The encounter log's Action.DISMISS events for summons that vanished."""
    return [
        e
        for e in _events(ui, Action.DISMISS)
        if e["value"].get("reason") == VANISHED_REASON
    ]


def test_a_drake_at_0_hp_vanishes_and_thats_logged_on_its_owner(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    drake = _char(ui, DRAKE)
    assert drake[ON_ZERO_HP_KEY] == "vanishes"
    _hit(ui, _char(ui, "Tiger"), drake, 30)
    assert DRAKE not in _names(ui) and DRAKE not in _order(ui)
    assert ui.target_characters == []
    assert id(drake) not in ui._card_widgets
    (event,) = _vanished(ui)
    assert event["character"] == "Hanna"
    assert event["value"]["names"] == [DRAKE]
    assert event["text"].endswith(f"{DRAKE} drops to 0 HP and vanishes")
    # It doesn't fall Unconscious first, and the log's combatants don't hold it.
    assert "Unconscious" not in _log_text(ui)
    saved = json.loads(_log_text(ui))
    assert DRAKE not in [c["name"] for c in saved["combatants"]]


def test_undo_brings_a_vanished_summon_back(tmp_path):
    ui = _in_fight(tmp_path)
    ui._pass_turn()  # the Tiger's turn
    _summon(ui, "Hanna", "Cold")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 30)
    assert DRAKE not in _names(ui)
    ui._undo_last()
    assert _order(ui) == ["Hanna", DRAKE, "Tiger", "Dessie"]
    assert _char(ui, DRAKE)["hp"] == 20
    assert _turn(ui) == "Tiger"
    assert _vanished(ui) == [] and "and vanishes" not in _log_text(ui)


def test_a_summon_vanishing_on_its_own_turn_passes_the_turn_on(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    ui._pass_turn()
    assert _turn(ui) == DRAKE
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 30)
    assert _turn(ui) == "Tiger"


def test_a_reanimated_companion_at_0_hp_stays_dead(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Dessie")
    reanimated = _char(ui, REANIMATED)
    assert reanimated[ON_ZERO_HP_KEY] == "dies"
    _hit(ui, _char(ui, "Tiger"), reanimated, 30)
    assert REANIMATED in _names(ui) and REANIMATED in _order(ui)
    assert reanimated["hp"] == 0 and ui._char_death_state(reanimated) == "dead"
    assert _events(ui, Action.DISMISS) == []


def test_a_drake_vanishes_when_its_owner_dies(tmp_path):
    ui = _in_fight(tmp_path)
    hanna = _char(ui, "Hanna")
    _summon(ui, "Hanna", "Cold")
    _hit(ui, _char(ui, "Tiger"), hanna, hanna["hp"])
    for _ in range(3):
        ui._apply_failed_death_save(hanna)
    assert DRAKE not in _names(ui)
    assert f"{DRAKE} drops to 0 HP: Hanna died" in _log_text(ui)
    assert [e["value"]["names"] for e in _vanished(ui)] == [[DRAKE]]


def test_a_vanished_summon_stays_gone_when_the_log_is_continued(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 30)
    ui._load_encounter(DEN, restart=False)
    assert DRAKE not in _names(ui)
    # The player log's replay doesn't spend the use twice either.
    assert _char(ui, "Hanna")["feature_uses_used"]["Drake Companion"] == 1


def test_a_summon_that_vanished_isnt_brought_back_from_an_earlier_encounter(
    tmp_path,
):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    # Out at the end of the Den: the Lair carries it over...
    ui._load_encounter(LAIR, restart=False)
    assert DRAKE in _names(ui)
    _start(ui, Hanna=15, Dessie=5)
    _hit(ui, _char(ui, "Tiger"), _char(ui, DRAKE), 30)
    assert DRAKE not in _names(ui)
    # ...and it vanished there, so the Cave doesn't bring back the Den's.
    ui._load_encounter(CAVE, restart=False)
    assert DRAKE not in _names(ui)
    # Summoned again, it's a drake of its own, unnumbered.
    _start(ui, Hanna=15, Dessie=5)
    _summon(ui, "Hanna", "Fire")
    assert _char(ui, DRAKE)["hp"] == 20


def test_a_damage_effect_skips_its_condition_on_a_summon_that_vanished(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    drake = _char(ui, DRAKE)
    drake["hp"] = 1
    ui._deal_damage(drake, [(5, "Slashing")], _char(ui, "Tiger"), False, False)
    assert DRAKE not in _names(ui)
    assert "Unconscious" not in drake["conditions"]


# ---------------------------------------------------------------------------
# A source with two specs: entries labelled by the spec

FAMILIAR = "Hanna's Owl Familiar"
SCOUT = "Hanna's Owl Scout"


@pytest.fixture
def two_owls(monkeypatch):
    """Hanna's Alert feat summons two kinds of owl, with the same stat block:
    a familiar that vanishes at 0 HP and a scout whose body stays."""
    hanna = _sheet(HANNA_BUILD)
    alert = next(f for f in hanna.iter_features_with_extensions() if f.name == "Alert")
    familiar = SummonSpec(name="Owl Familiar", build=lambda sheet, ctx: Owl())
    scout = SummonSpec(
        name="Owl Scout", build=lambda sheet, ctx: Owl(), on_zero_hp=OnZeroHp.DIES
    )
    monkeypatch.setattr(alert, "summons", lambda sheet: [familiar, scout])
    return alert, familiar, scout


def _summon_texts(ui, char) -> list[str]:
    return [t for t in _menu_texts(ui, char) if t.startswith("Summon")]


def test_a_source_with_two_specs_gets_an_entry_for_each(tmp_path, two_owls):
    alert, familiar, scout = two_owls
    ui = _in_fight(tmp_path)
    hanna = _char(ui, "Hanna")
    texts = _summon_texts(ui, hanna)
    assert "Summon Owl Familiar (free)" in texts
    assert "Summon Owl Scout (free)" in texts
    assert not any("Alert" in t for t in texts)
    ui._summon(hanna, alert, familiar, None)
    ui._summon(hanna, alert, scout, None)
    assert {c["name"] for c in ui._owner_summons(hanna)} == {FAMILIAR, SCOUT}
    assert (_char(ui, FAMILIAR)[SPEC_KEY], _char(ui, SCOUT)[SPEC_KEY]) == (
        "Owl Familiar",
        "Owl Scout",
    )
    # Each summon finds its own spec, though both have one source and type.
    found_scout = ui._summon_source(_char(ui, SCOUT))
    found_familiar = ui._summon_source(_char(ui, FAMILIAR))
    assert found_scout is not None and found_scout[3] is scout
    assert found_familiar is not None and found_familiar[3] is familiar
    # Each summon's card offers its own spec only.
    assert _summon_texts(ui, _char(ui, SCOUT)) == ["Summon Owl Scout (free)"]
    assert _summon_texts(ui, _char(ui, FAMILIAR)) == ["Summon Owl Familiar (free)"]
    # Summoning the familiar again replaces only the familiar.
    first = _char(ui, FAMILIAR)
    ui._summon(hanna, alert, familiar, None)
    assert {c["name"] for c in ui._owner_summons(hanna)} == {FAMILIAR, SCOUT}
    assert _char(ui, FAMILIAR) is not first
    # Each follows its own spec's rule at 0 HP.
    tiger = _char(ui, "Tiger")
    _hit(ui, tiger, _char(ui, SCOUT), 5)
    _hit(ui, tiger, _char(ui, FAMILIAR), 5)
    assert [c["name"] for c in ui._owner_summons(hanna)] == [SCOUT]
    assert _char(ui, SCOUT)["hp"] == 0


def test_the_menu_labels_a_summon_by_its_spec_not_its_feature(tmp_path, monkeypatch):
    """DI-050: no "Summon Summon Wildfire Spirit", and a feature named for
    something else (Animating Performance) says what it summons."""
    hanna = _sheet(HANNA_BUILD)
    alert = next(f for f in hanna.iter_features_with_extensions() if f.name == "Alert")
    item = SummonSpec(name="Dancing Item", build=lambda sheet, ctx: Owl())
    monkeypatch.setattr(alert, "summons", lambda sheet: [item])
    ui = _in_fight(tmp_path)
    assert "Summon Dancing Item (free)" in _summon_texts(ui, _char(ui, "Hanna"))


# ---------------------------------------------------------------------------
# DI-051: an Invisible player's summon is seen as its owner is


def test_an_invisible_players_summons_attack_roll_shows_the_targets_ac(tmp_path):
    ui = _in_fight(tmp_path)
    _summon(ui, "Hanna", "Cold")
    drake = _char(ui, DRAKE)
    drake["conditions"].append("Invisible")
    tiger = _char(ui, "Tiger")
    ui._select_character(drake)
    ui._select_target_character(tiger)
    ui.attack_roll_input.setText("5")
    ui._apply_attack_roll()
    assert tiger.get("ac_above") == 5
