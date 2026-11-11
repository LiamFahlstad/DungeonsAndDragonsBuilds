"""What a lasting effect changes on its bearer while it's on (plan Phase 7,
steps 7.1 to 7.5): its AC worked out from a new base (Mage Armor) or kept
at a floor (Barkskin) beside what adds to it (Shield of Faith, cover), and
damage Immunity and Vulnerability beside Resistance (Stoneskin, Protection
from Energy, Rage). Expected values come from the 2024 rules text: Mage
Armor ("the target's base AC becomes 13 plus its Dexterity modifier"),
Barkskin ("the target has an Armor Class of 17 if its AC is lower than
that"), Shield of Faith ("a +2 bonus to AC"), Rage ("Resistance to
Bludgeoning, Piercing, and Slashing damage", "Advantage on Strength checks
and Strength saving throws") and the Rules Glossary: Combining Game Effects
(the same effect twice doesn't add up), Cover (+2 / +5 to AC) and Damage
Resistance and Vulnerability (Resistance halves, then Vulnerability
doubles; Immunity takes none)."""

import random
from typing import Any

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import Rage
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.player_view import note_damage_defense
from Combat.PlayerLog import is_round_key
from Combat.CombatUIQt.saves import CustomEffect
from Combat.Effects.active_effects import KEY, give_modifiers, new_effect
from Combat.CombatUIQt.attack_rolls import armor_text
from Combat.Effects.modifiers import (
    armor_class,
    armor_class_bonus,
    armor_class_notes,
    armor_class_text,
    defenses_from_modifiers,
    hit_point_maximum,
    hit_point_maximum_text,
    immune_to_damage,
    resists,
    rolled_modifiers,
    save_plan,
    size_in_use,
    size_text,
    speed_changes,
    speed_in_use,
    vulnerable_to,
)
from Combat.CombatUIQt.dialogs_mixin import _speed_text
from Combat.CombatUIQt.player_view import _unit_details
from Combat.Effects.triggers import AttackOutcome, TriggerRow, outcome_firings
from Core.Definitions import Ability, Condition, CreatureSize, DamageType
from Model.Content.CombatEffect import CombatEffect, TurnEdge, TurnOf
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from Model.Content.CombatModifiers import (
    ArmorClass,
    ArmorClassBase,
    ArmorClassMinimum,
    ConditionImmunity,
    DamageImmunity,
    HitPointMaximum,
    Note,
    Resistance,
    Size,
    Speed,
    Vulnerability,
    modifier_from_dict,
    modifier_to_dict,
)
from Model.Creatures.Combatants import Visibility
from tests._combat_ui import make_ui

MAGE_ARMOR = ArmorClassBase(13, (Ability.DEXTERITY,))
BARKSKIN = ArmorClassMinimum(17)
SHIELD_OF_FAITH = ArmorClass(2)
HALF = Visibility.HALF_COVER.value
FIRE, POISON, SLASHING = (
    DamageType.FIRE.value,
    DamageType.POISON.value,
    DamageType.SLASHING.value,
)


def _with(badges: dict, **keys: Any) -> dict:
    """A combatant (the Tiger) with each badge in `badges` giving its
    modifiers, and `keys` too."""
    char = {"name": "Tiger", "conditions": list(badges), **keys}
    for badge, modifiers in badges.items():
        give_modifiers(char, badge, modifiers)
    return char


def _effects(spell: str) -> list[CombatEffect]:
    effects = SpellFactory.create(spell).combat_effects()
    assert effects is not None, f"{spell} has no combat effects"
    return effects


def _badge_modifiers(effect) -> tuple:
    (condition,) = effect.conditions
    return condition.modifiers


# ---------------------------------------------------------------------------
# The new modifiers as plain data
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "modifier, data",
    [
        (
            MAGE_ARMOR,
            {"type": "ArmorClassBase", "base": 13, "abilities": ["Dexterity"]},
        ),
        (BARKSKIN, {"type": "ArmorClassMinimum", "value": 17}),
        (
            DamageImmunity((DamageType.POISON,)),
            {"type": "DamageImmunity", "damage_types": ["Poison"]},
        ),
        (Vulnerability(), {"type": "Vulnerability"}),
    ],
)
def test_the_new_modifiers_read_back_as_written(modifier, data):
    written = modifier_to_dict(modifier)
    assert modifier_from_dict(written) == modifier
    assert written == data


@pytest.mark.parametrize(
    "data",
    [
        {"type": "ArmorClassBase", "base": "13"},
        {"type": "ArmorClassBase", "base": True},
        {"type": "ArmorClassMinimum"},
        {"type": "ArmorClassMinimum", "value": 17, "bonus": 2},
        {"type": "Vulnerability", "damage_types": ["Sonic"]},
    ],
)
def test_a_malformed_one_is_refused(data):
    with pytest.raises(ValueError, match="Invalid modifier"):
        modifier_from_dict(data, "a test")


