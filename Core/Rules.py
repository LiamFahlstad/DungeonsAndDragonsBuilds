"""The numbers the rules define, each named after its rule, and the few rules
that are plain formulas.

What belongs here: a number the engine or many features share (the level
range, the ability score cap, the spell save DC base). What doesn't: a number
that is one feature's own rule ("a Ring of Intellect gives +2", "Primal
Champion raises the maximum to 25") - that stays in the feature, where it's
read in context. Class tables (hit dice, starting gold, multiclass
prerequisites) live on CharacterClass in Core/Definitions.py.

Every value is from the 2024 Player's Handbook, except the carrying capacity
in item slots, which is this repo's house rule.
"""

from Core.Definitions import Ability

# ── Levels ───────────────────────────────────────────────────────────────────

# A character's level, and their level in any one class, runs from 1 to 20.
MIN_LEVEL = 1
MAX_LEVEL = 20
ALL_LEVELS = range(MIN_LEVEL, MAX_LEVEL + 1)


def proficiency_bonus(character_level: int) -> int:
    """+2 at levels 1-4, rising by 1 every 4 levels, to +6 at 17-20."""
    return 2 + (character_level - 1) // 4


# The bonus at level 20. Used as the box-count ceiling for features whose
# uses scale with the proficiency bonus.
MAX_PROFICIENCY_BONUS = proficiency_bonus(MAX_LEVEL)


def levels_gained(count_at_level, from_level: int = MIN_LEVEL) -> list[int]:
    """For a count that grows with level (`count_at_level(level) -> int`), the
    level each unit of it is gained at, in order - e.g. the proficiency bonus
    gives [1, 1, 5, 9, 13, 17]. Used as FeatureUses.gained_at, the number
    printed under each use box. `from_level` is the level the feature itself
    is gained at: nothing is gained before it, so a level-3 feature scaling
    with the proficiency bonus gives [3, 3, 5, 9, 13, 17]."""
    gained: list[int] = []
    for level in range(from_level, MAX_LEVEL + 1):
        while len(gained) < count_at_level(level):
            gained.append(level)
    return gained


# The level each box of a proficiency-bonus-scaled feature is gained at.
PROFICIENCY_BONUS_GAINED_AT = levels_gained(proficiency_bonus)

# Expertise doubles the proficiency bonus.
EXPERTISE_MULTIPLIER = 2

# ── Ability scores ───────────────────────────────────────────────────────────


def ability_modifier(score: int) -> int:
    """(score - 10) / 2, rounded down: 10-11 is +0, 12-13 is +1, 8-9 is -1."""
    return (score - 10) // 2


# "To a maximum of 20": the cap on ability score increases from the
# background, feats and Ability Score Improvements.
MAX_ABILITY_SCORE = 20

# No ability score can ever exceed 30.
ABSOLUTE_MAX_ABILITY_SCORE = 30

# The modifier of a score of 30. Used as the box-count ceiling for features
# whose uses scale with an ability modifier.
MAX_ABILITY_MODIFIER = ability_modifier(ABSOLUTE_MAX_ABILITY_SCORE)

STANDARD_ARRAY = (15, 14, 13, 12, 10, 8)

POINT_BUY_BUDGET = 27
POINT_BUY_MIN_SCORE = 8
POINT_BUY_MAX_SCORE = 15


def point_buy_cost(score: int) -> int:
    """Points a score costs: 8 is free, each point up to 13 costs 1, and 14
    and 15 cost 2 each (8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9)."""
    if score <= 13:
        return score - POINT_BUY_MIN_SCORE
    cost_of_13 = 13 - POINT_BUY_MIN_SCORE
    return cost_of_13 + 2 * (score - 13)


# Multiclassing needs a score of at least 13 in each prerequisite ability.
MULTICLASS_MIN_SCORE = 13

# ── Armor, spellcasting, equipment ───────────────────────────────────────────

# Without armor: AC 10 + Dexterity modifier.
UNARMORED_AC_BASE = 10

# Wearing armor without training gives Disadvantage on every D20 Test that
# involves Strength or Dexterity.
UNTRAINED_ARMOR_ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

# Spell save DC = 8 + spellcasting ability modifier + proficiency bonus.
SPELL_SAVE_DC_BASE = 8

# A creature can be attuned to at most three magic items at once.
MAX_ATTUNED_ITEMS = 3

# House rule: a person carries 3 + Strength modifier item slots, plus
# bonuses from containers and features.
CARRYING_CAPACITY_BASE_SLOTS = 3

# ── Combat ───────────────────────────────────────────────────────────────────

# A round, in which every combatant takes one turn, lasts about 6 seconds.
SECONDS_PER_ROUND = 6

# ── Psionic Energy Dice ──────────────────────────────────────────────────────

# The Psi Warrior and Soulknife Energy Dice tables are the same table, read by
# Fighter or Rogue level respectively: (from level, die size, number of dice).
_PSIONIC_ENERGY_DICE = (
    (17, "d12", 12),
    (13, "d10", 10),
    (11, "d10", 8),
    (9, "d8", 8),
    (5, "d8", 6),
    (3, "d6", 4),
)


def psionic_energy_dice(class_level: int) -> tuple[str, int]:
    """(die size, number of dice) at a Psi Warrior or Soulknife class level."""
    for from_level, die, count in _PSIONIC_ENERGY_DICE:
        if class_level >= from_level:
            return die, count
    return "d6", 0


# The level each Psionic Energy Die box is gained at: [3, 3, 3, 3, 5, 5, ...].
PSIONIC_ENERGY_DICE_GAINED_AT = levels_gained(
    lambda level: psionic_energy_dice(level)[1]
)
