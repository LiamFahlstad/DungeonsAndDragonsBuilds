# Feature Framework — Design Review

*Scope:* how `Feature`s are registered, ordered and applied to the `CharacterStatBlock`
(`CharacterSheetData.add_feature` → `setup_character_stat_block`), plus the `CharacterImprovement`
building blocks, extensions, and rendering responsibilities.

*Method:* code reading, plus three scratch scripts run against every build in
`BuildSelector` + `ExampleSelector`:

- an AST scan of every `apply()` / `apply_after_armor()`;
- a check of every `extend_feature()` child;
- a stale-value check that compares applied bonuses with the final stats.

Findings marked **Verified** were reproduced. Findings marked **By inspection** were reasoned
from the code but not run.

## Status (after the follow-up refactor)

The sections below describe the framework **as reviewed**. Since then:

| Finding | Status |
|---|---|
| C1 snapshots | **Fixed.** Stat-dependent bonuses are read-time formulas. |
| H1 phase chosen at call site | **Resolved by removal.** `ApplyWhen` and all 19 `apply_when=LAST` call sites are gone. Every effect only records facts and every value is computed on read, so order provably doesn't matter: a test shuffles every build's features, armor, weapons, items and fighting styles together and compares all stats. |
| H2 ad-hoc pipeline | **Fixed.** One unordered pass applies every effect (`CharacterSheetData.iter_stat_effects`), then `CharacterStatBlock.validate()` checks requirements (expertise needs proficiency, armor Strength). `apply_after_armor` is gone: armor-conditional effects are formulas. |
| M1 extensions render-only | **Fixed, and it was a real bug.** Extensions now apply. This fixed Forge Cleric *Saint of Forge and Fire* (fire immunity) and Hollow Warden *Ancient Might* (Exhaustion immunity), which had been silently dropped. The `HungeringMightBonus` / `RakishAudacityBonus` workaround classes were folded back into their extensions. |
| M4 shared weapons | **Fixed, verified bug.** A dropped Bracers of Archery bonus stuck to the bow. Each build now gets its own weapon copies. |
| M5 two lists | **Fixed.** There is a single `features` list in grant order. |
| L1 rendering in `Feature` | **Partly.** The three duplicated card and tag renderers now share helpers. Rendering still lives on `Feature`. |
| M2 partial-character choices | **Fixed.** "If already proficient, choose another" is a conditional grant resolved on read against every other grant (`SavingThrowProficiencyOrAlternative`); Skill Expert just records its grants. |
| M3 incremental ability caps | **Fixed.** Increases are recorded with their cap and resolved on read, lowest cap first (`AbilitiesStatBlock`). |
| L2, L3 | Open. String-typed levels and mixed metadata styles. |

---

## Current architecture (summary)

