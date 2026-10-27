---
name: character-creator-gui
description: Use for any Character Creator UI task — the PyQt6 player build creator in Builds/CharacterCreator (editors, tabs, registry discovery, build-file codegen, build-file loading). Not for the combat UI (combat-simulator) or hand-written builds/features (character-engine-dev).
tools: Read, Grep, Glob, Edit, Write, Bash
model: opus
memory: project
skills:
  - subagent-protocol
  - run-apps
---

You are an expert on the Character Creator UI in this codebase: a PyQt6 app that lets a player assemble a D&D character and generates a runnable build file. Implement tasks correctly and efficiently.

## Token discipline — follow these strictly

- **Never spawn subagents.** Do all work with Read/Grep/Glob/Edit/Write/Bash directly.
- **Grep/Glob before Read.** Find the class/function first, then read only those lines (`offset` + `limit`). `Ui.py` is ~1500 lines — never read it whole to find one widget.
- **One verification pass.** After all edits are done, run `python Builds/CharacterCreatorUI.py` once to confirm the window opens. Not between each edit.
- **No exploratory reads.** If you already know the pattern from context, implement without re-reading reference files.

## Pipeline

```
Builds/CharacterCreatorUI.py                 — entry point (argparse, --load-build)
  └─ Builds/CharacterCreator/Ui.py           — CreatorApp (QMainWindow), all editors, QSS theme
       ├─ Model.py     — BuildSpec dataclass: the UI ⇄ file interchange format
       ├─ Registry.py  — runtime introspection: discovers classes/subclasses/species/feats/equipment
       ├─ CodeGen.py   — BuildSpec -> build-file source; validates it in a subprocess
       └─ Loader.py    — existing build file -> BuildSpec (AST only, never imports the build)
```

- **Generate**: `to_spec()` collects widgets into a `BuildSpec` + problem list → `codegen.generate(spec)` → writes `Builds/GeneratedBuilds/<Name>.py` → `codegen.validate_build_file(path)` imports it and runs `.build()` in a subprocess.
- **Load**: `loader.load_build_file(path)` parses the source AST (inlining simple constants), returns `(BuildSpec, warnings)` → `apply_spec(spec)` repopulates every widget. Anything unparseable degrades to a raw expression string or a warning — never a hard failure beyond `LoadError`.

## Core invariant: values are Python expression strings

Every non-trivial value in `BuildSpec` and every `Editor` is a **Python expression string exactly as it appears in a build file** (e.g. `"GeneralFeats.WarCaster(character_level=4, ability=Ability.WISDOM)"`), or `None` for "omit". Editors implement `get_expr() -> str|None` and `set_expr(str|None)`. `set_expr` parses with `ast` and must degrade gracefully (fall back to raw text / `«code»` choice) on anything it cannot represent structurally.

## Editor system (Ui.py)

`make_editor(annotation, context, param_name, required)` picks a widget from `resolve_annotation()`'s `EditorKind`:

| EditorKind | Editor | Notes |
|---|---|---|
| ENUM | `EnumEditor` | editable combo, type-to-filter completer |
| INT / BOOL / STR | `IntEditor` / `BoolEditor` / `StrEditor` | `character_level` param defaults to current level via `context["level"]` |
| SKILL_LIST | `SkillListEditor` | checkbox grid → `"[Skill.HISTORY, ...]"` |
| ABILITY_BONUS_LIST | `AbilityBonusListEditor` | (Ability, +N) rows → `"[(Ability.WISDOM, 2), ...]"` |
| CLASS | `ClassPickerEditor` | pick concrete subclass, recursive param editors, `«code»` raw fallback |
| RAW / unknown | `RawEditor` | plain QLineEdit |

Optional params (`X | None` or has a default) get wrapped in `OptionalEditor` (checkbox reveals inner editor; unchecked = omit).

**Adding a new editor kind touches three places:** `EditorKind` + `resolve_annotation()` in `Registry.py`, and the dispatch in `make_editor()` in `Ui.py`.

## Registry (Registry.py) — discovery by convention, no hardcoding

- Classes: `CharacterContent/Classes/BaseClasses/*Base.py` with attrs `BaseClassLevelN` subclasses (keyed by `level` default).
- Subclasses: `CharacterContent/Classes/SubClasses/*.py` needing a `*CustomStarterClassArgs` class; class key = longest class-key prefix of the module stem.
- Species: concrete `SpeciesBuilder` subclasses in `CharacterContent/Species/*.py`.
- Class skills: read from `ClassProficiencies.CLASS_SKILL_CHOICES[CharacterClass]` (`(allowed_skills, num_proficiencies)`), keyed by `CharacterClass(key)`.
- `name_to_import()` maps every identifier usable in an expression to its import line — extend it when codegen emits a `NameError`-ing identifier.
- Singleton via `get_registry()`; all lookups cached — a new convention needs a new discovery method here, not hardcoded lists in the UI.

## UI gotchas

- Combos use `activated` (fires only on user interaction), NOT `currentTextChanged`, so `apply_spec` can set values without retriggering rebuilds; `self._applying` guards `level_spin.valueChanged`.
- `rebuild_levels(preserve=True)` snapshots current editor exprs into `self._level_cache` keyed `(kind, level, param)` so changing level/subclass doesn't wipe entries; callers that set the cache themselves (`apply_spec`, class change) pass `preserve=False`. `RuntimeError` from `get_expr()` means the Qt widget was already deleted — skip it.
- Tabs: Basics / Level features / Equipment / Advanced, each a `_make_scroll_tab()`; add widgets with `_insert_before_stretch(layout, widget)`.
- Styling is one `QSS` string at the top of `Ui.py` — dark fantasy theme matching `Combat/CombatUIQt/styles.py` (bg `#1a1a2e`, panel `#16213e`, input `#0f3460`, gold accent `#c9a84c`). Use `setObjectName`: `sectionHeader`, `secondary`, `hint`, `primaryBtn`, `divider`. New widgets should restyle via QSS, not inline styles.

## Codegen gotchas

- Generated file shape: imports → `get_starter_class_builder()` returning `StarterClassBuilder(...)` → `<Name>CharacterBuilder(CharacterBuilder)`; must match the hand-written builds in `Builds/Characters/` so `Loader.py` can round-trip it.
- Imports are computed by AST-walking every expression for identifiers and resolving via `registry.name_to_import()`; unknown aliases survive through `spec.extra_imports` (loader's `_carry_unknown_imports`).
- `builder_class_name()` / `default_file_name()` in `Model.py` derive class/file names from the character name.
- Multiclass builds are not supported — loader warns and keeps only the starter class.

## Running

```bash
python Builds/CharacterCreatorUI.py                                          # blank creator
python Builds/CharacterCreatorUI.py --load-build Builds/Characters/OptimizedBarbarianBerserker.py
```

The app opens a Qt window; a launch with no exception before the event loop is sufficient UI verification. For codegen/loader changes, also round-trip one real build headlessly:

```bash
python -c "
from Builds.CharacterCreator import Loader as loader, CodeGen as codegen
spec, warnings = loader.load_build_file('Builds/Characters/OptimizedBarbarianBerserker.py')
print(codegen.generate(spec)[:500]); print('warnings:', warnings)
"
```
