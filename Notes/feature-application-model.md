# How Features Are Applied

This describes how the engine turns granted features, armor, weapons and items into the numbers
on a character sheet, why the order they're applied in doesn't matter, and how to write an effect
whose value depends on something else ("a bonus equal to your Wisdom modifier", "while you aren't
wearing Heavy armor").

It replaces two older models: `ApplyWhen.IMMEDIATE` / `ApplyWhen.LAST`, and after that "apply in
grant order, with a few deliberately chronological exceptions". Neither exists any more.

## The short version

1. **`apply()` only records facts.** A proficiency, a +1, "add WIS to AC", "+10 speed unless in
   Heavy armor", "+2 STR to a maximum of 20". It gets `Effects` (`Model/Effects.py`), a
   write-only record, so it *can't* read a stat: not a score, not a proficiency, not a level.
2. **The stat block works every value out when it's read**, from everything recorded. So nothing
   can depend on what happened to apply first.
3. **Requirements are checked once, at the end** (`Character.validate()`): expertise
   needs proficiency, an armor needs a minimum Strength, and a multiclass character needs the
   ability minimums for every class it has.
4. **There are no exceptions.** A test shuffles every build's effects (features, extensions,
   armor, weapons, items and fighting styles together) and requires identical sheets. The
   write-only record makes "an effect read a stat mid-evaluation" impossible rather than a rule
   the tests police.

This follows the design of `~/Scripts/DungeonsAndDragons`: effects are recorded on a ledger,
then evaluated once in the rules' own dependency order. Here `Effects` is the ledger, and
`Character`'s getters are the evaluation.

## The pipeline

Two objects, built in that order:

- **`CharacterSources`** (`Model/CharacterSources.py`) is what builders fill in: the player's
  decisions and the sources they grant (features, spells, fighting styles, `inventory`, base
  ability scores and speed). It is mutable and answers no rules questions.
- **`Character`** (`Model/Character.py`) is built from them (`Character(sources)`) and never
  changes. It takes its own copy of the sources, exposes them read-only, and answers every query
  (`calculate_armor_class()`, `get_skill_modifier()`, ...). `CharacterBuilder.build()` returns
  one. To try a change, take `character.sources` (a copy), change it, and build a new
  `Character`.

Evaluation is internal and lazy. The first query builds a fresh, empty `Ledger`
(`Model/Effects.py`: one part per concern, see below) - no part starts from a copy of a source -
then:

| # | Stage | What runs |
|---|---|---|
| 1 | **Record** | `apply(effects)` of everything in `iter_stat_effects()`: features and their extensions, armor, weapons, items, and fighting styles with a computed effect (Defense, Archery, Dueling, Thrown Weapon Fighting). **Any order.** Every call gets the same write-only `Effects` view of a fresh `Ledger`, which is sealed afterwards |
| 2 | **Validate** | Only in `validate()`, the single entry point (the writers and the combat UI call it first): first the sources (name, subclass, abilities, speed, size and base class set, at most one worn body armor, the attunement limit), then `Effects.validate()`: expertise needs proficiency, ability requirements such as an armor's Strength, and multiclass ability minimums |

Weapons are never changed while a character is evaluated. A bonus the wielder brings to their
weapons (Archery's +2 to attack rolls with Ranged weapons, Bracers of Archery's +2 damage with
bows) is recorded as a `WeaponAttackBonus` / `WeaponDamageBonus` improvement with a filter for the
weapons it covers, and each weapon combines it with its own bonuses on read. So a builder's weapon
objects are shared by every sheet it builds, with no copies and no idempotence guards.

The evaluation is a `cached_property`: a `Character` never changes, so it is evaluated at most
once and needs no version bookkeeping. The effect order is a constructor argument
(`Character(sources, apply_order=...)`, a test seam).

## Where things live

`Character` has exactly three kinds of public member, and the name says which:

| Kind | Question it answers | Where it lives | Example |
|---|---|---|---|
| **Source** | What did the player choose, or what were they granted? | A field on `CharacterSources`, set by a builder (`add_*` / `set_*`, or through a `Grants` scope); `Character` exposes each read-only | `class_levels`, `base_abilities`, `base_speed`, `size`, `spell_casting_ability`, `fixed_spell_slots`, `feature_grants`, `spell_grants`, `inventory` |
| **Ledger** | What did the effects record? | `character.ledger.<part>`: evaluated on demand, sealed, read-only. A part holds only what effects recorded - never a copy of a source, never a final value | `character.ledger.skills`, `character.ledger.senses` |
| **Query** | What is the final number or answer? | A method on `Character`, one line that hands the character (as a `CharacterView`) to a part's resolver | `get_skill_modifier(skill)`, `calculate_armor_class()`, `spells`, `features` |

Rules of thumb:

- Anything derived is not stored on `Character`; a source is never copied into a part.
- Builder bookkeeping (the level being granted, who grants it) lives in the builder's `Grants`
  scope (`Model/Grants.py`), never on `Character`. `CharacterSources.add_feature` / `add_spell`
  require a `stamp`, so every grant goes through a scope (tests use `tests/_grants.py`).
- A feature is never changed after it's granted: a later level's addition is its own grant
  (an extension, a spell).
- `size`, `base_speed`, `spell_casting_ability` and `fixed_spell_slots` stay flat source fields:
  grouping them into objects would rewrite ~40 builder lines to save two names.

The `Model` package imports only point down: `Core` → `Model/Records/` and `Model/View.py` (the
one Protocol: `CharacterView`, plus `Formula`) → the parts → `Model/Effects.py` (`Ledger`,
`Effects`) → `Model/Content/` (the base classes content subclasses: `Feature`, `Item`,
`AbstractWeapon`, `AbstractArmor`, `FightingStyle`, `Improvements`) → `Model/Character.py` →
`Model/Grants.py`. A `Character` holds those concrete classes, so nothing narrows them back. It
never imports `CharacterContent`, not even for type hints, and nothing in the repo uses
`if TYPE_CHECKING:` (`tests/test_layering.py`, which checks the layer of every import in the
repo).

## How each value is worked out on read