@pytest.mark.parametrize("value", ["17", 17.0, None])
def test_a_floor_or_base_is_a_whole_number(value):
    with pytest.raises(ValueError, match="whole number"):
        ArmorClassMinimum(value)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="whole number"):
        ArmorClassBase(value)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 7.1: the AC in use
# ---------------------------------------------------------------------------


def test_mage_armor_gives_13_plus_dex_when_that_is_better():
    """DEX 16 is +3: a creature with AC 12 has 16, one in plate (18) keeps 18."""
    scores = {"Ability Scores": {"DEX": 16}}
    assert armor_class(_with({"Mage Armor": (MAGE_ARMOR,)}, **scores), 12) == 16
    assert armor_class(_with({"Mage Armor": (MAGE_ARMOR,)}, **scores), 18) == 18


def test_mage_armor_without_ability_scores_counts_no_modifier():
    assert armor_class(_with({"Mage Armor": (MAGE_ARMOR,)}), 10) == 13


def test_barkskin_is_a_floor_not_a_bonus():
    """AC 13 becomes 17; Shield of Faith's +2 on 13 is 15, still under 17;
    on 16 it is 18, above it."""
    assert armor_class(_with({"Barkskin": (BARKSKIN,)}), 13) == 17
    both = _with({"Barkskin": (BARKSKIN,), "Shield of Faith": (SHIELD_OF_FAITH,)})
    assert armor_class(both, 13) == 17
    assert armor_class(both, 16) == 18
    assert armor_class(_with({"Barkskin": (BARKSKIN,)}), 19) == 19


def test_cover_adds_to_whatever_the_ac_is():
    char = _with({"Barkskin": (BARKSKIN,)}, visibility_states=[HALF])
    assert armor_class(char, 13) == 19


def test_mage_armor_and_shield_of_faith_add_up():
    char = _with(
        {"Mage Armor": (MAGE_ARMOR,), "Shield of Faith": (SHIELD_OF_FAITH,)},
        **{"Ability Scores": {"DEX": 14}},
    )
    assert armor_class(char, 11) == 17  # 13 + 2, then + 2


def test_the_same_effect_twice_doesnt_add_up():
    """Two records of Shield of Faith (two casters) give +2, not +4."""
    char = {"name": "Tiger", "conditions": ["Shield of Faith"]}
    for _ in range(2):
        effect = new_effect("Shield of Faith")
        effect["modifiers"] = [modifier_to_dict(SHIELD_OF_FAITH)]
        char.setdefault(KEY, []).append(effect)
    assert armor_class(char, 15) == 17


def test_the_bonus_is_what_the_modifiers_add_to_the_stored_ac():
    """What the players' known-AC notes take off a roll (note_attack_roll)."""
    char = _with({"Barkskin": (BARKSKIN,)}, visibility_states=[HALF])
    assert armor_class_bonus(char, 13) == 6
    assert armor_class_bonus(char) == 2, "with no AC, only what adds to one"


def test_a_badge_that_is_off_changes_nothing():
    char = _with({"Barkskin": (BARKSKIN,)})
    char["conditions"].remove("Barkskin")
    assert armor_class(char, 13) == 13


def test_the_dialog_notes_say_what_changes_the_ac():
    char = _with(
        {
            "Mage Armor": (MAGE_ARMOR,),
            "Barkskin": (BARKSKIN,),
            "Shield of Faith": (SHIELD_OF_FAITH,),
        },
        visibility_states=[HALF],
    )
    assert armor_class_notes(char) == [
        "Mage Armor: base AC 13 + DEX",
        "Barkskin: AC at least 17",
        "Shield of Faith: +2 AC",
    ]


def test_the_spells_give_these_badges():
    (mage_armor,) = _effects("Mage Armor")
    assert _badge_modifiers(mage_armor) == (MAGE_ARMOR,)
    (barkskin,) = _effects("Barkskin")
    assert _badge_modifiers(barkskin) == (BARKSKIN,)


# ---------------------------------------------------------------------------
# 7.2: Immunity and Vulnerability beside Resistance
# ---------------------------------------------------------------------------


def test_immunity_and_vulnerability_from_a_badge():
    char = _with(
        {
            "Warded": (DamageImmunity((DamageType.POISON,)),),
            "Cursed": (Vulnerability((DamageType.FIRE,)),),
        }
    )
    assert immune_to_damage(char, POISON) and not immune_to_damage(char, FIRE)
    assert vulnerable_to(char, FIRE) and not vulnerable_to(char, POISON)
    assert vulnerable_to(_with({"Doom": (Vulnerability(),)}), SLASHING)


