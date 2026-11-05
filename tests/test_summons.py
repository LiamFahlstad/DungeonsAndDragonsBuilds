"""SummonSpec (Model/Content/Summons.py) and the Feature hooks that return it:
the dataclass defaults, and the two companion features' specs (Drake
Companion, Reanimated Companion) built with each of their choices and checked
against their rules text."""

import dataclasses
from functools import cache

import pytest

from CharacterContent.Features.SubClassFeatures.Artificer.ArtificerReanimatorFeatures import (
    ReanimatedCompanion,
)
from CharacterContent.Features.SubClassFeatures2014.Ranger.RangerDrakewardenFeatures import (
    DRACONIC_ESSENCE_TYPES,
    DrakeCompanion,
)
from Core.Definitions import CharacterClass, DamageType
from Model.Content.Feature import Feature
from Model.Content.Summons import (
    OnZeroHp,
    SummonContext,
    SummonCost,
    SummonLifetime,
    SummonSpec,
    SummonTurn,
    WhenFull,
)
from tests._snapshot_helpers import build

DESSIE_BUILD = "Y2024_Artificer_Reanimator_Dessie"
HANNA_BUILD = "Y2024_Ranger_Drakewarden_Hanna"


@cache
def _sheet(build_name: str):
    return build(build_name)


def _feature(sheet, feature_type: type) -> Feature:
    (feature,) = [f for f in sheet.features if isinstance(f, feature_type)]
    return feature


def _only_spec(sheet, feature_type: type) -> SummonSpec:
    (spec,) = _feature(sheet, feature_type).summons(sheet)
    return spec


def _never_built(character, ctx):
    raise AssertionError("not built in this test")


# ---------------------------------------------------------------------------
# The dataclasses


def test_a_spec_defaults_to_one_free_creature_after_its_owner_until_a_long_rest():
    spec = SummonSpec(name="Thing", build=_never_built)
    assert spec.choices(_sheet(HANNA_BUILD)) == []
    assert spec.choice_label == ""
    assert spec.count(_sheet(HANNA_BUILD), SummonContext()) == 1
    assert spec.max_out == 1
    assert spec.when_full is WhenFull.REPLACES
    assert spec.lifetime is SummonLifetime.UNTIL_LONG_REST
    assert spec.duration_seconds is None
    assert spec.turn is SummonTurn.AFTER_OWNER
    assert spec.costs == ()
    assert spec.on_zero_hp is OnZeroHp.VANISHES
    assert spec.drops_with_owner is False


def test_a_copy_of_a_spec_cant_change_the_originals_costs():
    # What Feature.adjust_summon does: a changed copy, not an edited spec.
    original = SummonSpec(name="Original", build=_never_built, costs=(SummonCost(),))
    copy = dataclasses.replace(
        original, costs=original.costs + (SummonCost(spell_slot=1),)
    )
    assert original.costs == (SummonCost(),)
    assert copy.costs == (SummonCost(), SummonCost(spell_slot=1))
    hash(original)  # frozen with no list in it, so it's hashable


def test_context_and_cost_defaults():
    assert SummonContext() == SummonContext(choice=None, slot_level=None)
    # A cost with nothing set is the summoning feature's own use.
    assert SummonCost() == SummonCost(feature_use=None, spell_slot=None)


def test_specs_contexts_and_costs_are_frozen():
    with pytest.raises(AttributeError):
        SummonContext().choice = "Fire"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        SummonCost().spell_slot = 2  # type: ignore[misc]
    with pytest.raises(AttributeError):
        SummonSpec(name="Thing", build=_never_built).max_out = 2  # type: ignore[misc]


@pytest.mark.parametrize(
    "make",
    [
        lambda: SummonCost(spell_slot=0),
        lambda: SummonSpec(name="Thing", build=_never_built, max_out=0),
        lambda: SummonSpec(name="Thing", build=_never_built, duration_seconds=0),
        lambda: SummonSpec(
            name="Thing", build=_never_built, lifetime=SummonLifetime.DURATION
        ),
    ],
    ids=["slot level 0", "max_out 0", "no duration", "DURATION without seconds"],
)
def test_impossible_values_are_refused(make):
    with pytest.raises(ValueError):
        make()


def test_a_duration_summon_with_its_seconds_and_no_limit_is_fine():
    spec = SummonSpec(
        name="Thing",
        build=_never_built,
        lifetime=SummonLifetime.DURATION,
        duration_seconds=3600,
        max_out=None,
    )
    assert (spec.duration_seconds, spec.max_out) == (3600, None)


# ---------------------------------------------------------------------------
# The Feature hooks' defaults


def test_a_feature_summons_nothing_and_changes_no_summon_by_default():
    sheet = _sheet(HANNA_BUILD)
    feature = Feature(name="Plain", origin="Test")
    spec = _only_spec(sheet, DrakeCompanion)
    stat_block = spec.build(sheet, SummonContext())
    before = repr(stat_block)
    assert feature.summons(sheet) == []
    assert feature.adjust_summon(sheet, spec) is spec
    assert feature.modify_summon(sheet, spec, stat_block, SummonContext()) is None
    assert repr(stat_block) == before


