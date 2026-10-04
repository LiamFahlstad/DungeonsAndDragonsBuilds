# Plan: Character, Effects, parts and Features, second pass

Follow-up to `CharacterContent/temp.plan.md`, whose steps 0–10 are done. That
pass made `apply()` write-only and every value resolve when it is read. This
pass fixes what is still unclear or still depends on order:

1. **Order independence end to end.** Today only the stat pass is proven order-free.
2. **One rule for where a value lives.** Today some values live on `Character` and some in a part.
3. **No `if TYPE_CHECKING:`.** The circular imports get removed, not hidden.

Every step is its own commit and ends green (see "Verification" at the end).

---

## 1. Current state

### 1a. Ordering: what is proven and what isn't

`tests/test_feature_apply_order.py::test_effect_order_does_not_change_stats`
shuffles `iter_stat_effects()` (the apply pass) for every build, but it only
compares `_stats()`. These other kinds of order are not tested:

| Order-dependent spot | Where | Effect |
|---|---|---|
| Ties in the feature card order | The sheet already sorts each level's cards by `(passive, name)` (`CharacterSheetWriters.py:1228`, and `_sort_features_key` at line 67 for the full sheet), but Python's sort is stable, so ties keep grant order. The level is parsed from the `origin` text (`_feature_level`, line 81) | Step 0 measured it: 53 of 136 builds change under a grant-order shuffle. The causes are two features with the same name on one level (Expertise, Alert, Spell Slots, Tough, Lucky), and extensions nested under a parent, which are listed in the order they were attached |
| `get_features_by_type(X)[0].extend_feature(child)` | 221 lookups in `CharacterContent/Classes/**` (e.g. `BarbarianBase.py:94`); 235 `extend_feature` calls in all | The parent must be granted before the child; if it isn't, the build fails with an `IndexError` |
| Conditional lookups: "extend whichever one was granted" | `ClericBase.py:275` (Level 14 checks for `DivineStrike`, then `PotentSpellcasting`), `DruidBase.py:273` | The result depends on what was granted *before* the call, not on the build's choice |
| Features changed after they are granted, other than by extensions | `PaladinBase.py:145` `get_features_by_type(ChannelDivinity)[0].add_spell("Abjure Foes")` | The same order dependence as extensions, plus a change the cache key can't see (it counts `Character` and `Inventory` changes, not feature changes) |
| Extensions change a feature after it has been granted | `BaseFeatures.extend_feature` calls a global counter `note_feature_extended()` (`Character.py:61`) to invalidate every cache | A hidden global, and `BaseFeatures` has to import `Model.Character` at runtime. Extensions live on the feature *instance*, so an instance shared between two characters shares its extensions |
| Spells | `add_spell` rejects duplicates depending on what was added before (`_duplicate_spell_check_start`, `separate_spell_source`); `replace_spell` needs the old spell to already be there; the grant level comes from the mutable `_current_grant_level` | The builder's call order matters |
| Last-wins parts | `Spellcasting.register_caster` (last `CasterType` for a class wins), `WornArmor.set_body_armor` (last wins) | Harmless today only because no build has conflicting grants. (`EquipmentTraining.add_tool_proficiency` keeps the first instance of each tool type. Tool types take no parameters, so that is really a set union keyed by type, not a conflict.) |
| Insertion-ordered source lists | `Bonuses._flat/_formulas`, `Defenses`, `Languages`, `Senses.sense_sources`, `CarryingCapacity`, `WeaponBonuses`, the `ArmorClass` formula list | The snapshot test sorts skill sources before comparing, so it can't tell whether the HTML depends on this order. The writer already sorts languages, senses, damage types, tools and spells, so the risk is limited to the remaining lists |

### 1b. Where values live: three rules mixed together

- **Sources on `Character`:** `character_name`, `is_example`, `class_levels`, `base_abilities`, `base_speed`, `size`, `features`, `spells`, `invocations`, `spell_casting_ability`, `fixed_spell_slots`, `weapon_masteries`, `fighting_styles`, `inventory`, `experience_points`.
- **Builder process state on `Character`:** `_current_grant_level` and `_duplicate_spell_check_start`. These aren't facts about the character at all.
- **Sources copied into parts** (`_get_parts`, `Character.py:407-415`):
  - `base_abilities` is deep-copied and then mutated as `abilities`.
  - `base_speed` becomes `Speed.base`.
  - `spell_casting_ability` and `fixed_spell_slots` are copied into `Spellcasting`.

  So `character.base_speed` is an int while `character.speed` is a part, and `base_abilities` and `abilities` are the same class with different meanings.
- **Sixteen part properties sit flat next to the sources:** `character.skills`, `.senses`, `.armor_class`, and so on. You can't tell from the name whether something is a build input or an evaluated result.
- **Queries have three shapes:**
  - one-line delegates (`is_proficient_in_skill`);
  - logic written directly in `Character` (`get_skill_modifier`, `get_saving_throw_modifier`, untrained armor, `warnings`, `initiative_roll_condition`);
  - part methods that each take a different set of pre-resolved arguments (`HitPoints.calculate(class_levels, con_mod, character)`, `Initiative.total(prof, character)`, `ArmorClass.calculate(abilities, character, wielding, trained)`, `CarryingCapacity.total(str_mod)`).
