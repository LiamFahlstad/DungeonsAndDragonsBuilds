"""
CharacterContent/Species/ (SpeciesBuilder.py, each Species/*.py builder, and the
CharacterContent/Features/SpeciesFeatures/*.py feature classes they assemble).

Expected values come from the species rules text reproduced in
CharacterContent/Species/species.txt (2024 Player's Handbook for the "common"
species, Eberron: Heroes of Eberron for Changeling/Kalashtar/Khoravar/Shifter/
Warforged, and Ravenloft: The Horrors Within for Dhampir/Hexblood/Lupin/Reborn),
never from running the engine and copying its output.

Key 2014-vs-2024 note: the 2014 PHB granted ability score increases per species
(e.g. Dwarf +2 Constitution, Hill Dwarf +1 Wisdom). The 2024 PHB moved all
ability score increases to Background instead, so a 2024-style species must
never touch ability scores. Every builder here is written to the 2024 rule
(confirmed by grep: no Species file references AbilityScoreBonus);
TestSpeciesNeverChangeAbilityScores asserts that directly.
"""

import pytest

from CharacterContent.Features.CharacterFeats import OriginFeats
from CharacterContent.Features.SpeciesFeatures import (
    AasimarFeatures,
    ChangelingFeatures,
    DhampirFeatures,
    DragonbornFeatures,
    DwarfFeatures,
    ElfFeatures,
    GnomeFeatures,
    GoliathFeatures,
    HexbloodFeatures,
    HumanFeatures,
    KalashtarFeatures,
    RebornFeatures,
    ShifterFeatures,
    TieflingFeatures,
    WarForgedFeatures,
)
from CharacterContent.Species.Aasimar import AasimarSpeciesBuilder
from CharacterContent.Species.Changeling import ChangelingSpeciesBuilder
from CharacterContent.Species.Dhampir import DhampirSpeciesBuilder
from CharacterContent.Species.Dragonborn import DragonbornSpeciesBuilder
from CharacterContent.Species.Dwarf import DwarfSpeciesBuilder
from CharacterContent.Species.Elf import ElfSpeciesBuilder, ElvenLineage
from CharacterContent.Species.Gnome import (
    ForestGnomeSpeciesBuilder,
    RockGnomeSpeciesBuilder,
)
from CharacterContent.Species.Goliath import GoliathSpeciesBuilder
from CharacterContent.Species.Halfling import HalflingSpeciesBuilder
from CharacterContent.Species.Hexblood import HexbloodSpeciesBuilder
from CharacterContent.Species.Human import HumanSpeciesBuilder
from CharacterContent.Species.Kalashtar import KalashtarSpeciesBuilder
from CharacterContent.Species.Khoravar import KhoravarSpeciesBuilder
from CharacterContent.Species.Lupin import LupinSpeciesBuilder
from CharacterContent.Species.Orc import OrcSpeciesBuilder
from CharacterContent.Species.Reborn import RebornSpeciesBuilder
from CharacterContent.Species.Shifter import ShifterSpeciesBuilder
from CharacterContent.Species.Tiefling import FiendishLineage, TieflingSpeciesBuilder
from CharacterContent.Species.Warforged import WarforgedSpeciesBuilder
from Core.Definitions import (
    Ability,
    CharacterClass,
    CreatureSize,
    DamageType,
    Sense,
    Skill,
)


def bug(reason):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


def spell_names(data) -> list[str]:
    return [s[0] for s in data.spells]


# ── Speed & size (fixed-size species) ───────────────────────────────────────


