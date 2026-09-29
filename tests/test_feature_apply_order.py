"""Feature application must not depend on the order features/armor/items apply.

A bonus "equal to your <ability> modifier" used to be computed inside apply()
and stored as a constant, freezing it at whatever the score was when that
feature happened to run. Primal Order (added at Druid level 1) therefore
missed every later Ability Score Improvement, and late-applied features still
missed ability-raising magic items (items apply after every feature). Such
bonuses are now formulas evaluated at read time.

More generally, every effect (feature, extension, armor, weapon, item,
fighting style) only records facts, and the stat block works values out when
they're read: ability caps, "if already proficient, choose another", AC
formulas, roll conditions and spell slots included. Requirements are validated
once everything has applied. These tests pin that down.
"""

import ast
import itertools
import pathlib
import random
import sys

import pytest

from CharacterContent.Features.CharacterFeats import GeneralFeats
from CharacterContent.Features.ClassFeatures.Bard import BardFeatures
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Features.ClassFeatures.Druid import DruidFeatures
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Features.SubClassFeatures.Monk import MonkShadowFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Features.ClassFeatures.SpellSlots import CasterType, SpellSlots
from CharacterContent.Features.CombatFeatures.FightingStyles import Defense
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import (
    GrantArmorTraining,
    GrantSense,
    GrantToolProficiency,
    GrantWeaponProficiency,
    InitiativeRollCondition,
    SavingThrowProficiency,
    SkillExpertise,
    SkillProficiency,
    SkillRollCondition,
    SkillToAbilityOverride,
)
from CharacterContent.Features.SubClassFeatures.Cleric import ClericKnowledgeFeatures
from CharacterContent.Features.SubClassFeatures.Ranger import (
    RangerGloomStalkerFeatures,
    RangerHollowWardenFeatures,
)
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericForgeFeatures
from CharacterContent.Features.SubClassFeatures2014.Rogue import (
    RogueSwashbucklerFeatures,
)
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items.Weapons import WeaponProficiency
from CharacterContent.Items.Items.Wondrous import BracersOfArchery, GauntletsOfStrength
from Core.Definitions import (
    Ability,
    ArmorType,
    CharacterClass,
    DamageType,
    DiceRollCondition,
    Sense,
    Skill,
)
from RunCharacterCreator import BuildSelector, ExampleSelector
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock


def _source_bonus(character, skill, source):
    return [
        value
        for value, name in character.get_skill_bonus_sources(skill)
        if name == source
    ]


class TestModifierBonusesTrackLaterScoreIncreases:
    """Apply the feature first, raise the score afterwards (as a later ASI or a
    magic item would), and expect the bonus to reflect the final score."""

    def test_primal_order_magician(self, make_character):
        character = make_character(wisdom=16)  # +3
        DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.MAGICIAN).apply(
            character
        )
        character.abilities.add_bonus(Ability.WISDOM, 4)  # 20 -> +5
        for skill in (Skill.ARCANA, Skill.NATURE):
            assert _source_bonus(character, skill, "Primal Order") == [5]
            # INT 10 (+0), not proficient: the bonus is the whole modifier.
            assert character.get_skill_modifier(skill) == 5

    def test_primal_order_warden_grants_no_skill_bonus(self, make_character):
        character = make_character(wisdom=16)
        DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.WARDEN).apply(character)
        assert character.get_skill_bonus(Skill.ARCANA) == 0

    def test_thaumaturge(self, make_character):
        character = make_character(wisdom=14)  # +2
        feature = ClericFeatures.DivineOrderThaumaturge(extra_cantrip="Guidance")
        feature.apply(character)
        character.abilities.add_bonus(Ability.WISDOM, 4)  # 18 -> +4
        for skill in (Skill.ARCANA, Skill.RELIGION):
            assert _source_bonus(character, skill, feature.name) == [4]

    def test_modifier_bonus_keeps_minimum_of_one(self, make_character):
        character = make_character(wisdom=8)  # -1
        feature = ClericFeatures.DivineOrderThaumaturge(extra_cantrip="Guidance")
        feature.apply(character)
        assert character.get_skill_bonus(Skill.RELIGION) == 1

    def test_aura_of_protection(self, make_character):
        character = make_character(charisma=14)  # +2
        PaladinFeatures.AuraOfProtection().apply(character)
        character.abilities.add_bonus(Ability.CHARISMA, 4)  # 18 -> +4
        for ability in Ability:
            expected = character.get_ability_modifier(ability) + 4
            assert character.get_saving_throw_modifier(ability) == expected

    def test_hungering_might(self, make_character):
        character = make_character(wisdom=12)  # +1
        RangerHollowWardenFeatures.HungeringMight().apply(character)
        character.abilities.add_bonus(Ability.WISDOM, 6)  # 18 -> +4
        assert character.get_saving_throw_modifier(Ability.CONSTITUTION) == 4
        assert character.get_saving_throw_modifier(Ability.STRENGTH) == 0

    def test_dread_ambusher(self, make_character):
        character = make_character(wisdom=16)  # +3
        RangerGloomStalkerFeatures.DreadAmbusher().apply(character)
        character.abilities.add_bonus(Ability.WISDOM, 2)  # 18 -> +4
        assert character.initiative == 4

    def test_rakish_audacity(self, make_character):
        character = make_character(charisma=16)  # +3
        RogueSwashbucklerFeatures.RakishAudacity().apply(character)
        character.abilities.add_bonus(Ability.CHARISMA, 4)  # 20 -> +5
        assert character.initiative == 5