def test_stoneskin_and_protection_from_energy_resist_their_types():
    (stoneskin,) = _effects("Stoneskin")
    char = _with({"Stoneskin": _badge_modifiers(stoneskin)})
    assert all(resists(char, t) for t in ("Bludgeoning", "Piercing", "Slashing"))
    assert not resists(char, FIRE)
    rows = _effects("Protection from Energy")
    assert [row.name for row in rows] == [
        f"Protection from Energy: {t}"
        for t in ("Acid", "Cold", "Fire", "Lightning", "Thunder")
    ]
    fire = _with({"Protection from Energy": _badge_modifiers(rows[2])})
    assert resists(fire, FIRE) and not resists(fire, "Cold")


def test_shield_gives_its_caster_5_ac_until_its_next_turn():
    """Shield: "Until the start of your next turn, you have a +5 bonus to AC"."""
    (shield,) = _effects("Shield")
    (condition,) = shield.conditions
    assert shield.targets_self
    assert condition.until == (TurnEdge.START, TurnOf.SOURCE)
    assert armor_class(_with({"Shield": condition.modifiers}), 15) == 20


def test_absorb_elements_resists_the_type_picked_until_its_next_turn():
    """Absorb Elements: "you have resistance to the triggering damage type
    until the start of your next turn" (Acid, Cold, Fire, Lightning or
    Thunder), a row per type."""
    rows = _effects("Absorb Elements")
    assert [row.name for row in rows] == [
        f"Absorb Elements: {t}"
        for t in ("Acid", "Cold", "Fire", "Lightning", "Thunder")
    ]
    fire = rows[2]
    (condition,) = fire.conditions
    assert fire.targets_self and condition.name == "Absorb Elements"
    assert condition.until == (TurnEdge.START, TurnOf.SOURCE)
    char = _with({"Absorb Elements": condition.modifiers})
    assert resists(char, FIRE) and not resists(char, "Cold")


def test_silence_gives_thunder_immunity_with_deafened():
    """Silence: "Any creature or object entirely inside the Sphere has
    Immunity to Thunder damage, and creatures have the Deafened condition"."""
    (row,) = _effects("Silence")
    deafened, badge = row.conditions
    assert deafened.name == Condition.DEAFENED.value and badge.name == "Silence"
    char = _with({"Silence": badge.modifiers})
    assert immune_to_damage(char, DamageType.THUNDER.value)
    assert not immune_to_damage(char, FIRE)


class _Barbarian:
    def __init__(self, level: int):
        self.level = level

    def get_class_level(self, character_class) -> int:
        return self.level


def test_rage_resists_weapons_and_gives_strength_advantage():
    (row,) = Rage().combat_effects(_Barbarian(5))  # type: ignore[arg-type]
    (condition,) = row.conditions
    assert condition.name == "Rage"
    assert condition.duration_seconds == 600  # "up to 10 minutes"
    raging = _with({"Rage": condition.modifiers})
    assert resists(raging, SLASHING) and not resists(raging, FIRE)
    assert save_plan(raging, "STR", "Neutral").mode == "Advantage"
    assert save_plan(raging, "DEX", "Neutral").mode == "Neutral"
    notes = [m.text for m in condition.modifiers if isinstance(m, Note)]
    assert "+2 damage on attacks using Strength (Rage Damage)" in notes


# ---------------------------------------------------------------------------
# In the window
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (the source) and a Tiger (the target) at AC 13."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    tiger["ac"] = 13
    return ui, pirate, tiger


def _rolls(monkeypatch, *d20s):
    rolls = iter(d20s)
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))


def test_barkskin_raises_the_ac_an_attack_is_compared_with(fight, monkeypatch):
    """10 + 5 hits AC 13, not Barkskin's 17; the miss shows the AC is above
    13 (the roll without the 4 Barkskin adds), which stays true after."""
    ui, pirate, tiger = fight
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Barkskin"))
    assert ui._target_armor() == 17
    _rolls(monkeypatch, 10, 1)
    ui._apply_custom_effect(
        CustomEffect(damage=[(20, "Fire")], attack_bonus=5, name="Fire Bolt")
    )
    assert tiger["hp"] == tiger["max_hp"]
    assert tiger["ac_above"] == 11
    ui._remove_condition_from(tiger, "Barkskin")
    assert ui._target_armor() == 13


def test_mage_armor_uses_the_targets_dexterity(fight):
    ui, pirate, tiger = fight
    tiger["Ability Scores"] = {**tiger.get("Ability Scores", {}), "DEX": 18}
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Mage Armor"))
    assert ui._target_armor() == 17  # 13 + 4


