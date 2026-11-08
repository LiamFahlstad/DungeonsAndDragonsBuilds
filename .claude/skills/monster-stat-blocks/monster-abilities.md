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

## What the combat UI's Custom Effect picker makes of an ability (`combat_effects`)

The combat UI's Custom Effect dialog lists every action, bonus action, reaction and legendary action, and fills in its form from the ability's text:
- **Attacks and saves:** the standard stat-block sentences, which every subclass above writes.
- **Hit Points:** "regains 9 (2d4 + 4) Hit Points" and "gains 10 Temporary Hit Points".
- **Spells it casts:** "casts Fear", "uses Spellcasting to cast Mind Spike (level 3 version)", at the stat block's spell save DC.
- **Another action it makes or uses:** "makes one Rend attack", "uses Dreadful Glare".

When the text says something else, write what it does on the ability itself, with the same model features use (`Model/Content/CombatEffect.py`):

```python
MonsterAbility(
    name="Compelled Duel (1/Day)",
    description="The paladin challenges one creature ... must succeed on a DC 11 Wisdom saving throw or ...",
    combat_effects=(
        CombatEffect(
            roll="save", save_ability=Ability.WISDOM, dc=11,
            conditions=(CombatCondition("Compelled Duel", duration_seconds=60),),
            concentration=True,
            notes=("It has Disadvantage on attack rolls against creatures other than the paladin ...",),
        ),
    ),
)
```

- **Write it** (in a hand-maintained file only) for the following: old-style prose ("must succeed on a DC 11 Wisdom saving throw or"); healing from a pool (`healing=CombatHitPoints()`, with no dice, lets the GM type the amount); a badge that isn't a rules condition; a condition the text gives only sometimes ("if it had Advantage", which the reader would apply on every hit); and an ability with several uses (a cleric's Life Domain Magic gets one `CombatEffect` per use, each with a `name=`). Examples are the Time Loop PR monsters: `HumanPaladinOfDevotion`, `DwarfLifeCleric`, `MirelleTheGildedKnight` and `MiraPrincessOfTheLoop`.
- **A trait is listed only once it has `combat_effects`** (a Divine Smite that's used, not a Pack Tactics that just is).
- **Don't write it** for an ability whose text the picker already reads right. Its numbers would then be in two places that can drift apart. Never write it in a generated `monsters.py`.
- **Costs stay in the name.** A recharge, uses per day and a legendary action's cost are still read from the name, and that's what the dialog spends. The stat-block section is the action.
- **It doesn't change the balance score.** `monster_score.py` doesn't read `combat_effects`, but check the score anyway if you also changed the text.
- **Check it** by running `./run_tests.sh -q tests/test_monster_combat_effects.py`.

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
