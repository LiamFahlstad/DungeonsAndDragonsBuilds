"""
2014-edition subclass features: CharacterContent/Features/SubClassFeatures2014/
and the subclass builders in CharacterContent/Classes/SubClasses2014/.

Expected values come from the 2014 Player's Handbook, Xanathar's Guide to
Everything, and Tasha's Cauldron of Everything - see SourceTexts/SubclassTexts2014/
for the source text of several subclasses quoted below - never from running the
engine and reading off its output.

House rules (2024 engine running 2014 content):
  - Every subclass starts at level 3 (ClassBuilder.SubclassLevel3), even where
    the 2014 rules grant it at 1st (Cleric, Sorcerer, Warlock) or 2nd (Wizard,
    Druid) level. See TestSubclassesStartAtLevel3.
  - A 2014 subclass that was reprinted in 2024 (including renames, e.g.
    Evocation -> Evoker) is deleted; only the 2024 version exists.
"""

import pytest

from RunCharacterCreator import ExampleSelector

from Builds.CharacterSheetAccumulator import CharacterSheetData
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.SubClasses2014.ClericDeath import ClericDeathLevel3
from CharacterContent.Classes.SubClasses2014.ClericForge import (
    ClericForgeLevel3,
    ClericForgeLevel6,
)
from CharacterContent.Classes.SubClasses2014.ClericNature import ClericNatureLevel3
from CharacterContent.Classes.SubClasses2014.ClericOrder import ClericOrderLevel3
from CharacterContent.Classes.SubClasses2014.ClericTempest import ClericTempestLevel3
from CharacterContent.Classes.SubClasses2014.ClericTwilight import ClericTwilightLevel3
from CharacterContent.Classes.SubClasses2014.DruidCircleOfDreams import (
    DruidDreamsLevel3,
)
from CharacterContent.Classes.SubClasses2014.FighterRuneKnight import (
    FighterRuneKnightLevel3,
    FighterRuneKnightLevel7,
    FighterRuneKnightLevel10,
    FighterRuneKnightLevel15,
    FighterRuneKnightLevel18,
)
from CharacterContent.Features.SubClassFeatures2014.Bard import BardWhispersFeatures
from CharacterContent.Features.SubClassFeatures2014.Cleric import (
    ClericDeathFeatures,
    ClericForgeFeatures,
    ClericNatureFeatures,
    ClericOrderFeatures,
    ClericTempestFeatures,
    ClericTwilightFeatures,
)
from CharacterContent.Features.SubClassFeatures2014.Druid import (
    DruidDreamsFeatures,
    DruidSporesFeatures,
)
from CharacterContent.Features.SubClassFeatures2014.Fighter import (
    FighterRuneKnightFeatures,
    FighterSamuraiFeatures,
)
from CharacterContent.Features.SubClassFeatures2014.Paladin import (
    PaladinConquestFeatures,
    PaladinRedemptionFeatures,
)
from CharacterContent.Features.SubClassFeatures2014.Rogue import RogueScoutFeatures
from CharacterContent.Features.SubClassFeatures2014.Sorcerer import (
    SorcererStormSorceryFeatures,
)
from CharacterContent.Classes.SubClasses2014.WarlockHexblade import (
    WarlockHexbladeLevel3,
)
from CharacterContent.Classes.SubClasses2014.WizardNecromancy import (
    WizardNecromancyLevel3,
)
from CharacterContent.Features.SubClassFeatures2014.Warlock import (
    WarlockHexbladeFeatures,
)
from CharacterContent.Features.SubClassFeatures2014.Wizard import (
    WizardNecromancyFeatures,
)
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Items import Armor
from CharacterContent.Items.Weapons.Enums import WeaponProficiency
from Core.Definitions import ArmorType, CharacterClass, DamageType


def bug(reason):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


def features_at(
    level_features_class, character_class: CharacterClass, class_level: int
):
    """Run one subclass Level<N> builder's add_features against a fresh sheet
    whose only fact is that `character_class` is at `class_level`, mirroring
    what BaseClassLevelFeatures.add_features does for a single level entry
    without needing a full StarterClassBuilder."""
    data = CharacterSheetData(level_per_class={character_class: class_level})
    blf = ClassBuilder.BaseClassLevelFeatures(
        base_class_features_by_level={},
        subclass_features_by_level={
            level_features_class().level: level_features_class()
        },
    )
    blf.add_features(data, character_class, ClassBuilder.AppliedLevelFeatures())
    return data


# ── Subclass-selection level: always 3 (house rule) ─────────────────────────


