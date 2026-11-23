"""A stat-block ability's combat effects: what the combat UI rolls and
applies for it, and the reader that writes them from its text where stat
blocks are written (Combat/Tools/monster_effect_text.py,
Notes/explicit-attributes-plan.md Phase 4.3)."""

import importlib
import inspect
import pkgutil

import Combat.Monsters
from CharacterContent.Features.SubClassFeatures.Artificer.ArtificerBattleSmithFeatures import (
    SteelDefender,
)
from Combat.Fight.effect_options import effect_options
from Combat.Fight.monster_actions import parse_action, upgrade_ability_keys
from Combat.EncounterLogs import _plain
from Combat.Tools.monster_effect_text import (
    EFFECT_SECTIONS,
    read_ability_effects,
    read_effects,
    read_reach_and_range,
    reads_effects,
)
from Combat.Tools.monster_enum_format import format_ability_list
from Core.Definitions import Ability, Condition, CreatureSize, DamageType
from Model.Content.CombatArea import CombatArea, CombatAreaShape
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from Model.Creatures.Combatants import ExtendedCombatantData
from Model.Creatures.MonsterAbilities import MonsterAbility, MonsterCast, dice_plus
from Model.Content.Summons import SummonContext
from tests._snapshot_helpers import build


def test_an_attack_and_the_condition_its_hit_gives():
    bite, poisoned = read_effects(
        "Bite",
        "Melee Attack Roll: +4, reach 5 ft. Hit: 4 (1d4 + 2) Piercing damage, and"
        " the target has the Poisoned condition until the end of its next turn.",
    )
    assert bite == CombatEffect(
        roll=EffectRoll.ATTACK,
        attack_bonus=4,
        damage=(CombatDamage("1d4 + 2", DamageType.PIERCING),),
        reach_ft=5,
    )
    assert poisoned == CombatEffect(
        name="Bite: Poisoned",
        conditions=(
            CombatCondition(Condition.POISONED, until=(TurnEdge.END, TurnOf.TARGET)),
        ),
        spends_use=False,
        trigger=CombatTrigger(TriggerEvent.HIT, optional=False, after="Bite"),
    )


def test_a_failed_saves_condition():
    (glare,) = read_effects(
        "Glare",
        "Wisdom Saving Throw: DC 13, one creature. Failure: The target has the"
        " Frightened condition until the end of the gorgon's next turn.",
    )
    assert (glare.save_ability, glare.dc, glare.conditions) == (
        Ability.WISDOM,
        13,
        (CombatCondition(Condition.FRIGHTENED, until=(TurnEdge.END, TurnOf.SOURCE)),),
    )


def test_a_save_with_half_damage_and_an_area():
    (breath,) = read_effects(
        "Fire Breath (Recharge 5-6)",
        "Dexterity Saving Throw: DC 14, each creature in a 30-foot Cone."
        " Failure: 27 (5d10) Fire damage. Success: Half damage.",
    )
    assert breath == CombatEffect(
        roll=EffectRoll.SAVE,
        save_ability=Ability.DEXTERITY,
        dc=14,
        half_on_success=True,
        damage=(CombatDamage("5d10", DamageType.FIRE),),
        area=CombatArea(CombatAreaShape.CONE, 30),
    )


def test_a_condition_in_a_sentence_of_its_own_comes_as_the_attack_hits():
    club, prone = read_effects(
        "Tree Club",
        "Melee Attack Roll: +8, reach 10 ft. Hit: 18 (3d8 + 5) Bludgeoning"
        " damage. If the target is a Large or smaller creature, it has the Prone"
        " condition.",
    )
    assert club.conditions == ()
    assert prone == CombatEffect(
        name="Tree Club: Prone",
        conditions=(CombatCondition(Condition.PRONE),),
        spends_use=False,
        trigger=CombatTrigger(
            TriggerEvent.HIT,
            optional=False,
            after="Tree Club",
            largest_target=CreatureSize.LARGE,
        ),
    )


