"""The SummonSpecs of the features that make a creature, beyond the two
companions in tests/test_summons.py (summon framework plan, Phase 3): Steel
Defender, Wildfire Spirit, Vestige Companion, Primal Companion, Animating
Performance's Dancing Item and Manifest Echo's echo, each checked against its
rules text and built for an example build."""

from functools import cache

import pytest

from CharacterContent.Features.ClassFeatures.Ranger.PrimalCompanions import (
    CompanionType,
)
from CharacterContent.Features.SubClassFeatures.Artificer.ArtificerBattleSmithFeatures import (
    SteelDefender,
)
from CharacterContent.Features.SubClassFeatures.Ranger.RangerBeastMasterFeatures import (
    PrimalCompanion,
)
from CharacterContent.Features.SubClassFeatures.Warlock.WarlockVestigeFeatures import (
    VestigeCompanion,
)
from CharacterContent.Features.SubClassFeatures2014.Bard.BardCreationFeatures import (
    AnimatingPerformance,
)
from CharacterContent.Features.SubClassFeatures2014.Druid.DruidWildfireFeatures import (
    SummonWildfireSpirit,
)
from CharacterContent.Features.SubClassFeatures2014.Fighter.FighterEchoKnightFeatures import (
    ManifestEcho,
)
from Core.Definitions import Ability, CharacterClass, Condition, DamageType
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

BATTLE_SMITH_BUILD = "Y2024_Artificer_BattleSmith_PetraGearhollow"
WILDFIRE_BUILD = "Y2014DruidWildfireEmberAshgroveCharacterBuilder"
VESTIGE_BUILD = "Y2024WarlockVestigeOrsolyaHollowvowCharacterBuilder"
BEAST_MASTER_BUILD = "Y2024RangerBeastMasterFennWildstriderCharacterBuilder"
CREATION_BUILD = "Y2014BardCreationPiperWrenhollowCharacterBuilder"
ECHO_KNIGHT_BUILD = "Y2014FighterEchoKnightLucianMirrorstrikeCharacterBuilder"


@cache
def _sheet(build_name: str):
    return build(build_name)


def _feature(sheet, feature_type: type) -> Feature:
    (feature,) = [f for f in sheet.features if isinstance(f, feature_type)]
    return feature


def _only_spec(sheet, feature_type: type) -> SummonSpec:
    (spec,) = _feature(sheet, feature_type).summons(sheet)
    return spec


@pytest.mark.parametrize(
    "build_name, feature_type",
    [
        (BATTLE_SMITH_BUILD, SteelDefender),
        (WILDFIRE_BUILD, SummonWildfireSpirit),
        (VESTIGE_BUILD, VestigeCompanion),
        (BEAST_MASTER_BUILD, PrimalCompanion),
        (CREATION_BUILD, AnimatingPerformance),
        (ECHO_KNIGHT_BUILD, ManifestEcho),
    ],
    ids=lambda v: v if isinstance(v, str) else v.__name__,
)
def test_the_summoning_feature_is_the_only_one_in_its_build(
    build_name: str, feature_type: type
):
    sheet = _sheet(build_name)
    summoners = [f for f in sheet.iter_features_with_extensions() if f.summons(sheet)]
    assert [type(f) for f in summoners] == [feature_type]


# ---------------------------------------------------------------------------
# Steel Defender


def test_the_steel_defender_spec_follows_its_rules_text():
    sheet = _sheet(BATTLE_SMITH_BUILD)
    spec = _only_spec(sheet, SteelDefender)
    assert spec.name == "Steel Defender"
    assert spec.choices(sheet) == []
    # "Whenever you finish a Long Rest, you can create a new defender ... If
    # you already have a defender from this feature, the first one vanishes."
    assert spec.max_out == 1
    assert spec.when_full is WhenFull.REPLACES
    assert spec.lifetime is SummonLifetime.UNTIL_DISMISSED
    # "If the defender has died within the last hour ... The defender returns
    # to life": it leaves a body.
    assert spec.on_zero_hp is OnZeroHp.DIES
    # "It vanishes if you die."
    assert spec.drops_with_owner is True
    # "In combat, the defender acts during your turn."
    assert spec.turn is SummonTurn.AFTER_OWNER
    # Made at the end of a Long Rest; nothing is spent.
    assert spec.costs == ()
    assert spec.count(sheet, SummonContext()) == 1