class TestJackOfAllTrades:
    def test_proficiency_granted_later_switches_bonus_off(self, make_character):
        # Bard 5: proficiency bonus +3, Jack of All Trades adds 3 // 2 = 1.
        character = make_character(levels={CharacterClass.BARD: 5})
        BardFeatures.JackOfAllTrades().apply(character)
        assert character.get_skill_modifier(Skill.STEALTH) == 1

        # A proficiency from anything that applies afterwards (species,
        # another builder, an item) must replace the half bonus, not stack.
        character.skills.add_skill_proficiency(Skill.STEALTH)
        assert character.get_skill_modifier(Skill.STEALTH) == 3
        assert _source_bonus(character, Skill.STEALTH, "Jack of All Trades") == []

    def test_unproficient_skills_list_the_source(self, make_character):
        character = make_character(levels={CharacterClass.BARD: 5})
        BardFeatures.JackOfAllTrades().apply(character)
        assert _source_bonus(character, Skill.ARCANA, "Jack of All Trades") == [1]


ALL_BUILDS = {**BuildSelector.builds(), **ExampleSelector.builds()}
_WISDOM_SKILL_BONUS_FEATURES = {
    "Primal Order": Skill.ARCANA,
    "Divine Order: Thaumaturge": Skill.ARCANA,
}


@pytest.mark.parametrize("name", sorted(ALL_BUILDS))
def test_wisdom_skill_bonuses_use_final_wisdom(name):
    # Regression: four example Druids printed Primal Order's Arcana bonus
    # from their level-1 Wisdom (+3) instead of their final Wisdom (+5).
    data = type(ALL_BUILDS[name])().build()
    character = data.setup_character_stat_block()
    expected = max(1, character.get_ability_modifier(Ability.WISDOM))
    for feature in data.features:
        skill = _WISDOM_SKILL_BONUS_FEATURES.get(feature.name)
        if skill is None:
            continue
        for value in _source_bonus(character, skill, feature.name):
            assert value == expected, feature.name


# ── The pipeline is order-insensitive ─────────────────────────────────────────


def _stats(data):
    cs = data.setup_character_stat_block()
    return {
        "scores": [cs.get_ability_score(a) for a in Ability],
        "ac": cs.calculate_armor_class(),
        "hp": cs.calculate_hit_points(),
        "initiative": cs.initiative,
        "initiative_roll": cs.initiative_roll_condition,
        "speed": cs.speed,
        "skills": [cs.get_skill_modifier(s) for s in Skill],
        "skill_proficiency": [
            (cs.is_proficient_in_skill(s), cs.has_expertise_in_skill(s)) for s in Skill
        ],
        "skill_rolls": [
            (cs.get_skill_roll_condition(s), sorted(cs.get_skill_roll_condition_reasons(s)))
            for s in Skill
        ],
        "saves": [cs.get_saving_throw_modifier(a) for a in Ability],
        "save_proficiency": [cs.is_proficient_in_saving_throw(a) for a in Ability],
        "spell_slots": cs.spell_slots,
        "pact_magic_slots": cs.pact_magic_slots,
        "resistances": sorted(map(str, cs.damage_resistances)),
        "immunities": sorted(map(str, cs.damage_immunities)),
        "condition_immunities": sorted(map(str, cs.condition_immunities)),
        "senses": sorted((str(k), v) for k, v in cs.senses.items()),
        "spell_save_dc_bonus": cs.spell_save_dc_bonus,
        "weapons_proficient": [w.is_proficient(cs) for w in data.weapons],
        "armor_training": sorted(map(str, cs.armor_training)),
        "weapon_proficiencies": sorted(map(str, cs.weapon_proficiencies)),
        "tool_proficiencies": sorted(t.name for t in cs.tool_proficiencies),
    }


