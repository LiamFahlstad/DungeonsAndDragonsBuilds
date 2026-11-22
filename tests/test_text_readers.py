"""Every regex in the code that runs as the app does (Combat/ outside
Combat/Tools/, Model/, Presentation/, CharacterContent/, Core/, Utils/,
Builds/), with why it's there (Notes/explicit-attributes-plan.md, guard
test G, widened in 6.4).

A rule the program acts on should be a field, not read back out of rules
text at runtime. The test finds every `re.` call by the module constant or
function it's in and compares them with TEXT_READERS. A new one fails here
until it's listed; one that's gone fails until its entry goes.

Each entry says what it reads:
- "input": what the GM types ("nat 20", "2d6 + 3");
- "log": our own log or display strings;
- "validation": checks a value's form;
- "phase 5": rules text the plan's phase replaces with fields;
- "later: ...": rules text no phase covers yet, with what it reads.

AUTHORING lists whole modules that read text only where content is
written (the spell converter, generate_monsters.py, an old log's upgrade
as it loads): that's where parsing belongs, so their regexes aren't listed
one by one. Don't add a "phase" or "later" entry, or an AUTHORING module
the fight calls, for new code: give the content a field instead. In
particular, nothing new may read text in EffectText (plan step 5.1);
describe the spell or feature with combat effects."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDERS = (
    "Combat",
    "Model",
    "Presentation",
    "CharacterContent",
    "Core",
    "Utils",
    "Builds",
)
SKIPPED = ("Combat/Tools/",)

# Modules that read text only where content is written: what each reads.
AUTHORING: dict[str, str] = {
    "Model/Content/CombatAreaText.py": (
        "a spell's or feature's area, drafted into its class by the converter"
        " (Phase 3)"
    ),
    "Model/Creatures/MonsterStatText.py": (
        "a stat block's speeds, senses and spell DC, for generate_monsters.py"
        " and an old log's monster as it loads (4.1)"
    ),
    "Model/Creatures/MonsterAbilityText.py": (
        "an ability's recharge, uses, casts and turn start, for"
        " generate_monsters.py and an old log's ability as it loads (4.2)"
    ),
    "CharacterContent/Spells/SpellFactory/SpellFields.py": (
        "a scraped spell record's casting time, range, components and"
        " duration, read when it's converted into a spell class"
    ),
    "CharacterContent/Spells/SpellFactory/DataSpell.py": (
        "a scraped spell record; every spell has a class, so only the"
        " converter reads one"
    ),
    "CharacterContent/Spells/SpellClassConverter.py": "writes the spell classes",
    "CharacterContent/Spells/SpellGenerator.py": "names the spell enum's members",
}

KINDS = ("input", "log", "validation", "phase 5", "later: ")

# (file, module constant or function): what it reads.
TEXT_READERS: dict[tuple[str, str], str] = {
    # What the GM types
    ("Combat/CombatUIQt/amounts.py", "_TERM"): "input",
    ("Combat/CombatUIQt/amounts.py", "_parse_terms"): "input",
    ("Combat/CombatUIQt/attack_rolls.py", "_NATURAL"): "input",
    ("Combat/CombatUIQt/use_cast/form.py", "_NATURAL_ROLL"): "input",
    ("Combat/CombatUIQt/use_cast/form.py", "_WHOLE_NUMBER"): "input",
    ("Combat/CombatUIQt/use_cast/form.py", "DICELESS"): "input",
    ("Combat/CombatUIQt/saves.py", "_DICE"): "input",
    # The dice of a roll, typed or an effect's ("2d6 + 3"), rolled
    ("Combat/CombatUIQt/monster_actions.py", "DIE"): "input",
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
    # Card display: the level an origin label names, damage types coloured,
    # a gear label made an id.
    ("Presentation/FeatureCards.py", "_LEVEL_LABEL"): "log",
    ("Presentation/Html.py", "_DAMAGE_TYPE_PATTERN"): "log",
    ("Presentation/Html.py", "carrying_checkbox_id"): "log",
    # Validation
    ("Combat/EncounterConfig.py", "ID_PATTERN"): "validation",
    # A CombatEffect's or modifier's dice and amounts are dice.
    ("Model/Content/CombatEffect.py", "DICE"): "validation",
    ("Model/Content/CombatEffect.py", "_UPCAST_DICE"): "validation",
    ("Model/Content/CombatEffect.py", "_UPCAST_DICE_OR_NUMBER"): "validation",
    ("Model/Content/CombatModifiers.py", "BONUS_AMOUNT"): "validation",
    ("Model/Content/CombatModifiers.py", "EXTRA_DAMAGE_AMOUNT"): "validation",
    ("Model/Content/CombatModifiers.py", "HIT_POINT_AMOUNT"): "validation",
    # combat_effects.py check: a trigger's `when` that should be a field.
    ("Model/Content/CombatTriggers.py", "_FIELD_IN_WHEN"): "validation",
    # Phase 5: EffectText, an undescribed spell's or feature's text. Frozen.
    # Its damage reading, which a monster's attacks no longer use (Phase
    # 4.3: Combat/Tools/monster_effect_text.py wrote their effects).
    ("Combat/CombatUIQt/monster_actions.py", "DAMAGE"): "phase 5",
    ("Combat/CombatUIQt/monster_actions.py", "JOINED"): "phase 5",
    ("Combat/CombatUIQt/monster_actions.py", "tidy_dice"): "phase 5",
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
    for folder in FOLDERS:
        for path in sorted((ROOT / folder).rglob("*.py")):
            file = path.relative_to(ROOT).as_posix()
            if file.startswith(SKIPPED) or file in AUTHORING:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            found |= {(file, scope) for scope in _scopes_in(tree)}
    return found


def test_every_authoring_module_is_there_and_reads_text():
    """An AUTHORING entry for a module that's gone, or no longer uses a
    regex, is taken out."""
    stale = [
        file
        for file in AUTHORING
        if not (ROOT / file).exists()
        or not _scopes_in(ast.parse((ROOT / file).read_text(encoding="utf-8")))
    ]
    assert not stale, f"Take these out of AUTHORING: {stale}"


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