def test_a_save_the_hit_forces_is_an_effect_of_its_own():
    claw, save = read_effects(
        "Claw",
        "Melee Attack Roll: +4, reach 5 ft. Hit: 4 (1d4 + 2) Slashing damage. If"
        " the target is a creature that isn't an Undead or elf, it is subjected"
        " to the following effect. Constitution Saving Throw: DC 10. Failure:"
        " The target has the Paralyzed condition until the end of its next turn.",
    )
    assert (claw.roll, claw.attack_bonus, claw.save_ability) == (
        EffectRoll.ATTACK,
        4,
        None,
    )
    assert save.name == "Claw: Constitution save"
    assert (save.roll, save.save_ability, save.dc, save.spends_use) == (
        EffectRoll.SAVE,
        Ability.CONSTITUTION,
        10,
        False,
    )
    assert save.conditions == (
        CombatCondition(Condition.PARALYZED, until=(TurnEdge.END, TurnOf.TARGET)),
    )
    assert save.trigger == CombatTrigger(
        TriggerEvent.HIT,
        optional=False,
        after="Claw",
        when="the target is a creature that isn't an Undead or elf",
    )


def test_a_save_after_the_attack_hit_or_miss_has_its_own_area():
    burst, save = read_effects(
        "Earth Burst",
        "Ranged Attack Roll: +10, range 120 ft. Hit: 15 (2d8 + 6) Bludgeoning"
        " damage. Hit or Miss: Earth explodes from the target's space, creating"
        " the following effect. Dexterity Saving Throw: DC 16, each creature in a"
        " 10-foot Emanation originating from and including the target. Failure:"
        " 10 (3d6) Thunder damage.",
    )
    assert burst.area is None
    assert save.area == CombatArea(CombatAreaShape.EMANATION, 10)
    assert save.trigger is not None
    assert save.trigger.event is TriggerEvent.USES
    assert save.damage == (CombatDamage("3d6", DamageType.THUNDER),)


def test_a_damage_type_to_choose_from_its_list():
    (spittle,) = read_effects(
        "Spittle",
        "Ranged Attack Roll: +5, range 30 ft. Hit: 6 (1d6 + 3) damage of a type"
        " chosen by the kobold: Acid, Cold or Fire.",
    )
    assert spittle.damage == (
        CombatDamage(
            "1d6 + 3",
            None,
            choices=(DamageType.ACID, DamageType.COLD, DamageType.FIRE),
        ),
    )
    (ray,) = read_effects(
        "Divine Ray",
        "Ranged Attack Roll: +7, range 60 ft. Hit: 6 (1d6 + 3) Necrotic or"
        " Radiant damage (empyrean's choice).",
    )
    assert ray.damage[0].choices == (DamageType.NECROTIC, DamageType.RADIANT)


def test_hit_points_it_gives():
    (heal,) = read_effects(
        "Healing Touch (3/Day)",
        "The dragon touches another creature. The target regains 11 (2d8 + 2)"
        " Hit Points.",
    )
    assert heal.healing == CombatHitPoints("2d8 + 2")


def test_nothing_to_apply_is_no_effect():
    assert read_effects("Multiattack", "The troll makes three Rend attacks.") == ()
    assert read_effects("Roar", "It roars.") == ()


def test_only_an_action_sections_undescribed_abilities_are_read():
    rend = MonsterAbility(
        "Rend", "Melee Attack Roll: +5, reach 5 ft. Hit: 7 Slashing damage."
    )
    assert reads_effects(rend, "actions")
    assert not reads_effects(rend, "traits")
    described = MonsterAbility(
        rend.name, rend.description, combat_effects=(CombatEffect(),)
    )
    assert not reads_effects(described, "actions")
    casts = MonsterAbility("Spell", rend.description, casts=(MonsterCast("Fear"),))
    assert not reads_effects(casts, "actions")
    uses = MonsterAbility("Lash", rend.description, uses_ability="Rend")
    assert not reads_effects(uses, "actions")


def test_the_turn_column_reads_the_effects_not_the_text():
    ability = MonsterAbility(
        "Claw",
        "Unreadable, as far as the fight goes.",
        combat_effects=(
            CombatEffect(
                roll=EffectRoll.ATTACK,
                attack_bonus=6,
                damage=(CombatDamage("2d6 + 3", DamageType.SLASHING),),
                notes=("Also: it hums.",),
            ),
            CombatEffect(
                name="Claw: Constitution save",
                roll=EffectRoll.SAVE,
                save_ability=Ability.CONSTITUTION,
                dc=13,
                spends_use=False,
                trigger=CombatTrigger(TriggerEvent.HIT, optional=False, after="Claw"),
            ),
        ),
    )
    action = parse_action(ability)
    assert (action.to_hit, action.save_ability, action.save_dc) == (
        6,
        "Constitution",
        13,
    )
    assert action.notes == ("Also: it hums.",)
    assert parse_action(MonsterAbility("Claw", ability.description)).to_hit is None