- **The evaluated parts can be written to by anyone.** `character.abilities.add_bonus(...)` succeeds, but the change is silently lost at the next rebuild. Tests also use `SomeImprovement.apply(character.effects)` (152 test sites) to write into a cache that will be thrown away.

### 1c. Why `TYPE_CHECKING` is needed

- **Model ↔ Model.**
  - `DerivedBonus = Callable[["Character"], int]` (`Bonuses.py:14`), and the `character: "Character"` parameters in `ArmorClass`, `HitPoints`, `Initiative`, `SavingThrows`, `Skills` and `Speed`, name the concrete `Character`.
  - `Character` imports `Effects`, and `Effects` imports those parts.
- **Model ↔ CharacterContent.** `Character.py:46-54` names `Feature`, `OriginFeat`, `FightingStyle`, `AbstractArmor`, `AbstractWeapon` and `Item`. `Inventory.py:19` names the item packages. `BaseFeatures.py` imports `Model.Character` at runtime.
- **Inside CharacterContent:** `Items/Weapons/Improvements.py:8` (`AbstractWeapon` ↔ `ExtraDamage`) and `Spells/SpellFactory/Writer.py:156`.
- **Utils:** `BuildGroupSheetWriter.py:7`.
- **Nothing checks types.** There is no pyright or mypy config, so nothing verifies the annotations that `TYPE_CHECKING` protects, or the Protocols that replace them (see Decision 4).

---

## 2. Target design

### 2a. Layers (imports only point down)

```
L0  Core/                 enums and rules tables
L1  Model/Contracts.py    Protocols only: StatView, Formula, Effect, Gear
L2  Model/<Part>.py       parts: recorded data + a documented commutative merge rule
                          + resolvers that take one StatView. Import only L0 and L1.
L3  Model/Effects.py      Ledger (all parts, sealed after evaluation, plus the rules
                          that combine two parts) + Effects (write-only)
    Model/Sources.py      Protocols for content: Effect, GrantedFeature, Gear, ArmorGear
L4  Model/Character.py    sources + cached Ledger + query facade (satisfies StatView)
L5  CharacterContent/, Builds/, Utils/, Combat/
```

- `Model` never imports `CharacterContent`, not even for type hints. It names content only through the `Model/Sources.py` Protocols, which features and items satisfy structurally without importing them.
- Formulas are `Callable[[StatView], int]`, so parts never need `Character`.
- `StatView` exposes answers (numbers, booleans, sources), never parts. A rule that needs two parts (untrained armor needs `WornArmor` and `EquipmentTraining`) lives on the `Ledger`, which owns both.
- Nothing in the repo uses `if TYPE_CHECKING:`. A test enforces this.

### 2b. The rule for where each thing lives

`Character` has exactly three kinds of public member:

| Kind | Question it answers | Where it lives | Example |
|---|---|---|---|
| **Source** | What did the player choose, or what were they granted? | A field on `Character`, set through `add_*`/`set_*` | `class_levels`, `base_abilities`, `species` (size, base speed), `features`, `spells`, `inventory` |
| **Ledger** | What did the effects record? | `character.ledger.<part>`: read-only and sealed. Parts hold only what effects recorded, never a copy of a source and never a final value | `character.ledger.skills`, `character.ledger.senses` |
| **Query** | What is the final number or answer? | A method on `Character`, one line: `return self.ledger.<part>.<resolve>(self)` | `get_skill_modifier(skill)`, `calculate_armor_class()` |

Rules of thumb:

- Anything derived is not stored on `Character`.
- No source is copied into a part.
- Builder bookkeeping (the current grant level and source, spell duplicate scopes) lives in the builder, not on `Character`.
- A feature is never changed after it is granted. Anything a later level adds is its own grant (an extension, or a spell), so the cache key never has to see inside a feature.

### 2c. Order independence as a design property

- **The apply pass:** every part documents one merge rule, and each rule is commutative:

  | Part | Merge rule |
  |---|---|
  | Proficiencies, training, languages, defenses | set union |
  | Tools | set union, keyed by tool type (tool types take no parameters) |
  | Bonuses | sum |
  | Senses | best plain grant + sum of extensions |
  | Armor Class | best applicable formula; a tie is broken by formula name |
  | Roll conditions | set, then advantage and disadvantage cancel |
  | Casters | one `CasterType` per class; a conflicting grant raises an error |
  | Worn body armor | at most one grant; more than one raises an error |

  Reads that reach the sheet come back in canonical order (enum order or `(source, value)`), never insertion order.
- **Granting:** a build is a set of grants. Extensions are declared (`add_feature(child, extends=Parent)`), not attached to an instance that must already exist. Spells are a set keyed by (name, source). Replacements are declared. Every grant carries its grant level and source, stamped by a builder-side `Grants` scope (Step 9).
- **Display:** the sheet sorts features, extensions and spells by a canonical key (grant level, source kind, class, name), not by call order. See Decision 1.

---

## 3. Steps

### Step 0: Safety net *(mechanical)* — done

