"""Monster abilities in the combat UI's Custom Effect picker: combat effects
written on a MonsterAbility (Model/Creatures/MonsterAbilities.py, the same
CombatEffect model features use), and what the picker reads from a stat
block's text besides its attacks and saves - the spells an ability casts, the
other action it makes or uses, Hit Points it gives. Monsters reach the UI
from the encounter's log, as plain dicts, so most checks go through that.
Expected values come from the stat blocks and the rules, not from the code."""

import json

import pytest

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.CombatUIQt.effect_options import effect_options
from Combat.CombatUIQt.monster_actions import ability_effects, parse_action
from Combat.CombatUIQt.saves import (
    ATTACK_ROLL,
    DAMAGE_AMOUNT,
    HEALING,
    MONSTER_ACTION,
    SAVING_THROW,
    TEMP_HP,
    known_spell_attack_bonus,
)
from Combat.EncounterLogs import LogJSONEncoder, _plain
from Combat.Monsters.CR_0.monsters_homebrew import DwarfLifeCleric
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.Monsters.CR_1.monsters_homebrew import HumanPaladinOfDevotion
from Combat.Monsters.CR_15.monsters import MummyLord
from Combat.Monsters.CR_21.monsters import Lich, Solar
from Combat.Monsters.CR_23.monsters import AncientBlueDragon
from Combat.Monsters.CR_24.monsters import AncientGoldDragon, AncientRedDragon
from Combat.Monsters.CR_3.monsters_homebrew import MirelleTheGildedKnight
from Combat.Monsters.CR_5.monsters_homebrew import MiraPrincessOfTheLoop
from Combat.Monsters.CR_8.monsters import FrostGiant
from Combat.PlayerCombatant import combatant_from_stat_block
from Core.Definitions import Ability, DamageType
from Core.Rules import SPELL_SAVE_DC_BASE
from Model.Content.ActionType import ActionType
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Creatures.MonsterAbilities import MeleeAttack, MonsterAbility

STUTTER = CombatEffect(
    roll=EffectRoll.SAVE,
    save_ability=Ability.WISDOM,
    dc=15,
    repeat_save=True,
    damage=(CombatDamage("2d8", DamageType.PSYCHIC),),
    conditions=(CombatCondition("Stutter Time", until=(TurnEdge.END, TurnOf.TARGET)),),
    notes=("Slowed.",),
)


def _as_logged(monster) -> dict:
    """The monster's dict as the combat UI gets it: from the encounter log."""
    return _plain({"c": combatant_from_stat_block(monster)})["c"]


def _rows(monster) -> dict:
    """Every picker row for the monster's abilities, by category and name."""
    char = _as_logged(monster)
    return {
        (title, option.name): option
        for title, options in effect_options(char, all_spells=[])
        for option in options
    }


def _row(monster, name: str):
    return next(o for (_, n), o in _rows(monster).items() if n == name)


# ---------------------------------------------------------------------------
# The model: written on the ability, kept through the log


def test_an_ability_has_no_effects_unless_written():
    ability = MonsterAbility("Bite", "Melee Attack Roll: +4 ...")  # positional
    assert ability.combat_effects == ()
    assert MeleeAttack(name="Claw", attack_bonus=3).combat_effects == ()


def test_combat_effects_are_keyword_only():
    """So a positional MonsterAbility(name, description) never shifts."""
    with pytest.raises(TypeError):
        MonsterAbility("a", "b", (STUTTER,))  # type: ignore[misc]


def test_the_log_leaves_out_effects_nobody_wrote():
    logged = json.loads(json.dumps(MonsterAbility("Bite", "x"), cls=LogJSONEncoder))
    assert logged == {"name": "Bite", "description": "x"}


def test_written_effects_come_back_from_the_log():
    ability = MonsterAbility("Stutter Time", "x", combat_effects=(STUTTER,))
    logged = json.loads(json.dumps(ability, cls=LogJSONEncoder))
    assert ability_effects(logged) == (STUTTER,)
    assert ability_effects(ability) == (STUTTER,)


@pytest.mark.parametrize(
    "effect",
    [
        STUTTER,
        CombatEffect(name="Cure Wounds", healing=CombatHitPoints("2d8 + 4")),
        CombatEffect(healing=CombatHitPoints()),
        CombatEffect(temp_hp=CombatHitPoints("10"), action_type=ActionType.REACTION),
        CombatEffect(
            roll=EffectRoll.ATTACK, attack_bonus=5, concentration=True, spell="Bless"
        ),
        CombatEffect(
            damage=(CombatDamage("2d6", None, (DamageType.FIRE, DamageType.COLD)),),
            conditions=(CombatCondition("Prone", duration_seconds=60),),
            spends_use=False,
        ),
    ],
)
def test_every_field_survives_json(effect):
    import dataclasses

    plain = json.loads(json.dumps(dataclasses.asdict(effect)))
    assert CombatEffect.from_dict(plain) == effect
    assert CombatEffect.from_dict(effect.to_dict()) == effect