def test_damage_from_a_badge(fight):
    """Stoneskin halves Slashing (11 -> 5); with a Vulnerability as well it
    is halved, then doubled (11 -> 10); Immunity takes it all."""
    ui, pirate, tiger = fight
    for kind in ("damage_resistances", "damage_vulnerabilities", "damage_immunities"):
        tiger[kind] = []
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Stoneskin"))
    assert ui._damage_type_modifier(tiger, 11, SLASHING) == (5, "resisted")
    assert ui._damage_type_modifier(tiger, 11, FIRE) == (11, None)
    tiger["conditions"].append("Cursed")
    give_modifiers(tiger, "Cursed", (Vulnerability((DamageType.SLASHING,)),))
    assert ui._damage_type_modifier(tiger, 11, SLASHING) == (
        10,
        "resisted and vulnerable",
    )
    tiger["conditions"].append("Warded")
    give_modifiers(tiger, "Warded", (DamageImmunity((DamageType.POISON,)),))
    assert ui._damage_type_modifier(tiger, 11, POISON) == (0, "immune")


def test_players_learn_nothing_from_a_defense_a_badge_gives():
    monster = _with(
        {
            "Stoneskin": (Resistance((DamageType.SLASHING,)),),
            "Warded": (DamageImmunity((DamageType.POISON,)),),
        }
    )
    note_damage_defense(monster, SLASHING, "resisted")
    note_damage_defense(monster, POISON, "immune")
    assert "known_resistances" not in monster
    assert "known_immunities" not in monster
    note_damage_defense(monster, FIRE, "resisted")
    assert monster["known_resistances"] == [FIRE]


# ---------------------------------------------------------------------------
# 7.4: the Hit Point maximum (Aid: "Each target's Hit Point maximum and
# current Hit Points increase by 5 for the duration", 5 more "for each spell
# slot level above 2"; Heroes' Feast: "Its Hit Point maximum also increases
# by 2d10, and it gains the same number of Hit Points")
# ---------------------------------------------------------------------------


def test_a_hit_point_maximum_reads_back_and_refuses_nonsense():
    aid = HitPointMaximum("5", upcast="5")
    assert modifier_to_dict(aid) == {
        "type": "HitPointMaximum",
        "amount": "5",
        "upcast": "5",
    }
    assert modifier_from_dict(modifier_to_dict(aid)) == aid
    for amount in ("0", "five", "+5", "2d0", ""):
        with pytest.raises(ValueError, match="HitPointMaximum"):
            HitPointMaximum(amount)
    with pytest.raises(ValueError, match="upcast"):
        HitPointMaximum("5", upcast="-5")


def test_dice_and_upcast_are_rolled_as_the_badge_is_given():
    """Aid at level 4 is 5 + 5 + 5; Heroes' Feast's 2d10 is the roll; the
    rest stays as it is."""
    resist = Resistance((DamageType.POISON,))
    rolls = {"5": 5, "2d10": 13}
    assert rolled_modifiers(
        (HitPointMaximum("5", upcast="5"), resist), 2, rolls.__getitem__
    ) == (HitPointMaximum("15"), resist)
    assert rolled_modifiers((HitPointMaximum("2d10"),), 0, rolls.__getitem__) == (
        HitPointMaximum("13"),
    )


def test_the_maximum_counts_a_badges_number_once():
    aid = HitPointMaximum("5")
    char = _with({"Aid": (aid,)}, max_hp=30)
    assert hit_point_maximum(char) == 35
    effect = new_effect("Aid")
    effect["modifiers"] = [modifier_to_dict(aid)]
    char[KEY].append(effect)
    assert hit_point_maximum(char) == 35, "the same effect twice adds once"
    char["conditions"].remove("Aid")
    assert hit_point_maximum(char) == 30
    assert (
        hit_point_maximum(_with({"Drained": (HitPointMaximum("-40"),)}, max_hp=30)) == 0
    )
    unrolled = _with({"Feast": (HitPointMaximum("2d10"),)}, max_hp=30)
    assert hit_point_maximum(unrolled) == 30, "dice not rolled count nothing"


@pytest.fixture
def aided(fight):
    """The Tiger at 20 of 30 HP, and a Pirate with a level 2 and a level 3
    slot to cast Aid with."""
    ui, pirate, tiger = fight
    tiger.update(max_hp=30, hp=20)
    pirate["spell_slots"] = {2: 1, 3: 1}
    ui._select_character(pirate)
    return ui, pirate, tiger


def _cast_aid(ui, slot_level=2):
    ui._apply_cast_spell(SpellFactory.create("Aid"), slot_level=slot_level)


def test_aid_raises_the_maximum_and_current_hit_points(aided):
    ui, _, tiger = aided
    _cast_aid(ui)
    assert (tiger["hp"], hit_point_maximum(tiger)) == (25, 35)
    assert tiger["max_hp"] == 30, "the stored maximum stays the sheet's"
    assert "Tiger's Hit Point maximum is 35 (30, Aid: +5)" in str(ui._read_log())


