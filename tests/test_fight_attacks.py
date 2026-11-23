"""An attack roll checked against its target without the combat window
(Combat/Fight/attacks.py, Notes/combat-ui-refactor-plan.md step 5.3).

Expected values are the 2024 rules' (Rules Glossary, Attack Rolls): a total
that equals or exceeds the target's AC hits; a natural 20 always hits and
is a Critical Hit, a natural 1 always misses; and an attack roll that hits
a Paralyzed creature is a Critical Hit if the attacker is within 5 feet."""

from Combat.Arena.arena import ArenaSettings
from Combat.Fight.attack_rolls import AttackRoll
from Combat.Fight.attacks import check_attack
from Combat.Fight.fight import Fight


def _creature(name: str, at=(1, 1), **keys) -> dict:
    return {
        "name": name,
        "hp": 20,
        "max_hp": 20,
        "ac": 15,
        "conditions": [],
        "size": "Medium",
        "position": list(at),
        **keys,
    }


def test_a_total_that_meets_the_ac_hits():
    fighter, ogre = _creature("Fighter"), _creature("Ogre", (2, 1))
    fight = Fight(characters=[fighter, ogre])
    assert check_attack(fight, ogre, AttackRoll(total=15), fighter).hit is True
    assert check_attack(fight, ogre, AttackRoll(total=14), fighter).hit is False


def test_naturals_hit_and_miss_whatever_the_ac():
    fighter, ogre = _creature("Fighter"), _creature("Ogre", (2, 1), ac=30)
    fight = Fight(characters=[fighter, ogre])
    twenty = check_attack(fight, ogre, AttackRoll(natural=20), fighter)
    assert twenty.hit is True and twenty.critical
    assert check_attack(fight, ogre, AttackRoll(natural=1), fighter).hit is False


def test_no_ac_cant_be_checked():
    fighter, blob = _creature("Fighter"), _creature("Blob", (2, 1), ac=None)
    check = check_attack(
        Fight(characters=[fighter, blob]), blob, AttackRoll(total=12), fighter
    )
    assert check.hit is None and check.armor is None


def test_paralyzed_within_5_feet_is_a_critical_hit():
    fighter = _creature("Fighter")
    near = _creature("Ogre", (2, 1), conditions=["Paralyzed"])
    far = _creature("Troll", (6, 1), conditions=["Paralyzed"])
    fight = Fight(
        characters=[fighter, near, far], arena_settings=ArenaSettings(in_use=True)
    )
    assert check_attack(fight, near, AttackRoll(total=16), fighter).critical
    assert not check_attack(fight, far, AttackRoll(total=16), fighter).critical


def test_a_miss_adds_no_notes_of_a_hit():
    fighter = _creature("Fighter")
    prone = _creature("Ogre", (2, 1), conditions=["Prone"])
    fight = Fight(characters=[fighter, prone])
    notes = ("Advantage",)
    miss = check_attack(fight, prone, AttackRoll(total=3), fighter, notes)
    assert miss.notes == notes
