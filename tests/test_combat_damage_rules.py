"""D&D 2024 rules in the combat UI's damage/HP pipeline (damage_mixin.py,
CardsMixin._char_death_state). Expected values come from the rules glossary:

- Hit Points: "you can't have less than 0".
- Damage and Healing: Immunity means no damage; otherwise Resistance (halve,
  round down) applies and then Vulnerability (double).
- Concentration: "If you take damage, you must succeed on a Constitution
  saving throw" - no damage, no save.
- Death Saving Throw: "A player character must make a Death Saving Throw";
  a monster dies at 0 HP unless it opts in with `death_saves=True`.
  A summon whose stat block leaves HP to its spell (max HP 0) isn't dead;
  the initiative screen asks for its HP.
"""

from functools import cache

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox, QPushButton

from Combat.Combatants import Pirate
from Combat.CombatUIQt import CombatAppQt
from Combat.Monsters.CR_0.monsters import DraconicSpirit
from Combat.Monsters.CR_1.monsters import Tiger
from Core.Definitions import DamageType
from Model.Creatures.Combatants import DamageTypeEntry
from tests._combat_ui import make_ui
from tests._snapshot_helpers import build

PLAYER_BUILD = "Y2014WarlockHexbladeDravenCursebladeCharacterBuilder"
FIRE = DamageType.FIRE.value


@cache
def _player():
    return build(PLAYER_BUILD)


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (initiative 15) attacking a 30 HP Tiger (10) in round 1, with
    a player log, which is where the structured damage values are recorded."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui.player_log_file = tmp_path / "players.json"
    ui.player_log_data = {"sessions": [{}]}
    ui._select_character(pirate)
    ui._select_target_character(tiger)
    return ui, pirate, tiger


def _damage(ui, amount: int, damage_type: str = FIRE, checked: bool = False):
    ui.damage_type_combo.setCurrentIndex(ui.damage_type_combo.findData(damage_type))
    ui.damage_input.setText(str(amount))
    if checked:
        ui._apply_damage_checked()
    else:
        ui._apply_damage()


def _heal(ui, amount: int):
    ui.heal_input.setText(str(amount))
    ui._apply_heal()


def _logged_damage(ui) -> list[dict]:
    session = ui.player_log_data["sessions"][-1]
    return [
        entry["value"]
        for key, entries in session.items()
        if key.split("_")[-1].isdigit()
        for entry in entries
        if isinstance(entry, dict) and entry.get("action") == "damage"
    ]


# ---------------------------------------------------------------------------
# 1. Hit Points never go below 0


def test_damage_past_zero_leaves_hp_at_zero(fight):
    ui, _, tiger = fight
    tiger["hp"] = 5
    _damage(ui, 15)
    assert tiger["hp"] == 0


def test_healing_from_zero_gives_the_heal_amount(fight):
    ui, _, tiger = fight
    tiger["hp"] = 5
    _damage(ui, 15)
    _heal(ui, 8)
    assert tiger["hp"] == 8


def test_logged_hp_delta_is_the_clamped_change(fight):
    ui, _, tiger = fight
    tiger["hp"] = 5
    _damage(ui, 15)
    (value,) = _logged_damage(ui)
    assert value["hp_delta"] == -5
    assert value["dmg"] == 15
    assert value["knockout"] is True

    # Replaying the logged delta onto the pre-hit state lands on 0, not -10.
    replayed = {"name": "Tiger", "hp": 5, "max_hp": 30, "temp_hp": 0, "conditions": []}
    ui._apply_replay_action(replayed, "damage", value)
    assert replayed["hp"] == 0


def test_hit_on_a_creature_already_at_zero_changes_no_hp(fight):
    ui, _, tiger = fight
    tiger["hp"] = 0
    _damage(ui, 7)
    assert tiger["hp"] == 0
    (value,) = _logged_damage(ui)
    assert value["hp_delta"] == 0
    assert value["knockout"] is False


# ---------------------------------------------------------------------------
# 2. Immunity, Resistance and Vulnerability


@pytest.mark.parametrize(
    "resist, vuln, immune, expected, outcome",
    [
        (True, True, False, 10, "resisted and vulnerable"),  # 11 // 2 * 2
        (True, False, False, 5, "resisted"),
        (False, True, False, 22, "vulnerable"),
        (False, False, True, 0, "immune"),
        (True, True, True, 0, "immune"),
        (False, False, False, 11, None),
    ],
)
def test_damage_type_modifiers(fight, resist, vuln, immune, expected, outcome):
    ui, _, tiger = fight
    fire = [DamageTypeEntry(damage_types=[DamageType.FIRE])]
    tiger["damage_resistances"] = fire if resist else []
    tiger["damage_vulnerabilities"] = fire if vuln else []
    tiger["damage_immunities"] = fire if immune else []

    assert ui._damage_type_modifier(tiger, 11, FIRE) == (expected, outcome)

    _damage(ui, 11, checked=True)
    assert tiger["hp"] == 30 - expected
    (value,) = _logged_damage(ui)
    assert value["outcome"] == outcome