FIXED_SIZE_SPECIES = [
    pytest.param(
        lambda: DwarfSpeciesBuilder().build(), 30, CreatureSize.MEDIUM, id="dwarf"
    ),
    pytest.param(
        lambda: HalflingSpeciesBuilder().build(), 30, CreatureSize.SMALL, id="halfling"
    ),
    pytest.param(
        lambda: OrcSpeciesBuilder().build(), 30, CreatureSize.MEDIUM, id="orc"
    ),
    pytest.param(
        lambda: GoliathSpeciesBuilder(
            GoliathFeatures.GiantAncestryType.HILL_GIANT
        ).build(),
        35,
        CreatureSize.MEDIUM,
        id="goliath",
    ),
    pytest.param(
        lambda: KalashtarSpeciesBuilder().build(),
        30,
        CreatureSize.MEDIUM,
        id="kalashtar",
    ),
    pytest.param(
        lambda: DragonbornSpeciesBuilder(DragonbornFeatures.DragonColor.RED).build(),
        30,
        CreatureSize.MEDIUM,
        id="dragonborn",
    ),
    pytest.param(
        lambda: ForestGnomeSpeciesBuilder(Ability.INTELLIGENCE).build(),
        30,
        CreatureSize.SMALL,
        id="forest_gnome",
    ),
    pytest.param(
        lambda: RockGnomeSpeciesBuilder().build(),
        30,
        CreatureSize.SMALL,
        id="rock_gnome",
    ),
]


class TestFixedSpeedAndSize:
    @pytest.mark.parametrize("build, expected_speed, expected_size", FIXED_SIZE_SPECIES)
    def test_speed_and_size(self, build, expected_speed, expected_size):
        data = build()
        assert data.speed == expected_speed
        assert data.size == expected_size


class TestChoosableSizeSpecies:
    """PHB 2024 / Heroes of Eberron / Ravenloft: several species let the player
    choose Medium or Small. The builder must faithfully reflect whichever size
    is passed in, not silently default to one."""

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_changeling_size_choice(self, size):
        data = ChangelingSpeciesBuilder(
            size=size, instinct_skills=[Skill.DECEPTION, Skill.INSIGHT]
        ).build()
        assert data.size == size
        assert data.speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_khoravar_size_choice(self, size):
        data = KhoravarSpeciesBuilder(
            size=size,
            skill_versatility=Skill.PERSUASION,
            spell_casting_ability=Ability.CHARISMA,
        ).build()
        assert data.size == size
        assert data.speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_shifter_size_choice(self, size):
        data = ShifterSpeciesBuilder(
            skill=Skill.ATHLETICS,
            size=size,
            shifter_form=ShifterFeatures.ShiftForm.SWIFTSTRIDE,
        ).build()
        assert data.size == size
        assert data.speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_lupin_size_choice(self, size):
        data = LupinSpeciesBuilder(
            size=size, werewolf_instincts_skill=Skill.PERCEPTION
        ).build()
        assert data.size == size
        assert data.speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_dhampir_size_choice_does_not_affect_speed(self, size):
        # Dhampir speed is a fixed 35 ft regardless of size (Ravenloft: The
        # Horrors Within), unlike most other species where speed never varies
        # with the size choice either.
        data = DhampirSpeciesBuilder(character_level=1, size=size).build()
        assert data.size == size
        assert data.speed == 35

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_hexblood_size_choice(self, size):
        data = HexbloodSpeciesBuilder(
            size=size, spell_casting_ability=Ability.WISDOM
        ).build()
        assert data.size == size
        assert data.speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_reborn_size_choice(self, size):
        data = RebornSpeciesBuilder(
            size=size,
            knowledge_skill=Skill.HISTORY,
            strange_endurance=DamageType.COLD,
        ).build()
        assert data.size == size
        assert data.speed == 30


# ── Darkvision ranges ────────────────────────────────────────────────────────


