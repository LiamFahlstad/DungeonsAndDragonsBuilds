# Structured MonsterAbility subclasses

`Model/Creatures/MonsterAbilities.py` holds `MonsterAbility` (free text: `name`, `description`) and structured subclasses that *generate* the standard 5e stat-block sentence from typed fields. The combat UI and the balance tools read those fields (attack bonus, DC, dice), which they can't do reliably from free text.

## Get the current list from the code, not from memory

```bash
python .claude/skills/monster-stat-blocks/abilities.py                    # every subclass
python .claude/skills/monster-stat-blocks/abilities.py MeleeAttack Pounce # just these
```

For each subclass this prints its constructor fields with defaults, whether `name` is derived, its docstring, and the exact text it generates. It reads the module itself, so it is always current. An earlier hand-copied reference here silently went stale: it missed seven subclasses and the second damage type on attacks.

## Rules the code doesn't tell you

- **Never pass `description=`** to a subclass; it is always generated in `__post_init__`.
- **Derived name** (the script marks it): don't pass `name=`. Pass `creature_name=` (the monster's lowercase self-reference, e.g. `"aboleth"`, `"young gold dragon"`) and any `name_suffix=` / `uses=` / `uses_per_day=` the name is built from.
- **Free name** (attacks, `SavingThrowEffect`, `CastSpellLegendaryAction`, `NamedAttackAction`): pass the flavour name (`"Bite"`, `"Chain Lash (Costs 1 Action)"`).
- **A proper-name monster** whose text omits "The" ("Garron makes two..."): set `use_article=False` where the class has it (`Multiattack`, `NamedAttackAction`) and pass the exact display name as `creature_name`.
- **Two damage types on one hit** ("14 (2d8 + 5) Piercing damage plus 4 (1d8) Fire damage"): `MeleeAttack` and `RangedAttack` support this through their `secondary_*` fields. `MeleeOrRangedAttack` does not; leave those as plain text.
- **Free text that names a DC** but doesn't fit `SavingThrowEffect`: use `DcMonsterAbility(name=..., description=...)`, so the combat UI can still pull the DC out for its save-chance table.

## When to use a subclass (writing or converting)

**Only on a clean match.** The subclass must reproduce the original text *exactly*, whitespace included. Leftover rider text is allowed only in a field built for it (`additional_ruling`, `extra_ruling`, `exception_note`, `name_suffix`, `attack_bonus_note`). Otherwise keep a plain `MonsterAbility`; don't force a lossy fit.

Signals, matched against `name` and `description`:

| Text | Subclass |
|---|---|
| `Melee Attack Roll: +N, reach X ft. Hit: ...` | `MeleeAttack` |
| `Ranged Attack Roll: +N, range X ft. Hit: ...` | `RangedAttack` |
| `Melee or Ranged Attack Roll: +N, reach X ft. or range Y ft. Hit: ...` | `MeleeOrRangedAttack` |
| `<Ability> Saving Throw: DC N, ... Failure: ...` | `SavingThrowEffect` (condition-only failures use `failure_effect` with no dice) |
| `The <creature> makes ...` under the name Multiattack | `Multiattack`. Other verbs ("uses Eye Rays twice") stay plain |
| `The <creature> makes one X attack.` under its own action name | `NamedAttackAction` |
| `The <creature> uses Spellcasting to cast X. ... until the start of its next turn.` | `CastSpellLegendaryAction` |
| Magic Resistance, Legendary Resistance (N/Day), Regeneration, Pack Tactics, Amphibious, Water Breathing, Sunlight Sensitivity, Rampage, Nimble Escape, Spider Climb, Illumination, Siege Monster, Pounce, Web Walker, Flyby, Primal Bond, Swarm (Tiny creatures) | the subclass of that name (Swarm is `TinySwarm`). Check that its generated text matches |

**After converting, verify** that the rendered text equals the original, in one batched check at the end:

```bash
python -c "
from Combat.Monsters.CR_<tier>.<module> import <MonsterClassName>
m = <MonsterClassName>()
for ab in m.traits + m.actions + m.bonus_actions + m.reactions + m.legendary_actions:
    print(repr(ab.name), '->', repr(ab.description))
"
```

Imports: add the subclasses to the `from Model.Creatures.MonsterAbilities import (...)` block (alphabetical). Before you remove `MonsterAbility` from it, grep the file to confirm no entry still uses the plain class.

## What the combat UI does with an ability (`combat_effects`)

The combat UI never reads an ability's text (Notes/explicit-attributes-plan.md, Phase 4.3). Its Custom Effect dialog and the turn column's buttons fill in from fields:
- **Attacks, saves, damage, conditions, Hit Points, areas:** `combat_effects`, one `CombatEffect` (`Model/Content/CombatEffect.py`, the model features and spells use) per way to use it. The first is its attack or save; then come the rows applied as it hits, one per condition its hit gives in a sentence of its own (`trigger=CombatTrigger(TriggerEvent.HIT, optional=False, after="Tree Club")`, `spends_use=False`) and one for a save its hit forces.
- **Spells it casts:** `casts=` (below), at the stat block's spell save DC.
- **Another action it makes or uses:** `uses_ability=` (below).

