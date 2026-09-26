"""
Class spell lists (CharacterContent/Spells/SpellLists.py), Eldritch Invocations
(CharacterContent/Invocations/), and equipment Packs (CharacterContent/Items/Packs.py).

Expected values come from:
  - The PHB spell-level/class-list rules, transcribed by hand for the spot
    checks (comments cite the spell).
  - The raw spell-compendium JSON files (spells_dnd2024.json, spells_aidedd.json,
    spells_dnd5e.json) read directly with `json.load` in this file -- NOT via
    the engine's SpellFactory -- as an independent source of each spell's
    canonical level/class list, to cross-check CharacterContent/Spells/SpellLists.py.
  - The raw invocations.json file, read directly, cross-checked against
    CharacterContent/Invocations/Definitions.py tiers.
  - The 2024 PHB Warlock "Invocations Known" table, transcribed by hand.
  - The 2024 PHB equipment pack contents, transcribed by hand, for
    CharacterContent/Items/Packs.py (the base classes that hand out the packs
    follow the 2024 PHB).

This codebase's base classes follow the 2024 PHB (see CLAUDE.md guidance), and
CharacterContent/Spells/SpellLists.py is a single, edition-unified set of
class spell lists (there is no separate 2014/2024 split for spell lists in
this codebase).
"""

import inspect
import json
from enum import Enum

import attr
import pytest

import CharacterContent.Classes.BaseClasses.WarlockBase as WarlockBase
import CharacterContent.Invocations.Definitions as InvocationDefs
import CharacterContent.Spells.SpellLists as SpellLists
from CharacterContent.Items import Packs


def bug(reason):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


SPELLS_DIR = "CharacterContent/Spells"
INVOCATIONS_JSON = "CharacterContent/Invocations/invocations.json"


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _all_spell_list_enums():
    """All Enum classes defined in SpellLists.py, keyed by class name."""
    return {
        name: obj
        for name, obj in inspect.getmembers(SpellLists)
        if inspect.isclass(obj) and issubclass(obj, Enum) and obj is not Enum
    }


def _raw_spell_names():
    """Every spell name present in any of the three raw spell JSON files.

    Read directly here (not via SpellFactory) so this is an independent
    check of what spells actually exist as data, rather than re-using the
    engine's own merge/lookup code.
    """
    names = set()
    for fname in (
        "spells_dnd2024.json",
        "spells_aidedd.json",
        "spells_dnd5e.json",
    ):
        names |= set(_load_json(f"{SPELLS_DIR}/{fname}").keys())
    return names


def _raw_spell_data():
    """Merge the three raw spell JSON files, lowest priority first, mirroring
    SpellFactory's own priority order (dnd2024 > aidedd > dnd5e) but reading
    the files directly rather than calling SpellFactory."""
    merged = {}
    for fname in ("spells_dnd5e.json", "spells_aidedd.json", "spells_dnd2024.json"):
        merged.update(_load_json(f"{SPELLS_DIR}/{fname}"))
    return merged


# ---------------------------------------------------------------------------
# Data-integrity checks over every class/level spell list.
# ---------------------------------------------------------------------------


