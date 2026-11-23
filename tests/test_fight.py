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


# ---- The battle map's questions (step 5.3): only once the map is in use ----

from Combat.Arena.cover import NO_COVER_READING  # noqa: E402
from Combat.Effects.sight import UNKNOWN  # noqa: E402


def _on_map(name: str, at: tuple[int, int], **keys) -> dict:
    return {
        "name": name,
        "hp": 10,
        "max_hp": 10,
        "conditions": [],
        "size": "Medium",
        "position": list(at),
        **keys,
    }


def test_before_the_map_is_in_use_it_says_nothing():
    fighter, ogre = _on_map("Fighter", (1, 1)), _on_map("Ogre", (2, 1))
    fight = Fight(characters=[fighter, ogre])
    assert fight.distance_ft(fighter, ogre) is None
    assert fight.sees(fighter, ogre) == UNKNOWN
    assert fight.map_cover(fighter, ogre) == NO_COVER_READING
    # No cover from the map: the target reads as it is.
    assert fight.covered(fighter, ogre) == ogre


def test_distances_count_once_the_map_is_in_use():
    fighter, ogre = _on_map("Fighter", (1, 1)), _on_map("Ogre", (4, 1))
    fight = Fight(characters=[fighter, ogre], arena_settings=ArenaSettings(in_use=True))
    assert fight.distance_ft(fighter, ogre) == 15
    assert fight.distance_ft(fighter, fighter) is None


def test_a_hit_on_the_paralyzed_from_within_5_feet_is_critical():
    # Rules Glossary, Paralyzed: an attack roll that hits it is a Critical
    # Hit if the attacker is within 5 feet.
    fighter = _on_map("Fighter", (1, 1))
    near = _on_map("Ogre", (2, 1), conditions=["Paralyzed"])
    far = _on_map("Troll", (6, 1), conditions=["Paralyzed"])
    fight = Fight(
        characters=[fighter, near, far], arena_settings=ArenaSettings(in_use=True)
    )
    assert fight.critical_against(fighter, near)
    assert not fight.critical_against(fighter, far)
    assert not fight.critical_against(fighter, None)