@pytest.mark.parametrize("name", sorted(ALL_BUILDS))
def test_effect_order_does_not_change_stats(name, monkeypatch):
    # Every effect - features, extensions, armor, weapons, items and fighting
    # styles - applied in shuffled orders, with no exceptions.
    expected = _stats(type(ALL_BUILDS[name])().build())
    for seed in range(3):
        data = type(ALL_BUILDS[name])().build()
        effects = data.iter_stat_effects()
        random.Random(seed).shuffle(effects)
        monkeypatch.setattr(data, "iter_stat_effects", lambda features: effects)
        assert _stats(data) == expected, f"effect order changed stats (seed {seed})"


# Effects that used to resolve against whatever applied before them. Each test
# applies the same effects in both orders and expects one answer.


def _in_every_order(make_character, effects, **scores):
    characters = []
    for ordered in itertools.permutations(effects):
        character = make_character(**scores)
        for effect in ordered:
            effect.apply(character)
        character.validate()
        characters.append(character)
    return characters


class TestPreviouslyChronologicalEffects:
    def test_capped_increases_resolve_lowest_cap_first(self, make_character):
        # STR 19: the ASI's +2 "to a maximum of 20" gives 20, then Primal
        # Champion's +4 "to a maximum of 25" gives 24 - also when the capstone
        # applies first (it used to reach 23 and waste the ASI).
        effects = [
            GeneralFeats.AbilityScoreImprovement([(Ability.STRENGTH, 2)]),
            BarbarianFeatures.PrimalChampion(),
        ]
        for character in _in_every_order(make_character, effects, strength=19):
            assert character.get_ability_score(Ability.STRENGTH) == 24

    def test_item_bonus_goes_on_top_of_capped_increases(self, make_character):
        effects = [
            GeneralFeats.AbilityScoreImprovement([(Ability.STRENGTH, 2)]),
            GauntletsOfStrength(),
        ]
        for character in _in_every_order(make_character, effects, strength=19):
            assert character.get_ability_score(Ability.STRENGTH) == 22

    def test_armor_strength_requirement_met_by_any_later_increase(
        self, make_character
    ):
        effects = [
            Armor.PlateArmor(),
            GeneralFeats.AbilityScoreImprovement([(Ability.STRENGTH, 2)]),
        ]
        for character in _in_every_order(make_character, effects, strength=13):
            assert character.calculate_armor_class() == 18

    def test_armor_strength_requirement_not_met_by_items(self, make_character):
        for ordered in itertools.permutations(
            [Armor.PlateArmor(), GauntletsOfStrength()]
        ):
            character = make_character(strength=13)
            for effect in ordered:
                effect.apply(character)
            with pytest.raises(ValueError, match="Strength"):
                character.validate()

    def test_iron_mind_sees_proficiency_granted_after_it(self, make_character):
        # "If you already have this proficiency, you instead gain proficiency
        # in Intelligence or Charisma saving throws."
        effects = [
            RangerGloomStalkerFeatures.IronMind(),
            SavingThrowProficiency([Ability.WISDOM]),
        ]
        for character in _in_every_order(make_character, effects):
            proficient = [
                a for a in Ability if character.is_proficient_in_saving_throw(a)
            ]
            assert proficient == [Ability.INTELLIGENCE, Ability.WISDOM]

    def test_iron_mind_and_unfettered_mind_together(self, make_character):
        effects = [
            RangerGloomStalkerFeatures.IronMind(),
            ClericKnowledgeFeatures.UnfetteredMind(),
            SavingThrowProficiency([Ability.WISDOM, Ability.INTELLIGENCE]),
        ]
        results = {
            tuple(a for a in Ability if character.is_proficient_in_saving_throw(a))
            for character in _in_every_order(make_character, effects)
        }
        assert len(results) == 1
        # Both fall back, each to a different save the character lacked.
        assert len(results.pop()) == 4

    def test_darkvision_extension_sees_grants_applied_after_it(self, make_character):
        # "You gain Darkvision with a range of 60 feet. If you already have
        # Darkvision, its range increases by 60 feet." - species Darkvision 60
        # plus Umbral Sight and Shadow Arts is 180 in every order.
        effects = [
            RangerGloomStalkerFeatures.UmbralSight(),
            MonkShadowFeatures.ShadowArts(),
            GrantSense(Sense.DARKVISION, 60, "Species"),
        ]
        for character in _in_every_order(make_character, effects):
            assert character.get_sense_range(Sense.DARKVISION) == 180

    def test_skill_expert_on_a_skill_proficient_from_elsewhere(self, make_character):
        effects = [
            GeneralFeats.SkillExpert(
                character_level=4, ability=Ability.INTELLIGENCE, skill=Skill.ARCANA
            ),
            SkillProficiency([Skill.ARCANA]),
        ]
        for character in _in_every_order(make_character, effects):
            assert character.has_expertise_in_skill(Skill.ARCANA)