class TestSpellListDataIntegrity:
    def test_no_aliased_duplicate_values_within_a_list(self):
        """Two different enum members must never share the same spell name
        within one level list (that would silently alias one member to the
        other and hide a spell)."""
        offenders = []
        for name, enum_cls in _all_spell_list_enums().items():
            values = [m.value for m in enum_cls]
            if len(values) != len(set(values)):
                offenders.append(name)
        assert offenders == []

    def test_every_listed_spell_exists_in_spell_json_sources(self):
        """Every spell referenced anywhere in SpellLists.py must be a real
        spell in one of the raw compendium JSON files (catches typos and
        renamed/removed spells)."""
        valid_names = _raw_spell_names()
        missing = []
        for name, enum_cls in _all_spell_list_enums().items():
            for m in enum_cls:
                if m.value not in valid_names:
                    missing.append(f"{name}.{m.name} = {m.value!r}")
        assert missing == []

    def test_spell_not_listed_at_two_different_levels_for_same_class(self):
        """A given class's spell list should not list the same spell under
        two different level numbers (e.g. Fireball as both a level-3 and a
        level-4 Wizard spell)."""
        import re

        pattern = re.compile(r"^([A-Za-z]+)Level(\d)Spells$")
        by_class = {}
        for name, enum_cls in _all_spell_list_enums().items():
            m = pattern.match(name)
            if not m:
                continue
            cls_name, level = m.group(1), int(m.group(2))
            by_class.setdefault(cls_name, {})[level] = {e.value for e in enum_cls}

        offenders = []
        for cls_name, levels in by_class.items():
            seen_at = {}
            for level, values in levels.items():
                for v in values:
                    seen_at.setdefault(v, []).append(level)
            for spell, lvls in seen_at.items():
                if len(lvls) > 1:
                    offenders.append((cls_name, spell, sorted(lvls)))
        assert offenders == []

    def test_declared_level_matches_spell_json_level(self):
        """For every classLevelNSpells enum, each spell's own 'level' field
        in the raw spell JSON (independent of SpellLists.py) must equal N."""
        import re

        pattern = re.compile(r"^([A-Za-z]+)Level(\d)Spells$")
        data = _raw_spell_data()
        mismatches = []
        for name, enum_cls in _all_spell_list_enums().items():
            m = pattern.match(name)
            if not m:
                continue
            level = int(m.group(2))
            for e in enum_cls:
                record = data.get(e.value)
                if record is None:
                    continue
                if record.get("level") != level:
                    mismatches.append((name, e.value, record.get("level"), level))
        assert mismatches == []

    def test_class_spell_list_membership_matches_spell_json_classes(self):
        """For every class's per-level list (excluding the school-based lists
        like AbjurationLevelNSpells, which aren't tied to one class), the
        class name must appear in the spell's own 'classes' field in the raw
        spell JSON."""
        import re

        pattern = re.compile(r"^([A-Za-z]+)Level(\d)Spells$")
        schools = {
            "Abjuration",
            "Conjuration",
            "Divination",
            "Enchantment",
            "Evocation",
            "Illusion",
            "Necromancy",
            "Transmutation",
        }
        data = _raw_spell_data()
        mismatches = []
        for name, enum_cls in _all_spell_list_enums().items():
            m = pattern.match(name)
            if not m:
                continue
            cls_name = m.group(1)
            if cls_name in schools:
                continue
            for e in enum_cls:
                record = data.get(e.value)
                if record is None or record.get("classes") is None:
                    continue
                if cls_name not in record["classes"]:
                    mismatches.append((name, e.value, record["classes"]))
        assert mismatches == []


# ---------------------------------------------------------------------------
# Hand-picked spot checks (independent of any JSON file -- straight from PHB
# knowledge of well-known, edition-stable spells).
# ---------------------------------------------------------------------------

# (class prefix, correct level, spell enum member) -- levels per 2014/2024 PHB
# (these particular spells did not change level between editions).
SPOT_CHECKS = [
    ("Wizard", 1, SpellLists.WizardLevel1Spells.MAGIC_MISSILE),
    ("Wizard", 3, SpellLists.WizardLevel3Spells.FIREBALL),
    ("Wizard", 9, SpellLists.WizardLevel9Spells.WISH),
    ("Sorcerer", 3, SpellLists.SorcererLevel3Spells.FIREBALL),
    ("Sorcerer", 4, SpellLists.SorcererLevel4Spells.POLYMORPH),
    ("Cleric", 1, SpellLists.ClericLevel1Spells.CURE_WOUNDS),
    ("Cleric", 1, SpellLists.ClericLevel1Spells.BLESS),
    ("Cleric", 2, SpellLists.ClericLevel2Spells.SPIRITUAL_WEAPON),
    ("Bard", 0, SpellLists.BardLevel0Spells.VICIOUS_MOCKERY),
    ("Druid", 1, SpellLists.DruidLevel1Spells.GOODBERRY),
    ("Druid", 2, SpellLists.DruidLevel2Spells.MOONBEAM),
    ("Ranger", 1, SpellLists.RangerLevel1Spells.HUNTERS_MARK),
    ("Warlock", 0, SpellLists.WarlockLevel0Spells.ELDRITCH_BLAST),
    ("Warlock", 3, SpellLists.WarlockLevel3Spells.COUNTERSPELL),
]