def test_aid_at_level_3_gives_10(aided):
    ui, _, tiger = aided
    _cast_aid(ui, slot_level=3)
    assert (tiger["hp"], hit_point_maximum(tiger)) == (30, 40)


@pytest.mark.parametrize("hp, left", [(33, 30), (10, 10)])
def test_aid_ending_leaves_no_more_than_the_maximum(aided, hp, left):
    ui, _, tiger = aided
    _cast_aid(ui)
    tiger["hp"] = hp
    ui._remove_condition_from(tiger, "Aid")
    assert (tiger["hp"], hit_point_maximum(tiger)) == (left, 30)


def test_bloodied_goes_by_the_maximum_in_use(aided):
    """17 of 35 is half or less; 17 of 30 isn't."""
    ui, _, tiger = aided
    _cast_aid(ui)
    tiger["hp"] = 17
    ui._apply_bloodied_condition(tiger)
    assert "Bloodied" in tiger["conditions"]
    ui._remove_condition_from(tiger, "Aid")
    assert "Bloodied" not in tiger["conditions"]


def test_one_undo_takes_back_the_cast_and_its_hit_points(aided):
    ui, _, tiger = aided
    _cast_aid(ui)
    ui._undo_last()
    assert (tiger["hp"], hit_point_maximum(tiger)) == (20, 30)
    assert "Aid" not in tiger["conditions"]


def test_aid_again_adds_nothing(aided):
    """The same badge given again keeps one number: Aid's 5 doesn't stack."""
    ui, pirate, tiger = aided
    _cast_aid(ui)
    ui._give_badge_modifiers(
        tiger, "Aid", (HitPointMaximum("5", upcast="5"),), source=pirate
    )
    assert (tiger["hp"], hit_point_maximum(tiger)) == (25, 35)


def test_aid_brings_a_creature_at_0_hp_to(aided):
    """A creature that makes Death Saving Throws, at 0 HP and dying."""
    ui, _, tiger = aided
    tiger.update(hp=0, death_saves=True)
    ui._apply_cast_spell(SpellFactory.create("Aid"), slot_level=2)
    assert tiger["hp"] == 5
    assert "regains consciousness" in str(ui._read_log())


def test_heroes_feast_rolls_its_2d10_once(fight, monkeypatch):
    ui, pirate, tiger = fight
    tiger.update(max_hp=30, hp=30)
    rolls = iter([4, 9])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Heroes' Feast"))
    assert (tiger["hp"], hit_point_maximum(tiger)) == (43, 43)
    assert hit_point_maximum(tiger) == 43, "the badge keeps the roll"
    assert resists(tiger, POISON)


def test_the_hit_points_lost_as_it_ends_replay(aided):
    """The party's history replays the drop, as it replays damage."""
    ui, _, tiger = aided
    _cast_aid(ui)
    tiger["hp"] = 33
    ui._remove_condition_from(tiger, "Aid")
    log = ui._read_log()
    (event,) = [
        e
        for key in log
        if is_round_key(key)
        for e in log[key]
        if isinstance(e, dict) and e.get("action") == "lose_hit_points"
    ]
    assert event["value"]["hp_delta"] == -3
    replayed = {"name": "Tiger", "hp": 33, "max_hp": 30, "conditions": []}
    ui._apply_replay_action(replayed, event["action"], event["value"])
    assert replayed["hp"] == 30


# ---------------------------------------------------------------------------
# 7.5: what the card and More Info show
# ---------------------------------------------------------------------------


def test_the_ac_text_says_what_changes_it():
    assert armor_class_text(_with({}), 15) == "15"
    faith = _with({"Shield of Faith": (SHIELD_OF_FAITH,)})
    assert armor_class_text(faith, 15) == "17 (15; Shield of Faith +2)"
    both = _with(
        {"Barkskin": (BARKSKIN,), "Shield of Faith": (SHIELD_OF_FAITH,)},
        visibility_states=[HALF],
    )
    assert armor_class_text(both, 13) == (
        "19 (13; Shield of Faith +2, Barkskin at least 17, Half Cover +2)"
    )
    assert armor_class_text(both, 16) == (
        "20 (16; Shield of Faith +2, Half Cover +2)"
    ), "a floor under the AC isn't named"
    armored = _with({"Mage Armor": (MAGE_ARMOR,)}, **{"Ability Scores": {"DEX": 16}})
    assert armor_class_text(armored, 12) == "16 (12; Mage Armor 13 + DEX)"
    assert armor_class_text(armored, 18) == "18", "a base that doesn't beat it"


