"""
2024-edition subclass features: CharacterContent/Features/SubClassFeatures/ and the
subclass builders in CharacterContent/Classes/SubClasses2024/.

Expected values are transcribed from the bundled 2024 PHB subclass texts in
SourceTexts/SubclassTexts2024/<subclass>.txt (quoted in comments next to each
assertion) or computed by hand from those texts - never read off the engine's
own output or re-derived with the engine's own formula.

apply_features() mirrors setup_character_stat_block's order: feature.apply,
then worn armor, then feature.apply_after_armor.
"""

import pytest

from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import (
    Ability,
    CharacterClass,
    Condition,
    DamageType,
    DiceRollCondition,
    DruidLandType,
    Skill,
)
from RunCharacterCreator import BuildSelector

from CharacterContent.Features.SubClassFeatures.Cleric import (
    ClericKnowledgeFeatures,
    ClericWarFeatures,
)
from CharacterContent.Features.SubClassFeatures.Sorcerer import SorcererDraconicFeatures
from CharacterContent.Features.SubClassFeatures.Warlock import (
    WarlockArchfeyFeatures,
    WarlockCelestialFeatures,
    WarlockFiendFeatures,
)
from CharacterContent.Features.SubClassFeatures.Fighter import (
    FighterBattleMasterFeatures,
    FighterChampionFeatures,
    FighterPsiWarriorFeatures,
)
from CharacterContent.Features.SubClassFeatures.Ranger import (
    RangerGloomStalkerFeatures,
    RangerWinterWalkerFeatures,
)
from CharacterContent.Features.SubClassFeatures.Bard import BardLoreFeatures
from CharacterContent.Features.SubClassFeatures.Druid import DruidLandFeatures
from CharacterContent.Features.SubClassFeatures.Wizard import WizardBladesingerFeatures

from CharacterContent.Classes.SubClasses2024 import DruidLand


def apply_features(character, features, armors=()):
    for feature in features:
        feature.apply(character)
    for armor in armors:
        armor.apply(character)
    for feature in features:
        feature.apply_after_armor(character)
    return character


# ---------------------------------------------------------------------------
# Always-prepared subclass spells: grant levels and spell names, transcribed
# from SourceTexts/SubclassTexts2024/*.txt. data.spells is a list of
# (spell, ability, ruling, grant_level) tuples accumulated by add_spell(),
# with grant_level set from the class level being processed when the
# subclass's LevelFeatures.add_features() ran (ClassBuilder.create()).
# ---------------------------------------------------------------------------


def _cleric_data_with_channel_divinity():
    # ClericWarLevel3/ClericKnowledgeLevel3.add_features() extend the Cleric's
    # base Channel Divinity feature (extend_feature), so it must already be on
    # the accumulator - exactly as ClassBuilder.create() guarantees by running
    # base-class-level features (which add Channel Divinity at Cleric level 2)
    # before subclass-level features.
    from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures

    data = CharacterSheetData(spell_casting_ability=Ability.WISDOM)
    data.add_feature(ClericFeatures.ChannelDivinity())
    return data