class TestSpellListSpotChecks:
    @pytest.mark.parametrize(
        "class_prefix,level,member", SPOT_CHECKS, ids=lambda v: str(v)
    )
    def test_spell_is_in_its_correct_level_list_and_no_other(
        self, class_prefix, level, member
    ):
        enums = _all_spell_list_enums()
        # The list it should be in:
        correct_enum_name = f"{class_prefix}Level{level}Spells"
        assert correct_enum_name in enums
        assert member.value in {e.value for e in enums[correct_enum_name]}

        # It should not also appear in a different level's list for the same class.
        for lvl in range(0, 10):
            if lvl == level:
                continue
            other_name = f"{class_prefix}Level{lvl}Spells"
            other_enum = enums.get(other_name)
            if other_enum is None:
                continue
            assert member.value not in {
                e.value for e in other_enum
            }, f"{member.value} incorrectly also listed in {other_name}"


# ---------------------------------------------------------------------------
# Invocations: data integrity between Definitions.py tiers and invocations.json
# ---------------------------------------------------------------------------

INVOCATION_TIERS = {
    "InvocationsLevel0": 0,
    "InvocationsLevel2": 2,
    "InvocationsLevel5": 5,
    "InvocationsLevel7": 7,
    "InvocationsLevel9": 9,
    "InvocationsLevel12": 12,
    "InvocationsLevel15": 15,
}


class TestInvocationDataIntegrity:
    def test_every_invocation_tier_matches_its_json_level(self):
        data = _load_json(INVOCATIONS_JSON)
        mismatches = []
        for enum_name, expected_level in INVOCATION_TIERS.items():
            enum_cls = getattr(InvocationDefs, enum_name)
            for m in enum_cls:
                record = data.get(m.value)
                if record is None:
                    mismatches.append((enum_name, m.value, "missing from JSON"))
                elif record["level"] != expected_level:
                    mismatches.append(
                        (enum_name, m.value, record["level"], expected_level)
                    )
        assert mismatches == []

    def test_no_invocation_missing_from_definitions_enums(self):
        """Every invocation in the JSON must be reachable through one of the
        Definitions.py tier enums (otherwise it could never be selected)."""
        data = _load_json(INVOCATIONS_JSON)
        all_enum_values = set()
        for enum_name in INVOCATION_TIERS:
            enum_cls = getattr(InvocationDefs, enum_name)
            all_enum_values |= {m.value for m in enum_cls}
        assert set(data.keys()) - all_enum_values == set()

    def test_no_duplicate_invocation_across_tiers(self):
        seen = []
        for enum_name in INVOCATION_TIERS:
            enum_cls = getattr(InvocationDefs, enum_name)
            seen.extend(m.value for m in enum_cls)
        assert len(seen) == len(set(seen))

    # Pact-gated invocations: the PHB requires a specific Pact Boon before
    # these can be selected. This only checks the JSON's own prerequisite
    # text is correct/self-consistent; add_invocation() does not actually
    # enforce these prerequisites anywhere (see report).
    @pytest.mark.parametrize(
        "invocation_name,required_pact_text",
        [
            ("Thirsting Blade", "Pact of the Blade"),
            ("Eldritch Smite", "Pact of the Blade"),
            ("Lifedrinker", "Pact of the Blade"),
            ("Investment of the Chain Master", "Pact of the Chain"),
            ("Gift of the Protectors", "Pact of the Tome"),
            ("Devouring Blade", "Thirsting Blade"),
        ],
    )
    def test_pact_gated_invocation_prerequisite_text(
        self, invocation_name, required_pact_text
    ):
        data = _load_json(INVOCATIONS_JSON)
        assert required_pact_text in data[invocation_name]["prerequisite"]

    def test_warlock_level_gated_invocation_prerequisite_text(self):
        """Spot check: every tiered invocation's prerequisite text names the
        correct minimum Warlock level (except the three at-will Pact Boons
        and Armor of Shadows/Eldritch Mind, which have no prerequisite)."""
        data = _load_json(INVOCATIONS_JSON)
        for enum_name, level in INVOCATION_TIERS.items():
            if level == 0:
                continue
            enum_cls = getattr(InvocationDefs, enum_name)
            for m in enum_cls:
                prereq = data[m.value]["prerequisite"]
                assert (
                    f"Level {level}+ Warlock" in prereq
                ), f"{m.value} (tier {level}) prerequisite text is {prereq!r}"


# ---------------------------------------------------------------------------
# Warlock "Invocations Known" cumulative count, 2024 PHB.
# ---------------------------------------------------------------------------

