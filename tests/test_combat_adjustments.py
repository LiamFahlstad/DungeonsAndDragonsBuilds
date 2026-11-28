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
from Combat.Fight.effect_options import feature_options
from Model.Content.CombatAdjustments import (
    PARENT,
    AddDamage,
    AddNote,
    Adjustment,
    Applies,
    CostsAction,
    EffectSource,
    Spells,
    adjusted,
    adjusted_effects,
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


# ---------------------------------------------------------------------------
# A change decides from the row as its phase found it


class _AddsFire(Feature):
    """Adds a Fire part to every spell it's cast with: a stand-in for any
    feature whose ADD change another ADD change could otherwise read."""

    def combat_adjustments(self, character):
        part = AddDamage(CombatDamage("1d6", DamageType.FIRE))
        return (Adjustment(Applies(spells=Spells()), (part,)),)


@pytest.mark.parametrize("name", ["A Adds Fire", "Z Adds Fire"])
def test_one_damage_roll_is_one_of_the_spells_own_whatever_the_names(name):
    """Elemental Affinity (Fire) is for "a spell that deals damage of that
    type": Lightning Bolt deals Lightning, so a Fire part another feature adds
    doesn't make it count, whichever feature's name sorts first."""
    sheet = _Sheet(_AddsFire(name=name), ElementalAffinity(DamageType.FIRE), charisma=3)
    bolt = _cast(sheet, "Lightning Bolt")
    assert [part.dice for part in bolt.damage][1:] == ["1d6"]


class _Costs(Feature):
    def __init__(self, name, change):
        super().__init__(name=name)
        self.change = change

    def combat_adjustments(self, character):
        return (Adjustment(Applies(features=(SteadyAim,)), (self.change,)),)


def test_a_conflict_note_names_both_features_and_what_each_would_make_it():
    steady = SteadyAim()
    sheet = _Sheet(
        steady,
        _Costs("B Feature", CostsAction(ActionType.NO_ACTION)),
        _Costs("A Feature", CostsAction(ActionType.BONUS_ACTION)),
        _Costs("C Feature", CostsAction(ActionType.BONUS_ACTION)),  # same: no clash
    )
    (effect,) = steady.combat_effects(sheet)
    effect = adjusted(sheet, EffectSource("Steady Aim", feature=steady), effect).effect
    assert effect.action_type is ActionType.BONUS_ACTION
    assert effect.notes[-1] == (
        "A Feature makes it a Bonus Action; B Feature would make it take no"
        " action. Check which applies."
    )


# ---------------------------------------------------------------------------
# Variants: another way to use a row


def _wei():
    from Builds.Examples.Y2024_Monk_OpenHand_WeiStonefist import (
        Y2024MonkOpenHandWeiStonefistCharacterBuilder,
    )
    from Combat.PlayerCombatant import combatant_from_character

    return combatant_from_character(
        Y2024MonkOpenHandWeiStonefistCharacterBuilder().build()
    )


def test_fleet_step_adds_a_step_of_the_wind_row_that_takes_no_action():
    """Fleet Step: "When you take a Bonus Action other than Step of the
    Wind, you can also use Step of the Wind immediately after that Bonus
    Action." Each of Step of the Wind's rows stays as it was, and gets a
    row of its own after it: no action, the same Focus Point."""
    char = _wei()
    sheet = char["_stat_block"]
    focus = next(f for f in sheet.features if f.name == "Monk's Focus")
    rows = {
        row.name: row
        for row in feature_options(char, focus)
        if row.name.startswith("Step of the Wind")
    }
    assert list(rows) == [
        "Step of the Wind: Dash",
        "Step of the Wind: Dash (Fleet Step)",
        "Step of the Wind: Disengage and Dash",
        "Step of the Wind: Disengage and Dash (Fleet Step)",
    ]
    own, fleet = (
        rows["Step of the Wind: Disengage and Dash"],
        rows["Step of the Wind: Disengage and Dash (Fleet Step)"],
    )
    assert own.action_cost is not None and fleet.action_cost is None
    assert "Fleet Step" not in own.note and "Fleet Step:" in fleet.note
    assert fleet.counts_uses and fleet.summary == own.summary  # the same use
    assert fleet.tooltip.endswith("Changed by Fleet Step.")


class _Variant(Feature):
    def combat_adjustments(self, character):
        return (
            Adjustment(
                Applies(features=(SteadyAim,)),
                (CostsAction(ActionType.NO_ACTION),),
                variant=self.name,
            ),
        )


def test_a_variant_row_has_the_rows_own_changes_too():
    """Roving Aim changes Steady Aim itself, so a variant of Steady Aim keeps
    Speed too; the row itself takes no variant's change."""
    steady = SteadyAim()
    sheet = _Sheet(steady, InfiltrationExpertise(), _Variant(name="Quick"))
    (effect,) = steady.combat_effects(sheet)
    row = adjusted(sheet, EffectSource("Steady Aim", feature=steady), effect)
    (quick,) = row.variants
    assert quick.effect.name == "Steady Aim (Quick)"
    assert quick.effect.action_type is ActionType.NO_ACTION
    assert row.effect.action_type is effect.action_type
    for each in row.rows:
        (badge,) = each.effect.conditions
        assert not any(isinstance(m, Speed) for m in badge.modifiers)
    assert quick.by == ("Infiltration Expertise", "Quick")


def test_a_cards_use_button_gets_the_row_never_a_variant():
    steady = SteadyAim()
    sheet = _Sheet(steady, _Variant(name="Quick"))
    effects = adjusted_effects(
        sheet, EffectSource("Steady Aim", feature=steady), steady.combat_effects(sheet)
    )
    assert [e.name for e in effects] == [""]


# ---------------------------------------------------------------------------
# Concentration and no action are values of their own


def test_concentration_is_the_sources_unless_the_row_says():
    assert CombatEffect().holds_concentration(True)
    assert not CombatEffect().holds_concentration(False)
    assert not CombatEffect(concentration=False).holds_concentration(True)
    assert CombatEffect(concentration=True).holds_concentration(False)


def test_a_feature_row_over_its_spell_keeps_what_it_sets():
    """A feature that casts a spell without Concentration says False, and
    that wins over the spell's own effect (over), as its notes go first."""
    spell = CombatEffect(damage=(CombatDamage("1d8", DamageType.FORCE),), notes=("S",))
    row = CombatEffect(spell="X", concentration=False, notes=("F",)).over(spell)
    assert row.concentration is False and row.damage == spell.damage
    assert row.notes == ("F", "S")
    assert CombatEffect(spell="X").over(spell).concentration is None
