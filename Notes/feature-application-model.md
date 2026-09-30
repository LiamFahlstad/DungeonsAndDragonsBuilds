# How Features Are Applied

This describes how the engine turns granted features, armor, weapons and items into the numbers
on a character sheet, why the order they're applied in doesn't matter, and how to write an effect
whose value depends on something else ("a bonus equal to your Wisdom modifier", "while you aren't
wearing Heavy armor").

It replaces two older models: `ApplyWhen.IMMEDIATE` / `ApplyWhen.LAST`, and after that "apply in
grant order, with a few deliberately chronological exceptions". Neither exists any more.

## The short version

1. **`apply()` only records facts.** A proficiency, a +1, "add WIS to AC", "+10 speed unless in
   Heavy armor", "+2 STR to a maximum of 20". It never reads the stat block.
2. **The stat block works every value out when it's read**, from everything recorded. So nothing
   can depend on what happened to apply first.
3. **Requirements are checked once, at the end** (`CharacterStatBlock.validate()`): expertise
   needs proficiency, an armor needs a minimum Strength, and a multiclass character needs the
   ability minimums for every class it has.
4. **There are no exceptions.** A test shuffles every build's effects (features, extensions,
   armor, weapons, items and fighting styles together) and requires identical sheets. Two guard
   tests fail on any effect that reads a stat during setup.

This follows the design of `~/Scripts/DungeonsAndDragons`: effects are recorded on a ledger,
then evaluated once in the rules' own dependency order. Here the stat block is the ledger, and
its getters are the evaluation.

## The pipeline

`CharacterSheetData.setup_character_stat_block()` first calls `CharacterSheetData.validate()`
(every field it needs to build a stat block is set, at most one worn body armor, and the
attunement limit), then builds a fresh `CharacterStatBlock` from copies of the base ability, skill and
saving-throw blocks, then:

| # | Stage | What runs |
|---|---|---|
| 1 | **Record** | `apply()` of everything in `iter_stat_effects()`: features and their extensions, armor, weapons, items, and stat fighting styles (Defense). **Any order.** |
| 2 | **Validate** | `character.validate()`: expertise needs proficiency, ability requirements such as an armor's Strength, and multiclass ability minimums |
| 3 | **Weapons** | Weapon fighting styles (Archery, Dueling, …) and `item.apply_to_weapons()` (Bracers of Archery). These write into the per-build weapon copies and read nothing from the stat block |

The result is cached. The cache is dropped by any `add_*` call, and also whenever the set of
features and extensions changes. `extend_feature()` has no reference back to the sheet data, so
without that second check a late extension would be missed.

## How each value is worked out on read