class TestDarkvision:
    def test_dwarf_darkvision_120(self, make_character):
        character = make_character()
        DwarfFeatures.Darkvision().apply(character)
        assert character.get_sense_range(Sense.DARKVISION) == 120

    def test_orc_darkvision_120(self, make_character):
        from CharacterContent.Features.SpeciesFeatures import OrcFeatures

        character = make_character()
        OrcFeatures.Darkvision().apply(character)
        assert character.get_sense_range(Sense.DARKVISION) == 120

    def test_gnome_darkvision_60(self, make_character):
        character = make_character()
        GnomeFeatures.Darkvision().apply(character)
        assert character.get_sense_range(Sense.DARKVISION) == 60

    def test_aasimar_darkvision_60(self, make_character):
        character = make_character()
        AasimarFeatures.Darkvision().apply(character)
        assert character.get_sense_range(Sense.DARKVISION) == 60

    def test_tiefling_darkvision_60(self, make_character):
        character = make_character()
        TieflingFeatures.Darkvision(60).apply(character)
        assert character.get_sense_range(Sense.DARKVISION) == 60

    def test_dhampir_darkvision_60(self, make_character):
        character = make_character()
        DhampirFeatures.Darkvision().apply(character)
        assert character.get_sense_range(Sense.DARKVISION) == 60

    def test_hexblood_darkvision_60(self, make_character):
        character = make_character()
        HexbloodFeatures.Darkvision().apply(character)
        assert character.get_sense_range(Sense.DARKVISION) == 60


# ── Elf lineages: darkvision, cantrip, and level-gated spells ───────────────


ELF_LINEAGES = [
    pytest.param(
        ElvenLineage.DROW,
        120,
        "Dancing Lights",
        "Faerie Fire",
        "Darkness",
        id="drow",
    ),
    pytest.param(
        ElvenLineage.HIGH_ELF,
        60,
        "Prestidigitation",
        "Detect Magic",
        "Misty Step",
        id="high_elf",
    ),
    pytest.param(
        ElvenLineage.WOOD_ELF,
        60,
        "Druidcraft",
        "Longstrider",
        "Pass without Trace",
        id="wood_elf",
    ),
    pytest.param(
        ElvenLineage.LORWYN_ELF,
        60,
        "Thorn Whip",
        "Command",
        "Silence",
        id="lorwyn_elf",
    ),
    pytest.param(
        ElvenLineage.SHADOWMOOR_ELF,
        120,
        "Starry Wisp",
        "Heroism",
        "Gentle Repose",
        id="shadowmoor_elf",
    ),
]


def _build_elf(lineage: ElvenLineage, level: int) -> ElfSpeciesBuilder:
    builder = ElfSpeciesBuilder(
        elven_lineage=lineage, skill_proficiency=Skill.PERCEPTION
    )
    builder.set_character_level(level)
    builder.set_spell_casting_ability(Ability.INTELLIGENCE)
    return builder


class TestElfLineages:
    @pytest.mark.parametrize(
        "lineage, expected_darkvision, cantrip, level3_spell, level5_spell",
        ELF_LINEAGES,
    )
    def test_level_1_has_only_cantrip_and_correct_darkvision(
        self, lineage, expected_darkvision, cantrip, level3_spell, level5_spell
    ):
        data = _build_elf(lineage, 1).build()

        assert data.speed == (35 if lineage == ElvenLineage.WOOD_ELF else 30)
        assert cantrip in spell_names(data)
        assert level3_spell not in spell_names(data)
        assert level5_spell not in spell_names(data)

        dv_features = [
            f for f in data.features if isinstance(f, ElfFeatures.Darkvision)
        ]
        assert len(dv_features) == 1
        assert dv_features[0].distance == expected_darkvision

    @pytest.mark.parametrize(
        "lineage, expected_darkvision, cantrip, level3_spell, level5_spell",
        ELF_LINEAGES,
    )
    def test_level_3_adds_level_3_spell_only(
        self, lineage, expected_darkvision, cantrip, level3_spell, level5_spell
    ):
        data = _build_elf(lineage, 3).build()
        assert level3_spell in spell_names(data)
        assert level5_spell not in spell_names(data)

    @pytest.mark.parametrize(
        "lineage, expected_darkvision, cantrip, level3_spell, level5_spell",
        ELF_LINEAGES,
    )
    def test_level_5_adds_both_spells(
        self, lineage, expected_darkvision, cantrip, level3_spell, level5_spell
    ):
        data = _build_elf(lineage, 5).build()
        assert level3_spell in spell_names(data)
        assert level5_spell in spell_names(data)


