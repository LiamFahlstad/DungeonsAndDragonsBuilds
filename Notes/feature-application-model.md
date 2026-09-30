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

There is one object, `Character` (`Model/Character.py`). It holds the player's decisions and
the sources they grant (features, spells, fighting styles, `inventory`, base ability scores and
speed), and answers every query (`calculate_armor_class()`, `get_skill_modifier()`, ...).

Evaluation is internal and lazy. The first query after a change builds a fresh `Effects` record
(`Model/Effects.py`: one part per concern, see below), starting from a copy of the base
ability scores, the base speed and the class spellcasting ability, then:

| # | Stage | What runs |
|---|---|---|
| 1 | **Record** | `apply(effects)` of everything in `iter_stat_effects()`: features and their extensions, armor, weapons, items, and fighting styles with a computed effect (Defense, Archery, Dueling, Thrown Weapon Fighting). **Any order.** Every call gets the same write-only `Effects` view of fresh `Parts` |
| 2 | **Validate** | Only in `validate()`, the single entry point (the writers and the combat UI call it first): first the sources (name, subclass, abilities, speed, size and base class set, at most one worn body armor, the attunement limit), then `Effects.validate()`: expertise needs proficiency, ability requirements such as an armor's Strength, and multiclass ability minimums |

Weapons are never changed while a character is evaluated. A bonus the wielder brings to their
weapons (Archery's +2 to attack rolls with Ranged weapons, Bracers of Archery's +2 damage with
bows) is recorded as a `WeaponAttackBonus` / `WeaponDamageBonus` improvement with a filter for the
weapons it covers, and each weapon combines it with its own bonuses on read. So a builder's weapon
objects are shared by every sheet it builds, with no copies and no idempotence guards.

The evaluation is cached under a version key: the character's own version (bumped by every
`add_*`/`set_*` call and, through an attrs `on_setattr` hook, by assigning any public field), the
inventory's version (bumped by every gear change), and a global count of feature extensions.
`extend_feature()` can't reach the character a feature was granted to, so it bumps that count
(`note_feature_extended()`) and every character re-evaluates on its next query.

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
| Armor training, tools | `armor_training`, `tool_proficiencies` on `Character.equipment_training` | Read directly (the same tool from two sources is listed once) |
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
    lambda cs: 0 if cs.worn_armor.body_armor_type == Definitions.ArmorType.HEAVY else 10
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
| "…while (not) wearing armor / wielding a Shield" | A **formula** on `SpeedBonus` / `ArmorClassBonus` reading `cs.worn_armor.body_armor_type`, `cs.is_wearing_armor`, `cs.worn_armor.shield_wielded` |
| "Your AC equals 10 + DEX + WIS" | `MultiAbilityArmorClass(10, [DEX, WIS])`, plus `allows_shield=False` if a Shield disables it |
| "You gain Expertise in X" | `SkillExpertise([X])`. The proficiency may come from anywhere; validation checks the pair |
| "Increase STR by 2, to a maximum of 20" | `AbilityScoreBonus([...], total=2, max_score=20)` |
| "Your Strength must be at least N" | `StrengthRequirement(N, reason)` (checked in validation) |
| "You gain proficiency with Martial weapons / Heavy armor / Smith's Tools" | `GrantWeaponProficiency([...])`, `GrantArmorTraining([...])`, `GrantToolProficiency([...])` |
| "+2 to attack rolls with Ranged weapons" / "+2 to damage rolls with the Longbow" | `WeaponAttackBonus(applies_to, 2, source)` / `WeaponDamageBonus(...)`, where `applies_to` is a `weapon -> bool` filter. Never write into the weapon |
| An upgrade to an earlier feature | `parent.extend_feature(Upgrade())`. Its `apply()` runs too, so don't also `add_feature()` it |

**`apply(self, effects: Effects)` can only record.** `Effects` offers `add_*`/`set_*`/
`register_*` methods and nothing else - no scores, no proficiency flags, no AC or armor state, and
no levels either. If a value depends on anything, pass a formula (`lambda character: ...`); it gets
the finished `Character` when the value is read. Every bonus with a formula form has an
`add_derived_*` method on `Effects` (skills, saving throws, AC, HP, speed, initiative), and the
improvements above choose between the flat and formula forms for you. `get_description()` and the
other rendering methods still get the `Character`, and may read anything.

## The parts

`Effects` (`Model/Effects.py`) holds one part per concern (`Model/*.py`), and
`Character` exposes each part under its own name, plus a few queries that combine several of them
(untrained-armor disadvantage, the final AC, `warnings`, `validate()`). Each part owns its own state *and* the queries on that
state; a part never reaches back into the character, so a value from another part (or the finished
character, for formula evaluation) is always passed in as an argument, e.g.
`HitPoints.calculate(class_levels, constitution_modifier, character)` and
`Initiative.total(proficiency_bonus, character)`. No part imports `CharacterContent`.

`Bonuses` (`Model/Bonuses.py`) is a small value object - flat values and formulas
(`DerivedBonus`), each with a source label - shared by every part that is "a bonus total plus
sources": `Initiative`, `ArmorClass`, `HitPoints`, `Speed`, `Skills` and `SavingThrows` each hold
one (or a `dict[..., Bonuses]` for the per-skill/per-ability ones) instead of reimplementing the
flat-list/formula-list/source-list shape themselves.