# 2024 PHB Warlock class table, "Invocations Known" column, transcribed by hand.
PHB_2024_WARLOCK_INVOCATIONS_KNOWN = {
    1: 1,
    2: 3,
    3: 3,
    4: 3,
    5: 5,
    6: 5,
    7: 6,
    8: 6,
    9: 7,
    10: 7,
    11: 7,
    12: 8,
    13: 8,
    14: 8,
    15: 9,
    16: 9,
    17: 9,
    18: 10,
    19: 10,
    20: 10,
}


def _invocation_slots_granted_at_level(level: int) -> int:
    """Count how many invocation-typed fields WarlockLevel<level> actually
    grants, by inspecting the real attr.dataclass fields (not by
    reimplementing the PHB table)."""
    cls = getattr(WarlockBase, f"WarlockLevel{level}")
    fields = attr.fields(cls)
    return sum(1 for f in fields if f.type and "Invocation" in str(f.type))


class TestWarlockInvocationsKnown:
    @pytest.mark.parametrize("level", range(1, 21))
    def test_cumulative_invocations_known(self, level):
        granted_by_level = {
            lvl: _invocation_slots_granted_at_level(lvl) for lvl in range(1, level + 1)
        }
        cumulative = sum(granted_by_level.values())
        assert cumulative == PHB_2024_WARLOCK_INVOCATIONS_KNOWN[level]


# ---------------------------------------------------------------------------
# Equipment packs vs. the 2024 PHB pack contents (Chapter 6, Adventuring Gear).
# The base classes follow the 2024 PHB, and the 2024 packs differ substantially
# from the 2014 PHB p.151 table (e.g. 2024 Explorer's Pack has 2 Flasks of Oil).
# ---------------------------------------------------------------------------


def _pack_contents(pack: Packs.Pack) -> dict:
    """{item class name: quantity} for a pack's get_items()."""
    contents = {}
    for item, quantity in pack.get_items():
        contents[type(item).__name__] = contents.get(type(item).__name__, 0) + quantity
    return contents


PHB_2024_PACKS = {
    "DungeoneersPack": {
        "Backpack": 1,
        "Caltrops": 1,
        "Crowbar": 1,
        "FlasksOfOil": 2,
        "Rations": 10,
        "Rope": 1,
        "Tinderbox": 1,
        "Torch": 10,
        "Waterskin": 1,
    },
    "EntertainersPack": {
        "Backpack": 1,
        "Bedroll": 1,
        "Bell": 1,
        "BullseyeLantern": 1,
        "Costume": 3,
        "Mirror": 1,
        "FlasksOfOil": 8,
        "Rations": 9,
        "Tinderbox": 1,
        "Waterskin": 1,
    },
    "BurglarsPack": {
        "Backpack": 1,
        "BallBearings": 1,
        "Bell": 1,
        "Candle": 10,
        "Crowbar": 1,
        "HoodedLantern": 1,
        "FlasksOfOil": 7,
        "Rations": 5,
        "Rope": 1,
        "Tinderbox": 1,
        "Waterskin": 1,
    },
    "DiplomatsPack": {
        "Chest": 1,
        "FineClothes": 1,
        "Ink": 1,
        "InkPen": 5,
        "Lamp": 1,
        "MapOrScrollCase": 2,
        "FlasksOfOil": 4,
        "Paper": 5,
        "Parchment": 5,
        "Perfume": 1,
        "Tinderbox": 1,
    },
    "ExplorersPack": {
        "Backpack": 1,
        "Bedroll": 1,
        "FlasksOfOil": 2,
        "Rations": 10,
        "Rope": 1,
        "Tinderbox": 1,
        "Torch": 10,
        "Waterskin": 1,
    },
    "PriestsPack": {
        "Backpack": 1,
        "Blanket": 1,
        "HolyWater": 1,
        "Lamp": 1,
        "Rations": 7,
        "Robe": 1,
        "Tinderbox": 1,
    },
    "ScholarsPack": {
        "Backpack": 1,
        "Book": 1,
        "Ink": 1,
        "InkPen": 1,
        "Lamp": 1,
        "FlasksOfOil": 10,
        "Parchment": 10,
        "Tinderbox": 1,
    },
}


@pytest.mark.parametrize("pack_name", sorted(PHB_2024_PACKS))
def test_pack_matches_2024_phb(pack_name):
    pack = getattr(Packs, pack_name)()
    assert _pack_contents(pack) == PHB_2024_PACKS[pack_name]