# ── Tiefling fiendish legacies: resistance, cantrip, and level-gated spells ─


TIEFLING_LEGACIES = [
    pytest.param(
        FiendishLineage.ABYSSAL,
        DamageType.POISON,
        "Poison Spray",
        "Ray of Sickness",
        "Hold Person",
        id="abyssal",
    ),
    pytest.param(
        FiendishLineage.CHTHONIC,
        DamageType.NECROTIC,
        "Chill Touch",
        "False Life",
        "Ray of Enfeeblement",
        id="chthonic",
    ),
    pytest.param(
        FiendishLineage.Infernal,
        DamageType.FIRE,
        "Fire Bolt",
        "Hellish Rebuke",
        "Darkness",
        id="infernal",
    ),
]


def _build_tiefling(lineage: FiendishLineage, level: int) -> TieflingSpeciesBuilder:
    builder = TieflingSpeciesBuilder(character_level=level, fiendish_lineage=lineage)
    builder.set_character_level(level)
    builder.set_spell_casting_ability(Ability.CHARISMA)
    return builder


class TestTieflingLegacies:
    @pytest.mark.parametrize(
        "lineage, resistance, cantrip, level3_spell, level5_spell", TIEFLING_LEGACIES
    )
    def test_level_1_grants_resistance_and_cantrips(
        self, make_character, lineage, resistance, cantrip, level3_spell, level5_spell
    ):
        data = _build_tiefling(lineage, 1).build()

        assert cantrip in spell_names(data)
        assert "Thaumaturgy" in spell_names(data)
        assert level3_spell not in spell_names(data)
        assert level5_spell not in spell_names(data)

        character = make_character()
        for feature in data.features:
            feature.apply(character)
        assert character.is_resistant_to_damage(resistance)

    @pytest.mark.parametrize(
        "lineage, resistance, cantrip, level3_spell, level5_spell", TIEFLING_LEGACIES
    )
    def test_level_5_grants_both_spells(
        self, lineage, resistance, cantrip, level3_spell, level5_spell
    ):
        data = _build_tiefling(lineage, 5).build()
        assert level3_spell in spell_names(data)
        assert level5_spell in spell_names(data)


# ── Dragonborn: ancestry -> damage type, and breath weapon scaling ─────────


DRACONIC_ANCESTRY_TABLE = [
    (DragonbornFeatures.DragonColor.BLACK, DamageType.ACID),
    (DragonbornFeatures.DragonColor.BLUE, DamageType.LIGHTNING),
    (DragonbornFeatures.DragonColor.BRASS, DamageType.FIRE),
    (DragonbornFeatures.DragonColor.BRONZE, DamageType.LIGHTNING),
    (DragonbornFeatures.DragonColor.COPPER, DamageType.ACID),
    (DragonbornFeatures.DragonColor.GOLD, DamageType.FIRE),
    (DragonbornFeatures.DragonColor.GREEN, DamageType.POISON),
    (DragonbornFeatures.DragonColor.RED, DamageType.FIRE),
    (DragonbornFeatures.DragonColor.SILVER, DamageType.COLD),
    (DragonbornFeatures.DragonColor.WHITE, DamageType.COLD),
]


