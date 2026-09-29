## Plan: one `Character` object

### What the two classes represent today

| | `CharacterSheetData` (`Builds/CharacterSheetAccumulator.py`) | `CharacterStatBlock` (`StatBlocks/`) |
|---|---|---|
| Represents | **The build**: everything the character *has*, as granted by the builders. That covers identity, class levels and history, base ability scores, base skill and save choices, features, spells, invocations, equipment, gold and XP. | **The evaluated character**: a fresh object that every effect is recorded into, which then answers questions (AC, skills, saves, speed, slots, warnings). |
| Other jobs it has picked up | Merging each class builder's partial sheet (`merge_with`), running the effect pass and caching it (`setup_character_stat_block`), multiclass validation, output paths, rendering | Copies of identity (name, subclass, base class, levels, class history, gold, spellcasting ability, spell slots), because feature text needs levels |

**Why there are two.** The accumulator is mutable and filled piecemeal by several builders. The stat block is the replay target, so rebuilding is repeatable and content code sees only stats, not builder internals.

The order-free work removed most of that reason. The stat block is now a record of facts with read-time getters, so one object can own both the sources and the derived values.

### What the split costs today

1. **Two "characters".** Identity, levels, class history, spellcasting ability, spell slots and gold live on both. Every consumer has to carry both objects:
   - The sheet writer takes the stat block **plus 14 separate lists** from the sheet data.
   - The combat UI reads both.
2. **Misleading names.**
   - "StatBlock" suggests a monster stat block.
   - "SheetData" / "Accumulator" suggests something built for rendering.
   - `setup_character_stat_block()` is a query that secretly builds everything.
3. **Class rules live in a type hierarchy.** 15 `*SkillsStatBlock` and 14 `*SavingThrowsStatBlock` subclasses hold each class's skill list and saving throws. These are the last proficiencies outside the feature model.
4. **Heuristic merging.** `merge_with` merges partial sheets field by field, with an "empty values" rule.
5. **Manual cache invalidation.** Every `add_*` calls `_invalidate_cache()`, and a feature-id tuple catches late extensions.
6. **Equipment is mutated during evaluation.** Fighting styles and items write into weapon objects, which forces per-build copies and idempotence guards.
7. **Validation in two places.** Requirements are checked in `CharacterStatBlock.validate()`, multiclass prerequisites in the sheet data.

### Target model

One public object, **`Character`**. It holds the player's decisions and the sources they grant, and derives everything else on read.

```
Character
├─ name, species, is_example
├─ class_levels: ClassLevels      level per class, level-by-level history, subclasses
├─ ability_scores: AbilityScores  base scores + recorded increases
├─ features                       every grant: class/subclass/species/background/feats,
│                                 proficiency bundles, skill choices
├─ spells, invocations
├─ inventory: Inventory           armor, weapons, items, equipment entries, gold
└─ effects (internal, lazy)       an Effects record built from the sources when they change
   queries: armor_class(), skill_modifier(), saving_throw_modifier(), hit_points(), initiative,
            speed, senses, resistances, proficiencies, spell_slots, warnings, validate()
```

**Content contract:**
- `Feature.apply(effects: Effects)` gets a **write-only** record: it can add proficiencies, bonuses and formulas, and nothing else.
- Formulas (`lambda c: ...`) and `get_description(character)` get the **`Character`**.

"apply() must not read stats" then stops being a rule the guard tests enforce and becomes something the type makes impossible to break.

**Naming:**

| Today | Proposed |
|---|---|
| `CharacterSheetData`, `CharacterSheetAccumulator.py` | `Character` (`Model/Character.py`) |
| `CharacterStatBlock`, recording half | `Effects` (internal to `Character`) |
| `CharacterStatBlock`, query half | methods on `Character` |
| `AbilitiesStatBlock` / `SkillsStatBlock` / `SavingThrowsStatBlock` | `AbilityScores` / `Skills` / `SavingThrows` (parts of `Effects`) |
| `CombatStatBlock` | dissolved: size and speed come from the species, AC formulas and HP bonus go into `Effects` |
| 29 per-class skill/save stat block subclasses | class data: saves in `ClassProficiencies`, plus a `ClassSkillChoice` feature |
| `setup_character_stat_block()` | gone (evaluation is internal and lazy) |
| `StatBlocks/` package | `Model/` |