class TestClericDomainSpellLevels:
    def test_war_domain_spell_counts_by_level(self):
        # SourceTexts/SubclassTexts2024/war_domain.txt - War Domain Spells table:
        # 3: Guiding Bolt, Magic Weapon, Shield of Faith, Spiritual Weapon (4)
        # 5: Crusader's Mantle, Spirit Guardians (2)
        # 7: Fire Shield, Freedom of Movement (2)
        # 9: Hold Monster, Steel Wind Strike (2)
        # (no 13/17 tier for War Domain)
        from CharacterContent.Classes.SubClasses2024 import ClericWar

        data = _cleric_data_with_channel_divinity()
        ClericWar.ClericWarLevel3().add_features(data)
        assert len(data.spells) == 4
        ClericWar.ClericWarLevel5().add_features(data)
        assert len(data.spells) == 4 + 2
        ClericWar.ClericWarLevel7().add_features(data)
        assert len(data.spells) == 4 + 2 + 2
        ClericWar.ClericWarLevel9().add_features(data)
        assert len(data.spells) == 4 + 2 + 2 + 2

    def test_knowledge_domain_spell_count_at_level_3_is_six(self):
        # SourceTexts/SubclassTexts2024/knowledge_domain.txt - Knowledge Domain
        # Spells table, Cleric level 3 row lists SIX prepared spells (Command,
        # Comprehend Languages, Detect Magic, Detect Thoughts, Identify, Mind
        # Spike) - twice as many as most other domains' level-3 row.
        from CharacterContent.Classes.SubClasses2024 import ClericKnowledge

        data = _cleric_data_with_channel_divinity()
        ClericKnowledge.ClericKnowledgeLevel3(Skill.ARCANA, Skill.HISTORY).add_features(
            data
        )
        assert len(data.spells) == 6

    def test_life_domain_spell_count_by_level(self):
        # SourceTexts/SubclassTexts2024/life_domain.txt - Life Domain Spells table:
        # 3: Aid, Bless, Cure Wounds, Lesser Restoration (4)
        # 5: Mass Healing Word, Revivify (2)
        # 7: Aura of Life, Death Ward (2)
        # 9: Greater Restoration, Mass Cure Wounds (2)
        # (no 13/17 tier for Life Domain)
        from CharacterContent.Classes.SubClasses2024 import ClericLife

        data = _cleric_data_with_channel_divinity()
        ClericLife.ClericLifeLevel3().add_features(data)
        assert len(data.spells) == 4
        ClericLife.ClericLifeLevel5().add_features(data)
        assert len(data.spells) == 4 + 2
        ClericLife.ClericLifeLevel7().add_features(data)
        assert len(data.spells) == 4 + 2 + 2
        ClericLife.ClericLifeLevel9().add_features(data)
        assert len(data.spells) == 4 + 2 + 2 + 2


class TestPaladinOathSpellGrantLevels:
    def test_oath_of_devotion_full_table_via_real_build(self):
        # SourceTexts/SubclassTexts2024/oath_of_devotion.txt - Oath of Devotion
        # Spells table: 3, 5, 9, 13, 17 (five tiers, two spells each = 10 total).
        data = BuildSelector.get_build("Y2024_Paladin_Devotion_ElricPactsworn").build()
        assert data.level_per_class[CharacterClass.PALADIN] >= 17
        oath_spells = {
            "Protection from Evil and Good",
            "Shield of Faith",
            "Aid",
            "Zone of Truth",
            "Beacon of Hope",
            "Dispel Magic",
            "Freedom of Movement",
            "Guardian of Faith",
            "Commune",
            "Flame Strike",
        }
        oath_grant_levels = {
            level
            for spell, _a, _r, level in data.spells
            if getattr(spell, "value", spell) in oath_spells
        }
        assert oath_grant_levels == {3, 5, 9, 13, 17}

    def test_oath_of_glory_spell_names_and_levels(self):
        # SourceTexts/SubclassTexts2024/oath_of_glory.txt - Oath of Glory Spells
        # table: 3 Guiding Bolt/Heroism, 5 Enhance Ability/Magic Weapon,
        # 9 Haste/Protection from Energy, 13 Compulsion/Freedom of Movement,
        # 17 Legend Lore/Yolande's Regal Presence. Note: no row at 7th level.
        data = BuildSelector.get_build("Y2024_Paladin_Glory_BalderSunoath").build()
        assert data.level_per_class[CharacterClass.PALADIN] == 20
        by_level = {}
        for spell, _ability, _ruling, level in data.spells:
            by_level.setdefault(level, set()).add(spell.value)
        # Subset checks (not equality): the level tag is also shared by
        # non-subclass spells granted at the same character level (e.g. feats
        # or class spells known), so extra entries at a level don't indicate
        # a problem here - only missing/misplaced Oath of Glory spells do.
        assert {"Guiding Bolt", "Heroism"} <= by_level[3]
        assert {"Enhance Ability", "Magic Weapon"} <= by_level.get(5, set())
        assert {"Haste", "Protection from Energy"} <= by_level.get(9, set())
        assert {"Compulsion", "Freedom of Movement"} <= by_level.get(13, set())
        assert {"Legend Lore", "Yolande's Regal Presence"} <= by_level.get(17, set())
        # None of the Oath of Glory spells themselves show up at 7 (the table
        # has no row there) - other level-7 entries are unrelated class spells.
        oath_of_glory_spells = {
            "Guiding Bolt",
            "Heroism",
            "Enhance Ability",
            "Magic Weapon",
            "Haste",
            "Protection from Energy",
            "Compulsion",
            "Freedom of Movement",
            "Legend Lore",
            "Yolande's Regal Presence",
        }
        assert not (oath_of_glory_spells & by_level.get(7, set()))


