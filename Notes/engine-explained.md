# The character engine, explained simply

Part 1 explains how the engine works. Part 2 suggests how to make it simpler
without giving up what makes it correct.

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
| `CharacterSources` | **the bag** | Everything the character has: name, ability scores, class levels, features, spells, gear. You can add to it while building. | [Model/CharacterSources.py](../Model/CharacterSources.py) |
| `Grants` (the `data` in builders) | **the label gun** | What builders put things into the bag through. It sticks a label on each thing: "Wizard, level 3" or "Elf, species". | [Model/Grants.py](../Model/Grants.py) |
| `GrantStamp` | **the label** | Level, kind (species/class/...), and who granted it. | [Model/Records/GrantStamp.py](../Model/Records/GrantStamp.py) |
| `Effect` *(singular)* | **anything that changes stats** | A feature, armor, weapon, item or fighting style. It has one method: `apply(effects)`. | [Model/Content/Effect.py](../Model/Content/Effect.py) |
| `Effects` *(plural)* | **the pen** | A **write-only** notepad given to each `Effect`. It can only write things down ("+10 speed", "proficient in Stealth"). It can't read anything back. | [Model/Effects.py](../Model/Effects.py) |
| `Ledger` | **the notebook** | What the pen wrote, split into sections: `skills`, `speed`, `armor_class`, `senses`, and so on. Each section is a small class in `Model/<Thing>.py`. It's sealed when it's done. | [Model/Effects.py](../Model/Effects.py) + `Model/Skills.py`, `Model/Speed.py`, ... |
| `Character` | **the clerk** | Holds the bag and the notebook. It answers every question ("what's my AC?"). Read-only once it's made. | [Model/Character.py](../Model/Character.py) |
| `Formula` | **a "work it out later" note** | `lambda character: ...`, written into the notebook and worked out when someone asks. | [Model/View.py](../Model/View.py) |
| `CharacterView` | **the questions you may ask the clerk** | The read-only interface that formulas and feature descriptions get. | [Model/View.py](../Model/View.py) |
| `CharacterImprovement` | **a reusable "write this down" snippet** | Small ready-made effects (`SkillProficiency`, `GrantSense`, `SpeedBonus`, ...) that features are put together from. | [Model/Content/Improvements.py](../Model/Content/Improvements.py) |

## The three phases

Everything happens in three phases, always in this order:

```
 ┌──────────────── 1. BUILD ────────────────┐   ┌──── 2. EVALUATE ────┐   ┌────── 3. ASK ──────┐
 │  (mutable, done by builders)             │   │ (once, automatic)   │   │ (read-only)        │
 │                                          │   │                     │   │                    │
 │  CharacterBuilder.build()                │   │  The first time any │   │  sheet writer,     │
 │    class builders ─┐                     │   │  stat is asked for: │   │  combat, tests ask │
 │    species builder ├─► Grants ─► the bag │   │                     │   │                    │
 │    gear ───────────┘    (label   (Char-  │   │  for each thing in  │   │  character.        │
 │                          gun)   acter-   │   │  the bag:           │   │   calculate_       │
 │                                 Sources) │   │    thing.apply(pen) │   │   armor_class()    │
 │                                    │     │   │  pen ─► notebook    │   │      │             │
 │           Character(sources) ◄─────┘     │   │  seal the notebook  │   │  notebook + any    │
 │           (copies the bag, read-only)    │   │                     │   │  formulas worked   │
 └──────────────────────────────────────────┘   └─────────────────────┘   │  out now ─► answer │
                                                                          └────────────────────┘
```

