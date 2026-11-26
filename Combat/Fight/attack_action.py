"""The Attack action's attacks and the actions a feature gives back, with no
Qt (Notes/combat-effects-plan.md, step 9.3, Q69's suggestion as Decision 22).

The simulator doesn't run the action economy: the GM does (principle 8). It
only fills in what's known. Extra Attack: "You can attack twice instead of
once whenever you take the Attack action on your turn" (three times with Two
Extra Attacks, four with Three): a weapon's row opens with Times at that
many while its owner's Action is unspent this turn, the first of the Attack
action's attacks, and at 1 after, as each further one costs nothing
(effect_options._weapon_option). The GM can still change it. Action Surge:
"On your turn, you can take one additional action": using it gives back the
turn's Action (Feature.gives_actions), so the next weapon row costs it and
opens with every attack again.
"""

from Combat.Definitions import ActionCost
from Combat.Effects.always_on import features_of

from .logger import Logger


def attacks_per_attack_action(char: dict) -> int:
    """How many attacks char makes when it takes the Attack action: the most
    any of its features gives (Feature.attacks_per_attack_action), else 1."""
    sheet = char.get("_stat_block")
    counts = [
        count
        for feature in features_of(char)
        if (count := _attacks(feature, sheet)) is not None
    ]
    return max(counts, default=1)


def _attacks(feature, sheet) -> int | None:
    hook = getattr(feature, "attacks_per_attack_action", None)
    return hook(sheet) if hook is not None else None


def has_acted(char: dict) -> bool:
    """Whether char has used its Action this turn."""
    return char.get("action_uses", {}).get(ActionCost.ACTION, 0) > 0


def attack_action_cost(char: dict) -> dict:
    """A weapon row's cost and Times: the Action and every attack of the
    Attack action while char hasn't used its Action this turn, else nothing
    and one more attack (EffectOption's action_cost, instances)."""
    if has_acted(char):
        return {"action_cost": None, "instances": 1}
    return {
        "action_cost": ActionCost.ACTION,
        "instances": attacks_per_attack_action(char),
    }


def give_back_actions(logger: Logger, char: dict, feature_name: str) -> None:
    """Give char back the actions its feature `feature_name` gives as it's
    used (Action Surge: one more Action this turn), and log it. One not used
    yet this turn is owed: the count goes below 0, and the next use takes it
    back to 0, so the turn's tally still resets as it starts."""
    feature = next(
        (f for f in features_of(char) if f.name == feature_name),
        None,
    )
    counts = char.setdefault("action_uses", {})
    for action in getattr(feature, "gives_actions", ()):
        counts[action] = counts.get(action, 0) - 1
        logger.log(
            f"{char['name']} gets another {action} this turn ({feature_name})",
            character=char["name"],
        )
