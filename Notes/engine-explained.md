# The character engine, explained simply

Part 1 explains how the engine works. Part 2 lists the simplifications made so
far, and one that was considered and rejected.

---

# Part 1: How it works

## The one-sentence version

A build file collects **everything the character has**. The engine then asks
each of those things to **write down what it does to the stats**. The finished
`Character` **answers questions** by reading those notes.

## The cast of characters

Use this table to keep the names straight. The "plain name" is how to think
about each one.

| Engine name | Plain name | What it is | File |
|---|---|---|---|
| `CharacterSources` | **the bag** | Everything the character has: name, ability scores, class levels, features, spells, gear. You can add to it while building. In builders it's called `sources`. | [Model/CharacterSources.py](../Model/CharacterSources.py) |
| `Grants` | **the label gun** | What level and species builders put features and spells into the bag through. It sticks a label on each one: "Wizard, level 3" or "Elf, species". In builders it's called `data`. | [Model/Grants.py](../Model/Grants.py) |
| `GrantStamp` | **the label** | Level, kind (species/class/...), and who granted it. | [Model/Records/GrantStamp.py](../Model/Records/GrantStamp.py) |
| `Effect` | **anything that changes stats** | A feature, armor, weapon, item or fighting style. It has a `name` and one method: `apply(ledger_writer)`. | [Model/Content/Effect.py](../Model/Content/Effect.py) |
| `LedgerWriter` | **the pen** | A **write-only** pen given to each `Effect`, labeled with that effect's name. It can only write things down ("+10 speed", "proficient in Stealth"). It can't read anything back. | [Model/Ledger/LedgerWriter.py](../Model/Ledger/LedgerWriter.py) |
| `Ledger` | **the notebook** | What the pens wrote, split into sections: `skills`, `speed`, `armor_class`, `senses`, and so on. Each section is a small class in `Model/Ledger/`. **Private to `Character`**: nobody else sees it. | [Model/Ledger/Ledger.py](../Model/Ledger/Ledger.py) |
| `Character` | **the clerk** | Holds the bag and the notebook. It answers every question ("what's my AC?"). Read-only once it's made. | [Model/Character.py](../Model/Character.py) |
| `Formula` | **a "work it out later" note** | `lambda character: ...`, written into the notebook and worked out when someone asks. | [Model/View.py](../Model/View.py) |
| `CharacterView` | **the questions you may ask the clerk** | The read-only interface that formulas and feature descriptions get. | [Model/View.py](../Model/View.py) |
| `CharacterImprovement` | **a reusable "write this down" snippet** | Small ready-made effects (`SkillProficiency`, `GrantSense`, `SpeedBonus`, ...) that features are put together from. Content records almost everything through these, not through the pen directly. | [Model/Content/Improvements.py](../Model/Content/Improvements.py) |

The `Model/` folder shows the three phases below:

```
Model/
  CharacterSources.py, Grants.py, FeatureGrants.py,     1. build: the bag and how things go in
  ClassLevels.py, Spells.py, Inventory.py, AbilityScores.py
  Ledger/                                                2. evaluate: the notebook, its sections, the pen
  Character.py, View.py                                  3. ask: the clerk and its questions
  Content/                                               base classes content is made of (Effect, Feature, ...)
  Records/                                               small shared records (GrantStamp, SourcedValue, ...)
  Creatures/                                             stat blocks for companions and wild shapes
```

## The three phases

Everything happens in three phases, always in this order:

```
 ┌──────────────────── 1. BUILD ────────────────────┐   ┌──── 2. EVALUATE ────┐   ┌────── 3. ASK ──────┐
 │  (mutable, done by CharacterBuilder.build())     │   │ (once, automatic)   │   │ (read-only)        │
 │                                                  │   │                     │   │                    │
 │  class builder:                                  │   │  The first time any │   │  sheet writer,     │
 │    levels, subclass, scores ──────────► the bag  │   │  stat is asked for: │   │  combat, tests ask │
 │    each level's features ─► Grants ──► (Char-    │   │                     │   │                    │
 │  species builder ─────────► Grants ──►  acter-   │   │  for each feature,  │   │  character.        │
 │  name, inventory ───────────────────►  Sources)  │   │  armor, weapon,     │   │   calculate_       │
 │                                          │       │   │  item and fighting  │   │   armor_class()    │
 │      Character(sources) ◄────────────────┘       │   │  style:             │   │      │             │
 │      (copies the bag; read-only from now on)     │   │    thing.apply(pen) │   │  notebook + any    │
 │                                                  │   │  pen ─► notebook    │   │  formulas worked   │
 └──────────────────────────────────────────────────┘   └─────────────────────┘   │  out now ─► answer │
                                                                                  └────────────────────┘
```

