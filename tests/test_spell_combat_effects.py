"""Spells' combat effects - Model/Content/CombatEffect.py's CombatEffect, in a
spell's class (CharacterContent/Spells/SpellClasses; every spell is one) - and how
the combat UI's Custom Effect picker fills its form from them instead of
reading the spell's text.

Expected values come from each spell's 2024 rules text, read by hand: Fireball
is a Dexterity save for 8d6 Fire, half on a success, 1d6 more per slot level
above 3; Toll the Dead is 1d8 Necrotic, 3d8 from character level 11; and so on.
"""

import re

import pytest

from CharacterContent.Spells.SpellFactory import DataSpell, SpellFactory
from Combat.CombatUIQt.effect_options import (
    ALL_SPELLS,
    effect_options,
    is_applicable,
    read_effect_text,
    spell_option,
    spell_options,
)
from Combat.CombatUIQt.saves import ATTACK_ROLL, HEALING, SAVING_THROW, TEMP_HP
from Core.Definitions import Ability, Condition, DamageType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    CombatInstances,
    EffectRoll,
    TurnEdge,
    TurnOf,
)

# A monster whose Spellcasting says its numbers.
CASTER = {
    "name": "Cultist",
    "actions": [
        {
            "name": "Spellcasting",
            "description": "It casts a spell (spell save DC 15, +7 to hit with spell attacks).",
        }
    ],
}


def _option(name: str, char: dict | None = None):
    return spell_option(SpellFactory.create(name), CASTER if char is None else char)


# ---------------------------------------------------------------------------
# The data files


def _all_described() -> list[str]:
    """Every spell with combat effects (in its class)."""
    return sorted(
        spell.name
        for spell in SpellFactory.all_spells()
        if spell.combat_effects() is not None
    )


def _effects(spell) -> list[CombatEffect]:
    effects = spell.combat_effects()
    assert effects is not None, f"{spell.name} isn't described"
    return effects


def test_there_are_described_spells():
    assert len(_all_described()) >= 50


@pytest.mark.parametrize("name", _all_described())
def test_only_cantrips_scale_with_character_level(name):
    spell = SpellFactory.create(name)
    for effect in _effects(spell):
        for damage in effect.damage:
            if spell.level == 0:
                assert not damage.upcast, name
            else:
                assert not damage.cantrip, name


@pytest.mark.parametrize("name", _all_described())
def test_a_condition_is_a_rules_condition_or_the_spells_own_badge(name):
    rules = {condition.value for condition in Condition}
    for effect in _effects(SpellFactory.create(name)):
        for condition in effect.conditions:
            assert condition.name in rules | {name}


# ---------------------------------------------------------------------------
# Reading an entry


def test_a_full_entry():
    effect = CombatEffect.from_dict(
        {
            "roll": "save",
            "save_ability": "Dexterity",
            "half_on_success": True,
            "repeat_save": True,
            "damage": [
                {
                    "dice": "1d8",
                    "damage_type": "Necrotic",
                    "cantrip": {"5": "2d8", "11": "3d8", "17": "4d8"},
                },
                {
                    "dice": "3d8",
                    "damage_type": None,
                    "choices": ["Acid", "Fire"],
                    "upcast": "1d8",
                    "add_modifier": True,
                },
            ],
            "conditions": [
                {"name": "Poisoned", "until": ["end", "source"]},
                {"name": "Prone"},
            ],
            "instances": {"count": 3, "upcast": 1, "noun": "ray"},
            "notes": ["A note."],
        },
        "spell 'Test'",
    )
    assert effect.save_ability is Ability.DEXTERITY
    assert effect.half_on_success and effect.repeat_save
    assert effect.damage[0].cantrip == ((5, "2d8"), (11, "3d8"), (17, "4d8"))
    assert effect.damage[1] == CombatDamage(
        "3d8",
        None,
        (DamageType.ACID, DamageType.FIRE),
        upcast="1d8",
        add_modifier=True,
    )
    assert effect.conditions == (
        CombatCondition("Poisoned", until=(TurnEdge.END, TurnOf.SOURCE)),
        CombatCondition("Prone"),
    )
    assert effect.instances == CombatInstances(3, upcast=1, noun="ray")
    assert effect.notes == ("A note.",)