def test_a_players_ac_sentence_stays_when_nothing_changes_it():
    sentence = "18 (with Shield) and 16 (without Shield)"
    assert armor_text({"name": "Edmund", "conditions": [], "ac": sentence}) == sentence
    faith = _with({"Shield of Faith": (SHIELD_OF_FAITH,)}, ac=sentence)
    assert armor_text(faith) == "20 (18; Shield of Faith +2)"


def test_the_hit_point_maximum_text():
    assert hit_point_maximum_text(_with({}, max_hp=30)) == ""
    aided = _with({"Aid": (HitPointMaximum("5"),)}, max_hp=30)
    assert hit_point_maximum_text(aided) == "35 (30; Aid +5)"


def test_defenses_given_say_where_from():
    char = _with(
        {
            "Rage": (
                Resistance(
                    (DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING)
                ),
            ),
            "Heroism": (ConditionImmunity((Condition.FRIGHTENED,)),),
            "Cursed": (Vulnerability(),),
        }
    )
    assert defenses_from_modifiers(char) == {
        "Resist": ["Bludgeoning, Piercing, Slashing (Rage)"],
        "Cond. Immune": ["Frightened (Heroism)"],
        "Vulnerable": ["all damage (Cursed)"],
    }
    petrified = {"name": "Statue", "conditions": [Condition.PETRIFIED.value]}
    assert defenses_from_modifiers(petrified)["Resist"] == ["all damage (Petrified)"]


def _card_texts(ui, char) -> list[str]:
    from PyQt6.QtWidgets import QLabel

    card = ui._make_card(char)  # kept, so its labels live while read
    return [label.text() for label in card.findChildren(QLabel)]


def test_the_card_shows_the_stats_in_use(aided):
    ui, pirate, tiger = aided
    tiger["damage_resistances"] = []
    _cast_aid(ui)
    for name, modifiers in (
        (
            "Stoneskin",
            (
                Resistance(
                    (DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING)
                ),
            ),
        ),
        ("Shield of Faith", (SHIELD_OF_FAITH,)),
    ):
        tiger["conditions"].append(name)
        give_modifiers(tiger, name, modifiers)
    texts = _card_texts(ui, tiger)
    assert "Max HP 35 (30; Aid +5)" in texts
    assert any(t.startswith("AC: 15 (13; Shield of Faith +2)") for t in texts)
    assert "Resist: Bludgeoning, Piercing, Slashing (Stoneskin)" in texts
    for name in ("Aid", "Stoneskin", "Shield of Faith"):
        ui._remove_condition_from(tiger, name)
    texts = _card_texts(ui, tiger)
    assert not any(t.startswith("Max HP") or t.startswith("Resist") for t in texts)
    assert any(t.startswith("AC: 13") and "(" not in t.split("   ")[0] for t in texts)


# ---------------------------------------------------------------------------
# 7.3: Speed and size. Expected values from the 2024 rules text: Haste ("the
# target's Speed is doubled"; as it ends, "has a Speed of 0 until the end of
# its next turn"), Longstrider ("Speed increases by 10 feet"), Enlarge/Reduce
# ("size increases by one category - from Medium to Large"; "decreases by
# one category"), Large Form ("change your size to Large", "your Speed
# increases by 10 feet") and the Rules Glossary's Speed ("any special speed
# you have increases or decreases by an equal amount", "if your Speed is
# halved ... your Fly Speed is also halved").
# ---------------------------------------------------------------------------

HASTE = Speed(multiplier=2)
LONGSTRIDER = Speed(bonus=10)
ENLARGE, REDUCE = Size(steps=1), Size(steps=-1)


@pytest.mark.parametrize(
    "modifier, data",
    [
        (HASTE, {"type": "Speed", "multiplier": 2}),
        (Speed(multiplier=0.5), {"type": "Speed", "multiplier": 0.5}),
        (Speed(bonus=-10), {"type": "Speed", "bonus": -10}),
        (Speed(set_to=0), {"type": "Speed", "set_to": 0}),
        (REDUCE, {"type": "Size", "steps": -1}),
        (Size(becomes=CreatureSize.LARGE), {"type": "Size", "becomes": "Large"}),
    ],
)
def test_speed_and_size_read_back_as_written(modifier, data):
    written = modifier_to_dict(modifier)
    assert written == data
    assert modifier_from_dict(written) == modifier


@pytest.mark.parametrize(
    "make",
    [
        lambda: Speed(),
        lambda: Speed(multiplier=0),
        lambda: Speed(bonus=10.0),  # type: ignore[arg-type]
        lambda: Speed(set_to=-5),
        lambda: Speed(bonus=10, set_to=0),
        lambda: Size(),
        lambda: Size(becomes="Enormous"),  # type: ignore[arg-type]
        lambda: modifier_from_dict({"type": "Speed", "multiplier": "2"}),
        lambda: modifier_from_dict({"type": "Size", "becomes": "Enormous"}),
    ],
)
def test_a_speed_or_size_that_says_nothing_or_nonsense_is_refused(make):
    with pytest.raises(ValueError):
        make()