class TestDragonbornAncestry:
    @pytest.mark.parametrize(
        "color, expected_damage_type",
        DRACONIC_ANCESTRY_TABLE,
        ids=[c.value for c, _ in DRACONIC_ANCESTRY_TABLE],
    )
    def test_damage_resistance_matches_ancestor(
        self, make_character, color, expected_damage_type
    ):
        character = make_character()
        DragonbornFeatures.DamageResistance(color).apply(character)
        assert character.is_resistant_to_damage(expected_damage_type)
        for other_type in DamageType:
            if other_type != expected_damage_type:
                assert not character.is_resistant_to_damage(other_type)

    @pytest.mark.parametrize(
        "level, expected_dice",
        [
            (1, "1d10"),
            (4, "1d10"),
            (5, "2d10"),
            (10, "2d10"),
            (11, "3d10"),
            (16, "3d10"),
            (17, "4d10"),
            (20, "4d10"),
        ],
    )
    def test_breath_weapon_damage_scales_with_level(
        self, make_character, level, expected_dice
    ):
        character = make_character(levels={CharacterClass.FIGHTER: level})
        feature = DragonbornFeatures.BreathWeapon(DragonbornFeatures.DragonColor.RED)
        table = dict(feature.get_table_description(character))
        assert expected_dice in table["Damage"]


# ── Damage resistance mechanics (correct wiring) ────────────────────────────


class TestDamageResistanceMechanics:
    def test_aasimar_celestial_resistance(self, make_character):
        character = make_character()
        AasimarFeatures.CelestialResistance().apply(character)
        assert character.is_resistant_to_damage(DamageType.NECROTIC)
        assert character.is_resistant_to_damage(DamageType.RADIANT)

    def test_kalashtar_mental_discipline(self, make_character):
        character = make_character()
        KalashtarFeatures.MentalDiscipline().apply(character)
        assert character.is_resistant_to_damage(DamageType.PSYCHIC)

    def test_warforged_construct_resilience_and_armor_bonus(self, make_character):
        character = make_character(dexterity=14)  # +2 modifier
        WarForgedFeatures.ConstructResilience().apply(character)
        WarForgedFeatures.IntegratedProtection().apply(character)
        assert character.is_resistant_to_damage(DamageType.POISON)
        # PHB base 10 + Dex 2 + Integrated Protection's flat +1.
        assert character.calculate_armor_class() == 13

    @pytest.mark.parametrize(
        "damage_type_text, expected",
        [
            ("Poison", DamageType.POISON),
            ("Necrotic", DamageType.NECROTIC),
            ("Fire", DamageType.FIRE),
        ],
    )
    def test_tiefling_fiendish_resistance(
        self, make_character, damage_type_text, expected
    ):
        character = make_character()
        TieflingFeatures.FiendishResistance(damage_type_text).apply(character)
        assert character.is_resistant_to_damage(expected)

    def test_dwarven_resilience_grants_poison_resistance(self, make_character):
        character = make_character()
        DwarfFeatures.DwarvenResilience().apply(character)
        assert character.is_resistant_to_damage(DamageType.POISON)

    def test_trace_of_undeath_grants_necrotic_resistance(self, make_character):
        character = make_character()
        DhampirFeatures.TraceOfUndeath().apply(character)
        assert character.is_resistant_to_damage(DamageType.NECROTIC)


# ── Gnomish Cunning: correct on its own, but never granted by either lineage ─


class TestGnomishCunning:
    def test_gnomish_cunning_feature_grants_advantage_on_mental_saves(
        self, make_character
    ):
        character = make_character()
        GnomeFeatures.GnomishCunning().apply(character)
        assert character.saving_throws.is_advantaged(Ability.INTELLIGENCE)
        assert character.saving_throws.is_advantaged(Ability.WISDOM)
        assert character.saving_throws.is_advantaged(Ability.CHARISMA)
        assert not character.saving_throws.is_advantaged(Ability.STRENGTH)
        assert not character.saving_throws.is_advantaged(Ability.DEXTERITY)
        assert not character.saving_throws.is_advantaged(Ability.CONSTITUTION)

    def test_forest_gnome_species_grants_gnomish_cunning(self):
        data = ForestGnomeSpeciesBuilder(Ability.INTELLIGENCE).build()
        assert data.get_features_by_type(GnomeFeatures.GnomishCunning)

    def test_rock_gnome_species_grants_gnomish_cunning(self):
        data = RockGnomeSpeciesBuilder().build()
        assert data.get_features_by_type(GnomeFeatures.GnomishCunning)


