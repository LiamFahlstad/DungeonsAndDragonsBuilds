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
from Model.Content.Feature import Feature
from Model.Content.Improvements import (
    AbilityScoreBonus,
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
from Model.Effects import Effects
from tests._grants import grant
from Model.Character import Character


def _source_bonus(character, skill, source):
    return [
        bonus.value
        for bonus in character.get_skill_bonus_sources(skill)
        if bonus.source == source
    ]


class TestModifierBonusesTrackLaterScoreIncreases:
    """Apply the feature first, raise the score afterwards (as a later ASI or a
    magic item would), and expect the bonus to reflect the final score."""

    def test_primal_order_magician(self, make_sources):
        sources = make_sources(wisdom=16)  # +3
        sources.add_effect(
            DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.MAGICIAN)
        )
        sources.add_effect(
            AbilityScoreBonus([(Ability.WISDOM, 4)], total=4)
        )  # 20 -> +5
        character = Character(sources)
        for skill in (Skill.ARCANA, Skill.NATURE):
            assert _source_bonus(character, skill, "Primal Order") == [5]
            # INT 10 (+0), not proficient: the bonus is the whole modifier.
            assert character.get_skill_modifier(skill) == 5

    def test_primal_order_warden_grants_no_skill_bonus(self, make_sources):
        sources = make_sources(wisdom=16)
        sources.add_effect(
            DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.WARDEN)
        )
        character = Character(sources)
        assert character.get_skill_bonus(Skill.ARCANA) == 0

    def test_thaumaturge(self, make_sources):
        sources = make_sources(wisdom=14)  # +2
        feature = ClericFeatures.DivineOrderThaumaturge(extra_cantrip="Guidance")
        sources.add_effect(feature)
        sources.add_effect(
            AbilityScoreBonus([(Ability.WISDOM, 4)], total=4)
        )  # 18 -> +4
        character = Character(sources)
        for skill in (Skill.ARCANA, Skill.RELIGION):
            assert _source_bonus(character, skill, feature.name) == [4]

    def test_modifier_bonus_keeps_minimum_of_one(self, make_sources):
        sources = make_sources(wisdom=8)  # -1
        feature = ClericFeatures.DivineOrderThaumaturge(extra_cantrip="Guidance")
        sources.add_effect(feature)
        character = Character(sources)
        assert character.get_skill_bonus(Skill.RELIGION) == 1

    def test_aura_of_protection(self, make_sources):
        sources = make_sources(charisma=14)  # +2
        sources.add_effect(PaladinFeatures.AuraOfProtection())
        sources.add_effect(
            AbilityScoreBonus([(Ability.CHARISMA, 4)], total=4)
        )  # 18 -> +4
        character = Character(sources)
        for ability in Ability:
            expected = character.get_ability_modifier(ability) + 4
            assert character.get_saving_throw_modifier(ability) == expected

    def test_hungering_might(self, make_sources):
        sources = make_sources(wisdom=12)  # +1
        sources.add_effect(RangerHollowWardenFeatures.HungeringMight())
        sources.add_effect(
            AbilityScoreBonus([(Ability.WISDOM, 6)], total=6)
        )  # 18 -> +4
        character = Character(sources)
        assert character.get_saving_throw_modifier(Ability.CONSTITUTION) == 4
        assert character.get_saving_throw_modifier(Ability.STRENGTH) == 0

    def test_dread_ambusher(self, make_sources):
        sources = make_sources(wisdom=16)  # +3
        sources.add_effect(RangerGloomStalkerFeatures.DreadAmbusher())
        sources.add_effect(
            AbilityScoreBonus([(Ability.WISDOM, 2)], total=2)
        )  # 18 -> +4
        character = Character(sources)
        assert character.calculate_initiative() == 4

    def test_rakish_audacity(self, make_sources):
        sources = make_sources(charisma=16)  # +3
        sources.add_effect(RogueSwashbucklerFeatures.RakishAudacity())
        sources.add_effect(
            AbilityScoreBonus([(Ability.CHARISMA, 4)], total=4)
        )  # 20 -> +5
        character = Character(sources)
        assert character.calculate_initiative() == 5


