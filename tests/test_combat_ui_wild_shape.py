"""Wild Shape in the combat simulator: a Druid's combatant taking on a Beast
form's game statistics by the 2024 rules (Combat/WildShape.py), and the UI
around it (Combat/CombatUIQt/wild_shape_mixin.py): spending a use, the
temporary Hit Points and badge, the form's attacks on the turn column,
leaving the form by choice or by being knocked out, undo, no spellcasting,
and the form lasting into the next encounter through the player log."""

import copy
from functools import cache

import pytest
from PyQt6.QtWidgets import QMenu, QPushButton

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.CombatUIQt import CombatAppQt
from Combat.CombatUIQt.monster_actions import first_number
from Combat.Definitions import Action
from Combat.EncounterConfig import resolve_players
from Combat.EncounterLogs import prepare_log, scenario_log_path
from Combat.Monsters.CR_1.monsters import BrownBear, Tiger
from Combat.PlayerCombatant import combatant_from_character
from Combat.Scenario import CombatScenario
from Combat.CombatUIQt.rest import SHORT_REST_CADENCES, _restore_feature_uses
from Combat.WildShape import (
    _saving_throws,
    assume_form,
    can_cast_in_form,
    current_form,
    form_badge,
    known_forms,
    leave_form,
    wild_shape_feature,
)
from Core.Definitions import Ability, CharacterClass, Skill
from tests._combat_ui import make_ui, qapp
from tests._snapshot_helpers import build

# Circle of the Moon Druid 3 (Circle Forms): WIS 17, forms Brown Bear, Dire
# Wolf, Giant Spider and Tiger, two uses of Wild Shape.
MOON = "Y2024DruidMoonBriarWolfshadeCharacterBuilder"
# Circle of the Land Druid 20: Beast Spells, no Circle Forms.
LAND = "Y2024DruidLandRowanThistledownCharacterBuilder"


@cache
def _sheet(build_name: str):
    return build(build_name)


def _druid(build_name: str = MOON) -> dict:
    return combatant_from_character(_sheet(build_name))


def _public(char: dict) -> dict:
    return {k: v for k, v in char.items() if not k.startswith("_")}


# ---------------------------------------------------------------------------
# The combatant in a form (Combat/WildShape.py)


def test_a_druid_knows_the_forms_their_sheet_lists():
    assert list(known_forms(_sheet(MOON).validate())) == [
        "Brown Bear",
        "Dire Wolf",
        "Giant Spider",
        "Tiger",
    ]


def test_a_form_brings_the_beasts_body_and_the_druid_keeps_their_mind():
    char = _druid()
    hp, int_score = char["hp"], char["Ability Scores"]["INT"]
    assume_form(char, "Brown Bear")
    bear = BrownBear()
    assert current_form(char) == "Brown Bear"
    # Strength, Dexterity and Constitution are the Beast's.
    for ability in ("STR", "DEX", "CON"):
        assert char["Ability Scores"][ability] == bear.ability_scores[ability]
    # Hit Points and Intelligence, Wisdom and Charisma are the Druid's.
    assert char["hp"] == hp
    assert char["Ability Scores"]["INT"] == int_score
    assert char["speed"] == 40
    assert char["speed_climb_ft"] == 30
    assert char["size"] == "Large"
    assert [a.name for a in char["actions"]] == ["Multiattack", "Bite", "Claw"]


def test_circle_forms_ac_is_13_plus_wisdom_when_higher_than_the_beasts():
    char = _druid()
    assume_form(char, "Brown Bear")  # AC 11
    assert char["ac"] == 13 + 3  # WIS 17


def test_without_circle_forms_the_ac_is_the_beasts():
    char = _druid(LAND)
    assume_form(char, "Giant Badger")
    assert char["ac"] == known_forms(_sheet(LAND).validate())["Giant Badger"]().ac


def test_saves_keep_the_druids_proficiencies_or_use_the_beasts_if_higher():
    sheet = _sheet(MOON).validate()
    char = _druid()
    assume_form(char, "Brown Bear")
    saves = char["Saving Throws"]
    # Not proficient: just the Bear's STR 17 modifier.
    assert saves["STR"] == 3
    # Proficient in Wisdom saves, with their own Wisdom.
    assert saves["WIS"] == sheet.get_saving_throw_modifier(Ability.WISDOM)
    # The Bear lists Charisma -2, the Druid's own is higher.
    assert saves["CHA"] == sheet.get_saving_throw_modifier(Ability.CHARISMA) > -2


