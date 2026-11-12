"""Feature.combat_effects (Model/Content/CombatEffect.py): what a feature says
using it does in a fight, which the combat UI's Custom Effect picker fills its
form from. The TimeLoopPR party's features are described first, so every one
of theirs is checked here. Expected values come from the rules text of each
feature, never from the code's own output."""

from dataclasses import replace
from functools import cache

import pytest

from Builds.Characters.Y2024_Artificer_Reanimator_Dessie import (
    Y2024ArtificerReanimatorDessieCharacterBuilder as Dessie,
)
from Builds.Characters.Y2024_Bard_Lore_TobiasGreyquill import (
    Y2024BardLoreTobiasGreyquillCharacterBuilder as Tobias,
)
from Builds.Characters.Y2024_Bard_Valor_Thomas import (
    Y2024BardValorThomasCharacterBuilder as Thomas,
)
from Builds.Characters.Y2024_Cleric_Light_GabrielGreybeard import (
    Y2024ClericLightGabrielGreybeardCharacterBuilder as Gabriel,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Builds.Characters.Y2024_Rogue_ArcaneTrickster_ThumSchtock import (
    Y2024RogueArcaneTricksterThumSchtockCharacterBuilder as Thum,
)
from Builds.Characters.Y2024_Druid_Moon_Maggie import (
    Y2024DruidMoonMaggieCharacterBuilder as Maggie,
)
from Builds.Characters.Y2024_Ranger_Drakewarden_Hanna import (
    Y2024RangerDrakewardenHannaCharacterBuilder as Hanna,
)
from CharacterContent.Features.SubClassFeatures.Artificer.ArtificerReanimatorFeatures import (
    ReanimatorSkillSet,
)
from Combat.Campaigns.TimeLoopPR.Campaign import CAMPAIGN
from Combat.CombatUIQt.effect_options import effect_options, feature_options
from Combat.CombatUIQt.saves import ATTACK_ROLL, HEALING, SAVING_THROW, TEMP_HP
from Combat.PlayerCombatant import combatant_from_character
from Core.Definitions import Ability, CharacterClass, DamageType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Content.Feature import ActionType, Feature, FeatureActivation

HOUR = 60 * 60


@cache
def _sheet(builder):
    return builder().build()


def _feature(sheet, name: str) -> Feature:
    return next(f for f in sheet.features if f.name == name)


def _effects(builder, feature_name: str) -> list[CombatEffect]:
    sheet = _sheet(builder)
    effects = _feature(sheet, feature_name).combat_effects(sheet)
    assert effects is not None, f"{feature_name} isn't described"
    return effects


def _rows(builder) -> dict:
    """The Custom Effect picker's Features rows for the character, by name."""
    char = combatant_from_character(_sheet(builder))
    features = dict(effect_options(char, all_spells=[])).get("Features", [])
    return {option.name: option for option in features}


# ---------------------------------------------------------------------------
# The model checks itself


def test_a_plain_effect_is_valid():
    effect = CombatEffect()
    assert effect.roll == "none" and effect.spends_use


@pytest.mark.parametrize(
    "kwargs",
    [
        {"roll": "save"},  # no ability
        {"save_ability": Ability.DEXTERITY},  # an ability without a save
        {"roll": "attack", "save_ability": Ability.DEXTERITY},
        {"half_on_success": True},
        {"repeat_save": True},
        {"dc": 13},
        {"attack_bonus": 5},
        {"roll": "check"},
        {"notes": ("",)},
    ],
)
def test_an_effect_that_contradicts_itself_is_refused(kwargs):
    with pytest.raises(ValueError):
        CombatEffect(**kwargs)


def test_a_roll_and_a_turn_given_as_text_are_kept_as_enums():
    # JSON and logs have them as text.
    effect = CombatEffect.from_dict(
        {
            "roll": "save",
            "save_ability": "Dexterity",
            "conditions": [{"name": "Prone", "until": ["start", "source"]}],
        }
    )
    assert effect.roll is EffectRoll.SAVE
    assert effect.conditions[0].until == (TurnEdge.START, TurnOf.SOURCE)
    assert type(effect.conditions[0].until[0]) is TurnEdge
    assert effect == CombatEffect.from_dict(effect.to_dict())
    assert effect.to_dict()["roll"] == "save"
    assert effect.to_dict()["conditions"][0]["until"] == ["start", "source"]


@pytest.mark.parametrize("until", [("middle", "source"), ("end", "ally")])
def test_an_unknown_turn_is_refused(until):
    with pytest.raises(ValueError):
        CombatCondition("Prone", until=until)  # type: ignore[arg-type]


@pytest.mark.parametrize("dice", ["2d4", "1d8 + 3", "4d6 - 1", "5"])
def test_damage_dice(dice):
    assert CombatDamage(dice, DamageType.FIRE).dice == dice


@pytest.mark.parametrize("dice", ["2d", "d6", "1d6+3", "two", ""])
def test_damage_that_isnt_dice_is_refused(dice):
    with pytest.raises(ValueError):
        CombatDamage(dice, DamageType.FIRE)


def test_a_damage_type_to_choose_needs_choices():
    with pytest.raises(ValueError):
        CombatDamage("1d6", None)
    with pytest.raises(ValueError):
        CombatDamage("1d6", DamageType.FIRE, choices=(DamageType.COLD,))
    both = (DamageType.COLD, DamageType.FIRE)
    assert CombatDamage("1d6", None, choices=both).choices == both


@pytest.mark.parametrize("until", [("middle", "target"), ("end", "ally")])
def test_a_condition_ends_at_a_turn_it_can_name(until):
    with pytest.raises(ValueError):
        CombatCondition("Prone", until=until)


def test_a_condition_needs_a_name():
    with pytest.raises(ValueError):
        CombatCondition(" ")


def test_a_feature_says_nothing_by_default():
    assert Feature("Something").combat_effects(_sheet(Thomas)) is None


# ---------------------------------------------------------------------------
# The TimeLoopPR party: every feature used in play is described


@pytest.mark.parametrize("sheet", CAMPAIGN.players(), ids=lambda s: s.character_name)
def test_every_feature_of_the_party_is_described(sheet):
    undescribed = [
        f.name
        for f in sheet.features
        if not f.passive and f.combat_effects(sheet) is None
    ]
    assert undescribed == []


@pytest.mark.parametrize(
    "builder, rows",
    [
        (Dessie, ["Shield (Magic Initiate)", "Tinker's Magic", "Jolt to Life"]),
        (Hanna, ["Portal Step", "Hunter's Mark (Favored Enemy)"]),
        (Maggie, ["Wild Companion"]),
        (Thomas, ["Bardic Inspiration"]),
    ],
    ids=["Dessie", "Hanna", "Maggie", "Thomas"],
)
def test_the_picker_lists_only_what_they_can_use(builder, rows):
    """Spellcasting, languages, Alert, summons and Wild Shape (used from the
    card menu) have nothing for the form, and passive features never had."""
    assert list(_rows(builder)) == rows


# Dessie: Reanimator's Skill Set's Jolt to Life


def test_jolt_to_life():
    (jolt,) = _effects(Dessie, "Reanimator's Skill Set")
    assert jolt.name == "Jolt to Life"
    assert jolt.roll == "save" and jolt.save_ability is Ability.DEXTERITY
    assert jolt.half_on_success
    assert jolt.damage == (CombatDamage("2d4", DamageType.LIGHTNING),)
    # Modifying Spare the Dying: the spell's casting takes the Action.
    assert jolt.action_type is ActionType.ACTION
    # "regains a number of Hit Points equal to your Artificer level"
    assert any("regains 3 Hit Points" in note for note in jolt.notes)


def test_jolt_to_life_in_the_picker():
    """Against the spell save DC: 8 + Intelligence modifier + proficiency."""
    sheet = _sheet(Dessie)
    row = _rows(Dessie)["Jolt to Life"]
    dc = 8 + sheet.get_intelligence_modifier() + sheet.get_proficiency_bonus()
    assert (row.roll, row.ability, row.dc) == (SAVING_THROW, "DEX", dc)
    assert row.damage == "2d4 Lightning" and row.half_on_save
    assert row.action_cost == "Action"
    # Its uses are Reanimator's Skill Set's.
    assert row.feature_name == "Reanimator's Skill Set" and row.counts_uses
    assert row.is_described


class _ArtificerAt:
    """Just enough of a character for Jolt to Life's damage at a level."""

    def __init__(self, level: int):
        self.level = level

    def get_class_level(self, character_class):
        assert character_class is CharacterClass.ARTIFICER
        return self.level


@pytest.mark.parametrize(
    "level, dice", [(3, "2d4"), (10, "2d4"), (11, "3d4"), (16, "3d4"), (17, "4d4")]
)
def test_jolt_to_life_grows_at_artificer_levels_11_and_17(level, dice):
    (jolt,) = ReanimatorSkillSet().combat_effects(_ArtificerAt(level))
    assert jolt.damage[0].dice == dice


def test_tinkers_magic_spends_a_use_and_the_action():
    row = _rows(Dessie)["Tinker's Magic"]
    assert row.roll == SAVING_THROW and row.ability is None  # no roll
    assert row.action_cost == "Action" and row.counts_uses
    assert row.is_tracked  # applying it alone spends it
    assert "nothing happens to the targets" in row.note


# Hanna: Portal Jumper and Favored Enemy


def test_portal_step_spends_a_use_and_no_action():
    """It's 15 feet of movement, once per turn."""
    row = _rows(Hanna)["Portal Step"]
    assert row.feature_name == "Portal Jumper"
    assert row.action_cost is None and row.counts_uses and row.is_tracked
    assert "15 feet of movement" in row.note


def test_favored_enemy_casts_hunters_mark_without_a_slot():
    row = _rows(Hanna)["Hunter's Mark (Favored Enemy)"]
    # Hunter's Mark: Bonus Action, Concentration, up to 1 hour, on the target.
    assert row.condition == "Hunter's Mark"
    assert row.duration_seconds == HOUR
    assert row.concentration and row.action_cost == "Bonus Action"
    assert row.spell_name == "Hunter's Mark"
    assert row.slot_level is None and row.counts_uses
    assert "1d6 Force" in row.note


# Maggie: Wild Companion


def test_wild_companion_takes_the_action_and_says_what_it_costs():
    row = _rows(Maggie)["Wild Companion"]
    assert row.action_cost == "Action"
    assert not row.counts_uses  # a slot or a Wild Shape use, by hand
    assert "spell slot or a use of Wild Shape" in row.note


def test_wild_shape_is_left_to_its_own_menu():
    sheet = _sheet(Maggie)
    assert _feature(sheet, "Wild Shape").combat_effects(sheet) == []


# Thomas: Bardic Inspiration, with Valor's Combat Inspiration


def test_bardic_inspiration_is_a_badge_for_an_hour():
    row = _rows(Thomas)["Bardic Inspiration"]
    assert row.condition == "Bardic Inspiration"
    assert row.duration_seconds == HOUR  # "Once within the next hour"
    assert row.action_cost == "Bonus Action" and row.counts_uses
    assert "1d6" in row.note  # a d6 until Bard level 5


def test_combat_inspiration_is_in_a_valor_bards_note():
    """Combat Inspiration adds to Bardic Inspiration's effect
    (Feature.adjust_combat_effect): two more ways to spend the die."""
    (effect,) = _effects(Thomas, "Bardic Inspiration")
    assert not any("Combat Inspiration" in n for n in effect.notes)
    note = _rows(Thomas)["Bardic Inspiration"].note
    assert "Combat Inspiration: it can instead add the 1d6 to its AC" in note


def test_a_lore_bard_has_no_combat_inspiration():
    assert "Combat Inspiration" not in _rows(Tobias)["Bardic Inspiration"].note


# ---------------------------------------------------------------------------
# What the picker makes of a description


class _Described(Feature):
    def __init__(self, effects):
        super().__init__(name="Test Feature")
        self._effects = effects

    def combat_effects(self, character):
        return self._effects


def _options(feature) -> list:
    return feature_options(combatant_from_character(_sheet(Thomas)), feature)


def test_nothing_to_apply_leaves_a_feature_out():
    assert _options(_Described([])) == []


def test_one_row_per_use():
    rows = _options(_Described([CombatEffect(name="A"), CombatEffect(name="B")]))
    assert [r.name for r in rows] == ["A", "B"]
    assert {r.feature_name for r in rows} == {"Test Feature"}


def test_an_undescribed_passive_feature_is_left_out():
    feature = Feature("Quiet", passive=True)
    assert _options(feature) == []
    assert len(_options(Feature("Loud"))) == 1  # read from its text, as before


def test_an_attack_takes_the_users_spell_attack_bonus():
    sheet = _sheet(Thomas)
    (row,) = _options(
        _Described(
            [
                CombatEffect(
                    roll=EffectRoll.ATTACK,
                    damage=(CombatDamage("1d10", DamageType.FIRE),),
                )
            ]
        )
    )
    attack = sheet.get_charisma_modifier() + sheet.get_proficiency_bonus()
    assert (row.roll, row.bonus, row.damage) == (ATTACK_ROLL, attack, "1d10 Fire")


def test_its_own_dc_and_a_condition_until_a_turn():
    effect = CombatEffect(
        roll=EffectRoll.SAVE,
        save_ability=Ability.WISDOM,
        dc=15,
        repeat_save=True,
        conditions=(
            CombatCondition("Frightened", until=(TurnEdge.END, TurnOf.SOURCE)),
        ),
    )
    (row,) = _options(_Described([effect]))
    assert (row.ability, row.dc, row.repeat_save) == ("WIS", 15, True)
    assert (row.condition, row.until) == ("Frightened", ("end", "source"))


def test_a_damage_type_to_choose_is_left_to_the_user():
    choices = (DamageType.COLD, DamageType.FIRE)
    (row,) = _options(
        _Described([CombatEffect(damage=(CombatDamage("2d6", None, choices),))])
    )
    assert row.damage == "2d6"
    assert "(Cold, Fire): give one" in row.note


def test_a_use_that_spends_nothing():
    feature = _Described([CombatEffect(spends_use=False)])
    feature.uses = _feature(_sheet(Thomas), "Bardic Inspiration").uses
    (row,) = _options(feature)
    assert not row.counts_uses


# Healing and Temporary Hit Points a feature gives each target


def test_a_feature_that_heals_fills_the_healing_box():
    (row,) = _options(_Described([CombatEffect(healing=CombatHitPoints("1d10 + 3"))]))
    assert (row.amount_kind, row.damage) == (HEALING, "1d10 + 3")
    assert row.summary == "heals 1d10 + 3"


def test_a_feature_that_gives_temporary_hit_points():
    (row,) = _options(_Described([CombatEffect(temp_hp=CombatHitPoints("5"))]))
    assert (row.amount_kind, row.damage) == (TEMP_HP, "5")


# A use that casts a spell, and features that change other effects


def test_a_use_that_casts_a_spell_takes_the_spells_effect():
    """Fireball cast by a feature: the spell's save and damage, the feature's
    own note first, and the spell's casting time and Concentration (none)."""
    (row,) = _options(
        _Described([CombatEffect(spell="Fireball", notes=("Without a slot.",))])
    )
    assert (row.ability, row.half_on_save, row.damage) == ("DEX", True, "8d6 Fire")
    assert row.note.startswith("Without a slot.")
    assert row.action_cost == "Action" and not row.concentration
    assert row.slot_level is None


def test_what_the_use_says_wins_over_the_spell():
    (row,) = _options(
        _Described(
            [
                CombatEffect(
                    spell="Hunter's Mark",
                    conditions=(
                        CombatCondition("Marked", until=(TurnEdge.END, TurnOf.SOURCE)),
                    ),
                    action_type=ActionType.REACTION,
                )
            ]
        )
    )
    assert row.condition == "Marked" and row.until == ("end", "source")
    assert row.action_cost == "Reaction"
    assert row.concentration  # still the spell's
    assert "1d6 Force" in row.note  # and its notes


def test_a_features_own_action_wins_over_the_spells_casting_time():
    """Wild Companion's Magic action casts Find Familiar (1 hour to cast)."""
    feature = _Described([CombatEffect(spell="Hunter's Mark")])
    feature.activation = FeatureActivation(action_type=ActionType.ACTION)
    (row,) = _options(feature)
    assert row.action_cost == "Action"


class _Adds(Feature):
    """Adds a note to the effects of the feature or spell named `source`."""

    def __init__(self, source: str, note: str):
        super().__init__(name=f"Adds to {source}")
        self.source, self.note = source, note

    def adjust_combat_effect(self, character, source, effect):
        if source != self.source:
            return effect
        return replace(effect, notes=effect.notes + (self.note,))


def test_a_feature_adjusts_only_the_source_it_names(monkeypatch):
    char = combatant_from_character(_sheet(Thomas))
    sheet = char["_stat_block"]
    real = sheet.iter_features_with_extensions
    adders = [_Adds("Test Feature", "From the hook."), _Adds("Other", "Never.")]
    monkeypatch.setattr(
        sheet, "iter_features_with_extensions", lambda: [*real(), *adders]
    )
    (row,) = feature_options(char, _Described([CombatEffect(notes=("Own.",))]))
    assert row.note == "Own. From the hook."
    fireball = dict(effect_options(char, all_spells=[]))
    assert all("Never." not in o.note for rows in fireball.values() for o in rows)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"healing": CombatHitPoints("1d4"), "temp_hp": CombatHitPoints("1d4")},
        {
            "healing": CombatHitPoints("1d4"),
            "damage": (CombatDamage("1d6", DamageType.FIRE),),
        },
        {
            "temp_hp": CombatHitPoints("5"),
            "damage": (CombatDamage("1d6", DamageType.FIRE),),
        },
        # Hit Points are a CombatHitPoints, not bare dice.
        {"healing": "1d4"},
    ],
)
def test_one_amount_box_and_hit_points_as_hit_points(kwargs):
    with pytest.raises(ValueError):
        CombatEffect(**kwargs)