class TestSubclassesStartAtLevel3:
    """2024 engine house rule: every 2014 subclass is gained at class level 3,
    including the classes whose 2014 rules grant it earlier (Cleric, Sorcerer,
    Warlock at 1st; Wizard, Druid at 2nd)."""

    @pytest.mark.parametrize(
        "level_features, character_class, feature_type",
        [
            (
                ClericForgeLevel3,
                CharacterClass.CLERIC,
                ClericForgeFeatures.BonusProficiencies,
            ),
            (
                WarlockHexbladeLevel3,
                CharacterClass.WARLOCK,
                WarlockHexbladeFeatures.HexbladesCurse,
            ),
            (
                WizardNecromancyLevel3,
                CharacterClass.WIZARD,
                WizardNecromancyFeatures.GrimHarvest,
            ),
            (
                DruidDreamsLevel3,
                CharacterClass.DRUID,
                DruidDreamsFeatures.BalmOfTheSummerCourt,
            ),
        ],
    )
    def test_first_subclass_feature_arrives_at_level_3(
        self, level_features, character_class, feature_type
    ):
        for early_level in (1, 2):
            data = features_at(level_features, character_class, early_level)
            assert not data.get_features_by_type(feature_type)
        data = features_at(level_features, character_class, 3)
        assert data.get_features_by_type(feature_type)


# ── Cleric domain "Bonus Proficiency"/"Bonus Proficiencies": text vs wiring ────


class TestClericDomainBonusProficienciesNotWired:
    """Every 2014 Cleric domain below grants a proficiency as its very first
    feature ("You gain proficiency with heavy armor[...]", per each feature's
    own get_description()). CharacterSheetData.add_armor_proficiency /
    add_weapon_proficiency exist and are used by other subclasses (e.g.
    SubClasses2024/BardValor.py calls add_armor_proficiency directly), but none
    of the Cleric domain builder files below ever call them - the promised
    proficiency never reaches the sheet's proficiency set."""

    def test_forge_domain_heavy_armor(self):
        data = features_at(ClericForgeLevel3, CharacterClass.CLERIC, 3)
        assert ArmorType.HEAVY in data.armor_proficiencies

    def test_tempest_domain_heavy_armor_and_martial_weapons(self):
        data = features_at(ClericTempestLevel3, CharacterClass.CLERIC, 3)
        assert ArmorType.HEAVY in data.armor_proficiencies
        assert WeaponProficiency.MARTIAL in data.weapon_proficiencies

    def test_nature_domain_heavy_armor(self):
        data = features_at(ClericNatureLevel3, CharacterClass.CLERIC, 3)
        assert ArmorType.HEAVY in data.armor_proficiencies

    def test_order_domain_heavy_armor(self):
        data = features_at(ClericOrderLevel3, CharacterClass.CLERIC, 3)
        assert ArmorType.HEAVY in data.armor_proficiencies

    def test_twilight_domain_heavy_armor_and_martial_weapons(self):
        data = features_at(ClericTwilightLevel3, CharacterClass.CLERIC, 3)
        assert ArmorType.HEAVY in data.armor_proficiencies
        assert WeaponProficiency.MARTIAL in data.weapon_proficiencies

    def test_death_domain_martial_weapons(self):
        data = features_at(ClericDeathLevel3, CharacterClass.CLERIC, 3)
        assert WeaponProficiency.MARTIAL in data.weapon_proficiencies


# ── Blessed Strikes: the 2024 base feature replaces the 2014 domain version ───


def _example_build(file_stem: str):
    builder_name = file_stem.replace("_", "") + "CharacterBuilder"
    return ExampleSelector.builds()[builder_name]


class TestBlessedStrikesComesFromBaseClassOnly:
    """House rule: the 2024 base Cleric's level-7 Blessed Strikes (Divine Strike
    or Potent Spellcasting) overrides every 2014 domain's level-8 Divine Strike
    / Potent Spellcasting, so a 2014-domain Cleric has exactly one of them."""

    @pytest.mark.parametrize(
        "example",
        [
            "Y2014_Cleric_Arcana_PeregrineStarbind",
            "Y2014_Cleric_Death_MortimerGrimvale",
            "Y2014_Cleric_Forge_BrennaHearthforge",
            "Y2014_Cleric_Nature_WillowdaleFernstep",
            "Y2014_Cleric_Order_CastellanTrueward",
            "Y2014_Cleric_Peace_HalcyonMeadowlight",
            "Y2014_Cleric_Tempest_StormWavecrest",
            "Y2014_Cleric_Twilight_VesperNightsong",
        ],
    )
    def test_single_blessed_strike(self, example):
        data = _example_build(example).build()
        strikes = [
            f
            for f in data.features
            if f.name in ("Divine Strike", "Potent Spellcasting")
        ]
        assert len(strikes) == 1

    def test_orders_wrath_rides_on_base_divine_strike(self):
        data = _example_build("Y2014_Cleric_Order_CastellanTrueward").build()
        base_strikes = data.get_features_by_type(ClericFeatures.DivineStrike)
        if base_strikes:
            assert any(
                isinstance(child, ClericOrderFeatures.OrdersWrath)
                for child in base_strikes[0].extensions
            )