def test_a_row_its_hit_brings_spends_nothing():
    """The attack spent its recharge; its Prone comes even once it's spent."""
    text = (
        "Melee Attack Roll: +8, reach 10 ft. Hit: 18 (3d8 + 5) Bludgeoning"
        " damage. If the target is a Large or smaller creature, it has the Prone"
        " condition."
    )
    club = MonsterAbility(
        "Tree Club (Recharge 6)",
        text,
        recharge=6,
        combat_effects=read_effects("Tree Club (Recharge 6)", text),
    )
    char = {
        "name": "Giant",
        "actions": [club],
        "spent_abilities": {"Tree Club (Recharge 6)": 1},
    }
    (actions,) = [
        rows for title, rows in effect_options(char, ()) if title == "Actions"
    ]
    attack, prone = actions
    assert attack.is_unavailable and attack.monster_action is not None
    assert not prone.is_unavailable and prone.monster_action is None
    assert prone.row_text == "Tree Club: Prone  on a hit, Large or smaller"


def test_an_old_logs_abilities_get_their_effects_once():
    text = "Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Slashing damage."
    old = {"name": "Claw", "description": text}
    char = upgrade_ability_keys({"actions": [old]})
    assert parse_action(char["actions"][0]).to_hit == 5
    # One with effects of its own is left as it is.
    kept = {"name": "Claw", "description": text, "combat_effects": []}
    upgrade_ability_keys({"actions": [kept]})
    assert kept["combat_effects"] == []


def test_an_old_logs_attack_gets_its_reach_and_range_once():
    """A log saved after Phase 4.3 and before 4.5 has an attack's effects
    without its reach and range: read once as it loads. A structured
    attack's own fields are its reach, so it isn't."""
    text = "Melee Attack Roll: +5, reach 10 ft. Hit: 7 (1d8 + 3) Slashing damage."
    attack = {"roll": "attack", "attack_bonus": 5}
    old = {"name": "Pike", "description": text, "combat_effects": [dict(attack)]}
    char = upgrade_ability_keys({"actions": [old]})
    assert char["actions"][0]["combat_effects"][0]["reach_ft"] == 10
    assert parse_action(char["actions"][0]).stated_range == (10, None, None)
    structured = {
        "name": "Pike",
        "description": text,
        "reach_ft": 10,
        "combat_effects": [dict(attack)],
    }
    upgrade_ability_keys({"actions": [structured]})
    assert structured["combat_effects"] == [attack]


def test_every_attack_says_how_far_it_goes():
    """The fight reads an attack's reach and range from its effect (or a
    structured attack's own fields), never its text (explicit-attributes
    plan 4.5): every catalog, homebrew and summon attack states one, and
    the one its text gives."""
    blocks = [monster for _, monster in _stat_blocks()] + list(_summons())
    wrong = []
    for block in blocks:
        for section in EFFECT_SECTIONS:
            for ability in getattr(block, section, None) or []:
                action = parse_action(ability)
                if action.to_hit is None:
                    continue
                said = read_reach_and_range(ability.description)
                if action.stated_range != said:
                    wrong.append(
                        f"{block.combatant_type}: {ability.name}"
                        f" {action.stated_range} != {said}"
                    )
    assert not wrong, f"Attacks whose reach or range isn't their text's: {wrong}"


def test_a_log_keeps_the_effects():
    text = "Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Slashing damage."
    claw = MonsterAbility("Claw", text, combat_effects=read_effects("Claw", text))
    logged = _plain({"a": claw})["a"]
    assert parse_action(logged) == parse_action(claw)
    assert upgrade_ability_keys({"actions": [logged]})["actions"][0] == logged