class TestJackOfAllTrades:
    def test_proficiency_granted_later_switches_bonus_off(self, make_sources):
        # Bard 5: proficiency bonus +3, Jack of All Trades adds 3 // 2 = 1.
        sources = make_sources(levels={CharacterClass.BARD: 5})
        sources.add_effect(BardFeatures.JackOfAllTrades())
        character = Character(sources)
        assert character.get_skill_modifier(Skill.STEALTH) == 1

        # A proficiency from anything that applies afterwards (species,
        # another builder, an item) must replace the half bonus, not stack.
        sources.add_effect(SkillProficiency([Skill.STEALTH]))
        character = Character(sources)
        assert character.get_skill_modifier(Skill.STEALTH) == 3
        assert _source_bonus(character, Skill.STEALTH, "Jack of All Trades") == []

    def test_unproficient_skills_list_the_source(self, make_sources):
        sources = make_sources(levels={CharacterClass.BARD: 5})
        sources.add_effect(BardFeatures.JackOfAllTrades())
        character = Character(sources)
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
    character = data.validate()
    expected = max(1, character.get_ability_modifier(Ability.WISDOM))
    for feature in data.features:
        skill = _WISDOM_SKILL_BONUS_FEATURES.get(feature.name)
        if skill is None:
            continue
        for value in _source_bonus(character, skill, feature.name):
            assert value == expected, feature.name


# ── The pipeline is order-insensitive ─────────────────────────────────────────


def _stats(data):
    cs = data.validate()
    return {
        "scores": [cs.get_ability_score(a) for a in Ability],
        "ac": cs.calculate_armor_class(),
        "hp": cs.calculate_hit_points(),
        "initiative": cs.calculate_initiative(),
        "initiative_roll": cs.initiative_roll_condition,
        "speed": cs.calculate_speed(),
        "skills": [cs.get_skill_modifier(s) for s in Skill],
        "skill_proficiency": [
            (cs.is_proficient_in_skill(s), cs.has_expertise_in_skill(s)) for s in Skill
        ],
        "skill_rolls": [
            (
                cs.get_skill_roll_condition(s),
                sorted(cs.get_skill_roll_condition_reasons(s)),
            )
            for s in Skill
        ],
        "saves": [cs.get_saving_throw_modifier(a) for a in Ability],
        "save_proficiency": [cs.is_proficient_in_saving_throw(a) for a in Ability],
        "spell_slots": cs.spell_slots,
        "pact_magic_slots": cs.pact_magic_slots,
        "resistances": sorted(map(str, cs.damage_resistances())),
        "immunities": sorted(map(str, cs.damage_immunities())),
        "condition_immunities": sorted(map(str, cs.condition_immunities())),
        "senses": sorted((str(k), v) for k, v in cs.senses().items()),
        "spell_save_dc_bonus": cs.spell_save_dc_bonus,
        "weapons_proficient": [w.is_proficient(cs) for w in data.weapons],
        "weapon_attack_bonuses": [
            sorted(w.get_attack_roll_bonuses(cs)) for w in data.weapons
        ],
        "weapon_damage_bonuses": [
            sorted(w.get_damage_roll_bonuses(cs)) for w in data.weapons
        ],
        "armor_training": sorted(map(str, cs.armor_training())),
        "weapon_proficiencies": sorted(map(str, cs.weapon_proficiencies())),
        "tool_proficiencies": sorted(t.name for t in cs.tool_proficiencies()),
    }


@pytest.mark.parametrize("name", sorted(ALL_BUILDS))
def test_effect_order_does_not_change_stats(name):
    # Every effect - features, extensions, armor, weapons, items and fighting
    # styles - applied in shuffled orders, with no exceptions.
    expected = _stats(type(ALL_BUILDS[name])().build())
    built = type(ALL_BUILDS[name])().build()
    for seed in range(3):

        def shuffled(effects, seed=seed):
            return random.Random(seed).sample(effects, len(effects))

        data = Character(built.sources, apply_order=shuffled)
        assert _stats(data) == expected, f"effect order changed stats (seed {seed})"