def test_only_the_two_companion_features_summon_in_these_builds():
    for build_name, feature_type in (
        (HANNA_BUILD, DrakeCompanion),
        (DESSIE_BUILD, ReanimatedCompanion),
    ):
        sheet = _sheet(build_name)
        summoners = [f for f in sheet.features if f.summons(sheet)]
        assert [type(f) for f in summoners] == [feature_type]


# ---------------------------------------------------------------------------
# Drake Companion


def test_the_drake_spec_follows_its_rules_text():
    sheet = _sheet(HANNA_BUILD)
    spec = _only_spec(sheet, DrakeCompanion)
    assert spec.name == "Drake Companion"
    # "Whenever you summon the drake, choose a damage type listed in its
    # Draconic Essence trait."
    assert spec.choice_label == "Draconic Essence"
    assert spec.choices(sheet) == ["Acid", "Cold", "Fire", "Lightning", "Poison"]
    # "The drake remains until it is reduced to 0 hit points, until you use
    # this feature to summon the drake again, or until you die."
    assert spec.lifetime is SummonLifetime.UNTIL_DISMISSED
    assert spec.when_full is WhenFull.REPLACES
    assert spec.max_out == 1
    assert spec.on_zero_hp is OnZeroHp.VANISHES
    assert spec.drops_with_owner is True
    # "In combat, the drake shares your initiative count, but it takes its
    # turn immediately after yours."
    assert spec.turn is SummonTurn.AFTER_OWNER
    # "Once you summon the drake, you can't do so again until you finish a
    # long rest, unless you expend a spell slot of 1st level or higher."
    assert spec.costs == (SummonCost(), SummonCost(spell_slot=1))
    assert spec.count(sheet, SummonContext()) == 1
    assert spec.duration_seconds is None


@pytest.mark.parametrize("damage_type", DRACONIC_ESSENCE_TYPES, ids=lambda d: d.value)
def test_each_draconic_essence_builds_a_drake_of_that_type(damage_type: DamageType):
    sheet = _sheet(HANNA_BUILD)
    spec = _only_spec(sheet, DrakeCompanion)
    drake = spec.build(sheet, SummonContext(choice=damage_type.value))
    assert drake.combatant_type == "Drake Companion"
    assert [e.damage_types for e in drake.damage_immunities or []] == [[damage_type]]
    (infused,) = drake.reactions or []
    assert f"extra 1d6 {damage_type.value} damage" in infused.description
    ranger_level = sheet.get_class_level(CharacterClass.RANGER)
    assert drake.hp == 5 + 5 * ranger_level


def test_no_choice_builds_the_drake_with_the_builds_own_essence():
    sheet = _sheet(HANNA_BUILD)
    feature = _feature(sheet, DrakeCompanion)
    assert isinstance(feature, DrakeCompanion)
    (spec,) = feature.summons(sheet)
    own = spec.build(sheet, SummonContext())
    assert feature.damage_type is not None
    assert [e.damage_types for e in own.damage_immunities or []] == [
        [feature.damage_type]
    ]


def test_a_drake_with_no_essence_chosen_by_the_build_falls_back_to_fire():
    sheet = _sheet(HANNA_BUILD)
    (spec,) = DrakeCompanion().summons(sheet)
    drake = spec.build(sheet, SummonContext())
    assert [e.damage_types for e in drake.damage_immunities or []] == [
        [DamageType.FIRE]
    ]


# ---------------------------------------------------------------------------
# Reanimated Companion


def test_the_reanimated_companion_spec_follows_its_rules_text():
    sheet = _sheet(DESSIE_BUILD)
    spec = _only_spec(sheet, ReanimatedCompanion)
    assert spec.name == "Reanimated Companion"
    assert spec.choices(sheet) == []
    # "You can have only one companion at a time and can't create one while
    # your companion is present."
    assert spec.max_out == 1
    assert spec.when_full is WhenFull.REFUSED
    # "It lasts until you finish a Long Rest ... It immediately drops to 0
    # Hit Points and dies (triggering its Death Burst trait) if you die."
    assert spec.lifetime is SummonLifetime.UNTIL_LONG_REST
    assert spec.on_zero_hp is OnZeroHp.DIES
    assert spec.drops_with_owner is True
    # "In combat, the companion acts during your turn."
    assert spec.turn is SummonTurn.AFTER_OWNER
    # "Once you create a companion, you can't do so again until you finish a
    # Long Rest or expend a spell slot to create one."
    assert spec.costs == (SummonCost(), SummonCost(spell_slot=1))
    assert spec.count(sheet, SummonContext()) == 1


def test_the_reanimated_companion_builds_its_stat_block():
    sheet = _sheet(DESSIE_BUILD)
    spec = _only_spec(sheet, ReanimatedCompanion)
    companion = spec.build(sheet, SummonContext())
    assert companion.combatant_type == "Reanimated Companion"
    artificer_level = sheet.get_class_level(CharacterClass.ARTIFICER)
    assert companion.hp == 5 + 5 * artificer_level
    assert companion.ac == 10 + sheet.get_intelligence_modifier()
    assert [t.name for t in companion.traits or []] == [
        "Death Burst",
        "Lightning Absorption",
    ]