- **Result:** apply order leaks nowhere: all 136 builds pass, in the default shuffle and the slow matrix. Grant order leaks in 53 builds under the default shuffle, all of them ties (see 1a). These are listed in `_GRANT_ORDER_LEAKS` as strict xfails. The slow grant orders are non-strict xfails. Baseline tag: `refactor-baseline`.

- **Goal:** tests that prove order independence on rendered output and the layering rule, before anything changes.
- **Files:** `tests/_snapshot_helpers.py` (new, factored out of `test_build_snapshots.py`), `tests/test_order_invariance.py` (new), `tests/test_model_layering.py` (new).
- **Changes:**
  1. Move `_compute_stats` and the render-and-hash helpers into `tests/_snapshot_helpers.py`. Both the snapshot test and the new tests use them.
  2. Add a `SNAPSHOT_DUMP_DIR=<dir>` option to the helpers, which writes every rendered page there as well as hashing it. The hashes only tell you *that* a page changed. `diff -r` between a baseline dump and a new dump tells you *what* changed, and that is what the reviews in Steps 2, 9 and 10 need. Tag the commit `refactor-baseline` and dump it once, to the scratchpad, not into the repo.
  3. `test_apply_order_keeps_sheet[build]`: for every build, apply effects in one seeded shuffle (seeded from the build name), render in full and concise mode, and compare to `sheet_hashes.json`. Reversed order plus 3 more shuffles run under `@pytest.mark.slow`. Today one render pass of all builds takes about 90 s, so the full matrix would add about 6 minutes to every run. Expected to pass. If it fails, that is a real leak: mark the build `xfail(strict=True)` and list it in the commit message for Step 2.
  4. `test_grant_order_keeps_sheet[build]`: shuffle the whole `character.features` list, every extension list, and `character.spells`, then compare the HTML. Shuffle the whole list, not just within each level: the level buckets must come from the grant, not the list position. Expected to fail today, so mark it `xfail(strict=True, reason="Step 10")`.
  5. `test_model_layering.py`, in three parts:
     - no `TYPE_CHECKING` anywhere in project code (`.claude/` excluded);
     - `Model/**` has no import of `CharacterContent`, `Builds` or `Utils`;
     - both start with an explicit allowlist of today's offenders (section 1c). Every later step shrinks the allowlist, and the test fails if an allowlisted file is already clean, so the list can't go stale.
  6. Register the `slow` marker in `pytest.ini`.
- **Verify:** A, B, C, plus snapshots under `PYTHONHASHSEED=1` and `=2`, plus `-m slow` once.

### Step 1: Test seams and a sealed ledger *(small)* — done

- **Result:** the base class is `Model/Recorder.py` (`Recorder`, with a `@records` decorator on every part mutator, and `SealedError`). The cache key includes `_apply_order`, so changing it re-evaluates. All 159 `X.apply(<c>.effects)` test sites now use `add_effect`, and so do the 14 direct part writes and the `make_character` armor-training fixture. Snapshots are unchanged. Found a bug on the way: changing `base_abilities` in place doesn't bump the version, so the cache goes stale. It is recorded as a strict xfail for Step 5 (`test_changing_a_base_score_in_place_re_evaluates`).

- **Goal:** the tests stop monkeypatching internals, and nothing can write into the evaluated record after evaluation.
- **Changes:**
  1. Add `Character._apply_order: Callable[[list], list]` (identity by default), used by `_get_parts`. Declare it like `_version` (`init=False, eq=False, repr=False`), so it is not a source and doesn't bump the version. Move the shuffle tests off `monkeypatch.setattr(data, "iter_stat_effects", ...)` and onto it.
  2. Add `Character.add_effect(effect)`: a real source list for loose effects, used by tests and tools and included in `iter_stat_effects`. Codemod every `X.apply(character.effects)` in `tests/` to `character.add_effect(X)`, then delete the `Character.effects` property. Exclude `.claude/worktrees` from the script.
  3. Rename `Parts` to `Ledger` and add `seal()`, called at the end of `_get_parts`. Every part mutator checks a small `_Recorder` base class and raises after sealing. Fix the tests that call `character.abilities.add_bonus(...)` directly (6 sites).
- **Tests:** a mutator raises after evaluation, and `add_effect` survives re-evaluation.
- **Verify:** A, B, C. No snapshot change.

### Step 2: Explicit, commutative merge rules in every part *(design-critical)* — done

- **Result:** every part has a "Merge rule:" line in its docstring, and every source read is canonical. Two items changed from the plan below:
  - **No AC tie-break.** `ArmorClassFormula` has no name, and only the best formula's *value* is used, so order can't matter there.
  - **The writer's sorts stay.** It sorts languages and damage types alphabetically, which is a presentation choice and differs from enum order, so dropping those sorts would change the output for no gain.
- **Also changed:** `Skills`/`SavingThrows` lost their unused constructor parameters, and `reset_skill_to_ability`/`reset_all_skill_to_ability` were deleted: they are removals, which can't be order-free, and only one test used them. `tests/test_part_merge_rules.py` has 22 permutation tests, and 13 of them fail on the pre-Step-2 code. Snapshots didn't move at all, neither stats nor sheet hashes: no build had a tie the new reads reorder.