# Effects that used to resolve against whatever applied before them. Each test
# applies the same effects in both orders and expects one answer.


def _in_every_order(make_sources, effects, **scores):
    characters = []
    for ordered in itertools.permutations(effects):
        sources = make_sources(**scores)
        for effect in ordered:
            sources.add_effect(effect)
        character = Character(sources).validate()
        characters.append(character)
    return characters


class TestPreviouslyChronologicalEffects:
    def test_capped_increases_resolve_lowest_cap_first(self, make_sources):
        # STR 19: the ASI's +2 "to a maximum of 20" gives 20, then Primal
        # Champion's +4 "to a maximum of 25" gives 24 - also when the capstone
        # applies first (it used to reach 23 and waste the ASI).
        effects = [
            GeneralFeats.AbilityScoreImprovement([(Ability.STRENGTH, 2)]),
            BarbarianFeatures.PrimalChampion(),
        ]
        for character in _in_every_order(make_sources, effects, strength=19):
            assert character.get_ability_score(Ability.STRENGTH) == 24

    def test_item_bonus_goes_on_top_of_capped_increases(self, make_sources):
        effects = [
            GeneralFeats.AbilityScoreImprovement([(Ability.STRENGTH, 2)]),
            GauntletsOfStrength(),
        ]
        for character in _in_every_order(make_sources, effects, strength=19):
            assert character.get_ability_score(Ability.STRENGTH) == 22

    def test_armor_strength_requirement_met_by_any_later_increase(self, make_sources):
        effects = [
            Armor.PlateArmor(),
            GeneralFeats.AbilityScoreImprovement([(Ability.STRENGTH, 2)]),
        ]
        for character in _in_every_order(make_sources, effects, strength=13):
            assert character.calculate_armor_class() == 18

    def test_armor_strength_requirement_not_met_by_items(self, make_sources):
        for ordered in itertools.permutations(
            [Armor.PlateArmor(), GauntletsOfStrength()]
        ):
            sources = make_sources(strength=13)
            for effect in ordered:
                sources.add_effect(effect)
            character = Character(sources)
            with pytest.raises(ValueError, match="Strength"):
                character.validate()

    def test_iron_mind_sees_proficiency_granted_after_it(self, make_sources):
        # "If you already have this proficiency, you instead gain proficiency
        # in Intelligence or Charisma saving throws."
        effects = [
            RangerGloomStalkerFeatures.IronMind(),
            SavingThrowProficiency([Ability.WISDOM]),
        ]
        for character in _in_every_order(make_sources, effects):
            proficient = [
                a for a in Ability if character.is_proficient_in_saving_throw(a)
            ]
            assert proficient == [Ability.INTELLIGENCE, Ability.WISDOM]

    def test_iron_mind_and_unfettered_mind_together(self, make_sources):
        effects = [
            RangerGloomStalkerFeatures.IronMind(),
            ClericKnowledgeFeatures.UnfetteredMind(),
            SavingThrowProficiency([Ability.WISDOM, Ability.INTELLIGENCE]),
        ]
        results = {
            tuple(a for a in Ability if character.is_proficient_in_saving_throw(a))
            for character in _in_every_order(make_sources, effects)
        }
        assert len(results) == 1
        # Both fall back, each to a different save the character lacked.
        assert len(results.pop()) == 4

    def test_darkvision_extension_sees_grants_applied_after_it(self, make_sources):
        # "You gain Darkvision with a range of 60 feet. If you already have
        # Darkvision, its range increases by 60 feet." - species Darkvision 60
        # plus Umbral Sight and Shadow Arts is 180 in every order.
        effects = [
            RangerGloomStalkerFeatures.UmbralSight(),
            MonkShadowFeatures.ShadowArts(),
            GrantSense(Sense.DARKVISION, 60, "Species"),
        ]
        for character in _in_every_order(make_sources, effects):
            assert character.get_sense_range(Sense.DARKVISION) == 180

    def test_skill_expert_on_a_skill_proficient_from_elsewhere(self, make_sources):
        effects = [
            GeneralFeats.SkillExpert(
                character_level=4, ability=Ability.INTELLIGENCE, skill=Skill.ARCANA
            ),
            SkillProficiency([Skill.ARCANA]),
        ]
        for character in _in_every_order(make_sources, effects):
            assert character.has_expertise_in_skill(Skill.ARCANA)