def test_resist_and_vulnerable_shows_in_the_log_line(fight):
    ui, _, tiger = fight
    fire = [DamageTypeEntry(damage_types=[DamageType.FIRE])]
    tiger["damage_resistances"] = fire
    tiger["damage_vulnerabilities"] = fire
    _damage(ui, 11, checked=True)
    text = ui.log_file.read_text()
    assert "takes 10 Fire damage" in text
    assert "(resisted and vulnerable)" in text


# ---------------------------------------------------------------------------
# 3. Concentration saves only for damage taken


@pytest.fixture
def save_requests(fight, monkeypatch):
    ui, _, tiger = fight
    tiger["conditions"].append("Concentrating")
    asked: list[int] = []
    monkeypatch.setattr(
        ui, "_concentration_check_dialog", lambda char, dmg: asked.append(dmg)
    )
    return asked


def test_immune_concentrator_makes_no_save(fight, save_requests):
    ui, _, tiger = fight
    tiger["damage_immunities"] = [DamageTypeEntry(damage_types=[DamageType.FIRE])]
    _damage(ui, 10, checked=True)
    assert save_requests == []
    assert "Concentrating" in tiger["conditions"]


def test_damaged_concentrator_makes_a_save(fight, save_requests):
    ui, _, _ = fight
    _damage(ui, 10)
    assert save_requests == [10]


def test_damage_soaked_by_temp_hp_still_forces_a_save(fight, save_requests):
    ui, _, tiger = fight
    tiger["temp_hp"] = 10
    _damage(ui, 6)
    assert tiger["hp"] == 30 and tiger["temp_hp"] == 4
    assert save_requests == [6]


# ---------------------------------------------------------------------------
# 4. Who makes Death Saving Throws


def _death_buttons(ui, char) -> list[str]:
    card = ui._make_card(char)
    return [
        b.objectName()
        for b in card.findChildren(QPushButton)
        if b.objectName() in ("deathFailBtn", "deathSuccessBtn")
    ]


def test_monster_at_zero_hp_is_dead(tmp_path):
    ui = make_ui(tmp_path, [Tiger()])
    (tiger,) = ui.characters
    assert tiger["death_saves"] is False
    tiger["hp"] = 0
    assert ui._char_death_state(tiger) == "dead"
    assert _death_buttons(ui, tiger) == []


def test_plain_basic_combatant_at_zero_hp_is_dead(tmp_path):
    ui = make_ui(tmp_path, [Pirate()])
    (pirate,) = ui.characters
    pirate["hp"] = 0
    assert ui._char_death_state(pirate) == "dead"


def test_monster_opting_in_to_death_saves_is_dying(tmp_path):
    tiger_data = Tiger()
    tiger_data.death_saves = True
    ui = make_ui(tmp_path, [tiger_data])
    (tiger,) = ui.characters
    tiger["hp"] = 0
    assert ui._char_death_state(tiger) == "dying"
    assert _death_buttons(ui, tiger) == ["deathFailBtn", "deathSuccessBtn"]


def test_player_at_zero_hp_is_dying(tmp_path):
    ui = make_ui(tmp_path, [], [_player()])
    (player,) = ui.characters
    player["hp"] = 0
    assert ui._char_death_state(player) == "dying"
    assert _death_buttons(ui, player) == ["deathFailBtn", "deathSuccessBtn"]


def test_monster_killed_by_damage_takes_no_death_saves(fight):
    ui, _, tiger = fight
    _damage(ui, 40)
    assert tiger["hp"] == 0
    assert ui._char_death_state(tiger) == "dead"
    ui._apply_failed_death_save(tiger)
    assert tiger["death_saves_fail"] == 0


def test_resumed_log_without_the_key_defaults_to_no_death_saves():
    # Combat logs saved before the flag existed have no "death_saves" key.
    old = {"name": "Tiger", "hp": 0, "death_saves_fail": 0}
    assert CombatAppQt._char_death_state(old) == "dead"
    assert CombatAppQt._char_death_state({**old, "death_saves": True}) == "dying"


def test_summon_without_hp_is_not_dead(tmp_path):
    ui = make_ui(tmp_path, [DraconicSpirit()])
    (spirit,) = ui.characters
    assert (spirit["hp"], spirit["max_hp"]) == (0, 0)
    assert ui._char_death_state(spirit) == "alive"


def test_initiative_screen_asks_for_summon_hp(tmp_path):
    ui = make_ui(tmp_path, [DraconicSpirit(), Tiger()])
    spirit, tiger = ui.characters
    assert list(ui._initiative_hp_inputs) == [id(spirit)]
    ui._initiative_inputs[id(spirit)].setText("12")
    ui._initiative_inputs[id(tiger)].setText("10")
    assert not ui._start_combat_btn.isEnabled()
    for bad in ("", "abc", "0", "-5"):
        ui._initiative_hp_inputs[id(spirit)].setText(bad)
        assert not ui._start_combat_btn.isEnabled(), bad
    ui._initiative_hp_inputs[id(spirit)].setText("50")
    assert ui._start_combat_btn.isEnabled()
    ui._start_combat()
    assert (spirit["hp"], spirit["max_hp"]) == (50, 50)
    assert tiger["hp"] == tiger["max_hp"] == 30
    ui._select_character(tiger)
    ui._select_target_character(spirit)
    _damage(ui, 60)
    assert spirit["hp"] == 0
    assert ui._char_death_state(spirit) == "dead"
