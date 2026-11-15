"""The standard actions in the combat UI (Model/Content/StandardActions.py):
the Use / Cast picker's "Standard Actions" rows for every combatant, applied
through the real dialog, and what each does afterwards in the fight.

Expected values come from the Rules Glossary (Combat > Actions): Dodge gives
Disadvantage to attack rolls against its taker (if it can see the attacker)
and Advantage on its Dexterity saves until the start of its next turn, lost
to Incapacitated or a Speed of 0; Dash is as much movement again as its
Speed this turn; Disengage means no Opportunity Attacks as it leaves reach
this turn; Help's attack assist is Advantage on the next attack roll against
that enemy; a successful Hide is the Invisible condition until, among other
things, its next attack roll; every one of them takes an Action."""

import random

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QPushButton, QTreeWidget

from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
    Y2024MonkElementsKiviJattiCharacterBuilder as Kivi,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Builds.Characters.Y2024_Rogue_Assassin_LysandraNightblade import (
    Y2024RogueAssassinLysandraNightbladeCharacterBuilder as Lysandra,
)
from Combat.Arena.arena import (
    DASHES_KEY,
    MOVED_KEY,
    POSITION_KEY,
    movement_ft,
    opportunity_attackers,
    reach_ft,
    remaining_ft,
)
from Combat.Arena.geometry import Cell
from Combat.Combatants import Tiger
from Combat.CombatUIQt.effect_options import (
    STANDARD_ACTIONS,
    effect_options,
    feature_options,
)
from Combat.CombatUIQt.saves import STANDARD_ACTION
from Combat.Effects.modifiers import attack_plan, save_plan
from Combat.PlayerCombatant import combatant_from_character
from Combat.EncounterLogs import TURN_PREFIX
from Combat.PlayerLog import is_round_key
from Model.Content.StandardActions import (
    DASH,
    DISENGAGE,
    DODGE,
    HELP,
    HIDDEN,
    STANDARD_ACTION_RULES,
)
from tests._combat_ui import make_ui, open_dialog


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """Nothing here should ask: an out-of-resources question fails the test."""
    from PyQt6.QtWidgets import QMessageBox

    def refuse(*args, **kwargs):
        raise AssertionError(f"Unexpected question: {args[1:3]}")

    monkeypatch.setattr(QMessageBox, "question", refuse)


def _fight(tmp_path, builder=Edmund):
    """The player (initiative 15) against a Tiger (10), the player's turn,
    the player the source and the Tiger the target."""
    ui = make_ui(tmp_path, [Tiger()], [builder().build()])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(player)
    ui._select_target_character(tiger)
    return ui, player, tiger


def _rows(dlg):
    tree = dlg.findChild(QTreeWidget, "effectOptions")
    return [
        tree.topLevelItem(i).child(j)
        for i in range(tree.topLevelItemCount())
        for j in range(tree.topLevelItem(i).childCount())
    ]


def _take(ui, monkeypatch, row: str):
    """Pick `row` in the Use / Cast dialog and Apply it."""
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    tree = dlg.findChild(QTreeWidget, "effectOptions")
    item = next(
        r for r in _rows(dlg) if r.data(0, Qt.ItemDataRole.UserRole).name == row
    )
    tree.setCurrentItem(item)
    next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply").click()
    return dlg


def _log(ui) -> list[str]:
    """The fight's log lines, without the "[Edmund's turn] " before them."""
    lines = []
    for key, events in ui._read_log().items():
        if is_round_key(key):
            for event in events:
                match = TURN_PREFIX.match(event["text"])
                lines.append(match.group(2) if match else event["text"])
    return lines


def _next_turn(ui):
    ui._advance_turn()


# ---------------------------------------------------------------------------
# The picker