class TestSorcererAndWarlockSpellGrantLevels:
    def test_draconic_sorcery_spell_names_and_levels(self):
        # SourceTexts/SubclassTexts2024/draconic_sorcery.txt - Draconic Spells
        # table: 3 Alter Self/Chromatic Orb/Command/Dragon's Breath (4 spells,
        # not the usual 2 - Sorcerer subclasses start at level 3 too),
        # 5 Fear/Fly, 7 Arcane Eye/Charm Monster, 9 Legend Lore/Summon Dragon.
        #
        # Constructed directly from the builder module (rather than via a real
        # Y2024 example build) because the only level-5+ Draconic example in
        # BuildSelector (Y2024_Sorcerer_Draconic_IgnatiaEmberscale) never
        # registers SorcererDraconicLevel5 in its level map even though the
        # character is Sorcerer level 5 - see bug note in the test report.
        from CharacterContent.Classes.SubClasses2024 import SorcererDraconic

        data = CharacterSheetData(spell_casting_ability=Ability.CHARISMA)
        # set_current_grant_level mirrors what ClassBuilder.create() does before
        # calling each level's add_features(), so add_spell() tags spells with
        # the right level (see Builds/CharacterSheetAccumulator.py add_spell).
        data.set_current_grant_level(3)
        SorcererDraconic.SorcererDraconicLevel3().add_features(data)
        data.set_current_grant_level(5)
        SorcererDraconic.SorcererDraconicLevel5().add_features(data)

        by_level = {}
        for spell, _ability, _ruling, level in data.spells:
            by_level.setdefault(level, set()).add(spell.value)
        assert by_level[3] == {
            "Alter Self",
            "Chromatic Orb",
            "Command",
            "Dragon's Breath",
        }
        assert by_level[5] == {"Fear", "Fly"}

    def test_archfey_patron_never_grants_spells_past_level_9(self):
        # SourceTexts/SubclassTexts2024/archfey_patron.txt - Archfey Spells table
        # stops at Warlock level 9 (Dominate Person, Seeming); unlike Paladin
        # oaths there is no 13th/17th-level row for Warlock patrons.
        data = BuildSelector.get_build("Y2024_Warlock_Archfey_CaelumBladefey").build()
        grant_levels = {level for _, _, _, level in data.spells}
        for forbidden_level in (13, 17):
            assert forbidden_level not in grant_levels

    def test_archfey_patron_level_3_spell_names(self):
        # SourceTexts/SubclassTexts2024/archfey_patron.txt - level 3 row:
        # Calm Emotions, Faerie Fire, Misty Step, Phantasmal Force, Sleep (5).
        data = BuildSelector.get_build("Y2024_Warlock_Archfey_WrennaThornpact").build()
        level_3_spells = {
            spell.value for spell, _a, _r, level in data.spells if level == 3
        }
        # Subset: cantrips/level-1 spells known also tag as grant level 3 for
        # a level-3 Warlock, alongside the always-prepared Archfey Spells.
        assert {
            "Calm Emotions",
            "Faerie Fire",
            "Misty Step",
            "Phantasmal Force",
            "Sleep",
        } <= level_3_spells