# ── Granted spells missing from otherwise-implemented traits ────────────────


class TestGrantedSpellsAndCantrips:
    def test_forest_gnome_spells(self):
        data = ForestGnomeSpeciesBuilder(Ability.WISDOM).build()
        assert "Minor Illusion" in spell_names(data)
        assert "Speak with Animals" in spell_names(data)

    def test_rock_gnome_spells(self):
        data = RockGnomeSpeciesBuilder().build()
        assert "Mending" in spell_names(data)
        assert "Prestidigitation" in spell_names(data)

    def test_aasimar_light_cantrip(self):
        builder = AasimarSpeciesBuilder(character_level=1)
        builder.set_character_level(1)
        builder.set_spell_casting_ability(Ability.CHARISMA)
        data = builder.build()
        assert "Light" in spell_names(data)

    def test_khoravar_knows_friends_cantrip(self):
        data = KhoravarSpeciesBuilder(
            size=CreatureSize.MEDIUM,
            skill_versatility=Skill.PERSUASION,
            spell_casting_ability=Ability.CHARISMA,
        ).build()
        assert "Friends" in spell_names(data)

    def test_hexblood_knows_disguise_self_and_hex(self):
        data = HexbloodSpeciesBuilder(
            size=CreatureSize.MEDIUM, spell_casting_ability=Ability.WISDOM
        ).build()
        names = spell_names(data)
        assert "Disguise Self" in names
        assert "Hex" in names


# ── Reborn: skill choice and resistance choice both unimplemented ──────────


class TestReborn:
    def test_reborn_grants_a_skill_proficiency(self, make_character):
        data = RebornSpeciesBuilder(
            size=CreatureSize.MEDIUM,
            knowledge_skill=Skill.HISTORY,
            strange_endurance=DamageType.COLD,
        ).build()
        character = make_character()
        for feature in data.features:
            feature.apply(character)
        assert character.skills.is_proficient(Skill.HISTORY)

    def test_reborn_grants_one_of_the_strange_endurance_resistances(
        self, make_character
    ):
        data = RebornSpeciesBuilder(
            size=CreatureSize.MEDIUM,
            knowledge_skill=Skill.HISTORY,
            strange_endurance=DamageType.COLD,
        ).build()
        character = make_character()
        for feature in data.features:
            feature.apply(character)
        assert any(
            character.is_resistant_to_damage(dt)
            for dt in (DamageType.COLD, DamageType.NECROTIC, DamageType.POISON)
        )

    def test_reborn_knowledge_skill_feature_works_in_isolation(self, make_character):
        # The helper class itself is correct; only the builder's wiring is missing.
        character = make_character()
        RebornFeatures.RebornKnowledgeSkill(Skill.ARCANA).apply(character)
        assert character.skills.is_proficient(Skill.ARCANA)


# ── Dwarven Toughness: +1 max HP per character level ────────────────────────


class TestDwarvenToughness:
    @pytest.mark.parametrize(
        "level, expected_bonus", [(1, 1), (5, 5), (11, 11), (20, 20)]
    )
    def test_hit_point_bonus_equals_character_level(
        self, make_character, level, expected_bonus
    ):
        character = make_character(levels={CharacterClass.FIGHTER: level})
        DwarfFeatures.DwarvenToughness().apply(character)
        assert character.combat.hit_points_bonus == expected_bonus


# ── Granted proficiencies (choice-validated) ────────────────────────────────