| Value | Recorded as | Resolved by |
|---|---|---|
| Ability score | Base score + `(ability, bonus, max_score)` increases | `AbilityScores.get_score`: capped increases lowest cap first, then uncapped (equipment) bonuses on top |
| Ability modifier | | From the score |
| Skill modifier | Proficiency/expertise flags, flat and formula bonuses, ability overrides | `CharacterStatBlock.get_skill_modifier`. With several overrides for one skill, the best ability is used |
| Skill roll condition | Every Advantage/Disadvantage source, with reasons | `Skills.get_roll_condition`: both cancel out |
| Saving throw | Proficiency flags, conditional grants, flat and formula bonuses | `get_saving_throw_modifier`, `SavingThrows.is_proficient` |
| AC | Every `ArmorClassFormula` (unarmored default, Unarmored Defense, worn armor), flat and formula bonuses | `calculate_armor_class`: the best applicable formula + bonuses |
| Speed | Base + flat and formula bonuses | `CharacterStatBlock.calculate_speed()` |
| Senses | Plain grants and "or extend" grants | `CharacterStatBlock.senses.ranges`: best plain grant + every extension |
| Weapon proficiency | `weapon_proficiencies` on `CharacterStatBlock.equipment_training` (categories such as Martial weapons, or single kinds such as the Scimitar) | `AbstractWeapon.is_proficient(cs)`: an explicit `player_is_proficient` override, or any recorded grant that covers the weapon |
| Armor training, tools | `armor_training`, `tool_proficiencies` on `CharacterStatBlock.equipment_training` | Read directly (the same tool from two sources is listed once) |
| Untrained armor / Shield (2024 PHB) | Worn armor, wielded Shield (`CharacterStatBlock.worn_armor`), `armor_training` | Untrained armor: a Disadvantage source on STR/DEX skills (by the skill's actual ability), STR/DEX saves, initiative and STR/DEX weapon attacks, plus a `warnings` entry (no spellcasting). Untrained Shield: its AC bonus is left out. `calculate_armor_class(ignore_shield=True)` gives the sheet's "w/o Shield" AC |
| Initiative | DEX, proficiency, flat and formula bonuses; roll-condition sources | `calculate_initiative()`, `initiative_roll_condition` |
| Spell slots | Registered casters `{class: CasterType}` | `spell_slots` / `pact_magic_slots`, via `Core.SpellcastingRules.calculate_spell_slots` |
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

`CharacterStatBlock.armor_class.armor_class_formulas` starts with 10 + DEX. `MultiAbilityArmorClass` (Unarmored
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
    lambda cs: 0 if cs.worn_armor.body_armor_type == Definitions.ArmorType.HEAVY else 10
).apply(character_stat_block)

# Defense fighting style, Soul of the Forge
ArmorClassBonus(lambda cs: 1 if cs.is_wearing_armor else 0).apply(character_stat_block)
```

## Writing a new feature effect

| The effect says… | Write it as |
|---|---|
| "You gain proficiency in X" | `SkillProficiency([X])` / `SavingThrowProficiency([...])` |
| "…if you already have it, choose another" | `SavingThrowProficiencyOrAlternative(X, [alternatives])` |
| "You gain Darkvision 60 ft. If you already have it, its range increases by 60 ft." | `GrantOrExtendSense(Sense.DARKVISION, 60, name)`. Resolved on read as the best other grant + 60 |
| "+N to …" (a fixed number) | `SkillBonus(skill, N)`, `SavingThrowBonus(..., N)`, `ArmorClassBonus(N)`, `SpeedBonus(N)`, … |
| "a bonus equal to your *ability* modifier" / "half your proficiency bonus" | A **formula**: `SkillBonus(skill, lambda cs: ...)`, `SavingThrowBonus`, `InitiativeBonus` |
| "…while (not) wearing armor / wielding a Shield" | A **formula** on `SpeedBonus` / `ArmorClassBonus` reading `cs.worn_armor.body_armor_type`, `cs.is_wearing_armor`, `cs.worn_armor.shield_wielded` |
| "Your AC equals 10 + DEX + WIS" | `MultiAbilityArmorClass(10, [DEX, WIS])`, plus `allows_shield=False` if a Shield disables it |
| "You gain Expertise in X" | `SkillExpertise([X])`. The proficiency may come from anywhere; validation checks the pair |
| "Increase STR by 2, to a maximum of 20" | `AbilityScoreBonus([...], total=2, max_score=20)` |
| "Your Strength must be at least N" | `StrengthRequirement(N, reason)` (checked in validation) |
| "You gain proficiency with Martial weapons / Heavy armor / Smith's Tools" | `GrantWeaponProficiency([...])`, `GrantArmorTraining([...])`, `GrantToolProficiency([...])` |
| An upgrade to an earlier feature | `parent.extend_feature(Upgrade())`. Its `apply()` runs too, so don't also `add_feature()` it |

**Never read the stat block inside `apply()`.** That includes ability scores and modifiers,
proficiency flags, AC and armor state. If a value depends on anything, pass a formula. Every part
that takes bonuses (`Initiative`, `ArmorClass`, `HitPoints`, `Speed`, `Skills`, `SavingThrows`)
accepts one via its own `Bonuses` instance (`StatBlocks/Bonuses.py`) - `add(value, source)` for a
flat value, `add_formula(formula, source)` for one evaluated at read time. **Safe to read
directly:** class levels, character level and proficiency bonus. They're fixed before any effect
applies and no effect changes them.

## The parts

`CharacterStatBlock` is a composition root: a thin object holding one part per concern
(`StatBlocks/*.py`), plus a few queries that combine several of them (untrained-armor disadvantage,
the final AC, `warnings`, `validate()`). Each part owns its own state *and* the queries on that
state; a part never reaches back into the character, so a value from another part (or the finished
character, for formula evaluation) is always passed in as an argument, e.g.
`HitPoints.calculate(class_levels, constitution_modifier, character)` and
`Initiative.total(proficiency_bonus, character)`. No part imports `CharacterContent`.

`Bonuses` (`StatBlocks/Bonuses.py`) is a small value object - flat values and formulas
(`DerivedBonus`), each with a source label - shared by every part that is "a bonus total plus
sources": `Initiative`, `ArmorClass`, `HitPoints`, `Speed`, `Skills` and `SavingThrows` each hold
one (or a `dict[..., Bonuses]` for the per-skill/per-ability ones) instead of reimplementing the
flat-list/formula-list/source-list shape themselves.

| Part (`character_stat_block.<attr>`) | Owns |
|---|---|
| `equipment_training` (`EquipmentTraining`) | `weapon_proficiencies`, `armor_training`, `tool_proficiencies`, `has_shield_training` |
| `languages` (`Languages`) | Known languages, each with sources (`knows`, `sources`, `add`) |
| `defenses` (`Defenses`) | Damage resistance/immunity, condition immunity, each with sources |
| `senses` (`Senses`) | Sense ranges (`.ranges`) and "or extend" grants |
| `ability_requirements` (`AbilityRequirements`) | Ability score minimums (e.g. an armor's Strength) plus the multiclass ability-score prerequisites, both checked by `validate(abilities, class_levels)` |
| `initiative` (`Initiative`) | Proficiency, roll conditions and a `Bonuses` total (`character_stat_block.calculate_initiative()` / `.initiative_roll_condition` combine it with the Dexterity modifier and untrained-armor Disadvantage) |
| `worn_armor` (`WornArmor`) | The worn body armor's type/name and whether a Shield is wielded - what untrained-armor Disadvantage, spellcasting warnings, Defense, Unarmored Movement and `ArmorClass.calculate` all read |
| `armor_class` (`ArmorClass`) | AC formulas (`ArmorClassFormula`, `UNARMORED_ARMOR_CLASS`), a `Bonuses` total and the Shield's AC bonus; `calculate(abilities, character, is_wielding_shield, has_shield_training)` |
| `hit_points` (`HitPoints`) | A `Bonuses` total; `calculate(class_levels, constitution_modifier, character)` |
| `speed` (`Speed`) | Base walking speed and a `Bonuses` total (`character_stat_block.calculate_speed()`) |
| `carrying_capacity` (`CarryingCapacity`) | Carrying capacity bonus sources; `sources(strength_modifier)` / `total(strength_modifier)` also compute the dynamic "Person" base |
| `spellcasting` (`Spellcasting`) | Spell casting ability, registered casters, spell save DC bonus; `spell_slots()`/`pact_magic_slots()` also take `class_levels` |
| `skills` / `saving_throws` (`Skills` / `SavingThrows`) | Proficiency/expertise/advantage flags, a `Bonuses` per skill/ability (`get_total_bonus(skill_or_ability, character)`) |

Every part is exposed directly under its own name. `CharacterStatBlock`'s own methods
(`add_damage_resistance`, `calculate_armor_class`, `get_sense_range`, …) are kept as one-line
delegations to the parts, so existing feature call sites don't need to change; `spell_casting_ability`
is a read-only delegating property for the same reason (too many callers to rewrite safely).
`character_stat_block.initiative` and `.speed` are the parts themselves - the *int* versions are
the `calculate_initiative()` / `calculate_speed()` methods, named after the existing
`calculate_armor_class()` / `calculate_hit_points()` convention so the name doesn't collide with
the part. `character_stat_block.senses.ranges` is the resolved `dict[Sense, int]` (`senses` itself
is the `Senses` part).

## Extensions

`parent.extend_feature(child)` controls how the sheet **groups** a feature: the child renders
inside the parent's card. Mechanically, a child is a normal feature, and its `apply()` runs like
any other. Don't also `add_feature()` the same instance, or it will apply twice.

## Equipment isolation

`CharacterBuilder.build()` gives each sheet its own **copies** of the builder's weapons. Fighting
styles and items write into weapon objects. Without the copies, a bonus from gear that was later
dropped stayed on the weapon for every subsequent build.

## What enforces all this

All in `tests/test_feature_apply_order.py`:

| Test | Catches |
|---|---|
| `test_effect_order_does_not_change_stats` | Shuffles all of every build's effects (features, extensions, armor, weapons, items, fighting styles), with no exceptions, and requires identical scores, AC, HP, initiative, speed, skills, proficiencies, roll conditions, saves, spell slots, resistances, immunities and senses |
| `TestPreviouslyChronologicalEffects` | Ability caps, item bonuses, Strength requirements, Iron Mind / Unfettered Mind and Skill Expert give one answer in every permutation |
| `TestCompetingEffectsNeverOverwrite` | Unarmored Defenses don't stack, armor and Shield interactions, Defense, roll-condition cancelling, skill-ability overrides and multiclass spell slots, in every permutation |
| `test_effects_do_not_read_mutable_stats_during_setup` | **Runtime:** instruments every stat reader and property during setup and fails when any effect reads one, including through helpers, items, armor or extensions. The allow-list is empty |
| `test_apply_methods_do_not_snapshot_derived_stats` | **Static:** the same rule, including armor-state reads, for code that no current build runs |
| `TestModifierBonusesTrackLaterScoreIncreases`, `TestJackOfAllTrades`, `TestExpertiseRequirement`, `TestExtensionsApply`, `test_dropped_gear_does_not_leave_bonuses_on_weapons` | Formula features, validation, extensions and equipment isolation |

Both the shuffle test and the guards were checked by mutation. Resolving capped increases in
grant order, or making Defense read armor state inside `apply()`, fails many builds.

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