class TestCompetingEffectsNeverOverwrite:
    def test_two_unarmored_defenses_use_the_best_not_both(self, make_character):
        # Barbarian 10+DEX+CON (16) vs Monk 10+DEX+WIS (15): the rules let
        # you use one AC calculation - their abilities must not stack.
        effects = [BarbarianFeatures.UnarmoredDefense(), MonkFeatures.UnarmoredDefense()]
        for character in _in_every_order(
            make_character, effects, dexterity=14, constitution=18, wisdom=16
        ):
            assert character.calculate_armor_class() == 10 + 2 + 4

    def test_armor_replaces_unarmored_defense_in_any_order(self, make_character):
        effects = [MonkFeatures.UnarmoredDefense(), Armor.LeatherArmor()]
        for character in _in_every_order(
            make_character, effects, dexterity=14, wisdom=20
        ):
            assert character.calculate_armor_class() == 11 + 2

    def test_monk_unarmored_defense_lost_with_a_shield(self, make_character):
        # "While you aren't wearing armor or wielding a Shield..."
        effects = [MonkFeatures.UnarmoredDefense(), Armor.ShieldArmor()]
        for character in _in_every_order(
            make_character, effects, dexterity=14, wisdom=16
        ):
            assert character.calculate_armor_class() == 10 + 2 + 2

    def test_defense_fighting_style_sees_armor_applied_after_it(self, make_character):
        effects = [Defense(), Armor.LeatherArmor()]
        for character in _in_every_order(make_character, effects, dexterity=14):
            assert character.calculate_armor_class() == 11 + 2 + 1

    def test_roll_conditions_cancel_in_any_order(self, make_character):
        effects = [
            SkillRollCondition(Skill.STEALTH, DiceRollCondition.ADVANTAGE, "A"),
            Armor.PlateArmor(),  # Stealth Disadvantage
            InitiativeRollCondition(DiceRollCondition.ADVANTAGE),
            InitiativeRollCondition(DiceRollCondition.DISADVANTAGE),
        ]
        for character in _in_every_order(make_character, effects, strength=15):
            assert character.get_skill_roll_condition(Skill.STEALTH) == (
                DiceRollCondition.NEUTRAL
            )
            assert character.initiative_roll_condition == DiceRollCondition.NEUTRAL

    def test_several_skill_ability_overrides_use_the_best(self, make_character):
        effects = [
            SkillToAbilityOverride([Skill.ARCANA], Ability.WISDOM),
            SkillToAbilityOverride([Skill.ARCANA], Ability.CHARISMA),
        ]
        for character in _in_every_order(
            make_character, effects, wisdom=12, charisma=16
        ):
            assert character.get_skill_ability(Skill.ARCANA) == Ability.CHARISMA

    def test_multiclass_spell_slots_in_any_order(self, make_character):
        # Wizard 5 + Eldritch Knight (Fighter 6 -> 2 caster levels) = caster
        # level 7; Warlock 3 adds two separate 2nd-level Pact Magic slots.
        levels = {
            CharacterClass.WIZARD: 5,
            CharacterClass.FIGHTER: 6,
            CharacterClass.WARLOCK: 3,
        }
        effects = [
            SpellSlots(CasterType.FULL_CASTER, CharacterClass.WIZARD),
            SpellSlots(CasterType.THIRD_CASTER, CharacterClass.FIGHTER),
            SpellSlots(CasterType.WARLOCK_CASTER, CharacterClass.WARLOCK),
        ]
        for ordered in itertools.permutations(effects):
            character = make_character(levels=levels)
            for effect in ordered:
                effect.apply(character)
            assert character.spell_slots == {1: 4, 2: 3, 3: 3, 4: 1}
            assert character.pact_magic_slots == {2: 2}