@pytest.mark.parametrize("dice", ["lots", "1d"])
def test_hit_points_that_arent_dice_are_refused(dice):
    with pytest.raises(ValueError):
        CombatHitPoints(dice)


# ---------------------------------------------------------------------------
# The Curse of the Lich party: Gabriel (Light Domain Cleric), Edmund
# (Devotion Paladin), Thum Schtock (Arcane Trickster Rogue)


def _level(builder, character_class) -> int:
    return _sheet(builder).get_class_level(character_class)


def test_divine_spark_heals_or_harms():
    """1d8 + Wisdom modifier at Cleric levels below 7: healing, or a
    Constitution save for Necrotic or Radiant damage, half on a success."""
    rows = _rows(Gabriel)
    wisdom = _sheet(Gabriel).get_wisdom_modifier()
    heal, harm = rows["Divine Spark: heal"], rows["Divine Spark: harm"]
    assert (heal.amount_kind, heal.damage) == (HEALING, f"1d8 + {wisdom}")
    assert (harm.ability, harm.half_on_save) == ("CON", True)
    assert harm.damage == f"1d8 + {wisdom}"
    assert "Necrotic, Radiant" in harm.note
    for row in (heal, harm):
        assert row.feature_name == "Channel Divinity" and row.counts_uses
        assert row.action_cost == "Action"


