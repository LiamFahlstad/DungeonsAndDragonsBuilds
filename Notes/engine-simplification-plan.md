# Plan: Simplify the build engine ("simple rather than clever")

Follow-up to `Notes/model-refactor-plan.md` (Steps 0–15, all done). That pass
made the engine order-free and removed `TYPE_CHECKING`. This pass keeps both
of those properties and makes the engine easier to read and change:

1. **Plain code over clever code.** More lines that read top to bottom beat a
   one-liner you have to decode.
2. **A folder structure where imports only point down and readers get concrete
   types.** Then no `cast`, no `_as`, no `isinstance` narrowing and no
   `TYPE_CHECKING` are needed.
3. **One job each for `Grants`, `CharacterSources` (new), `Effects`, `Ledger`
   and `Character`.**
4. **`Character` is the one complete object about a character.** The sheet, the
   combat engine and the tests all use it the same way.
5. **Every rules number has one name in one place** (`Core/Rules.py`).
6. **Pylance is clean**, and the checker that runs in CI is the same one the
   editor uses.

**Kept from the first plan, and never traded away:**

- Order independence: features, extensions, spells, gear and fighting styles
  may be granted and applied in any order.
- No `if TYPE_CHECKING:`.
- The source / ledger / query rule (first plan, section 2b).
- The merge rules (2c) and grant stamps (Steps 9–10).
- The snapshot discipline.

Every step is its own commit and ends green (section 4). Nothing in this
document has been changed in the code yet.

---

## 0. Step overview

| Step | What | Kind | Output change | Size |
|---|---|---|---|---|
| 0 | Safety net: baseline, layering rules, Creator round-trip | tests | none | S |
| 1 | Rules constants in `Core/Rules.py` | mechanical | none | S |
| 2 | Named records and enums instead of tuples and string literals | internal | none | M |
| 3 | One way to record a bonus | API | none | S |
| 4 | Rewrite the dense spots | internal | none | M |
| 5 | One copy of each enum; content stops importing Combat | structure | none | M |
| 6 | Presentation leaves the domain classes | structure | none (byte-identical) | L |
| 7 | `CharacterView`: content reads the character through one interface | codemod | none | M |
| 8 | Ledger parts record facts only (tools, weapon filters) | design | none | M |
| 9 | Content base classes move below `Character`; `_as` is deleted | structure | none | L |
| 10 | Attack math belongs to the character (`AttackProfile`) *(skipped, see Step 10)* | design | none | M |
| 11 | Builder pattern: `CharacterSources` → immutable `Character` | design | none | L |
| 12 | Builder cleanup | small items | none | M |
| 13 | `Character` as the combat representation | design + fixes | combat values (reviewed) | M |
| 14 | Card labels come from the stamp *(optional)* | content codemod | reviewed | M |
| 15 | Pylance clean | fixes | none | M |
| 16 | Docs, agent instructions, final layering | docs | none | S |

Steps 6–11 depend on each other in that order. Steps 1–5 are independent of
each other, and Steps 12–16 come after Step 11.

---

## 1. Findings

### 1a. Clever code, by location

| Where | What it does | Why it's hard to follow | Step |
|---|---|---|---|
| `Model/Character.py:89-103` | `_count_change` is an attrs `on_setattr` hook: assigning any public field bumps `_version` | The cache invalidates through an invisible side effect of `=` | 11 |
| `Model/Character.py:151-173`, `507-543` | Three caches (ledger, extension tree, stamp index), each with its own version field. The cache key includes `inventory.version` and the identity of the `_apply_order` *function* | Five numbers must agree for a read to be correct | 11 |
| `Model/Character.py:180-214` | Delegating properties with setters (`character_subclass`, `base_class`, `level_per_class`, `class_by_character_level`) that also bump the version | Two ways to write the same field, one of which bypasses the version (below) | 11, 12 |
| `CharacterContent/Classes/BaseClasses/ClassBuilder.py:384-392` | `_update_subclass_name` changes `data.class_levels` in place | Bypasses `_version`. It works only because nothing queries the character before the build ends | 11, 12 |
| `Model/Character.py:307-330` | `_resolved_extensions()` returns a `(dict, list)` tuple that callers index with `[0]`/`[1]` (lines 284, 289, 298) | Positional meaning | 2 |
| `Model/Character.py:38-50` | `GrantKind` is a `Literal[...]` with a parallel `GRANT_KINDS` tuple, used for ordering via `.index` | The same list written twice | 2 |
| `Model/Character.py:269-279` | `feature_sort_key` uses `getattr(feature, "skippable_in_concise", False)` | Sheet order lives in the model, and reflection hides the type | 6 |
| `Model/Character.py:486-505` | `iter_stat_effects(features=None)`, with an optional override that only the class itself uses | An unused branch | 4 |
| `Model/Character.py:592-610` | The feats-taken-once check iterates twice, with `next(...)` to find a name | Dense | 4 |
| `Model/Recorder.py:20-27` | `seal()` walks `vars(self)` reflectively and recurses into dict values | Reflection | 13 |
| `Model/AbilityScores.py:11-17`, `61-71` | A property *factory* makes the six score properties. `with_scores(**kw)` maps keyword names via `ability.value.lower()` | Metaprogramming for six fields | 4 |
| `Model/AbilityIncreases.py:28`, `AbilityRequirements.py:21`, `Senses.py:17`, `WornArmor.py:18` | Positional tuples `(ability, bonus, max)`, `(ability, min, reason)`, `(range, source)`, `(type, name)` | Fields read as `m[0]`, `m[1]` | 2 |
| `Model/Bonuses.py:18` vs `Model/CarryingCapacity.py:17` | `(value, source)` in one part, `(source, value)` in the other | The same concept in opposite orders | 2 |
| `Model/SavingThrows.py:45-52` | The sort key is `[order.index(a) for a in (grant[0], *grant[1])]`, then `next(...)` | Decoding it takes a minute | 4 |
| `Model/Spellcasting.py:50,54` | `calculate_spell_slots(...)[0]` and `[1]` | Positional return value | 2 |
| `Model/Effects.py` and `Improvements.py` | Six pairs of `add_X_bonus(int)` / `add_derived_X_bonus(Formula)`, plus six `if callable(self.bonus)` branches in Improvements (lines 234, 345, 429, 443, 468, 522) | Two ways to record one thing | 3 |
| `Model/Grants.py:38-85` | `add_feature`/`add_spell` take `kind=`/`granted_by=` overrides (`kind or self.kind`) | The scope's identity can change per call | 12 |
| `Builds/CharacterBuilder.py:118-120` | `species_builder.set_character_level(...)` and `set_spell_casting_ability(...)` must be called before `build()` | Temporal coupling: state injected through setters | 12 |
| `Builds/CharacterBuilder.py:123-125` | `is_example` is worked out from `type(self).__module__.startswith("Builds.Examples")` | Behavior depends on the file's location | 12 *(optional)* |
| `ClassBuilder.py:256-289` | One loop over a list of 3-tuples `(features_by_level, applied_levels, kind)` | A compact loop that hides two plain calls | 12 |
| `ClassBuilder.py:383` | `getattr(self, "subclass", None)`, because the starter builder has a property and the multiclass builder an attribute | Reflection instead of a declared field | 12 |
| `ClassBuilder.py:468-498` | Eight properties on `StarterClassBuilder` that only forward to `non_generic_arguments` | Boilerplate indirection | 12 |
| `CharacterContent/Features/Core/BaseFeatures.py:141`, `500-510` | The regex `_LEVEL_LABEL` rewrites the level inside 860 hard-coded `origin="X Level N"` strings | Parses text the stamp already knows | 14 |
| `BaseFeatures.py:832` | `from Utils.Html import _bold_prefix` *inside* a function, importing a private name | A hidden dependency | 4 |
| `BaseFeatures.py:144-432` | 290 lines of CSS and the whole card writer in the domain class `Feature` | Presentation mixed into the domain | 6 |
| `CharacterContent/Items/Items/Wondrous.py:252-255` | Bracers of Archery recognize a bow by matching class *names* along the MRO, "because importing Weapons would be circular" | A clever workaround for a structural cycle | 8 |
| `CharacterContent/ToolProficiencies/Proficiencies.py` (`make_item`) | `getattr(Items, type(self).__name__, None)` finds the matching item by class name | Reflection as a lookup table | 8 |
| `Model/Inventory.py:310-324` | A stack merge written as `for ... else` with an index rewrite | Dense | 4 |
| `Utils/CharacterSheetWriters.py:37` | `_as(value, kind)` narrows Protocol-typed model data back to concrete classes (9 call sites) | A symptom; see 1b | 9 |

### 1b. Why `_as` exists (point 9)

A Protocol is needed on exactly one side of every two-way relationship.
`Character` holds features, and a feature reads the character to describe
itself.

