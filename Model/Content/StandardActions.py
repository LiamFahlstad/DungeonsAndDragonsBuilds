"""The actions every creature can take on its turn (Rules Glossary, Combat >
Actions), in one place: each one's 2024 rules text and what taking it does in
a fight, as combat effects. The combat picker lists them for every combatant
("Standard Actions", Combat/Fight/effect_options.py), and features that
let their owner take one of them (Cunning Action's Dash, Patient Defense's
Dodge, Step of the Wind's Disengage) give the same badges, from here:
take_actions() is such a feature's row, for a Bonus Action or a Reaction.

    Dodge       a badge until the start of its next turn: attack rolls against
                it have Disadvantage (if it can see the attacker), and it has
                Advantage on Dexterity saving throws. It ends early if it's
                Incapacitated or its Speed is 0 (the combat UI ends it).
    Dash        a badge for the current turn: the battle map gives it its
                Speed again in movement, once per Dash taken.
    Disengage   a badge for the current turn: the battle map doesn't remind
                anyone of an Opportunity Attack as it leaves their reach.
    Help        a badge until the start of the helper's next turn: Advantage
                on the next attack roll against the enemy it distracts, used
                up by that roll (one of the helper's allies' only); or an
                ally's Advantage on an ability check.
    Hide        Hidden and Invisible, together, after a DC 15 Dexterity
                (Stealth) check made at the table: Advantage on its next
                attack roll, which ends both.
    Ready       a badge until the start of its next turn: its Reaction is held
                for the trigger it chose.
    Influence, Search, Study, Utilize
                nothing to put on anyone: the action is spent and logged, and
                the check is the GM's.

Attack and Magic aren't here: they are the picker's attacks and spells. The
rules text is the Rules Glossary's (SourceTexts/RulesGlossary/Combat/
Actions). Nothing here imports Combat."""

from Core.Definitions import Ability, Condition
from Model.Content.ActionType import ActionType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatEffect,
    TurnEdge,
    TurnOf,
)
from Model.Content.CombatModifiers import (
    AttacksAgainst,
    D20Mode,
    D20Test,
    Note,
    RollMode,
)

DODGE = "Dodge"
DASH = "Dash"
DISENGAGE = "Disengage"
HELP = "Help"
HIDE = "Hide"
HIDDEN = "Hidden"
READY = "Ready"
INFLUENCE = "Influence"
SEARCH = "Search"
STUDY = "Study"
UTILIZE = "Utilize"