- **Goal:** no part has first-wins or last-wins behavior, and no read that reaches the sheet uses insertion order.
- **Files:** `EquipmentTraining.py`, `Spellcasting.py`, `WornArmor.py`, `Bonuses.py`, `Defenses.py`, `Languages.py`, `Senses.py`, `CarryingCapacity.py`, `WeaponBonuses.py`, `ArmorClass.py`, `Skills.py`, `SavingThrows.py`.
- **Changes:**
  - `add_tool_proficiency`: store `dict[type, ToolProficiency]`, a set union keyed by tool type. Granting the same tool twice is normal, for example Thieves' Tools from both Rogue and the Criminal background, so it must not raise. `Feature` has no `__eq__`, so an "equal instances" check would raise on every duplicate.
  - `register_caster`: the same class registered with two different `CasterType`s raises an error (Decision 3).
  - `WornArmor`: record every body-armor grant. The resolved value is "the one grant", and more than one raises. `validate()` already rejects more than one worn armor, so check that items and weapons never call `set_worn_armor`.
  - `ArmorClass`: break a tie between two equally good formulas by formula name, so the name shown on the sheet doesn't depend on order.
  - Replace `dict[Ability, bool]` in `SavingThrows` with sets, which fits the "set union" rule.
  - Every source-listing read returns a canonical order: enum definition order for enum keys, otherwise `(source, value)`. Never sort `str`-valued enums through set iteration (see the hash-seed note in `test_build_snapshots.py`). Where the writer already sorts (languages, senses, damage types, tools), drop the writer's sort once the part's read is canonical, so the order lives in one place.
  - Put the merge rule in each part's class docstring, in one line.
- **Tests:** one permutation test per part, with small inputs, `itertools.permutations`, and canonical-read equality. Add a failing case for each "conflict raises" rule, and a passing case for "the same tool from two sources".
- **Verify:** A, B, C, and the snapshots under both hash seeds.
  - The stats goldens must not move.
  - If sheet hashes move, the only acceptable cause is canonical ordering of source lists. In that case regenerate them with `UPDATE_SNAPSHOTS=1`, `diff -r` a dump against the baseline dump, confirm that only order changed, and say so in the commit message.

### Step 3: `StatView` and `Formula` break the Model cycle *(design-critical, small surface)* — done

- **Result:** the members were measured rather than guessed. A recording proxy on every formula evaluation, run over all builds and the full test suite, showed formulas read `character_level`, `get_class_level`, `get_proficiency_bonus`, the ability modifiers, `get_skill_ability`, `is_wearing_armor`, and two whole parts (`skills`, `worn_armor`). The parts were replaced with answers: `is_proficient_in_skill` already existed, and the new `Character.worn_armor_type` and `Character.is_wielding_shield` were added. That meant changing six formula sites in content. `get_ability_score`, `is_wearing_untrained_armor` and `has_shield_training` are *not* in `StatView`, because no formula reads them. `Improvements.Value` is `int | Formula`, and the formula functions in content are typed `StatView`. `tests/test_contracts.py` calls every member on a real `Character`, checks that `Effects` has none of them, and checks that no member returns a part.

- **Goal:** parts no longer know `Character` exists.
- **Files:** new `Model/Contracts.py`; `Bonuses.py`, `ArmorClass.py`, `HitPoints.py`, `Initiative.py`, `SavingThrows.py`, `Skills.py`, `Speed.py`.
- **Changes:**
  - `class StatView(Protocol)` holds exactly the reads that formulas and resolvers use. Build the list by grepping the 14 content lambdas and the 25 `add_derived_*` sites; expect `get_ability_modifier` and the six `get_<ability>_modifier` helpers, `get_ability_score`, `get_proficiency_bonus`, `character_level`, `get_class_level`, `is_wearing_armor`, `is_wearing_untrained_armor`, `has_shield_training`, `is_proficient_in_skill`.
  - `Formula = Callable[[StatView], int]`, with `DerivedBonus` kept as an alias until Step 11.
  - Every `character: "Character"` parameter in `Model/` becomes `view: StatView`. The seven `TYPE_CHECKING` blocks in `Model/` (all except `Character.py` and `Inventory.py`) are deleted, and the allowlist shrinks to match.
- **Tests:**
  - A `Character` passes a conformance check against `StatView`. Use a test that calls every Protocol member, not just `runtime_checkable`, because that only checks names.
  - `Effects` does not satisfy `StatView`, so a formula can never read in the middle of `apply()`.
- **Callers:** none. Content lambdas keep working because `Character` satisfies the Protocol structurally.
- **Verify:** A, B, C, plus D.

### Step 4: Content Protocols, so Model never names CharacterContent *(design-critical)* — done

- **Result:** there is no `TYPE_CHECKING` anywhere in the repo, and both layering allowlists are empty. Four things changed from the plan below:
  - **The content Protocols live in a new `Model/Sources.py` (L3½), not in `Contracts.py`.** They are `Effect`, `GrantedFeature`, `Gear` and `ArmorGear`. `Effect.apply` takes `Effects`, and `Contracts.py` (L1) can't import `Effects` (L3), because `Effects` imports the parts that import `Contracts`. `Character` and `Inventory` import `Sources`.
  - **`add_origin_feat` became `OriginFeat.grant_to(data)`, not a `CharacterBuilder` method.** Its two callers are a class builder and a species builder, so it belongs to the feat itself.
  - **The spell cycle was removed by deleting `Spell.write_to_file`.** It only forwarded to the writer. Its two callers now call `write_spell_to_file(spell, ...)`, so `Writer.py` imports `Spell` and not the other way round.
  - **`FightingStyle` got a no-op `apply()`, like `Feature` has.** So every fighting style is an `Effect`, and `iter_stat_effects` lists them all, without `hasattr`.
