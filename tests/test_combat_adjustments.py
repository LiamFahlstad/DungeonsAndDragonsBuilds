"""One feature changing another's (or a spell's) combat effect:
Feature.combat_adjustments and Model/Content/CombatAdjustments.py
(Notes/combat-effects-plan.md, Phase 10). Expected values come from the
features' rules text."""

import pytest

from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import Rage
from CharacterContent.Features.ClassFeatures.Rogue.RogueFeatures import SteadyAim
from CharacterContent.Features.SubClassFeatures.Barbarian.BarbarianPathOfTheBerserkerFeatures import (
    MindlessRage,
)
from CharacterContent.Features.SubClassFeatures.Cleric.ClericLifeFeatures import (
    DiscipleOfLife,
    SupremeHealing,
)
from CharacterContent.Features.SubClassFeatures.Rogue.RogueAssassinFeatures import (
    InfiltrationExpertise,
)
from CharacterContent.Features.SubClassFeatures.Sorcerer.SorcererDraconicFeatures import (
    ElementalAffinity,
)
from CharacterContent.Features.SubClassFeatures.Warlock.WarlockCelestialFeatures import (
    RadiantSoul,
)
from CharacterContent.Features.SubClassFeatures.Wizard.WizardEvokerFeatures import (
    EmpoweredEvocation,
)
from CharacterContent.Spells.SpellClasses import SPELL_CLASSES
from Combat.Fight.monster_actions import DamageRoll
from Combat.Fight.saves import with_dice
from Core.Definitions import Condition, DamageType
from Model.Content.ActionType import ActionType
from Model.Content.CombatAdjustments import (
    PARENT,
    AddNote,
    Adjustment,
    Applies,
    CostsAction,
    EffectSource,
    adjusted,
)
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
)
from Model.Content.CombatModifiers import ConditionImmunity, D20Mode, Speed
from Model.Content.Feature import Feature


class _Sheet:
    """Just what adjusting needs of a character: its features, which of them
    extend which, and the ability modifiers the features read."""

    def __init__(self, *features, extensions=(), intelligence=0, charisma=0):
        self.features = list(features)
        self.children = {}
        for child, parent in extensions:
            self.children.setdefault(id(parent), []).append(child)
        self.intelligence, self.charisma = intelligence, charisma

    def iter_features_with_extensions(self):
        for feature in self.features:
            yield feature
            yield from self.children.get(id(feature), [])

    def extensions_of(self, feature):
        return self.children.get(id(feature), [])

    def get_intelligence_modifier(self):
        return self.intelligence

    def get_charisma_modifier(self):
        return self.charisma


def _spell(name: str):
    return SPELL_CLASSES[name]()


def _cast(sheet, name: str, row: int = 0, with_slot: bool = True) -> CombatEffect:
    spell = _spell(name)
    effect = spell.combat_effects()[row]
    source = EffectSource(name, spell=spell, with_slot=with_slot and spell.level > 0)
    return adjusted(sheet, source, effect).effect


# ---------------------------------------------------------------------------
# A rider on its parent


def _raging(sheet, rage) -> CombatEffect:
    effect = CombatEffect(conditions=(CombatCondition("Rage"),), targets_self=True)
    return adjusted(sheet, EffectSource("Rage", feature=rage), effect).effect


def test_mindless_rage_makes_rage_immune_to_charmed_and_frightened():
    """ "You have Immunity to the Charmed and Frightened conditions while your
    Rage is active. If you're Charmed or Frightened when you enter your
    Rage, the condition ends on you." """
    rage, mindless = Rage(), MindlessRage()
    sheet = _Sheet(rage, extensions=[(mindless, rage)])
    effect = _raging(sheet, rage)
    (badge,) = effect.conditions
    immune = (Condition.CHARMED, Condition.FRIGHTENED)
    assert badge.modifiers == (ConditionImmunity(immune),)
    assert set(effect.ends_conditions) == set(immune)


def test_a_rider_not_granted_onto_its_parent_changes_nothing():
    rage, mindless = Rage(), MindlessRage()
    effect = _raging(_Sheet(rage, mindless), rage)
    assert effect.conditions[0].modifiers == () and effect.ends_conditions == ()


# ---------------------------------------------------------------------------
# Spells that match


def test_empowered_evocation_adds_intelligence_to_an_evocation_spell():
    """ "Whenever you cast a Wizard spell from the Evocation school, you can
    add your Intelligence modifier to one damage roll of that spell." """
    sheet = _Sheet(EmpoweredEvocation(), intelligence=4)
    fireball = _cast(sheet, "Fireball")
    assert fireball.damage[1] == CombatDamage("4", DamageType.FIRE)
    assert _cast(sheet, "Cure Wounds").healing.dice == "2d8"  # not Evocation


def test_empowered_evocation_is_the_casting_not_witch_bolts_later_turns():
    sheet = _Sheet(EmpoweredEvocation(), intelligence=4)
    assert len(_cast(sheet, "Witch Bolt").damage) == 2
    assert len(_cast(sheet, "Witch Bolt", row=1).damage) == 1


def test_one_damage_roll_of_several_darts_is_a_note():
    """Magic Missile's three darts: the modifier would count for each."""
    missile = _cast(_Sheet(EmpoweredEvocation(), intelligence=4), "Magic Missile")
    assert len(missile.damage) == 1
    assert "Empowered Evocation: 4 more on one dart's damage." in missile.notes