def test_turn_undead_frightens_and_incapacitates_for_a_minute():
    row = _rows(Gabriel)["Turn Undead"]
    assert (row.ability, row.dc) == (
        "WIS",
        _sheet(Gabriel).calculate_difficulty_class_for_ability(Ability.WISDOM),
    )
    assert row.condition == "Frightened + Incapacitated"
    assert row.duration_seconds == 60
    assert "Undead" in row.note


def test_radiance_of_the_dawn_is_a_use_of_channel_divinity():
    """An extension of Channel Divinity: a Constitution save for 2d10 +
    Cleric level Radiant damage, half on a success."""
    row = _rows(Gabriel)["Radiance of the Dawn"]
    level = _level(Gabriel, CharacterClass.CLERIC)
    assert (row.ability, row.half_on_save) == ("CON", True)
    assert row.damage == f"2d10 + {level} Radiant"
    assert row.feature_name == "Channel Divinity" and row.counts_uses


def test_warding_flare_is_a_reaction_with_its_own_uses():
    row = _rows(Gabriel)["Warding Flare"]
    assert row.action_cost == "Reaction"
    assert row.feature_name == "Warding Flare" and row.counts_uses
    assert "Disadvantage" in row.note


def test_lay_on_hands_heals_what_the_gm_types_from_the_pool():
    row = _rows(Edmund)["Lay on Hands"]
    pool = 5 * _level(Edmund, CharacterClass.PALADIN)
    assert (row.amount_kind, row.damage) == (HEALING, "")
    assert row.action_cost == "Bonus Action"
    assert f"({pool} after a Long Rest)" in row.note
    assert "Poisoned" not in row.note  # a row of its own now (Q7)