- **Also:** `ExtraDamage` moved to `Items/Weapons/ExtraDamage.py` and is re-exported from `Improvements.py`. `tests/test_contracts.py` checks that every build's features, armor, weapons, items and fighting styles have the members the Protocols name. Snapshots didn't move, the pages are byte-for-byte identical to the pre-Step-3 baseline dump, and the Creator UI starts.

- **Goal:** `Character.py` and `Inventory.py` have no content imports, and the rest of the repo drops `TYPE_CHECKING`.
- **Changes:**
  - In `Model/Contracts.py`, add `Effect(Protocol)` (`name`, `apply(effects)`) and `Gear(Protocol)` (the fields `Inventory` and `_validate_sources` actually read: `name`, `is_wearing`, `is_shield`, `requires_attunement`, value/weight fields, `apply`). Widen them only as far as the grep shows is needed.
  - `Character.features: list[Effect]`, `fighting_styles`, and the typed lists in `inventory` use the Protocols.
  - Replace `hasattr(style, "apply")` in `iter_stat_effects` (`Character.py:388`) with an explicit split: fighting styles with an effect are `Effect`s, and description-only styles are not stat sources.
  - Move `add_origin_feat` into `CharacterBuilder`: it is builder logic that knows about `OriginFeat` (4 call sites). Update its callers.
  - Move `ExtraDamage` into a leaf module (`Items/Weapons/ExtraDamage.py`) that `Base.py` and `Improvements.py` both import. Re-export it from `Improvements.py`.
  - Change `Utils/BuildGroupSheetWriter.py` and `Spells/SpellFactory/Writer.py` to plain imports. If one of them really does cycle, move the shared piece to a leaf module in the same way.
- **Tests:** the layering allowlist is now empty.
- **Verify:** A, B, C, D, plus `python RunCharacterCreatorUI.py` starts (the Creator imports the most modules).

### Step 5: Sources are never copied into parts *(design-critical)* — done

- **Result:** `Ledger()` takes no arguments, and every part starts empty.
  - **Ability scores.** `AbilityScores` is now only the immutable base scores: read-only properties, plus `with_scores(...)` for a changed copy. That fixed the stale-cache bug from Step 1, and its xfail became a passing test. The new `AbilityIncreases` part (`character.ability_increases`) records the increases and resolves `score(ability, view)` and `own_score(ability, view)`. `Character.abilities` and the `deepcopy` are gone, and the queries are `get_ability_score`, `get_own_ability_score` (new) and `get_ability_modifier`.
  - **Speed and spellcasting.** `Speed` holds bonuses only, and `Spellcasting` holds casters and the DC bonus only.
  - **`StatView` gained source reads.** They are methods that fail clearly when a source isn't set: `get_base_ability_score`, `get_base_speed`, `get_own_ability_score`, `class_levels` and `fixed_spell_slots`.
  - **Parts of Step 6 happened early.** `ArmorClass.calculate(view, ...)` and `AbilityRequirements.validate(view)` already take the view, because the evaluated `AbilityScores` they read no longer exists.
  - **Tests.** `tests/_fake_view.py` is a minimal `StatView` for unit-testing parts without a `Character`. Snapshots didn't move, and the pages are byte-for-byte identical to the baseline.

- **Goal:** `Ledger()` takes no arguments, and parts hold contributions only.
- **Changes:**
  - Split `AbilityScores` into `base_abilities`, the immutable source (frozen, so changing a score in place is impossible, which fixes the stale-cache xfail from Step 1), and an `AbilityIncreases` part, which records the increases and caps. Its resolver is `AbilityIncreases.score(ability, view)`, which reads the base score through `view.base_abilities`. The cap rule is unchanged and tested.
  - Delete `Character.abilities` and the `deepcopy`. Keeping a resolved `abilities` next to `base_abilities` would bring back the "same class, two meanings" pair that 1b complains about. The final values are the existing queries `get_ability_score`/`get_ability_modifier`. The 28 reads of `.abilities` in `CharacterContent`, `Utils`, `Combat`, `Builds` and `tests` move to those queries, or to `ledger.ability_increases` when they need the breakdown.
  - `Speed` holds bonuses only; `total(view)` reads `view.base_speed`.
  - `Spellcasting` drops `ability` and `fixed_slots`. They are sources, and `spell_slots(view)` reads them through the view.
  - `StatView` gains these source reads (`base_abilities`, `base_speed`, `spell_casting_ability`, `fixed_spell_slots`, `class_levels`). They are sources, so this doesn't break the "answers, not parts" rule.
- **Callers:** grep `\.abilities\.`, `\.speed\b` and `\.spellcasting\.` in `CharacterContent`, `Utils`, `Combat`, `Builds` and `tests`. The 51 `.spell_casting_ability` reads already use the source, so they are unchanged.
- **Tests:** a fresh `Ledger()` is empty, and evaluating twice gives the same answers without mutating `base_abilities`.
- **Verify:** A, B, C, D.

