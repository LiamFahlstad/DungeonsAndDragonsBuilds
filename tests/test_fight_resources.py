"""Running out of resources without the combat window
(Combat/Fight/resources.py, Combat/Fight/asker.py,
Notes/combat-ui-refactor-plan.md step 5.4): what a combatant has none left
of, and the question the fight asks the GM through its Asker, answered here
by a ScriptedAsker. One Action, one Bonus Action and one Reaction a round
(Rules Glossary: Action, Bonus Action, Reaction)."""

from Combat.Fight.asker import ScriptedAsker
from Combat.Fight.resources import action_lack, feature_lack, go_ahead_anyway


def test_one_action_of_each_kind_a_turn():
    fighter = {"name": "Fighter", "action_uses": {"Action": 1}}
    assert action_lack(fighter, "Action") == "Action: already used this turn"
    assert action_lack(fighter, "Bonus Action") is None
    assert action_lack(fighter, None) is None
    fighter["action_uses"]["Reaction"] = 1
    assert action_lack(
        fighter,
        "Reaction",
    ).startswith("Reaction: already used")


def test_a_feature_without_counted_uses_never_runs_out():
    assert feature_lack({"name": "Goblin"}, "Nimble Escape") is None


def test_nothing_missing_asks_nothing():
    asker = ScriptedAsker()
    assert go_ahead_anyway(asker, {"name": "Fighter"}, "Use Second Wind", [None])
    assert asker.asked == []


def test_the_gm_is_asked_about_what_is_missing():
    asker = ScriptedAsker(answers=[True, False])
    fighter = {"name": "Fighter"}
    lacks = [None, "Bonus Action: already used this turn"]
    assert go_ahead_anyway(asker, fighter, "Use Second Wind", lacks)
    assert not go_ahead_anyway(asker, fighter, "Use Second Wind", lacks)
    assert asker.asked[0] == (
        "Fighter",
        "Use Second Wind",
        ["Bonus Action: already used this turn"],
    )
    # Out of scripted answers, it says the default: no.
    assert not go_ahead_anyway(asker, fighter, "Dash", ["Action: already used"])