# ── Limited-use resources: FeatureUses/number_of_uses/regained_on wiring ──────


class TestLimitedUseResourcesNotWired:
    """A feature with a fixed number of uses per rest should set
    uses=FeatureUses(...) in __init__ (as e.g. RunicShield right next to
    GiantsMight does) so number_of_uses()/regained_on() reflect it generically,
    not just describe it in prose/get_table_description() text."""

    def test_giants_might_uses_equal_proficiency_bonus(self, make_character):
        character = make_character(levels={CharacterClass.FIGHTER: 3})  # PB +2
        feature = FighterRuneKnightFeatures.GiantsMight()
        assert feature.number_of_uses(character) == 2

    def test_fighting_spirit_three_uses(self, make_character):
        character = make_character(levels={CharacterClass.FIGHTER: 3})
        feature = FighterSamuraiFeatures.FightingSpirit()
        assert feature.number_of_uses(character) == 3

    def test_runic_shield_uses_correctly_equal_proficiency_bonus(self, make_character):
        # Control: the very next Rune Knight feature does wire this correctly.
        character = make_character(levels={CharacterClass.FIGHTER: 7})  # PB +3
        feature = FighterRuneKnightFeatures.RunicShield()
        assert feature.number_of_uses(character) == 3

    def test_fungal_infestation_minimum_one_use(self, make_character):
        character = make_character(wisdom=10, levels={CharacterClass.DRUID: 6})
        feature = DruidSporesFeatures.FungalInfestation()
        assert feature.number_of_uses(character) == 1


# ── Missing apply(): promised passive bonuses that never touch the sheet ──────


class TestPromisedPassiveBonusNeverApplied:
    def test_soul_of_the_forge_ac_bonus_while_wearing_heavy_armor(self, make_character):
        character = make_character(strength=15, levels={CharacterClass.CLERIC: 6})
        feature = ClericForgeFeatures.SoulOfTheForge()
        feature.apply(character)
        armor = Armor.PlateArmor()
        armor.apply(character)
        feature.apply_after_armor(character)
        assert character.calculate_armor_class() == 19  # Plate 18 + 1

    def test_soul_of_the_forge_fire_resistance_is_applied(self, make_character):
        # Control: the other half of the same feature IS wired correctly.
        character = make_character(levels={CharacterClass.CLERIC: 6})
        feature = ClericForgeFeatures.SoulOfTheForge()
        feature.apply(character)
        assert character.is_resistant_to_damage(DamageType.FIRE)

    def test_superior_mobility_speed_increase(self, make_character):
        character = make_character(levels={CharacterClass.ROGUE: 9})
        feature = RogueScoutFeatures.SuperiorMobility()
        feature.apply(character)
        assert character.combat.speed == 40

    def test_survivalist_proficiency_and_expertise_are_applied(self, make_character):
        # Control: the earlier Scout feature correctly wires both grants.
        from Core.Definitions import Skill

        character = make_character(
            intelligence=10, wisdom=10, levels={CharacterClass.ROGUE: 3}
        )  # PB +2
        feature = RogueScoutFeatures.Survivalist()
        feature.apply(character)
        assert character.is_proficient_in_skill(Skill.NATURE)
        assert character.is_proficient_in_skill(Skill.SURVIVAL)
        # Expertise doubles proficiency bonus: 0 (WIS/INT mod) + 2*PB(2) = 4.
        assert character.get_skill_modifier(Skill.NATURE) == 4
        assert character.get_skill_modifier(Skill.SURVIVAL) == 4


# ── character_level vs get_class_level: multiclass scaling bugs ───────────────
#
# All four features below scale off "your <class> level" per their own prose,
# but read character_stat_block.character_level (the *total* level across every
# class) instead of get_class_level(<that class>). Multiclassing is required to
# tell the two apart; each test picks a dip that keeps the class level low while
# character_level is high, so a fix would change the result.


class TestClassLevelVsCharacterLevelScaling:
    def test_psychic_blades_scales_with_bard_level_not_total_level(
        self, make_character
    ):
        character = make_character(
            levels={CharacterClass.BARD: 5, CharacterClass.FIGHTER: 10}
        )
        feature = BardWhispersFeatures.PsychicBlades()
        description = feature.get_description(character)
        assert "3d6 psychic damage" in description

    def test_aura_of_conquest_scales_with_paladin_level_not_total_level(
        self, make_character
    ):
        character = make_character(
            levels={CharacterClass.PALADIN: 7, CharacterClass.ROGUE: 13}
        )
        feature = PaladinConquestFeatures.AuraOfConquest()
        table = dict(feature.get_table_description(character))
        assert table["Damage"] == "Psychic damage = half paladin level (3)"

    def test_protective_spirit_scales_with_paladin_level_not_total_level(
        self, make_character
    ):
        character = make_character(
            levels={CharacterClass.PALADIN: 15, CharacterClass.ROGUE: 5}
        )
        feature = PaladinRedemptionFeatures.ProtectiveSpirit()
        table = dict(feature.get_table_description(character))
        assert table["Effect"] == "Regain 1d6 + 7 HP"