def test_one_condition_as_older_logs_have_it_still_reads():
    effect = CombatEffect.from_dict({"condition": {"name": "Prone"}})
    assert effect.conditions == (CombatCondition("Prone"),)
    assert "condition" not in effect.to_dict()


def test_instances_grow_by_slot_and_character_level():
    rays = CombatInstances(3, upcast=1, noun="ray")
    assert (rays.at(1, 0), rays.at(1, 2)) == (3, 5)
    beams = CombatInstances(1, cantrip=((5, 2), (11, 3), (17, 4)), noun="beam")
    assert [beams.at(level, 0) for level in (4, 5, 11, 17)] == [1, 2, 3, 4]


def test_to_dict_leaves_out_the_defaults():
    steps = ((5, "2d8"), (11, "3d8"), (17, "4d8"))
    effect = CombatEffect(
        roll=EffectRoll.SAVE,
        save_ability=Ability.WISDOM,
        damage=(CombatDamage("1d8", DamageType.NECROTIC, cantrip=steps),),
    )
    assert effect.to_dict() == {
        "roll": "save",
        "save_ability": "Wisdom",
        "damage": [
            {
                "dice": "1d8",
                "damage_type": "Necrotic",
                "cantrip": {"5": "2d8", "11": "3d8", "17": "4d8"},
            }
        ],
    }
    assert CombatEffect().to_dict() == {}
    assert CombatEffect.from_dict(effect.to_dict()) == effect


def test_an_empty_effect_just_happens():
    effect = CombatEffect.from_dict({})
    assert effect == CombatEffect()
    assert effect.roll == "none"
    assert effect.conditions == ()


@pytest.mark.parametrize(
    "entry, field",
    [
        ({"roll": "save"}, "effect"),  # a save with no ability
        ({"roll": "attack", "save_ability": "Dexterity"}, "effect"),
        ({"roll": "save", "save_ability": "DEX"}, "save_ability"),
        ({"roll": "check"}, "roll"),
        (
            {"damage": [{"dice": "8d6", "damage_type": "Flame"}]},
            "damage[0].damage_type",
        ),
        ({"damage": [{"dice": "eight d6", "damage_type": "Fire"}]}, "damage[0]"),
        ({"damage": [{"dice": "3d8", "damage_type": None}]}, "damage[0]"),
        (
            {
                "damage": [
                    {"dice": "3d8", "damage_type": "Fire", "choices": ["Acid", "Fire"]}
                ]
            },
            "damage[0]",
        ),
        (
            {
                "damage": [
                    {"dice": "1d8", "damage_type": "Fire", "cantrip": {"5": "2d8"}}
                ]
            },
            "damage[0]",
        ),
        ({"conditions": [{"name": ""}]}, "conditions[0]"),
        ({"conditions": [{"name": "Prone", "until": ["end"]}]}, "conditions[0].until"),
        ({"conditions": [{"name": "Prone"}, {"name": "Prone"}]}, "effect"),
        ({"conditions": {"name": "Prone"}}, "conditions"),
        ({"instances": {"count": 0}}, "instances"),
        ({"instances": {"count": 2, "cantrip": {"5": "2"}}}, "instances.cantrip"),
        ({"concentration": "yes"}, "concentration"),
        ({"dc": True}, "dc"),
        ({"notes": "one note"}, "notes"),
        ({"halfOnSave": True}, "effect"),  # a key the model doesn't have
        ({"healing": {"dice": "1d4"}, "temp_hp": {"dice": "1d4"}}, "effect"),
        ({"healing": {"dice": "lots"}}, "healing"),
    ],
)
def test_a_wrong_entry_names_the_spell_and_field(entry, field):
    with pytest.raises(ValueError, match=re.escape(f"of spell 'Test', {field}:")):
        CombatEffect.from_dict(entry, "spell 'Test'")