def test_the_steel_defender_builds_its_stat_block():
    sheet = _sheet(BATTLE_SMITH_BUILD)
    defender = _only_spec(sheet, SteelDefender).build(sheet, SummonContext())
    assert defender.combatant_type == "Steel Defender"
    artificer_level = sheet.get_class_level(CharacterClass.ARTIFICER)
    # "Hit Points 5 + five times your Artificer level", "AC 12 plus your
    # Intelligence modifier".
    assert defender.hp == 5 + 5 * artificer_level
    assert defender.ac == 12 + sheet.get_intelligence_modifier()
    assert [a.name for a in defender.actions or []] == [
        "Force-Empowered Rend",
        "Repair (3/Day)",
    ]


# ---------------------------------------------------------------------------
# Wildfire Spirit


def test_the_wildfire_spirit_spec_follows_its_rules_text():
    sheet = _sheet(WILDFIRE_BUILD)
    spec = _only_spec(sheet, SummonWildfireSpirit)
    assert spec.name == "Wildfire Spirit"
    assert spec.choices(sheet) == []
    # "The spirit manifests for 1 hour, until it is reduced to 0 hit points,
    # until you use this feature to summon the spirit again, or until you die."
    assert spec.lifetime is SummonLifetime.DURATION
    assert spec.duration_seconds == 60 * 60
    assert spec.max_out == 1
    assert spec.when_full is WhenFull.REPLACES
    assert spec.on_zero_hp is OnZeroHp.VANISHES
    assert spec.drops_with_owner is True
    # "In combat, the spirit shares your initiative count, but it takes its
    # turn immediately after yours."
    assert spec.turn is SummonTurn.AFTER_OWNER
    # "you can expend one use of your Wild Shape feature to summon your
    # wildfire spirit".
    assert spec.costs == (SummonCost(feature_use="Wild Shape"),)


def test_the_wildfire_spirit_is_paid_with_a_feature_the_druid_has():
    sheet = _sheet(WILDFIRE_BUILD)
    (cost,) = _only_spec(sheet, SummonWildfireSpirit).costs
    names = {f.name for f in sheet.iter_features_with_extensions()}
    assert cost.feature_use in names


def test_the_wildfire_spirit_builds_its_stat_block():
    sheet = _sheet(WILDFIRE_BUILD)
    spirit = _only_spec(sheet, SummonWildfireSpirit).build(sheet, SummonContext())
    assert spirit.combatant_type == "Wildfire Spirit"
    druid_level = sheet.get_class_level(CharacterClass.DRUID)
    # "Hit Points 5 + five times your druid level", "Armor Class 13".
    assert spirit.hp == 5 + 5 * druid_level
    assert spirit.ac == 13
    assert [a.name for a in spirit.actions or []] == [
        "Flame Seed",
        "Fiery Teleportation",
    ]


# ---------------------------------------------------------------------------
# Vestige Companion


def test_the_vestige_spec_follows_its_rules_text():
    sheet = _sheet(VESTIGE_BUILD)
    spec = _only_spec(sheet, VestigeCompanion)
    assert spec.name == "Vestige Companion"
    # Its type changes only when a Long Rest ends: nothing to choose in a
    # fight.
    assert spec.choices(sheet) == []
    # "If the vestige is already manifested from this feature, its form
    # changes to the new one."
    assert spec.max_out == 1
    assert spec.when_full is WhenFull.REPLACES
    assert spec.lifetime is SummonLifetime.UNTIL_DISMISSED
    # "When the vestige drops to 0 Hit Points, it disappears."
    assert spec.on_zero_hp is OnZeroHp.VANISHES
    # "It vanishes if you die."
    assert spec.drops_with_owner is True
    # "In combat, the vestige acts during your turn."
    assert spec.turn is SummonTurn.AFTER_OWNER
    # A 1-minute ceremony, no resource.
    assert spec.costs == ()


