# Stat block template

Every monster class, canonical or homebrew, has the same shape as the classes `generate_monsters.py` emits, so homebrew monsters are indistinguishable in style from canonical ones.

Match this shape exactly — it's the same field order `generate_monsters.py` emits for every monster in `monsters.py`, so a homebrew monster is indistinguishable in style from a canonical one:

```python
from Core.Definitions import Ability, Condition, CreatureSize, DamageType
from Model.Creatures.Combatants import (
    Alignment,
    DamageTypeEntry,
    ExtendedCombatantData,
    MonsterType,
)
from Model.Creatures.MonsterAbilities import MonsterAbility


class MonsterClassName(ExtendedCombatantData):
    def __init__(self):
        super().__init__(
            combatant_type="Monster Display Name",
            hp=90,
            ac=16,
            temp_hp=0,
            conditions=[],
            ability_scores={
                Ability.STRENGTH: 10,
                Ability.DEXTERITY: 10,
                Ability.CONSTITUTION: 10,
                Ability.INTELLIGENCE: 10,
                Ability.WISDOM: 10,
                Ability.CHARISMA: 10,
            },
            saving_throws={},
            spell_slots={},
            cr="7",
            monster_type=MonsterType.UNDEAD,
            monster_type_note="",
            alignment=Alignment.NEUTRAL_EVIL,
            size=CreatureSize.MEDIUM,
            ac_note="natural armor",
            hp_formula="20d4+40",
            speed_ground_ft=30,
            speed_fly_ft=None,
            speed_climb_ft=None,
            speed_special_rules="",
            skills={},
            damage_vulnerabilities=[],
            damage_resistances=[
                DamageTypeEntry(damage_types=[DamageType.NECROTIC], note=""),
            ],
            damage_immunities=[
                DamageTypeEntry(damage_types=[DamageType.POISON], note=""),
            ],
            condition_immunities=[
                Condition.CHARMED,
                Condition.FRIGHTENED,
            ],
            senses="darkvision 60 ft., Passive Perception 11",
            languages="understands Common but can't speak",
            traits=[
                MonsterAbility(
                    name="Trait Name",
                    description="Full 5e-style rules text.",
                ),
            ],
            actions=[
                MonsterAbility(
                    name="Attack Name",
                    description="Melee Attack Roll: +7, reach 5 ft. Hit: 9 (2d6 + 2) Piercing damage.",
                ),
            ],
            bonus_actions=[],
            reactions=[],
            legendary_actions=[],
            legendary_resistances=0,
            lair_actions=[],
            mythic_actions=[],
        )
```

Rules for this shape:
- **Field order is fixed** — `combatant_type, [description], hp, ac, temp_hp, conditions, ability_scores, saving_throws, spell_slots, cr, monster_type, monster_type_note, alignment, size, ac_note, hp_formula, speed_ground_ft, speed_fly_ft, speed_climb_ft, speed_special_rules, skills, damage_vulnerabilities, damage_resistances, damage_immunities, condition_immunities, senses, languages, traits, actions, bonus_actions, reactions, legendary_actions, legendary_resistances, lair_actions, mythic_actions`. Don't reorder even when a field is empty.
- **Class name**: strip non-alphanumeric characters from the monster's display name, title-case each word, join with no spaces (`"The Crown Without a King"` → `TheCrownWithoutAKing`). `combatant_type=` keeps the real display name with spaces/punctuation.
- **Every enum-backed field uses the enum, never a raw string**: `Ability.<X>` (bare enum, not `.short_name`) for ability/saving-throw keys — `ExtendedCombatantData` normalizes `Ability` keys to their short name internally, `Skill.<X>` for skills dict keys (only import `Skill` if you actually use it), `Alignment.<X>`, `CreatureSize.<X>`, `DamageType.<X>` inside `DamageTypeEntry`, `Condition.<X>` in condition lists, and `MonsterType.<X>` for `monster_type` (e.g. `MonsterType.UNDEAD`, `MonsterType.DRAGON` — the 14 standard 5e creature types). Any subtype/swarm qualifier that isn't part of the base type goes in `monster_type_note` as free text (e.g. `monster_type=MonsterType.DRAGON, monster_type_note="Metallic"` for "Dragon (Metallic)"; `monster_type=MonsterType.BEAST, monster_type_note="Swarm of Tiny"` for "Swarm of Tiny Beasts"). If a monster's type genuinely doesn't map to one of the 14 (a rare multi-type entry like "Celestial or Fey or Fiend"), use `monster_type=None` and put the full text in `monster_type_note`.
- **Only import what you use.** If a monster has no skills, don't import `Skill`. If it has no damage vulnerabilities, you still need `DamageTypeEntry`/`DamageType` only if resistances or immunities use them.
- **Speed fields**: unused directions are `None`, not `0` — a monster with no fly speed is `speed_fly_ft=None`, not `speed_fly_ft=0`. `speed_ground_ft` is usually a real number (walking speed), rarely `None`.
- **Empty list fields** (`conditions`, `saving_throws={}`, `damage_vulnerabilities`, etc.) that don't apply: use `[]` or `{}`, not `None` — `ExtendedCombatantData.__attrs_post_init__` normalizes `None` to empty anyway, but every existing file writes the empty literal explicitly, so match that.
- **Ability entries**: one per trait/action/etc. Where a structured subclass fits the ability exactly (an attack, a saving-throw effect, Multiattack, Magic Resistance, ...; see `monster-abilities.md`), use it and import it from `Model.Creatures.MonsterAbilities`. Its stat-block text is then generated, and the combat UI and balance tools can read its numbers. Otherwise use a plain `MonsterAbility` with `name=` and `description=` as full sentences in 5e stat-block prose (`"Melee Attack Roll: +X, reach 5 ft. Hit: N (XdY + Z) <DamageType> damage."`, `"... must succeed on a DC N <Ability> saving throw or ..."`). Multiattack goes first in `actions` when present. Recharge/limited-use abilities get `(Recharge 5-6)` or `(1/Day)` etc. appended to the `name`, matching existing convention.
- **New traits/actions/bonus actions/reactions/legendary actions the user asks you to invent**: design them to fit the monster's concept and target CR — this is expected and encouraged, not just copying an inspiration monster's abilities verbatim. Keep damage/DC numbers roughly in line with your calibration (sibling monsters, or `cr-guidelines.md`).
- **No file-level header comment** — `monsters_homebrew.py` files are hand-written, so skip the `# Auto-generated...` line that real `monsters.py`/`__init__.py` files have. Just start with the imports.

## Field defaults and gotchas

- `saving_throws={}` is fine even for monsters with no noteworthy saves — only add entries for saves actually called out in the stat block (e.g. `{Ability.WISDOM: 0}` for the Zombie's mediocre Wisdom save).
- `legendary_resistances` is a plain `int` count (e.g. `1`, `3`), separate from also listing a "Legendary Resistance (N/Day)" `MonsterAbility` in `traits` — real files do both (the int drives any mechanical tracking, the trait entry is the display text).
- `ac_note` is free text like `"natural armor"` or `""` — not an enum.
- `hp_formula` is the dice string (`"20d4+40"`), independent of the `hp=` int (which is the average/rolled total actually used in combat).
- `description=` is optional freeform flavor text/notes about the monster: lore, campaign context, DM notes, whatever doesn't belong in `traits`/`actions`. Leave it out unless the user gives you flavor text to record; don't invent lore unprompted. When you do use it, put it **right after `combatant_type`**, where every existing homebrew monster puts it (generated monsters never have it). `check_monster.py` checks the order.
