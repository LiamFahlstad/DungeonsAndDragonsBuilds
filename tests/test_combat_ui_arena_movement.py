"""Moving on the combat window's battle map with what a creature has
(Combat/Arena/arena.py's movement_rules): standing up from Prone spends
movement on its own turn (Rules Glossary, Prone: half its Speed), and a move
can end where a rule lets it (a Swarm's space)."""

from Combat.Arena.arena import MOVED_KEY, POSITION_KEY, position, walking_speed_ft
from Combat.Arena.geometry import Cell
from Combat.Combatants import Pirate
from Combat.Monsters.CR_1.monsters import Tiger
from tests._combat_ui import make_ui


def _fight(tmp_path):
    """The Tiger (20, Speed 40) and the Pirate (10), in combat: the
    Tiger's turn."""
    ui = make_ui(tmp_path, [Tiger(), Pirate()], [])
    for char, roll in zip(ui.characters, ("20", "10")):
        ui._initiative_inputs[id(char)].setText(roll)
    ui._start_combat()
    return ui


def _named(ui, name: str) -> dict:
    return next(c for c in ui.characters if c["name"] == name)


def test_standing_up_on_its_own_turn_spends_half_its_speed(tmp_path):
    ui = _fight(tmp_path)
    tiger, pirate = _named(ui, "Tiger"), _named(ui, "Pirate")
    assert ui._current_turn_character() is tiger
    for char in (tiger, pirate):
        ui._add_condition_to(char, "Prone")
    assert walking_speed_ft(tiger) == 40

    ui._remove_condition_from(tiger, "Prone")
    assert tiger[MOVED_KEY] == 20

    pirate["speed"] = 30
    ui._remove_condition_from(pirate, "Prone")
    assert not pirate.get(MOVED_KEY), "not its turn: a correction, not a move"

    ui._undo_last()
    assert "Prone" in pirate["conditions"]
    ui._undo_last()
    assert "Prone" in tiger["conditions"]
    assert not tiger.get(MOVED_KEY), "Undo gives the movement back"


def test_a_move_can_end_in_a_swarms_space(tmp_path):
    ui = _fight(tmp_path)
    tiger, pirate = _named(ui, "Tiger"), _named(ui, "Pirate")
    tiger[POSITION_KEY] = [5, 5]
    pirate[POSITION_KEY] = [7, 5]
    ui._move_combatant(tiger, Cell(7, 5))
    assert position(tiger) == Cell(5, 5), "can't end on the Pirate"

    pirate["traits"] = [*(pirate.get("traits") or []), {"name": "Swarm"}]
    ui._move_combatant(tiger, Cell(7, 5))
    assert position(tiger) == Cell(7, 5)