class TestDruidCircleOfTheLandSpells:
    # SourceTexts/SubclassTexts2024/circle_of_the_land.txt - Circle Spells
    # tables, one per land type, keyed by Druid level.
    LAND_SPELLS = {
        DruidLandType.ARID: {
            3: {"Blur", "Burning Hands", "Fire Bolt"},
            5: {"Fireball"},
            7: {"Blight"},
            9: {"Wall of Stone"},
        },
        DruidLandType.POLAR: {
            3: {"Fog Cloud", "Hold Person", "Ray of Frost"},
            5: {"Sleet Storm"},
            7: {"Ice Storm"},
            9: {"Cone of Cold"},
        },
        DruidLandType.TEMPERATE: {
            3: {"Misty Step", "Shocking Grasp", "Sleep"},
            5: {"Lightning Bolt"},
            7: {"Freedom of Movement"},
            9: {"Tree Stride"},
        },
        DruidLandType.TROPICAL: {
            3: {"Acid Splash", "Ray of Sickness", "Web"},
            5: {"Stinking Cloud"},
            7: {"Polymorph"},
            9: {"Insect Plague"},
        },
    }

    LEVEL_BUILDERS = {
        3: DruidLand.DruidLandLevel3,
        5: DruidLand.DruidLandLevel5,
        7: DruidLand.DruidLandLevel7,
        9: DruidLand.DruidLandLevel9,
    }

    @pytest.mark.parametrize("land_type", list(DruidLandType))
    @pytest.mark.parametrize("level", [3, 5, 7, 9])
    def test_land_spells_by_type_and_level(self, land_type, level):
        data = CharacterSheetData(spell_casting_ability=Ability.WISDOM)
        builder_cls = self.LEVEL_BUILDERS[level]
        builder_cls(land_type=land_type).add_features(data)
        names = {spell.value for spell, _a, _r, _lvl in data.spells}
        assert names == self.LAND_SPELLS[land_type][level]


# ---------------------------------------------------------------------------
# Damage/condition resistance and immunity apply(): the codebase has a real
# pattern of subclass features whose description promises a Resistance or
# Immunity but whose apply() never calls add_damage_resistance /
# add_condition_immunity. These tests check both the ones that DO wire it up
# (so a future refactor can't silently break them) and, in the xfail section
# below, one confirmed case that doesn't.
# ---------------------------------------------------------------------------


class TestResistanceAndImmunityGrants:
    def test_psi_warrior_guarded_mind_grants_psychic_resistance(self, make_character):
        # SourceTexts/SubclassTexts2024/psi_warrior.txt, Fighter level 10:
        # "You have Resistance to Psychic damage."
        character = make_character()
        FighterPsiWarriorFeatures.GuardedMind().apply(character)
        assert character.is_resistant_to_damage(DamageType.PSYCHIC)

    def test_celestial_patron_radiant_soul_grants_radiant_resistance(
        self, make_character
    ):
        # SourceTexts/SubclassTexts2024/celestial_patron.txt, Warlock level 6:
        # "You have Resistance to Radiant damage."
        character = make_character()
        WarlockCelestialFeatures.RadiantSoul().apply(character)
        assert character.is_resistant_to_damage(DamageType.RADIANT)

    def test_winter_walker_frigid_explorer_grants_cold_resistance(self, make_character):
        # SourceTexts/SubclassTexts2024/winter_walker.txt, Ranger level 3:
        # "Frost Resistance. You have Resistance to Cold damage."
        character = make_character()
        RangerWinterWalkerFeatures.FrigidExplorer().apply(character)
        assert character.is_resistant_to_damage(DamageType.COLD)

    def test_war_domain_avatar_of_battle_grants_physical_resistances(
        self, make_character
    ):
        # SourceTexts/SubclassTexts2024/war_domain.txt, Cleric level 17:
        # "You gain Resistance to Bludgeoning, Piercing, and Slashing damage."
        character = make_character()
        ClericWarFeatures.AvatarOfBattle().apply(character)
        for damage_type in (
            DamageType.BLUDGEONING,
            DamageType.PIERCING,
            DamageType.SLASHING,
        ):
            assert character.is_resistant_to_damage(damage_type)

    def test_archfey_patron_beguiling_defenses_grants_charmed_immunity(
        self, make_character
    ):
        # SourceTexts/SubclassTexts2024/archfey_patron.txt, Warlock level 10:
        # "You are immune to the Charmed condition."
        character = make_character()
        WarlockArchfeyFeatures.BeguilingDefenses().apply(character)
        assert character.is_immune_to_condition(Condition.CHARMED)
        assert not character.is_immune_to_condition(Condition.FRIGHTENED)