def test_every_combatant_has_the_standard_actions_each_spending_an_action():
    for char in ({"name": "Goblin"}, combatant_from_character(Edmund().build())):
        categories = dict(effect_options(char))
        rows = categories[STANDARD_ACTIONS]
        names = [row.name for row in rows]
        assert names == [
            "Dash",
            "Disengage",
            "Dodge",
            "Help: Assist an Attack Roll",
            "Help: Assist an Ability Check",
            "Hide",
            "Influence",
            "Ready",
            "Search",
            "Study",
            "Utilize",
        ]
        assert {row.action_cost for row in rows} == {"Action"}
        assert {row.kind for row in rows} == {STANDARD_ACTION}
        # Each row's tooltip is its Rules Glossary text.
        dodge = next(row for row in rows if row.name == "Dodge")
        assert dodge.tooltip == STANDARD_ACTION_RULES[DODGE]
        help_row = next(row for row in rows if row.name.startswith("Help:"))
        assert "Assist an Attack Roll" in help_row.tooltip


def test_an_action_that_puts_nothing_on_anyone_is_logged_and_spent(
    tmp_path, monkeypatch
):
    ui, player, tiger = _fight(tmp_path)
    ui.target_characters = []
    _take(ui, monkeypatch, "Search")
    assert player["action_uses"] == {"Action": 1}
    assert f"{player['name']} takes the Search action" in _log(ui)
    assert player["conditions"] == [] or "Search" not in player["conditions"]


# ---------------------------------------------------------------------------
# Dodge


def test_dodge_gives_disadvantage_against_it_and_advantage_on_dex_saves(
    tmp_path, monkeypatch
):
    ui, player, tiger = _fight(tmp_path)
    _take(ui, monkeypatch, "Dodge")
    # It goes on the one who took it, not the target.
    assert DODGE in player["conditions"]
    assert DODGE not in tiger["conditions"]
    assert player["action_uses"] == {"Action": 1}
    assert attack_plan(tiger, player, "Neutral").mode == "Disadvantage"
    assert save_plan(player, "DEX", "Neutral").mode == "Advantage"
    assert save_plan(player, "STR", "Neutral").mode == "Neutral"