def test_skills_keep_the_druids_proficiencies_or_use_the_beasts_if_higher():
    sheet = _sheet(MOON).validate()
    char = _druid()
    assume_form(char, "Brown Bear")
    # Perception: the Druid's (Wisdom +3, proficient) beats the Bear's +3.
    assert char["skills"][Skill.PERCEPTION] == sheet.get_skill_modifier(
        Skill.PERCEPTION
    )
    assert char["skills"][Skill.PERCEPTION] > BrownBear().skills[Skill.PERCEPTION]
    # Athletics, which neither is proficient in: just the Bear's STR 17.
    assert char["skills"][Skill.ATHLETICS] == 3


def test_leaving_the_form_puts_back_everything_it_replaced():
    char = _druid()
    before = copy.deepcopy(_public(char))
    assume_form(char, "Brown Bear")
    assert leave_form(char) == "Brown Bear"
    assert _public(char) == before
    assert leave_form(char) is None


def test_a_new_form_replaces_the_old_one_not_the_druid():
    char = _druid()
    before = copy.deepcopy(_public(char))
    assume_form(char, "Brown Bear")
    assume_form(char, "Tiger")
    assert current_form(char) == "Tiger"
    assert char["Ability Scores"]["DEX"] == Tiger().ability_scores["DEX"]
    leave_form(char)
    assert _public(char) == before


def test_in_a_form_only_circle_of_the_moon_spells_can_be_cast():
    char = _druid()
    assert can_cast_in_form(char, "Entangle")
    assume_form(char, "Brown Bear")
    assert not can_cast_in_form(char, "Entangle")
    assert can_cast_in_form(char, "Moonbeam")  # Circle of the Moon Spells


def test_beast_spells_lets_a_druid_cast_in_a_form():
    char = _druid(LAND)
    assume_form(char, "Giant Badger")
    assert can_cast_in_form(char, "Entangle")


def test_beast_spells_excludes_a_costly_or_consumed_material_component():
    char = _druid(LAND)
    assume_form(char, "Giant Badger")
    # "diamond dust worth 100+ GP, which the spell consumes"
    assert not can_cast_in_form(char, "Stoneskin")


def test_a_druid_gains_the_forms_skill_proficiencies_with_their_own_bonus():
    # Rowan (Proficiency Bonus +6) isn't proficient in Stealth; the Owl is
    # (+5 listed on DEX 13). In the form: DEX 13's +1 plus Rowan's +6, which
    # beats the Owl's +5.
    char = _druid(LAND)
    assume_form(char, "Owl")
    assert char["skills"][Skill.STEALTH] == 1 + 6


def test_a_druid_gains_the_forms_save_proficiencies_with_their_own_bonus():
    sheet = _sheet(LAND).validate()
    bear = BrownBear()
    bear.saving_throws = {"DEX": 5}  # proficient: DEX 12 alone is +1
    scores = {**bear.ability_scores, "INT": 8, "WIS": 20, "CHA": 8}
    # Rowan isn't proficient in Dexterity saves: +1 plus Rowan's +6.
    assert _saving_throws(sheet, bear, scores)["DEX"] == 1 + 6


def test_passive_perception_is_the_druids_in_the_form():
    char = _druid(LAND)
    assume_form(char, "Owl")
    perception = char["skills"][Skill.PERCEPTION]
    assert f"Passive Perception {10 + perception}" in char["senses"]
    assert "Passive Perception 13" not in char["senses"]  # the Owl's own


# ---------------------------------------------------------------------------
# Wild Shape in a fight