def test_lay_on_hands_ends_poisoned_in_a_row_of_its_own():
    """ "expend 5 Hit Points from the pool ... to remove the Poisoned
    condition from the creature; those points don't also restore Hit Points"."""
    row = _rows(Edmund)["Lay on Hands: end Poisoned"]
    assert row.ends_conditions == ("Poisoned",)
    assert (row.damage, row.condition) == ("", "")
    assert row.action_cost == "Bonus Action"
    assert "Spends 5 from the pool" in row.note


def test_paladins_smite_casts_divine_smite_without_a_slot():
    row = _rows(Edmund)["Divine Smite (Paladin's Smite)"]
    assert row.damage == "2d8 Radiant"
    assert row.spell_name == "Divine Smite" and row.slot_level is None
    assert row.action_cost == "Bonus Action"  # the spell's casting time
    assert row.note.startswith("Without a spell slot, once per Long Rest.")


def test_paladins_smite_counts_its_one_free_casting():
    """ "you must finish a Long Rest before you can cast it in this way
    again": one use, all back on a Long Rest (Q8)."""
    from CharacterContent.Features.ClassFeatures.Paladin.PaladinFeatures import (
        PaladinsSmite,
    )
    from Combat.CombatUIQt.resources import feature_lack

    uses = PaladinsSmite().uses
    assert uses is not None
    assert (uses.max_uses, uses.regain_all_on) == (1, "long rest")
    row = _rows(Edmund)["Divine Smite (Paladin's Smite)"]
    assert row.counts_uses and row.feature_name == "Paladin's Smite"
    char = combatant_from_character(_sheet(Edmund))
    assert feature_lack(char, "Paladin's Smite") is None
    char["feature_uses_used"] = {"Paladin's Smite": 1}
    assert feature_lack(char, "Paladin's Smite") == "Paladin's Smite: no uses left"
    assert "If the target is a Fiend or an Undead: 1d8 Radiant more" in row.note