1. **Build.** `CharacterBuilder.build()` makes an empty bag (`CharacterSources`).
   The class builders, then the species builder, put things into it through a
   `Grants` (that's the `data` parameter in every builder). Then the gear goes
   in. At the end, `Character(sources)` takes a copy of the bag. From then on
   nothing can change it.
2. **Evaluate.** It's lazy: it happens the first time anyone asks for a stat
   (`Character.ledger`). The engine makes an empty `Ledger`, wraps it in an
   `Effects` pen, and calls `apply(effects)` on every feature, extension,
   armor, weapon, item and fighting style. Then it seals the ledger.
3. **Ask.** Every query on `Character` reads the ledger. When a note is a
   formula, it's worked out right then, against the finished character.

Spells, the class levels and the inventory never go through the pen. They're
just lists in the bag that `Character` reads directly. Only things that
change **numbers and proficiencies** go through `apply()`.

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
`apply()` runs. For Darkvision, the write goes through four hops:

```
Darkvision.apply(effects)                       # the feature
  └─ GrantSense(DARKVISION, 60, "Darkvision").apply(effects)   # an Improvement
       └─ effects.add_sense(DARKVISION, 60, "Darkvision")      # the pen
            └─ ledger.senses.add_sense(...)                    # the notebook section
```

**Ask.** The read goes through two hops:

```
character.get_sense_range(DARKVISION)
  └─ ledger.senses.get_sense_range(DARKVISION)  ─►  60
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

- **The pen (`Effects`) can only write.** It has no getters at all.
- **Anything that depends on another stat is written as a formula**, and
  worked out only when someone asks, after everything has been applied:

  ```python
  # BarbarianFeatures.FastMovementBonus
  SpeedBonus(lambda cs: 0 if cs.worn_armor_type == ArmorType.HEAVY else 10).apply(effects)

  # SorcererDraconicFeatures.DraconicResilience: +1 HP per Sorcerer level
  HitPointsBonus(lambda character: character.get_class_level(CharacterClass.SORCERER)).apply(effects)
  ```

- **The `lambda` gets a `CharacterView`**, which is the finished character's
  read-only question list.
- **Rules that need everything are checked at the end.** For example,
  "expertise needs proficiency" and "this armor needs Strength 15" are checked
  in `character.validate()`, once everything has been applied.

`tests/test_feature_apply_order.py` enforces the rule: it applies every
build's effects in shuffled orders and requires the same result every time.

Almost every "why is it built like this?" question comes back to this rule:

| Question | Answer |
|---|---|
| Why is `Effects` separate from `Ledger`? | So `apply()` gets something it can only write to. |
| Why do bonuses take `int` *or* a `lambda`? | The `lambda` is the "work it out later" case. |
| Why is `Character` read-only? | The notebook is filled once. If the bag could still change, the notes would be stale. |
| Why seal the ledger? | So nothing can write to the notebook after the fact. |
| Why do ability-score caps ("to a max of 20") resolve on read? | The cap must not depend on which increase applied first. |
| Why are extensions *declared* (`extends=Parent`) instead of attached? | So the parent can be granted before or after its extension. |

## The other pieces, briefly

| Piece | What it does | File |
|---|---|---|
| `FeatureGrant` / `ExtensionTree` | A feature is granted either **plainly** (it gets its own card) or as an **extension** of another feature (a rider shown on the parent's card). `ExtensionTree` matches each extension to its parent after everything is granted. `IfParentMissing` says what to do when the parent isn't there: raise an error, drop the extension, or show it on its own. | [Model/FeatureGrants.py](../Model/FeatureGrants.py) |
| `SpellGrant` / `resolve_spells` | Spells are a separate list in the bag. "Replace spell X with Y" is recorded as a note and applied when the spells are read. | [Model/Spells.py](../Model/Spells.py) |
| `ClassLevels` | Levels per class, which class was taken at each character level, and the subclasses. | [Model/ClassLevels.py](../Model/ClassLevels.py) |
| `Inventory` | Armor, weapons, items and gold, in labeled entries. | [Model/Inventory.py](../Model/Inventory.py) |
| `Recorder` / `@records` | The base class of every notebook section. `@records` marks a write method, and after sealing that method raises `SealedError`. | [Model/Recorder.py](../Model/Recorder.py) |
| `Bonuses` | A shared helper: a list of flat bonuses plus formula bonuses, each with a label. Speed, AC, HP, initiative, skills and saves all use it. | [Model/Bonuses.py](../Model/Bonuses.py) |

## Names that trip people up

- **`Effect` and `Effects` are unrelated.** `Effect` is *a thing that changes
  stats* (a feature, an item). `Effects` is *the pen*. One letter apart, two
  completely different jobs.
- **`Recorder` doesn't record anything.** It's the base class of the notebook
  sections, and its only job is the seal.
- **"Source" means at least four things:**
  1. `CharacterSources`: the bag;
  2. the `source=` label on a bonus, resistance or sense, usually the feature's
     name;
  3. the `source=` label on a spell, like "Chosen spell";
  4. related to these, `GrantStamp.granted_by` and `Feature.origin` ("Elf
     Trait"), which are two more "where did this come from" labels.
- **`data` in builders** is a `Grants` (the label gun), not the bag itself.

## Cheat sheet: "I want to..."

| I want to... | Do this |
|---|---|
| add a feature with a fixed effect | Override `apply(self, effects)` and use an Improvement (`GrantSense(...).apply(effects)`) or call `effects.add_...` |
| add a bonus that depends on another stat | Pass a `lambda character: ...` instead of an `int` |
| show a number in a feature's text | Override `get_description(self, character)`. `character` is a `CharacterView`, so you can read anything there |
| add a rider to an existing feature | `data.add_feature(Child(), extends=Parent)` |
| track a brand-new kind of stat | Add a new notebook section (`Model/<Thing>.py`), then an `Effects.add_...` method, a `Character` query, and a `CharacterView` entry if content needs to read it |
| test a single effect | `sources.add_effect(SkillBonus(...))`, then `Character(sources).get_skill_bonus(...)` |

---

# Part 2: How to simplify it

## Keep these (they're the quality, not the complexity)

These ideas *are* the engine's correctness. Every suggestion below keeps them:

1. **The three phases:** build, then evaluate, then ask.
2. **A write-only pen during `apply()`**, with formulas worked out when they're
   read. This is what makes the order of application not matter.
3. **An immutable `Character`.**
4. **Grant stamps**, so every grant knows where it came from.
5. **`CharacterView`**, the one read interface. It's what keeps imports
   pointing downward.

Most of what's confusing comes from **names** and **extra hops**, not from
these concepts. The suggestions are ranked by clarity gained per unit of
effort.

## S1. Rename the confusing names *(small, mechanical, biggest clarity win)*

| Today | Suggested | Why |
|---|---|---|
| `Effects` (the pen) | `LedgerWriter` | It says what it is: the write side of the `Ledger`. No more `Effect`/`Effects` mix-up. |
| `Recorder` | `LedgerPart` | It's the base class of a ledger section. |
| `apply(self, effects: Effects)` | `apply(self, ledger: LedgerWriter)` | It reads as "write into the ledger". |

`Effect`, `Ledger`, `Character` and `CharacterSources` can keep their names.
Once the pen has a different name, `Effect` on its own is clear.

- **Cost:** about 190 `apply` signatures plus the imports. It's a pure
  find-and-replace, and the snapshot and apply-order tests prove nothing
  changed.
- **Watch out:** exclude `.claude/worktrees/` from any scripted rewrite.

## S2. Remove duplicate methods on `Character` *(small)*

`Character` has several pairs of methods that do the same thing:

| Duplicate | Keep | Notes |
|---|---|---|
| `get_level_for_class` (1 use) / `get_class_level` (85 uses) | `get_class_level` | |
| `base_speed` / `get_base_speed` | one of them | `CharacterView` uses `get_base_speed` |
| `spell_casting_ability` / `get_spell_casting_ability` | both, with clearer names | One returns `None`, the other raises. Name that difference, e.g. `spell_casting_ability` and `require_spell_casting_ability()` |
| `spell_slots` / `get_spell_slots` | both, with clearer names | Same `None`-versus-raise split |

Each pair is one more "which one do I call?" question for the reader.

## S3. Fill in the source label automatically *(medium)*

Today, about 10 `Effects` methods take a `source`/`reason` label, and content
nearly always passes `self.name`. Two things are inconsistent:

- the argument order: `add_carrying_capacity_bonus(source, bonus)` versus
  `add_damage_resistance(type, source)`;
- the coverage: speed, AC, HP and initiative bonuses have no label at all.

The evaluation loop in `Character.ledger` already knows which effect it's
applying, so it could give each one a pen that knows the label:

```python
for effect in self._apply_order(self.iter_stat_effects()):
    effect.apply(LedgerWriter(ledger, source=effect.name))
```

- **What you gain:**
  - every recorded fact gets traced back to its feature for free (a quality
    gain: the sheet could list sources for *every* bonus);
  - the `source` parameter disappears from the pen's methods;
  - the inconsistencies above go away.
- **Cost:**
  - `name` has to move up to the `Effect` base class (features, armor,
    weapons, items and fighting styles already have it);
  - the few places that want a different label need an optional override;
  - about 60 call sites drop an argument.

## S4. Stop wrapping one-line Improvements *(large, but where feature authors spend their time)*

Today, a feature that grants one fact goes through **four hops**: feature →
Improvement → pen → ledger section. There are 172 lines in content that only
pass the pen along (`self._x.apply(effects)`). Many of the 61 Improvement
classes are a single line:

```python
class SpeedBonus(CharacterImprovement):
    def __init__(self, bonus): self.bonus = bonus
    def apply(self, effects): effects.add_speed_bonus(self.bonus)
```

With S1 and S3 in place, a feature can call the pen directly:

```python
# before
class Darkvision(Feature):
    def __init__(self, distance):
        self.distance = distance
        super().__init__(name="Darkvision", ...)
        self._sense = GrantSense(Sense.DARKVISION, self.distance, self.name)

    def apply(self, effects: Effects):
        self._sense.apply(effects)

# after
class Darkvision(Feature):
    def __init__(self, distance):
        self.distance = distance
        super().__init__(name="Darkvision", ...)

    def apply(self, ledger: LedgerWriter):
        ledger.add_sense(Sense.DARKVISION, self.distance)
```

**Keep** the Improvements that actually contain logic:

- choice validation (`SkillProficiencyChoice`, or a plain
  `validate_choice(skills, pool, count)` function);
- the AC formulas (`SetArmorClass`, `MultiAbilityArmorClass`);
- `JackOfAllTradesBonus`;
- `StrengthRequirement`;
- the `InformationalImprovement` family.

The pen is already the typed, documented API, so nothing is lost, and order
independence is untouched because the pen is still write-only.

- **Cost:** a codemod over about 170 sites. Do it one folder at a time, and
  run the apply-order and snapshot tests after each folder.
- **Tests:** tests that use `sources.add_effect(SkillBonus(...))` can keep
  using whichever Improvements remain.

## S5. Group `Model/` by phase *(medium, mechanical)*

Today about 20 ledger-section files (`Skills.py`, `Speed.py`, `Senses.py`, ...)
sit flat next to `Character.py`, so you can't see the three phases in the
folder. Plan section 2b already proposed this, and it hasn't been done yet:

```
Model/
  Build:     CharacterSources.py, Grants.py, FeatureGrants.py, ClassLevels.py, Spells.py, Inventory.py
  Ledger/    Ledger.py, LedgerWriter.py, LedgerPart.py, Bonuses.py, Skills.py, Speed.py, ... (every section)
  Answer:    Character.py, View.py
  Records/, Content/   (unchanged)
```

Then the folder itself explains the engine. The Creator round-trip test
catches any broken import that the codegen emits.

## S6. Make the ledger private and drop the seal *(optional, medium)*

There are two locks today:

- the pen can't read during evaluation (the important one);
- the seal stops writes after evaluation.

The seal exists only because `character.ledger` is public. The presentation
code reads it in 13 places (known languages, sense ranges, the defense lists),
and the tests in 62.

The alternative:

1. Add the 4–5 missing queries to `Character`.
2. Rename the attribute to `_ledger`.
3. Add a rule to `test_layering.py` that forbids `._ledger` outside
   `Character.py`.

Then `Recorder.py`, the `@records` decorator on every write method, and
`SealedError` can all go. The same protection moves from runtime reflection
into a test. Do this only if the seal bothers you: it's cheap where it is.

## Don't simplify these

| Tempting change | Why not |
|---|---|
| Let features write ledger sections directly (drop the pen) | That removes the write-only guarantee, and order bugs come back. |
| Replace formulas with "apply in priority order" | That's the exact design the order-free engine replaced. |
| Remove `Character`'s query methods and have callers use `character.ledger.skills.modifier(skill, character)` | Every caller would have to pass the character back in, and you'd lose the single read API. |
| Drop `CharacterView` and type everything as `Character` | That brings back the import cycles (and `TYPE_CHECKING`). |
| Remove `ExtensionTree` / `IfParentMissing` | The three modes are real cases: a build error, an upgrade to an option that wasn't chosen, and a feature that stands alone. |

## Suggested order

| # | Step | Size | Risk |
|---|---|---|---|
| 1 | S1: renames | S | none (mechanical) |
| 2 | S2: duplicate methods | S | none |
| 3 | S3: automatic source labels | M | low; snapshot-checked |
| 4 | S5: group `Model/` by phase | M | low; round-trip test |
| 5 | S4: remove one-line Improvements | L | low per folder; apply-order test |
| 6 | S6: private ledger, no seal | M | optional |

S1 and S2 alone remove most of the "which thing is this?" confusion. S3 and S4
remove most of the "why are there so many hops?" confusion.