def test_dodge_isnt_counted_against_an_attacker_it_cant_see(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    _take(ui, monkeypatch, "Dodge")
    tiger["conditions"].append("Invisible")
    plan = attack_plan(tiger, player, "Neutral")
    assert plan.mode == "Neutral"
    assert any("Dodge (not counted)" in note for note in plan.notes)


def test_dodge_lasts_until_the_start_of_its_takers_next_turn(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    _take(ui, monkeypatch, "Dodge")
    _next_turn(ui)  # the Tiger's turn: still Dodging
    assert DODGE in player["conditions"]
    _next_turn(ui)  # the player's next turn starts
    assert DODGE not in player["conditions"]


def test_dodge_ends_when_its_taker_is_grappled(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    _take(ui, monkeypatch, "Dodge")
    ui._add_condition_to(player, "Grappled", source=tiger)
    assert DODGE not in player["conditions"]
    assert attack_plan(tiger, player, "Neutral").mode == "Neutral"


def test_dodge_counts_for_nothing_while_its_speed_is_0(tmp_path, monkeypatch):
    """However it got there: Dodge taken while already Restrained."""
    ui, player, tiger = _fight(tmp_path)
    player["conditions"].append("Restrained")
    _take(ui, monkeypatch, "Dodge")
    plan = attack_plan(tiger, player, "Neutral")
    # Restrained's own Advantage only, not cancelled by the Dodge.
    assert plan.mode == "Advantage"
    assert save_plan(player, "DEX", "Neutral").mode == "Disadvantage"


# ---------------------------------------------------------------------------
# Dash


def test_dash_gives_its_speed_again_on_the_map_this_turn(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    speed = movement_ft(player)
    assert speed == 30
    _take(ui, monkeypatch, "Dash")
    assert DASH in player["conditions"]
    assert player[DASHES_KEY] == 1
    assert movement_ft(player) == 60
    assert remaining_ft(player) == 60
    assert f"{player['name']} dashes: 60 ft. of movement this turn" in _log(ui)
    # A 50-foot move is within it: no warning past the Speed.
    player[POSITION_KEY] = [2, 2]
    ui._move_combatant(player, Cell(2, 12))
    assert player[MOVED_KEY] == 50
    assert "Speed" not in ui._status_label.text()
    assert any("(50 ft.; 10 of 60 ft. left this turn (Dash))" in x for x in _log(ui))
    assert remaining_ft(player) == 10
    # The Dash, and the feet moved, end as its next turn starts.
    _next_turn(ui)
    _next_turn(ui)
    assert DASH not in player["conditions"]
    assert DASHES_KEY not in player
    assert movement_ft(player) == 30


def test_a_second_dash_in_a_turn_adds_its_speed_again(tmp_path, monkeypatch):
    """The Dash action, then Cunning Action's Dash as a Bonus Action."""
    ui, rogue, tiger = _fight(tmp_path, Lysandra)
    speed = movement_ft(rogue)
    _take(ui, monkeypatch, "Dash")
    _take(ui, monkeypatch, "Cunning Action: Dash")
    assert rogue[DASHES_KEY] == 2
    assert movement_ft(rogue) == 3 * speed
    assert rogue["action_uses"] == {"Action": 1, "Bonus Action": 1}


# ---------------------------------------------------------------------------
# Disengage and Opportunity Attacks


def _side_by_side(ui, player, tiger):
    """The player at (5, 5), the Tiger next to it at (6, 5)."""
    player[POSITION_KEY] = [5, 5]
    tiger[POSITION_KEY] = [6, 5]


def test_walking_out_of_an_enemys_reach_reminds_of_its_opportunity_attack(
    tmp_path,
):
    ui, player, tiger = _fight(tmp_path)
    _side_by_side(ui, player, tiger)
    ui._move_combatant(player, Cell(2, 5))
    status = ui._status_label.text()
    assert "leaves Tiger's reach: an Opportunity Attack" in status
    assert any("leaves Tiger's reach" in line for line in _log(ui))


def test_disengage_means_no_opportunity_attack(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    _side_by_side(ui, player, tiger)
    _take(ui, monkeypatch, "Disengage")
    assert DISENGAGE in player["conditions"]
    ui._move_combatant(player, Cell(2, 5))
    assert "Disengaged: no Opportunity Attack" in ui._status_label.text()
    # It's over as the turn ends.
    _next_turn(ui)
    assert DISENGAGE not in player["conditions"]


def test_no_reminder_for_a_used_reaction_or_a_move_that_stays_in_reach(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    _side_by_side(ui, player, tiger)
    ui._move_combatant(player, Cell(6, 4))  # still next to the Tiger
    assert "Opportunity Attack" not in ui._status_label.text()
    tiger["action_uses"] = {"Reaction": 1}
    ui._move_combatant(player, Cell(1, 6))
    assert "Opportunity Attack" not in ui._status_label.text()


def test_reach_comes_from_the_stat_block():
    long_arm = {"actions": [{"description": "Melee Attack Roll: +5, reach 10 ft."}]}
    assert reach_ft(long_arm) == 10
    assert reach_ft({"actions": []}) == 5


def test_leaving_a_10_foot_reach_takes_two_cells(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    tiger["actions"] = [{"name": "Glaive", "description": "reach 10 ft."}]
    player[POSITION_KEY] = [5, 5]
    tiger[POSITION_KEY] = [7, 5]
    settings = ui.arena_settings
    player[POSITION_KEY] = [4, 5]  # 15 ft. away: out of reach
    assert opportunity_attackers(player, Cell(5, 5), ui.characters, settings) == [tiger]


# ---------------------------------------------------------------------------
# Help


def test_help_gives_the_next_attack_against_the_enemy_advantage(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    _take(ui, monkeypatch, "Help: Assist an Attack Roll")
    assert HELP in tiger["conditions"]
    assert HELP not in player["conditions"]
    # "the next attack roll by one of your allies": not the helper's own,
    # nor the Tiger's allies'.
    ally = {"name": "Clover", "_is_player": True, "conditions": []}
    tigers_friend = {"name": "Panther", "conditions": []}
    assert attack_plan(ally, tiger, "Neutral").mode == "Advantage"
    assert attack_plan(player, tiger, "Neutral").mode == "Neutral"
    assert attack_plan(tigers_friend, tiger, "Neutral").mode == "Neutral"
    ui._use_up_badges(player, tiger)
    assert HELP in tiger["conditions"]
    assert f"{player['name']} takes the Help action (Assist an Attack Roll)" in _log(ui)
    # The ally's roll uses it up.
    ui._use_up_badges(ally, tiger)
    assert HELP not in tiger["conditions"]


# ---------------------------------------------------------------------------
# Hide


def test_hide_is_hidden_and_invisible_until_its_next_attack_roll(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    _take(ui, monkeypatch, "Hide")
    assert HIDDEN in player["conditions"]
    assert "Invisible" in player["conditions"]
    assert attack_plan(player, tiger, "Neutral").mode == "Advantage"
    # Its attack roll: Hidden is used up, and the Invisible it stood for goes.
    monkeypatch.setattr(random, "randint", lambda low, high: 15)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    first_attack = next(
        r
        for r in _rows(dlg)
        if r.parent().text(0) == "Attacks" or r.parent().text(0).startswith("Attacks")
    )
    dlg.findChild(QTreeWidget, "effectOptions").setCurrentItem(first_attack)
    next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply").click()
    assert HIDDEN not in player["conditions"]
    assert "Invisible" not in player["conditions"]


def test_invisible_from_a_spell_stays_after_hidden_is_used_up(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    player["conditions"].append("Invisible")
    _take(ui, monkeypatch, "Hide")
    ui._use_up_badges(player, tiger)
    assert HIDDEN not in player["conditions"]
    assert "Invisible" in player["conditions"]


# ---------------------------------------------------------------------------
# Features that take a standard action


def test_cunning_action_has_a_bonus_action_row_for_dash_disengage_and_hide():
    rogue = combatant_from_character(Lysandra().build())
    feature = next(f for f in rogue["_feature_objects"] if f.name == "Cunning Action")
    rows = feature_options(rogue, feature)
    assert [(r.name, r.action_cost, r.condition) for r in rows] == [
        ("Cunning Action: Dash", "Bonus Action", "Dash"),
        ("Cunning Action: Disengage", "Bonus Action", "Disengage"),
        ("Cunning Action: Hide", "Bonus Action", "Hidden + Invisible"),
    ]


def test_patient_defense_gives_the_dodge_actions_badge(tmp_path, monkeypatch):
    ui, monk, tiger = _fight(tmp_path, Kivi)
    _take(ui, monkeypatch, "Patient Defense: Disengage and Dodge")
    assert DODGE in monk["conditions"]
    assert DISENGAGE in monk["conditions"]
    assert attack_plan(tiger, monk, "Neutral").mode == "Disadvantage"
    assert monk["action_uses"] == {"Bonus Action": 1}
    # Each keeps its own duration: the Disengage ends with this turn, the
    # Dodge at the start of the monk's next.
    _next_turn(ui)
    assert DISENGAGE not in monk["conditions"]
    assert DODGE in monk["conditions"]
    _next_turn(ui)
    assert DODGE not in monk["conditions"]


def test_step_of_the_wind_dashes(tmp_path, monkeypatch):
    ui, monk, tiger = _fight(tmp_path, Kivi)
    speed = movement_ft(monk)
    _take(ui, monkeypatch, "Step of the Wind: Dash")
    assert movement_ft(monk) == 2 * speed
    assert DISENGAGE not in monk["conditions"]


def test_undo_takes_a_dash_back(tmp_path, monkeypatch):
    ui, player, tiger = _fight(tmp_path)
    _take(ui, monkeypatch, "Dash")
    ui._undo_last()
    assert DASHES_KEY not in player
    assert DASH not in player["conditions"]
    assert not player.get("action_uses")


def test_a_dash_ends_with_its_badge(tmp_path, monkeypatch):
    """Taken on someone else's turn (a summon's, a Ready), it's over as that
    turn ends, not as its own next turn starts."""
    ui, player, tiger = _fight(tmp_path)
    ui._select_character(tiger)
    _take(ui, monkeypatch, "Dash")
    assert tiger[DASHES_KEY] == 1
    _next_turn(ui)  # the player's turn ends: so does the Tiger's Dash
    assert DASH not in tiger["conditions"]
    assert DASHES_KEY not in tiger