class TestCompetingEffectsNeverOverwrite:
    def test_two_unarmored_defenses_use_the_best_not_both(self, make_sources):
        # Barbarian 10+DEX+CON (16) vs Monk 10+DEX+WIS (15): the rules let
        # you use one AC calculation - their abilities must not stack.
        effects = [
            BarbarianFeatures.UnarmoredDefense(),
            MonkFeatures.UnarmoredDefense(),
        ]
        for character in _in_every_order(
            make_sources, effects, dexterity=14, constitution=18, wisdom=16
        ):
            assert character.calculate_armor_class() == 10 + 2 + 4

    def test_armor_replaces_unarmored_defense_in_any_order(self, make_sources):
        effects = [MonkFeatures.UnarmoredDefense(), Armor.LeatherArmor()]
        for character in _in_every_order(
            make_sources, effects, dexterity=14, wisdom=20
        ):
            assert character.calculate_armor_class() == 11 + 2

    def test_monk_unarmored_defense_lost_with_a_shield(self, make_sources):
        # "While you aren't wearing armor or wielding a Shield..."
        effects = [MonkFeatures.UnarmoredDefense(), Armor.ShieldArmor()]
        for character in _in_every_order(
            make_sources,
            effects,
            dexterity=14,
            wisdom=16,
            armor_training=[ArmorType.SHIELD],
        ):
            assert character.calculate_armor_class() == 10 + 2 + 2

    def test_defense_fighting_style_sees_armor_applied_after_it(self, make_sources):
        effects = [Defense(), Armor.LeatherArmor()]
        for character in _in_every_order(make_sources, effects, dexterity=14):
            assert character.calculate_armor_class() == 11 + 2 + 1

    def test_roll_conditions_cancel_in_any_order(self, make_sources):
        effects = [
            SkillRollCondition(Skill.STEALTH, DiceRollCondition.ADVANTAGE, "A"),
            Armor.PlateArmor(),  # Stealth Disadvantage
            InitiativeRollCondition(DiceRollCondition.ADVANTAGE),
            InitiativeRollCondition(DiceRollCondition.DISADVANTAGE),
        ]
        for character in _in_every_order(make_sources, effects, strength=15):
            assert character.get_skill_roll_condition(Skill.STEALTH) == (
                DiceRollCondition.NEUTRAL
            )
            assert character.initiative_roll_condition == DiceRollCondition.NEUTRAL

    def test_several_skill_ability_overrides_use_the_best(self, make_sources):
        effects = [
            SkillToAbilityOverride([Skill.ARCANA], Ability.WISDOM),
            SkillToAbilityOverride([Skill.ARCANA], Ability.CHARISMA),
        ]
        for character in _in_every_order(make_sources, effects, wisdom=12, charisma=16):
            assert character.get_skill_ability(Skill.ARCANA) == Ability.CHARISMA

    def test_multiclass_spell_slots_in_any_order(self, make_sources):
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
            sources = make_sources(levels=levels)
            for effect in ordered:
                sources.add_effect(effect)
            character = Character(sources)
            assert character.spell_slots == {1: 4, 2: 3, 3: 3, 4: 1}
            assert character.pact_magic_slots == {2: 2}


class _GrantExpertise(Feature):
    def __init__(self, skill: Skill):
        super().__init__(name="Test Expertise")
        self._expertise = SkillExpertise([skill])

    def apply(self, effects):
        self._expertise.apply(effects)


class _GrantProficiency(Feature):
    def __init__(self, skill: Skill):
        super().__init__(name="Test Proficiency")
        self._proficiency = SkillProficiency([skill])

    def apply(self, effects):
        self._proficiency.apply(effects)