class _GrantExpertise(Feature):
    def __init__(self, skill: Skill):
        super().__init__(name="Test Expertise")
        self._expertise = SkillExpertise([skill])

    def apply(self, character_stat_block):
        self._expertise.apply(character_stat_block)


class _GrantProficiency(Feature):
    def __init__(self, skill: Skill):
        super().__init__(name="Test Proficiency")
        self._proficiency = SkillProficiency([skill])

    def apply(self, character_stat_block):
        self._proficiency.apply(character_stat_block)


class TestExpertiseRequirement:
    def _data_and_unproficient_skill(self):
        data = type(ALL_BUILDS["Y2014ClericForgeBrennaHearthforgeCharacterBuilder"])()
        data = data.build()
        character = data.setup_character_stat_block()
        skill = next(s for s in Skill if not character.is_proficient_in_skill(s))
        return data, skill

    def test_expertise_without_proficiency_is_rejected(self):
        data, skill = self._data_and_unproficient_skill()
        data.add_feature(_GrantExpertise(skill))
        with pytest.raises(ValueError, match="unproficient skill"):
            data.setup_character_stat_block()

    def test_proficiency_granted_after_the_expertise_satisfies_it(self):
        # e.g. a class's Expertise pick relying on a species proficiency,
        # which merges after every class builder.
        data, skill = self._data_and_unproficient_skill()
        data.add_feature(_GrantExpertise(skill))
        data.add_feature(_GrantProficiency(skill))
        character = data.setup_character_stat_block()
        assert character.has_expertise_in_skill(skill)


class TestExtensionsApply:
    def test_extension_mechanics_reach_the_stat_block(self):
        # Regression: Saint of Forge and Fire (Forge Cleric 17) is wired as
        # an extension of Soul of the Forge, and extensions were render-only,
        # so its fire immunity silently never applied.
        data = type(ALL_BUILDS["Y2014ClericForgeBrennaHearthforgeCharacterBuilder"])()
        character = data.build().setup_character_stat_block()
        assert character.is_immune_to_damage(DamageType.FIRE)

    def test_extending_after_setup_refreshes_the_cached_stat_block(self):
        data = type(ALL_BUILDS["Y2014DruidDreamsSomnaDriftwillowCharacterBuilder"])()
        data = data.build()
        assert not data.setup_character_stat_block().is_immune_to_damage(
            DamageType.FIRE
        )
        # extend_feature() can't invalidate the cache itself.
        data.features[0].extend_feature(ClericForgeFeatures.SaintOfForgeAndFire())
        assert data.setup_character_stat_block().is_immune_to_damage(DamageType.FIRE)


def test_dropped_gear_does_not_leave_bonuses_on_weapons():
    # Regression: weapons were shared between a builder and every sheet it
    # built, so Bracers of Archery's +2 damage (and bow proficiency) stuck to
    # the bow after the bracers were dropped and the character rebuilt.
    builder = type(
        ALL_BUILDS["Y2014FighterArcaneArcherSylvaineFarshotCharacterBuilder"]
    )()
    bracers = BracersOfArchery()
    builder.add_adventuring_gear("Loot", items=[(bracers, 1)])

    def longbow_damage_bonuses():
        data = builder.build()
        data.setup_character_stat_block()
        bow = next(w for w in data.weapons if w.name == "Longbow")
        return bow.damage_roll_bonuses

    assert (2, "2 (Bracers of Archery)") in longbow_damage_bonuses()
    builder.drop_item(bracers)
    assert (2, "2 (Bracers of Archery)") not in longbow_damage_bonuses()