def test_hit_points_can_upcast_by_a_number():
    """False Life's "5 additional Temporary Hit Points" and Heal's "The
    healing increases by 10" per slot level."""
    assert CombatHitPoints("5", upcast="5").upcast == "5"
    assert CombatHitPoints("70", upcast="10").upcast == "10"
    with pytest.raises(ValueError):
        CombatHitPoints("1d4", upcast="lots")


# ---------------------------------------------------------------------------
# Loading


def _unchecked_spell():
    """A spell with no entry yet: the first, by name, of those left."""
    return next(
        spell
        for spell in sorted(SpellFactory.all_spells(), key=lambda s: s.name)
        if spell.name not in _all_described()
    )


def test_a_spell_without_an_entry_is_not_described():
    assert _unchecked_spell().combat_effects() is None


def test_a_scraped_record_has_no_combat_effects():
    """A record is only the scraped rules: a spell's effects are in its
    class, so a record read on its own (a spell scraped and not converted
    yet) is read from its text."""
    record = DataSpell(SpellFactory._load_json()["Fireball"])
    assert record.combat_effects() is None
    assert SpellFactory.create("Fireball").combat_effects()


# ---------------------------------------------------------------------------
# The Custom Effect picker


def test_fireball():
    fireball = _option("Fireball")
    assert fireball.is_curated
    assert fireball.roll == SAVING_THROW
    assert fireball.ability == "DEX"
    assert fireball.dc == 15
    assert fireball.half_on_save
    assert fireball.damage == "8d6 Fire"
    assert fireball.damage_at(5) == "10d6 Fire"
    assert fireball.note == ""


def test_hold_person():
    hold = _option("Hold Person")
    assert hold.ability == "WIS"
    assert hold.condition == "Paralyzed"
    assert hold.repeat_save
    assert hold.concentration
    assert hold.damage == ""
    assert "Humanoids" in hold.note


def test_guiding_bolt_is_an_attack():
    bolt = _option("Guiding Bolt")
    assert bolt.roll == ATTACK_ROLL
    assert bolt.bonus == 7
    assert bolt.ability is None
    assert bolt.damage_at(3) == "6d6 Radiant"


def test_ray_of_sickness_poisons_until_the_end_of_the_casters_next_turn():
    ray = _option("Ray of Sickness")
    assert ray.roll == ATTACK_ROLL
    assert ray.condition == "Poisoned"
    assert ray.until == ("end", "source")


def test_sleep_incapacitates_until_the_end_of_the_targets_next_turn():
    sleep = _option("Sleep")
    assert sleep.condition == "Incapacitated"
    assert sleep.until == ("end", "target")
    assert not sleep.repeat_save  # its second save is a different one
    assert "Unconscious" in sleep.note


def test_only_the_part_that_grows_is_upcast():
    storm = _option("Ice Storm")
    assert storm.damage == "2d10 Bludgeoning + 4d6 Cold"
    assert storm.damage_at(6) == "4d10 Bludgeoning + 4d6 Cold"


def test_a_type_to_choose_is_left_to_the_gm():
    orb = _option("Chromatic Orb")
    assert orb.damage == "3d8"
    assert "Acid, Cold, Fire, Lightning, Poison, Thunder" in orb.note


@pytest.mark.parametrize(
    "level, damage",
    [
        (4, "1d8 Necrotic"),
        (5, "2d8 Necrotic"),
        (11, "3d8 Necrotic"),
        (17, "4d8 Necrotic"),
    ],
)
def test_a_cantrip_grows_with_the_characters_level(level, damage):
    caster = dict(CASTER, class_levels={"Cleric": level})
    assert _option("Toll the Dead", caster).damage == damage


def test_a_monsters_cantrip_stays_as_it_is():
    assert _option("Toll the Dead").damage == "1d8 Necrotic"