# Each action's rules, as the Rules Glossary words them (its tables as lines).
STANDARD_ACTION_RULES: dict[str, str] = {
    DASH: (
        "When you take the Dash action, you gain extra movement for the current"
        " turn. The increase equals your Speed after applying any modifiers."
        " With a Speed of 30 feet, for example, you can move up to 60 feet on"
        " your turn if you Dash. If your Speed of 30 feet is reduced to 15"
        " feet, you can move up to 30 feet this turn if you Dash.\n"
        "If you have a special speed, such as a Fly Speed or Swim Speed, you"
        " can use that speed instead of your Speed when you take this action."
        " You choose which speed to use each time you take it."
    ),
    DISENGAGE: (
        "If you take the Disengage action, your movement doesn't provoke"
        " Opportunity Attacks for the rest of the current turn."
    ),
    DODGE: (
        "If you take the Dodge action, you gain the following benefits: until"
        " the start of your next turn, any attack roll made against you has"
        " Disadvantage if you can see the attacker, and you make Dexterity"
        " saving throws with Advantage.\n"
        "You lose these benefits if you have the Incapacitated condition or if"
        " your Speed is 0."
    ),
    HELP: (
        "When you take the Help action, you do one of the following.\n"
        "Assist an Ability Check. Choose one of your skill or tool proficiencies"
        " and one ally who is near enough for you to assist verbally or"
        " physically when they make an ability check. That ally has Advantage on"
        " the next ability check they make with the chosen skill or tool. This"
        " benefit expires if the ally doesn't use it before the start of your"
        " next turn. The DM has final say on whether your assistance is"
        " possible.\n"
        "Assist an Attack Roll. You momentarily distract an enemy within 5 feet"
        " of you, giving Advantage to the next attack roll by one of your allies"
        " against that enemy. This benefit expires at the start of your next"
        " turn."
    ),
    HIDE: (
        "With the Hide action, you try to conceal yourself. To do so, you must"
        " succeed on a DC 15 Dexterity (Stealth) check while you're Heavily"
        " Obscured or behind Three-Quarters Cover or Total Cover, and you must"
        " be out of any enemy's line of sight; if you can see a creature, you"
        " can discern whether it can see you.\n"
        "On a successful check, you have the Invisible condition while hidden."
        " Make note of your check's total, which is the DC for a creature to"
        " find you with a Wisdom (Perception) check.\n"
        "You stop being hidden immediately after any of the following occurs:"
        " you make a sound louder than a whisper, an enemy finds you, you make"
        " an attack roll, or you cast a spell with a Verbal component."
    ),
    INFLUENCE: (
        "With the Influence action, you urge a monster to do something."
        " Describe or roleplay how you're communicating with the monster. Are"
        " you trying to deceive, intimidate, amuse, or gently persuade? The DM"
        " then determines whether the monster feels willing, unwilling, or"
        " hesitant due to your interaction; this determination establishes"
        " whether an ability check is necessary, as explained below.\n"
        "Willing. If your urging aligns with the monster's desires, no ability"
        " check is necessary; the monster fulfills your request in a way it"
        " prefers.\n"
        "Unwilling. If your urging is repugnant to the monster or counter to its"
        " alignment, no ability check is necessary; it doesn't comply.\n"
        "Hesitant. If you urge the monster to do something that it is hesitant"
        " to do, you must make an ability check, which is affected by the"
        " monster's attitude: Indifferent, Friendly, or Hostile. The DM chooses"
        " the check, which has a default DC equal to 15 or the monster's"
        " Intelligence score, whichever is higher. On a successful check, the"
        " monster does as urged. On a failed check, you must wait 24 hours (or a"
        " duration set by the DM) before urging it in the same way again.\n"
        "Influence Checks: Charisma (Deception) to deceive a monster that"
        " understands you; Charisma (Intimidation) to intimidate a monster;"
        " Charisma (Performance) to amuse a monster; Charisma (Persuasion) to"
        " persuade a monster that understands you; Wisdom (Animal Handling) to"
        " gently coax a Beast or Monstrosity."
    ),
    READY: (
        "You take the Ready action to wait for a particular circumstance before"
        " you act. To do so, you take this action on your turn, which lets you"
        " act by taking a Reaction before the start of your next turn.\n"
        "First, you decide what perceivable circumstance will trigger your"
        " Reaction. Then, you choose the action you will take in response to"
        " that trigger, or you choose to move up to your Speed in response to"
        " it.\n"
        "When the trigger occurs, you can either take your Reaction right after"
        " the trigger finishes or ignore the trigger.\n"
        "When you Ready a spell, you cast it as normal (expending any resources"
        " used to cast it) but hold its energy, which you release with your"
        " Reaction when the trigger occurs. To be readied, a spell must have a"
        " casting time of an action, and holding on to the spell's magic"
        " requires Concentration, which you can maintain up to the start of"
        " your next turn. If your Concentration is broken, the spell dissipates"
        " without taking effect."
    ),
    SEARCH: (
        "When you take the Search action, you make a Wisdom check to discern"
        " something that isn't obvious.\n"
        "Search: Wisdom (Insight) for a creature's state of mind; Wisdom"
        " (Medicine) for a creature's ailment or cause of death; Wisdom"
        " (Perception) for a concealed creature or object; Wisdom (Survival)"
        " for tracks or food."
    ),
    STUDY: (
        "When you take the Study action, you make an Intelligence check to study"
        " your memory, a book, a clue, or another source of knowledge and call"
        " to mind an important piece of information about it.\n"
        "Areas of Knowledge: Intelligence (Arcana) for spells, magic items,"
        " eldritch symbols, magical traditions, planes of existence, and"
        " Aberrations, Constructs, Elementals, Fey, and Monstrosities;"
        " Intelligence (History) for historic events and people, ancient"
        " civilizations, wars, and Giants and Humanoids; Intelligence"
        " (Investigation) for traps, ciphers, riddles, and gadgetry;"
        " Intelligence (Nature) for terrain, flora, weather, and Beasts,"
        " Dragons, Oozes, and Plants; Intelligence (Religion) for deities,"
        " religious hierarchies and rites, holy symbols, cults, and Celestials,"
        " Fiends, and Undead."
    ),
    UTILIZE: (
        "You normally interact with an object while doing something else, such"
        " as when you draw a sword as part of the Attack action. When an object"
        " requires an action for its use, you take the Utilize action."
    ),
}