- **Today the Protocol is on the storage side.** `Character` stores
  `GrantedFeature`, `Gear`, `ArmorGear` and `Effect` (`Model/Sources.py`), so
  every reader of a character gets Protocols back. The sheet writer narrows
  them with `_as`, `Feature.write_to_file` asserts `isinstance`, the combat UI
  uses `getattr(f, "name", ...)`, and `CharacterBuilder.get_starting_item` is a
  type error (`Gear` isn't `AbstractArmor | AbstractWeapon | Item`).
- **The fix is to put it on the reading side.** Content base classes read the
  character through one Protocol, `CharacterView`, defined low. `Character`
  sits above them and stores the concrete classes, so every reader gets
  concrete types for free.

The reading side is small. Measured in `CharacterContent`:

| Reads | Count |
|---|---|
| `get_proficiency_bonus` | 77 |
| `get_class_level` | 66 |
| the six ability-modifier helpers and `get_ability_modifier` | ~110 |
| `calculate_difficulty_class` | 24 |
| `character_level` | 7 |
| `get_features_by_type` | 2 |
| a few armor and skill answers | — |
| weapons reading `character.ledger` | 4 sites |
| `BaseFeatures` reading `stamp_of`, `extensions_of`, `has_granted` | 6 sites, and all of them are card rendering, which leaves in Step 6 |

### 1c. Who does what today (point 10)

- **`Character` has seven jobs:** it's a source store, a version counter, three
  caches, the evaluator, the extension resolver, the query facade, a sheet sort
  key (`feature_sort_key`), and validation.
- **`Grants`** wraps the `Character`, but individual calls can override its
  identity (`kind=`, `granted_by=`).
- **`Ledger` and `Effects`** share `Model/Effects.py`. `Effects` is the
  write-only door to the ledger. This is the order-independence guarantee and
  stays.
- **Builders write the character three ways:** through `Grants`, through
  `Character.add_*` / `set_*`, and by changing `character.class_levels` in
  place. The species builder also gets state injected through setters before
  `build()`.

### 1d. Layering leaks

- **Content imports Combat.** Six content files import `Combat.Definitions`
  (`ExtendedCombatantData` for wild shapes and companions): `DruidBase.py`,
  `DruidFeatures.py`, `WildShapeForms.py`, `PrimalCompanions.py`,
  `DruidWildfireFeatures.py` and `RangerDrakewardenFeatures.py`.
  `Utils/CreatureStatBlocks.py` does too.
- **Two enums are duplicated.** `Combat/Definitions.py:39,148` redefines
  `Condition` (with two extra members, Bloodied and Concentrating) and
  `DamageType`. Pyright already flags a mismatch in
  `DruidWildfireFeatures.py:63` and `RangerDrakewardenFeatures.py:84`.
- **`Utils/` holds two layers.** Generic helpers (`Html`, `StringUtils`,
  `TableUtils`, `DamageCalculator`) sit next to writers that import content and
  Combat (`CharacterSheetWriters`, `BuildGroupSheetWriter`,
  `CreatureStatBlocks`).
- **Presentation sits in content.** `Items/Weapons/Writer.py`,
  `Items/Armor/Writer.py`, the `Feature` card writer and CSS, and
  `FightingStyle.write_to_file` all live with the content.
- **Weak types where the model can't name content:**
  `EquipmentTraining` stores tools as `Any` and weapon proficiencies as a bare
  `Enum`, and `WeaponFilter` is `Callable[[Any], bool]`.

### 1e. Magic numbers (point 13)

| Value | Where | Rule |
|---|---|---|
| `3` | `Character.py:35` `MAX_ATTUNED_ITEMS` | attunement limit |
| `2 + (level - 1) // 4` | `Character.py:739` | proficiency bonus |
| `(score - 10) // 2` | `AbilityScores.py:7` | ability modifier |
| `{8, 10, 12, 13, 14, 15}`, `27`, `8`, `15`, the cost formula | `AbilityScores.py:107-179` | standard array, point buy |
| `13` | `AbilityRequirements.py:51` | multiclass minimum |
| `8` | `Spellcasting.py:67` | spell save DC base |
| `2 *` | `Skills.py:131` | expertise doubles proficiency |
| `10` | `ArmorClass.py:31` | unarmored AC base |
| `3` | `CarryingCapacity.py:25` | base carrying slots |
| `(STRENGTH, DEXTERITY)` | `Effects.py:88` | untrained-armor abilities |
| `1 <= level <= 20`, `max_level=20`, `range(1, 21)` ×6 | `ClassBuilder.py:302`, `Character.py:656`, writers | character level range |
| `max_score=20` ×7, `max_score=25` ×2, `total=2` ×3 | content | ability score caps, ASI points |
| starting gold per class | `Builds/StartingEquipment.py:17` | class table |
| `ac - 2` | `Combat/CombatUIQt/app.py:121` | assumes every shield is +2 (a bug, 1g) |
| `"Other"`, `"Person"`, `"Item"` | `Bonuses`, `Skills`, `Effects`, `CarryingCapacity`, `Improvements` | default source labels, repeated as literals |

`MAX_PROFICIENCY_BONUS`, `MAX_ABILITY_MODIFIER` and the hit dice are already
named, in `Core/Definitions.py`.

### 1f. Pylance

Pyright 1.1.411 in its default (standard) mode, over `Model`, `Core`, `Utils`,
`Builds`, `CharacterContent`, the Combat UI and `RunCharacterCreator.py`,
finds **415 errors**:

- **369 in `Combat/CombatUIQt`.** The mixins use attributes that only the app
  class defines (`selected_character` ×48, `_log_event` ×22, `characters`,
  `player_log_file`, ...).
- **46 elsewhere:**
  - `FeatureGeneration/Output.py`: 10. It's generator output with undefined
    names.
  - `Builds/CharacterCreator/Ui.py`: 11, mostly `Optional` access.
  - `Utils`: 8, of which `Scroll` attributes on `Item` were already noted in
    the first plan's Step 12.
  - Override mismatches: 3 (`Weapon.write_to_file`, and `ItemImprovement.apply`
    twice).
  - The duplicate-enum mismatch: 2.
  - Missing constructor args on `ExtendedCombatantData`: 2.
  - `ClassBuilder.py:289` passes a `str` where a `GrantKind` is expected.
  - `Armor/Base.py:131` may pass `None` as an `ArmorType`.
  - `FighterSamuraiFeatures.py:65` declares `regained_on` twice.
  - `RunCharacterCreator.py:114` instantiates `type[CharacterBuilder]` without
    arguments.
- **`Model/`: 0** (check D, basic mode).

### 1g. Bugs found while reading

| Bug | Where | Step |
|---|---|---|
| Combat shows the species' base speed, not `calculate_speed()` (so Unarmored Movement, Fast Movement and so on are missing) | `Combat/CombatUIQt/app.py:174` | 13 |
| Combat's no-shield AC is `ac - 2`. That's wrong for a +1 shield, and wrong for a shield without training (which gives no bonus) | `app.py:117-121` | 13 |
| `class_levels` is changed in place without a version bump. Latent today | `ClassBuilder.py:384-392` | 11 |
| A duplicate `regained_on`: the first definition is dead code | `FighterSamuraiFeatures.py:65` | 15 |
| Core's `DamageType` is passed where Combat's is expected | `DruidWildfireFeatures.py:63`, `RangerDrakewardenFeatures.py:84` | 5 |

---

## 2. Target design

### 2a. Principles

**"Simple rather than clever", made concrete:**

- **A record has named fields.** No tuple whose meaning lives in `[0]`/`[1]`.
  Use a frozen attrs class, like `SpellGrant`.
- **A fixed set of choices is an `Enum`.** Not a `Literal` plus a parallel
  tuple.
- **No reflection in program logic.** No `getattr`/`hasattr` on our own types,
  no `vars()` walks, no MRO name matching, no module-path sniffing, no
  `on_setattr` hooks.
- **A loop with a condition is written as a loop.** Not
  `next(x for x in ... if ...)` or a nested comprehension.
- **A function returns one thing.** Two results get a small record with named
  fields.
- **One way to do each thing:** one way to grant, one way to record a bonus,
  one way to read a value.
- **A number from the rulebook gets a name in `Core/Rules.py`.** A
  presentation number (CSS, column widths) stays where it's used.

**Well-established patterns, each used for one thing:**

| Pattern | Where |
|---|---|
| Builder | `CharacterBuilder` / class and species builders → `CharacterSources` → `Character` |
| Facade | `Character`: the only read API. `Effects`: the only write API during evaluation |
| Dependency inversion / interface segregation | `CharacterView`: the one Protocol, owned by the lower layer |
| Value object | records in `Model/Records/` and `Core/`: frozen, compared by value |
| Template method | `Feature.get_description` and its sibling hooks, called by the presentation layer |
| Strategy | `Formula` callables evaluated on read |
| Layered architecture | section 2b, enforced by `tests/test_layering.py` |
| Separation of domain and presentation | `Model/` and `CharacterContent/` describe; `Presentation/` renders |

### 2b. Folder structure and layers

```
Core/                      L0  rules data; imports only Core
  Definitions.py               enums - exactly one copy of each (Ability, Skill, DamageType, Condition, ...)
  Rules.py            (new)    every rules number + tiny rules functions (proficiency_bonus, ability_modifier, ...)
  Weapons.py          (new)    weapon enums (WeaponProficiency, WeaponProperty, mastery), moved from content
  SpellcastingRules.py
Utils/                     L0  generic helpers, no domain imports: Html primitives, StringUtils, TableUtils, DamageCalculator

Model/
  Records/            (new) L1  plain immutable data, imports only Core:
                               AbilityScores, ClassLevels, GrantStamp/GrantKind, SpellGrant/SpellReplacement,
                               WeaponTraits, ToolProficiency, SourcedValue, ...
  View.py           (renamed) L1  CharacterView (Protocol) + Formula   <- was Contracts.py / StatView
  Stats/            (moved)   L2  one part per concern + Bonuses       <- was Model/<Part>.py
  Ledger.py         (split)   L3  Ledger: the parts + rules that span two parts
  Effects.py                  L3  Effects: the write-only door into a Ledger
  Content/          (new)     L4  base classes content is made of:
                               Effect (ABC), Feature, Improvements, FightingStyle,
                               Gear/Item, Gear/Weapon, Gear/Armor, Gear/ExtraDamage
  Creatures/        (new)     L4  stat-block data for companions and wild shapes (from Combat/Definitions.py)
  Attacks.py        (new)     L5  AttackProfile: one weapon in one character's hands
  Inventory.py                L5  typed with the Content gear classes
  CharacterSources.py (new)   L5  every choice and grant, stamped; mutable while building
  Grants.py                   L5  the builder's scope; writes into CharacterSources
  Character.py                L6  the finished character: sources + ledger + every query

CharacterContent/          L7  concrete content only (features, classes, species, items, spells)
Builds/                    L8  CharacterBuilder, StartingEquipment, build files, Character Creator
Presentation/       (new)  L8  sheet writers, card renderers, CSS (from Utils/ writers, Items/*/Writer.py, Feature cards)
Combat/                    L9  combat simulator and UI
```

| Package | May import |
|---|---|
| `Core` | stdlib, `attr` |
| `Utils` | `Core` |
| `Model/Records`, `Model/View.py` | `Core` |
| `Model/Stats` | `Core`, `Model/Records`, `Model/View.py` |
| `Model/Ledger.py`, `Model/Effects.py` | the above + `Model/Stats` |
| `Model/Content`, `Model/Creatures` | the above + `Utils` |
| `Model/Attacks.py`, `Inventory.py`, `CharacterSources.py`, `Grants.py` | the above + `Model/Content` |
| `Model/Character.py` | everything in `Model` |
| `CharacterContent` | `Core`, `Utils`, `Model` |
| `Combat/Monsters` (the monster catalog, layer "creatures") | `Core`, `Utils`, `Model` |
| `Builds`, `Presentation` | everything below, plus each other where needed (the Creator renders sheets) |
| `Combat` | everything |

**Two rules make this hold without `TYPE_CHECKING`:**

1. **Ledger parts record facts typed with `Core`/`Records` types only.** They
   never store content objects. That's why tools become a record and weapon
   filters take `WeaponTraits` (Step 8).
2. **Content reads the character only through `CharacterView`.** It's the only
   Protocol left. `Character` satisfies it structurally, and `Effects`
   deliberately doesn't, so a formula can never read in the middle of
   evaluation.

### 2c. Responsibilities (point 10)

```
 level / species / background builders
            │  grant (stamped)
            ▼
         Grants ──────────────► CharacterSources        mutable while building
                                       │
                                       │  Character(sources)
                                       ▼
                                   Character            immutable, complete
                                   │      ▲
                     apply() each  │      │ queries resolve parts against
                     effect once   ▼      │ the character (as a CharacterView)
                     Effects ────► Ledger ┘
```

| Object | Owns | Written by | Read by | Lifetime |
|---|---|---|---|---|
| `Grants` | where the builder is: level, kind, `granted_by` | — | — | one per class level, species, background or origin feat being granted |
| `CharacterSources` | every choice and grant, each grant stamped | `Grants`, builders | `Character` | mutable until it's handed to `Character` |
| `Effects` | nothing: a write-only door into one `Ledger` | `apply()` of features, gear and fighting styles | — | one evaluation |
| `Ledger` | what the effects recorded, one part per concern, plus the rules that combine two parts | `Effects` only | `Character` | built once, inside `Character` |
| `Character` | the finished character: its sources, its ledger and every query | nobody (immutable) | sheet, combat, tests, formulas and descriptions (as a `CharacterView`) | after the build |

Each verb has one owner: **grant** (`Grants` → `CharacterSources`),
**record** (`Effects` → `Ledger`), **ask** (`Character`).

### 2d. `Character`, the one object (point 11)

- **Identity:** `name`, `character_level`, `class_levels` (classes, levels,
  history, subclasses), `size`.
- **Sources:**
  - `features`, `top_level_features()`, `extensions_of(feature)`,
    `stamp_of(feature)`;
  - `spells` (resolved), `invocations`, `fighting_styles`, `weapon_masteries`;
  - `armors`, `weapons`, `items`, `equipment_entries`, `current_gold`.

  These are all concrete types (`Feature`, `Weapon`, `Armor`, `Item`,
  `FightingStyle`).
- **Queries:**
  - ability scores and modifiers, skills, saves, AC (with and without
    shield), HP, initiative, speed;
  - spell DC, attack bonus and slots; defenses, senses, languages, tools;
  - `attack_profile(weapon)`: attack bonus, damage bonus, roll condition,
    proficiency and mastery.
- **Immutable after the build.** A combat engine can hold it for the whole
  encounter. Combat state (current HP, conditions, slots spent) lives on a
  combat-side object that holds a `Character`, never on the `Character` itself.

What this looks like for the people who use it:

```python
# A feature (content)
from Model.Content.Feature import Feature
from Model.View import CharacterView

class Rage(Feature):
    def get_description(self, character: CharacterView) -> str: ...

# A test
sources = make_sources()
sources.add_effect(SkillBonus(Skill.ARCANA, 2))
character = Character(sources)
assert character.get_skill_modifier(Skill.ARCANA) == 5

# The sheet writer: concrete types, no _as
for feature in character.top_level_features():   # list[Feature]
    render_feature_card(feature, character, file)

# Combat
profile = character.attack_profile(weapon)
profile.attack_bonus, profile.damage_bonus, profile.roll_condition
```

### 2e. Order independence (point 1)

Nothing in this plan relaxes it. What guarantees it, and what checks it:

- **`Effects` is write-only**, and every value resolves on read. Checked by
  `tests/test_feature_apply_order.py`.
- **Every part documents a commutative merge rule** (first plan, 2c). Checked
  by `tests/test_part_merge_rules.py`.
- **Extensions are declared and resolved by `ExtensionTree`; spells by
  `resolve_spells`.** Neither depends on grant order. Checked by
  `tests/test_order_invariance.py` and `tests/test_spell_grants.py`.
- **The sheet sorts by a canonical key**, which moves to `Presentation/` in
  Step 6. Checked by `test_grant_order_keeps_sheet`, plus the `-m slow`
  matrix.
- **The `_apply_order` seam survives Step 11** as a keyword-only constructor
  argument, `Character(sources, apply_order=...)`. It's the only test seam, and
  it's not part of the cache key, because there is no cache.

Every step that touches evaluation or granting (2, 3, 4, 8, 9, 10, 11) runs
`-m slow` before it's committed.

### 2f. Constants (point 13)

`Core/Rules.py` holds the numbers the rulebook defines that the engine or many
features share, each named after its rule, plus the few pure functions that
are rules (`proficiency_bonus(level)`, `ability_modifier(score)`,
`point_buy_cost(score)`).

- **A number that is one feature's own rule stays in that feature**, where
  it's read in context. Examples: a feat's `total=2`, Primal Champion's
  "maximum of 25", a Ring of Intellect's +2, and `fighter_level >= 13` in one
  feature's table.

- **Class tables stay with `CharacterClass`** in `Core/Definitions.py`: hit
  dice, and starting gold moved from `StartingEquipment.py`. `Rules.py` imports
  `Definitions`, never the other way round.
- **Default source labels** (`"Other"`, `"Person"`) are named constants in the
  module that owns them. They are labels, not rules.

---

## 3. Steps

Every step lists its goal, changes, tests, verification and output. "Verify"
refers to the checks in section 4.

### Step 0: Safety net *(tests only)* — done

- **Result:**
  - **Baseline.** The tag `simplify-baseline` is on `9f64c74` ("Step 5"), the
    last commit before this plan. The page dump (3585 pages) went to that
    session's scratchpad. A later session regenerates it from the tag:
    `git worktree add <dir> simplify-baseline`, then run the snapshot test in
    `<dir>` with `SNAPSHOT_DUMP_DIR` set.
  - **`tests/test_layering.py`** replaces `test_model_layering.py`. Every
    project file has a layer (`LAYER_OF`, longest module prefix wins), and a
    test fails when a new folder isn't placed. The offenders found:
    - 6 content files → combat (stat-block types);
    - 4 content files → presentation (`Utils.CreatureStatBlocks`);
    - `Utils/CreatureStatBlocks.py` → combat;
    - the 37 monster catalog files (`Combat/Monsters/`) → combat. These are
      allowlisted as one folder entry.
    - `cast` is only in `Model/Recorder.py`, and `_as` only in the sheet
      writer.
  - **One change from the plan:** `Combat/Monsters` is its own layer,
    "creatures". 12 build files import monsters for wild shapes, so the
    catalog is data that sits below `Builds`, not part of the combat engine.
    Step 5 has to move the types it imports, so the catalog stops importing
    `Combat.Definitions`. `Model` may now import the `Utils` helpers (the
    target in 2b); the old test forbade all of `Utils`.
  - **`tests/test_creator_roundtrip.py`.** 120 of 137 builds round-trip to
    identical stats, and the whole test takes about 7 s, so it isn't `slow`.
    The 17 others are strict xfails, each with its reason:
    - 5 multiclass builds: the `BuildSpec` has none;
    - 5 builds with adventuring gear: the `BuildSpec` has none;
    - 7 real Creator bugs, left for you to decide on:
      - the generated 2014 `MonkLevel4` call misses `general_feat` (5 builds);
      - the Druid Land build uses a module constant (`_EARLY_LAND`) and Kivi
        Jatti uses a local variable (`martial_arts_die`), neither of which the
        generated file defines;
      - the Loader doesn't know `RogueCustomStarterClassArgs`.
  - **Pyright baseline:** see 1f (415 errors in standard mode; `Model/` 0).
  - **Verified:** A (no golden change), B (3245 passed, 17 xfailed), C, D.

- **Goal:** catch any behavior, output, layering or codegen change before
  anything moves.
- **Changes:**
  1. **Baseline.** Tag the commit `simplify-baseline` and dump every page once:
     `SNAPSHOT_DUMP_DIR=<scratchpad>/baseline python -m pytest tests/test_build_snapshots.py`.
     The dump goes in the scratchpad, never the repo.
  2. **Layering test.** `tests/test_layering.py` replaces
     `tests/test_model_layering.py`:
     - it encodes the table in 2b as data;
     - it keeps the "no `TYPE_CHECKING`" rule;
     - it adds "no `typing.cast`" and "no `_as(`".

     Each rule starts with an allowlist of today's offenders: content → Combat
     (6 files), `Utils` writers → content/Combat, `Recorder.py`'s `cast`, and
     the writer's `_as`. As before, a file that is allowlisted but already
     clean fails the test, so the lists can't go stale.
  3. **Creator round-trip test.** `tests/test_creator_roundtrip.py`, for every
     build `Builds/CharacterCreator/Loader.py` can read: load → `BuildSpec` →
     `CodeGen` → import the generated module from `tmp_path` → build → compare
     with `build_stats.json`.
     - It guards against module moves breaking the import lines the codegen
       emits, and the Registry's `cls.__module__` discovery.
     - List any build the Loader can't read explicitly in the test.
     - Mark it `slow` if it takes more than about 20 s.
  4. **Pyright baseline.** Record the counts per folder (1f) in the commit
     message. They aren't a gate yet.
- **Verify:** A, B, C, D.

### Step 1: Rules constants in `Core/Rules.py` *(mechanical)* — done

- **Result:**
  - **`Core/Rules.py`** holds:
    - `MIN_LEVEL`, `MAX_LEVEL`, `ALL_LEVELS`;
    - `proficiency_bonus()`, `MAX_PROFICIENCY_BONUS` (now derived from
      level 20), `EXPERTISE_MULTIPLIER`;
    - `ability_modifier()`, `MAX_ABILITY_SCORE`, `ABSOLUTE_MAX_ABILITY_SCORE`,
      `MAX_ABILITY_MODIFIER` (now derived from a score of 30);
    - `STANDARD_ARRAY`, `POINT_BUY_BUDGET`, `POINT_BUY_MIN_SCORE`,
      `POINT_BUY_MAX_SCORE`, `point_buy_cost()`;
    - `MULTICLASS_MIN_SCORE`, `UNARMORED_AC_BASE`,
      `UNTRAINED_ARMOR_ABILITIES`, `SPELL_SAVE_DC_BASE`, `MAX_ATTUNED_ITEMS`,
      `CARRYING_CAPACITY_BASE_SLOTS`.
  - **Changed from the plan below:**
    - The level names are `MIN_LEVEL` / `MAX_LEVEL`, because they bound class
      levels too.
    - `CAPSTONE_MAX_ABILITY_SCORE` and `ABILITY_SCORE_IMPROVEMENT_POINTS`
      weren't added. Each is one feature's own rule, so it stays in that
      feature (2f).
  - **Duplicates removed:**
    - the ability-modifier formula: 7 copies, in the Combat UI (4) and
      `CreatureStatBlocks` (2), plus `Model/AbilityScores`;
    - the Creator UI's own point-buy cost, budget and range, and its
      standard array;
    - `CharacterClass.hit_die`'s literal table, which now reads the named
      `*_HIT_DIE` constants;
    - `StartingEquipment`'s gold table, which is now
      `CharacterClass.starting_gold`.
  - **Codemod.** 52 files moved their `MAX_PROFICIENCY_BONUS` /
    `MAX_ABILITY_MODIFIER` imports to `Core.Rules`, and `Definitions.MAX_X`
    became the bare name.
  - **Labels.** `"Other"` is `Bonuses.OTHER_SOURCE`, and `"Person"` is
    `CarryingCapacity.PERSON_SOURCE`.
  - **Tests.** `tests/test_rules.py` checks against the PHB tables: proficiency
    by level, the modifier for scores 1–30, point-buy costs, the budget and the
    array.
  - **Verified.** A: no golden change. B: 3308 passed, 17 xfailed. C: both UIs
    construct offscreen, and the Creator's point-buy label and validation
    messages read as before. D: 0 errors, and no new pyright errors in the
    touched modules outside `Model/`.

- **Goal:** no rules number appears as a literal outside `Core/`.
- **Changes:**
  - **Create `Core/Rules.py`** with:
    - `MIN_CHARACTER_LEVEL`, `MAX_CHARACTER_LEVEL`;
    - `proficiency_bonus(level)`, and `MAX_PROFICIENCY_BONUS` (moved);
    - `ability_modifier(score)`, and `MAX_ABILITY_MODIFIER` (moved);
    - `MAX_ABILITY_SCORE` (20), `CAPSTONE_MAX_ABILITY_SCORE` (25),
      `ABILITY_SCORE_IMPROVEMENT_POINTS` (2);
    - `STANDARD_ARRAY`, `POINT_BUY_BUDGET`, `POINT_BUY_MIN_SCORE`,
      `POINT_BUY_MAX_SCORE`, `point_buy_cost(score)`;
    - `MULTICLASS_MIN_SCORE`, `MAX_ATTUNED_ITEMS`, `SPELL_SAVE_DC_BASE`,
      `EXPERTISE_MULTIPLIER`, `UNARMORED_AC_BASE`,
      `CARRYING_CAPACITY_BASE_SLOTS`, `UNTRAINED_ARMOR_ABILITIES`.
  - **Move starting gold** to `CharacterClass.starting_gold`, next to the hit
    dice.
  - **Replace every site in 1e** (combat's `ac - 2` is fixed in Step 13). Use
    the new names in content: `max_score=MAX_ABILITY_SCORE` ×7, and so on.
  - **Codemod** the 45 `MAX_PROFICIENCY_BONUS` and 62 `MAX_ABILITY_MODIFIER`
    imports to `Core.Rules`. Don't leave an alias behind in `Definitions`.
  - **Name the default labels** `"Other"` and `"Person"` in the modules that
    own them.
- **Tests:** `tests/test_rules.py` checks `proficiency_bonus` for levels 1–20
  against the PHB table, `ability_modifier` for scores 1–30, and the
  point-buy cost table. Expected values come from the book, not from the code.
- **Verify:** A, B, C, D. **Output:** none.

### Step 2: Named records and enums *(internal)* — done

- **Result:**
  - **`Model/Records/GrantStamp.py`:**
    - `GrantKind` is an `Enum`, and its definition order is the sheet order.
      `sheet_rank` replaces `GRANT_KINDS.index`, and `is_class_level`
      replaces the four `kind in ("class", "subclass")` checks (the sheet
      writer, `Feature`, `GeneralFeat`, `EpicBoon`).
    - `GrantStamp` lives here too.
    - The `str` passed as a `GrantKind` in `ClassBuilder` is gone.
  - **`Model/FeatureGrants.py`:** `IfParentMissing`, `FeatureGrant` and
    `ExtensionTree` (`resolve`, `children_of`, `standalone`), which replaces
    the `(dict, list)` tuple. The content and test sites that pass
    `if_missing=` use the enum.
  - **`Model/Records/SourcedValue.py`.** `SourcedValue(value, source)` is
    shared by `Bonuses`, `Skills`, `CarryingCapacity` and the writer.
    `CarryingCapacity` now stores `(value, source)` like everything else, and
    `Bonuses.by_source` is the one sort key, so its order is unchanged.
    `get_skill_bonus_sources`, `get_carrying_capacity_sources` and
    `get_sense_sources` now return records, and their callers (the writer, 6
    test sites) read fields by name.
  - **One change from the plan:** a record used by only one part lives in
    that part's module, next to the only code that reads it:
    - `SourcedFormula` (`Bonuses`);
    - `SenseGrant` (`Senses`);
    - `CappedIncrease` (`AbilityIncreases`), which now keeps uncapped
      equipment bonuses as a per-ability sum, so no `Optional` cap needs
      checking;
    - `AbilityMinimum` (`AbilityRequirements`);
    - `ConditionalProficiency` (`SavingThrows`);
    - `BodyArmor` (`WornArmor`).

    Only records shared across modules go in `Model/Records/`.
  - **`SlotTable(spell_slots, pact_magic_slots)`** is a `NamedTuple` in
    `Core/SpellcastingRules.py`, like `SlotProgression` next to it, and it's
    read by name.
  - **Done early from Step 4:**
    - `SavingThrows._resolved_proficiencies` is a plain loop with a named sort
      key;
    - `AbilityRequirements` has a named sort key;
    - the `((cls, type),) = items()` unpacking in `calculate_spell_slots` is
      gone.
  - **Weapon-bonus labels** (`WeaponBonuses.attack_bonuses`) still return
    `(value, label)` tuples. They're combined with each weapon's own bonus
    tuples, and Step 10 moves that math to `AttackProfile`.
  - **Verified:** A, B (3308 passed, 17 xfailed), C, D, E (1096 slow passed),
    and the snapshots under `PYTHONHASHSEED` 1 and 2. In the touched modules
    outside `Model/`, the only pyright errors left are the two known `Scroll`
    ones.

- **Goal:** every tuple with a meaning gets field names, and every closed set
  of strings becomes an enum.
- **Changes:**
  - **`GrantKind` becomes an `Enum`.** Its definition order is the sheet
    order, so `GRANT_KINDS` is deleted. `if_missing` becomes an
    `IfParentMissing` enum. This also fixes the `str` passed as a `GrantKind`
    at `ClassBuilder.py:289`.
  - **`SourcedValue(value, source)`** replaces the `(value, source)` and
    `(source, value)` tuples in `Bonuses`, `CarryingCapacity` and `Skills`
    sources.
    - Keep each read's *sort key* exactly as it is today:
      `CarryingCapacity` sorts by `(source, slots)`. Otherwise the sheet
      order moves.
  - **More records:**
    - `AbilityIncrease(ability, bonus, max_score)`;
    - `AbilityMinimum(ability, min_score, reason)`;
    - `ConditionalProficiency(ability, alternatives)`;
    - `SenseGrant(range_feet, source)`;
    - `BodyArmor(armor_type, name)`.
  - **`calculate_spell_slots` returns a `SlotTable(spell_slots,
    pact_magic_slots)`.** `Spellcasting` reads it by name.
  - **`ExtensionTree`** replaces the `(dict, list)` tuple:
    `ExtensionTree.resolve(feature_grants)`, `.children_of(feature)` and
    `.standalone`.
  - **Records that leave the Model** (`get_sense_sources`,
    `get_skill_bonus_sources`, carrying capacity sources): switch them to
    records in the same commit and update the writer, as long as there are
    about 20 call sites or fewer. Otherwise do it in a second commit.
  - **New records go in `Model/Records/`.** Create the folder now.
- **Tests:** the existing merge-rule and resolver tests, updated to the field
  names.
- **Verify:** A, B, C, D, E. **Output:** none.

### Step 3: One way to record a bonus *(small API change)* — done

- **Result:**
  - **`Value = int | Formula`** lives in `Model/Contracts.py`, next to
    `Formula`. Step 7 renames that module to `View.py`. `Improvements.py`
    imports `Value` instead of defining its own.
  - **`Bonuses.add(value: Value, source)`** is the one place that tells a
    formula from a flat number. `add_formula` is gone.
  - **Deleted:**
    - the six `add_derived_*` methods on `Effects`, and each part's
      `add_derived_bonus`. The flat `add_*_bonus` methods take a `Value`;
    - the six `if callable(self.bonus)` branches in `Improvements.py`.
    - `SkillBonus` defaults its source to `OTHER_SOURCE` instead of
      branching on `None`. No caller passed `None`.
  - **Content was never touched:** it reaches bonuses only through
    `Improvements`, so the planned "about 25 content sites" were 0.
  - **Tests.** 5 test sites were updated. The `Bonuses` merge test records a
    flat value and a formula through the same `add()`.
  - **Verified:** A, B (3308 passed), C, D, E (1096 slow passed). 117 lines
    deleted, 48 added.

- **Goal:** a bonus is a `Value` (`int | Formula`), recorded by one method.
- **Changes:**
  - `Bonuses.add(value: Value, source)` replaces `add` and `add_formula`.
    `Value` is defined in `Model/View.py`, next to `Formula`.
  - Delete the six `add_derived_*` methods from `Effects` and from the parts.
    Codemod their callers (about 25 content sites).
  - Delete the six `if callable(self.bonus)` branches in `Improvements.py`.
    `SkillBonus.apply` loses its three-way branch, because the source defaults
    to the named label from Step 1.
- **Tests:** a part test records an `int` and a formula through the same
  method.
- **Verify:** A, B, C, D, E. **Output:** none.

### Step 4: Rewrite the dense spots *(internal)* — done

- **Result:**
  - **`AbilityScores`** is a frozen attrs class with six `int` fields:
    - the property factory and the `MappingProxyType` are gone;
    - `get_score` is an explicit mapping;
    - `with_scores` builds a plain `AbilityScores` from `attr.asdict`. It
      isn't `attr.evolve`, which would re-run the standard-array or point-buy
      validation on the changed copy;
    - the two highest-modifier helpers are one `max(...)` each.

    `StandardArrayAbilityScores` and `PointBuyAbilityScores` keep their
    names and constructor (keywords or positional), and validate in
    `__attrs_post_init__`. Assigning a score still raises `AttributeError`.
  - **`Character`:**
    - `iter_stat_effects()` lost its unused `features=` parameter;
    - `_validate_feats_taken_once` groups features by type once, with no
      `Counter` and no `next(...)`.
  - **`Inventory`:**
    - `items` merges stacks with a dict keyed by type, which keeps the first
      instance and the first-seen order, as before;
    - `drop_item` uses `_all_gear()` instead of four concatenated
      comprehensions, and `item.name` instead of `getattr`.
  - **Bolding.** `Utils/Html.py` has a public `bold_lead_in(line)`. The same
    "`.` within 5 words, else `:` within 10" logic was written twice (in
    `Html` and in `Feature._bolden_line`, which imported the private
    `_bold_prefix` inside the function). The two word limits are named.
  - **Verified:** A, B (3308 passed), C, D, E (1096 slow passed). 164 lines
    deleted, 99 added.

- **Goal:** every row of 1a marked "4" reads top to bottom.
- **Changes:**
  - **`AbilityScores`.** Make it a frozen attrs class with six `int` fields.
    `get_score` uses an explicit mapping, `with_scores(**kw)` becomes
    `attr.evolve`, and the property factory goes.
    - `StandardArrayAbilityScores` and `PointBuyAbilityScores` keep their
      names, because builds and the codegen use them. They validate in
      `__attrs_post_init__` using the Step 1 constants.
  - **`SavingThrows._resolved_proficiencies`.** Use a named
    `_canonical_order(grant)` key and a plain `for` loop instead of
    `next(...)`.
  - **`AbilityRequirements.validate`.** Use a named sort key.
  - **`_validate_feats_taken_once`.** Group features by type into
    `dict[type, list[Feature]]` once, then report.
  - **`Inventory`.**
    - `items` merges stacks with a dict keyed by type, keeping the first
      instance, which is today's behavior.
    - `drop_item` uses an `_all_gear()` helper instead of four concatenated
      comprehensions.
  - **`iter_stat_effects()`** loses its unused `features=` parameter.
  - **`Feature._bolden_line`.** `Utils/Html.py` exposes `bold_prefix`
    publicly, and the import moves to the top of the module.
- **Verify:** A, B, C, D, E. **Output:** none.

### Step 5: One copy of each enum; content stops importing Combat *(structure)* — done

- **Result:**
  - **`Combat/Definitions.py` was split by what each class is:**
    - `Model/Creatures/MonsterAbilities.py`: `MonsterAbility`, all 28
      structured subclasses, `DcMonsterAbility`, `extract_dc_from_text`,
      `DiceType`;
    - `Model/Creatures/Combatants.py`: `BasicCombatantData`,
      `ExtendedCombatantData`, `MonsterType`, `Alignment`, `Visibility`,
      `DamageTypeEntry`;
    - **`Combat/Definitions.py` keeps only combat-runtime names:** `Action`,
      `ConditionRule`, the new `CombatStatus` (Bloodied, Concentrating) and
      `tracked_condition_names()`. The tracker's condition list is checked to
      be identical (same 17 names, same order).
  - **Duplicates merged into Core:**
    - Combat's `DamageType` and `Condition` became Core's; their values were
      the same;
    - Combat's `Size` became `Core.Definitions.CreatureSize` (539 `Size.X`
      sites in the catalog, plus content).
    - The two pyright errors from mixing the `DamageType`s (Wildfire,
      Drakewarden) are fixed.
  - **The rewrite.** An AST script rewrote the imports in 63 files: 37
    monster files, 6 content files, the Combat UI and tools,
    `Utils/CreatureStatBlocks.py` and the scenarios.
    `Combat/Tools/generate_monsters.py` writes the new imports and
    `CreatureSize`, so regenerating keeps them.
  - **Weapon enums.** `CharacterContent/Items/Weapons/Enums.py` moved to
    `Core/Weapons.py` (`git mv`), and the `Weapons` package re-exports them
    (Decision 5).
  - **Layering.** Content → Combat, monster catalog → Combat, and
    `CreatureStatBlocks` → Combat are all gone from the allowlist. What's left
    is the 4 content files that render stat blocks (Step 6).
  - **Agent docs updated:** `dnd-monster-creator`,
    `dnd-monster-ability-refactor` (new subclasses go at the end of
    `MonsterAbilities.py`), `combat-sim`, `combat-sim-haiku`.
  - **Left as is:**
    - `DiceType` (monsters) vs `Core.Definitions.Die`. Their APIs disagree:
      `Die.average` is a property, `DiceType.average(count)` a method. Merging
      them renames one API, which is a separate decision.
    - The one-shot `Combat/Tools/migrate_monster_*.py` scripts still contain
      the old import text. They've already been applied, and their match
      strings no longer occur anywhere.
  - **Verified:**
    - A: no golden change. B: 3308 passed. D: 0 errors.
    - Pyright over Combat, content, Utils and Core against a clean HEAD
      worktree: no new errors, 2 fixed.
    - C: `RunCharacterCreator.py` and `RunBuildGroups.py` run; the combat app
      loads every scenario and the Players group offscreen; all 539 catalog
      monsters build; the Combat tools import.

- **Goal:** each enum is defined once, and nothing in content imports `Combat`.
- **Changes:**
  - **`DamageType`.** Combat uses `Core.Definitions.DamageType`. Delete its
    copy.
  - **`Condition`.** Combat uses `Core.Definitions.Condition` for the rules
    conditions and a separate `Combat.Definitions.CombatStatus` for Bloodied
    and Concentrating. Python enums can't be extended, so one enum can't hold
    both. Count the UI usages first; see Decision 7.
  - **Stat-block data moves.** The types content uses for companions and wild
    shapes move from `Combat/Definitions.py` to `Model/Creatures/`:
    `BasicCombatantData`, `ExtendedCombatantData`, `DamageTypeEntry`, and the
    `MonsterAbility` types they reference. `Combat` imports them from there,
    and so do the 37 monster catalog files in `Combat/Monsters/` (the
    "creatures" layer, which builds use for wild shapes). That clears the
    `("Combat/Monsters/", "combat")` allowlist entry.
  - **Weapon enums move.** `CharacterContent/Items/Weapons/Enums.py` moves to
    `Core/Weapons.py`. They're rules enums, and the Model needs them in
    Step 8. The `Weapons` package keeps exporting them (Decision 5).
  - **Allowlist.** Shrink the layering allowlist: content → Combat is gone.
- **Verify:** A, B, C, D, plus `python RunCombatSimulator.py` starts, plus the
  combat tests. **Output:** none.

### Step 6: Presentation leaves the domain classes *(structure, byte-identical)* — done

- **Result:**
  - **`Presentation/` holds every renderer.** All of these moved with
    `git mv`, keeping history:
    - `CharacterSheetWriters.py`, `BuildGroupSheetWriter.py`,
      `CreatureStatBlocks.py` and `Html.py` (all from `Utils/`; nothing below
      presentation used `Html`);
    - `WeaponCards.py`, `ArmorCards.py`, `SpellCards.py` (the three content
      `Writer.py` files);
    - `SpellCompendium.py` (was `CharacterContent/Spells/SpellCompendiumGenerator.py`;
      run it with `python -m Presentation.SpellCompendium`).

    `Utils/` keeps only `StringUtils`, `TableUtils`, `DamageCalculator` and
    `ItemSheetSettings`.
  - **`Presentation/FeatureCards.py`:** `feature_label`,
    `render_feature_description`, `description_to_html`,
    `write_feature_card`, `write_extension_card`, the tag chips and
    `FEATURE_CARD_CSS`. `Feature` went from 900 lines to about 260: content
    hooks only.
  - **`GeneralFeat` and `EpicBoon` no longer override `_label_for`.** They set
    `labeled_by_class_level = True`.
  - **`Presentation/FeatureOrder.py`:** `feature_sort_key` and
    `ordered_extensions`. `Character.feature_sort_key` is gone, and with it the
    `getattr` on `skippable_in_concise`. `Character.extensions_of` keeps a
    canonical, order-free order (level, name, kind, `granted_by`); the "passive
    last" display order is presentation's.
  - **Deleted dead code:** `FightingStyle.write_to_file`,
    `Invocation.write_to_file` (both from the text-file era, never called),
    `Weapon.write_to_file` (a no-op, and an incompatible override pyright
    reported), and `Weapon.write_damage_report` (never called). The content
    packages no longer re-export the writer functions; nothing imported them
    through the package.
  - **The text markers** (`[BOXES:`, `[RESET:`, `[CURRENT:`) moved to
    `Utils/StringUtils.py`, which writes them. `Presentation/Html.py` imports
    them from there, and `add_boxes`'s in-function import of `Html` is gone.
  - **Left allowlisted:** the 4 content files that build companion and
    wild-shape stat blocks (`format_creature_stat_block`) inside their
    description text. That text then goes through `description_to_html` (bolding,
    damage-type colors), so pulling it out byte-identically means a new
    content hook ("creatures this feature shows"). That's a follow-up.
  - **Docs:** agent docs (`dnd-builds-haiku`, `dnd-equipment`,
    `dnd-feature-summaries`), `Builds/README.md`, `QUICKSTART.txt` and
    `feature-application-model.md` point at `Presentation/`.
  - **Verified:**
    - F: all 3585 pages are byte-identical to the Step 0 baseline dump.
    - A, B (3308 passed), E (1096 slow passed), D: 0 errors.
    - Pyright against a clean HEAD worktree: no new errors, 1 fixed.
    - C: `RunCharacterCreator`, `RunBuildGroups`, `RunItemSheets` and
      `SpellCompendium` run; both UIs construct offscreen; the combat feature
      tooltips show the right labels.

- **Goal:** `Model/` and `CharacterContent/` describe a character. Only
  `Presentation/` renders one.
- **Changes:**
  - **Create `Presentation/`** and move into it:
    - `Utils/CharacterSheetWriters.py` (split by section, such as
      `Presentation/Sheet/Overview.py` and `Skills.py`, if that helps; at
      least the module moves), `Utils/BuildGroupSheetWriter.py` and
      `Utils/CreatureStatBlocks.py`;
    - `CharacterContent/Items/Weapons/Writer.py` and `Items/Armor/Writer.py`;
    - `Spells/SpellFactory/Writer.py`, if it only renders.
  - **Feature cards.** These move out of `BaseFeatures.py` into
    `Presentation/FeatureCards.py`: `label`, `_label_for`,
    `render_html_description`, `write_to_file`,
    `write_extension_card_to_file`, the tag HTML, `_description_to_html` and
    `FEATURE_CARD_CSS`. So do `FightingStyle.write_to_file` and
    `Invocation.write_to_file`, and the sheet order key
    (`Character.feature_sort_key`), which goes to
    `Presentation/FeatureOrder.py`.
  - **`Feature` keeps only the content hooks:** `get_description`,
    `get_concise_description`, `get_table_description`,
    `get_resource_tiles`, `calculate_dc`, `number_of_uses`, `regained_on`,
    `target`, and the `uses`/`activation`/`usage_tags` data. The renderer calls
    them (template method).
  - **Split `Utils/Html.py`.** Generic text-to-HTML helpers stay in `Utils`;
    the sheet CSS and slot-box widgets move to `Presentation/`.
  - **Leftover errors disappear:** `Weapon.write_to_file`'s incompatible
    override is gone, and `getattr(feature, "skippable_in_concise")` becomes a
    plain attribute read.
- **Tests:** the layering test now forbids `Model` and `CharacterContent` from
  importing `Presentation`.
- **Verify:** A, B, C, D, and the page dump diffed against the baseline must be
  empty (F). **Output:** none. Every page must be byte-identical.

### Step 7: `CharacterView` *(codemod)* — done

- **Result:**
  - **`Model/Contracts.py` is now `Model/View.py`** (`git mv`), and `StatView`
    is `CharacterView` everywhere: code, tests, `feature-application-model.md`
    and the agent docs. Its docstring now says it's what parts, formulas
    *and content* read.
  - **Members added**, exactly what pyright found content reading (no
    guesses): `calculate_difficulty_class()` (24 reads),
    `calculate_difficulty_class_for_ability()`,
    `calculate_attack_bonus_for_ability()`, and
    `has_feature(feature_type) -> bool`.
    `Character.has_feature` is new, and the two Druid reads use it instead of
    `get_features_by_type(...)`'s list.
  - **Codemod:** every `character: Character` in the features, items, tool
    proficiencies, invocations and spells became `character: CharacterView`,
    and the `Model.Character` imports went (the AST check ignores comments).
    It also dropped the unused `Character` import from 157 class and species
    builder files, left over from the `Grants` codemod.
  - **`format_creature_stat_block`'s `character` parameter was never read,** so
    it's gone from the function and its 5 callers.
  - **The weapon base keeps `Character`** (allowlisted) because it reads
    `character.ledger`; Step 10 moves that math to `AttackProfile`. Its
    `get_description` takes `CharacterView`, matching `Item`.
  - **Feature generator.** `FeatureGeneration/GenerateFeatures.py` emits
    `CharacterView`. Its scratch output, `Output.py`, was left alone
    (Decision 6).
  - **Tests:**
    - `tests/test_layering.py` has a new rule: no feature, item, tool or
      invocation module imports `Model.Character`;
    - `tests/test_contracts.py` calls every `CharacterView` member on a real
      `Character`, including `has_feature`.
  - **Agent docs:** the builds docs now say content reads through
    `CharacterView` and uses `has_feature`; the action-tags, summaries and
    extender docs were updated too.
  - **Verified:**
    - A, B (3317 passed), D: 0 errors.
    - F: all pages byte-identical to the baseline.
    - Pyright against a clean HEAD worktree over Model, content, Presentation,
      Combat, Utils, Core and the entry points: no new errors.
    - C: the three render entry points run, and all 92 combat feature
      tooltips render.

- **Goal:** content reads the character through one small, named interface.
- **Changes:**
  - **Rename** `Model/Contracts.py` to `Model/View.py`, and `StatView` to
    `CharacterView`.
  - **Add the members content reads** (1b): `calculate_difficulty_class()`,
    `calculate_difficulty_class_for_ability(ability)`,
    `calculate_attack_bonus_for_ability(ability)`, and
    `has_feature(feature_type: type) -> bool`. The last replaces
    `get_features_by_type` in `DruidFeatures.py:137` and
    `WildShapeForms.py:13`.
    - Measure the final list the way the first plan's Step 3 did: run every
      build and the test suite with a recording proxy, and add only what is
      read.
  - **Codemod** the 2219 `character: Character` annotations in
    `CharacterContent` to `character: CharacterView`, and drop the imports of
    `Model.Character` that become unused. Exclude `.claude/worktrees`, then run
    `format.sh`.
- **Tests:** `tests/test_contracts.py` calls every `CharacterView` member on a
  real `Character`, checks that `Effects` doesn't satisfy it, and checks that
  no member returns a part. The layering test adds a rule: no file under
  `CharacterContent/Features`, `Items`, `ToolProficiencies` or `Invocations`
  imports `Model.Character`.
- **Verify:** A, B, C, D. **Output:** none.

### Step 8: Ledger parts record facts only *(design)* — done

- **Result:**
  - **`WeaponTraits` lives in `Core/Weapons.py`, not `Model/Records`.** It's
    weapon rules data over Core enums, so it sits next to them, along with the
    proficiency rule `weapon_matches_proficiency(traits, proficiency)`.
    - Its fields are `weapon_type`, `properties`, `kind` and
      `is_unarmed_strike`, with `is_simple`/`is_martial`/`is_melee`/`is_ranged`.
    - Every weapon has `traits`. `Scimitar`, `Longbow` and `Shortbow` declare
      `kind` as a class attribute, which magic subclasses
      (`MarksmansLongbow`) inherit, and `UnarmedStrike` sets
      `is_unarmed_strike`.
  - **Two class-name hacks are gone:** Bracers of Archery's MRO name matching,
    and `weapon_matches_proficiency`'s, which the plan hadn't listed. Both
    compare `traits.kind` now.
  - **The filters take `WeaponTraits`:** Archery (`is_ranged`), Dueling
    (melee, not Two-Handed, not unarmed), Thrown Weapon Fighting, and Bracers
    of Archery. `WeaponFilter` is `Callable[[WeaponTraits], bool]`, so `Any`
    is gone.
  - **`ToolProficiency` is a plain record in `Model/Records/Tools.py`,** not
    a `Feature`. Its card methods were never rendered, because the sheet
    builds its own tool cards.
    - The 37 tool classes stay, since the Creator picks tools by subclass.
    - `craftables` are item names (20 lists rewritten, checked to give the
      same text).
    - `make_item`'s `getattr(Items, type(self).__name__)` became the explicit
      table `TOOL_ITEMS` plus `tool_item(tool)`, with its values typed as
      no-argument factories.
  - **`EquipmentTraining` and `Effects` are typed:**
    `set[WeaponProficiency]`, and tools as `dict[str, ToolProficiency]`
    keyed by name. `Any` and `Enum` are gone from both.
  - **Tests:**
    - `tests/test_weapon_traits.py` has 28 cases with values from the
      PHB/DMG;
    - `tests/test_layering.py` adds `test_ledger_parts_record_facts_only`:
      each part imports only Core, `Model.Records`, `Model.View`,
      `Model.Bonuses` and `Model.Recorder`.
  - **Verified:**
    - A, B (3346 passed), E (1096 slow passed), D: 0 errors.
    - F: all pages byte-identical to the baseline.
    - Pyright against a clean HEAD worktree: no new errors, and one existing
      one fixed (`ClassProficiencies`' tool table).
    - C: the entry points run, and the Creator's tool picker builds.

- **Goal:** no part stores a content object, so `Model/Stats` never needs a
  content type, and the Bracers class-name hack goes away.
- **Changes:**
  - **`WeaponTraits`** is a new record in `Model/Records/`:
    - its fields are `kind` (a `WeaponProficiency` member, such as `LONGBOW`),
      `category`, `properties` and `is_ranged`;
    - every weapon exposes `traits`;
    - `WeaponBonus.applies_to` becomes `Callable[[WeaponTraits], bool]`.
  - **Rewrite the filters on `traits`:** Archery, Dueling, Thrown Weapon
    Fighting, and Bracers of Archery. Bracers checks
    `traits.kind in {LONGBOW, SHORTBOW}` and no longer walks the MRO.
  - **`ToolProficiency` becomes a plain record** in `Model/Records/Tools.py`,
    not a `Feature`. Its fields are `name`, `category`, `ability`,
    `utilize`, and `craftables` (item names).
    - The 38 tools stay in `CharacterContent/ToolProficiencies/` as instances.
    - The tool's card text moves to `Presentation/`.
    - `make_item`'s `getattr(Items, ...)` becomes an explicit dict, from tool
      name to item class, in content.
    - First check that no tool is granted as a feature. Today tools reach the
      Ledger only through the 4 `GrantToolProficiency`/`add_tool_proficiency`
      sites.
  - **`EquipmentTraining` gets concrete types:** `set[WeaponProficiency]` and
    `dict[str, ToolProficiency]` (a set union keyed by tool name).
- **Tests:** a part test records Archery and Bracers bonuses and checks which
  traits they apply to. The layering test adds a rule: `Model/Stats` imports
  only `Core`, `Model/Records` and `Model/View.py`.
- **Verify:** A, B, C, D, E, F. Check the dumps of builds with Archery, Dueling,
  Thrown Weapon Fighting and Bracers by name. **Output:** none.

### Step 9: Content base classes move below `Character` *(structure)* — done

- **Result:**
  - **`Model/Content/`** holds the base classes, all moved with `git mv`:
    - `Feature.py` (was `Features/Core/BaseFeatures.py`), `Improvements.py`;
    - `Item.py` (was `Items/Items/Base.py`), `Weapon.py` (was
      `Items/Weapons/Base.py`), `Armor.py` (was `Items/Armor/Base.py`),
      `ExtraDamage.py`;
    - and, new: `FightingStyle.py` (the base, cut out of `FightingStyles.py`)
      and `Effect.py`, a nominal ABC with `apply(effects)`. `Feature`,
      `CharacterImprovement` and `FightingStyle` subclass it.

    `UnarmedStrike` is concrete content, so it moved to
    `CharacterContent/Items/Weapons/Unarmed.py`.
  - **One change from the plan:** `AbstractWeapon` and `AbstractArmor` keep
    their names. Renaming them `Weapon`/`Armor` would collide with the
    `Weapons`/`Armor` content packages every build imports (`Armor.Armor`).
  - **The weapon base no longer reads `character.ledger`.** `CharacterView`
    gained three answers in `WeaponTraits` terms: `is_proficient_with_weapon`,
    `get_weapon_attack_bonuses` and `get_weapon_damage_bonuses`
    (`EquipmentTraining.is_proficient_with` backs the first). So the weapon
    math moved below `Character` unchanged, typed `CharacterView`, and the
    content-readers allowlist is empty.
  - **The codemod.** An AST script routed every imported name to its new
    module (227 files), including relative and in-function imports, and the
    two split modules (`UnarmedStrike`, `FightingStyle`). The content
    packages keep re-exporting the base names (Decision 5).
  - **The Model is typed concretely:** `Character`, `Grants`, `Inventory`,
    `FeatureGrants` and `StartingEquipment` name `Feature`,
    `AbstractWeapon`, `AbstractArmor`, `Item`, `FightingStyle` and `Effect`,
    and `get_features_by_type` is generic. **`Model/Sources.py` is deleted.**
  - **Narrowing removed:** the writer's `_as` (9 sites), its `TypeVar`, and
    the `isinstance` asserts in `FeatureOrder`. The gear collection lost a
    walrus expression, and `isinstance(weapon, UnarmedStrike)` became
    `weapon.is_unarmed_strike`. The `_as` and content-readers allowlists are
    empty.
  - **Done early from Step 15:** `Model/Content` is now under check D, which
    surfaced the known Armor `Optional[ArmorType]` error. It's fixed: wearing
    an armor whose `base_stats()` set no `armor_type` raises, and every
    concrete armor sets one.
  - **Tests:** `test_contracts` checks every build's content is the
    `Model/Content` classes (Python doesn't check annotations at runtime),
    replacing the Protocol conformance test.
  - **Verified:**
    - A, B (3352 passed), E (1096 slow passed), D: 0 errors, now including
      `Model/Content`.
    - F: all pages byte-identical to the baseline.
    - Pyright against a clean HEAD worktree: no new errors, 2 fixed
      (`CharacterBuilder.get_starting_item`'s `Gear` return, and the Armor
      one).
    - C: the entry points run, the combat UI shows all 92 tooltips, and the
      Creator loads a build with no problems.
- **What this means for Step 10.** The weapon no longer reaches into the
  Ledger, and its attack math already takes a `CharacterView`. So the attack
  numbers are one call each (`weapon.calculate_total_attack_roll_bonus_int(character)`),
  usable by combat as they are. Moving that math into an `AttackProfile`
  would relocate it without making it simpler. Step 10 is downgraded to
  optional: do it only if combat wants one object holding every number for a
  weapon.

- **Goal:** `Character` stores concrete types, and `_as`, `Model/Sources.py`
  and the `isinstance` asserts are deleted.
- **Changes:**
  - **Move to `Model/Content/`:**
    - `Feature` and its data types (`FeatureUses`, `FeatureActivation`,
      `ActionType`, `RegainedOn`, `FeatureTarget`);
    - `Improvements` (`CharacterImprovement`, `ItemImprovement` and the
      families);
    - the `FightingStyle` base;
    - `Item`, `ItemCategory`, `ItemRarity`;
    - `AbstractWeapon`, renamed `Weapon`, plus `ExtraDamage`;
    - `AbstractArmor`, renamed `Armor`.
    - Concrete weapons, armor, items and styles stay in `CharacterContent`.
  - **Add `Model/Content/Effect.py`.** It's a nominal ABC with
    `apply(effects)`. `Feature`, `Item`, `FightingStyle` and
    `CharacterImprovement` subclass it, which replaces the `Effect` Protocol.
  - **Type `Character`, `CharacterSources` and `Inventory` concretely:**
    `list[Feature]`, `list[Weapon]`, `list[Armor]`,
    `list[tuple[Item, int]]`, `list[FightingStyle]`.
    `get_features_by_type(T) -> list[T]` becomes generic, and `Any` goes away.
  - **Delete** `Model/Sources.py` (the Protocols), the writer's `_as`, and the
    `assert isinstance` in card rendering. `CharacterBuilder.get_starting_item`
    type-checks again.
  - **Codemod imports.** Rewrite the imports of
    `CharacterContent.Features.Core.BaseFeatures` (181 files) and
    `.Improvements` (102 files) to `Model.Content.*`.
    - The `CharacterContent.Items.Weapons` / `Armor` / `Items` packages keep
      exporting the base names that build files and the codegen use
      (Decision 5).
    - Inside `Model/` and `CharacterContent/`, always import from the defining
      module.
  - **Don't reuse the old name.** `Model/Sources.py` (the Protocols) is deleted
    in this step. Step 11 adds `Model/CharacterSources.py`, and its different
    name avoids confusing the two.
- **Tests:** the layering allowlists for `_as` and content → Model Protocols
  are empty, and "`Model` imports no `CharacterContent`" still holds.
- **Verify:** A, B, C, D, E, F, plus the Creator UI starts, plus the Creator
  round trip. **Output:** none.

### Step 10: Attack math belongs to the character *(design)* — skipped

- **Result:** not done. As Step 9 found, the attack numbers are already one
  call each against a `CharacterView`, so an `AttackProfile` would move the
  math without making it simpler. Revisit it in Step 13 only if combat wants
  one object holding every number for a weapon.


- **Goal:** "what's my attack bonus with this weapon" is a character query,
  and the weapon holds only its own facts.
- **Changes:**
  - **Add `Model/Attacks.py`:** `AttackProfile(weapon, ability,
    attack_bonus, attack_bonus_parts, damage_bonus, damage_bonus_parts,
    roll_condition, is_proficient, has_mastery)`, built by
    `AttackProfile.of(weapon, view, ledger)`. `Character.attack_profile(weapon)`
    is one line.
  - **Move the character-dependent methods** of `Weapon` into it:
    `is_proficient`, `get_attack_roll_bonuses`, `get_damage_roll_bonuses`,
    `calculate_total_attack_roll_bonus[_int]`, `calculate_damage_bonus_int`,
    `attack_roll_condition`, `_calculate_ability_modifier_bonus` and
    `has_mastery`.
  - **Weapons stop reading `character.ledger`.** `Presentation` (the weapon
    cards and hit probabilities) and `Combat` read the profile.
- **Tests:** `tests/test_attacks.py`, against `FakeView`: a proficient and a
  non-proficient wielder, finesse picking the better ability, Archery
  applying, and untrained armor giving Disadvantage. Expected values come
  from the rules.
- **Verify:** A, B, C, D, E, F. **Output:** none.

### Step 11: Builder pattern, `CharacterSources` → immutable `Character` *(design-critical; Decision 1)* — done

- **Result:**
  - **`Model/CharacterSources.py`** (new): an attrs class with the source
    fields and every `add_*` / `replace_*` / `set_*` / `record_*` method. It's
    mutable, with no evaluation and no version, and `copy()` copies its lists
    and inventory. `SpellSource` moved here too. `Grants` wraps it
    (`Grants.sources`). `ClassBuilder`, `SpeciesBuilder`, `DruidBase` and
    `Scrapers/GenerateClassHandouts.py` write into it, and
    `CharacterBuilder.build()` returns `Character(sources)`.
  - **`Character(sources, *, apply_order=in_given_order)`** is a plain class:
    - it keeps its own copy of the sources, and `character.sources` returns
      another copy to change and build a variant from;
    - every source is a read-only property;
    - the stamp index, the extension tree, `spells` and `ledger` are
      `functools.cached_property`, so each is worked out at most once;
    - `base_abilities`, `base_speed` and `size` are no longer `Optional`.
      Reading one that was never set raises "Character … must be set" through
      a single `_required()` helper, which also replaces the repeated
      `if … is None: raise` blocks in `ledger`, `validate()`,
      `get_base_ability_score()` and `get_base_speed()`;
    - `Character` has no `inventory`. It exposes the reads only: `armors`,
      `weapons`, `items`, and, for the writers, `equipment_entries`,
      `starting_equipment_entry` and `current_gold`.
  - **Deleted:** the version machinery (`_version`, `_changed()`,
    `on_setattr`, the version-keyed caches, `Inventory.version`) and every
    mutator on `Character`.
  - **One change from the plan:** the required fields are checked when read,
    not in the constructor. Unit tests build characters from partial sources
    (for example only a spellcasting ability, to count domain spells), and
    `validate()` still needs to report every missing field on an incomplete
    build.
  - **Tests:**
    - New fixture `make_sources` in `tests/conftest.py`. `make_character(...)`
      is now `Character(make_sources(...))`. `tests/_grants.py` grants into
      sources.
    - About 250 test sites now change sources and then build a `Character`.
      The `apply_features` helpers return a new `Character`. The order tests
      pass `apply_order=`.
    - The cache-invalidation tests are replaced by
      `TestACharacterIsBuiltFromItsSources` (`tests/test_character_model.py`):
      no mutators and no `inventory`, read-only fields, changing the sources
      afterwards changes nothing, the inventory is copied, and an unset
      required source raises when read.
  - **Docs:** `Notes/feature-application-model.md`, and the agent files
    `dnd-builds`, `dnd-builds-haiku`, `dnd-equipment` and `dnd-test-bughunter`.
  - **Verified:**
    - A, B: 3355 passed. E: 1096 slow passed. Both also pass with
      `PYTHONHASHSEED` 1 and 2. D: 0 errors.
    - F: all 3585 pages byte-identical to the baseline.
    - Pyright against a clean HEAD worktree: no new errors, 3 fixed.
    - C: `RunCharacterCreator.py`, `RunBuildGroups.py` and `RunItemSheets.py`
      run. Offscreen, the Creator loads 34 build files, with only the existing
      multiclass warnings, and the combat window builds for its scenario with
      the Players group.


- **Goal:** the versioning machinery disappears. A `Character` is evaluated
  once and can never go stale.
- **Changes:**
  - **`Model/CharacterSources.py`.** It's an attrs class with today's source
    fields and the `add_*` / `replace_*` / `set_*` methods. It's mutable, and
    it has no evaluation and no version. `Grants` wraps it.
    `ClassBuilder`, `SpeciesBuilder` and `CharacterBuilder` write into it,
    and `CharacterBuilder.build()` returns `Character(sources)`.
  - **`Character(sources, *, apply_order=in_given_order)`:**
    - it takes its own copy of the sources (lists and inventory);
    - it checks the required fields once, so its reads are no longer
      `Optional`, and the repeated `if self.base_abilities is None: raise` go;
    - it resolves the `ExtensionTree`, the stamp index and the spells once;
    - it evaluates the `Ledger` on the first query (`functools.cached_property`)
      or eagerly; pick whichever keeps the snapshot test time the same;
    - every attribute is read-only.
  - **`validate()` stays the explicit check** for one armor, attunement, feats
    taken once and requirements, so a build can still be inspected when it's
    invalid.
  - **Delete:** `_count_change`, `on_setattr`, `_version`, `_changed()`,
    `_ledger_key`, `_extension_tree_version`, `_stamp_index_version`,
    `Inventory.version`, and the delegating setters. Builders change
    `sources.class_levels` through `ClassLevels` methods.
  - **Inventory.** `Character` exposes only reads (`armors`, `weapons`,
    `items`, `equipment_entries`, `current_gold`). The inventory's mutators are
    the builder's.
- **Tests:**
  - **Fixtures.** `make_character` becomes `make_sources`, plus
    `Character(sources)`. Rewrite the ~250 test sites that add to a character
    and then query it.
  - **Delete the cache-invalidation tests**, such as
    `test_apply_order_change_re_evaluates` and "in-place change re-evaluates".
    They test machinery that no longer exists.
  - **Add:** `Character` has no `add_*` methods; changing `sources` after
    construction doesn't change the character; the order tests pass
    `apply_order=`.
- **Verify:** A, B, C, D, E, F, `-m slow`, plus the Creator UI and combat UI
  start. **Output:** none.

### Step 12: Builder cleanup *(small items)* — done

- **Result:**
  - **Origin feats:** `Grants.for_origin_feat(feat)` returns the feat's own
    scope (kind `ORIGIN_FEAT`, granted by the feat, same level).
    `OriginFeat.grant_to` grants the feat and its spells through it. The
    `kind=` / `granted_by=` overrides on `add_feature`, `add_spell` and
    `add_cantrip` are deleted.
  - **Species:** `SpeciesBuilder.build(sources, spell_casting_ability)`
    replaces `set_character_level` and `set_spell_casting_ability`.
    - **One change from the plan:** the two values travel on the species'
      scope, not as `_grant` arguments. `SpeciesGrants(Grants)` (in
      `SpeciesBuilder.py`) carries `character_level` (read from
      `sources.class_levels`) and `spell_casting_ability`. Only the 4 species
      that use them (Aasimar, Dhampir, Elf, Tiefling) changed; the other 16
      keep `_grant(self, data: Grants)`.
    - **Found on the way:** the setters overwrote values the species already
      had. Aasimar, Dhampir and Tiefling took a `character_level` constructor
      argument that was always replaced by the real level (4 builds passed 3
      at level 4). Gnome, Hexblood and Khoravar took the player's chosen
      `spell_casting_ability`, which was always replaced by the best mental
      ability. The dead `character_level` parameters are deleted (5 build
      files changed). Gnome, Hexblood and Khoravar now use their own ability,
      as the rules say. Every existing build passes the same value the setter
      wrote, so no output changes.
  - **Subclasses:** `ClassBuilder.__init__` takes `subclass` (so the
    `getattr` goes). `ClassLevels.add_subclass(cls, name, reached=...)`
    records it. `character_subclass` is now a property: the active subclasses
    joined with " / ", or else the first one named. The stored display
    string and `_update_subclass_name` are gone.
  - **`_grant_levels(...)`** is a module function, called once for class
    levels and once for subclass levels.
  - **`StarterClassBuilder`:** the 8 forwarding properties are gone.
    `_grant_class` reads `self.non_generic_arguments`, and so does
    `CharacterBuilder` (for `default_equipment` and `default_pack`).
  - **Skipped (optional):** `is_example` as a class attribute. The one-line
    module-path check works, and a 104-file codemod isn't worth it.
  - **Tests:**
    - `tests/test_species.py` builds through a `species_character(builder,
      level, spell_casting_ability)` helper.
    - New: an origin feat granted through a species is stamped as an origin
      feat and lists its spells under the feat; and `character_subclass`
      shows the first subclass named until one is reached.
  - **Docs:** `dnd-builds` and `dnd-builds-haiku` (`SpeciesGrants`).
  - **Verified:**
    - A, B: 3356 passed. E: 1096 slow passed (`PYTHONHASHSEED=1`). D: 0
      errors.
    - F: all pages byte-identical to the baseline.
    - Pyright against a clean HEAD worktree: no new errors.
    - C: the three runners run. Offscreen, the Creator loads all 34 character
      files, with only the existing warnings, and the combat window builds.
      The Creator round-trip tests pass.


- **Goal:** builders hand data over through arguments and declared fields, not
  through setters, overrides and reflection.
- **Changes:**
  - **Origin feats get their own scope.** `Grants.for_origin_feat(feat)`
    returns a new scope (kind "origin feat", granted by the feat). It replaces
    the `kind=` and `granted_by=` override parameters on `add_feature` and
    `add_spell`, which are deleted.
  - **Species builders take arguments.**
    `SpeciesBuilder.build(sources, spell_casting_ability)` replaces
    `set_character_level` and `set_spell_casting_ability`. Species read the
    level from `sources.class_levels`.
  - **Subclasses are declared.** `ClassBuilder` declares
    `subclass: Optional[str]`, so the `getattr` goes.
    `ClassLevels.add_subclass(cls, name)` replaces the in-place changes, and
    `character_subclass` becomes a derived property of `ClassLevels`, not a
    stored display string.
  - **`BaseClassLevelFeatures.add_features`** calls a `_grant_levels(...)`
    helper twice (class levels, then subclass levels) instead of looping over
    3-tuples.
  - **`StarterClassBuilder`** loses its 8 forwarding properties. Code reads
    `self.non_generic_arguments.<field>` directly. The constructor parameter
    keeps its name, because 144 build files and the codegen use it.
  - *(Optional)* **`is_example`** becomes a class attribute instead of
    module-path sniffing. That's a codemod of 104 example builds plus the
    codegen.
- **Verify:** A, B, C, D, E, plus the Creator round trip. **Output:** none.

### Step 13: `Character` as the combat representation *(design + bug fixes; Decision 2)* — done

- **Result:**
  1. **Extracted.** `Combat/PlayerCombatant.py` (no Qt) has
     `combatant_from_character(character)` and `weapon_summary(weapon,
     character)`.
     - The app adds its own battle `stats` to the dict, and the info dialog
       uses `weapon_summary`.
     - `tests/test_combatant_snapshots.py` snapshots the dict's plain values
       and every weapon line for all 138 builds, in
       `tests/snapshots/combatants.json`.
  2. **Fixed, reviewed against the snapshot taken before the fix.** Only
     these fields changed:
     - **Speed** (27 builds) is `calculate_speed()`, not the species' base:
       Barbarian/Ranger 30 → 40, Monks up to 60, Scout 35 → 45, and so on.
     - **AC** (1 build): the Shield check now looks for a wielded shield,
       not the exact `ShieldArmor` type. Garrick's +1 Shield was missed, so
       "21 (no Shield)" becomes "21 (with Shield) and 18 (without Shield)".
       The AC without a shield is `calculate_armor_class(ignore_shield=True)`,
       not "minus 2".
     - **Weapon damage** (18 weapons) adds every damage bonus (Dueling,
       magic weapons, ...), not only the ability modifier. Every new number
       equals the sheet's weapon card in `build_stats.json` (for example
       Skullcrusher +4 → +10, Perrin's Rapier +4 → +6). The line no longer
       names the ability.
     - Feature names are `feature.name`, and the dialog no longer uses
       `getattr` on features.
  3. **Ledger private.** `Character.ledger` became `Character._ledger`.
     - New listing queries: `languages()`, `senses()`,
       `damage_resistances()`, `damage_immunities()`,
       `condition_immunities()`, `armor_training()` and
       `weapon_proficiencies()` (both frozensets), and
       `tool_proficiencies()`.
     - The sheet writer and every test read through queries. The Hit Point
       bonus tests compare `calculate_hit_points()` with and without the
       feature.
     - **Deleted:** `Model/Recorder.py` (`Recorder`, `@records`,
       `SealedError`, and the repo's last `cast`), and `Ledger.seal()`.
       `CAST_ALLOWLIST` is empty.
     - The contract test "the view exposes answers, not parts" now checks
       against the Ledger's own part types.
  4. **One way to ask:**
     - `spell_slots` is always a dict (the part never returned `None`), and
       `get_spell_slots()` is deleted.
     - `get_spell_casting_ability()` and `get_level_for_class()` had no
       callers and are deleted. `spell_casting_ability` and
       `get_class_level` remain.
  - **Documented:** combat state stays in the UI's dict, never on the
    Character (docstring of `Combat/PlayerCombatant.py`).
  - **Docs:** `Notes/feature-application-model.md`, and the agent files
    `dnd-builds`, `dnd-builds-haiku`, `dnd-equipment` and
    `dnd-test-bughunter`.
  - **Verified:**
    - A: sheet snapshots unchanged, plus the new combatant snapshot. B:
      3493 passed, also with `PYTHONHASHSEED=1`. E: 1096 slow passed
      (`PYTHONHASHSEED=2`). D: 0 errors.
    - F: all 3585 pages byte-identical to the baseline.
    - Pyright against a clean HEAD worktree: no new errors.
    - C: the three runners run. Offscreen, the Creator loads all 34
      character files, and the combat window builds. The combat info dialog
      opens with no errors for all 137 combatants built from the 138 builds.


- **Goal:** combat reads the character as it is, and the two combat bugs are
  fixed.
- **Changes, in this commit order:**
  1. **Extract.** Move `_add_from_character_sheet` (`Combat/CombatUIQt/app.py:112`)
     into a Qt-free `Combat/PlayerCombatant.py`, as
     `combatant_from_character(character) -> dict`. Snapshot its output for
     every build to `tests/snapshots/combatants.json`. No behavior change.
  2. **Fix the combat values:**
     - speed is `calculate_speed()`;
     - AC without a shield is `calculate_armor_class(ignore_shield=True)`, and
       "with Shield" is shown only while wielding one;
     - feature names use `feature.name` (no `getattr`);
     - weapons use the weapon's own queries against the character
       (`calculate_total_attack_roll_bonus_int(character)` and so on; Step 10
       was skipped).

     Regenerate the combatant snapshot, and review the diff: only speed and
     no-shield AC may change.
  3. **Listing queries** (Decision 2): `senses()`, `damage_resistances()`,
     `damage_immunities()`, `condition_immunities()`, `languages()`,
     `tool_proficiencies()`, `armor_training()`.
     - The writers stop reading `character.ledger` (12 reads; the weapons'
       3 went in Step 9), and the ledger becomes private.
     - Delete `Recorder`, `@records` and `SealedError`: only `Effects` writes,
       only inside `Character`, so nothing is left to guard. If you keep the
       ledger public instead, keep `Recorder`, but make `seal()` list its
       parts explicitly.
  4. **Deduplicate the query API**, one way to ask each thing:
     - `spell_slots` (property) vs `get_spell_slots()`;
     - the `spell_casting_ability` field vs `get_spell_casting_ability()`;
     - `get_level_for_class` vs `get_class_level`.
- **Documented:** combat state (current HP, conditions, slots spent) belongs to
  a combat-side object holding a `Character`. Moving the UI off dicts is a
  follow-up (section 7).
- **Verify:** A, B, C, D, plus the combat UI starts, plus the combat tests.
  **Output:** sheets none; `combatants.json` changes as reviewed in commit 2.

### Step 14: Card labels come from the stamp *(optional; reviewed output change; Decision 4)* — skipped

- **Result:** not done. Its premise - that `origin` repeats what the stamp
  knows - only holds for a feature on a built character. The class handouts
  (`Scrapers/GenerateClassHandouts.py`) create every feature class on its own,
  with no stamp, and read `origin` for each card's label and to find the level
  it sorts the handout by. Deleting the `origin` strings would break every
  handout. Doing this step first needs the handouts to take each feature's
  level from the class's level tables instead.

- **Goal:** delete the `_LEVEL_LABEL` regex and the 860 hard-coded
  `origin="<Class> Level N"` strings, which repeat what the stamp already knows.
- **Changes:**
  - `GrantStamp` gains `label`: the class name ("Barbarian") for class
    levels, and the subclass display name ("Wild Magic Sorcerer") for
    subclass levels.
  - A card's label is `"{label} Level {level}"` for class and subclass grants;
    otherwise it's the feature's own `origin`, which is free text such as
    "Human Trait" or "Maneuver".
  - A codemod deletes each `origin=` whose text the stamp reproduces exactly.
    Proof: the pages stay byte-identical with it deleted. Every other origin is
    listed for review, not deleted.
  - Delete `_LEVEL_LABEL` and `_label_for` once no "… Level N" origin
    remains.
- **Verify:** A, B, C, D, plus a card-by-card compare against the dump, as in
  the first plan's Step 13. Only reviewed labels may change; stats never.

### Step 15: Pylance clean *(fixes; Decision 3)* — done, 8 errors left for decisions

- **Result:**
  - **Root `pyrightconfig.json`** (standard mode). `typecheck.sh` uses it, and
    `pyright-model.json` is deleted. Excluded: `Scrapers/` and
    `Combat/Tools/scrape_monsters.py` (hand-run scrapers whose BeautifulSoup
    lookups the stubs type as Optional at every step) and generated scratch
    output.
  - **538 errors → 8.** By area:
    - **Combat UI (~370):** `Combat/CombatUIQt/state.py` adds
      `CombatWindowState`, inherited by every mixin. It declares the 35 shared
      attributes, with types, and the 59 cross-mixin methods, with their exact
      signatures. The card's reassigned `mousePressEvent` lambda became a
      `_CombatantCard` widget. The undo history is typed
      `list[tuple[Action, Any]]`. An empty initiative order made
      `_card_state_flags` return `[]` instead of `False`.
    - **Build discovery (~27):** `BuildSelector`/`ExampleSelector` return
      build classes (`BuildClass`, `Builds/CharacterBuilder.py`), so a fresh
      build is `ALL_BUILDS[name]()`. `is_build_class` is the one `TypeGuard`,
      used where builds are found with `inspect`.
    - **Tests (~50):** `FakeView` is a complete `CharacterView`: the members
      no part reads raise.
    - **Content (~15):** `CreatureForm` (`Model/Creatures/Combatants.py`)
      types Wild Shape forms. `ItemImprovement.apply` takes its item
      positional-only, so subclasses may call it `armor`/`weapon`. The dead
      first `FightingSpirit.regained_on` is deleted. Five build spells used a
      school enum where the class-list enum has the same spell.
    - **`FeatureGeneration/Output.py`** (Decision 6): deleted and git-ignored;
      `GenerateFeatures.py` recreates it.
  - **Left for decisions (8):**
    - `Builds/Characters/Y2024_Cleric_Light_GabrielGreybeard.py`: Silence (a
      level 2 spell) at Cleric level 2, which has only level 1 slots.
    - `Builds/Examples/Y2024_Druid_Land_RowanThistledown.py`: Fire Bolt as a
      Druid cantrip; it isn't on the Druid list.
    - `Combat/Monsters/CR_0` (5): summoned creatures whose DC "equals your
      spell save DC" don't fit `dc: int`.
    - `Combat/Monsters/CR_12` (1): a condition immunity with a qualifier
      ("Charmed (with Mind Blank)") doesn't fit `list[Condition]`.
    - Both monster files are generated by `generate_monsters.py`, so the fix
      goes in the generator and the creature types.
  - **Verified:** A (sheet hashes unchanged), B (3493 passed), C (every app
    starts), D (the 8 above).

- **Goal:** zero errors where the editor looks, checked by the same
  configuration.
- **Changes:**
  - **Fix what's left of the 46 non-Combat errors** after Steps 5–13. Expected
    leftovers:
    - the `Optional` accesses in `Builds/CharacterCreator/Ui.py`;
    - `Utils/StringUtils.py` and `TableUtils.py` defaults typed `None` but
      annotated `str`/`tuple`;
    - `Maneuvers.py:15`;
    - `PrimalCompanions.py:280,288`;
    - the duplicate `regained_on` in `FighterSamuraiFeatures.py:65`;
    - `Armor` passing an `Optional[ArmorType]`: armor without a type is a
      construction error;
    - the `Scroll` reads in the writer: narrow the parameter to `Scroll`, and
      decide what to do with a scroll-category item that isn't a `Scroll`;
    - `RunCharacterCreator.py:114`: the registry stores builder classes, not
      instances, or the build classes declare a no-argument constructor;
    - `ItemImprovement.apply` overrides: type their parameter as the
      improvement's target (`Weapon` or `Armor`) through a generic base, or
      widen the subclasses to `Item`.
  - **Combat UI mixins (369 errors).** Add `Combat/CombatUIQt/state.py` with a
    `CombatWindowState` class. It declares the shared attributes
    (`characters`, `selected_character`, `target_characters`, `history`,
    `player_log_file`, `_grid_layout`, ...) and the cross-mixin methods
    (`_log_event`, ...) with types. Every mixin inherits it. That's the
    standard way for a mixin to declare what it needs from its host.
  - **`CharacterContent/Features/FeatureGeneration/Output.py`:** delete it, or
    exclude it from checking (Decision 6).
  - **Root `pyrightconfig.json`** (standard mode; excludes `Output`,
    `SourceTexts`, `.claude` and `Scrapers` if out of scope).
    `typecheck.sh` uses it, and `pyright-model.json` is deleted.
- **Verify:** D reports 0 errors repo-wide, plus A, B, C. **Output:** none.

### Step 16: Docs, agent instructions, final layering *(docs)* — done, except the layering allowlist

- **Result:**
  - **Agent instructions:** the sheet is written with
    `HtmlCharacterSheetWriter().write_character_sheet(...)`. Six agents still
    called `create_character_sheet()`, which no longer exists, and
    `import Definitions`. `dnd-subclass-creator` pointed at a deleted
    `SubFeatures.py`. The combat agents now describe `state.py`.
  - **`Builds/README.md`** and **`_TEMPLATE.py`:** builds are registered as
    classes.
  - **`Notes/model-refactor-plan.md`** is marked superseded.
  - **Not done:** `LAYER_ALLOWLIST` still has the 4 content files that render
    creature stat blocks (`Presentation.CreatureStatBlocks`) in their
    descriptions. Emptying it means moving that rendering into
    `Presentation/`, which is a code change, not a docs pass.
  - **Open question:** `CharacterContent/temp.plan.md` is stale (it predates
    both plans). Delete it?

- **Rewrite** `Notes/feature-application-model.md`: "Where things live"
  (section 2b/2c), the pipeline, and "What enforces all this".
- **Update the agent instructions:** `.claude/agents/dnd-builds.md`,
  `dnd-builds-haiku.md`, `dnd-feature-extender.md`, `dnd-subclass-creator.md`,
  `character-creator.md`, `combat-sim.md`, `dnd-equipment.md` and
  `dnd-test-bughunter.md`. Also update `Builds/README.md` and
  `QUICKSTART.txt`.
  - Agents write content in parallel, so update a document **in the step that
    changes the API it describes**, not only here. This step is the final
    pass.
- **Every layering allowlist is empty.** Mark `Notes/model-refactor-plan.md`
  as superseded, where they conflict, by this plan's 2b–2d.
- **Ask about** the stale `CharacterContent/temp.plan.md`.

---

## 4. Verification (every step)

```bash
# A. snapshots unchanged (stats + sheet hashes), unless the step says otherwise
python -m pytest tests/test_build_snapshots.py -q && git diff --exit-code tests/snapshots
# B. full suite (layering, contracts, order invariance, merge rules, round trip)
./run_tests.sh -q
# C. smoke: every build renders; the apps start
python RunCharacterCreator.py && python RunBuildGroups.py
python RunCharacterCreatorUI.py   # start and close
python RunCombatSimulator.py      # start and close (Steps 5, 11, 13)
# D. type check (Model only until Step 15; the whole repo afterwards)
./typecheck.sh
# E. order matrix: steps touching evaluation or granting (2, 3, 4, 8, 9, 10, 11)
./run_tests.sh -m slow -q
# F. pages byte-identical: steps 6, 8, 9, 10, 11, 14
SNAPSHOT_DUMP_DIR=<scratchpad>/after python -m pytest tests/test_build_snapshots.py -q
diff -r <scratchpad>/baseline <scratchpad>/after
```

- **Stats goldens never move.** In this plan, only Step 13's combatant
  snapshot and Step 14's reviewed labels may change output.
- **When output changes on purpose:** regenerate with `UPDATE_SNAPSHOTS=1`,
  explain the `diff -r` in the commit message, and dump a new baseline for the
  steps after it.
- **Snapshots under both hash seeds** (`PYTHONHASHSEED=1` and `=2`) for
  Steps 2, 8 and 11, which touch set/dict iteration.
- **Runtime:** today the default suite takes about 45 s for 3121 tests, and
  `-m slow` about 80 s. If a step makes either more than 20% slower, it isn't
  done.

## 5. Risks and delegation

| Steps | Kind | Who |
|---|---|---|
| 0, 1, 15 | Mechanical, test-heavy | Can be delegated to Sonnet-tier agents (`dnd-test-bughunter` for Step 0's tests). Review the diff yourself afterwards. |
| 2, 3, 4 | Internal rewrites in `Model/` | Directly. They're small, but they touch the evaluation core. |
| 5, 6, 9 | File moves plus import codemods | The design and the first file by hand. The codemod is a script, not an agent edit. Run it once, then `format.sh`. |
| 7 | Annotation codemod (2219 sites) | Script. Use pyright to find stragglers. |
| 8, 10, 11 | Design-critical | Directly, or one Sonnet agent under review. Never split them across parallel agents. Step 11's test migration (~250 sites) can be delegated in batches once `CharacterSources` exists. |
| 12, 13, 14, 16 | Small, but they change APIs, combat or docs | Directly |

- **Haiku agents:** not for any of these steps. They have clobbered core files
  and overcorrected before, and they wrote tautological tests. Verify every
  agent's report against the diff, not against its own summary.
- **Codemods must exclude `.claude/worktrees`.** Another agent's branch may be
  checked out there.
- **Module moves break things the tests don't import:**
  - the Registry finds classes by `cls.__module__` (Step 0's round trip covers
    this);
  - the agent docs (update them in the same step);
  - open worktrees (rebase them after Steps 6 and 9).
- **`CharacterView` creep.** Every member is something every formula and
  description may depend on. Add a member only when content reads it, and
  never expose a part.
- **The immutable `Character` (Step 11)** removes the cheapest way to poke at a
  character in a REPL. `make_sources()` plus `Character(sources)` is the
  replacement. Put it in the test helpers and the docs.

## 6. Decisions for you

1. **Immutable `Character` built from `CharacterSources` (Step 11).**
   - *(Recommended.)* It deletes the version counter, the `on_setattr` hook,
     three caches and the inventory version, and a `Character` can't go stale.
     The cost is ~250 test sites rewritten.
   - Alternative: keep the mutable `Character`, but merge the three caches
     into one, keyed by one version that every mutator bumps explicitly.
2. **Make `Character.ledger` private, and add listing queries (Step 13).**
   This reverses the first plan's Decision 2.
   - *(Recommended.)* `Character` becomes the only read API for the sheet and
     combat; parts become an internal detail; `Recorder` and `SealedError` can
     go. Only 15 reads outside `Model/` use the ledger today: 3 in weapons,
     which Step 9 removed, and 12 in the writers.
   - Alternative: keep `character.ledger.<part>` public for breakdowns, and
     keep `Recorder`.
3. **A root `pyrightconfig.json` in standard mode (Step 15).**
   - *(Recommended.)* Pylance and check D then report the same thing.
   - It changes what the editor shows, which is why the first plan avoided it.
     After Step 15 there's nothing left to hide.
4. **Labels from stamps (Step 14).**
   - *(Recommended, optional.)* It deletes 860 strings and a regex, and any
     wrong hard-coded origin shows up in the review.
   - Skip it if you'd rather keep `origin` text as the source of truth.
5. **Content packages keep re-exporting base names** (`Weapons.AbstractWeapon`,
   `Weapons.WeaponProficiency`, ...).
   - *(Recommended.)* This keeps the 144 build files and the codegen as they
     are.
   - Alternative: codemod the build files and the codegen to import from
     `Model.Content` / `Core.Weapons`.
6. **`FeatureGeneration/Output.py`:** delete it *(recommended, if it's
   generator scratch output)* or exclude it from type checking.
7. **Combat's extra conditions** (Bloodied, Concentrating):
   - a separate `CombatStatus` enum *(recommended)*;
   - or keep Combat's own `Condition` enum and convert at the boundary.

## 7. Considered and left out

- **The 40 `BaseClassLevelN` / `SubclassLevelN` classes** in `ClassBuilder.py`.
  They're boilerplate, but not clever: each is three obvious lines. The level
  is stated twice (dict key and class), and `add_features` checks that the two
  agree, which catches a mis-mapped level. Removing them would rewrite ~935
  class headers for no readability gain.
- **Renaming `Model/` to `Engine/`.** That's ~2000 import lines for a name.
- **`AppliedLevelFeatures`** (deduplicating levels when a class is resumed
  after a dip). It works and it's documented; changing it changes the meaning
  of build files.
- **`Effects`' 40 forwarding methods.** They are the order-independence
  guarantee (a write-only door), not cleverness.
- **Renaming the `get_` / `calculate_` query prefixes.** That's 2000+ call
  sites for naming alone. Step 13 removes only the duplicates.
- **`Item` inheriting from `Feature`.** That's inheritance for reuse. Revisit
  after Step 6: if `Item` no longer needs anything from `Feature` except
  `name`/`apply`, make it subclass `Effect` directly.
- **Moving the combat UI from dicts to objects.** Step 13 gives it a clean
  `Character` and `AttackProfile` to read. Replacing the per-combatant dicts is
  a combat refactor of its own.