class TestExpertiseRequirement:
    def _sources_and_unproficient_skill(self):
        builder = type(
            ALL_BUILDS["Y2014ClericForgeBrennaHearthforgeCharacterBuilder"]
        )()
        character = builder.build().validate()
        skill = next(s for s in Skill if not character.is_proficient_in_skill(s))
        return character.sources, skill

    def test_expertise_without_proficiency_is_rejected(self):
        sources, skill = self._sources_and_unproficient_skill()
        grant(sources).add_feature(_GrantExpertise(skill))
        with pytest.raises(ValueError, match="unproficient skill"):
            Character(sources).validate()

    def test_proficiency_granted_after_the_expertise_satisfies_it(self):
        # e.g. a class's Expertise pick relying on a species proficiency,
        # which merges after every class builder.
        sources, skill = self._sources_and_unproficient_skill()
        grant(sources).add_feature(_GrantExpertise(skill))
        grant(sources).add_feature(_GrantProficiency(skill))
        character = Character(sources).validate()
        assert character.has_expertise_in_skill(skill)


class TestExtensionsApply:
    def test_extension_mechanics_reach_the_stat_block(self):
        # Regression: Saint of Forge and Fire (Forge Cleric 17) is wired as
        # an extension of Soul of the Forge, and extensions were render-only,
        # so its fire immunity silently never applied.
        data = type(ALL_BUILDS["Y2014ClericForgeBrennaHearthforgeCharacterBuilder"])()
        character = data.build().validate()
        assert character.is_immune_to_damage(DamageType.FIRE)

    def test_extending_a_built_character(self):
        data = type(ALL_BUILDS["Y2014DruidDreamsSomnaDriftwillowCharacterBuilder"])()
        data = data.build()
        assert not data.validate().is_immune_to_damage(DamageType.FIRE)
        # An extension is a source like any other.
        sources = data.sources
        grant(sources).add_feature(
            ClericForgeFeatures.SaintOfForgeAndFire(), extends=data.features[0]
        )
        assert Character(sources).validate().is_immune_to_damage(DamageType.FIRE)


def test_dropped_gear_does_not_leave_bonuses_on_weapons():
    # Regression: Bracers of Archery's +2 damage (and bow proficiency) stuck
    # to the bow after the bracers were dropped and the character rebuilt.
    # Weapons are now shared between a builder and every sheet it builds, so
    # this also proves nothing writes into them.
    builder = type(
        ALL_BUILDS["Y2014FighterArcaneArcherSylvaineFarshotCharacterBuilder"]
    )()
    bracers = BracersOfArchery()
    builder.add_adventuring_gear("Loot", items=[(bracers, 1)])

    def longbow_damage_bonuses():
        data = builder.build()
        character = data.validate()
        bow = next(w for w in data.weapons if w.name == "Longbow")
        return bow.get_damage_roll_bonuses(character)

    assert (2, "2 (Bracers of Archery)") in longbow_damage_bonuses()
    builder.drop_item(bracers)
    assert (2, "2 (Bracers of Archery)") not in longbow_damage_bonuses()


# ── Guard: apply() gets a write-only record ──────────────────────────────────
# An effect can't read a stat that other effects may still change, because
# apply() never sees one: it gets Effects (Model/Effects.py), which can
# only record. A read inside any apply() fails every build that uses it
# (tests/test_all_builds.py builds them all), so there is nothing to allow-list
# and nothing to instrument - only the shape of the record to pin down.

_RECORDING_PREFIXES = ("add_", "set_", "register_")


def test_effects_can_only_record():
    public = [name for name in dir(Effects) if not name.startswith("_")]
    assert public, "Effects has no recording methods"
    readers = [name for name in public if not name.startswith(_RECORDING_PREFIXES)]
    assert not readers, f"Effects must be write-only, but exposes {readers}"
    # No instance attributes beyond the private record it writes into.
    assert Effects.__slots__ == ("_ledger",)