### Step 6: One resolver shape; Character is only a facade *(mostly mechanical after Step 3)* — done

- **Result:** every part resolver takes only the view:
  - `HitPoints.total(view)`, and `Initiative.total(view)`, which now includes the Dexterity modifier;
  - `Initiative.roll_condition(view)`, `ArmorClass.total(view, ignore_shield)`, and `CarryingCapacity.total/sources(view)`;
  - `Spellcasting.difficulty_class/attack_bonus(ability, view)`;
  - `Skills.ability/modifier/roll_condition/roll_condition_sources/roll_condition_reasons(skill, view)`;
  - `SavingThrows.modifier/roll_condition(ability, view)`.
- **The armor-training rules live on the `Ledger`:** `is_wearing_untrained_armor()`, `has_shield_training()`, `has_untrained_armor_disadvantage(ability)` and `armor_warnings()`. `StatView` gained `has_shield_training` and `has_untrained_armor_disadvantage` as answers.
- **Removed from `Skills`:** the part-only `get_roll_condition*`, which silently ignored untrained armor, and `get_skill_ability`. The default mapping is `DEFAULT_SKILL_ABILITIES` / `Skills.default_ability(skill)`, and the writer uses that.
- **`Character`'s public queries are all one line.**
- **Tests and output:** `tests/test_part_resolvers.py` tests the resolvers against `FakeView`. Snapshots didn't move, and the pages are byte-for-byte identical to the baseline.

- **Goal:** each part resolves its own final values from a `StatView`, and every query on `Character` is one line.
- **Changes:**
  - Resolvers take only the view: `HitPoints.total(view)`, `Initiative.total(view)`, `Initiative.roll_condition(view)`, `ArmorClass.total(view, ignore_shield=False)`, `CarryingCapacity.total(view)`, `Skills.modifier(skill, view)`, `SavingThrows.modifier(ability, view)`.
  - Move the logic that currently sits on `Character` into its owning part:
    - skill and save modifiers go to `Skills` and `SavingThrows`;
    - skill ability choice and roll-condition sources go to `Skills`;
    - untrained armor, shield training and `warnings` go to methods on the `Ledger` (`is_wearing_untrained_armor()`, `has_shield_training()`, `armor_warnings()`), because they combine two parts, `WornArmor` and `EquipmentTraining`, and the `Ledger` owns both. They need no view.
  - `StatView` exposes these as answers (add `is_wearing_untrained_armor` and `has_shield_training` if a resolver needs them; Step 3 left them out because no formula reads them), never as `worn_armor`/`equipment_training` parts. Step 7 deletes those flat properties from `Character`, so a `StatView` that needed them would break there.
- **Callers:** none. The public `get_*`/`calculate_*` names stay.
- **Tests:** each part's resolvers get unit tests against a tiny fake `StatView`, with no builder and no `Character`. That these tests are possible is the proof the design is clean.
- **Verify:** A, B, C, D.

### Step 7: Access rule, `character.ledger.<part>` *(mechanical codemod)* — done

- **Result:** `Character.ledger` is the only way to reach a part, and the 17 flat part properties are gone. That's the plan's 16 plus `ability_increases` from Step 5. The codemod rewrote 86 reads, and only receivers known to be a `Character` were touched: `character`, `cs`, and `data.validate()`. Same-named attributes on other objects were left alone, such as `monster.skills`, `combatant.senses`, and `self.skills` on builders. The plan's verification grep was too broad as written, because it would also match those, so it was run with the non-`Character` receivers excluded. Only CSS class names remain. `Character`'s own 36 `self.<part>` reads go through `self.ledger`, and it no longer imports the part classes. Snapshots didn't move, the pages are byte-for-byte identical to the baseline, and `RunCharacterCreator.py`, `RunBuildGroups.py` and the Creator UI all run.

- **Goal:** a part can't be confused with a source or with a final value.
- **Changes:**
  - Add `Character.ledger -> Ledger` (sealed). The property is named after the class. `stats` would suggest final values, but a part holds unresolved contributions, and the final values come from the queries.
  - Codemod the 17 source and 64 test reads of `character.<part>` to `character.ledger.<part>`, with `.claude/worktrees` excluded.
  - Delete the 16 flat part properties in the same commit, so there is no deprecated alias to forget.
- **Verify:** A, B, C, D, plus a grep proving that no `\.(skills|saving_throws|senses|defenses|languages|armor_class|worn_armor|hit_points|initiative|speed|carrying_capacity|equipment_training|weapon_bonuses|ability_requirements|spellcasting)\b` read remains outside `Model/`.

### Step 8: Declared extensions, no global, no lookups *(design-critical, then mechanical)*