def test_the_generator_writes_the_effects():
    monster = {
        "actions": [
            {
                "name": "Rend",
                "description": "Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3)"
                " Slashing damage.",
            },
            {"name": "Breath (Recharge 5-6)", "description": "It casts Fear."},
        ]
    }
    written = format_ability_list(monster["actions"], "actions", monster)
    assert (
        "combat_effects=(CombatEffect(roll=EffectRoll.ATTACK, attack_bonus=5,"
        " damage=(CombatDamage('1d8 + 3', DamageType.SLASHING),), reach_ft=5),)"
    ) in written
    # The spell it casts is its row, not effects read from its text.
    assert written.count("combat_effects=") == 1


def test_dice_plus():
    assert dice_plus("1d8", 3) == "1d8 + 3"
    assert dice_plus("1d8", -1) == "1d8 - 1"
    assert dice_plus("1d8", 0) == "1d8"


def _stat_blocks():
    for info in pkgutil.walk_packages(Combat.Monsters.__path__, "Combat.Monsters."):
        if info.ispkg:
            continue
        module = importlib.import_module(info.name)
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__ and issubclass(
                cls, ExtendedCombatantData
            ):
                yield info.name, cls()  # pyright: ignore[reportCallIssue]


def test_every_catalog_abilitys_effects_are_what_its_text_says():
    """The fight reads the effects; the text is shown. generate_monsters.py
    writes a generated stat block's effects from its text, so the two say
    the same, which also lets an old log's abilities be read once as they
    load (upgrade_ability_keys)."""
    wrong = []
    for module, monster in _stat_blocks():
        if not module.endswith(".monsters"):
            continue
        for section in EFFECT_SECTIONS:
            for ability in getattr(monster, section, None) or []:
                if ability.casts or ability.uses_ability:
                    assert not ability.combat_effects, (monster, ability.name)
                    continue
                said = read_effects(ability.name, ability.description)
                if tuple(ability.combat_effects) != said:
                    wrong.append(f"{monster.combatant_type}: {ability.name}")
    assert not wrong, f"Effects that aren't what the text says: {wrong}"


def _summons():
    """Every feature summon of the example builds that have one, each choice."""
    for name in (
        "Y2024_Artificer_BattleSmith_PetraGearhollow",
        "Y2014DruidWildfireEmberAshgroveCharacterBuilder",
        "Y2024WarlockVestigeOrsolyaHollowvowCharacterBuilder",
        "Y2024RangerBeastMasterFennWildstriderCharacterBuilder",
        "Y2014BardCreationPiperWrenhollowCharacterBuilder",
        "Y2014FighterEchoKnightLucianMirrorstrikeCharacterBuilder",
        "Y2024_Artificer_Reanimator_Dessie",
        "Y2024_Ranger_Drakewarden_Hanna",
    ):
        sheet = build(name)
        for feature in sheet.features:
            for spec in feature.summons(sheet) or ():
                for choice in spec.choices(sheet) or [None]:
                    yield spec.build(sheet, SummonContext(choice=choice))


def test_no_ability_with_a_roll_in_its_text_lacks_effects():
    """A homebrew monster's or a summon's effects are written by hand, so
    they can say more than the reader would (Mira's Stutter Time), but one
    whose text has an attack, save, damage or condition the picker would
    fill in must have them: the fight no longer reads its text."""
    blocks = [monster for _, monster in _stat_blocks()] + list(_summons())
    missing = [
        f"{block.combatant_type}: {ability.name}"
        for block in blocks
        for section in EFFECT_SECTIONS
        for ability in getattr(block, section, None) or []
        if read_ability_effects(ability, section)
    ]
    assert not missing, f"Abilities to describe with combat_effects: {missing}"


def test_a_summons_effects_follow_its_owner():
    sheet = build("Y2024_Artificer_BattleSmith_PetraGearhollow")
    (feature,) = [f for f in sheet.features if isinstance(f, SteelDefender)]
    (spec,) = feature.summons(sheet)
    defender = spec.build(sheet, SummonContext())
    rend = parse_action((defender.actions or [])[0])
    modifier = sheet.get_intelligence_modifier()
    assert rend.to_hit == sheet.calculate_attack_bonus_for_ability(Ability.INTELLIGENCE)
    assert rend.damage[0].dice == dice_plus("1d8", 2 + modifier)