# ── extend_feature wiring: a feature learned later augments an earlier one ────


class TestExtendFeatureWiring:
    """Rune Knight layers Great Stature (level 10) and Runic Juggernaut (level
    18) onto the original Giant's Might feature object, and Master of Runes
    (level 15) onto Rune Carver, via Feature.extend_feature - not by adding a
    new top-level feature. Verify both the wiring and BaseClassLevelFeatures'
    level-gating: a level-10 Rune Knight has Great Stature but not Runic
    Juggernaut yet."""

    def _build_up_to(self, fighter_level: int) -> CharacterSheetData:
        data = CharacterSheetData(
            level_per_class={CharacterClass.FIGHTER: fighter_level}
        )
        blf = ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={},
            subclass_features_by_level={
                3: FighterRuneKnightLevel3(),
                7: FighterRuneKnightLevel7(),
                10: FighterRuneKnightLevel10(),
                15: FighterRuneKnightLevel15(),
                18: FighterRuneKnightLevel18(),
            },
        )
        blf.add_features(
            data, CharacterClass.FIGHTER, ClassBuilder.AppliedLevelFeatures()
        )
        return data

    def test_giants_might_has_no_extensions_before_level_10(self):
        data = self._build_up_to(7)
        giants_might = data.get_features_by_type(FighterRuneKnightFeatures.GiantsMight)[
            0
        ]
        assert giants_might.extensions == []

    def test_giants_might_gains_great_stature_at_level_10(self):
        data = self._build_up_to(10)
        giants_might = data.get_features_by_type(FighterRuneKnightFeatures.GiantsMight)[
            0
        ]
        extension_types = [type(f) for f in giants_might.extensions]
        assert extension_types == [FighterRuneKnightFeatures.GreatStature]

    def test_giants_might_gains_runic_juggernaut_at_level_18(self):
        data = self._build_up_to(18)
        giants_might = data.get_features_by_type(FighterRuneKnightFeatures.GiantsMight)[
            0
        ]
        extension_types = [type(f) for f in giants_might.extensions]
        assert extension_types == [
            FighterRuneKnightFeatures.GreatStature,
            FighterRuneKnightFeatures.RunicJuggernaut,
        ]

    def test_rune_carver_gains_master_of_runes_at_level_15_not_before(self):
        data_before = self._build_up_to(14)
        rune_carver = data_before.get_features_by_type(
            FighterRuneKnightFeatures.RuneCarver
        )[0]
        assert rune_carver.extensions == []

        data_after = self._build_up_to(15)
        rune_carver = data_after.get_features_by_type(
            FighterRuneKnightFeatures.RuneCarver
        )[0]
        assert [type(f) for f in rune_carver.extensions] == [
            FighterRuneKnightFeatures.MasterOfRunes
        ]


# ── Sanity checks on other correctly-wired mechanical effects (breadth) ───────


class TestOtherCorrectlyWiredEffects:
    def test_heart_of_the_storm_grants_lightning_and_thunder_resistance(
        self, make_character
    ):
        # Storm Sorcery (Sorcerer 6) text: "You gain resistance to lightning
        # and thunder damage."
        character = make_character(levels={CharacterClass.SORCERER: 6})
        feature = SorcererStormSorceryFeatures.HeartOfTheStorm()
        feature.apply(character)
        assert character.is_resistant_to_damage(DamageType.LIGHTNING)
        assert character.is_resistant_to_damage(DamageType.THUNDER)
        assert not character.is_resistant_to_damage(DamageType.FIRE)

    def test_fungal_body_grants_condition_immunities(self, make_character):
        # Circle of Spores (Druid 14) text: "you can't be blinded, deafened,
        # frightened, or poisoned".
        from Core.Definitions import Condition

        character = make_character(levels={CharacterClass.DRUID: 14})
        feature = DruidSporesFeatures.FungalBody()
        feature.apply(character)
        assert character.is_immune_to_condition(Condition.BLINDED)
        assert character.is_immune_to_condition(Condition.DEAFENED)
        assert character.is_immune_to_condition(Condition.FRIGHTENED)
        assert character.is_immune_to_condition(Condition.POISONED)
        assert not character.is_immune_to_condition(Condition.CHARMED)