- **Goal:** the parent and child of an extension can be granted in either order, and nothing is mutated after granting.
- **Changes:**
  - Add `Character.add_feature(feature, extends: type[Feature] | Feature | None = None, optional: bool = False)`. The extension tree is resolved when it is read:
    - a type matches with `isinstance`, the same as `get_features_by_type` does today, and must match exactly one granted feature. An instance must itself be granted, which covers "extend the feature I just created in this method";
    - `optional=True` drops the extension without error if no parent is granted. This replaces the conditional lookups: Cleric Level 14 declares `ImprovedDivineStrike` (extends `DivineStrike`) and `ImprovedPotentSpellcasting` (extends `PotentSpellcasting`), both optional, and whichever parent Level 7 granted wins. Druid Level 15 works the same way;
    - `iter_features_with_extensions()` walks the resolved tree;
    - `character.extensions_of(feature)` replaces `feature.extensions` in `BaseFeatures.py:689`, `CharacterSheetWriters.py:1135`, `tests/test_all_builds.py:110` and `tests/test_subclass_features_2014.py:279`. It returns the extensions in canonical order (grant level, name);
    - `validate()` raises if a non-optional extension's parent isn't granted, or if a type matches more than one granted feature, because that would be ambiguous.
  - Codemod the pattern `x = data.get_features_by_type(P)[0]` … `x.extend_feature(C())` to `data.add_feature(C(), extends=P)` across the 221 lookups, one class file per commit batch. Convert the remaining `extend_feature` calls on a local instance to `extends=instance`.
  - Other changes to a granted feature become grants too. Grep for method calls on a looked-up feature other than `extend_feature`; today that is `ChannelDivinity.add_spell("Abjure Foes")` (`PaladinBase.py:145`). Make each one an extension feature, or pass it to the parent's constructor, so that 2b's "a feature is never changed after it is granted" holds.
  - Delete `_feature_extensions`, `note_feature_extended`, `Feature.extensions`, `Feature.extend_feature`, and `get_features_by_type` if nothing reads it any more. Delete `Character.remove_features` if nothing outside the tests uses it, since removal is order-dependent too. `BaseFeatures.py` no longer needs `Model.Character` at runtime, except for the `get_description(character)` annotation, which is a one-way dependency (L5 → L4).
  - Check `Builds/CharacterCreator/` codegen for any `extend_feature` or `get_features_by_type` it emits.
  - Update `.claude/agents/dnd-feature-extender.md` and `dnd-builds.md` for the new API.
- **Tests:** grant the child before the parent and get the same sheet; the error cases for a missing or ambiguous parent; an optional extension without its parent is dropped; one feature instance granted to two characters doesn't share extensions.
- **Verify:** A, B, C, D, plus `-m slow`. The goldens must not move.

### Step 9: Spells are order-free grants, through a `Grants` scope *(design-critical)*

- **Goal:** spell handling has no call-order rules and no builder state on `Character`.
- **Changes:**
  - **`Grants` scope.** The level and source of a grant come from where the builder is, not from the call. So `ClassBuilder` (at `ClassBuilder.py:283`), `SpeciesBuilder` (at `SpeciesBuilder.py:22`), background and feat granting each hand `add_features` a `Grants` object in place of the bare `Character`. It wraps the `Character` and has the same `add_*`/`replace_*` API, and it stamps every grant with `(grant level, source kind, source name)`. Codemod the `data: Character` annotation in the 935 `def add_features` signatures to `data: Grants`. Step 10 reuses the same stamps for features. `Grants` lives in `Model/` (L4), next to `Character`.
  - Replace `spells: list[tuple[...]]` with `SpellGrant` records (attrs: name, ability, ruling, grant level, source), stored as a list and read in canonical order (level, name, source).
  - Duplicates: the same spell from two different sources is allowed and listed per source, which replaces `separate_spell_source`. The same spell twice from the same source is an error, checked in `validate()`. A "source" is the stamped source name ("Wizard", "Rock Gnome", "Magic Initiate"). So two class levels picking the same spell is still an error, as it is today.
  - `replace_spell` becomes a declared `SpellReplacement(old, new, ...)` source that is resolved on read. It replaces the old spell from every source and keeps the old grant level, as today. A replacement whose old spell is never granted fails in `validate()`, not at call time. A chain (A→B and B→C) fails in `validate()` too, because the result would depend on the order the replacements resolve in.
  - `_current_grant_level`, `set_current_grant_level` and `_duplicate_spell_check_start` leave `Character`.
- **Callers:** `add_spell`/`add_cantrip` keep their signatures. The writer's `_spell_level` reads the record field. Update `tests/test_subclass_features_2024.py:228-233`, which calls `set_current_grant_level` directly.
- **Output:** the writer already sorts spells by `(level, name)` (`CharacterSheetWriters.py:796`), so the hashes should not move. If they do, `diff -r` against the baseline dump before accepting it.
- **Tests:** the same spell sets granted in shuffled order produce equal sheets; a replacement declared before its target works; a chained replacement fails.
- **Verify:** A, B, C, D, and the snapshots under both hash seeds.

### Step 10: Canonical feature display order *(deliberate output change; see Decision 1)*

- **Goal:** reordering `add_feature` calls never changes the sheet.
- **Changes:**
  - Every feature and extension carries the `(grant level, source kind, source name)` stamp from its `Grants` scope (Step 9). The sheet buckets by the stamped level instead of parsing `origin` (`parse_feature_level`). `origin` stays as display text only.
  - Keep the existing `(passive, name)` sort, and add tie-breakers from the stamp: `(passive, name, source kind rank: species → background → origin feat → class → subclass → feat, source name)`. Keeping the existing keys first means only tied cards move. `_sort_features_key` and the level-page sort (`CharacterSheetWriters.py:67` and `:1228`) become one key function. Nested extensions and extension cards on their own level pages use the same key.
  - Remove `_GRANT_ORDER_LEAKS` and every `xfail` on `test_grant_order_keeps_sheet`, including the slow orders.
