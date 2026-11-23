"""Spending a resource without the combat window (Combat/Fight/resources.py,
Combat/Fight/spells.py, logged through Combat/Fight/logger.py's Logger,
Notes/combat-ui-refactor-plan.md step 5.4): each use is counted and logged
with the action the party's replay reads, so the next run spends it too."""

from Combat.Definitions import Action
from Combat.Fight.log import apply_replay_action
from Combat.Fight.logger import RecordingLogger
from Combat.Fight.resources import count_feature_use, use_action
from Combat.Fight.spells import use_slot


def test_an_action_used_is_counted_for_the_turn_and_logged():
    logger = RecordingLogger()
    fighter = {"name": "Fighter"}
    use_action(logger, fighter, "Bonus Action")
    assert fighter["action_uses"] == {"Bonus Action": 1}
    assert logger.texts == ["Fighter uses Bonus Action"]
    assert logger.lines[0].character == "Fighter"


def test_a_feature_use_is_logged_for_the_replay():
    logger = RecordingLogger()
    monk: dict = {"name": "Monk"}
    count_feature_use(logger, monk, "Focus Points", counts_uses=True, count=2)
    assert monk["feature_uses_used"] == {"Focus Points": 2}
    assert monk["stats"]["features_enabled"] == 1
    (line,) = logger.lines
    assert line.text == "Monk uses Focus Points (2 uses)"
    assert line.action == Action.ENABLE_FEATURE
    # The replay of that line spends the same on a fresh Monk.
    fresh: dict = {"name": "Monk", "_feature_objects": []}
    apply_replay_action(fresh, line.action, line.value)
    assert fresh["stats"]["features_enabled"] == 1


def test_a_slot_used_is_logged_and_none_left_logs_nothing():
    logger = RecordingLogger()
    warlock = {"name": "Warlock", "spell_slots": {}, "pact_slots": {2: 1}}
    spent = use_slot(logger, warlock, 2)
    assert spent is not None and spent.pact
    (line,) = logger.lines
    assert line.text == "Warlock uses a Level 2 Pact Magic slot"
    assert (line.action, line.value) == (Action.REMOVE_PACT_SLOT, 2)
    assert use_slot(logger, warlock, 2) is None
    assert len(logger.lines) == 1
