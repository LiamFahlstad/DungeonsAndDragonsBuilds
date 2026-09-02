"""Encounter difficulty calculator for the OFFICIAL D&D 2024 ("5.5e") rules.

This is deliberately NOT the 2014/5e Dungeon Master's Guide system. Key
things that changed between 2014 and 2024, implemented here:

1. XP thresholds. The 2014 DMG had four difficulty tiers per character
   level -- Easy/Medium/Hard/Deadly. The 2024 rules (SRD 5.2.1, "XP Budget
   per Character") replaced these with THREE tiers -- Low/Moderate/High.
   There is no "Deadly" tier in the current rules: an encounter at or
   above a party's High threshold is simply classified "High" difficulty.
   Thresholds are class-agnostic (based purely on character level), and a
   party's threshold is the sum of each member's own per-level threshold,
   so mixed-level parties are handled naturally.

2. The multiple-monster adjustment was REMOVED entirely in 2024. The 2014
   DMG multiplied total monster XP by a table value (x1.5/x2/x2.5/x3/x4)
   that scaled with monster count (and, in 2014, party size too). The
   2024 SRD 5.2.1 encounter-building rules drop this step completely --
   you simply sum each monster's XP against the party's budget with no
   multiplier of any kind. This module therefore always has
   `adjusted_xp == base_xp`; see the "Adjusted XP" section below for why
   the field still exists as its own name rather than being collapsed
   into `base_xp`.

3. CR -> XP table. The 2024 rules' CR-to-XP table gives CR 0 a flat 10 XP
   (2014 split CR 0 into "0 or 10" depending on whether the monster has
   any actions). CR 1/8 through CR 30 are unchanged from 2014.

Sources consulted: D&D SRD 5.2.1 (via Roll20 Compendium, cross-checked
against other sources), "Building Combat Encounters" section (XP Budget
per Character table, CR-to-XP table). CR_TO_XP and XP_THRESHOLDS_BY_LEVEL
below are the two tables to revisit if these rules are ever re-verified
against a fresh printing/errata; everything else is plumbing.

Usage:

    from Combat.EncounterDifficulty import evaluate_encounter

    result = evaluate_encounter(
        character_levels=[5, 5, 6, 6],
        monster_crs=["6", "3", "3"],
    )
    print(result.difficulty, result.adjusted_xp, result.xp_awarded)
"""

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# CR -> XP (2024 DMG). Keys match the `cr` string format already used by
# `ExtendedCombatantData.cr` in Combat/Definitions.py (e.g. cr="1/2", cr="7").
# ---------------------------------------------------------------------------
CR_TO_XP: dict[str, int] = {
    "0": 10,
    "1/8": 25,
    "1/4": 50,
    "1/2": 100,
    "1": 200,
    "2": 450,
    "3": 700,
    "4": 1100,
    "5": 1800,
    "6": 2300,
    "7": 2900,
    "8": 3900,
    "9": 5000,
    "10": 5900,
    "11": 7200,
    "12": 8400,
    "13": 10000,
    "14": 11500,
    "15": 13000,
    "16": 15000,
    "17": 18000,
    "18": 20000,
    "19": 22000,
    "20": 25000,
    "21": 33000,
    "22": 41000,
    "23": 50000,
    "24": 62000,
    "25": 75000,
    "26": 90000,
    "27": 105000,
    "28": 120000,
    "29": 135000,
    "30": 155000,
}


def cr_to_xp(cr: str) -> int:
    """Look up a monster's XP value from its CR string, e.g. "1/2", "7",
    "30". Raises ValueError for an unrecognized CR."""
    key = str(cr).strip()
    if key not in CR_TO_XP:
        raise ValueError(f"Unrecognized challenge rating: {cr!r}")
    return CR_TO_XP[key]


# ---------------------------------------------------------------------------
# Party XP thresholds by character level (SRD 5.2.1 "XP Budget per
# Character" table). Three tiers -- Low, Moderate, High -- per level 1-20.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LevelThreshold:
    low: int
    moderate: int
    high: int


