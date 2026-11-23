"""A combatant's health without the combat window (Combat/Fight/health.py,
Notes/combat-ui-refactor-plan.md step 5.3).

Expected values are the 2024 rules' (Rules Glossary): Death Saving Throws
(three successes make you Stable, three failures kill you), Damage at 0 Hit
Points (a failure, two from a Critical Hit, death if it's at least your Hit
Point maximum), Healing (not above the maximum; at 0 Hit Points, any
regained ends dying) and Temporary Hit Points (they don't stack)."""

from Combat.Fight.health import (
    ALIVE,
    DEAD,
    DYING,
    STABLE,
    damage_at_zero_hp,
    death_state,
    fail_death_save,
    give_temp_hp,
    regain_hit_points,
    revive,
    succeed_death_save,
)


def _player(**keys) -> dict:
    return {
        "name": "Hanna",
        "hp": 0,
        "max_hp": 28,
        "temp_hp": 0,
        "conditions": [],
        "death_saves_fail": 0,
        "death_saves_success": 0,
        "_is_player": True,
        **keys,
    }


def test_who_is_alive_dying_stable_or_dead():
    assert death_state(_player(hp=5)) == ALIVE
    assert death_state(_player()) == DYING
    assert death_state(_player(death_saves_success=3)) == STABLE
    assert death_state(_player(death_saves_fail=3)) == DEAD
    # A monster without death saves dies at 0 Hit Points.
    assert death_state({"hp": 0, "max_hp": 7}) == DEAD
    assert death_state({"hp": 0, "max_hp": 7, "death_saves": True}) == DYING


def test_three_failures_kill_and_three_successes_stabilize():
    hanna = _player(death_saves_fail=1)
    assert not fail_death_save(hanna)
    assert fail_death_save(hanna)  # the third
    assert death_state(hanna) == DEAD and hanna["stats"]["deaths"] == 1
    steady = _player(death_saves_success=2)
    assert succeed_death_save(steady) and death_state(steady) == STABLE


def test_damage_at_zero_is_a_failed_save_or_two_from_a_critical_hit():
    hanna = _player()
    hit = damage_at_zero_hp(hanna, 3, critical=False)
    assert (hit.failures, hanna["death_saves_fail"], hit.newly_dead) == (1, 1, False)
    hit = damage_at_zero_hp(hanna, 3, critical=True)
    assert (hit.failures, hanna["death_saves_fail"], hit.newly_dead) == (2, 3, True)


def test_damage_at_zero_of_the_whole_maximum_kills():
    hanna = _player()
    hit = damage_at_zero_hp(hanna, 28, critical=False)
    assert hit.massive and hit.newly_dead and death_state(hanna) == DEAD


def test_damage_ends_stable():
    hanna = _player(death_saves_success=3, death_saves_fail=2)
    hit = damage_at_zero_hp(hanna, 1, critical=False)
    # Its saves start over, with this failure.
    assert hit.ends_stable
    assert (hanna["death_saves_success"], hanna["death_saves_fail"]) == (0, 1)
    assert death_state(hanna) == DYING


def test_healing_stops_at_the_maximum_and_wakes_the_dying():
    hanna = _player(hp=25)
    assert regain_hit_points(hanna, 10, None).amount == 3
    dying = _player(death_saves_fail=2, death_saves_success=1)
    regained = regain_hit_points(dying, 4, _player(name="Cleric"))
    assert regained.came_to and dying["hp"] == 4
    assert (dying["death_saves_fail"], dying["death_saves_success"]) == (0, 0)


def test_temporary_hit_points_dont_stack():
    hanna = _player(hp=10, temp_hp=5)
    assert give_temp_hp(hanna, 3, None) == 5 and hanna["temp_hp"] == 5
    assert give_temp_hp(hanna, 8, None) == 5 and hanna["temp_hp"] == 8


def test_revived_with_one_hit_point():
    hanna = _player(death_saves_fail=3)
    revive(hanna)
    assert hanna["hp"] == 1 and death_state(hanna) == ALIVE
    assert (hanna["death_saves_fail"], hanna["death_saves_success"]) == (0, 0)
