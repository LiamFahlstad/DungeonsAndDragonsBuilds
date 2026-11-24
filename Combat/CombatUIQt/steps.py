"""Running one of the fight's Qt-free operations from the combat window
(Notes/combat-ui-refactor-plan.md, R34): give it a Step with the window's
Logger and Asker, then show the StepResult it filled in (Combat/Fight/step.py).

The window's methods of the operations' names (ConditionsMixin's
_add_condition_to, ...) are wrappers that do just this, so the tests and the
rest of the window call them as before."""

from collections.abc import Callable
from typing import Concatenate, ParamSpec, TypeVar

from Combat.Definitions import ActionCost
from Combat.Effects.triggers import OpportunityAttack
from Combat.Fight.step import Step, StepResult

from .state import CombatWindowState

P = ParamSpec("P")
R = TypeVar("R")


def run_step(
    app: CombatWindowState,
    operation: Callable[Concatenate[Step, P], R],
    *args: P.args,
    **kwargs: P.kwargs,
) -> R:
    """operation(step, *args, **kwargs) on app's fight, then what it left
    for the window shown (show_step). Returns what the operation returns."""
    step = Step(app.fight, app.logger, app.asker)
    value = operation(step, *args, **kwargs)
    show_step(app, step.result)
    return value


def show_step(app: CombatWindowState, result: StepResult):
    """Redraw the cards of who changed, say the status, take away a spent
    Reaction's Opportunity Attack buttons (arena step 23), save the fight
    state and bring the views up to date, as the operation asked."""
    for char in result.removed:
        app._forget_removed(char)
    if result.all_cards:
        app._rebuild_cards()
    else:
        for char in result.changed:
            app._rebuild_card(char)
    for text in result.status:
        app._show_status(text)
    for char, action_type in result.spent:
        if action_type != ActionCost.REACTION:
            continue
        left = tuple(
            p
            for p in app._hit_prompts
            if not (isinstance(p, OpportunityAttack) and p.attacker is char)
        )
        if len(left) != len(app._hit_prompts):
            app._hit_prompts = left
            app._refresh_turn_prompts()
    if result.spent:
        app._refresh_selected_card()
    if result.save:
        app._write_log(app._read_log())
    elif result.save_begun:
        app._save_fight_state()
    if result.turn:
        app._refresh_turn()
    if result.views:
        app._refresh_views()