# ── Guard: no effect reads a mutable stat while the sheet is set up ───────────
# Runtime counterpart of the AST guard below: it follows reads through helper
# functions, items, armor, fighting styles and extensions, and sees every
# effect a real build exercises. There are no exceptions: an effect only
# records facts, and anything computed from other stats is a formula.

_MUTABLE_STAT_READERS = {
    AbilitiesStatBlock: ("get_score", "get_own_score", "get_modifier"),
    SkillsStatBlock: (
        "is_proficient",
        "has_expertise",
        "get_skill_ability",
        "get_skill_abilities",
        "get_bonus_sources",
        "get_roll_condition",
    ),
    SavingThrowsStatBlock: ("is_proficient", "is_advantaged", "get_bonus"),
    CharacterStatBlock: (
        "get_skill_modifier",
        "get_skill_bonus",
        "get_saving_throw_modifier",
        "calculate_armor_class",
        "calculate_hit_points",
        "calculate_difficulty_class_for_ability",
        "calculate_attack_bonus_for_ability",
        "get_carrying_capacity_sources",
        "get_sense_range",
    ),
}
_MUTABLE_STAT_PROPERTIES = (
    "initiative",
    "initiative_roll_condition",
    "speed",
    "spell_slots",
    "pact_magic_slots",
    "is_wearing_armor",
    "senses",
)
_EFFECT_METHODS = {"apply", "apply_to_weapons"}


def _effect_chain() -> list[str]:
    """Class names of the effects (feature/extension/improvement/armor/item)
    whose apply is on the call stack, outermost first."""
    chain = []
    frame = sys._getframe(2)
    while frame is not None:
        if frame.f_code.co_name in _EFFECT_METHODS and "self" in frame.f_locals:
            chain.append(type(frame.f_locals["self"]).__name__)
        frame = frame.f_back
    return chain[::-1]


@pytest.mark.parametrize("name", sorted(ALL_BUILDS))
def test_effects_do_not_read_mutable_stats_during_setup(name, monkeypatch):
    offending_reads = set()

    def record(reader: str):
        chain = _effect_chain()
        if chain:
            offending_reads.add(f"{' > '.join(chain)} reads {reader}")

    def instrument(cls, method_name):
        original = getattr(cls, method_name)

        def instrumented(*args, **kwargs):
            record(f"{cls.__name__}.{method_name}")
            return original(*args, **kwargs)

        monkeypatch.setattr(cls, method_name, instrumented)

    def instrument_property(name):
        original = getattr(CharacterStatBlock, name)

        def instrumented(self):
            record(f"CharacterStatBlock.{name}")
            return original.fget(self)

        monkeypatch.setattr(CharacterStatBlock, name, property(instrumented))

    for cls, method_names in _MUTABLE_STAT_READERS.items():
        for method_name in method_names:
            instrument(cls, method_name)
    for name_ in _MUTABLE_STAT_PROPERTIES:
        instrument_property(name_)

    type(ALL_BUILDS[name])().build().setup_character_stat_block()
    assert not offending_reads, (
        "an effect reads a stat that other effects can still change - pass a "
        "formula (Improvements.Value) instead:\n" + "\n".join(sorted(offending_reads))
    )


# ── Guard: apply() must not snapshot derived stats ────────────────────────────

# Proficiency bonus and levels aren't listed: they depend only on class
# levels, which are fixed before any feature applies.
_DERIVED_READERS = {
    "get_ability_modifier",
    "get_ability_score",
    "get_own_score",
    "get_strength_modifier",
    "get_dexterity_modifier",
    "get_constitution_modifier",
    "get_intelligence_modifier",
    "get_wisdom_modifier",
    "get_charisma_modifier",
    "get_modifier",
    "get_score",
    "is_proficient",
    "has_expertise",
    "is_proficient_in_skill",
    "is_proficient_in_saving_throw",
    "calculate_armor_class",
}
# Armor state is set by worn armor, which may apply after the feature.
_ARMOR_STATE = {"worn_armor_type", "is_wearing_armor", "is_wielding_shield"}