1. **Registration.** Each builder calls `data.add_feature(feature, apply_when=IMMEDIATE|LAST)`
   ([CharacterSheetAccumulator.py:133](../Builds/CharacterSheetAccumulator.py#L133)). Two lists
   are maintained:
   - `features` is the display order (IMMEDIATE is inserted at index 0; LAST is appended).
   - `feature_apply_order` is the call order, tagged with the phase.

   `merge_with` concatenates both lists across builders, with the species merged last.
2. **Application.** `setup_character_stat_block` builds a fresh stat block from deep-copied
   ability, skill and save blocks. It then runs a fixed pipeline
   ([:415-451](../Builds/CharacterSheetAccumulator.py#L415-L451)):

   `apply()` IMMEDIATE → `apply()` LAST → multiclass validation → armor →
   `apply_after_armor()` IMMEDIATE → LAST → weapons → items → fighting styles →
   `item.apply_to_weapons`

3. **Derived values are mostly lazy.** AC, skill totals, saves, HP, spell DC and initiative are
   computed when read, in [CharacterStatBlock.py](../StatBlocks/CharacterStatBlock.py). This is
   the framework's best property: most features only *write facts* (proficiencies, flat bonuses,
   flags), so they are order-insensitive.
4. **The ordering contract is documented, not enforced.** See the docstring in
   [Improvements.py:6-27](../CharacterContent/Features/Core/Improvements.py#L6-L27). It sorts
   improvements into additive writers, overwriters and eager readers, and says eager readers
   must be LAST.
5. **Extensions.** `parent.extend_feature(child)` attaches `child` to `parent.extensions`. Only
   the renderer reads that list.

**Strengths worth keeping:**
- Lazy derived stats.
- Rebuilding from deep copies on every setup, so there is no double application of ability,
  skill or save bonuses.
- The written ordering contract.
- Pool validation in the `*Choice` improvements.
- The fail-fast `SkillExpertise`.

---

## Critical

### C1. Eager snapshots in `apply()` make results depend on application order — **Verified bug**

> **Status: fixed.**
> - `SkillBonus`, `SavingThrowBonus` and `InitiativeBonus` now accept a formula
>   (`Improvements.Value`). `CharacterStatBlock` evaluates it at read time.
> - `JackOfAllTradesBonus` is now a formula for each skill.
> - The 6 features that stored a modifier as a fixed number (Primal Order, Thaumaturge, Aura of
>   Protection, Dread Ambusher, Hungering Might, Rakish Audacity) now pass formulas.
> - Regression tests and the AST guard live in `tests/test_feature_apply_order.py`. The remaining
>   eager readers are intentional and allow-listed there.

**Evidence.** 12 `apply()` methods read *derived* state (ability modifiers, proficiency bonus,
proficiency flags) and store the result as a constant:

| Feature | Location | Reads | Phase |
|---|---|---|---|
| PrimalOrder (Magician) | [DruidFeatures.py:80](../CharacterContent/Features/ClassFeatures/Druid/DruidFeatures.py#L80) | WIS mod → Arcana/Nature bonus | IMMEDIATE, level 1 |
| DivineOrderThaumaturge | [ClericFeatures.py:63](../CharacterContent/Features/ClassFeatures/Cleric/ClericFeatures.py#L63) | WIS mod → Arcana/Religion bonus | IMMEDIATE, level 1 |
| AuraOfProtection | [PaladinFeatures.py:227](../CharacterContent/Features/ClassFeatures/Paladin/PaladinFeatures.py#L227) | CHA mod → save bonus | LAST |
| DreadAmbusher | [RangerGloomStalkerFeatures.py:27](../CharacterContent/Features/SubClassFeatures/Ranger/RangerGloomStalkerFeatures.py#L27) | WIS mod → initiative bonus | LAST |
| HungeringMightBonus | [RangerHollowWardenFeatures.py:95](../CharacterContent/Features/SubClassFeatures/Ranger/RangerHollowWardenFeatures.py#L95) | WIS mod | LAST |
| RakishAudacityBonus | [RogueSwashbucklerFeatures.py:71](../CharacterContent/Features/SubClassFeatures2014/Rogue/RogueSwashbucklerFeatures.py#L71) | CHA mod | LAST |
| JackOfAllTradesBonus | [Improvements.py:374](../CharacterContent/Features/Core/Improvements.py#L374) | prof bonus + `is_proficient` | LAST |
| + IronMind, UnfetteredMind, SkillExpert, AbilityScoreBonus(max_score), StrengthRequirement | — | proficiency flags / scores | mixed |

**Failure scenario (reproduced).** Primal Order is added IMMEDIATE at Druid level 1. It applies
before the level 4/8/… ASIs, which are also IMMEDIATE but called later. It therefore captures the
level-1 Wisdom modifier. Four example builds print the wrong number on the sheet:

```
Y2014DruidDreamsSomnaDriftwillow:    Primal Order Arcana bonus=3 but final Wisdom mod gives 5
Y2014DruidShepherdMeridianFlockward: Primal Order Arcana bonus=3 but final Wisdom mod gives 5
Y2014DruidSporesMossenRotbloom:      Primal Order Arcana bonus=3 but final Wisdom mod gives 5
Y2014DruidWildfireEmberAshgrove:     Primal Order Arcana bonus=3 but final Wisdom mod gives 5
```

The same thing happens to Thaumaturge whenever a Cleric raises Wisdom after level 1. Moving these
features to LAST only fixes part of the problem. **Items apply after every feature**, and items
can raise ability scores (`AbilityScoreBonus` is used in `Items/Armor/Magic.py`,
`Items/Items/Wondrous.py`, `Items/Weapons/Magic.py`, …). So Aura of Protection, Dread Ambusher and
the others still miss a Charisma or Wisdom increase from a magic item. **By inspection.**

**Root cause.** The framework lets a feature turn a *formula* ("bonus equal to your WIS mod")
into a *number* at apply time. That is the one operation the lazy design cannot protect against.

**Suggested design.** Make contributions lazy: store the formula and evaluate it on read.

```python
# Improvements.py
Value = int | Callable[[CharacterStatBlock], int]

class SkillBonus(CharacterImprovement):
    def __init__(self, skill: Skill, bonus: Value, source: str | None = None): ...

# SkillsStatBlock stores (value_or_fn, source) and resolves at read time:
def get_bonus(self, skill, character) -> int:
    return sum(v(character) if callable(v) else v for v, _ in self._bonuses[skill])

# PrimalOrder.apply
bonus = lambda cs: max(1, cs.get_wisdom_modifier())
SkillBonus(Skill.ARCANA, bonus, source=self.name).apply(character_stat_block)
```

Apply the same change to `SavingThrowBonus`, `InitiativeBonus`, `ArmorClassBonus` and
`HitPointsPerLevelBonus`. Then `JackOfAllTradesBonus` becomes a single lazy rule: "if not
proficient, add ⌊PB/2⌋." It no longer needs LAST and cannot double up with a proficiency granted
later.

**Guardrail.** Turn the AST scan into a test. It fails when an `apply()` calls
`get_*_modifier` / `get_ability_score` / `get_proficiency_bonus` / `is_proficient`, with an
explicit allow-list for real validators (`StrengthRequirement`) and for chronological choices
(see M2).

**Migration cost.** Low to medium. There are about 5 improvement classes and 7 feature call
sites. The stat block accessors change internally, but their public signatures stay the same.

---

## High

### H1. The ordering phase is chosen at the call site, not declared by the feature

**Evidence.** There are 19 `apply_when=ApplyWhen.LAST` call sites across `BardBase`, `RogueBase`,
`RangerBase`, `WizardBase`, `PaladinBase` and three subclass builders. Each one carries a copied
comment explaining *why* the feature is LAST, for example
[RogueBase.py:32](../CharacterContent/Classes/BaseClasses/RogueBase.py#L32). But whether a
feature is an eager reader is a property of the **feature class**, not of the builder that adds
it.

**Failure scenario.** Someone adds Expertise from a new source (a feat, a subclass, the Character
Creator's generated build code) and forgets `apply_when=LAST`:
- `SkillExpertise` raises if the proficiency comes from a later builder or the species. This is
  loud, which is good.
- `JackOfAllTradesBonus` or any C1-style snapshot silently computes the wrong value, which is bad.

`add_origin_feat` never forwards `apply_when`
([:154](../Builds/CharacterSheetAccumulator.py#L154)), so an origin feat *cannot* be LAST even if
it needs to be.

**Suggested design.** Declare the phase on the feature:

```python
class Feature:
    phase: ClassVar[Phase] = Phase.GRANTS          # default

class Expertise(Feature):
    phase = Phase.READERS

def add_feature(self, feature, apply_when=None):
    phase = apply_when or feature.phase             # call-site override stays possible but rare
```

Composite features can derive their phase from their improvements, for example the maximum of the
`CharacterImprovement.phase` values. **Migration cost:** low. Move the 19 call-site arguments onto
roughly 12 classes, then delete the comments.

### H2. The pipeline has grown ad-hoc phases; items and armor sit outside the feature ordering model

**Evidence.**
- `apply_after_armor` was bolted on as a second hook that every feature carries
  ([BaseFeatures.py:490](../CharacterContent/Features/Core/BaseFeatures.py#L490)).
- Armor, weapons, items and fighting styles each have a hard-coded slot in
  [setup_character_stat_block](../Builds/CharacterSheetAccumulator.py#L415-L451).
- Two rules exist only as *side effects* of statement order:
  - "a Strength item can't satisfy an armor requirement" ([Improvements.py:421](../CharacterContent/Features/Core/Improvements.py#L421));
  - "worn armor overrides Unarmored Defense" ([:218](../CharacterContent/Features/Core/Improvements.py#L218)).

  Reordering two loops would silently change game rules.
- Fighting styles have two unrelated `apply` signatures (stat block vs. `list[weapons]`)
  dispatched by `isinstance`.

**Failure scenario.** Every new cross-cutting rule needs another hard-coded hook or another loop.
Examples: "while wielding a shield", "while not wearing armor" applying to items, and features
that read item-granted stats. C1's item gap is one instance of this.

**Suggested design.** Use one explicit, ordered phase list. Every effect source (features, armor,
items, fighting styles, species) contributes into it:

```python
class Phase(IntEnum):
    ABILITY_SCORES = 10     # background/ASI/feat increases, then item score setters
    GRANTS         = 20     # proficiencies, languages, senses, resistances, flat bonuses
    BASE_FORMULAS  = 30     # Unarmored Defense, SetArmorClass
    EQUIPMENT      = 40     # worn armor (overrides BASE_FORMULAS), shields
    CONDITIONAL    = 50     # "while (not) wearing armor/shield" (today's apply_after_armor)
    READERS        = 60     # expertise, choice-dependent grants
    VALIDATION     = 70     # StrengthRequirement, multiclass prereqs, attunement

class Effect(Protocol):
    phase: Phase
    def apply(self, cs: CharacterStatBlock) -> None: ...

for phase in Phase:
    for source in all_effect_sources:              # stable: (phase, seq)
        for effect in source.effects_for(phase):
            effect.apply(cs)
```

The two "rules by accident" become explicit phase assignments that can be tested. **Migration
cost:** medium. Once C1 makes most effects order-free, few features need a non-default phase.

---

## Medium

### M1. Extensions are render-only, and nothing enforces it

**Evidence.** `extend_feature` appends to `extensions`
([BaseFeatures.py:484](../CharacterContent/Features/Core/BaseFeatures.py#L484)). The apply
pipeline only iterates `feature_apply_order`, so an extension's `apply()` / `apply_after_armor()`
**never runs**. The scan found 221 extension classes and **0** of them override `apply`, so no
build is wrong today. **Verified.**

**Failure scenario.** Someone converts a mechanical upgrade (for example, a level-10 "your aura
now also grants +1 AC" rider) from `add_feature` to `extend_feature`. The
`dnd-feature-extender` agent exists to do exactly this conversion. The bonus disappears silently.

**Suggested design.** Pick one of these:
- **Fail fast:** in `extend_feature`, raise if
  `type(feature).apply is not Feature.apply or type(feature).apply_after_armor is not Feature.apply_after_armor`.
- **Make extensions real features:** the apply loop walks `feature` plus
  `feature.extensions` recursively. This needs a check that no extension is also registered
  through `add_feature`, to avoid double application.

The fail-fast option is a 3-line change.

### M2. Choice-dependent features resolve against a *partial* character

**Evidence.**
- `IronMind` ([RangerGloomStalkerFeatures.py:91](../CharacterContent/Features/SubClassFeatures/Ranger/RangerGloomStalkerFeatures.py#L91))
  and `UnfetteredMind` ([ClericKnowledgeFeatures.py:97](../CharacterContent/Features/SubClassFeatures/Cleric/ClericKnowledgeFeatures.py#L97)):
  "if already proficient in WIS/INT saves, pick another one."
- `SkillExpert` ([GeneralFeats.py:736](../CharacterContent/Features/CharacterFeats/GeneralFeats.py#L736)):
  "grant the proficiency only if it's missing."

**Failure scenario.** These choices are resolved at apply time, which effectively means "at the
time of the level-up". That is the right idea, but the call order is only *approximately*
chronological:
- The species merges **last**, so a species proficiency is never visible to a class-level choice.
- Within a phase, the order depends on builder chunking.

A grant later in the pipeline can duplicate a grant made earlier. The result is a wasted choice
that nobody detects. **By inspection.**

**Suggested design.** Make the choice an explicit build-time parameter, the way
`SkillExpertiseChoice` already works. Add a VALIDATION-phase check that warns on redundant grants
("Wisdom save proficiency granted by both Iron Mind and Resilient").

### M3. Ability score caps are resolved incrementally, one feature at a time

**Evidence.** `AbilityScoreBonus` with `max_score` clamps against the score *at apply time*
([Improvements.py:204](../CharacterContent/Features/Core/Improvements.py#L204)). Background, ASI
feats and the level-20 capstones (Barbarian and Monk, `max_score=25`) all rely on call order
matching level order.

**Failure scenario.** The result is correct only while call order equals chronological order.
Two things can break that:
- a species or background that raises a score and merges late;
- a Character Creator build that registers features in a different order.

Either one changes whether a +2 is clamped to +1. **By inspection.**

**Suggested design.** Record each increase as a ledger entry `(ability, amount, cap, level, source)`.
Resolve all entries in one pass in the ABILITY_SCORES phase, sorted by `level`. This also gives
the sheet a free "where did my 20 STR come from" breakdown.

### M4. Mutable equipment objects are shared across rebuilds

**Evidence.** Ability, skill and save blocks are deep-copied for each setup
([:399-413](../Builds/CharacterSheetAccumulator.py#L399-L413)). Weapons are not: weapon fighting
styles and `item.apply_to_weapons` mutate the builder's weapon instances in place. Correctness
relies on "must be idempotent" conventions (`_add_bonus_once`, and the docstring at
[Items/Base.py:102](../CharacterContent/Items/Items/Base.py#L102)). The stat block also shares the
`level_per_class` and `spell_slots` dicts by reference.

**Failure scenario.**
1. Build once with Bracers of Archery.
2. `drop_item(bracers)` on the same `CharacterBuilder`.
3. Build again. The bow still carries the Bracers damage bonus, because idempotence prevents
   *adding* a bonus twice but nothing ever *removes* one.

**By inspection, not run.**

**Suggested design.** Treat equipment as build-scoped. Either copy weapons into the stat block
(`cs.weapons = [copy.copy(w) for w in ...]`, with fresh bonus lists), or register weapon bonuses
as lazy modifiers keyed by weapon predicate, the same way as C1. Then the idempotence convention
can be deleted.

### M5. Two lists must stay in sync, and display order is tied to apply semantics

**Evidence.** `features` (IMMEDIATE is `insert(0)`, LAST is appended) and `feature_apply_order`
are separate lists. They must be updated together in `add_feature`, `remove_features` and
`merge_with`
([:133-152](../Builds/CharacterSheetAccumulator.py#L133-L152)). Display order is a by-product of
the apply phase: a LAST feature is always displayed at the end, whatever level it came from.

**Suggested design.** Use a single `list[FeatureEntry(feature, phase, seq, source, level)]`.
Apply order is `sorted(key=(phase, seq))`. Display order is the writer's decision (by level, by
source). `remove_features` and `merge_with` then touch one structure.

---

## Low

### L1. `Feature` carries mechanics, metadata *and* HTML/CSS rendering

[BaseFeatures.py](../CharacterContent/Features/Core/BaseFeatures.py) is about 900 lines. Only
about 110 of them are mechanics. The rest is a CSS blob and three near-duplicate HTML writers
(`write_to_file`, the extension block inside it, and `write_extension_card_to_file`), and all
three repeat the tag-chip assembly. **Suggestion:** move rendering into a
`FeatureCardRenderer` in `Utils/`, with one `_tags_html(feature)` helper. `Feature` keeps only
`get_*_description` and its metadata. This makes the class easier to test and stops rendering
changes from touching the engine core.

### L2. Level and source are string-typed

`parse_feature_level` recovers the level by parsing `origin` strings such as
`"Bard Level 3"` ([BaseFeatures.py:138](../CharacterContent/Features/Core/BaseFeatures.py#L138)).
Anything it can't parse defaults to level 1, and that level decides which extensions appear on
which shard. **Suggestion:** structured fields `level: int` and `source: FeatureSource`
(class/subclass/species/feat/background). `origin` becomes a display property derived from them.
M3 and M5 need these fields anyway.

### L3. Mixed metadata styles

Some metadata is constructor data (`activation`, `uses`, `usage_tags`). Some is an overridable
method that takes a stat block (`regained_on`, `target`, `calculate_dc`, `number_of_uses`). Static
facts such as `target` and `regained_on` could be constructor fields like `activation`, which
would leave methods only for values that are actually computed.

---

## Optional

- **Order-invariance property test.** For each build, shuffle `feature_apply_order` *within each
  phase*, rebuild, and assert that the stat blocks are identical: AC, all skills, saves,
  initiative, HP, DC. This test would have caught C1 and will catch any future eager reader.
  It is cheap and high-value, so add it first whatever else is adopted.
- **Effect provenance.** Record `(source feature, phase)` for every write to the stat block. This
  makes "why is my Arcana +8?" answerable on the sheet, and makes ordering bugs easy to debug.
- **Freeze features after registration.** Features are configured in `__init__` and should be
  immutable afterwards. A `__setattr__` guard, or frozen dataclasses for improvements, prevents
  hidden state from carrying over between rebuilds.

---

## Suggested order of work

1. Add the **order-invariance test** and the **no-eager-reads AST test**. Both will fail on
   Primal Order.
2. **C1:** lazy `Value` contributions, and migrate the 7 snapshotting features. Fix the Primal
   Order and Thaumaturge sheets.
3. **M1:** fail fast in `extend_feature` (3 lines).
4. **H1:** move the phase onto the feature class.
5. **H2 + M5 + M3:** the unified phase pipeline with a single entry list and an ability-score
   ledger. This is the larger refactor, and it is much smaller once steps 2–4 are done.
6. **M4, L1–L3** as time permits.