def test_sneak_attack_is_its_dice_of_the_weapons_type():
    """(Rogue level + 1) // 2 d6, once per turn, on a creature hit."""
    row = _rows(Thum)["Sneak Attack"]
    dice = (_level(Thum, CharacterClass.ROGUE) + 1) // 2
    assert row.damage == f"{dice}d6"
    assert row.action_cost is None and not row.counts_uses
    assert "Finesse or a Ranged weapon" in row.note


# Free castings counted once per Long Rest each (Q56)


def test_fey_touched_counts_each_free_casting_on_its_own():
    # Fey Touched: "You can cast each of these spells without expending a
    # spell slot. Once you cast either spell in this way, you can't cast that
    # spell in this way again until you finish a Long Rest."
    char = combatant_from_character(_sheet(Thum))
    misty, detect = "Misty Step (Fey Touched)", "Detect Magic (Fey Touched)"
    char["feature_uses_used"] = {misty: 1}
    rows = _rows(Thum)
    assert rows[misty].counts_uses and rows[misty].feature_name == misty
    assert rows[detect].feature_name == detect
    rows = {
        option.name: option
        for option in dict(effect_options(char, all_spells=[]))["Features"]
    }
    assert rows[misty].summary.startswith("0/1")
    assert rows[detect].summary.startswith("1/1")  # the other one is still free


def test_uses_per_long_rest_reads_back_as_it_was_written():
    effect = CombatEffect(name="Misty Step (Fey Touched)", uses_per_long_rest=1)
    data = effect.to_dict()
    assert data == {"name": "Misty Step (Fey Touched)", "uses_per_long_rest": 1}
    assert CombatEffect.from_dict(data) == effect


@pytest.mark.parametrize(
    "make",
    [
        lambda: CombatEffect(uses_per_long_rest=1),  # nothing to count it under
        lambda: CombatEffect(name="Free", uses_per_long_rest=-1),
        lambda: CombatEffect(name="Free", uses_per_long_rest=True),
    ],
)
def test_uses_per_long_rest_is_a_count_under_a_name(make):
    with pytest.raises(ValueError):
        make()