class TestSorcererDraconicResilienceAndElementalAffinity:
    def test_draconic_resilience_hp_bonus_scales_with_sorcerer_level(
        self, make_character
    ):
        # SourceTexts/SubclassTexts2024/draconic_sorcery.txt: "Your Hit Point
        # maximum increases by 3, and it increases by 1 whenever you gain
        # another Sorcerer level." At Sorcerer level L (L >= 3) that is
        # 3 + (L - 3) extra hit points.
        for sorcerer_level, expected_bonus in (
            (3, 3 + (3 - 3)),
            (6, 3 + (6 - 3)),
            (12, 3 + (12 - 3)),
        ):
            character = make_character(levels={CharacterClass.SORCERER: sorcerer_level})
            SorcererDraconicFeatures.DraconicResilience().apply(character)
            assert character.combat.hit_points_bonus == expected_bonus

    def test_draconic_resilience_ac_unarmored_formula(self, make_character):
        # "While you aren't wearing armor, your base Armor Class equals 10
        # plus your Dexterity and Charisma modifiers." DEX 14 (+2), CHA 16 (+3).
        character = make_character(
            dexterity=14, charisma=16, levels={CharacterClass.SORCERER: 3}
        )
        SorcererDraconicFeatures.DraconicResilience().apply(character)
        assert character.calculate_armor_class() == 10 + 2 + 3

    def test_elemental_affinity_grants_a_resistance(self, make_character):
        character = make_character(levels={CharacterClass.SORCERER: 6}, charisma=16)
        SorcererDraconicFeatures.ElementalAffinity(DamageType.COLD).apply(character)
        assert character.is_resistant_to_damage(DamageType.COLD)
        assert not character.is_resistant_to_damage(DamageType.FIRE)

    def test_elemental_affinity_rejects_non_draconic_type(self):
        # Only Acid, Cold, Fire, Lightning, or Poison may be chosen.
        with pytest.raises(ValueError):
            SorcererDraconicFeatures.ElementalAffinity(DamageType.RADIANT)


# ---------------------------------------------------------------------------
# Resource counts (number_of_uses) that scale with an ability modifier.
# ---------------------------------------------------------------------------


class TestChaModifierResourceCounts:
    @pytest.mark.parametrize(
        "feature_cls",
        [WarlockArchfeyFeatures.StepsOfTheFey, WarlockFiendFeatures.DarkOnesOwnLuck],
        ids=["StepsOfTheFey", "DarkOnesOwnLuck"],
    )
    @pytest.mark.parametrize(
        "charisma,expected_uses",
        [(8, 1), (10, 1), (16, 3), (18, 4)],
        ids=["cha8_min1", "cha10_min1", "cha16", "cha18"],
    )
    def test_uses_equal_charisma_modifier_minimum_one(
        self, make_character, feature_cls, charisma, expected_uses
    ):
        # Both features read: "a number of times equal to your Charisma
        # modifier (minimum of once)". CHA 8/10 -> mod 0/-1 (still 1 use), 16
        # -> mod 3, 18 -> mod 4.
        character = make_character(charisma=charisma)
        assert feature_cls().number_of_uses(character) == expected_uses


class TestFighterBattleMasterSuperiorityDice:
    # SourceTexts/SubclassTexts2024/battle_master.txt, Combat Superiority:
    # "You have four Superiority Dice... You gain an additional Superiority
    # Die when you reach Fighter levels 7 (five dice total) and 15 (six dice
    # total)." Die size: d8 up to level 9, d10 at 10-17, d12 at 18+ (Improved/
    # Ultimate Combat Superiority).

    @pytest.mark.parametrize(
        "fighter_level,expected_dice",
        [
            pytest.param(3, 4),
            pytest.param(6, 4),
            pytest.param(7, 5),
            pytest.param(14, 5),
            pytest.param(15, 6),  # correct even under the bug: max_uses IS 6 here
            pytest.param(20, 6),  # correct even under the bug: max_uses IS 6 here
        ],
    )
    def test_number_of_superiority_dice_by_level(
        self, make_character, fighter_level, expected_dice
    ):
        character = make_character(levels={CharacterClass.FIGHTER: fighter_level})
        feature = FighterBattleMasterFeatures.SuperiorityDice()
        feature.apply(character)
        assert feature.number_of_uses(character) == expected_dice

    def test_die_size_uses_fighter_class_level_not_character_level(
        self, make_character
    ):
        # Fighter 3 / Wizard 15 (character level 18, Fighter class level 3):
        # the die size must key off Fighter class level, not total character
        # level, or this multiclass would incorrectly show a d12.
        character = make_character(
            levels={CharacterClass.FIGHTER: 3, CharacterClass.WIZARD: 15}
        )
        description = FighterBattleMasterFeatures.SuperiorityDice().get_description(
            character
        )
        assert "1d8" in description
        assert "1d12" not in description