| Part (`character.<attr>`) | Owns |
|---|---|
| `equipment_training` (`EquipmentTraining`) | `weapon_proficiencies`, `armor_training`, `tool_proficiencies`, `has_shield_training` |
| `languages` (`Languages`) | Known languages, each with sources (`knows`, `sources`, `add`) |
| `defenses` (`Defenses`) | Damage resistance/immunity, condition immunity, each with sources |
| `senses` (`Senses`) | Sense ranges (`.ranges`) and "or extend" grants |
| `ability_requirements` (`AbilityRequirements`) | Ability score minimums (e.g. an armor's Strength) plus the multiclass ability-score prerequisites, both checked by `validate(abilities, class_levels)` |
| `initiative` (`Initiative`) | Proficiency, roll conditions and a `Bonuses` total (`character.calculate_initiative()` / `.initiative_roll_condition` combine it with the Dexterity modifier and untrained-armor Disadvantage) |
| `worn_armor` (`WornArmor`) | The worn body armor's type/name and whether a Shield is wielded - what untrained-armor Disadvantage, spellcasting warnings, Defense, Unarmored Movement and `ArmorClass.calculate` all read |
| `armor_class` (`ArmorClass`) | AC formulas (`ArmorClassFormula`, `UNARMORED_ARMOR_CLASS`), a `Bonuses` total and the Shield's AC bonus; `calculate(abilities, character, is_wielding_shield, has_shield_training)` |
| `hit_points` (`HitPoints`) | A `Bonuses` total; `calculate(class_levels, constitution_modifier, character)` |
| `speed` (`Speed`) | Base walking speed and a `Bonuses` total (`character.calculate_speed()`) |
| `carrying_capacity` (`CarryingCapacity`) | Carrying capacity bonus sources; `sources(strength_modifier)` / `total(strength_modifier)` also compute the dynamic "Person" base |
| `spellcasting` (`Spellcasting`) | Spell casting ability, registered casters, spell save DC bonus; `spell_slots()`/`pact_magic_slots()` also take `class_levels` |
| `skills` / `saving_throws` (`Skills` / `SavingThrows`) | Proficiency/expertise/advantage flags, a `Bonuses` per skill/ability (`get_total_bonus(skill_or_ability, character)`) |
| `weapon_bonuses` (`WeaponBonuses`) | Attack and damage roll bonuses the wielder brings to their weapons, each a `WeaponBonus(applies_to, value, source)`; `attack_bonuses(weapon)` / `damage_bonuses(weapon)` return the ones that apply |

Every part is exposed directly under its own name, for reading. Recording goes through
`Effects`, whose methods (`add_damage_resistance`, `add_skill_proficiency`, `register_caster`, …)
each write one part; `Character` has none of them, so nothing can record onto an evaluation that
the next change would discard. A test or tool applying one feature to a bare character passes
`character.effects`, a write-only view of the current evaluation.
`character.abilities` is the evaluated `AbilityScores` (every increase applied); the player's
scores before any increase are `base_abilities`. Likewise `character.speed` is the `Speed` part,
and the species' walking speed is `base_speed`.
`character.initiative` and `.speed` are the parts themselves - the *int* versions are
the `calculate_initiative()` / `calculate_speed()` methods, named after the existing
`calculate_armor_class()` / `calculate_hit_points()` convention so the name doesn't collide with
the part. `character.senses.ranges` is the resolved `dict[Sense, int]` (`senses` itself
is the `Senses` part).

## Extensions

`parent.extend_feature(child)` controls how the sheet **groups** a feature: the child renders
inside the parent's card. Mechanically, a child is a normal feature, and its `apply()` runs like
any other. Don't also `add_feature()` the same instance, or it will apply twice.

## Equipment isolation

`CharacterBuilder.build()` hands every sheet the builder's own weapon objects. That's safe
because nothing writes into a weapon after it's constructed: fighting styles and items record
their weapon bonuses on the stat block (`weapon_bonuses`), and mastery is worked out at render time
(`AbstractWeapon.has_mastery`). So a bonus from gear that was later dropped can't stay on the weapon
(`test_dropped_gear_does_not_leave_bonuses_on_weapons`).

## What enforces all this

All in `tests/test_feature_apply_order.py`:

| Test | Catches |
|---|---|
| `test_effect_order_does_not_change_stats` | Shuffles all of every build's effects (features, extensions, armor, weapons, items, fighting styles), with no exceptions, and requires identical scores, AC, HP, initiative, speed, skills, proficiencies, roll conditions, saves, spell slots, resistances, immunities and senses |
| `TestPreviouslyChronologicalEffects` | Ability caps, item bonuses, Strength requirements, Iron Mind / Unfettered Mind and Skill Expert give one answer in every permutation |
| `TestCompetingEffectsNeverOverwrite` | Unarmored Defenses don't stack, armor and Shield interactions, Defense, roll-condition cancelling, skill-ability overrides and multiclass spell slots, in every permutation |
| `test_effects_can_only_record` | `Effects` exposes only `add_*`/`set_*`/`register_*` methods and holds nothing but its private record |
| `test_evaluation_passes_apply_the_write_only_record` | Every build's evaluation hands `apply()` an `Effects`, never the `Character` |
| `test_content_never_reaches_into_the_record` | **Static:** no code in `CharacterContent` touches `Effects._parts` |
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