def test_the_vestige_builds_the_builds_own_type():
    sheet = _sheet(VESTIGE_BUILD)
    feature = _feature(sheet, VestigeCompanion)
    assert isinstance(feature, VestigeCompanion)
    (spec,) = feature.summons(sheet)
    vestige = spec.build(sheet, SummonContext())
    assert vestige.combatant_type == "Vestige Companion"
    warlock_level = sheet.get_class_level(CharacterClass.WARLOCK)
    # "Hit Points 4 + four times your Warlock level", "AC 13 plus your
    # Charisma modifier".
    assert vestige.hp == 4 + 4 * warlock_level
    assert vestige.ac == 13 + sheet.get_charisma_modifier()
    # Celestial: Radiant; Fiend: Fire; Undead: Necrotic.
    resisted = {"Celestial": "Radiant", "Fiend": "Fire", "Undead": "Necrotic"}
    assert [
        [d.value for d in e.damage_types] for e in vestige.damage_resistances or []
    ] == [[resisted[feature.vestige_type.value]]]


# ---------------------------------------------------------------------------
# Primal Companion


def test_the_primal_companion_spec_follows_its_rules_text():
    sheet = _sheet(BEAST_MASTER_BUILD)
    spec = _only_spec(sheet, PrimalCompanion)
    assert spec.name == "Primal Companion"
    # "Choose its stat block: Beast of the Land, Beast of the Sea or Beast of
    # the Sky", and the Strike's damage type when it's summoned (the Sky's
    # is always Slashing).
    assert spec.choice_label == "Primal Beast"
    assert spec.choices(sheet) == [
        "Beast of the Land (Bludgeoning)",
        "Beast of the Land (Piercing)",
        "Beast of the Land (Slashing)",
        "Beast of the Sea (Bludgeoning)",
        "Beast of the Sea (Piercing)",
        "Beast of the Sky",
    ]
    # "If you already have a beast from this feature, the old one vanishes
    # when the new one appears."
    assert spec.max_out == 1
    assert spec.when_full is WhenFull.REPLACES
    assert spec.lifetime is SummonLifetime.UNTIL_DISMISSED
    # "If the beast has died within the last hour ... The beast returns to
    # life": it leaves a body.
    assert spec.on_zero_hp is OnZeroHp.DIES
    # Nothing says it goes when you die.
    assert spec.drops_with_owner is False
    # "In Combat, the beast acts during your turn."
    assert spec.turn is SummonTurn.AFTER_OWNER
    assert spec.costs == ()


@pytest.mark.parametrize(
    "choice, combatant_type, damage_type",
    [
        ("Beast of the Land (Bludgeoning)", "Beast of the Land", "Bludgeoning"),
        ("Beast of the Land (Piercing)", "Beast of the Land", "Piercing"),
        ("Beast of the Land (Slashing)", "Beast of the Land", "Slashing"),
        ("Beast of the Sea (Bludgeoning)", "Beast of the Sea", "Bludgeoning"),
        ("Beast of the Sea (Piercing)", "Beast of the Sea", "Piercing"),
        ("Beast of the Sky", "Beast of the Sky", "Slashing"),
    ],
)
def test_each_primal_beast_choice_builds_that_beast(
    choice: str, combatant_type: str, damage_type: str
):
    sheet = _sheet(BEAST_MASTER_BUILD)
    beast = _only_spec(sheet, PrimalCompanion).build(
        sheet, SummonContext(choice=choice)
    )
    assert beast.combatant_type == combatant_type
    (strike,) = beast.actions or []
    assert strike.name == "Beast's Strike"
    assert f" {damage_type} damage" in strike.description
    ranger_level = sheet.get_class_level(CharacterClass.RANGER)
    # Land and Sea: "5 + five times your Ranger level"; Sky: "4 + four times".
    per_level = 4 if combatant_type == "Beast of the Sky" else 5
    assert beast.hp == per_level + per_level * ranger_level


def test_no_choice_builds_the_builds_own_primal_beast():
    sheet = _sheet(BEAST_MASTER_BUILD)
    feature = _feature(sheet, PrimalCompanion)
    assert isinstance(feature, PrimalCompanion)
    (spec,) = feature.summons(sheet)
    own = spec.build(sheet, SummonContext())
    assert own.combatant_type == feature.companion_type.value


def test_a_primal_companion_built_without_a_damage_type_uses_its_first():
    sheet = _sheet(BEAST_MASTER_BUILD)
    (spec,) = PrimalCompanion(CompanionType.BEAST_OF_THE_SEA).summons(sheet)
    (strike,) = spec.build(sheet, SummonContext()).actions or []
    assert f" {DamageType.BLUDGEONING.value} damage" in strike.description