class TestGrantedProficiencies:
    def test_human_skillful_grants_chosen_skill(self, make_character):
        character = make_character()
        HumanFeatures.Skillful(Skill.STEALTH).apply(character)
        assert character.skills.is_proficient(Skill.STEALTH)

    def test_elf_keen_senses_restricted_to_pool(self, make_character):
        character = make_character()
        ElfFeatures.KeenSenses(Skill.INSIGHT).apply(character)
        assert character.skills.is_proficient(Skill.INSIGHT)
        with pytest.raises(ValueError):
            ElfFeatures.KeenSenses(Skill.ATHLETICS)

    def test_changeling_instincts_requires_exactly_two_skills(self):
        with pytest.raises(ValueError):
            ChangelingFeatures.ChangelingInstincts([Skill.DECEPTION])

    def test_warforged_specialized_design_grants_chosen_skill(self, make_character):
        character = make_character()
        WarForgedFeatures.SpecializedDesign(Skill.PERCEPTION).apply(character)
        assert character.skills.is_proficient(Skill.PERCEPTION)


# ── PowerfulBuild is displayed under the wrong trait name ───────────────────


class TestGoliathTraitNaming:
    def test_powerful_build_has_correct_name(self):
        feature = GoliathFeatures.PowerfulBuild()
        assert feature.name == "Powerful Build"


# ── 2024 species never touch ability scores (2014 vs 2024 edition check) ───


class TestSpeciesNeverChangeAbilityScores:
    """2014 PHB Dwarf: +2 CON (+1 subrace ability). 2024 PHB Dwarf: no
    ability score change at all (ASI moved to Background). Every builder here
    targets 2024 rules, so applying a species' features must leave every
    ability score untouched."""

    def _dwarf_features(self):
        return DwarfSpeciesBuilder().build().features

    def _human_features(self):
        return (
            HumanSpeciesBuilder(
                origin_feat=OriginFeats.Tough(), skill_proficiency=Skill.PERCEPTION
            )
            .build()
            .features
        )

    def _elf_features(self):
        return _build_elf(ElvenLineage.HIGH_ELF, 5).build().features

    @pytest.mark.parametrize(
        "features_factory_name", ["_dwarf_features", "_human_features", "_elf_features"]
    )
    def test_no_ability_score_change(self, make_character, features_factory_name):
        character = make_character(
            strength=13,
            dexterity=13,
            constitution=13,
            intelligence=13,
            wisdom=13,
            charisma=13,
        )
        features = getattr(self, features_factory_name)()
        for feature in features:
            feature.apply(character)
        for ability in Ability:
            assert character.get_ability_score(ability) == 13


class TestSpeciesChoiceValidation:
    def test_strange_endurance_rejects_non_listed_damage_type(self):
        # Strange Endurance: "one of ... Cold, Necrotic, or Poison."
        with pytest.raises(ValueError):
            RebornFeatures.StrangeEndurance(DamageType.FIRE)

    @pytest.mark.parametrize(
        "dt", [DamageType.COLD, DamageType.NECROTIC, DamageType.POISON]
    )
    def test_strange_endurance_grants_only_the_chosen_resistance(
        self, make_character, dt
    ):
        character = make_character()
        RebornFeatures.StrangeEndurance(dt).apply(character)
        options = {DamageType.COLD, DamageType.NECROTIC, DamageType.POISON}
        assert character.is_resistant_to_damage(dt)
        for other in options - {dt}:
            assert not character.is_resistant_to_damage(other)

    def test_hexblood_rejects_physical_spellcasting_ability(self):
        # Hex Magic: "Intelligence, Wisdom, or Charisma is your spellcasting ability"
        with pytest.raises(AssertionError):
            HexbloodSpeciesBuilder(
                size=CreatureSize.MEDIUM, spell_casting_ability=Ability.STRENGTH
            )

    def test_khoravar_rejects_physical_spellcasting_ability(self):
        # Fey Gift: "Intelligence, Wisdom, or Charisma is your spellcasting ability"
        with pytest.raises(AssertionError):
            KhoravarSpeciesBuilder(
                size=CreatureSize.MEDIUM,
                skill_versatility=Skill.PERSUASION,
                spell_casting_ability=Ability.DEXTERITY,
            )