| Value | Recorded as | Resolved by |
|---|---|---|
| Ability score | Base score + `(ability, bonus, max_score)` increases | `AbilityScores.get_score`: capped increases lowest cap first, then uncapped (equipment) bonuses on top |
| Ability modifier | | From the score |
| Skill modifier | Proficiency/expertise flags, flat and formula bonuses, ability overrides | `Character.get_skill_modifier`. With several overrides for one skill, the best ability is used |
| Skill roll condition | Every Advantage/Disadvantage source, with reasons | `Skills.get_roll_condition`: both cancel out |
| Saving throw | Proficiency flags, conditional grants, flat and formula bonuses | `get_saving_throw_modifier`, `SavingThrows.is_proficient` |
| AC | Every `ArmorClassFormula` (unarmored default, Unarmored Defense, worn armor), flat and formula bonuses | `calculate_armor_class`: the best applicable formula + bonuses |
| Speed | Base + flat and formula bonuses | `Character.calculate_speed()` |
| Senses | Plain grants and "or extend" grants | `Character.senses.ranges`: best plain grant + every extension |
| Weapon proficiency | `weapon_proficiencies` on `Character.equipment_training` (categories such as Martial weapons, or single kinds such as the Scimitar) | `AbstractWeapon.is_proficient(cs)`: an explicit `player_is_proficient` override, or any recorded grant that covers the weapon |
| Armor training, tools | `armor_training`, `tool_proficiencies` on `Character.equipment_training` | Read directly. A tool is a `ToolProficiency` record (`Model/Records/Tools.py`), keyed by name, so the same tool from two sources is listed once |
| Untrained armor / Shield (2024 PHB) | Worn armor, wielded Shield (`Character.worn_armor`), `armor_training` | Untrained armor: a Disadvantage source on STR/DEX skills (by the skill's actual ability), STR/DEX saves, initiative and STR/DEX weapon attacks, plus a `warnings` entry (no spellcasting). Untrained Shield: its AC bonus is left out. `calculate_armor_class(ignore_shield=True)` gives the sheet's "w/o Shield" AC |
| Initiative | DEX, proficiency, flat and formula bonuses; roll-condition sources | `calculate_initiative()`, `initiative_roll_condition` |
| Spell slots | Registered casters `{class: CasterType}` | `spell_slots` / `pact_magic_slots`, via `Core.SpellcastingRules.calculate_spell_slots` |
| Weapon attack and damage bonuses | The weapon's own bonuses (a +1 weapon, set at construction), plus `WeaponBonus(applies_to, value, source)` records on `Character.weapon_bonuses` | `AbstractWeapon.get_attack_roll_bonuses(cs)` / `get_damage_roll_bonuses(cs)`: the weapon's own, then every recorded bonus whose filter accepts it |
| Weapon mastery | `player_has_mastery` on the weapon, or a chosen Weapon Mastery on the sheet data | `AbstractWeapon.has_mastery(weapon_masteries)`, at render time |
| HP, spell DC, weapon attacks, carrying capacity | | Computed from the final stats as before |

### Ability increases "to a maximum of N"

`AbilityScoreBonus(..., max_score=20)` records the increase and its cap; it doesn't clamp while it
applies. `get_score` resolves the recorded increases:

- **Capped increases apply lowest cap first.** With equal caps, order can't change the result:
  applying +a then +b under cap C gives `min(s + a + b, C)` either way. Across different caps,
  lowest-first is the order the rules grant them in (ASIs and feats at 20, then the level-20
  capstones Primal Champion and Body and Mind at 25). It's also never worse for the player: STR
  19 with an ASI +2 and Primal Champion +4 is 24, whichever applied first.
- **An increase never lowers a score** something else already pushed past its cap.
- **`max_score=None` is an equipment bonus** (Gauntlets of Strength, Ring of Intellect). It goes on
  top of the character's own score. Requirements read `get_own_score()`, which excludes it, so an
  item can't satisfy an armor's Strength or a multiclass minimum.

### "If you already have this proficiency, choose another"

Iron Mind and Unfettered Mind use `SavingThrowProficiencyOrAlternative(ability, alternatives)`.
It records a conditional grant. `SavingThrows` resolves it on read: fixed proficiencies
first, then each conditional grant in a fixed (Ability-enum) order, each taking its ability or the
first alternative still missing. "Already have" therefore means *from any source*, including a
species or another class merged later, so the choice is never silently wasted.

Skill Expert records its proficiency and expertise unconditionally. Both are idempotent flags,
and the expertise-needs-proficiency check runs in validation.

### AC is a set of formulas, not an overwritten field

`Character.armor_class.armor_class_formulas` starts with 10 + DEX. `MultiAbilityArmorClass` (Unarmored
Defense, Draconic Resilience) adds an unarmored formula, and worn armor adds an armor formula via
`SetArmorClass`. On read:

- while any body armor is worn, only armor formulas apply;
- otherwise every unarmored formula applies, except ones with `allows_shield=False` (Monk's
  Unarmored Defense) while a Shield is wielded;
- the best applicable formula wins, then flat and formula `ArmorClassBonus`es are added.

This fixed two latent bugs. A Barbarian/Monk multiclass used to *stack* both Unarmored Defenses
(10 + DEX + CON + WIS), and Monk Unarmored Defense kept working with a Shield. No current build
was affected.

### Armor-conditional effects are formulas

"While you aren't wearing Heavy armor…" used to need a second `apply_after_armor()` pass. That
hook is gone. The effect is a formula reading the armor state on read:

```python
# Roving / Fast Movement
SpeedBonus(
    lambda cs: 0 if cs.ledger.worn_armor.body_armor_type == Definitions.ArmorType.HEAVY else 10
).apply(effects)

# Defense fighting style, Soul of the Forge
ArmorClassBonus(lambda cs: 1 if cs.is_wearing_armor else 0).apply(effects)
```

## Writing a new feature effect

| The effect says… | Write it as |
|---|---|
| "You gain proficiency in X" | `SkillProficiency([X])` / `SavingThrowProficiency([...])` |
| "…if you already have it, choose another" | `SavingThrowProficiencyOrAlternative(X, [alternatives])` |
| "You gain Darkvision 60 ft. If you already have it, its range increases by 60 ft." | `GrantOrExtendSense(Sense.DARKVISION, 60, name)`. Resolved on read as the best other grant + 60 |
| "+N to …" (a fixed number) | `SkillBonus(skill, N)`, `SavingThrowBonus(..., N)`, `ArmorClassBonus(N)`, `SpeedBonus(N)`, … |
| "a bonus equal to your *ability* modifier" / "half your proficiency bonus" / "+1 per Sorcerer level" | A **formula**: `SkillBonus(skill, lambda cs: ...)`, `SavingThrowBonus`, `InitiativeBonus`, `HitPointsBonus` |
| "…while (not) wearing armor / wielding a Shield" | A **formula** on `SpeedBonus` / `ArmorClassBonus` reading `cs.ledger.worn_armor.body_armor_type`, `cs.is_wearing_armor`, `cs.ledger.worn_armor.shield_wielded` |
| "Your AC equals 10 + DEX + WIS" | `MultiAbilityArmorClass(10, [DEX, WIS])`, plus `allows_shield=False` if a Shield disables it |
| "You gain Expertise in X" | `SkillExpertise([X])`. The proficiency may come from anywhere; validation checks the pair |
| "Increase STR by 2, to a maximum of 20" | `AbilityScoreBonus([...], total=2, max_score=20)` |
| "Your Strength must be at least N" | `StrengthRequirement(N, reason)` (checked in validation) |
| "You gain proficiency with Martial weapons / Heavy armor / Smith's Tools" | `GrantWeaponProficiency([...])`, `GrantArmorTraining([...])`, `GrantToolProficiency([...])` |
| "+2 to attack rolls with Ranged weapons" / "+2 to damage rolls with the Longbow" | `WeaponAttackBonus(applies_to, 2, source)` / `WeaponDamageBonus(...)`, where `applies_to` is a `WeaponTraits -> bool` filter (`Core/Weapons.py`: the weapon's type, properties and, for the Scimitar, Longbow and Shortbow, its `kind`). Never write into the weapon, and never match class names |
| An upgrade to an earlier feature | `data.add_feature(Upgrade(), extends=Parent)`. Its `apply()` runs too, so don't also grant it plainly |

**`apply(self, effects: Effects)` can only record.** `Effects` offers `add_*`/`set_*`/
`register_*` methods and nothing else - no scores, no proficiency flags, no AC or armor state, and
no levels either. If a value depends on anything, pass a formula (`lambda character: ...`); it gets
the finished `Character` when the value is read. Every bonus (skills, saving throws, AC, HP,
speed, initiative) is a `Value` (`Model/View.py`): a flat `int` or a formula, recorded by the
same `add_*_bonus` method on `Effects`. `Bonuses.add` is the one place that tells them apart. `get_description()` and the
other rendering methods still get the `Character`, and may read anything.

## The parts

The `Ledger` (`Model/Effects.py`) holds one part per concern (`Model/*.py`), plus the rules that
combine two parts (untrained armor, Shield training, `armor_warnings()`). Each part owns its own
state *and* works out its own final values: every resolver takes one argument, a `CharacterView`
(`Model/View.py`) of the finished character, e.g. `HitPoints.total(view)`,
`Initiative.total(view)`, `Skills.modifier(skill, view)`. A part never names `Character`, so it can
be unit-tested against a fake view (`tests/_fake_view.py`, `tests/test_part_resolvers.py`). Every
query on `Character` is one line that hands itself to a resolver. No part imports
`CharacterContent`.

`Bonuses` (`Model/Bonuses.py`) is a small value object - flat values and formulas
(`Formula`, from `Model/View.py`), each with a source label - shared by every part that is "a bonus total plus
sources": `Initiative`, `ArmorClass`, `HitPoints`, `Speed`, `Skills` and `SavingThrows` each hold
one (or a `dict[..., Bonuses]` for the per-skill/per-ability ones) instead of reimplementing the
flat-list/formula-list/source-list shape themselves.

| Part (`character.ledger.<attr>`) | Owns |
|---|---|
| `equipment_training` (`EquipmentTraining`) | `weapon_proficiencies`, `armor_training`, `tool_proficiencies`, `has_shield_training` |
| `languages` (`Languages`) | Known languages, each with sources (`knows`, `sources`, `add`) |
| `defenses` (`Defenses`) | Damage resistance/immunity, condition immunity, each with sources |
| `senses` (`Senses`) | Sense ranges (`.ranges`) and "or extend" grants |
| `ability_increases` (`AbilityIncreases`) | Every ability score increase and its cap, on top of `base_abilities`; `score(ability, view)` / `own_score(ability, view)` (own = without equipment bonuses) |
| `ability_requirements` (`AbilityRequirements`) | Ability score minimums (e.g. an armor's Strength) plus the multiclass ability-score prerequisites, both checked by `validate(view)` against the own scores |
| `initiative` (`Initiative`) | Proficiency, roll conditions and a `Bonuses` total; `total(view)` adds the Dexterity modifier, `roll_condition(view)` adds untrained-armor Disadvantage |
| `worn_armor` (`WornArmor`) | The worn body armor's type/name and whether a Shield is wielded - what untrained-armor Disadvantage, spellcasting warnings, Defense, Unarmored Movement and `ArmorClass.calculate` all read |
| `armor_class` (`ArmorClass`) | AC formulas (`ArmorClassFormula`, `UNARMORED_ARMOR_CLASS`), a `Bonuses` total and the Shield's AC bonus; `total(view, ignore_shield=False)` (the Shield counts only with training) |
| `hit_points` (`HitPoints`) | A `Bonuses` total; `total(view)` adds the roll worked out from class levels and Constitution |
| `speed` (`Speed`) | A `Bonuses` total; `total(view)` adds the species' `base_speed` (`character.calculate_speed()`) |
| `carrying_capacity` (`CarryingCapacity`) | Carrying capacity bonus sources; `sources(view)` / `total(view)` also compute the dynamic "Person" base |
| `spellcasting` (`Spellcasting`) | Registered casters and the spell save DC bonus; `spell_slots(view)`/`pact_magic_slots(view)` read the class levels and the fixed slots (sources) through the view |
| `skills` / `saving_throws` (`Skills` / `SavingThrows`) | Proficiency/expertise/advantage flags and a `Bonuses` per skill/ability; `modifier(_, view)`, `roll_condition(_, view)`, and for skills `ability(skill, view)` and `roll_condition_reasons(skill, view)` |
| `weapon_bonuses` (`WeaponBonuses`) | Attack and damage roll bonuses the wielder brings to their weapons, each a `WeaponBonus(applies_to, value, source)`; `attack_bonuses(weapon.traits)` / `damage_bonuses(weapon.traits)` return the ones that apply |

Every part is read through `character.ledger`. Recording goes through
`Effects`, whose methods (`add_damage_resistance`, `add_skill_proficiency`, `register_caster`, …)
each write one part; `Character` has none of them, and once the `Ledger` is evaluated it is
sealed (`Model/Recorder.py`): every part mutator raises `SealedError`, so nothing can record onto
an evaluation after the fact. A test or tool applying one feature to a bare character grants it
with `sources.add_effect(feature)`, a real source like any other, and builds `Character(sources)`.
No part holds a copy of a source. The player's scores before any increase are `base_abilities`,
an immutable `AbilityScores` (change one by assigning `sources.base_abilities.with_scores(...)`); the final
scores are the `get_ability_score()` / `get_own_ability_score()` queries. Likewise
`character.ledger.speed` is the `Speed` part (bonuses only), and the species' walking speed is
`base_speed`.
`character.ledger.initiative` and `.speed` are the parts themselves - the *int* versions are
the `calculate_initiative()` / `calculate_speed()` methods, named after the existing
`calculate_armor_class()` / `calculate_hit_points()` convention so the name doesn't collide with
the part. `character.ledger.senses.ranges` is the resolved `dict[Sense, int]` (`senses` itself
is the `Senses` part).

## Extensions

`data.add_feature(child, extends=Parent)` controls how the sheet **groups** a feature: the child
renders inside the parent's card. Mechanically, a child is a normal feature, and its `apply()` runs
like any other. Don't also grant the same instance plainly, or it will apply twice.

Extensions are declared, not attached: the character records a `FeatureGrant` with `extends=`
(`Model/FeatureGrants.py`), and `ExtensionTree.resolve` finds each parent from the complete set of
grants when the character is read (`character.extensions_of(parent)`), so the parent and the child
may be granted in either order, and no feature is ever changed after it's granted. `Parent` is a
feature type (exactly one granted top-level feature must match) or a feature instance;
`if_missing=IfParentMissing.DROP` or `IfParentMissing.STANDALONE` handles a parent that may not be
granted. A missing or ambiguous parent raises from `validate()`.

## Where a feature was granted, and the sheet's order

Every feature is recorded as a `FeatureGrant` with a `GrantStamp` (`Model/Records/GrantStamp.py`):
the class-relative level it was granted at, the kind of source (a `GrantKind`: species,
background, origin feat, class, subclass) and which one ("Wizard", "Rock Gnome", "Alert"). The builder's `Grants` scope
(`Model/Grants.py`) stamps it. A feature's `origin` text is only its default card label:
`feature_label(feature, character)` (`Presentation/FeatureCards.py`) makes it agree with the stamp - a "... Level N" label takes the
stamped level, and a general feat or epic boon taken at a class level reads "Fighter Level 8" -
so a builder never relabels a feature it grants. The sheet lists each
feature on the level page of its stamped level, and orders features with
`feature_sort_key` (passive last, then name, then kind and source) and extensions by
grant level, then that key (`Presentation/FeatureOrder.py`). Nothing on the sheet depends on the order features were granted in;
`tests/test_order_invariance.py` proves it for every build.

## Feats are taken once

A feat that isn't Repeatable (2024 PHB: everything but Ability Score Improvement, Skilled, Magic
Initiate and Elemental Adept) can be granted only once - from the background, the species and every
Ability Score Improvement level together. `Feature.repeatable` is `True` by default (class features
repeat freely); `OriginFeat`, `GeneralFeat` and `EpicBoon` set it `False`, the Repeatable feats back
to `True`, and `validate()` rejects a second copy.

## Spells

A spell is a `SpellGrant` (`Model/Spells.py`): name, casting ability, ruling, the class-relative
level it was granted at, who granted it (`granted_by`: "Wizard", "Rock Gnome", "Magic Initiate"),
and an optional free-text `source` label for the sheet. Level and species builders grant through a
`Grants` scope (`Model/Grants.py`) that stamps the level and `granted_by`, so neither is state on
the `Character`. A replacement is a declared `SpellReplacement`, resolved when `character.spells`
is read (which lists them in canonical order). The same spell from two grants is listed for each;
the same spell twice from one grant, a replacement of a spell nobody grants, and a chain of
replacements all fail `validate()`.

## Equipment isolation

`CharacterBuilder.build()` hands every sheet the builder's own weapon objects. That's safe
because nothing writes into a weapon after it's constructed: fighting styles and items record
their weapon bonuses on the stat block (`weapon_bonuses`), and mastery is worked out at render time
(`AbstractWeapon.has_mastery`). So a bonus from gear that was later dropped can't stay on the weapon
(`test_dropped_gear_does_not_leave_bonuses_on_weapons`).

## What enforces all this

The whole model:

| Test file | Catches |
|---|---|
| `test_order_invariance.py` | Every build's rendered sheet (full and concise) is identical when its effects apply in another order, and when its features, extensions, spells and replacements are granted in another order (`-m slow` adds reversed order and three more shuffles) |
| `test_part_merge_rules.py` | Every part gives the same answer for the same contributions in every permutation, including the order of listed sources; conflicting grants raise |
| `test_part_resolvers.py` | Every part works out its final values from a fake `CharacterView`, with no builder and no `Character` |
| `test_contracts.py` | `Character` really satisfies `CharacterView` (every member called), `Effects` has none of it, no member returns a part, and every build's content satisfies the `Sources` Protocols |
| `test_layering.py` | Every import points down the layers (`Core` → `Utils` helpers → `Model` → `CharacterContent` → `Builds`/presentation → `Combat`), with an allowlist of today's offenders; no `TYPE_CHECKING`, `typing.cast` or `_as(...)` narrowing |
| `test_creator_roundtrip.py` | The Character Creator loads every build file and generates one that builds to the same stats (builds it can't reproduce yet are strict xfails, with the reason) |
| `test_spell_grants.py` | Spell stamping, duplicate and replacement rules, and order-free spell grants |
| `test_character_model.py` | The sealed `Ledger`, `add_effect`, immutable base scores, declared extensions (either order, `if_missing`, errors) and grant stamps |
| `test_build_snapshots.py` | Every build's stats and every rendered page against golden snapshots |

The feature pipeline in particular, in `tests/test_feature_apply_order.py`:

| Test | Catches |
|---|---|
| `test_effect_order_does_not_change_stats` | Shuffles all of every build's effects (features, extensions, armor, weapons, items, fighting styles), with no exceptions, and requires identical scores, AC, HP, initiative, speed, skills, proficiencies, roll conditions, saves, spell slots, resistances, immunities and senses |
| `TestPreviouslyChronologicalEffects` | Ability caps, item bonuses, Strength requirements, Iron Mind / Unfettered Mind and Skill Expert give one answer in every permutation |
| `TestCompetingEffectsNeverOverwrite` | Unarmored Defenses don't stack, armor and Shield interactions, Defense, roll-condition cancelling, skill-ability overrides and multiclass spell slots, in every permutation |
| `test_effects_can_only_record` | `Effects` exposes only `add_*`/`set_*`/`register_*` methods and holds nothing but its private record |
| `test_evaluation_passes_apply_the_write_only_record` | Every build's evaluation hands `apply()` an `Effects`, never the `Character` |
| `test_content_never_reaches_into_the_record` | **Static:** no code in `CharacterContent` touches `Effects._ledger` |
| `TestModifierBonusesTrackLaterScoreIncreases`, `TestJackOfAllTrades`, `TestExpertiseRequirement`, `TestExtensionsApply`, `test_dropped_gear_does_not_leave_bonuses_on_weapons` | Formula features, validation, extensions and equipment isolation |

The shuffle test was checked by mutation: resolving capped increases in grant order fails many
builds. An `apply()` that tries to read a stat (Defense reading armor state, say) now fails with
an `AttributeError` in every build that uses it.

When the model changed, every one of the 136 builds produced identical ability scores, AC, HP,
initiative, speed, skills, saves, proficiencies, roll conditions, spell and pact slots,
resistances, senses and weapon attack/damage numbers.

## Known findings outside the feature pipeline (not changed)

These are rules or content decisions rather than ordering problems:

1. **Rock Gnome hardcodes Intelligence** for Mending and Prestidigitation
   (`CharacterContent/Species/Gnome.py`). The 2024 Gnomish Lineage lets you choose Intelligence,
   Wisdom or Charisma.
2. **The fallback spellcasting ability for species and feat spells is picked from base scores**
   in `CharacterBuilder.build()`, before background, ASI and feat increases.
3. **Finesse weapon damage label.** When Strength and Dexterity modifiers are equal, the label
   depends on set ordering. The number is the same either way.
4. **Weapon, armor and tool proficiencies come from features.** The starting class grants its
   Core Traits (`ClassProficiencies`), a class gained by multiclassing grants its "As a Multiclass
   Character" subset (`MulticlassProficiencies`), and subclass/feat grants live in the feature that
   describes them. `tests/test_proficiencies.py` fails on any builder that grants one directly. The
   multiclass skill and Musical Instrument *choices* aren't modelled. The stat block is the only
   place proficiencies live; `player_is_proficient=True` on a weapon is only for proficiency no
   grant describes (Unarmed Strike).
5. **Choices with no parameter yet.** Otherworldly Glamour, Genie's Splendor, Knightly Envoy and
   Dragonscarred describe a skill or resistance choice the builders don't take, so only their
   choice-independent parts apply.