- **Verify:**
  - Regenerate the sheet hashes on purpose.
  - `diff -r` the HTML of 3 builds against the baseline dump: a multiclass build, a species with spells, and a build with feats. Only the order of feature cards may change.
  - The stats goldens must not move.
  - Then run A, B, C, D, `-m slow`, and the snapshots under both hash seeds.

### Step 11: Tidy the sources and finish *(small)*

- **Changes:**
  - Group species facts (`size`, `base_speed`) into a `SpeciesTraits` source, and group `spell_casting_ability` and `fixed_spell_slots` into a `SpellcastingSource`. Do each grouping only if it is a net win after counting callers (`size` is written 27 times, `base_speed` 21, `spell_casting_ability` 14). Otherwise leave them as flat scalar fields and document them as sources.
  - Remove the `DerivedBonus` alias.
  - Rewrite the "Where things live" and "What enforces this" sections of `Notes/feature-application-model.md` to match section 2b, and update `.claude/agents/dnd-builds.md` (the pipeline, key APIs, `Grants`, `extends=`, and the `Model/` rows).
  - Final run under both hash seeds, plus `-m slow`.

---

## 4. Verification (every step)

```bash
# A. snapshots unchanged, unless the step says otherwise
python -m pytest tests/test_build_snapshots.py -q && git diff --exit-code tests/snapshots
# B. full suite (includes order-invariance and layering tests; -m slow where a step asks)
./run_tests.sh -q
# C. smoke: every build renders
python RunCharacterCreator.py
# D. type check (from Step 3 on, if Decision 4 is yes)
pyright Model/
```

- When a step legitimately changes output (only Steps 2 and 10 may), regenerate with `UPDATE_SNAPSHOTS=1 python -m pytest tests/test_build_snapshots.py`, `diff -r` a `SNAPSHOT_DUMP_DIR` dump against the `refactor-baseline` dump, and explain the diff in the commit message.
- Stats goldens must never move in this plan. Every step is meant to leave the rules unchanged.

## 5. Risks and delegation

| Steps | Kind | Who |
|---|---|---|
| 0, 1, 7 | Mechanical, test-heavy | Can be delegated (dnd-test-bughunter for 0; Sonnet-tier for the codemods). Verify yourself afterwards, because agents overcorrect and can clobber core files. |
| 2, 3, 4, 5, 6, 9 | Design-critical | Do these directly, or have one Sonnet agent work under review. Don't split them across parallel agents. The `Grants` codemod in Step 9 (935 signatures) can be delegated once the class is written. |
| 8 | Design first, then codemod | Design and one class file directly; the remaining class files can be delegated in batches. |
| 10, 11 | Small, but they change output or docs | Direct |

- **`StatView` creep.** Every member is something a formula may read. Keep the Protocol minimal: answers and sources only, never parts. Never let `Effects` implement it (Step 3 test).
- **Consumers outside CharacterContent.** Before Steps 5–9, grep `Combat/`, `Utils/` and `Builds/CharacterCreator/` (codegen writes calls like `add_feature` into build files) for the names being changed.
- **Codemods** must skip `.claude/worktrees`, and are followed by `black` (`format.sh`).
- **Snapshot coverage** only proves the existing builds. The per-part permutation tests (Step 2) and the extension and spell order tests (Steps 8–9) cover content that no build exercises.
- **Test runtime.** Pages are captured in memory (`HtmlCharacterSheetWriter._open_page`, overridden in `tests/_snapshot_helpers.py`): on Windows, reading a freshly written page back cost ~13 ms per file, because the antivirus scans it, and that was ~85% of the render time. The default suite takes ~45 s and the `slow` order matrix ~80 s.

## 6. Decisions for you

1. **Feature display order (Step 10).**
   - Complete the canonical sort *(recommended)*: this is the only way "feature order doesn't affect the output" holds for the HTML, not just the numbers. The sheet already sorts cards by name (Step 0 found this), so only same-name features and nested extensions move.
   - Keep grant order as a deliberate presentation choice: drop Step 10 and delete the grant-order test instead.
2. **`character.ledger.<part>` (Step 7)** *(recommended)*, or keep the flat `character.skills`-style properties and only document them as evaluated?
3. **Conflicting caster grants (Step 2).**
   - Raise an error *(recommended)*: surfaces content bugs.
   - Resolve by a fixed rule: for example, the higher caster type wins.

   Tools are not a conflict. The same tool from two sources is merged (section 2c).
4. **Add a type checker (pyright, basic mode, dev-only, scoped to `Model/`)?** *(recommended)* Without one, nothing checks that features and items really satisfy the `Effect`/`Gear` Protocols, or that removing `TYPE_CHECKING` left the annotations correct. Pylance in VS Code already uses pyright, so the only new thing is running it as check D. If you say no, drop D and rely on the Step 3 conformance test.