None of these names are taken in the repo. The model package must not import `CharacterContent` at runtime; it refers to features and weapons through small Protocols. That keeps the import graph acyclic.

### Steps

Every step is shippable on its own. Steps that change no rules must keep all 272 rendered sheets byte-identical, checked with the harness from step 0.

0. **Safety net.** Move the snapshot and render comparison I've been running from scratch into the repo. That means a test holding each build's stats plus a hash of every rendered page. Regenerate it on purpose when a rules fix is meant to change output.
1. **Rendering out of the data.** The writer takes the sheet data itself instead of the stat block plus 14 lists. `create_character_sheet`, `get_output_folder` and `_slugify_name` move into the writer. `RunCharacterCreator`, `RunBuildGroups` and the combat UI call the writer.
   - *Small; touches `Utils`, runners, `Combat/CombatUIQt/app.py`.*
2. **One validation entry point.** Multiclass prerequisites and the required-field checks move into `validate()`.
   - *Small.*
3. **Class rules become features.**
   - Starting-class saving throws go into `ClassProficiencies`; multiclassing grants none.
   - A `ClassSkillChoice(pool, count, chosen)` feature validates skills like the background skill choice does.
   - The 29 stat block subclasses are deleted. After this, the sheet data holds no skill or save state, only base ability scores.
   - *Medium: every build file's `skills=PaladinSkillsStatBlock(...)` argument changes, and so does the Character Creator's code generation.*
4. **One identity.** The stat block stops copying name, subclass, levels, class history and gold. A shared `ClassLevels` object carries levels, history and subclasses.
   - *Small to medium.*
5. **Weapons stay unchanged during evaluation.** Fighting styles and items record weapon bonuses as effects, for example `WeaponAttackBonus(applies_to, value, source)`, and attack math reads them.
   - `apply_to_weapons`, the per-build weapon copies and `_add_bonus_once` go away.
   - *Medium.*
6. **Builders write into one object.** Class, species and background builders grant straight into a single sheet instead of producing partial sheets. `merge_with` and `_MERGE_EMPTY_VALUES` are deleted, and the equipment handler's state becomes `Inventory`.
   - *Medium: `ClassBuilder`, `SpeciesBuilder`, `CharacterBuilder`.*
7. **Merge into `Character`.**
   - The sheet data becomes `Character`. The stat block's recording state becomes its internal `Effects`, built lazily, and its query methods move onto `Character`.
   - One version counter replaces the manual cache invalidation.
   - Aliases (`CharacterStatBlock = Character`, and `setup_character_stat_block()` returning self) keep all 185 importing files working.
   - *Medium to large, but mostly moving code.*
8. **Write-only apply.**
   - `Feature.apply(effects)` gets the write-only record; formulas and descriptions get `Character`.
   - `Improvements.py` changes in one place.
   - The roughly 16 direct sub-block writes in features become improvements.
   - The guard tests get simpler.
   - *Medium.*
9. **Rename sweep.** Change `character_stat_block: CharacterStatBlock` to `character: Character` across 1,414 method signatures in 185 files (scripted, then Black), rename the packages and sub-blocks, and remove the aliases. Update the Character Creator's code generation, the agent instructions and `Notes/`.
   - *Large but purely mechanical; the harness proves nothing changed.*

The rename comes last on purpose, so the steps that change behavior stay small and reviewable.

### Decisions for you

1. **Name.** `Character` for the one object, or something more specific like `PlayerCharacter`?
2. **Write-only `apply`** (step 8, my recommendation) or `apply(character)`? The second is simpler, but loses the guarantee that `apply()` can't read stats.
3. **Package.** Rename `StatBlocks/` to `Model/`, or keep the folder name?
4. **Harness.** A hash-based test in `tests/` (my recommendation) or a separate script you run by hand?

Want me to save this plan to `Notes/character-model-plan.md` alongside the other design notes?