XP_THRESHOLDS_BY_LEVEL: dict[int, LevelThreshold] = {
    1: LevelThreshold(50, 75, 100),
    2: LevelThreshold(100, 150, 200),
    3: LevelThreshold(150, 225, 400),
    4: LevelThreshold(250, 375, 500),
    5: LevelThreshold(500, 750, 1100),
    6: LevelThreshold(600, 1000, 1400),
    7: LevelThreshold(750, 1300, 1700),
    8: LevelThreshold(1000, 1700, 2100),
    9: LevelThreshold(1300, 2000, 2600),
    10: LevelThreshold(1600, 2300, 3100),
    11: LevelThreshold(1900, 2900, 4100),
    12: LevelThreshold(2200, 3700, 4700),
    13: LevelThreshold(2600, 4200, 5400),
    14: LevelThreshold(2900, 4900, 6200),
    15: LevelThreshold(3300, 5400, 7800),
    16: LevelThreshold(3800, 6100, 9800),
    17: LevelThreshold(4500, 7200, 11700),
    18: LevelThreshold(5000, 8700, 14200),
    19: LevelThreshold(5500, 10700, 17200),
    20: LevelThreshold(6400, 13200, 22000),
}


@dataclass(frozen=True)
class PartyThresholds:
    """Party-wide XP thresholds -- the sum of every character's own
    per-level threshold. An encounter is considered to have reached a tier
    once its Adjusted XP is >= that tier's number (standard 5e convention:
    thresholds are inclusive floors, not exclusive ceilings)."""

    low: int
    moderate: int
    high: int


def party_thresholds(character_levels: list[int]) -> PartyThresholds:
    """Sum each character's per-level threshold (2024 DMG). Works for any
    party size (including a single character) and any mix of levels --
    it's purely a per-character sum, so mixed-level parties fall out
    naturally with no special-casing."""
    if not character_levels:
        raise ValueError("character_levels must contain at least one character")
    low = moderate = high = 0
    for level in character_levels:
        if level not in XP_THRESHOLDS_BY_LEVEL:
            raise ValueError(f"Unsupported character level: {level!r} (must be 1-20)")
        threshold = XP_THRESHOLDS_BY_LEVEL[level]
        low += threshold.low
        moderate += threshold.moderate
        high += threshold.high
    return PartyThresholds(low=low, moderate=moderate, high=high)


DIFFICULTY_TRIVIAL = "Trivial"
DIFFICULTY_LOW = "Low"
DIFFICULTY_MODERATE = "Moderate"
DIFFICULTY_HIGH = "High"


def classify_difficulty(adjusted_xp: float, thresholds: PartyThresholds) -> str:
    """Standard 5e ">=" convention: an encounter is classified by the
    highest tier its Adjusted XP has reached or passed. Below the party's
    Low threshold, the encounter is "Trivial" (not a 2024 DMG term, but a
    useful bottom bucket -- the DMG only names Low/Moderate/High)."""
    if adjusted_xp >= thresholds.high:
        return DIFFICULTY_HIGH
    if adjusted_xp >= thresholds.moderate:
        return DIFFICULTY_MODERATE
    if adjusted_xp >= thresholds.low:
        return DIFFICULTY_LOW
    return DIFFICULTY_TRIVIAL


@dataclass(frozen=True)
class EncounterDifficultyResult:
    """Everything a caller needs to both use and explain a difficulty
    verdict. `xp_awarded` (raw monster XP sum, what the party actually earns
    for winning) and `adjusted_xp` (the value compared against the party's
    thresholds to classify difficulty) are kept as two explicitly separate
    fields, as requested by the API contract -- even though, per the
    verified 2024 SRD 5.2.1 rules, there is no multi-monster adjustment
    step, so `adjusted_xp` always equals `base_xp` today. Keeping them
    distinct (rather than collapsing to one field) means a future rules
    change that reintroduces some adjustment wouldn't require an API
    change here."""

    base_xp: int
    xp_awarded: int
    adjusted_xp: float
    monster_count: int
    thresholds: PartyThresholds
    difficulty: str

    def as_dict(self) -> dict:
        return {
            "base_xp": self.base_xp,
            "xp_awarded": self.xp_awarded,
            "adjusted_xp": self.adjusted_xp,
            "monster_count": self.monster_count,
            "thresholds": {
                "low": self.thresholds.low,
                "moderate": self.thresholds.moderate,
                "high": self.thresholds.high,
            },
            "difficulty": self.difficulty,
        }