def test_haste_doubles_every_speed_after_longstrider():
    """Bonuses count first, then the doubling: (30 + 10) x 2."""
    hasted = _with({"Haste": (HASTE,), "Longstrider": (LONGSTRIDER,)})
    assert speed_in_use(hasted, 30) == 80
    assert speed_in_use(hasted, 60) == 140, "a Fly Speed changes the same way"
    assert speed_changes(hasted) == ["Longstrider +10 ft.", "Haste ×2"]


def test_a_speed_set_to_0_wins_and_nothing_goes_below_0():
    slowed = _with({"Haste": (Speed(set_to=0),), "Longstrider": (LONGSTRIDER,)})
    assert speed_in_use(slowed, 30) == 0
    assert speed_changes(slowed) == ["Haste 0 ft."]
    frozen = _with({"Ray of Frost": (Speed(bonus=-10),)})
    assert speed_in_use(frozen, 5) == 0
    halved = _with({"Slow": (Speed(multiplier=0.5),)})
    assert speed_in_use(halved, 25) == 12, "rounded down"
    assert speed_changes(halved) == ["Slow halved"]


def test_the_same_speed_effect_twice_counts_once():
    twice = _with({"Longstrider": (LONGSTRIDER, LONGSTRIDER)})
    assert speed_in_use(twice, 30) == 40


@pytest.mark.parametrize(
    "size, badges, in_use",
    [
        ("Medium", {"Enlarge/Reduce": (ENLARGE,)}, CreatureSize.LARGE),
        ("Large", {"Enlarge/Reduce": (REDUCE,)}, CreatureSize.MEDIUM),
        ("Gargantuan", {"Enlarge/Reduce": (ENLARGE,)}, CreatureSize.GARGANTUAN),
        ("Tiny", {"Enlarge/Reduce": (REDUCE,)}, CreatureSize.TINY),
        (
            "Medium",
            {"Large Form": (Size(becomes=CreatureSize.LARGE),)},
            CreatureSize.LARGE,
        ),
        (
            "Medium",
            {
                "Enlarge/Reduce": (ENLARGE,),
                "Large Form": (Size(becomes=CreatureSize.LARGE),),
            },
            CreatureSize.HUGE,
        ),
        (CreatureSize.HUGE, {}, CreatureSize.HUGE),
        (None, {"Enlarge/Reduce": (ENLARGE,)}, None),
    ],
)
def test_the_size_in_use(size, badges, in_use):
    char = _with(badges, **({"size": size} if size else {}))
    assert size_in_use(char) == in_use


def test_the_size_text():
    assert size_text(_with({}, size="Medium")) == ""
    enlarged = _with({"Enlarge/Reduce": (ENLARGE,)}, size="Medium")
    assert size_text(enlarged) == "Large (Medium; Enlarge/Reduce +1)"
    goliath = _with({"Large Form": (Size(becomes=CreatureSize.LARGE),)}, size="Medium")
    assert size_text(goliath) == "Large (Medium; Large Form)"


def _tumble_firings(target: dict):
    kivi = {"name": "Kivi", "conditions": [], "hp": 27, "max_hp": 27}
    tumble = CombatTrigger(
        TriggerEvent.HIT, needs_damage=True, largest_target=CreatureSize.LARGE
    )
    row = TriggerRow(
        name="Hill's Tumble",
        trigger=tumble,
        conditions=("Prone",),
        what="Prone",
        uses=(2, 2),
        costs=True,
    )
    hit = AttackOutcome(kivi, target, True, damage_dealt=7)
    return outcome_firings([hit], lambda char: [row] if char is kivi else [])[0]


def test_hills_tumble_goes_by_the_size_in_use():
    """An Enlarged Large Ogre is Huge: no Tumble. A Reduced Huge giant is
    Large: Tumble asks, naming the size it is now. Both go with the badge."""
    ogre = _with({"Enlarge/Reduce": (ENLARGE,)}, name="Ogre", size="Large", hp=60)
    assert _tumble_firings(ogre) == []
    ogre["conditions"].remove("Enlarge/Reduce")
    assert len(_tumble_firings(ogre)) == 1
    giant = _with({"Enlarge/Reduce": (REDUCE,)}, name="Giant", size="Huge", hp=100)
    (firing,) = _tumble_firings(giant)
    assert firing.question.startswith("Kivi hits Giant (Large): use Hill's Tumble?")
    giant["conditions"].remove("Enlarge/Reduce")
    assert _tumble_firings(giant) == []


