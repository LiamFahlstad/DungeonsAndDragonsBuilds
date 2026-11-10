"""What the Custom Effect dialog's picker reads out of spells, features,
weapons and stat-block actions (Combat/CombatUIQt/effect_options.py). The
expected values come from each spell's own text and the rules, read by hand:
Fireball's "taking 8d6 Fire damage on a failed save or half as much damage on a
successful one", Web's 2d4 Fire that's for the webs burning, and so on."""

import random
from types import SimpleNamespace

import pytest

from Builds.Characters.Y2024_Barbarian_Berserker_YmiraSkullcrusher import (
    Y2024BarbarianBerserkerYmiraSkullcrusherCharacterBuilder as Ymira,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory
from Combat.CombatUIQt.effect_options import (
    ALL_SPELLS,
    FEATURES,
    effect_options,
    read_effect_text,
    spell_option,
)
from Combat.CombatUIQt.saves import (
    EffectOption,
    ATTACK_ROLL,
    DAMAGE_AMOUNT,
    FEATURE,
    HEALING,
    MONSTER_ACTION,
    SAVING_THROW,
    TEMP_HP,
    read_damage,
)
from Combat.Monsters.CR_1.monsters import Ghoul
from Combat.Monsters.CR_21.monsters import Lich
from Combat.Monsters.CR_7.monsters import MindFlayer
from Combat.PlayerCombatant import (
    combatant_from_character,
    combatant_from_stat_block,
)
from Core.Weapons import WeaponDamageRolls, WeaponDamageTypes
from Model.Content.ExtraDamage import ExtraDamage

# A monster whose Spellcasting says its numbers, as a reloaded fight has it.
CASTER = {
    "name": "Cultist",
    "actions": [
        {
            "name": "Spellcasting",
            "description": "It casts a spell (spell save DC 15, +7 to hit with spell attacks).",
        }
    ],
}
SLASH = {
    "name": "Scimitar",
    "description": "Melee Attack Roll: +4, reach 5 ft. Hit: 5 (1d6 + 2) Slashing damage.",
}
GRAB = {
    "name": "Bite",
    "description": "Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d10 + 2) Piercing"
    " damage, and the target has the Grappled condition (escape DC 13).",
}
BREATH = {
    "name": "Fire Breath (Recharge 5–6)",
    "description": "Dexterity Saving Throw: DC 13, each creature in a 15-foot Cone."
    " Failure: 14 (4d6) Fire damage. Success: Half damage.",
}
SMITE = {
    "name": "Smite",
    "description": "Melee Attack Roll: +6, reach 5 ft. Hit: 8 (1d8 + 4) Radiant or"
    " Necrotic damage, and it can't regain Hit Points until the start of its next turn.",
}
GAZE = {
    "name": "Gaze (Costs 2 Actions)",
    "description": "Wisdom Saving Throw: DC 14, one creature. Failure: The target has"
    " the Frightened condition, and it repeats the save at the end of each of its turns.",
}


def _spell(name: str):
    """The spell without its combat effects, if it has any: these tests are
    for reading its text, which every spell without them still relies on.
    tests/test_spell_combat_effects.py covers the described ones."""
    data = SpellFactory._load_json()[name]
    return DataSpell(
        {key: value for key, value in data.items() if key != "combat_effects"}
    )


def _option(name: str, char: dict | None = None):
    return spell_option(_spell(name), CASTER if char is None else char)


# ---------------------------------------------------------------------------
# Spells, from their text


def test_fireball():
    fireball = _option("Fireball")
    assert fireball.roll == SAVING_THROW
    assert fireball.ability == "DEX"
    assert fireball.dc == 15
    assert fireball.half_on_save
    assert fireball.damage == "8d6 Fire"
    assert fireball.condition == ""
    assert fireball.action_cost == "Action"
    assert not fireball.concentration


def test_hold_person():
    hold = _option("Hold Person")
    assert hold.ability == "WIS"
    assert hold.condition == "Paralyzed"
    assert hold.concentration
    assert hold.repeat_save
    assert hold.damage == ""
    assert hold.duration_seconds == 60


def test_guiding_bolt_is_an_attack():
    bolt = _option("Guiding Bolt")
    assert bolt.roll == ATTACK_ROLL
    assert bolt.bonus == 7
    assert bolt.ability is None
    assert bolt.damage == "4d6 Radiant"


def test_webs_fire_damage_is_for_the_webs():
    web = _option("Web")
    assert web.ability == "DEX"
    assert web.condition == "Restrained"
    assert web.damage == ""


def test_toll_the_dead_fills_the_first_die_and_says_so():
    toll = _option("Toll the Dead")
    assert toll.ability == "WIS"
    assert toll.damage == "1d8 Necrotic"
    assert toll.note


@pytest.mark.parametrize(
    "name, damage",
    [
        ("Flame Strike", "5d6 Fire + 5d6 Radiant"),
        ("Ice Storm", "2d10 Bludgeoning + 4d6 Cold"),
        ("Enervation", "6d8 Necrotic"),  # not the 2d8 of its later turns
    ],
)
def test_damage_joined_onto_the_first(name, damage):
    option = _option(name)
    assert option.ability == "DEX"
    assert option.half_on_save
    assert option.damage == damage


def test_a_spell_with_nothing_to_roll_is_its_own_condition():
    bless = _option("Bless")
    assert bless.ability is None
    assert bless.roll == SAVING_THROW  # with "No saving throw"
    assert bless.damage == ""
    assert bless.condition == "Bless"
    assert bless.concentration


@pytest.mark.parametrize("name", ["Hex", "Hunter's Mark"])
def test_damage_with_no_roll_isnt_filled_in_but_said(name):
    option = _option(name)
    assert option.damage == ""
    assert option.ability is None
    assert "damage" in option.note


def test_healing_is_not_damage():
    """It fills the amount box as healing, with no damage type."""
    cure = _option("Cure Wounds")
    assert cure.amount_kind == HEALING
    assert [roll.damage_type for roll in cure.rolls] == [None]
    assert cure.ability is None


def test_slow_has_a_save_and_no_condition_of_the_rules():
    slow = _option("Slow")
    assert slow.ability == "WIS"
    assert slow.condition == "Slow"
    assert slow.repeat_save


@pytest.mark.parametrize(
    "level, damage",
    [(4, "1d10 Fire"), (5, "2d10 Fire"), (11, "3d10 Fire"), (17, "4d10 Fire")],
)
def test_a_cantrip_grows_with_the_characters_level(level, damage):
    caster = {"class_levels": {"Wizard": level - 1, "Fighter": 1}}
    assert _option("Fire Bolt", caster).damage == damage


def test_a_monsters_cantrip_stays_as_it_is():
    assert _option("Fire Bolt").damage == "1d10 Fire"


@pytest.mark.parametrize(
    "slot, damage", [(None, "8d6 Fire"), (3, "8d6 Fire"), (5, "10d6 Fire")]
)
def test_upcasting(slot, damage):
    assert _option("Fireball").damage_at(slot) == damage


def test_upcasting_grows_only_the_part_it_names():
    assert _option("Ice Storm").damage_at(6) == "4d10 Bludgeoning + 4d6 Cold"
    assert _option("Flame Strike").damage_at(7) == "7d6 Fire + 7d6 Radiant"


def test_the_slot_is_the_cheapest_that_fits():
    caster = dict(CASTER, spell_slots={1: 0, 2: 0, 3: 0, 4: 2, 5: 1})
    fireball = _option("Fireball", caster)
    assert fireball.slot_level == 4
    assert fireball.damage == "9d6 Fire"


def test_no_slot_left_says_so():
    fireball = _option("Fireball", dict(CASTER, spell_slots={1: 2, 3: 0}))
    assert fireball.slot_level is None
    assert fireball.damage == "8d6 Fire"
    assert "No slot of level 3" in fireball.note


def test_a_monsters_spell_attack_isnt_its_weapons():
    """known_attack_bonus falls back to a monster's first attack; a spell
    mustn't, so the GM sets it."""
    bolt = _option("Guiding Bolt", {"name": "Thug", "actions": [SLASH]})
    assert bolt.bonus is None
    assert "bonus" in bolt.note


def test_an_unknown_dc_is_left_to_the_gm():
    fireball = _option("Fireball", {"name": "Thug"})
    assert fireball.dc is None
    assert "DC" in fireball.note


def test_a_players_own_spell_uses_its_own_ability():
    """A multiclass caster's spell has its class's ability."""
    edmund = combatant_from_character(Edmund().build())
    sheet = edmund["_stat_block"]
    command = spell_option(edmund["_spell_objects"]["Command"], edmund)
    ability = edmund["_spell_objects"]["Command"].spell_casting_ability
    assert command.dc == sheet.calculate_difficulty_class_for_ability(ability)


def test_a_spells_modifier_is_added_for_a_player():
    edmund = combatant_from_character(Edmund().build())
    modifier = edmund["_stat_block"].get_ability_modifier(
        edmund["_stat_block"].spell_casting_ability
    )
    weapon = spell_option(_spell("Spiritual Weapon"), edmund)
    assert weapon.damage == f"1d8 + {modifier} Force"


@pytest.mark.parametrize(
    "text",
    [
        "You have Advantage on Wisdom saving throws.",
        "Each ally has Advantage on Dexterity saving throws against effects it can see.",
        "When you make a Constitution saving throw to maintain Concentration, add 2.",
        "Immediately after the spell ends, you must succeed on a DC 15 Constitution"
        " saving throw or gain 1 Exhaustion level.",
    ],
)
def test_merely_mentioning_a_save_isnt_one(text):
    assert read_effect_text(text).ability is None


def test_rage_and_danger_sense_have_no_save():
    ymira = combatant_from_character(Ymira().build())
    options = dict(effect_options(ymira, all_spells=[]))[FEATURES]
    for name in ("Rage", "Danger Sense"):
        option = next(o for o in options if o.name == name)
        assert option.ability is None, name
        assert option.condition == "", name  # Rage ends on Incapacitated


# ---------------------------------------------------------------------------
# Monster actions, weapons and features


def test_a_monsters_attack():
    (scimitar,) = dict(effect_options({"actions": [SLASH]}, []))["Actions"]
    assert scimitar.kind == MONSTER_ACTION
    assert scimitar.roll == ATTACK_ROLL
    assert scimitar.bonus == 4
    assert scimitar.damage == "1d6 + 2 Slashing"
    assert scimitar.row_text == "Scimitar  +4  1d6 + 2 Slashing"


def test_a_monsters_save():
    (breath,) = dict(effect_options({"actions": [BREATH]}, []))["Actions"]
    assert breath.ability == "DEX"
    assert breath.dc == 13
    assert breath.half_on_save
    assert breath.damage == "4d6 Fire"


def test_a_monsters_condition_and_rider():
    bite, smite = dict(effect_options({"actions": [GRAB, SMITE]}, []))["Actions"]
    assert bite.condition == "Grappled"
    assert smite.damage == "1d8 + 4"  # the type it chooses is left to the GM
    assert "type" in smite.note
    assert "Also: " in smite.note and "regain Hit Points" in smite.note


def test_a_monsters_repeat_save():
    (gaze,) = dict(effect_options({"legendary_actions": [GAZE]}, []))[
        "Legendary Actions"
    ]
    assert gaze.condition == "Frightened"
    assert gaze.repeat_save


def test_what_a_monster_cant_use_now_is_unavailable():
    char = {
        "actions": [BREATH, SLASH],
        "legendary_actions": [GAZE],
        "legendary_actions_left": 1,
        "spent_abilities": {BREATH["name"]: 1},
    }
    options = dict(effect_options(char, []))
    breath, scimitar = options["Actions"]
    (gaze,) = options["Legendary Actions"]
    assert breath.is_unavailable and "(spent)" in breath.row_text
    assert not scimitar.is_unavailable
    assert gaze.is_unavailable and "(1 left)" in gaze.row_text


def test_nothing_to_roll_is_listed_by_name():
    multiattack = {"name": "Multiattack", "description": "It makes two attacks."}
    (option,) = dict(effect_options({"actions": [multiattack]}, []))["Actions"]
    assert option.damage == "" and option.bonus is None and option.ability is None


def _weapon(die: str, bonus: int, extra=()):
    return SimpleNamespace(
        name="Blade",
        description_text="",
        damage_type=WeaponDamageTypes.SLASHING,
        extra_damage=list(extra),
        calculate_total_attack_roll_bonus_int=lambda sheet: 5,
        get_damage_roll=lambda sheet: SimpleNamespace(value=die),
        calculate_damage_bonus_int=lambda sheet: bonus,
    )


def _weapon_option(weapon):
    char = {"_weapons_objects": [weapon], "_stat_block": None}
    return dict(effect_options(char, []))["Attacks"][0]


@pytest.mark.parametrize(
    "die, bonus, damage",
    [
        ("1d8", 3, "1d8 + 3 Slashing"),
        ("1d8", 0, "1d8 Slashing"),
        ("1d8", -1, "1d8 - 1 Slashing"),
        ("1d1", 3, "4 Slashing"),  # an Unarmed Strike's 1 + modifier
        ("1d1", -2, "0 Slashing"),
    ],
)
def test_a_weapons_damage(die, bonus, damage):
    option = _weapon_option(_weapon(die, bonus))
    assert option.damage == damage
    assert option.roll == ATTACK_ROLL
    assert option.bonus == 5
    assert option.action_cost == "Action"


def test_a_weapons_extra_damage_counts_unless_it_waits_on_something():
    always = ExtraDamage(
        WeaponDamageRolls.D6x2, WeaponDamageTypes.FIRE, "magical flames"
    )
    chosen = ExtraDamage(
        WeaponDamageRolls.D6,
        WeaponDamageTypes.COLD,
        "chosen type, activate as bonus action",
    )
    option = _weapon_option(_weapon("1d8", 4, [always, chosen]))
    assert option.damage == "1d8 + 4 Slashing + 2d6 Fire"
    assert "1d6 Cold" in option.note


def test_a_weapons_damage_reads_and_doubles_on_a_critical(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda low, high: 3)
    option = _weapon_option(
        _weapon("1d8", 4, [ExtraDamage(WeaponDamageRolls.D6x2, WeaponDamageTypes.FIRE)])
    )
    assert read_damage(option.damage) == ([(7, "Slashing"), (6, "Fire")], "")
    assert read_damage(option.damage, critical=True) == (
        [(10, "Slashing"), (12, "Fire")],
        "",
    )
    unarmed = _weapon_option(_weapon("1d1", 3))
    assert read_damage(unarmed.damage, critical=True) == ([(4, "Slashing")], "")


def test_a_players_weapon_matches_the_sheet():
    edmund = combatant_from_character(Edmund().build())
    sheet = edmund["_stat_block"]
    longsword = next(w for w in edmund["_weapons_objects"] if w.name == "Longsword")
    option = next(
        o for o in dict(effect_options(edmund, []))["Attacks"] if o.name == "Longsword"
    )
    die = longsword.get_damage_roll(sheet).value
    bonus = longsword.calculate_damage_bonus_int(sheet)
    assert option.bonus == longsword.calculate_total_attack_roll_bonus_int(sheet)
    assert option.damage == f"{die} + {bonus} Slashing"


def test_a_features_uses_show_and_running_out_is_said():
    edmund = combatant_from_character(Edmund().build())
    divinity = next(
        o
        for o in dict(effect_options(edmund, []))[FEATURES]
        if o.name == "Channel Divinity"
    )
    assert divinity.counts_uses
    assert divinity.row_text.startswith("Channel Divinity  2/2")
    edmund["feature_uses_used"] = {"Channel Divinity": 2}
    spent = next(
        o
        for o in dict(effect_options(edmund, []))[FEATURES]
        if o.name == "Channel Divinity"
    )
    assert spent.row_text.startswith("Channel Divinity  0/2")
    assert "No uses left" in spent.note
    assert not spent.is_unavailable  # still the GM's to pick


# ---------------------------------------------------------------------------
# The categories


def test_a_players_categories():
    edmund = combatant_from_character(Edmund().build())
    titles = [title for title, _ in effect_options(edmund)]
    assert titles == ["Attacks", "Edmund's Spells", FEATURES, ALL_SPELLS]
    all_spells = dict(effect_options(edmund))[ALL_SPELLS]
    assert "Bless" not in {o.name for o in all_spells}  # Edmund's own
    assert "Fireball" in {o.name for o in all_spells}


def test_a_monsters_categories_and_an_empty_one_left_out():
    titles = [
        title for title, _ in effect_options({"actions": [SLASH], "reactions": []})
    ]
    assert titles == ["Actions", ALL_SPELLS]


# ---------------------------------------------------------------------------
# What review found (each from the stat block's or spell's own text)


def _monster_option(combatant, name: str):
    options = effect_options(combatant_from_stat_block(combatant), [])
    return next(o for _, section in options for o in section if o.name == name)


def test_a_hits_save_doesnt_give_its_condition_on_the_hit():
    """Ghoul's Claw: "Hit: 4 (1d4 + 2) Slashing damage. If the target is a
    creature that isn't an Undead or elf, ... Constitution Saving Throw: DC 10.
    Failure: The target has the Paralyzed condition". Only a failed save
    paralyzes, so the hit doesn't, and the GM is told to apply the save."""
    claw = _monster_option(Ghoul(), "Claw")
    assert claw.roll == ATTACK_ROLL
    assert claw.damage == "1d4 + 2 Slashing"
    assert claw.condition == ""
    assert "Constitution save" in claw.note


def test_a_hits_own_condition_stays():
    bite = {
        "name": "Bite",
        "description": "Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d10 + 2) Piercing"
        " damage, and the target has the Grappled condition (escape DC 13).",
    }
    (option,) = dict(effect_options({"actions": [bite]}, []))["Actions"]
    assert option.condition == "Grappled"


@pytest.mark.parametrize(
    "monster, name, condition, until",
    [
        # "has the Paralyzed condition until the start of the lich's next turn"
        (Lich, "Paralyzing Touch", "Paralyzed", ("start", "source")),
        # "has the Stunned condition until the end of the mind flayer's next turn"
        (MindFlayer, "Mind Blast (Recharge 5–6)", "Stunned", ("end", "source")),
    ],
)
def test_a_monsters_condition_lasts_till_a_turn(monster, name, condition, until):
    option = _monster_option(monster(), name)
    assert option.condition == condition
    assert option.until == until


def test_its_next_turn_is_the_targets():
    gaze = {
        "name": "Gaze",
        "description": "Wisdom Saving Throw: DC 12, one creature. Failure: The target"
        " has the Frightened condition until the end of its next turn.",
    }
    (option,) = dict(effect_options({"actions": [gaze]}, []))["Actions"]
    assert option.until == ("end", "target")


@pytest.mark.parametrize(
    "name, condition, until",
    [
        # "has the Blinded condition until the end of your next turn"
        ("Color Spray", "Blinded", ("end", "source")),
        # "has the Incapacitated condition until the end of its next turn"
        ("Sleep", "Incapacitated", ("end", "target")),
    ],
)
def test_a_spells_condition_lasts_till_a_turn(name, condition, until):
    option = _option(name)
    assert option.condition == condition
    assert option.until == until


def test_hold_person_lasts_its_minute():
    assert _option("Hold Person").until is None


def test_a_condition_only_in_one_option_isnt_filled():
    """Command: only "Grovel. The target has the Prone condition"."""
    command = _option("Command")
    assert command.ability == "WIS"
    assert command.condition == ""
    assert "Prone only with one of its options (Grovel)" in command.note


def test_a_condition_a_spell_cures_isnt_a_note():
    """Dispel Evil and Good's Break Enchantment ends Charmed on "a creature that
    is possessed by or has the Charmed or Frightened condition"."""
    assert "Charmed" not in _option("Dispel Evil and Good").note


@pytest.mark.parametrize(
    "name", ["Magic Missile", "Divine Smite", "Cure Wounds", "Healing Word", "Gust"]
)
def test_no_name_badge_for_damage_healing_or_an_instant(name):
    """Magic Missile's and Divine Smite's damage is typed in by hand, Cure Wounds
    and Healing Word heal, and Gust is Instantaneous: a badge would be left over."""
    assert _option(name).condition == ""


def test_the_badge_stays_for_a_spell_that_lasts():
    assert _option("Bless").condition == "Bless"


def test_a_weapon_costs_the_action_only_if_it_isnt_used():
    """Extra Attack fits more attacks in one Attack action, and an Opportunity
    Attack is a Reaction."""
    edmund = combatant_from_character(Edmund().build())

    def longsword():
        attacks = dict(effect_options(edmund, []))["Attacks"]
        return next(o for o in attacks if o.name == "Longsword")

    assert longsword().action_cost == "Action"
    edmund["action_uses"] = {"Action": 1}
    assert longsword().action_cost is None


@pytest.mark.parametrize(
    "counts_uses, action_cost, tracked",
    [(False, None, False), (True, None, True), (False, "Bonus Action", True)],
)
def test_only_a_feature_thats_used_can_be_applied_by_itself(
    counts_uses, action_cost, tracked
):
    """Tough or Darkvision is always on: there's nothing to spend."""
    option = EffectOption(
        "Feature", FEATURE, counts_uses=counts_uses, action_cost=action_cost
    )
    assert option.is_tracked is tracked


# ---------------------------------------------------------------------------
# Hit Points a spell gives, read from its text: they fill the amount box


@pytest.mark.parametrize(
    "name, kind, amount, at_slot",
    [
        # "regain Hit Points equal to 2d4 plus your spellcasting ability modifier"
        ("Mass Healing Word", HEALING, "2d4", {3: "2d4"}),
        # "regain 2d8 Hit Points"; "The healing increases by 1d8" above 2
        ("Prayer of Healing", HEALING, "2d8", {3: "3d8"}),
        ("Regenerate", HEALING, "4d8 + 15", {}),
        # "You gain 5 Temporary Hit Points"; they "increase by 5" above 1
        ("Armor of Agathys", TEMP_HP, "5", {3: "5 + 10"}),
    ],
)
def test_hit_points_from_the_text(name, kind, amount, at_slot):
    option = spell_option(_spell(name), {})
    assert not option.is_described
    assert (option.amount_kind, option.damage) == (kind, amount)
    for slot, expected in at_slot.items():
        assert option.damage_at(slot) == expected


@pytest.mark.parametrize(
    "name",
    [
        "Chill Touch",  # "can't regain Hit Points"
        "Aura of Life",  # "regains 1 Hit Point", a rider on later turns
        "Heroism",  # "equal to your spellcasting ability modifier", each turn
    ],
)
def test_hit_points_that_arent_given_now(name):
    option = spell_option(_spell(name), {})
    assert option.amount_kind == DAMAGE_AMOUNT
    assert not any(roll.damage_type is None for roll in option.rolls)


def test_damage_stays_in_the_box_and_hit_points_become_a_note():
    """Conjure Constructs deals 3d6 Force damage and gives the target 1d6 +
    the modifier Temporary Hit Points: one amount box, so the damage."""
    option = spell_option(_spell("Conjure Constructs"), CASTER)
    assert option.amount_kind == DAMAGE_AMOUNT
    assert "Force" in option.damage
    assert "It also gives 1d6" in option.note and "Temporary Hit Points" in option.note


def test_the_casters_own_temporary_hit_points():
    """Armor of Agathys: "You gain 5 Temporary Hit Points"."""
    option = spell_option(_spell("Armor of Agathys"), {})
    assert "pick the caster as the target" in option.note


def test_a_creatures_healing_is_a_targets():
    """Cure Wounds: "A creature you touch regains ..."."""
    assert "caster as the target" not in spell_option(_spell("Cure Wounds"), {}).note