1. **Build.** `CharacterBuilder.build()` makes an empty bag (`CharacterSources`).
   - Each class builder writes its bookkeeping straight into the bag: class
     levels, subclass, ability scores, spell replacements. It grants each
     level's features and spells through a `Grants`, which labels them.
   - The species builder grants through a `Grants` the same way.
   - `CharacterBuilder` sets the name and copies in the inventory.
   - At the end, `Character(sources)` takes a copy of the bag. From then on
     nothing can change it.
2. **Evaluate.** It's lazy: it happens the first time anyone asks for a stat,
   or calls `validate()`. The work is done in the private `Character._ledger`
   property. The engine makes an empty `Ledger`, and for every feature,
   extension, armor, weapon, item and fighting style it calls
   `apply(LedgerWriter(ledger, effect.name))`: each effect gets its own pen,
   labeled with its own name.
3. **Ask.** Every query on `Character` reads the ledger. When a note is a
   formula, it's worked out right then, against the finished character.

**What goes through the pen, and what doesn't.** Features, armor, weapons,
items and fighting styles go through `apply()`, because they change numbers
and proficiencies. Spells, class levels, invocations, weapon masteries and
gold never do: they're plain lists in the bag that `Character` reads directly.

## One feature, start to finish: an Elf's Darkvision

**Build.** In [CharacterContent/Species/Elf.py](../CharacterContent/Species/Elf.py):

```python
data.add_feature(ElfFeatures.Darkvision(60))
```

`data` is a `SpeciesGrants` (a `Grants`). It labels the feature
`GrantStamp(level=1, kind=SPECIES, granted_by="Elf")` and adds a `FeatureGrant`
to `sources.feature_grants`. Nothing is worked out yet. The feature is just in
the bag.

**Evaluate.** Later, the sheet asks `character.get_sense_range(Sense.DARKVISION)`.
That's the first question, so the ledger gets built, and each feature's
`apply()` runs with its own pen. For Darkvision, the write goes through four
hops:

```
Darkvision.apply(ledger_writer)                         # the feature; its pen is labeled "Darkvision"
  └─ GrantSense(DARKVISION, 60).apply(ledger_writer)    # an Improvement
       └─ ledger_writer.add_sense(DARKVISION, 60)       # the pen adds the label
            └─ ledger.senses.add_sense(DARKVISION, 60, "Darkvision")   # the notebook section
```

**Ask.** The read goes through two hops:

```
character.get_sense_range(DARKVISION)
  └─ self._ledger.senses.get_sense_range(DARKVISION)  ─►  60
```

## The one rule that explains the whole design

> **While features are being applied, nobody may read a stat.**

Here's why. Take the Barbarian's Fast Movement: *"+10 speed while you aren't
wearing Heavy armor."* Suppose the feature could ask *"am I wearing heavy
armor?"* while it applies. If the armor hasn't been applied yet, the answer
is "no", and the character wrongly gets +10. The result would depend on the
order things happened to be applied in, which is a source of hard-to-find
bugs.

So the engine makes that impossible:

- **The pen (`LedgerWriter`) can only write.** It has no getters at all.
- **Anything that depends on another stat is written as a formula**, and
  worked out only when someone asks, after everything has been applied:

  ```python
  # BarbarianFeatures.FastMovementBonus
  SpeedBonus(lambda cs: 0 if cs.worn_armor_type == ArmorType.HEAVY else 10).apply(ledger_writer)

  # SorcererDraconicFeatures.DraconicResilience: +1 HP per Sorcerer level
  HitPointsBonus(lambda character: character.get_class_level(CharacterClass.SORCERER)).apply(ledger_writer)
  ```

- **The `lambda` gets a `CharacterView`**, which is the finished character's
  read-only question list.