def test_elemental_affinity_counts_only_for_its_type():
    """ "When you cast a spell that deals damage of that type, you can add
    your Charisma modifier to one damage roll of that spell." """
    sheet = _Sheet(ElementalAffinity(DamageType.FIRE), charisma=3)
    assert _cast(sheet, "Fireball").damage[1] == CombatDamage("3", DamageType.FIRE)
    assert len(_cast(sheet, "Lightning Bolt").damage) == 1
    orb = _cast(sheet, "Chromatic Orb")
    assert orb.damage[1] == CombatDamage(
        "3", DamageType.FIRE, when="you chose Fire damage"
    )


def test_nothing_for_a_modifier_of_zero():
    sheet = _Sheet(ElementalAffinity(DamageType.FIRE), charisma=0)
    assert len(_cast(sheet, "Fireball").damage) == 1


def test_radiant_soul_is_for_one_target_on_every_turn():
    """ "Once per turn, when a spell you cast deals Radiant or Fire damage,
    you can add your Charisma modifier to that spell's damage against one of
    the spell's targets." """
    fireball = _cast(_Sheet(RadiantSoul(), charisma=4), "Fireball")
    assert fireball.damage[1].damage_type is DamageType.FIRE
    assert "one target" in fireball.damage[1].when


def test_the_order_features_come_in_doesnt_change_the_result():
    evoker, affinity = EmpoweredEvocation(), ElementalAffinity(DamageType.FIRE)
    one = _cast(_Sheet(evoker, affinity, intelligence=4, charisma=3), "Fireball")
    two = _cast(_Sheet(affinity, evoker, intelligence=4, charisma=3), "Fireball")
    assert one == two and len(one.damage) == 3


def test_the_row_says_which_features_changed_it():
    spell = _spell("Fireball")
    sheet = _Sheet(EmpoweredEvocation(), intelligence=4)
    changed = adjusted(
        sheet, EffectSource("Fireball", spell=spell), spell.combat_effects()[0]
    )
    assert changed.by == ("Empowered Evocation",)


# ---------------------------------------------------------------------------
# Healing


def test_disciple_of_life_is_two_plus_the_slots_level():
    """ "... regains additional Hit Points ... equal to 2 plus the spell
    slot's level": Cure Wounds (level 1) 3 more, and 1 more per slot level
    above."""
    healing = _cast(_Sheet(DiscipleOfLife()), "Cure Wounds").healing
    assert healing == CombatHitPoints("2d8 + 3", "2d8 + 1", add_modifier=True)
    at_level_3 = with_dice(DamageRoll(healing.dice, None), healing.upcast, 2)
    assert at_level_3.dice == "6d8 + 3 + 2"


def test_disciple_of_life_needs_a_spell_slot():
    """A feature's free casting isn't "a spell you cast with a spell slot"."""
    cure = _cast(_Sheet(DiscipleOfLife()), "Cure Wounds", with_slot=False)
    assert cure.healing.dice == "2d8"


def test_supreme_healing_uses_the_highest_number_before_disciple_adds():
    """ "... use the highest number possible for each die": 2d8 is 16, and
    the 2d8 more per slot level is 16; Disciple of Life adds on after."""
    for sheet in (
        _Sheet(SupremeHealing(), DiscipleOfLife()),
        _Sheet(DiscipleOfLife(), SupremeHealing()),
    ):
        healing = _cast(sheet, "Cure Wounds").healing
        assert healing == CombatHitPoints("19", "17", add_modifier=True)


# ---------------------------------------------------------------------------
# Taking away, and changes that can't both be made


def test_roving_aim_keeps_steady_aims_speed():
    """ "Your speed isn't reduced to 0 by using Steady Aim." """
    steady = SteadyAim()
    sheet = _Sheet(steady, InfiltrationExpertise())
    (effect,) = steady.combat_effects(sheet)
    effect = adjusted(sheet, EffectSource("Steady Aim", feature=steady), effect).effect
    (badge,) = effect.conditions
    assert not any(isinstance(m, Speed) for m in badge.modifiers)
    assert any(isinstance(m, D20Mode) for m in badge.modifiers)  # still Advantage


class _Sets(Feature):
    def __init__(self, name, action):
        super().__init__(name=name)
        self.action = action

    def combat_adjustments(self, character):
        return (
            Adjustment(Applies(features=(SteadyAim,)), (CostsAction(self.action),)),
        )


def test_two_features_setting_different_actions_say_so():
    steady = SteadyAim()
    sheet = _Sheet(
        steady,
        _Sets("B Feature", ActionType.REACTION),
        _Sets("A Feature", ActionType.ACTION),
    )
    (effect,) = steady.combat_effects(sheet)
    effect = adjusted(sheet, EffectSource("Steady Aim", feature=steady), effect).effect
    assert effect.action_type is ActionType.ACTION  # the first by name
    assert any("Check which applies" in note for note in effect.notes)


# ---------------------------------------------------------------------------
# The model checks itself


def test_an_adjustment_says_what_it_applies_to_and_changes():
    with pytest.raises(ValueError):
        Applies()
    with pytest.raises(ValueError):
        Adjustment(PARENT, ())
    with pytest.raises(ValueError):
        Adjustment(PARENT, ("a note",))
    assert Adjustment(PARENT, (AddNote("x"),)).applies.parent


def test_an_upcast_can_be_dice_and_a_number():
    assert CombatHitPoints("2d8", "2d8 + 1").upcast == "2d8 + 1"
    with pytest.raises(ValueError):
        CombatHitPoints("2d8", "2d8 + ")
