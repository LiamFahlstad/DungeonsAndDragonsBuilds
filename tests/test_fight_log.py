"""The fight and its logs without the combat window (Combat/Fight/log.py,
Notes/combat-ui-refactor-plan.md step 5.3): what an encounter log saves of
a fight, a log's combatants taken back into one, a saved fight continued on
the turn it stopped at, and the party replayed from recorded actions (with
Bloodied kept in step silently, Rules Glossary: Bloodied)."""

from Combat.Arena.arena import ArenaSettings
from Combat.Definitions import Action, Phase
from Combat.EncounterLogs import (
    ARENA_KEY,
    ORDER_KEY,
    PLAYER_FIGHT_STATE_KEY,
    TURN_KEY,
)
from Combat.Fight.fight import INITIATIVE_KEY, Fight
from Combat.Fight.health import bloodied_change, resync_bloodied
from Combat.Fight.log import (
    apply_replay_action,
    continue_fight,
    record_fight,
    replay_player_log,
    saved_map,
    saved_initiative_order,
    slots_by_level,
    take_combatants_from,
)


def _c(name: str, hp: int = 10, **keys) -> dict:
    return {"name": name, "hp": hp, "max_hp": 10, "conditions": [], **keys}


def _player(name: str, hp: int = 10, **keys) -> dict:
    return _c(name, hp, _is_player=True, temp_hp=0, **keys)


def test_a_log_saves_the_turn_order_by_name_and_no_underscore_keys():
    hero, goblin = _player("Hero"), _c("Goblin", _initiative=12)
    fight = Fight(
        characters=[goblin, hero],
        initiative_order=[goblin, hero],
        current_turn_idx=1,
        round_number=3,
        phase=Phase.COMBAT,
    )
    data: dict = {}
    record_fight(fight, data)
    assert data["round_number"] == 3
    assert (data[ORDER_KEY], data[TURN_KEY]) == (["Goblin", "Hero"], "Hero")
    assert ARENA_KEY in data
    # Players aren't in "combatants"; the "_" keys aren't saved.
    assert data["combatants"] == [{k: v for k, v in goblin.items() if k[0] != "_"}]
    assert PLAYER_FIGHT_STATE_KEY not in data


def test_before_the_fight_a_log_saves_no_turn_order():
    data: dict = {ORDER_KEY: ["Old"]}
    record_fight(Fight(characters=[_c("Goblin")]), data)
    assert data[ORDER_KEY] == ["Old"] and TURN_KEY not in data


def test_a_logs_combatants_join_the_players_with_their_slots_by_level():
    hero = _player("Hero", spell_slots={1: 2}, _initiative=15)
    fight = Fight(characters=[hero, _c("Someone gone")])
    goblin = _c("Goblin", spell_slots={"1": 3})
    take_combatants_from(
        fight,
        {
            "combatants": [goblin],
            PLAYER_FIGHT_STATE_KEY: {"Hero": {"active_spells": [{"name": "Bless"}]}},
        },
    )
    assert fight.characters == [hero, goblin]
    assert goblin["spell_slots"] == {1: 3}
    assert INITIATIVE_KEY not in hero
    assert hero["active_spells"] == [{"name": "Bless"}]
    assert goblin["stats"]["damage_dealt"] == 0


def test_a_saved_fight_continues_on_the_turn_it_stopped_at():
    a, b, c = _player("A"), _c("B"), _c("C")
    fight = Fight(characters=[a, b, c])
    continue_fight(fight, {ORDER_KEY: ["C", "A"], TURN_KEY: "A"})
    assert fight.phase == Phase.COMBAT
    # B isn't named in the saved order: it goes last.
    assert fight.characters == [c, a, b] and fight.initiative_order == [c, a, b]
    assert fight.current_turn_idx == 1


def test_saved_order_and_map_of_an_older_log():
    a, b = _c("A"), _c("B")
    assert saved_initiative_order([a, b], {}) == [a, b]
    assert saved_map({}) is None
    settings = ArenaSettings()
    assert isinstance(saved_map({ARENA_KEY: settings.to_dict()}), ArenaSettings)
    assert slots_by_level({"2": 1}) == {2: 1} and slots_by_level(None) == {}


def test_bloodied_follows_hit_points_silently():
    hero = _player("Hero", hp=5)
    assert bloodied_change(hero) is True
    resync_bloodied(hero)
    assert hero["conditions"] == ["Bloodied"] and "stats" not in hero
    assert bloodied_change(hero) is None
    hero["hp"] = 6  # above half its Hit Point maximum
    resync_bloodied(hero)
    assert hero["conditions"] == []
    # At 0 Hit Points the code takes Bloodied off, which the rule doesn't
    # ("half its Hit Points or fewer"): DI-007, left as it is by step 5.


def test_replayed_damage_counts_for_both_and_bloodies():
    hero, cleric = _player("Hero"), _player("Cleric")
    damage = {"hp_delta": -6, "temp_delta": 0, "dmg": 6, "source_name": "Cleric"}
    session = {"round_1": [{"character": "Hero", "action": "damage", "value": damage}]}
    replay_player_log([hero, cleric, _c("Goblin")], [session])
    assert hero["hp"] == 4 and "Bloodied" in hero["conditions"]
    assert hero["stats"]["damage_taken"] == 6
    assert cleric["stats"]["damage_dealt"] == 6


def test_a_replayed_heal_brings_a_downed_player_to():
    hero = _player("Hero", hp=0, death_saves_fail=2, death_saves_success=1)
    apply_replay_action(hero, Action.HEAL, {"heal": 3})
    assert hero["hp"] == 3
    assert (hero["death_saves_fail"], hero["death_saves_success"]) == (0, 0)
    assert hero["stats"]["healing_received"] == 3


def test_a_replayed_slot_spent_is_counted():
    wizard = _player("Wizard", spell_slots={1: 2})
    apply_replay_action(wizard, Action.REMOVE_SPELL_SLOT, 1)
    assert wizard["spell_slots"] == {1: 1}
    assert wizard["stats"]["spell_slots_used"] == 1