- **Rules that need everything are checked at the end.** For example,
  "expertise needs proficiency" and "this armor needs Strength 15" are checked
  in `character.validate()`, once everything has been applied.

Tests enforce this, all in
[tests/test_feature_apply_order.py](../tests/test_feature_apply_order.py):

- `test_effect_order_does_not_change_stats` applies every build's effects in
  three shuffled orders and requires the same stats each time.
- `test_effects_can_only_record` fails if `LedgerWriter` gets any method that
  isn't `add_`/`set_`/`register_`.
- `test_nothing_outside_the_model_reaches_into_the_record` fails if any code
  outside `Model/` (and `tests/`) touches `_ledger`.

Almost every "why is it built like this?" question comes back to this rule:

| Question | Answer |
|---|---|
| Why is `LedgerWriter` separate from `Ledger`? | So `apply()` gets something it can only write to. |
| Why do bonuses take `int` *or* a `lambda`? | The `lambda` is the "work it out later" case. |
| Why is `Character` read-only? | The notebook is filled once. If the bag could still change, the notes would be stale. |
| Why is the ledger private? | So the only way to write is the pen, during evaluation, and the only way to read is a `Character` query, afterwards. |
| Why do ability-score caps ("to a max of 20") resolve on read? | The cap must not depend on which increase applied first. |
| Why are extensions *declared* (`extends=Parent`) instead of attached? | So the parent can be granted before or after its extension. |

## The other pieces, briefly