def test_the_spells_and_large_form_give_speed_and_size():
    hasted, lethargy = _effects("Haste")
    assert HASTE in _badge_modifiers(hasted)
    assert ArmorClass(2) in _badge_modifiers(hasted)
    assert [c.name for c in lethargy.conditions] == ["Incapacitated", "Haste"]
    assert lethargy.conditions[1].modifiers == (Speed(set_to=0),)
    assert not lethargy.spends_use
    (longstrider,) = _effects("Longstrider")
    assert _badge_modifiers(longstrider) == (LONGSTRIDER,)
    enlarge, reduce = _effects("Enlarge/Reduce")
    assert ENLARGE in _badge_modifiers(enlarge)
    assert REDUCE in _badge_modifiers(reduce)
    assert reduce.save_ability == Ability.CONSTITUTION
    large_form = _large_form_badge()
    assert Size(becomes=CreatureSize.LARGE) in large_form
    assert LONGSTRIDER in large_form, "Speed +10 feet, as Longstrider's"


def _large_form_badge() -> tuple:
    from Builds.Characters.Y2024_Monk_Elements_KiviJatti import (
        Y2024MonkElementsKiviJattiCharacterBuilder as Kivi,
    )
    from CharacterContent.Features.SpeciesFeatures.GoliathFeatures import LargeForm

    sheet = Kivi().build()
    assert LargeForm().combat_effects(sheet) == [], "Kivi is below level 5"
    level_5 = type("Level5", (), {"character_level": 5})()
    (effect,) = LargeForm().combat_effects(level_5)  # type: ignore[arg-type]
    return _badge_modifiers(effect)


def test_the_card_shows_speed_and_size_in_use(fight):
    """Haste on the Tiger (Large, Speed 40): "Speed: 80 ft. (40 ft.; Haste
    x2)"; Enlarge/Reduce's Enlarge: "Size Huge (Large; Enlarge/Reduce +1)".
    Both go when the badges end; the player view shows only the speed and
    size in use."""
    ui, pirate, tiger = fight
    tiger.update(size="Large", speed_ground_ft=40)
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Haste"))
    tiger["conditions"].append("Enlarge/Reduce")
    give_modifiers(tiger, "Enlarge/Reduce", (ENLARGE,))
    texts = _card_texts(ui, tiger)
    assert any(t.endswith("Speed: 80 ft. (40 ft.; Haste ×2)") for t in texts)
    assert "Size Huge (Large; Enlarge/Reduce +1)" in texts
    assert _speed_text(tiger, sources=False) == "80 ft."
    assert "Huge" in _unit_details([tiger])
    for name in ("Haste", "Enlarge/Reduce"):
        ui._remove_condition_from(tiger, name)
    texts = _card_texts(ui, tiger)
    assert any(t.endswith("Speed: 40 ft.") for t in texts)
    assert not any(t.startswith("Size") for t in texts)


# ---------------------------------------------------------------------------
# "Until the end of the current turn" (Q37): Steady Aim and Sentinel's Halt


def test_the_current_turn_has_no_start():
    from Model.Content.CombatEffect import CombatCondition, TurnEdge, TurnOf

    with pytest.raises(ValueError, match="already started"):
        CombatCondition("Halt", until=(TurnEdge.START, TurnOf.CURRENT))
    assert CombatCondition("Halt", until=("end", "current")).until == (
        TurnEdge.END,
        TurnOf.CURRENT,
    )


def test_steady_aim_sets_speed_0_until_the_end_of_the_current_turn():
    """2024 Rogue: "your Speed is 0 until the end of the current turn"."""
    from CharacterContent.Features.ClassFeatures.Rogue.RogueFeatures import SteadyAim
    from Model.Content.CombatEffect import TurnEdge, TurnOf

    (row,) = SteadyAim().combat_effects(None)  # type: ignore[arg-type]
    (condition,) = row.conditions
    assert condition.until == (TurnEdge.END, TurnOf.CURRENT)
    assert Speed(set_to=0) in condition.modifiers
    assert not any("Speed is 0" in note for note in row.notes)


def test_sentinels_halt_sets_speed_0_for_the_rest_of_the_turn():
    """Halt: "the creature's Speed becomes 0 for the rest of the current turn"."""
    from CharacterContent.Features.CharacterFeats.GeneralFeats import Sentinel
    from Model.Content.CombatEffect import TurnEdge, TurnOf

    feat = Sentinel(4, Ability.DEXTERITY)
    (row,) = feat.combat_effects(None)  # type: ignore[arg-type]
    (condition,) = row.conditions
    assert (row.name, condition.name) == ("Halt", "Halt")
    assert condition.until == (TurnEdge.END, TurnOf.CURRENT)
    assert condition.modifiers == (Speed(set_to=0),)
