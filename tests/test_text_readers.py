"""Every regex under Combat/ (outside Combat/Tools/), with why it's there
(Notes/explicit-attributes-plan.md, guard test G).

A rule the simulator acts on should be a field, not read back out of rules
text at runtime. The test finds every `re.` call by the module constant or
function it's in and compares them with TEXT_READERS. A new one fails here
until it's listed; one that's gone fails until its entry goes.

Each entry says what it reads:
- "input": what the GM types ("nat 20", "2d6 + 3");
- "log": our own log or display strings;
- "validation": checks a value's form;
- "phase 4" / "phase 5": rules text the plan's phase replaces with fields;
- "later: ...": rules text no phase covers yet, with what it reads.

Don't add a "phase" or "later" entry for new code: give the content a
field instead. In particular, nothing new may read text in EffectText
(plan step 5.1); describe the spell or feature with combat effects."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDER = "Combat"
SKIPPED = ("Combat/Tools/",)

KINDS = ("input", "log", "validation", "phase 4", "phase 5", "later: ")

# (file, module constant or function): what it reads.
TEXT_READERS: dict[tuple[str, str], str] = {
    # What the GM types
    ("Combat/CombatUIQt/amounts.py", "_TERM"): "input",
    ("Combat/CombatUIQt/amounts.py", "_parse_terms"): "input",
    ("Combat/CombatUIQt/attack_rolls.py", "_NATURAL"): "input",
    ("Combat/CombatUIQt/conditions_mixin.py", "_NATURAL_ROLL"): "input",
    ("Combat/CombatUIQt/conditions_mixin.py", "_WHOLE_NUMBER"): "input",
    ("Combat/CombatUIQt/conditions_mixin.py", "_DICELESS"): "input",
    ("Combat/CombatUIQt/saves.py", "_DICE"): "input",
    ("Combat/CombatUIQt/trigger_prompt.py", "TriggerPrompt.choice"): "input",
    # Our own log and display strings
    ("Combat/CombatUIQt/arena_view.py", "token_label"): "log",
    ("Combat/CombatUIQt/player_view.py", "_scaled_style"): "log",
    ("Combat/CombatUIQt/public_log.py", "_ATTACK"): "log",
    ("Combat/CombatUIQt/public_log.py", "_event_lines"): "log",
    ("Combat/CombatUIQt/effect_options.py", "_without_slot_note"): "log",
    # An ability's name without its "(Recharge 5-6)", for its row's name.
    ("Combat/CombatUIQt/effect_options.py", "_NAME_ALONE"): "log",
    ("Combat/EncounterLogs.py", "TURN_PREFIX"): "log",
    # A Wild Shape form's shown senses say the Druid's Passive Perception.
    ("Combat/WildShape.py", "_PASSIVE_PERCEPTION"): "log",
    # Validation
    ("Combat/EncounterConfig.py", "ID_PATTERN"): "validation",
    # Phase 4: monster stat blocks. Freeform abilities' reach and range
    ("Combat/Arena/arena.py", "_REACH"): "phase 4",
    ("Combat/Arena/ranges.py", "_REACH"): "phase 4",
    ("Combat/Arena/ranges.py", "_RANGE"): "phase 4",
    # The condition a freeform ability's hit gives
    ("Combat/CombatUIQt/effect_options.py", "_HIT_ENDS"): "phase 4",
    ("Combat/CombatUIQt/effect_options.py", "_monster_action_condition"): "phase 4",
    # Attacks, saves, damage and riders
    ("Combat/CombatUIQt/monster_actions.py", "_ATTACK"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_SAVE"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "DAMAGE"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "JOINED"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "DIE"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_CONDITIONAL"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_JOINED_RIDER"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_IF_RIDER"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_GATES"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_PLAIN_RIDER"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_WHILE_GRAPPLED"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_RIDER_SENTENCE"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_THE_TARGETS_TURN"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "parse_action"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "_damage_rolls"): "phase 4",
    ("Combat/CombatUIQt/monster_actions.py", "tidy_dice"): "phase 4",
    # Phase 5: EffectText, an undescribed spell's or feature's text. Frozen.
    ("Combat/CombatUIQt/effect_options.py", "_UPGRADE_PARAGRAPH"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_SENTENCE_END"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_SAVE"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_NOT_THE_TARGETS_SAVE"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_FOR_CONCENTRATION"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_SAID_TO_THE_CASTER"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_ATTACK"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_HALF"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_ON_A_FAILED_SAVE"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_ON_A_HIT"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_WAITS_ON_SOMETHING"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_ANOTHER_AMOUNT"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_DAMAGE_ROLL"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_ANY_DAMAGE"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_REPEATS_THE_SAVE"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_HAS_CONDITION"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_NOT_INFLICTED"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_UPCAST"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_ONE_DAMAGE"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_ANY_UPCAST"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_CANTRIP_STEP"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_OPTION_LINE"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_UNTIL_A_TURN"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_THE_TARGETS"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_HEALS"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_HEAL_AMOUNT"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_TEMP_HP_AMOUNT"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_HEAL_UPCAST"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_TEMP_HP_UPCAST"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_JUST_YOU"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_IGNORES_COVER"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "read_effect_text"): "phase 5",
    ("Combat/CombatUIQt/effect_options.py", "_upcast_dice"): "phase 5",
    # Rules text no phase covers yet
    ("Combat/Arena/ranges.py", "_RANGED_SPELL"): (
        "later: a spell's attack is ranged (to its range), from its text"
    ),
    ("Combat/Arena/ranges.py", "_MELEE_SPELL"): (
        "later: a spell's attack is melee (5 feet), from its text"
    ),
    ("Combat/CombatUIQt/effect_options.py", "_NOT_ALWAYS"): (
        "later: a weapon's extra damage that isn't always dealt, from its note"
    ),
    ("Combat/CombatUIQt/monster_actions.py", "first_number"): (
        "later: a player's AC as a number, from the sheet's AC sentence"
    ),
    ("Combat/WildShape.py", "_MATERIAL_COST"): (
        "later: a spell's Material component costs GP, from its text"
    ),
}


def _scopes_in(tree: ast.AST) -> set[str]:
    """The module constant (`_FOO = re.compile(...)`) or the dotted
    class/function name each `re.` call is in."""
    found: set[str] = set()
    stack: list[str] = []

    class Visitor(ast.NodeVisitor):
        def _visit_named(
            self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
        ):
            stack.append(node.name)
            self.generic_visit(node)
            stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef):
            self._visit_named(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            self._visit_named(node)

        def visit_ClassDef(self, node: ast.ClassDef):
            self._visit_named(node)

        def _visit_assignment(self, node, targets):
            named = not stack and len(targets) == 1 and isinstance(targets[0], ast.Name)
            if named:
                stack.append(targets[0].id)
            self.generic_visit(node)
            if named:
                stack.pop()

        def visit_Assign(self, node):
            self._visit_assignment(node, node.targets)

        def visit_AnnAssign(self, node):
            self._visit_assignment(node, [node.target])

        def visit_Call(self, node):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "re"
                and func.attr != "escape"
            ):
                found.add(".".join(stack) or "<module>")
            self.generic_visit(node)

    Visitor().visit(tree)
    return found


def _text_readers() -> set[tuple[str, str]]:
    found = set()
    for path in sorted((ROOT / FOLDER).rglob("*.py")):
        file = path.relative_to(ROOT).as_posix()
        if file.startswith(SKIPPED):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found |= {(file, scope) for scope in _scopes_in(tree)}
    return found


def test_every_regex_is_listed():
    new = sorted(_text_readers() - TEXT_READERS.keys())
    assert not new, (
        "These use a regex but aren't in TEXT_READERS. If one reads rules"
        " text, give the content a field instead"
        f" (Notes/explicit-attributes-plan.md); otherwise list it: {new}"
    )


def test_every_listed_regex_is_still_there():
    gone = sorted(TEXT_READERS.keys() - _text_readers())
    assert not gone, f"These no longer use a regex; take them out: {gone}"


def test_every_entry_says_what_it_reads():
    bad = {
        key: kind for key, kind in TEXT_READERS.items() if not kind.startswith(KINDS)
    }
    assert not bad, f"Each entry starts with one of {KINDS}: {bad}"