def test_the_modifier_is_added_when_known_and_asked_for_when_not():
    weapon = _option("Spiritual Weapon")
    assert weapon.damage == "1d8 Force"
    assert "modifier" in weapon.note


def test_healing_fills_the_amount_box():
    """Cure Wounds: 2d8 plus the modifier, 2d8 more per slot level above 1.
    This caster's modifier isn't known, so the note says to add it."""
    cure = _option("Cure Wounds")
    assert cure.amount_kind == HEALING
    assert cure.damage == "2d8"
    assert cure.damage_at(3) == "6d8"
    assert cure.ability is None
    assert cure.condition == ""  # no badge for healing
    assert cure.summary == "heals 2d8"
    assert "Add the spellcasting ability modifier to the healing." in cure.note


def test_a_spell_with_nothing_to_roll_can_be_its_own_badge():
    bless = _option("Bless")
    assert bless.condition == "Bless"
    assert bless.summary == ""  # its own name says nothing more in its row
    assert "1d4" in bless.note


def test_a_spell_has_no_badge_unless_it_says_so():
    assert _option("Alarm").condition == ""
    assert _option("Spike Growth").condition == ""


def test_a_spell_with_two_steps_has_a_row_for_each():
    """Ice Knife: an attack for 1d10 Piercing, then, hit or miss, a DEX save
    for 2d6 Cold (1d6 more per slot level above 1), all one casting. Read
    from its text it was one row that said so in a note."""
    shard, burst = spell_options(SpellFactory.create("Ice Knife"), CASTER)
    assert (shard.name, shard.roll, shard.damage) == (
        "Ice Knife: shard",
        ATTACK_ROLL,
        "1d10 Piercing",
    )
    assert shard.counts_uses and shard.action_cost == "Action"
    assert (burst.name, burst.ability, burst.damage_at(3)) == (
        "Ice Knife: explosion",
        "DEX",
        "4d6 Cold",
    )
    # Part of the same casting: no slot, no action, no cast counted.
    assert not burst.counts_uses
    assert (burst.slot_level, burst.action_cost) == (None, None)
    assert shard.spell_name == burst.spell_name == "Ice Knife"


def test_command_has_a_row_per_option():
    rows = spell_options(SpellFactory.create("Command"), CASTER)
    assert [row.name for row in rows] == [
        "Command: Approach",
        "Command: Drop",
        "Command: Flee",
        "Command: Grovel",
        "Command: Halt",
    ]
    grovel, halt = rows[3], rows[4]
    assert (grovel.ability, grovel.condition) == ("WIS", "Prone")
    # The others mark the target until the end of its next turn.
    assert (halt.condition, halt.until) == ("Command", ("end", "target"))


def test_toll_the_dead_has_a_row_for_a_hurt_target():
    caster = dict(CASTER, class_levels={"Cleric": 5})
    whole, hurt = spell_options(SpellFactory.create("Toll the Dead"), caster)
    assert (whole.damage, hurt.damage) == ("2d8 Necrotic", "2d12 Necrotic")


@pytest.mark.parametrize("slot, rays", [(None, 3), (2, 3), (3, 4), (5, 6)])
def test_scorching_ray_has_three_rays_and_one_more_per_slot_level(slot, rays):
    ray = _option("Scorching Ray")
    assert ray.damage == "2d6 Fire"  # each ray
    assert ray.instances_at(slot) == rays
    assert "3 rays" in ray.summary


@pytest.mark.parametrize("level, beams", [(1, 1), (5, 2), (11, 3), (17, 4)])
def test_eldritch_blast_has_more_beams_at_higher_levels(level, beams):
    blast = _option("Eldritch Blast", dict(CASTER, class_levels={"Warlock": level}))
    assert blast.instances_at(None) == beams
    assert blast.damage == "1d10 Force"


def test_magic_missile_darts_hit_without_a_roll():
    darts = _option("Magic Missile")
    assert (darts.ability, darts.roll, darts.damage) == (
        None,
        SAVING_THROW,
        "1d4 + 1 Force",
    )
    assert (darts.instances_at(1), darts.instances_at(4)) == (3, 6)


