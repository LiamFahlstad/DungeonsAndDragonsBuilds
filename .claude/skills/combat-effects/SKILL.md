---
name: combat-effects
description: Combat effects - what a spell or feature does in a fight (saving throw or attack roll, which ability, damage dice and types, half on a save, a condition or badge and how long it lasts, what the badge does while it's on, upcasting, cantrip scaling, healing, Temporary Hit Points, a use that casts a spell, or nothing to apply at all), written as CombatEffect objects in the spell's class (CharacterContent/Spells/SpellClasses) or the feature's class (its combat_effects() method), and used by the combat UI's Custom Effect picker instead of reading the rules text. The same CombatEffect model monster abilities use. Holds the format, the design principles, the rubric for each field and for features, and a script that checks every spell's and party feature's effects, lists spells without them (by level, class or campaign) and a party's features still read from their text, gives a coverage line per campaign, reports notes repeated often enough to be a missing field, drafts spells' effects from the text as Python for review, writes reviewed drafts into each spell's class and compares them with the text reading. Use when adding, reviewing or fixing a spell's or feature's combat effects, when a spell or feature fills the Custom Effect form wrongly, when a campaign's spells or features should be checked, or when someone asks why a picker row says "Read from its rules text".
---

# Combat effects (spells and features)

The combat UI's Custom Effect dialog fills its form from a spell
(`spell_option()` in `Combat/CombatUIQt/effect_options.py`). A spell whose
`combat_effects()` returns a list is filled from it; any other spell is read
from its rules text with regexes, which the GM then has to check. Combat
effects replace that guess with checked data, so every one must be right.

Spells, features and monster abilities all describe themselves with the same
model, `CombatEffect` (`Model/Content/CombatEffect.py`; its docstring has every
field). The plan behind this is `Notes/combat-effects-plan.md`.

## Principles

From `Notes/combat-effects-plan.md` (Design principles); each is a reason a
draft gets sent back:

1. **One vocabulary.** Spells, features and monster abilities all return
   `CombatEffect`s; a spell and a feature that do the same thing are
   written the same way.
2. **The model describes the rules, not the form.** Say what happens; the
   picker decides what fits the dialog and turns the rest into notes.
3. **Caster numbers are worked out when used.** No DC, attack bonus or
   modifier written in; a feature may work out its own from `character`.
4. **`None`, `[]` and a list mean the same everywhere:** not described yet
   / nothing to apply / one picker row per item.
5. **Notes are the escape hatch, and a repeated note is a missing field.**
   `notes` lists the ones written for three or more spells or features;
   report any you add to.
6. **The simulator never guesses positions or table decisions.** What
   depends on where creatures are, or on a choice at the table, is a note
   or a trigger with a `when` (a prompt), never counted.
7. **Nothing lands on a target unless the effect says so.**
8. **An extension's uses are its parent's.** An extension that is another
   way to use its parent describes its own rows (they spend the parent's
   uses unless it has its own); one that only changes the parent's effect
   uses `adjust_combat_effect` and returns `[]`.

## Where they live

In the spell's **class**, `CharacterContent/Spells/SpellClasses/<Level>.py`
(`Cantrips.py`, `Level1.py`, ...; see `SpellFactory/ClassSpell.py`):

```python
class Fireball(ClassSpell):
    rules = SpellRules(...)

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll=EffectRoll.SAVE,
                save_ability=Ability.DEXTERITY,
                half_on_success=True,
                damage=(CombatDamage("8d6", DamageType.FIRE, upcast="1d6"),),
            )
        ]
```

The list holds:

- one effect per way to cast it: usually one; several for options with
  different mechanics (Command's five, each `name="Command: Grovel"`) or
  steps of one casting (Ice Knife's shard, then its explosion), or
- nothing (`[]`) when the spell has nothing to apply to a creature in a fight.

A spell whose `combat_effects()` returns `None` (no method, or a JSON spell)
is "not described yet" and is read from its text.

**Every spell is a class** (since 2026-11-09). A spell scraped since, a
record with no class yet, isn't converted by hand: `add` turns it into a
class (with `CharacterContent/Spells/SpellClassConverter.py`, which checks
the class says what the record said) and gives it your effects. One the
converter can't write (a malformed record) is refused, and `todo` says why;
its record wants a scraper fix. There is no JSON for combat effects any
more: never edit the source spell JSON by hand.

Leave out every number that belongs to the caster (`dc`, `attack_bonus`): the
picker works those out. Leave out every field at its default.

## Tools

```bash
S=.claude/skills/combat-effects/combat_effects.py
python $S todo --campaign time_loop_pr          # what's missing, and where each goes (also --level N, --class Wizard, --name X)
python $S draft --level 2 --out <scratchpad>/draft.py   # drafts as Python + a review sheet with each spell's full text
python $S add <scratchpad>/draft.py             # check the reviewed EFFECTS, write each into its class
python $S compare --level 2                     # where the effects and the text reading disagree
python $S check                                 # run before you report: exit 1 on any problem
python $S features --campaign curse_of_the_lich [--member Kivi] [--all]   # a party's features still read from text, with file:line
python $S coverage                              # one line per campaign: spells and features described
python $S notes [--min 3]                       # notes on 3+ spells/features: a field the model may be missing
```

The draft file is a Python module: `EFFECTS = {"Spell name": [CombatEffect(...), ...]}`,
each spell's checks as comments above it, imports included. Write drafts in
the scratchpad, never the repo. A draft the model refuses (a damage type to
choose with no choices yet) is left as a dict with the reason; `add` refuses
it until you write it as `CombatEffect(...)`. `add` writes nothing if any
spell in the file has a problem, and refuses to replace effects a spell has
already unless you pass `--force`. Use that only when you are fixing that
spell on purpose; it replaces the whole `combat_effects()` method, hand
edits included.

To fix one spell that has a class, you can also edit its `combat_effects()`
directly; then run `check` and the tests below.

## Procedure

1. `todo` for your filter, then `draft --out`.
2. For **every** spell, read its full description on the review sheet and fix
   the draft field by field against the rubric below. The draft comes from the
   regex reading these effects exist to replace. "Improved description agrees"
   only means the two automatic readings agree, not that they are right.
3. `add`, then `compare` for your filter. Every difference it lists must be one
   you made on purpose (the reason is usually in the effect's notes).
4. `check`, and `./run_tests.sh -q tests/test_spell_classes.py tests/test_spell_combat_effects.py tests/test_combat_ui_effect_options.py tests/test_picker_rows.py`.
   A picker-row golden that changes is a spell now described: read the
   diff (the `snapshot-diffs` skill) before `UPDATE_SNAPSHOTS=1`.

## Features

A feature's effects live in its class's `combat_effects(self, character)`
(`Model/Content/Feature.py` has the contract). There is no draft or `add`
for features: write the method by hand, then `check` and
`./run_tests.sh -q tests/test_feature_combat_effects.py tests/test_picker_rows.py`.
Work party by party: `features --campaign <name>` lists what's left, with
where each class is.

The rubric above applies; on top of it:

- **`[]` for a feature with nothing to put on a creature in a fight**:
  senses (Darkvision), proficiencies, languages, a feature that only grants
  spells (its spells are in the picker as spells: Cartographer Spells),
  one used from its own control (Wild Shape, a summon), Spellcasting
  itself, or a rider that only changes another feature (then also
  `adjust_combat_effect`). A passive feature that only changes the stat
  block can stay `None` (no row either way); give it `[]` only when it has
  `passive=False`.
- **Work numbers out from `character`**: the level's dice
  (`SNEAK_ATTACK_DICE.at(character)`), a pool (Lay on Hands' `5 x Paladin
  level`, said in a note), a DC through `calculate_dc`. `with_bonus("1d8",
  4)` writes "1d8 + 4"; Radiance of the Dawn writes `f"2d10 + {level}"`.
- **A use that casts a spell** sets `spell="Hunter's Mark"` and only what
  differs: its `name` ("Divine Smite (Paladin's Smite)"), a note ("Without
  a spell slot, once per Long Rest."), another action. The spell's own
  effect, badge and modifiers come along. A feature that lets its owner
  cast a level 1+ spell it grants without a slot (Fey Touched, Fiendish
  Legacy) gives one such row per spell; a cantrip's needs none.
- **A feature's own attack** (Martial Arts' Bonus Unarmed Strike, Flurry of
  Blows) sets `attack_bonus` itself, worked out from `character`: the
  picker's default is the spell attack bonus.
- **A badge its owner puts on itself** (Patient Defense's Dodge, Sacred
  Weapon) says "pick yourself as the target" in a note; what it does only
  some of the time is a modifier with a `when` (Dodge's Disadvantage "if
  it can see the attacker"), which the simulator shows but doesn't count.
- **Several ways to use one feature** are several effects, each with a
  `name` (Channel Divinity's "Divine Spark: heal", "Divine Spark: harm", "Turn Undead"); an extension's ways go
  in the extension's own `combat_effects()`, not the parent's.
- **A choice at the table** (which damage type, which of two options) is
  `CombatDamage(dice, None, choices)` or one effect per option, never a
  guess.
- **A feature that changes another's effect** (Combat Inspiration on
  Bardic Inspiration, Agonizing Blast on Eldritch Blast) overrides
  `adjust_combat_effect(character, source, effect)`: check `source` first,
  only add (a note, a damage part, `add_modifier`), and return
  `dataclasses.replace(effect, ...)`.
- **Badges and their modifiers** work as for spells: a feature that lasts
  and marks its targets (Sacred Weapon, Rage) gives a `CombatCondition`
  named after the feature, with its `modifiers` when the model has them.

## Rubric

Names are the Python ones; `Ability`, `Condition` and `DamageType` come from
`Core.Definitions`, the rest from `Model.Content.CombatEffect`.

- **`roll`.** `EffectRoll.ATTACK` when the caster makes a spell attack, or a
  weapon attack the spell grants (True Strike). `EffectRoll.SAVE` when the
  *target* rolls a save that decides the effect. Leave it out
  (`EffectRoll.NONE`) when it just happens: healing, buffs, auto-hit damage
  (Magic Missile), or a condition with no save (Invisibility). If a spell has
  both an attack and a save, give each its own effect (Ice Knife: "Ice Knife:
  shard", then "Ice Knife: explosion").
- **`save_ability`** (with a save): `Ability.DEXTERITY`. **`half_on_success`**
  only when the text says half as much damage on a success. **`repeat_save`**
  only for "at the end of each of its turns, the target repeats the save,
  ending the effect on a success" (Hold Person, Tasha's). Other later saves,
  such as Sleep's second save, an Athletics check to escape, or a save when
  it enters the area, go in `notes`.
- **`damage`.** A tuple of `CombatDamage(dice, damage_type)`, only the damage
  the hit or failed save deals *now*. Damage on later turns, on moving
  through an area, or on a later hit goes in `notes` (Witch Bolt's 1d12,
  Spike Growth, Ensnaring Strike), or in the badge's modifiers when the
  model has it (Hunter's Mark's `ExtraDamageFrom`, a turn's damage as a
  trigger row: see Triggers). One part per damage type.
  `upcast="1d6"` goes only on the part the higher-level paragraph names.
  `cantrip=((5, "2d8"), (11, "3d8"), (17, "4d8"))` only when the dice
  themselves grow (Eldritch Blast's extra beams are `instances`). `add_modifier=True`
  when the text adds "your spellcasting ability modifier"; damage equal to
  the modifier alone is dice `"0"` with it (Green-Flame Blade's leaping
  fire, `cantrip` giving its dice from level 5). When the caster
  picks the type: `CombatDamage("2d6", None, (DamageType.ACID, DamageType.COLD,
  ...))`. Damage only some targets take is a part with `when`, what follows
  "if": Divine Smite's `CombatDamage("1d8", DamageType.RADIANT, when="the
  target is a Fiend or an Undead")`. When the dice *replace* the others for
  some targets, make a second effect instead ("Toll the Dead (hurt target)"
  with d12s).
- **`instances`.** `CombatInstances(count, upcast=0, cantrip=..., noun="")`
  when one casting rolls and deals its damage several times, at one target or
  several: Scorching Ray `CombatInstances(3, upcast=1, noun="ray")`, Magic
  Missile's darts, Eldritch Blast `CombatInstances(1, cantrip=((5, 2), (11,
  3), (17, 4)), noun="beam")`. The damage is one instance's. The dialog fills its
  Times box with the count. Extra *targets* per slot level are not
  instances: they go in `notes`.
- **`healing`.** `CombatHitPoints(dice, upcast=..., add_modifier=...)` for Hit
  Points each target regains now (Cure Wounds, Healing Word); the picker
  fills the form's amount box with it, set to Healing. `upcast` is dice
  or a number, as text (Heal's `upcast="10"`). Hit Points regained later, or "equal to half the
  damage dealt" (Vampiric Touch), go in `notes`.
- **`temp_hp`.** The same for Temporary Hit Points (False Life, Armor of
  Agathys), with the Temp HP box. An effect has at most one of `damage`,
  `healing` and `temp_hp` (the form has one amount box): a spell that deals
  damage puts its Hit Points in `notes`. When the caster gets them ("You gain
  ..."), say so in `notes`: the dialog gives them to its targets.
- **`conditions`.** A tuple of `CombatCondition(...)`, each a rules condition
  (`CombatCondition(Condition.PRONE)`) the effect gives, **or the spell's own
  name as a badge** on its targets (`CombatCondition("Bless")`; also Faerie
  Fire, Shield, Hunter's Mark). Use a badge when the spell lasts and marks its
  targets with something the form can't show (a bonus, a rider), and not for
  an area (Spike Growth), for healing or damage that's over when cast, or for
  a spell that's instantaneous. Nothing is put on a target unless the effect
  says so. Use `until` only when it lasts until the start or end of a turn
  (`until=(TurnEdge.END, TurnOf.TARGET)` = the end of the target's next turn;
  `TurnOf.SOURCE` = the caster's); otherwise it lasts the spell's duration.
  List every condition it gives (Tasha's: Incapacitated and Prone): the
  dialog applies them all, for the same time, and one repeat save ends them
  all. A spell whose option only lasts the target's next turn (Command: Halt)
  marks it with its own name until `(TurnEdge.END, TurnOf.TARGET)`.
- **A badge's `modifiers`** (`Model.Content.CombatModifiers`): what it does
  while it's on, which the simulator counts: `D20Bonus` (Bless),
  `ArmorClass` (Shield of Faith), `ExtraDamageFrom` (Hunter's Mark, on the
  target), `ExtraDamageOnHit` (Divine Favor, on the caster),
  `ConditionImmunity` (Heroism's Frightened), `Speed(bonus, multiplier,
  set_to)` (Longstrider `bonus=10`, Haste `multiplier=2`, a Speed of 0
  `set_to=0`; every special speed changes with it) and `Size(steps,
  becomes)` (Enlarge `steps=1`, Large Form `becomes=CreatureSize.LARGE`;
  the trigger size gates read the size in use). Never on a rules condition.
  A spell's badge keeps the spell's name even when its rows differ
  (Enlarge/Reduce's two rows both give "Enlarge/Reduce").
- **Triggers** are modifiers too: `AtTurnStart(effect, whose, when)` and
  `AtTurnEnd(...)` for what the badge does as a turn starts or ends. `effect`
  names a second effect of the same spell with `spends_use=False`, which is
  what happens: Heroism's `AtTurnStart("Heroism: Temporary Hit Points")`
  with that row's `temp_hp=CombatHitPoints(add_modifier=True)` (no dice: the
  modifier alone). `whose=WhoseTurn.ENEMY` is each turn of a creature not on
  the caster's side (Spirit Guardians' `AtTurnEnd("Spirit Guardians:
  damage", WhoseTurn.ENEMY, when="it ends its turn in the Emanation")`).
  The simulator gives Hit Points itself; a row that rolls or deals damage,
  or a trigger with a `when` (where creatures are), is a prompt the GM
  answers. Damage on later turns that isn't tied to a turn (moving through
  Spike Growth) stays a note.
- **`[]`.** Use it only when the spell has nothing the form could put on a
  creature in a fight (Alarm, Message, Minor Illusion, Thaumaturgy, Disguise
  Self, Speak with Animals, Fog Cloud). The spell is hidden from "All spells"
  but stays in its caster's own list, so casting it still spends the slot.
- **`notes`.** A tuple of short, complete sentences, taken from the text,
  about what the form can't hold: riders, who is affected, extra targets per
  slot level, how the spell ends early. Don't restate what the form already
  shows (the damage, the ability, the condition). When you write the same
  kind of note for a third spell, report it: it is a field the model is
  missing (`Notes/combat-effects-plan.md`, principle 7).
- **`spends_use=False`** only on a later step of one casting (Ice Knife's
  explosion): that row spends no slot, no action and counts no cast.
- **`trigger`** (`Model/Content/CombatTriggers.py`, plan Phase 6): when a
  row is used, in place of a "Right after you hit ..." note (a row says
  what, a trigger says when). `CombatTrigger(TriggerEvent.HIT,
  needs_damage=True, largest_target=CreatureSize.LARGE)` is Hill's Tumble's
  "When you hit a Large or smaller creature with an attack roll and deal
  damage to it, you can ...". `optional=True` (the default) is "you can":
  the GM is asked as the hit lands; `optional=False` is "it happens" (a
  monster's rider), applied without asking when every gate is checked and
  nothing is spent. Gates: `attacks` (an `AttackKind`), `largest_target`,
  `needs_damage`, `critical_only`, `once_per_turn`, `reaction`; what only
  the GM can judge is a `when` (it always asks). `after="Tree Club"` makes it
  come only after that other row of the same source (`check` refuses one
  naming no row). Only `HIT` and `MISS` fire so far; the other events are
  data until their step (6.5-6.7).
- **Not for spells:** `dc`, `attack_bonus` (the caster's), `action_type` and
  `concentration` (the spell's casting time and duration say them), and
  `spell` (for a feature's use that casts one).