class TestBladesingerTrainingInWarAndSongWeaponProficiency:
    def test_training_in_war_and_song_grants_martial_weapon_proficiency(self):
        data = BuildSelector.get_build(
            "Y2024_Wizard_Bladesinger_IlyanaBladesong"
        ).build()
        from CharacterContent.Items.Weapons.Base import is_proficient_with
        from CharacterContent.Items.Weapons.MartialMelee import Scimitar

        # Scimitar: Martial Melee, Finesse + Light (no Two-Handed/Heavy), so a
        # Bladesinger with Training in War and Song should be proficient.
        assert is_proficient_with(Scimitar(), data.weapon_proficiencies)


# ---------------------------------------------------------------------------
# Skill/saving-throw proficiency and expertise grants (Feature.apply wiring).
# ---------------------------------------------------------------------------


class TestSkillAndSavingThrowGrants:
    def test_college_of_lore_bonus_proficiencies_grants_three_chosen_skills(
        self, make_character
    ):
        # SourceTexts/SubclassTexts2024/college_of_lore.txt, Bard level 3:
        # "You gain proficiency with three skills of your choice."
        character = make_character()
        BardLoreFeatures.BonusProficiencies(
            Skill.ARCANA, Skill.PERSUASION, Skill.SURVIVAL
        ).apply(character)
        assert character.is_proficient_in_skill(Skill.ARCANA)
        assert character.is_proficient_in_skill(Skill.PERSUASION)
        assert character.is_proficient_in_skill(Skill.SURVIVAL)
        assert not character.is_proficient_in_skill(Skill.STEALTH)

    def test_knowledge_domain_blessings_grants_proficiency_and_expertise(
        self, make_character
    ):
        # SourceTexts/SubclassTexts2024/knowledge_domain.txt, Cleric level 3:
        # "...in two of the following skills of your choice: Arcana, History,
        # Nature, or Religion. You have Expertise in those two skills."
        character = make_character()
        ClericKnowledgeFeatures.BlessingsOfKnowledge(
            Skill.ARCANA, Skill.RELIGION
        ).apply(character)
        assert character.is_proficient_in_skill(Skill.ARCANA)
        assert character.is_proficient_in_skill(Skill.RELIGION)
        assert character.has_expertise_in_skill(Skill.ARCANA)
        assert character.has_expertise_in_skill(Skill.RELIGION)
        assert not character.has_expertise_in_skill(Skill.HISTORY)

    def test_knowledge_domain_blessings_rejects_skill_outside_the_pool(self):
        # Only Arcana, History, Nature, or Religion are allowed choices.
        with pytest.raises(ValueError):
            ClericKnowledgeFeatures.BlessingsOfKnowledge(Skill.ARCANA, Skill.STEALTH)

    def test_unfettered_mind_grants_intelligence_save_first(self, make_character):
        # SourceTexts/SubclassTexts2024/knowledge_domain.txt, Cleric level 6:
        # "you gain proficiency in Intelligence saving throws."
        character = make_character()
        ClericKnowledgeFeatures.UnfetteredMind().apply(character)
        assert character.is_proficient_in_saving_throw(Ability.INTELLIGENCE)

    def test_unfettered_mind_falls_back_when_int_already_proficient(
        self, make_character
    ):
        # "If you already have this proficiency, you instead gain saving
        # throw proficiency with one ability in which you lack it."
        character = make_character()
        character.add_proficiency_in_saving_throw(Ability.INTELLIGENCE)
        ClericKnowledgeFeatures.UnfetteredMind().apply(character)
        # STRENGTH is first in the fallback list after INTELLIGENCE.
        assert character.is_proficient_in_saving_throw(Ability.STRENGTH)