**Every action, bonus action, reaction and legendary action whose text has an attack, save, damage, condition or Hit Points needs `combat_effects`**, structured subclasses included: `tests/test_monster_effect_text.py` fails otherwise. Draft them from the text, then check and fix the draft by hand:

```bash
python -m Combat.Tools.monster_effect_text "Bite" "Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Piercing damage."
```

A hand-written one says what the text means where the reader can't:

```python
MonsterAbility(
    name="Compelled Duel (1/Day)",
    description="The paladin challenges one creature ... must succeed on a DC 11 Wisdom saving throw or ...",
    combat_effects=(
        CombatEffect(
            roll=EffectRoll.SAVE, save_ability=Ability.WISDOM, dc=11,
            conditions=(CombatCondition("Compelled Duel", duration_seconds=60),),
            concentration=True,
            notes=("It has Disadvantage on attack rolls against creatures other than the paladin ...",),
        ),
    ),
)
```

- **Fix the draft by hand** (in a hand-maintained file only) for: old-style prose ("must succeed on a DC 11 Wisdom saving throw or", which the reader misses); healing from a pool (`healing=CombatHitPoints()`, with no dice, lets the GM type the amount); a badge that isn't a rules condition; a condition the text gives only sometimes ("if it had Advantage": a `CombatTrigger(..., when="it had Advantage")` row, not the attack's own condition); and an ability with several uses (a cleric's Life Domain Magic gets one `CombatEffect` per use, each with a `name=`). Examples are the Time Loop PR monsters: `HumanPaladinOfDevotion`, `DwarfLifeCleric`, `MirelleTheGildedKnight` and `MiraPrincessOfTheLoop`, and the summons in `CharacterContent` (Steel Defender, Primal Companion), whose numbers follow their owner (`dice_plus("1d8", 2 + intelligence_modifier)`).
- **An attack's effect says how far it goes:** `reach_ft=10` for "reach 10 ft.", `range_ft=80, long_range_ft=320` for "range 80/320 ft.", both for "Melee or Ranged". The battle map checks reach and range, and opportunity attacks use the longest reach, from these fields only, never from the text. A `MeleeAttack` / `RangedAttack` / `MeleeOrRangedAttack`'s own `reach_ft` / `range_ft` count, so its effect can leave them off. The draft writes them; `tests/test_monster_effect_text.py::test_every_attack_says_how_far_it_goes` fails when one is missing or differs from the text.
- **A trait is listed only once it has `combat_effects`** (a Divine Smite that's used, not a Pack Tactics that just is).
- **Never write them by hand in a generated `monsters.py`**: `generate_monsters.py` writes them from the text, and the test holds each to what its text says.
- **Costs, casts and uses are fields; the name is shown.** A recharge, uses per day and a legendary action's cost stay in the name for display ("Fire Breath (Recharge 5-6)"), but the combat UI spends `recharge=5`, `per_day=2` and `legendary_cost=2` on the ability. Likewise `at_turn_start=` (a trait's sentence saying what it does at the start of the monster's turn, which the turn column reminds of), `casts=(MonsterCast("Fear"),)` (`MonsterCast(spell, level=None, per_day=None)`, the spell's name as the spell list has it), and `uses_ability="Rend"` (the other ability whose use this is, as in "makes one Rend attack"; add `moves_first=True` for "moves up to half its Speed, and"). Write only the ones the name or text gives, after `description=` / `combat_effects=`; `generate_monsters.py` emits them, and `tests/test_monster_ability_text.py` fails when the fields and the text disagree. The stat-block section is the action.
- **It doesn't change the balance score.** `monster_score.py` doesn't read `combat_effects`, but check the score anyway if you also changed the text.
- **Check it** by running `./run_tests.sh -q tests/test_monster_combat_effects.py tests/test_monster_effect_text.py`.

## Adding a new subclass

Add one only for a pattern with 3+ real occurrences that no subclass covers, or when the user asks. A one-off is simpler as plain text. (Frightful Presence was checked and rejected: its real stat blocks split across two inconsistent phrasings with fewer than 3 occurrences each. Re-check before proposing it again.)

```python
@dataclass_decorator
class NewPattern(MonsterAbility):
    """One-line description of the stat-block pattern this models."""

    creature_name: str = "creature"
    # ...whatever varies between instances...
    name: str = field(init=False, default="")          # only if the name is templated text
    description: str = field(init=False, default="")   # always init=False

    def __post_init__(self):
        self.name = "..."
        self.description = f"..."
```

- Place it at the end of `Model/Creatures/MonsterAbilities.py`, with a docstring that says when it fits. `abilities.py` shows the docstring to every future user.
- Derive `name` only when it is always the same templated text. Leave it a normal field when it varies per monster (like an attack's name).
- Reuse `_format_dice_notation` for dice maths.
- Then convert the monsters that motivated it, and verify as above.