# ---------------------------------------------------------------------------
# Animating Performance


def test_the_dancing_item_spec_follows_its_rules_text():
    sheet = _sheet(CREATION_BUILD)
    spec = _only_spec(sheet, AnimatingPerformance)
    assert spec.name == "Dancing Item"
    assert spec.choices(sheet) == []
    # "You can have only one item animated by this feature at a time; if you
    # use this action and already have a dancing item from this feature, the
    # first one immediately becomes inanimate."
    assert spec.max_out == 1
    assert spec.when_full is WhenFull.REPLACES
    # "It lives for 1 hour, until it is reduced to 0 hit points, or until you
    # die."
    assert spec.lifetime is SummonLifetime.DURATION
    assert spec.duration_seconds == 60 * 60
    assert spec.on_zero_hp is OnZeroHp.VANISHES
    assert spec.drops_with_owner is True
    # "In combat, the item shares your initiative count, but it takes its
    # turn immediately after yours."
    assert spec.turn is SummonTurn.AFTER_OWNER
    # "Once you animate an item with this feature, you can't do so again
    # until you finish a long rest, unless you expend a spell slot of 3rd
    # level or higher".
    assert spec.costs == (SummonCost(), SummonCost(spell_slot=3))


def test_the_dancing_item_builds_its_stat_block():
    sheet = _sheet(CREATION_BUILD)
    item = _only_spec(sheet, AnimatingPerformance).build(sheet, SummonContext())
    assert item.combatant_type == "Dancing Item"
    bard_level = sheet.get_class_level(CharacterClass.BARD)
    # "Armor Class: 16 (natural armor)", "Hit Points: 10 + 5 times your bard
    # level", "Speed: 30 ft., fly 30 ft. (hover)".
    assert item.ac == 16
    assert item.hp == 10 + 5 * bard_level
    assert (item.speed_ground_ft, item.speed_fly_ft) == (30, 30)
    assert [d.value for e in item.damage_immunities or [] for d in e.damage_types] == [
        "Poison",
        "Psychic",
    ]
    assert [t.name for t in item.traits or []] == [
        "Immutable Form",
        "Irrepressible Dance",
    ]
    (slam,) = item.actions or []
    # "Hit: 1d10 + PB force damage", to hit with your spell attack modifier
    # (a bard's: Proficiency Bonus plus Charisma modifier).
    pb = sheet.get_proficiency_bonus()
    assert f"1d10 + {pb} Force damage" in slam.description
    spell_attack = pb + sheet.get_charisma_modifier()
    assert f"{spell_attack:+} to hit" in slam.description


# ---------------------------------------------------------------------------
# Manifest Echo


def test_the_echo_spec_follows_its_rules_text():
    sheet = _sheet(ECHO_KNIGHT_BUILD)
    spec = _only_spec(sheet, ManifestEcho)
    assert spec.name == "Echo"
    assert spec.choices(sheet) == []
    # It "lasts until it is destroyed, until you dismiss it as a bonus action,
    # until you manifest another echo, or until you're incapacitated."
    assert spec.max_out == 1
    assert spec.when_full is WhenFull.REPLACES
    assert spec.lifetime is SummonLifetime.UNTIL_DISMISSED
    assert spec.on_zero_hp is OnZeroHp.VANISHES
    assert spec.drops_with_owner is True
    # No turn of its own: it stays beside its owner's.
    assert spec.turn is SummonTurn.AFTER_OWNER
    # Only the Bonus Action.
    assert spec.costs == ()


def test_the_echo_builds_its_card():
    sheet = _sheet(ECHO_KNIGHT_BUILD)
    echo = _only_spec(sheet, ManifestEcho).build(sheet, SummonContext())
    assert echo.combatant_type == "Echo"
    # "Your echo has AC 14 + your proficiency bonus, 1 hit point, and immunity
    # to all conditions. If it has to make a saving throw, it uses your saving
    # throw bonus for the roll."
    assert echo.ac == 14 + sheet.get_proficiency_bonus()
    assert echo.hp == 1
    assert set(echo.condition_immunities or []) == set(Condition)
    # (A stat block keys its saves by the ability's short name.)
    assert echo.saving_throws == {
        ability.short_name: sheet.get_saving_throw_modifier(ability)
        for ability in Ability
    }
    assert echo.actions == []