_UNTIL_ITS_NEXT_TURN = (TurnEdge.START, TurnOf.SOURCE)
_THIS_TURN = (TurnEdge.END, TurnOf.CURRENT)


def dodge_condition() -> CombatCondition:
    """The Dodge action's badge, on the creature that took it."""
    return CombatCondition(
        DODGE,
        until=_UNTIL_ITS_NEXT_TURN,
        modifiers=(
            AttacksAgainst(RollMode.DISADVANTAGE, seen_attacker=True),
            D20Mode((D20Test.SAVING_THROW,), RollMode.ADVANTAGE, (Ability.DEXTERITY,)),
            Note(
                "It ends early if it has the Incapacitated condition or its Speed is 0."
            ),
        ),
    )


def dash_condition() -> CombatCondition:
    """The Dash action's badge, for the current turn: the battle map counts
    each Dash taken as its Speed again in movement."""
    return CombatCondition(
        DASH,
        until=_THIS_TURN,
        modifiers=(
            Note("Extra movement this turn, equal to its Speed, for each Dash taken."),
        ),
    )


def disengage_condition() -> CombatCondition:
    """The Disengage action's badge, for the current turn."""
    return CombatCondition(
        DISENGAGE,
        until=_THIS_TURN,
        modifiers=(
            Note("Its movement doesn't provoke Opportunity Attacks this turn."),
        ),
    )


def hidden_conditions() -> tuple[CombatCondition, ...]:
    """A successful Hide: the Hidden badge and the Invisible condition it
    stands for. Its next attack roll has Advantage and ends both."""
    return (
        CombatCondition(
            HIDDEN,
            modifiers=(
                D20Mode((D20Test.ATTACK_ROLL,), RollMode.ADVANTAGE, once=True),
                Note(
                    "It stops being hidden after it makes a sound louder than a"
                    " whisper, an enemy finds it, it makes an attack roll, or it"
                    " casts a spell with a Verbal component."
                ),
            ),
        ),
        CombatCondition(Condition.INVISIBLE),
    )


def _action(
    name: str,
    action_type: ActionType,
    *conditions: CombatCondition,
    row: str = "",
    targets_self: bool = True,
    notes: tuple[str, ...] = (),
) -> CombatEffect:
    return CombatEffect(
        name=row or name,
        conditions=conditions,
        targets_self=targets_self,
        action_type=action_type,
        notes=notes,
    )


def dash(action_type: ActionType = ActionType.ACTION) -> CombatEffect:
    return _action(DASH, action_type, dash_condition())


def disengage(action_type: ActionType = ActionType.ACTION) -> CombatEffect:
    return _action(DISENGAGE, action_type, disengage_condition())


def dodge(action_type: ActionType = ActionType.ACTION) -> CombatEffect:
    return _action(DODGE, action_type, dodge_condition())


_HIDE_NOTE = (
    "Apply it only on a DC 15 Dexterity (Stealth) check, made while"
    " Heavily Obscured or behind Three-Quarters or Total Cover and out"
    " of any enemy's line of sight. The check's total is the DC to find"
    " it (Wisdom (Perception)). On a failure, log the action spent alone."
)


def hide(action_type: ActionType = ActionType.ACTION) -> CombatEffect:
    return _action(HIDE, action_type, *hidden_conditions(), notes=(_HIDE_NOTE,))


# The badges taking each of these actions gives its taker.
_BADGES_OF = {
    DASH: lambda: (dash_condition(),),
    DISENGAGE: lambda: (disengage_condition(),),
    DODGE: lambda: (dodge_condition(),),
    HIDE: hidden_conditions,
}