def evaluate_encounter(
    character_levels: list[int], monster_crs: list[str]
) -> EncounterDifficultyResult:
    """Full 2024-rules pipeline: CR->XP sum (Base XP, also XP awarded) ->
    classify against the party's summed thresholds. `monster_crs` takes one
    CR string per monster in the encounter (duplicate the CR string per
    monster for multiples, e.g. ["3", "3"] for two CR 3 monsters).

    Per the verified 2024 SRD 5.2.1 rules, there is NO multiple-monster XP
    multiplier step (that 2014 DMG mechanic was removed entirely) -- Base
    XP is compared directly against the party's thresholds, so
    `adjusted_xp` always equals `base_xp`."""
    if not monster_crs:
        raise ValueError("monster_crs must contain at least one monster")
    base_xp = sum(cr_to_xp(cr) for cr in monster_crs)
    monster_count = len(monster_crs)
    adjusted_xp = float(base_xp)  # no 2024-rules adjustment step -- see docstring
    thresholds = party_thresholds(character_levels)
    difficulty = classify_difficulty(adjusted_xp, thresholds)
    return EncounterDifficultyResult(
        base_xp=base_xp,
        xp_awarded=base_xp,
        adjusted_xp=adjusted_xp,
        monster_count=monster_count,
        thresholds=thresholds,
        difficulty=difficulty,
    )


def evaluate_encounter_combatants(
    character_levels: list[int], monsters: list
) -> EncounterDifficultyResult:
    """Convenience wrapper for callers already holding combatant objects
    (e.g. `ExtendedCombatantData` instances from Combat/Monsters/CR_*/) --
    pulls each monster's `.cr` attribute rather than requiring the caller
    to extract CR strings by hand."""
    crs = []
    for monster in monsters:
        cr = getattr(monster, "cr", None)
        if not cr:
            raise ValueError(f"Combatant {monster!r} has no usable `cr` attribute")
        crs.append(cr)
    return evaluate_encounter(character_levels, crs)


if __name__ == "__main__":
    # Example from the task spec: 4 characters (levels 5, 5, 6, 6) vs.
    # 1x CR 6 + 2x CR 3.
    levels = [5, 5, 6, 6]
    crs = ["6", "3", "3"]
    result = evaluate_encounter(levels, crs)

    print(f"Party levels: {levels}")
    print("Encounter: 1x CR 6, 2x CR 3")
    print(f"Base XP: {result.base_xp}")
    print(f"Monster count: {result.monster_count} (no 2024-rules multiplier)")
    print(f"Adjusted XP: {result.adjusted_xp}")
    print(
        "Party thresholds -- "
        f"Low: {result.thresholds.low}, "
        f"Moderate: {result.thresholds.moderate}, "
        f"High: {result.thresholds.high}"
    )
    print(f"Difficulty: {result.difficulty}")
    print(f"XP awarded: {result.xp_awarded}")

    # --- Edge case sanity checks ---

    # Single-monster encounter: adjusted_xp must equal base_xp (always true
    # under the 2024 rules, but especially clear-cut with only 1 monster).
    solo = evaluate_encounter([3], ["1"])
    assert solo.adjusted_xp == solo.base_xp
    print(
        "\n[OK] Single monster / single character: adjusted_xp == base_xp ->",
        solo.as_dict(),
    )

    # Fractional CRs.
    fractional = evaluate_encounter([1, 1, 1, 1], ["1/8", "1/4", "1/2"])
    print("[OK] Fractional CRs handled ->", fractional.as_dict())

    # Many-monster encounter: still no multiplier under the 2024 rules --
    # adjusted_xp must equal base_xp even with a large monster count.
    swarm = evaluate_encounter([10, 10, 10, 10], ["1/4"] * 20)
    assert swarm.adjusted_xp == swarm.base_xp
    print(
        "[OK] 20-monster swarm -> still no multiplier, adjusted_xp == base_xp ->",
        swarm.as_dict(),
    )

    # Threshold boundary: Adjusted XP exactly equal to a threshold counts
    # as having reached that tier (">=" convention).
    boundary_thresholds = party_thresholds([1])
    at_low = classify_difficulty(boundary_thresholds.low, boundary_thresholds)
    assert at_low == DIFFICULTY_LOW
    print(
        f"[OK] Adjusted XP == Low threshold ({boundary_thresholds.low}) classifies as Low"
    )