def test_a_log_from_before_hit_points_had_a_type_still_reads():
    """Logs written before 2026-11-08 keep healing and temp_hp as dice text."""
    old = {"name": "Cure Wounds", "healing": "2d8 + 4", "temp_hp": None}
    assert CombatEffect.from_dict(old) == CombatEffect(
        name="Cure Wounds", healing=CombatHitPoints("2d8 + 4")
    )
    assert CombatEffect.from_dict({"healing": ""}).healing == CombatHitPoints()


def test_a_written_effect_sets_the_turn_buttons_numbers():
    """The turn column rolls its first effect; its cost is still its name's."""
    ability = MonsterAbility(
        "Stutter Time (Recharge 5-6)",
        "unreadable prose",
        combat_effects=(STUTTER,),
    )
    for form in (ability, json.loads(json.dumps(ability, cls=LogJSONEncoder))):
        action = parse_action(form)
        assert (action.save_ability, action.save_dc) == ("Wisdom", 15)
        assert [(d.dice, d.damage_type) for d in action.damage] == [("2d8", "Psychic")]
        assert action.recharge_on == 5


# ---------------------------------------------------------------------------
# The Time Loop PR homebrew monsters, described


def test_compelled_duel():
    """ "must succeed on a DC 11 Wisdom saving throw or, for 1 minute
    (Concentration), ..." - not the stat-block sentence the reader knows."""
    row = _row(HumanPaladinOfDevotion(), "Compelled Duel (1/Day)")
    assert (row.roll, row.ability, row.dc) == (SAVING_THROW, "WIS", 11)
    assert row.condition == "Compelled Duel"
    assert row.duration_seconds == 60 and row.concentration
    assert row.is_curated and row.monster_action is not None


def test_lay_on_hands_is_healing_from_a_pool():
    row = _row(HumanPaladinOfDevotion(), "Lay on Hands")
    assert row.amount_kind == HEALING
    assert row.damage == ""  # the GM types what it spends
    assert "pool of 15" in row.note


def test_divine_smite_is_a_trait_that_is_used():
    rows = _rows(HumanPaladinOfDevotion())
    smite = rows[("Traits", "Divine Smite (2/Day)")]
    assert smite.damage == "2d8 Radiant"
    assert smite.monster_action.per_day == 2  # its 2/Day is spent


def test_traits_without_effects_arent_listed():
    titles = {title for title, _ in _rows(Tiger())}
    assert "Traits" not in titles


def test_life_domain_magic_has_a_row_per_use():
    rows = {n: o for (t, n), o in _rows(DwarfLifeCleric()).items()}
    cure, bless, preserve = rows["Cure Wounds"], rows["Bless"], rows["Preserve Life"]
    assert (cure.amount_kind, cure.damage) == (HEALING, "2d8 + 4")
    assert bless.condition == "Bless" and bless.concentration
    assert bless.spell_name == "Bless"  # its badge shows the spell
    assert preserve.amount_kind == HEALING and preserve.damage == ""
    # Each is a use of Life Domain Magic.
    assert {o.monster_action.name for o in (cure, bless, preserve)} == {
        "Life Domain Magic"
    }


def test_gilded_greatsword_doesnt_knock_prone_on_every_hit():
    """Prone only with Advantage, once per turn: the GM's to add."""
    row = _row(MirelleTheGildedKnight(), "Gilded Greatsword")
    assert (row.roll, row.bonus, row.damage) == (ATTACK_ROLL, 5, "2d6 + 3 Slashing")
    assert row.condition == ""
    assert "Prone" in row.note


def test_stutter_time_repeats_its_save():
    row = _row(MiraPrincessOfTheLoop(), "Stutter Time")
    assert row.repeat_save and row.condition == "Stutter Time"
    assert not row.half_on_save  # "Success: No effect."


def test_temporal_shift_lasts_until_miras_next_turn():
    row = _row(MiraPrincessOfTheLoop(), "Temporal Shift")
    assert row.condition == "Temporal Shift"
    assert row.until == ("start", "source")