class TestInitiativeAndSkillRollConditionGrants:
    def test_gloom_stalker_dread_ambusher_initiative_bonus_equals_wisdom_mod(
        self, make_character
    ):
        # SourceTexts/SubclassTexts2024/gloom_stalker.txt, Ranger level 3:
        # "Initiative Bonus. When you roll Initiative, you can add your
        # Wisdom modifier to the roll." WIS 16 -> +3, DEX 10 -> +0.
        character = make_character(wisdom=16)
        RangerGloomStalkerFeatures.DreadAmbusher().apply(character)
        assert character.initiative == 0 + 3

    def test_champion_remarkable_athlete_initiative_and_athletics_advantage(
        self, make_character
    ):
        # SourceTexts/SubclassTexts2024/champion.txt, Fighter level 3:
        # "you have Advantage on Initiative rolls and Strength (Athletics)
        # checks."
        character = make_character()
        FighterChampionFeatures.RemarkableAthlete().apply(character)
        assert character.initiative_roll_condition == DiceRollCondition.ADVANTAGE
        assert character.get_skill_roll_condition(Skill.ATHLETICS) == (
            DiceRollCondition.ADVANTAGE
        )
        assert character.get_skill_roll_condition(Skill.ACROBATICS) == (
            DiceRollCondition.NEUTRAL
        )


class TestDruidLandsAidDamageDiceScaling:
    # SourceTexts/SubclassTexts2024/circle_of_the_land.txt, Land's Aid:
    # "taking 2d6 Necrotic damage... The damage and healing increase by 1d6
    # when you reach Druid levels 10 (3d6) and 14 (4d6)."
    @pytest.mark.parametrize(
        "druid_level,expected_dice",
        [(3, "2d6"), (9, "2d6"), (10, "3d6"), (13, "3d6"), (14, "4d6"), (20, "4d6")],
    )
    def test_lands_aid_dice_by_druid_level(
        self, make_character, druid_level, expected_dice
    ):
        character = make_character(levels={CharacterClass.DRUID: druid_level})
        table = dict(DruidLandFeatures.LandsAid().get_table_description(character))
        assert expected_dice in table["Damage"]
        assert expected_dice in table["Healing"]


class TestBladesingerWeaponProficiencyScope:
    # "proficiency with all Melee Martial weapons that don't have the
    # Two-Handed or Heavy property"
    @pytest.mark.parametrize(
        "weapon_name, expected",
        [
            ("Scimitar", True),  # Finesse, Light
            ("Longsword", True),  # Versatile only
            ("Rapier", True),  # Finesse
            ("Greatsword", False),  # Heavy, Two-Handed
            ("Glaive", False),  # Heavy, Two-Handed, Reach
        ],
    )
    def test_martial_melee_not_heavy_or_two_handed(self, weapon_name, expected):
        from CharacterContent.Items.Weapons import MartialMelee
        from CharacterContent.Items.Weapons.Base import weapon_matches_proficiency
        from CharacterContent.Items.Weapons.Enums import WeaponProficiency

        weapon = getattr(MartialMelee, weapon_name)()
        assert (
            weapon_matches_proficiency(
                weapon, WeaponProficiency.MARTIAL_MELEE_NOT_HEAVY_OR_TWO_HANDED
            )
            == expected
        )

    def test_does_not_cover_martial_ranged(self):
        from CharacterContent.Items.Weapons import Ranged
        from CharacterContent.Items.Weapons.Base import weapon_matches_proficiency
        from CharacterContent.Items.Weapons.Enums import WeaponProficiency

        # Hand Crossbow is Light, but ranged - not a Melee Martial weapon.
        assert not weapon_matches_proficiency(
            Ranged.HandCrossbow(),
            WeaponProficiency.MARTIAL_MELEE_NOT_HEAVY_OR_TWO_HANDED,
        )
