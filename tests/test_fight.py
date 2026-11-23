"""The fight's state lives in Combat/Fight/fight.py's Fight
(Notes/combat-ui-refactor-plan.md, step 5.2): a Fight needs no Qt, and the
combat window's attributes of the same names are its."""

from Combat.Arena.arena import ArenaSettings
from Combat.Definitions import Phase
from Combat.Fight.fight import Fight
from tests._combat_ui import make_ui


def test_a_new_fight_waits_for_initiative():
    fight = Fight()
    assert (fight.characters, fight.initiative_order) == ([], [])
    assert (fight.current_turn_idx, fight.round_number) == (0, 1)
    assert fight.phase == Phase.INITIATIVE
    assert fight.arena_settings == ArenaSettings()


def test_fights_share_nothing():
    one, two = Fight(), Fight()
    one.characters.append({"name": "Goblin"})
    assert two.characters == []


def test_the_window_reads_and_writes_its_fight(tmp_path):
    ui = make_ui(tmp_path)
    assert ui.characters is ui.fight.characters
    ui.round_number = 3
    ui.phase = Phase.COMBAT
    ui.initiative_order = list(ui.characters)
    ui.current_turn_idx = 0
    settings = ArenaSettings()
    ui.arena_settings = settings
    fight = ui.fight
    assert (fight.round_number, fight.phase) == (3, Phase.COMBAT)
    assert fight.initiative_order == ui.initiative_order
    assert fight.arena_settings is settings