def test_rewind_gives_temporary_hit_points():
    row = _row(MiraPrincessOfTheLoop(), "Rewind (2/Day)")
    assert (row.amount_kind, row.damage) == (TEMP_HP, "10")


# ---------------------------------------------------------------------------
# Read from the text, for every monster


def test_healing_from_a_stat_block_sentence():
    """ "regains 9 (2d4 + 4) Hit Points": the dice, not the average."""
    row = _row(DwarfLifeCleric(), "Healing Word (2/Day)")
    assert (row.amount_kind, row.damage) == (HEALING, "2d4 + 4")


def test_temporary_hit_points_from_a_stat_block_sentence():
    """Frost Giant's War Cry: "gains 16 (2d10 + 5) Temporary Hit Points"."""
    row = _row(FrostGiant(), "War Cry (Recharge 5–6)")
    assert (row.amount_kind, row.damage) == (TEMP_HP, "2d10 + 5")


def test_a_legendary_action_that_makes_another_attack():
    """Tail Swipe: "The dragon makes one Rend attack." It's the Rend, spent
    as Tail Swipe."""
    rows = _rows(AncientBlueDragon())
    rend = rows[("Actions", "Rend")]
    swipe = rows[("Legendary Actions", "Tail Swipe")]
    assert (swipe.roll, swipe.bonus, swipe.damage) == (
        rend.roll,
        rend.bonus,
        rend.damage,
    )
    assert swipe.monster_action.name == "Tail Swipe"
    assert swipe.monster_action.legendary_cost == 1
    assert "makes one Rend attack" in swipe.note


def test_pounce_says_to_move_first():
    """ "The dragon moves up to half its Speed, and it makes one Rend attack."
    The move is the GM's."""
    pounce = _row(AncientRedDragon(), "Pounce")
    assert pounce.bonus == _row(AncientRedDragon(), "Rend").bonus
    assert "move it by hand" in pounce.note


def test_an_action_that_uses_another():
    """The mummy lord's Glare: "The mummy uses Dreadful Glare.\" """
    rows = _rows(MummyLord())
    glare = rows[("Legendary Actions", "Glare")]
    dreadful = next(o for (t, n), o in rows.items() if n.startswith("Dreadful Glare"))
    assert (glare.ability, glare.dc, glare.condition) == (
        dreadful.ability,
        dreadful.dc,
        dreadful.condition,
    )
    assert glare.ability is not None


def test_a_spell_it_casts_at_its_own_dc():
    """The lich's Frightening Gaze casts Fear (a Wisdom save) at the DC of its
    Spellcasting, 20, spending the legendary action, not a slot."""
    gaze = _row(Lich(), "Frightening Gaze")
    assert (gaze.ability, gaze.dc) == ("WIS", 20)
    assert gaze.spell_name == "Fear"
    assert gaze.kind == MONSTER_ACTION
    assert gaze.slot_level is None and gaze.action_cost is None
    assert gaze.monster_action.legendary_cost == 1


def test_one_row_for_each_spell_it_can_cast():
    rows = {n for (t, n) in _rows(Lich())}
    assert {"Protective Magic: Counterspell", "Protective Magic: Shield"} <= rows


def test_a_spell_cast_at_a_higher_level():
    """Guiding Light: Guiding Bolt (level 4 version): 4d6 Radiant and 1d6 more
    per slot level above 1, so 7d6; the attack is its DC 24 - 8."""
    light = _row(AncientGoldDragon(), "Guiding Light")
    assert light.damage == "7d6 Radiant"
    assert "7d6" in light.summary
    assert light.bonus == 24 - SPELL_SAVE_DC_BASE


def test_a_spell_list_with_a_level_for_one():
    """The solar's Divine Aid: Cure Wounds (level 2 version), Lesser
    Restoration, or Remove Curse."""
    rows = {n: o for (t, n), o in _rows(Solar()).items()}
    cure = rows["Divine Aid (3/Day): Cure Wounds"]
    assert cure.amount_kind == HEALING
    assert cure.damage.startswith("4d8")  # 2d8, and 2d8 more at level 2
    assert "Divine Aid (3/Day): Remove Curse" in rows


def test_one_of_the_following_spells_isnt_a_spell():
    spellcasting = _row(Lich(), "Spellcasting")
    assert spellcasting.spell_name == ""


def test_the_spell_attack_is_the_dc_less_8_when_the_text_has_no_bonus():
    char = _as_logged(AncientGoldDragon())
    assert known_spell_attack_bonus(char) == 24 - 8