def _apply_methods_reading_derived_stats():
    root = pathlib.Path(__file__).resolve().parent.parent / "CharacterContent"
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            for method in cls.body:
                if not isinstance(method, ast.FunctionDef) or method.name != "apply":
                    continue
                # Reads inside a nested def/lambda are formulas evaluated at
                # read time, not snapshots - skip those subtrees.
                nested = {
                    id(node)
                    for inner in ast.walk(method)
                    if inner is not method
                    and isinstance(inner, (ast.FunctionDef, ast.Lambda))
                    for node in ast.walk(inner)
                }
                reads = set()
                for node in ast.walk(method):
                    if id(node) in nested:
                        continue
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr in _DERIVED_READERS
                    ):
                        reads.add(node.func.attr)
                    elif (
                        isinstance(node, ast.Attribute)
                        and isinstance(node.ctx, ast.Load)
                        and node.attr in _ARMOR_STATE
                    ):
                        reads.add(node.attr)
                if reads:
                    yield f"{cls.name}.{method.name}", path, method.lineno, sorted(reads)


def test_apply_methods_do_not_snapshot_derived_stats():
    offenders = [
        f"{path.name}:{line} {qualname} reads {', '.join(reads)}"
        for qualname, path, line, reads in _apply_methods_reading_derived_stats()
    ]
    assert not offenders, (
        "apply() computes a stat-dependent value up front, freezing it before "
        "later features/armor/items apply - pass a formula instead "
        "(e.g. SkillBonus(skill, lambda cs: cs.get_wisdom_modifier())):\n"
        + "\n".join(offenders)
    )


# ── Weapon, armor and tool proficiencies are recorded, not snapshotted ───────


class _GrantMartialWeapons(Feature):
    def __init__(self):
        super().__init__(name="Test Martial Weapon Training")

    def apply(self, character_stat_block):
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(character_stat_block)


class TestProficienciesResolveOnRead:
    def test_a_feature_can_grant_weapon_proficiency(self, make_character):
        # Features used to have no way to grant this: proficiency lived on the
        # sheet data and was stamped onto each weapon when it was added.
        longsword = Weapons.Longsword()
        for character in _in_every_order(
            make_character, [longsword, _GrantMartialWeapons()], strength=16
        ):
            assert longsword.is_proficient(character)
            # STR +3 plus the proficiency bonus (+2 at level 1).
            assert longsword.calculate_total_attack_roll_bonus_int(character) == 5

    def test_grant_added_after_the_weapon_reaches_the_sheet(self):
        # A Bladesinger: trained with some martial melee weapons, not bows.
        data = type(ALL_BUILDS["SpellSlotTestWizard5"])().build()
        longbow = Weapons.Longbow()
        data.add_weapon(longbow)
        assert not longbow.is_proficient(data.setup_character_stat_block())
        # Granted after the weapon was added - no longer too late.
        data.add_feature(_GrantMartialWeapons())
        character = data.setup_character_stat_block()
        assert longbow.is_proficient(character)
        assert WeaponProficiency.MARTIAL in character.weapon_proficiencies

    def test_builder_proficiencies_reach_the_stat_block(self):
        data = type(ALL_BUILDS["SpellSlotTestWizard5"])().build()
        character = data.setup_character_stat_block()
        assert character.weapon_proficiencies == data.weapon_proficiencies
        assert character.armor_training == data.armor_proficiencies
        assert {type(t) for t in character.tool_proficiencies} == {
            type(t) for t in data.tool_proficiencies
        }

    def test_bracers_of_archery_grant_bow_proficiency_while_worn(
        self, make_character
    ):
        longbow, longsword = Weapons.Longbow(), Weapons.Longsword()
        worn = make_character()
        BracersOfArchery().apply(worn)
        assert longbow.is_proficient(worn)
        assert not longsword.is_proficient(worn)
        unworn = make_character()
        BracersOfArchery(is_wearing=False).apply(unworn)
        assert not longbow.is_proficient(unworn)

    def test_armor_training_and_tools_from_features(self, make_character):
        from CharacterContent.ToolProficiencies.Proficiencies import SmithsTools

        effects = [
            GrantArmorTraining([ArmorType.HEAVY]),
            GrantToolProficiency([SmithsTools()]),
            GrantToolProficiency([SmithsTools()]),  # same tool, second source
        ]
        for character in _in_every_order(make_character, effects):
            assert character.armor_training == {ArmorType.HEAVY}
            assert [t.name for t in character.tool_proficiencies] == [
                SmithsTools().name
            ]