@pytest.mark.parametrize("name", sorted(ALL_BUILDS))
def test_evaluation_passes_apply_the_write_only_record(name):
    received = []

    class _Spy:
        def apply(self, effects):
            received.append(effects)

    sources = type(ALL_BUILDS[name])().build().sources
    sources.add_effect(_Spy())
    Character(sources).validate()
    assert received and all(type(r) is Effects for r in received)


def test_content_never_reaches_into_the_record():
    # Effects._ledger and Character._ledger are the record the Character
    # answers from; content that
    # reached it could read stats mid-evaluation again.
    root = pathlib.Path(__file__).resolve().parent.parent / "CharacterContent"
    offenders = [
        f"{path.relative_to(root)}:{node.lineno}"
        for path in root.rglob("*.py")
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.Attribute) and node.attr == "_ledger"
    ]
    assert not offenders, offenders


# ── Weapon, armor and tool proficiencies are recorded, not snapshotted ───────


class _GrantMartialWeapons(Feature):
    def __init__(self):
        super().__init__(name="Test Martial Weapon Training")

    def apply(self, effects):
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(effects)


class TestProficienciesResolveOnRead:
    def test_a_feature_can_grant_weapon_proficiency(self, make_sources):
        # Features used to have no way to grant this: proficiency lived on the
        # sheet data and was stamped onto each weapon when it was added.
        longsword = Weapons.Longsword()
        for character in _in_every_order(
            make_sources, [longsword, _GrantMartialWeapons()], strength=16
        ):
            assert longsword.is_proficient(character)
            # STR +3 plus the proficiency bonus (+2 at level 1).
            assert longsword.calculate_total_attack_roll_bonus_int(character) == 5

    def test_grant_added_after_the_weapon_reaches_the_sheet(self):
        # A Bladesinger: trained with some martial melee weapons, not bows.
        sources = type(ALL_BUILDS["SpellSlotTestWizard5"])().build().sources
        longbow = Weapons.Longbow()
        sources.add_weapon(longbow)
        assert not longbow.is_proficient(Character(sources).validate())
        # Granted after the weapon was added - no longer too late.
        grant(sources).add_feature(_GrantMartialWeapons())
        character = Character(sources).validate()
        assert longbow.is_proficient(character)
        assert WeaponProficiency.MARTIAL in character.weapon_proficiencies()

    def test_class_proficiencies_reach_the_stat_block(self):
        # Wizard's Core Traits: Simple weapons, no armor. Its Bladesinger
        # subclass adds Melee Martial weapons without Two-Handed or Heavy.
        data = type(ALL_BUILDS["SpellSlotTestWizard5"])().build()
        character = data.validate()
        assert character.weapon_proficiencies() == {
            WeaponProficiency.SIMPLE,
            WeaponProficiency.MARTIAL_MELEE_NOT_HEAVY_OR_TWO_HANDED,
        }
        assert character.armor_training() == set()

    def test_bracers_of_archery_grant_bow_proficiency_while_worn(self, make_sources):
        longbow, longsword = Weapons.Longbow(), Weapons.Longsword()
        worn_sources = make_sources()
        worn_sources.add_effect(BracersOfArchery())
        worn = Character(worn_sources)
        assert longbow.is_proficient(worn)
        assert not longsword.is_proficient(worn)
        unworn_sources = make_sources()
        unworn_sources.add_effect(BracersOfArchery(is_wearing=False))
        unworn = Character(unworn_sources)
        assert not longbow.is_proficient(unworn)

    def test_armor_training_and_tools_from_features(self, make_sources):
        from CharacterContent.ToolProficiencies.Proficiencies import SmithsTools

        effects = [
            GrantArmorTraining([ArmorType.HEAVY]),
            GrantToolProficiency([SmithsTools()]),
            GrantToolProficiency([SmithsTools()]),  # same tool, second source
        ]
        for character in _in_every_order(make_sources, effects):
            assert character.armor_training() == {ArmorType.HEAVY}
            assert [t.name for t in character.tool_proficiencies()] == [
                SmithsTools().name
            ]