def test_multiattack_says_to_pick_each_attack():
    row = _row(MirelleTheGildedKnight(), "Multiattack")
    assert row.note.startswith("Pick each of its attacks in turn.")


def test_an_attack_read_from_its_text_is_unchanged():
    row = _row(Tiger(), "Rend")
    assert (row.bonus, row.damage, row.condition) == (5, "2d6 + 3 Slashing", "Prone")
    assert row.amount_kind == DAMAGE_AMOUNT and not row.is_curated


def test_every_monster_still_reads():
    """No stat block in the catalog breaks the picker."""
    import importlib
    import inspect
    import pkgutil

    import Combat.Monsters as monsters
    from Model.Creatures.Combatants import ExtendedCombatantData

    count = 0
    for info in pkgutil.walk_packages(monsters.__path__, "Combat.Monsters."):
        module = importlib.import_module(info.name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__:
                continue
            if not issubclass(cls, ExtendedCombatantData):
                continue
            effect_options(_as_logged(cls()), all_spells=[])
            count += 1
    assert count > 500
    assert SpellFactory.create("Fear") is not None


# ---------------------------------------------------------------------------
# In the dialog: picking them fills the form, and Apply spends the ability


def _monster_fight(tmp_path, monster):
    """`monster` (the source) and a hurt Tiger (the target)."""
    from tests._combat_ui import make_ui

    ui = make_ui(tmp_path, [monster, Tiger()])
    source, tiger = ui.characters
    ui._initiative_inputs[id(source)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(source)
    ui._select_target_character(tiger)
    tiger["hp"] = tiger["max_hp"] - 20
    return ui, source, tiger


def _pick(ui, monkeypatch, search: str):
    from PyQt6.QtWidgets import QComboBox, QLineEdit

    from tests._combat_ui import open_dialog

    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    box = dlg.findChild(QLineEdit, "effectSearch")
    box.setText(search)
    box.returnPressed.emit()
    kind = dlg.findChild(QComboBox, "amountKind").currentText()
    return dlg, kind


def _apply(dlg):
    from PyQt6.QtWidgets import QPushButton

    next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply").click()


def test_lay_on_hands_heals_what_the_gm_types(tmp_path, monkeypatch):
    from PyQt6.QtWidgets import QLineEdit

    ui, _, tiger = _monster_fight(tmp_path, HumanPaladinOfDevotion())
    dlg, kind = _pick(ui, monkeypatch, "lay on")
    assert kind == HEALING
    amount = dlg.findChild(QLineEdit, "effectDamage")
    assert amount.text() == ""
    amount.setText("7")
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 13


def test_divine_smite_spends_one_of_its_two_a_day(tmp_path, monkeypatch):
    ui, paladin, tiger = _monster_fight(tmp_path, HumanPaladinOfDevotion())
    dlg, kind = _pick(ui, monkeypatch, "divine smite")
    assert kind == DAMAGE_AMOUNT
    _apply(dlg)
    assert tiger["hp"] < tiger["max_hp"] - 20  # 2d8 Radiant more
    assert paladin["spent_abilities"] == {"Divine Smite (2/Day)": 1}


def test_a_legendary_spell_spends_a_legendary_action(tmp_path, monkeypatch):
    ui, lich, tiger = _monster_fight(tmp_path, Lich())
    dlg, _ = _pick(ui, monkeypatch, "frightening")
    _apply(dlg)
    assert lich["legendary_actions_left"] == 2
    assert "DC 20 Wisdom save against Frightening Gaze" in str(ui._read_log())


def test_a_spellcasting_list_has_a_row_per_spell():
    """ "At will: Thaumaturgy, Toll the Dead. 2/Day each: Hold Person,
    Silence. 1/Day: Bestow Curse." at its spell save DC 12."""
    from Combat.Monsters.CR_2.monsters_homebrew import PriestOfTheBlackTongues

    rows = {n: o for (t, n), o in _rows(PriestOfTheBlackTongues()).items()}
    names = {n for n in rows if n.startswith("Spellcasting: ")}
    assert names == {
        "Spellcasting: Thaumaturgy",
        "Spellcasting: Toll the Dead",
        "Spellcasting: Toll the Dead (hurt target)",
        "Spellcasting: Hold Person",
        "Spellcasting: Silence",
        "Spellcasting: Bestow Curse",
    }
    hold = rows["Spellcasting: Hold Person"]
    assert (hold.ability, hold.dc, hold.condition) == ("WIS", 12, "Paralyzed")
    assert "(2/Day each)" in hold.note
    assert "(At will)" not in rows["Spellcasting: Thaumaturgy"].note
