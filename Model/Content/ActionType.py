"""The action economy cost of using a feature. Its own module so both
Feature.py (FeatureActivation) and CombatEffect.py can use it without
importing each other; Feature.py re-exports it, so the usual import is
`from Model.Content.Feature import ActionType`."""

from enum import Enum


class ActionType(str, Enum):
    """Action economy cost to activate a feature."""

    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    # None at all: part of another action (Fleet Step's Step of the Wind,
    # right after another Bonus Action). A CombatEffect's action_type of None
    # means "its source's action", so "no action" needs a value of its own.
    NO_ACTION = "no_action"