def take_actions(
    row: str,
    *actions: str,
    action_type: ActionType | None = None,
    notes: tuple[str, ...] = (),
    **fields,
) -> CombatEffect:
    """A feature's row for taking one or more of the Dash, Disengage, Dodge
    and Hide actions some other way than with an Action: a Bonus Action
    (Cunning Action, Timely Retreat), a Reaction (Elusive Brawler's Reactive
    Dodge) or as part of something else (no action_type: the feature's own
    cost, or none). Its user gets each action's own badges, which the fight
    counts as if it took the action itself (a Dash's movement, a Disengage's
    missing Opportunity Attack reminders, a Dodge's Disadvantage).

    `fields` are any other CombatEffect fields (temp_hp, ends_conditions,
    spends_use, trigger...). The badges that end with a turn come first, as
    the form gives every badge the first's duration and lets the others
    keep their own."""
    unknown = [a for a in actions if a not in _BADGES_OF]
    if unknown or not actions:
        raise ValueError(f"take_actions takes {', '.join(_BADGES_OF)}, got {actions!r}")
    conditions = [c for a in actions for c in _BADGES_OF[a]()]
    conditions.sort(key=lambda c: c.until is None)  # stable: the order given
    if HIDE in actions:
        notes = (*notes, _HIDE_NOTE)
    return CombatEffect(
        name=row,
        conditions=tuple(conditions),
        targets_self=True,
        action_type=action_type,
        notes=tuple(notes),
        **fields,
    )


def help_attack() -> CombatEffect:
    """Help's Assist an Attack Roll: on the enemy distracted."""
    return _action(
        HELP,
        ActionType.ACTION,
        CombatCondition(
            HELP,
            until=_UNTIL_ITS_NEXT_TURN,
            modifiers=(AttacksAgainst(RollMode.ADVANTAGE, by_allies=True, once=True),),
        ),
        row="Help: Assist an Attack Roll",
        targets_self=False,
        notes=("Target the enemy, within 5 feet of the helper.",),
    )


def help_check() -> CombatEffect:
    """Help's Assist an Ability Check: on the ally helped."""
    return _action(
        HELP,
        ActionType.ACTION,
        CombatCondition(
            HELP,
            until=_UNTIL_ITS_NEXT_TURN,
            modifiers=(
                D20Mode(
                    (D20Test.ABILITY_CHECK,),
                    RollMode.ADVANTAGE,
                    when="it uses the skill or tool the helper chose",
                ),
                Note("For its next ability check with that skill or tool."),
            ),
        ),
        row="Help: Assist an Ability Check",
        targets_self=False,
        notes=(
            "Target the ally; choose one of the helper's skill or tool proficiencies.",
        ),
    )


def ready() -> CombatEffect:
    return _action(
        READY,
        ActionType.ACTION,
        CombatCondition(
            READY,
            until=_UNTIL_ITS_NEXT_TURN,
            modifiers=(
                Note(
                    "It holds its Reaction for the trigger it chose: an action,"
                    " or a move up to its Speed. A readied spell is cast now and"
                    " held with Concentration."
                ),
            ),
        ),
        notes=(
            "Name the trigger and the response in the dialog's notes. A readied"
            " spell is cast now: cast it too, holding Concentration.",
        ),
    )


def _check(name: str, note: str) -> CombatEffect:
    return _action(name, ActionType.ACTION, notes=(note,))


def standard_action_effects() -> list[CombatEffect]:
    """Every standard action besides Attack and Magic, as the picker lists
    them, each spending an Action."""
    return [
        dash(),
        disengage(),
        dodge(),
        help_attack(),
        help_check(),
        hide(),
        _check(
            INFLUENCE,
            "Roll the check at the table: DC 15 or the monster's Intelligence"
            " score, whichever is higher.",
        ),
        ready(),
        _check(SEARCH, "Roll the Wisdom check at the table."),
        _check(STUDY, "Roll the Intelligence check at the table."),
        _check(UTILIZE, "Using an object that takes an action."),
    ]


def standard_action_rules(row: str) -> str:
    """The rules text of a standard action's row ("Help: Assist an Attack
    Roll" is Help's)."""
    return STANDARD_ACTION_RULES[row.split(":")[0]]