def test_divine_smite_against_a_fiend_or_undead_is_a_note():
    """2d8 Radiant, 1d8 more per slot level above 1, and 1d8 more if the
    target is a Fiend or an Undead."""
    smite = _option("Divine Smite")
    assert smite.damage == "2d8 Radiant"
    assert smite.damage_at(2) == "3d8 Radiant"
    assert "If the target is a Fiend or an Undead: 1d8 Radiant more." in smite.note


def test_chill_touch_marks_its_target_until_the_end_of_the_casters_turn():
    touch = _option("Chill Touch")
    assert (touch.roll, touch.damage) == (ATTACK_ROLL, "1d10 Necrotic")
    assert (touch.condition, touch.until) == ("Chill Touch", ("end", "source"))


def test_a_spell_without_an_entry_is_read_from_its_text():
    spell = _unchecked_spell()
    option = spell_option(spell, CASTER)
    assert not option.is_curated
    assert option.ability == read_effect_text(spell.description).ability


def test_a_spell_with_nothing_to_apply_is_left_out_of_all_spells():
    assert not is_applicable(SpellFactory.create("Alarm"))
    assert is_applicable(SpellFactory.create("Fireball"))
    assert is_applicable(_unchecked_spell())
    names = {option.name for option in dict(effect_options(CASTER))[ALL_SPELLS]}
    assert "Alarm" not in names
    assert "Fireball" in names


def test_a_casters_own_spell_with_nothing_to_apply_is_still_listed():
    """Picking it still spends the slot and the action."""
    alarm = SpellFactory.create("Alarm")
    caster = dict(CASTER, _spell_objects={"Alarm": alarm})
    options = dict(effect_options(caster, all_spells=[]))
    (row,) = options["Cultist's Spells"]
    assert row.name == "Alarm"
    assert (row.roll, row.ability, row.damage, row.condition) == (
        SAVING_THROW,
        None,
        "",
        "",
    )
    assert row.spell_level == 1


# ---------------------------------------------------------------------------
# What the text reading got wrong, fixed by an entry


def test_hunters_mark_is_a_badge_not_damage_to_fill_in():
    mark = _option("Hunter's Mark")
    assert mark.condition == "Hunter's Mark"
    assert mark.damage == ""
    assert "1d6 Force" in mark.note


def test_hideous_laughter_gives_prone_and_incapacitated():
    laughter = _option("Tasha's Hideous Laughter")
    assert laughter.ability == "WIS"
    assert laughter.condition == "Incapacitated + Prone"
    assert laughter.repeat_save


def test_true_strike_is_a_weapon_attack():
    strike = _option("True Strike")
    assert strike.roll == ATTACK_ROLL
    assert strike.damage == ""
    assert "weapon" in strike.note


def test_healing_word_heals_with_the_modifier():
    """2d4 plus the spellcasting ability modifier: Thomas's Charisma."""
    from Builds.Characters.Y2024_Bard_Valor_Thomas import (
        Y2024BardValorThomasCharacterBuilder as Thomas,
    )
    from Combat.PlayerCombatant import combatant_from_character

    sheet = Thomas().build()
    word = _option("Healing Word", combatant_from_character(sheet))
    assert word.damage == f"2d4 + {sheet.get_charisma_modifier()}"
    assert word.note == ""


def test_false_life_gives_temporary_hit_points():
    """2d4 + 4 Temporary Hit Points, 5 more per slot level above 1, to the
    caster."""
    life = _option("False Life")
    assert life.amount_kind == TEMP_HP
    assert life.damage == "2d4 + 4"
    assert life.damage_at(3) == "2d4 + 4 + 10"
    assert "the caster as the target" in life.note


def test_an_entry_in_a_2014_file():
    """Absorb Elements is only in the 2014 data; its class (converted from
    that record) has the effect."""
    absorb = _option("Absorb Elements")
    assert absorb.is_curated
    assert absorb.damage == ""
    assert "Resistance" in absorb.note