| Piece | What it does | File |
|---|---|---|
| `FeatureGrant` / `ExtensionTree` | A feature is granted either **plainly** (it gets its own card) or as an **extension** of another feature (a rider shown on the parent's card). `ExtensionTree` matches each extension to its parent after everything is granted. `IfParentMissing` says what to do when the parent isn't there: raise an error, drop the extension, or show it on its own. | [Model/FeatureGrants.py](../Model/FeatureGrants.py) |
| `SpellGrant` / `resolve_spells` | Spells are a separate list in the bag. "Replace spell X with Y" is recorded as a note and applied when the spells are read. | [Model/Spells.py](../Model/Spells.py) |
| `ClassLevels` | Levels per class, which class was taken at each character level, and the subclasses. | [Model/ClassLevels.py](../Model/ClassLevels.py) |
| `Inventory` | Armor, weapons, items and gold, in labeled entries. | [Model/Inventory.py](../Model/Inventory.py) |
| `Bonuses` | A shared helper: a list of flat bonuses plus formula bonuses, each with a label. Speed, AC, HP, initiative, skills and saves all use it. | [Model/Ledger/Bonuses.py](../Model/Ledger/Bonuses.py) |

## Names that still need care

- **"Source" means a few things:**
  1. `CharacterSources`: the bag;
  2. the label on a bonus, resistance, sense or language, which is always the
     name of the effect that recorded it;
  3. the `source=` label on a spell, like "Chosen spell";
  4. related to these, `GrantStamp.granted_by` and `Feature.origin` ("Elf
     Trait"), which are two more "where did this come from" labels.
- **Weapon bonuses carry their own label.** A `WeaponBonus` is a record with a
  descriptive label ("Dueling Fighting Style - Applied if one-handed weapon and
  no other weapons"), so it doesn't take the pen's label.

## Cheat sheet: "I want to..."

| I want to... | Do this |
|---|---|
| add a feature with a fixed effect | Override `apply(self, ledger_writer)` and use an Improvement: `GrantSense(Sense.DARKVISION, 60).apply(ledger_writer)`. It's listed under the feature's `name` automatically |
| add a bonus that depends on another stat | Pass a `lambda character: ...` instead of an `int` |
| show a number in a feature's text | Override `get_description(self, character)`. `character` is a `CharacterView`, so you can read anything there |
| add a rider to an existing feature | `data.add_feature(Child(), extends=Parent)` |
| add a fighting style | Subclass `FightingStyle` and set `name = "..."`, matching the start of its description |
| track a brand-new kind of stat | 1. Add a notebook section in `Model/Ledger/`. 2. Add it in `Ledger.__init__`. 3. Add a `LedgerWriter.add_...` method. 4. Add a `Character` query. 5. Add a `CharacterView` entry if content needs to read it. 6. Usually add an Improvement too. The layering test checks the new section automatically |
| test a single effect | Use the `make_sources` fixture: `sources = make_sources(dexterity=16)`, then `sources.add_effect(SkillBonus(...))`, then `Character(sources).get_skill_bonus(...)`. A bare Improvement is listed under "Other" |

---

# Part 2: Simplifying it

## What we kept

These ideas *are* the engine's correctness, and none of the changes touched
them:

1. **The three phases:** build, then evaluate, then ask.
2. **A write-only pen during `apply()`**, with formulas worked out when they're
   read. This is what makes the order of application not matter.
3. **An immutable `Character` with a private ledger.**
4. **Grant stamps**, so every grant knows where it came from.
5. **`CharacterView`**, the one read interface. It's what keeps imports
   pointing downward.

## Done

| What | Change |
|---|---|
| Private ledger, no seal *(part 12)* | `ledger` became `_ledger`. `Recorder`, `@records` and `SealedError` are gone, and `Character` gained the listing queries the sheet needed. |
| Duplicate methods *(part 12 + after)* | `get_level_for_class`, `get_spell_slots`, `get_spell_casting_ability` and `get_base_speed` are gone. `CharacterView` reads the `base_speed` property. |
| Privacy test covers everything *(after part 12)* | `test_nothing_outside_the_model_reaches_into_the_record` scans every folder except `Model/` and `tests/`, not just `CharacterContent/`. |
| S1: clear names | `Effects` → `LedgerWriter`, so `Effect` and the pen are no longer one letter apart. `Ledger` and `LedgerWriter` each have their own file. Builders call a `CharacterSources` `sources`, so `data` always means a `Grants`. |
| S3: automatic labels | Each effect gets its own `LedgerWriter`, labeled with `effect.name`. The `source`/`reason` parameters are gone from the pen and from the Improvements (87 call sites). `add_carrying_capacity_bonus` no longer has its arguments backwards. Speed, AC, HP, initiative and saving-throw bonuses are now labeled too. Fighting styles got a `name`. Every rendered page is byte-identical to before. |
| S5: `Model/Ledger/` | The 17 notebook sections, `Bonuses`, `Ledger` and `LedgerWriter` moved into `Model/Ledger/`. The layering rule for sections now finds them from the folder, so a new section is checked automatically. |
| Parameter name | `apply(self, effects: LedgerWriter)` became `apply(self, ledger_writer: LedgerWriter)` everywhere (189 methods), so the name says what it is. Lists of effects (the tests' `_in_every_order`, `apply_order`) keep the name `effects`. |

## Considered and rejected: S4, record through the pen directly

The idea was to let features call the pen directly
(`ledger_writer.add_sense(Sense.DARKVISION, 60)`) and delete the 33
Improvements whose `apply` is a single call to the pen, removing one of the
four hops (feature → Improvement → pen → ledger section).

We dropped it, because Improvements do more than wrap a pen call:

- **They're how items declare their effects as data.** 26 item declarations
  list them: `improvements=[CarryingCapacityBonus(8)]`, or
  `add_character_improvement(...)` in `setup_improvements()`. A pen call can't
  sit in a list, so each of those items would need its own `apply()`.
- **Keeping them for items but not features gives two ways to record a fact.**
  Today content follows exactly one rule: it records through Improvements.
  Only one call in `CharacterContent` uses the pen directly.
- **Several take a list.** 6 grants pass two or more skills, saves or
  proficiencies at once; with the pen they'd become loops.
- **They're readable values.** 10 features read a stored Improvement back for
  their description, and tests use them as a ready-made vocabulary.

With the automatic labels (S3), the Improvements have also become as short as
the pen calls they wrap, so the extra hop costs very little.

## Don't simplify these

| Tempting change | Why not |
|---|---|
| Let features write ledger sections directly (drop the pen) | That removes the write-only guarantee, and order bugs come back. |
| Replace formulas with "apply in priority order" | That's the exact design the order-free engine replaced. |
| Remove `Character`'s query methods and let callers reach into the ledger | Every caller would have to pass the character back in for formulas, and the ledger would stop being private. |
| Drop `CharacterView` and type everything as `Character` | That brings back the import cycles (and `TYPE_CHECKING`). |
| Remove `ExtensionTree` / `IfParentMissing` | The three modes are real cases: a build error, an upgrade to an option that wasn't chosen, and a feature that stands alone. |
