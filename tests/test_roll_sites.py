"""Every place the combat UI rolls dice, with how that roll is made at the
table instead (Notes/combat-effects-plan.md, design principle 13, step 8.7).

The test finds every call of a dice-rolling function in Combat/CombatUIQt/
and Combat/Effects/ by the function it's in, and compares them with ROLL_SITES.
A new place that rolls fails here until it's listed, with its way to the
table; one that no longer rolls fails until its entry goes. Don't add an
entry without the way to the table: build that first (or say in the plan why
there is none, as for the free d20 roller)."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDERS = ("Combat/CombatUIQt", "Combat/Effects")

# The functions that roll dice, or roll them for their caller.
ROLLERS = {
    "randint",
    "roll_dice",
    "rolled_damage",
    "roll_bonuses",
    "_roll_d20",
    "_roll_d20_for_attack",
    "roll_save",
    "roll_attack",
    "roll_planned_attack",
    "roll_extra_damage",
    "rolled_modifiers",
    "_recharge_roll",
    "_roll_into_turn_order",
}

# (file, function, what it calls): how the roll is made at the table. A
# helper's entry says so; its callers carry the way to the table.
ROLL_SITES: dict[tuple[str, str, str], str] = {
    # The helpers
    ("monster_actions.py", "roll_dice", "randint"): "helper",
    ("saves.py", "_roll_d20", "randint"): "helper",
    ("saves.py", "roll_bonuses", "roll_dice"): "helper",
    ("saves.py", "roll_save", "randint"): "helper: typed= is the table's",
    ("saves.py", "roll_save", "_roll_d20"): "helper: typed= is the table's",
    ("saves.py", "roll_save", "roll_bonuses"): "helper: typed= is the table's",
    ("saves.py", "roll_attack", "_roll_d20"): "helper",
    ("saves.py", "roll_planned_attack", "_roll_d20"): "helper",
    ("saves.py", "roll_planned_attack", "roll_bonuses"): "helper",
    ("saves.py", "roll_extra_damage", "roll_dice"): "helper: plan.at_table",
    ("saves.py", "rolled_damage", "roll_dice"): "helper",
    ("saves.py", "read_damage", "rolled_damage"): "the Damage field: a total",
    ("saves.py", "read_hit_points", "rolled_damage"): "the Damage field: a total",
    ("turn_panel_mixin.py", "_roll_d20_for_attack", "randint"): "helper",
    ("turn_panel_mixin.py", "_recharge_roll", "randint"): "helper",
    # The Custom Effect dialog
    ("conditions_mixin.py", "_damage_preview", "rolled_damage"): "a preview only",
    (
        "conditions_mixin.py",
        "_show_custom_condition_dialog.show_typed_type",
        "rolled_damage",
    ): "a preview only",
    (
        "conditions_mixin.py",
        "_apply_effect_to_targets",
        "roll_planned_attack",
    ): "a box per target (typedAttack)",
    ("conditions_mixin.py", "_with_hit_extras", "roll_extra_damage"): (
        "a box under the target's row (typedExtra, 8.1)"
    ),
    ("conditions_mixin.py", "_roll_effect_save", "roll_save"): (
        "a box per target (typedTotal)"
    ),
    ("conditions_mixin.py", "_give_badge_modifiers", "rolled_modifiers"): (
        "the dialog's Hit Point maximum box (8.6)"
    ),
    # Turns
    ("conditions_mixin.py", "_roll_repeat_save", "roll_save"): (
        "a player's is a reminder; a monster's with monsters_roll_turn_dice off"
    ),
    ("turn_panel_mixin.py", "_start_monster_turn", "_recharge_roll"): (
        "monsters_roll_turn_dice off: a reminder, and ↺"
    ),
    ("turn_panel_mixin.py", "_give_trigger_hit_points", "roll_dice"): (
        "dice from a player's badge, or with monsters_roll_turn_dice off: a"
        " turn-column button opening the dialog (8.6)"
    ),
    ("damage_mixin.py", "_roll_concentration", "roll_save"): (
        "monsters_roll_concentration off (the default): on the card"
    ),
    # The main window
    ("turn_panel_mixin.py", "_roll_action", "_roll_d20_for_attack"): (
        "the Attack roll field, typed instead of pressing the button"
    ),
    ("turn_panel_mixin.py", "_roll_action", "roll_bonuses"): (
        "the Attack roll field, typed instead of pressing the button"
    ),
    ("turn_panel_mixin.py", "_roll_action", "roll_dice"): (
        "the Damage field it fills, changed before Enter"
    ),
    ("turn_panel_mixin.py", "_roll_action", "roll_extra_damage"): (
        "the Damage field it fills, changed before Enter"
    ),
    ("turn_panel_mixin.py", "_before_hit", "roll_dice"): (
        "the trigger pop-up's box (triggerRolled, 8.2)"
    ),
    # Initiative
    ("turns_mixin.py", "_add_initiative_row._roll", "randint"): "the row's box",
    ("turns_mixin.py", "_roll_initiative", "randint"): "the row's box",
    ("turns_mixin.py", "_roll_into_turn_order", "randint"): "helper",
    ("summons_mixin.py", "_join_fight", "_roll_into_turn_order"): (
        "the card's Set initiative... (8.4)"
    ),
    # Not a rules roll: the free d20 under the turn panel.
    ("rolls_mixin.py", "_roll_d20", "randint"): "not a rules roll",
}


def _roll_calls() -> set[tuple[str, str, str]]:
    found = set()
    for folder in FOLDERS:
        for path in sorted((ROOT / folder).glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            found |= _calls_in(tree, path.name)
    return found


def _calls_in(tree: ast.AST, file: str) -> set[tuple[str, str, str]]:
    found: set[tuple[str, str, str]] = set()
    stack: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Call(self, node):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else None
            if isinstance(func, ast.Name):
                name = func.id
            if name in ROLLERS:
                found.add((file, ".".join(stack), name))
            self.generic_visit(node)

    Visitor().visit(tree)
    return found


def test_every_roll_has_a_way_to_be_made_at_the_table():
    found = _roll_calls()
    new = sorted(found - ROLL_SITES.keys())
    assert not new, (
        "These roll dice but aren't in ROLL_SITES. Give each a way to type"
        f" the roll in (plan principle 13), then list it: {new}"
    )


def test_every_listed_roll_still_rolls():
    gone = sorted(ROLL_SITES.keys() - _roll_calls())
    assert not gone, f"These no longer roll; take them out of ROLL_SITES: {gone}"


def test_every_entry_says_how():
    assert all(how.strip() for how in ROLL_SITES.values())