@pytest.fixture
def fight(tmp_path):
    ui = make_ui(tmp_path, [Tiger()], [_sheet(MOON)])
    char, tiger = ui.characters
    ui._initiative_inputs[id(char)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(char)
    return ui, char, tiger


def _actions(ui, name: str) -> list[tuple[str, object]]:
    return [
        (event["action"], event["value"])
        for event in ui._read_log()["round_1"]
        if event.get("character") == name and event.get("action")
    ]


def _turn_buttons(ui) -> list[str]:
    layout = ui._actions_layout
    widgets = [layout.itemAt(i).widget() for i in range(layout.count())]
    return [
        button.text().split("\n")[0]
        for widget in widgets
        if widget is not None
        for button in [widget, *widget.findChildren(QPushButton)]
        if isinstance(button, QPushButton) and button.objectName() == "monsterActionBtn"
    ]


def test_wild_shape_spends_a_use_and_a_bonus_action(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    assert char["feature_uses_used"]["Wild Shape"] == 1
    assert char["action_uses"] == {"Bonus Action": 1}
    actions = _actions(ui, char["name"])
    assert (Action.ENABLE_FEATURE, {"feature_name": "Wild Shape"}) in actions
    assert (Action.WILD_SHAPE, {"form": "Brown Bear"}) in actions


def test_wild_shape_gives_circle_forms_temp_hp_and_a_badge(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    assert char["temp_hp"] == 3 * 3  # three times Druid level 3
    assert form_badge("Brown Bear") in char["conditions"]


def test_the_forms_attacks_are_on_the_turn_column(fight):
    ui, char, _ = fight
    assert _turn_buttons(ui) == []
    ui._assume_wild_shape(char, "Brown Bear")
    assert _turn_buttons(ui) == ["Bite", "Claw"]


def test_attacks_against_a_druid_in_a_form_use_its_ac(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    assert first_number(char["ac"]) == 16


def test_no_uses_left_means_no_wild_shape(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    ui._assume_wild_shape(char, "Tiger")
    ui._assume_wild_shape(char, "Dire Wolf")
    assert current_form(char) == "Tiger"
    assert char["feature_uses_used"]["Wild Shape"] == 2
    assert "no uses left" in ui._status_label.text()


def test_a_new_form_ends_the_old_one(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    ui._assume_wild_shape(char, "Tiger")
    assert form_badge("Brown Bear") not in char["conditions"]
    assert form_badge("Tiger") in char["conditions"]
    leave_form(char)
    assert char["ac"] == combatant_from_character(_sheet(MOON))["ac"]


def test_leaving_by_choice_is_a_bonus_action(fight):
    ui, char, _ = fight
    ac = char["ac"]
    ui._assume_wild_shape(char, "Brown Bear")
    ui._leave_wild_shape(char)
    assert current_form(char) is None
    assert char["ac"] == ac
    assert form_badge("Brown Bear") not in char["conditions"]
    assert char["action_uses"] == {"Bonus Action": 2}
    assert (Action.LEAVE_WILD_SHAPE, {"form": "Brown Bear"}) in _actions(
        ui, char["name"]
    )


def test_taking_the_badge_off_leaves_the_form(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    ui._remove_condition_from(char, form_badge("Brown Bear"), source=char)
    assert current_form(char) is None
    assert _turn_buttons(ui) == []


@pytest.mark.parametrize("condition", ["Incapacitated", "Stunned", "Paralyzed"])
def test_an_incapacitating_condition_ends_the_form(fight, condition):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    ui._add_condition_to(char, condition)
    assert current_form(char) is None
    assert char["action_uses"] == {"Bonus Action": 1}  # no action to leave


def test_an_incapacitated_druid_cant_wild_shape(fight):
    ui, char, _ = fight
    ui._add_condition_to(char, "Stunned")
    ui._assume_wild_shape(char, "Brown Bear")
    assert current_form(char) is None
    assert char.get("feature_uses_used", {}).get("Wild Shape", 0) == 0
    assert "can't take a Bonus Action" in ui._status_label.text()


def test_a_short_rest_gives_back_one_use_of_wild_shape(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    ui._assume_wild_shape(char, "Tiger")
    _restore_feature_uses(ui, char, SHORT_REST_CADENCES, note="short rest")
    assert char["feature_uses_used"]["Wild Shape"] == 1


def test_a_condition_that_doesnt_incapacitate_keeps_the_form(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    ui._add_condition_to(char, "Prone")
    assert current_form(char) == "Brown Bear"


def test_being_knocked_out_ends_the_form_and_keeps_the_druids_hp(fight):
    ui, char, tiger = fight
    ui._assume_wild_shape(char, "Brown Bear")
    # The form's temporary Hit Points soak first, then the Druid's own.
    ui._deal_damage(char, [(9 + char["hp"], "Slashing")], tiger, True, False)
    assert char["hp"] == 0
    assert "Unconscious" in char["conditions"]
    assert current_form(char) is None
    assert char["ac"] == combatant_from_character(_sheet(MOON))["ac"]


def test_undo_takes_wild_shape_back(fight):
    ui, char, _ = fight
    before = copy.deepcopy(_public(char))
    ui._assume_wild_shape(char, "Brown Bear")
    ui._undo_last()
    assert current_form(char) is None
    assert _public(char) == before


def test_a_druid_in_a_form_cant_cast_spells_but_moon_spells(fight):
    ui, char, _ = fight
    ui._assume_wild_shape(char, "Brown Bear")
    ui._apply_cast_spell(SpellFactory.create("Entangle"))
    assert char["stats"].get("spells_cast", 0) == 0
    assert "can't cast Entangle in Brown Bear form" in ui._status_label.text()
    ui._apply_cast_spell(SpellFactory.create("Moonbeam"))
    assert char["stats"]["spells_cast"] == 1


def test_the_card_menu_offers_the_forms_and_a_way_out(fight):
    ui, char, tiger = fight
    menu = ui._card_menu(char)
    wild_shape = next(a.menu() for a in menu.actions() if a.menu() is not None)
    assert wild_shape.title() == "Wild Shape (2 left)"
    assert [a.text() for a in wild_shape.actions()] == list(
        known_forms(_sheet(MOON).validate())
    )
    next(a for a in wild_shape.actions() if a.text() == "Tiger").trigger()
    assert current_form(char) == "Tiger"
    texts = [a.text() for a in ui._wild_shape_menu(char).actions()]
    assert texts[-1] == "Leave Tiger form"
    assert all(a.menu() is None for a in ui._card_menu(tiger).actions())


def test_enable_feature_asks_which_form(fight, monkeypatch):
    ui, char, _ = fight

    def pick_dire_wolf(menu, *args):
        next(a for a in menu.actions() if a.text() == "Dire Wolf").trigger()

    monkeypatch.setattr(QMenu, "exec", pick_dire_wolf)
    feature = wild_shape_feature(char)
    assert feature is not None
    ui._apply_feature(feature)
    assert current_form(char) == "Dire Wolf"
    # Using it through Enable Feature counts the use once, not twice.
    assert char["feature_uses_used"]["Wild Shape"] == 1


def test_wild_shape_temp_hp_without_circle_forms_is_the_druid_level(tmp_path):
    ui = make_ui(tmp_path, [Tiger()], [_sheet(LAND)])
    char = ui.characters[0]
    for i, c in enumerate(ui.characters):
        ui._initiative_inputs[id(c)].setText(str(20 - i))
    ui._start_combat()
    ui._select_character(char)
    ui._assume_wild_shape(char, "Giant Badger")
    druid_level = _sheet(LAND).validate().get_class_level(CharacterClass.DRUID)
    assert char["temp_hp"] == druid_level


# ---------------------------------------------------------------------------
# The party's player log: a form lasts into the next encounter


def _scenario() -> CombatScenario:
    return CombatScenario(
        name="tiger_den",
        title="Tiger Den",
        combatants=lambda: [Tiger()],
        players=[_sheet(MOON).character_name],
        monster_summary=["Tiger"],
    )


def _party_ui(tmp_path) -> CombatAppQt:
    qapp()
    logs = tmp_path / "CombatLogs"
    scenario = _scenario()
    path = scenario_log_path(logs, scenario.name)
    if not path.exists():
        names = [_sheet(MOON).character_name]
        prepare_log(path, scenario, resolve_players(scenario.players, names))
    ui = CombatAppQt(
        [],
        [_sheet(MOON)],
        combat_log_dir=logs,
        player_log_path=str(tmp_path / "PlayerLogs" / "main_party.json"),
        scenario_name=None,
        scenarios=[scenario],
    )
    ui._build_window()
    return ui


def _party_druid(ui) -> dict:
    return next(c for c in ui.characters if c.get("_is_player"))


def _wild_shape_in_a_fight(tmp_path) -> CombatAppQt:
    ui = _party_ui(tmp_path)
    ui._load_encounter(_scenario(), restart=False)
    for i, char in enumerate(ui.characters):
        ui._initiative_inputs[id(char)].setText(str(20 - i))
    ui._start_combat()
    druid = _party_druid(ui)
    ui._select_character(druid)
    ui._assume_wild_shape(druid, "Brown Bear")
    return ui


def test_a_druid_is_still_in_their_form_on_the_next_run(tmp_path):
    _wild_shape_in_a_fight(tmp_path)
    druid = _party_druid(_party_ui(tmp_path))
    assert current_form(druid) == "Brown Bear"
    assert druid["ac"] == 16
    assert druid["temp_hp"] == 9
    assert druid["feature_uses_used"]["Wild Shape"] == 1


def test_a_druid_who_left_their_form_is_themselves_on_the_next_run(tmp_path):
    ui = _wild_shape_in_a_fight(tmp_path)
    ui._leave_wild_shape(_party_druid(ui))
    druid = _party_druid(_party_ui(tmp_path))
    assert current_form(druid) is None
    assert druid["ac"] == combatant_from_character(_sheet(MOON))["ac"]
