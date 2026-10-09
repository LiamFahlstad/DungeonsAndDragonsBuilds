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

from Model.Character import Character

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
from CharacterContent.Species.SpeciesBuilder import SpeciesBuilder
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
from tests._grants import grant
from Model.CharacterSources import CharacterSources
from Model.ClassLevels import ClassLevels


def bug(reason):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


def spell_names(data) -> list[str]:
    return [s.name for s in data.spells]


def species_character(
    builder: SpeciesBuilder,
    level: int = 1,
    spell_casting_ability: Ability = Ability.INTELLIGENCE,
) -> Character:
    """A level `level` character with only `builder`'s species granted.
    `spell_casting_ability` is for the species spells whose ability the
    builder doesn't choose itself (Elf, Tiefling)."""
    sources = CharacterSources(
        class_levels=ClassLevels(level_per_class={CharacterClass.WIZARD: level})
    )
    return Character(builder.build(sources, spell_casting_ability))


# ── Speed & size (fixed-size species) ───────────────────────────────────────


FIXED_SIZE_SPECIES = [
    pytest.param(
        lambda: species_character(DwarfSpeciesBuilder()),
        30,
        CreatureSize.MEDIUM,
        id="dwarf",
    ),
    pytest.param(
        lambda: species_character(HalflingSpeciesBuilder()),
        30,
        CreatureSize.SMALL,
        id="halfling",
    ),
    pytest.param(
        lambda: species_character(OrcSpeciesBuilder()),
        30,
        CreatureSize.MEDIUM,
        id="orc",
    ),
    pytest.param(
        lambda: species_character(
            GoliathSpeciesBuilder(GoliathFeatures.GiantAncestryType.HILL_GIANT)
        ),
        35,
        CreatureSize.MEDIUM,
        id="goliath",
    ),
    pytest.param(
        lambda: species_character(KalashtarSpeciesBuilder()),
        30,
        CreatureSize.MEDIUM,
        id="kalashtar",
    ),
    pytest.param(
        lambda: species_character(
            DragonbornSpeciesBuilder(DragonbornFeatures.DragonColor.RED)
        ),
        30,
        CreatureSize.MEDIUM,
        id="dragonborn",
    ),
    pytest.param(
        lambda: species_character(ForestGnomeSpeciesBuilder(Ability.INTELLIGENCE)),
        30,
        CreatureSize.SMALL,
        id="forest_gnome",
    ),
    pytest.param(
        lambda: species_character(RockGnomeSpeciesBuilder()),
        30,
        CreatureSize.SMALL,
        id="rock_gnome",
    ),
]


class TestFixedSpeedAndSize:
    @pytest.mark.parametrize("build, expected_speed, expected_size", FIXED_SIZE_SPECIES)
    def test_speed_and_size(self, build, expected_speed, expected_size):
        data = build()
        assert data.base_speed == expected_speed
        assert data.size == expected_size


class TestChoosableSizeSpecies:
    """PHB 2024 / Heroes of Eberron / Ravenloft: several species let the player
    choose Medium or Small. The builder must faithfully reflect whichever size
    is passed in, not silently default to one."""

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_changeling_size_choice(self, size):
        data = species_character(
            ChangelingSpeciesBuilder(
                size=size, instinct_skills=[Skill.DECEPTION, Skill.INSIGHT]
            )
        )
        assert data.size == size
        assert data.base_speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_khoravar_size_choice(self, size):
        data = species_character(
            KhoravarSpeciesBuilder(
                size=size,
                skill_versatility=Skill.PERSUASION,
                spell_casting_ability=Ability.CHARISMA,
            )
        )
        assert data.size == size
        assert data.base_speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_shifter_size_choice(self, size):
        data = species_character(
            ShifterSpeciesBuilder(
                skill=Skill.ATHLETICS,
                size=size,
                shifter_form=ShifterFeatures.ShiftForm.SWIFTSTRIDE,
            )
        )
        assert data.size == size
        assert data.base_speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_lupin_size_choice(self, size):
        data = species_character(
            LupinSpeciesBuilder(size=size, werewolf_instincts_skill=Skill.PERCEPTION)
        )
        assert data.size == size
        assert data.base_speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_dhampir_size_choice_does_not_affect_speed(self, size):
        # Dhampir speed is a fixed 35 ft regardless of size (Ravenloft: The
        # Horrors Within), unlike most other species where speed never varies
        # with the size choice either.
        data = species_character(DhampirSpeciesBuilder(size=size))
        assert data.size == size
        assert data.base_speed == 35

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_hexblood_size_choice(self, size):
        data = species_character(
            HexbloodSpeciesBuilder(size=size, spell_casting_ability=Ability.WISDOM)
        )
        assert data.size == size
        assert data.base_speed == 30

    @pytest.mark.parametrize("size", [CreatureSize.SMALL, CreatureSize.MEDIUM])
    def test_reborn_size_choice(self, size):
        data = species_character(
            RebornSpeciesBuilder(
                size=size,
                knowledge_skill=Skill.HISTORY,
                strange_endurance=DamageType.COLD,
            )
        )
        assert data.size == size
        assert data.base_speed == 30


# ── Darkvision ranges ────────────────────────────────────────────────────────


class TestDarkvision:
    def test_dwarf_darkvision_120(self, make_sources):
        sources = make_sources()
        sources.add_effect(DwarfFeatures.Darkvision())
        character = Character(sources)
        assert character.get_sense_range(Sense.DARKVISION) == 120

    def test_orc_darkvision_120(self, make_sources):
        from CharacterContent.Features.SpeciesFeatures import OrcFeatures

        sources = make_sources()
        sources.add_effect(OrcFeatures.Darkvision())
        character = Character(sources)
        assert character.get_sense_range(Sense.DARKVISION) == 120

    def test_gnome_darkvision_60(self, make_sources):
        sources = make_sources()
        sources.add_effect(GnomeFeatures.Darkvision())
        character = Character(sources)
        assert character.get_sense_range(Sense.DARKVISION) == 60

    def test_aasimar_darkvision_60(self, make_sources):
        sources = make_sources()
        sources.add_effect(AasimarFeatures.Darkvision())
        character = Character(sources)
        assert character.get_sense_range(Sense.DARKVISION) == 60

    def test_tiefling_darkvision_60(self, make_sources):
        sources = make_sources()
        sources.add_effect(TieflingFeatures.Darkvision(60))
        character = Character(sources)
        assert character.get_sense_range(Sense.DARKVISION) == 60

    def test_dhampir_darkvision_60(self, make_sources):
        sources = make_sources()
        sources.add_effect(DhampirFeatures.Darkvision())
        character = Character(sources)
        assert character.get_sense_range(Sense.DARKVISION) == 60

    def test_hexblood_darkvision_60(self, make_sources):
        sources = make_sources()
        sources.add_effect(HexbloodFeatures.Darkvision())
        character = Character(sources)
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


class TestElfLineages:
    @pytest.mark.parametrize(
        "lineage, expected_darkvision, cantrip, level3_spell, level5_spell",
        ELF_LINEAGES,
    )
    def test_level_1_has_only_cantrip_and_correct_darkvision(
        self, lineage, expected_darkvision, cantrip, level3_spell, level5_spell
    ):
        data = species_character(ElfSpeciesBuilder(lineage, Skill.PERCEPTION), level=1)

        assert data.base_speed == (35 if lineage == ElvenLineage.WOOD_ELF else 30)
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
        data = species_character(ElfSpeciesBuilder(lineage, Skill.PERCEPTION), level=3)
        assert level3_spell in spell_names(data)
        assert level5_spell not in spell_names(data)

    @pytest.mark.parametrize(
        "lineage, expected_darkvision, cantrip, level3_spell, level5_spell",
        ELF_LINEAGES,
    )
    def test_level_5_adds_both_spells(
        self, lineage, expected_darkvision, cantrip, level3_spell, level5_spell
    ):
        data = species_character(ElfSpeciesBuilder(lineage, Skill.PERCEPTION), level=5)
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


class TestTieflingLegacies:
    @pytest.mark.parametrize(
        "lineage, resistance, cantrip, level3_spell, level5_spell", TIEFLING_LEGACIES
    )
    def test_level_1_grants_resistance_and_cantrips(
        self, make_sources, lineage, resistance, cantrip, level3_spell, level5_spell
    ):
        data = species_character(
            TieflingSpeciesBuilder(lineage),
            level=1,
            spell_casting_ability=Ability.CHARISMA,
        )

        assert cantrip in spell_names(data)
        assert "Thaumaturgy" in spell_names(data)
        assert level3_spell not in spell_names(data)
        assert level5_spell not in spell_names(data)

        sources = make_sources()
        for feature in data.features:
            sources.add_effect(feature)
        character = Character(sources)
        assert character.is_resistant_to_damage(resistance)

    @pytest.mark.parametrize(
        "lineage, resistance, cantrip, level3_spell, level5_spell", TIEFLING_LEGACIES
    )
    def test_level_5_grants_both_spells(
        self, lineage, resistance, cantrip, level3_spell, level5_spell
    ):
        data = species_character(
            TieflingSpeciesBuilder(lineage),
            level=5,
            spell_casting_ability=Ability.CHARISMA,
        )
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
        self, make_sources, color, expected_damage_type
    ):
        sources = make_sources()
        sources.add_effect(DragonbornFeatures.DamageResistance(color))
        character = Character(sources)
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
    def test_aasimar_celestial_resistance(self, make_sources):
        sources = make_sources()
        sources.add_effect(AasimarFeatures.CelestialResistance())
        character = Character(sources)
        assert character.is_resistant_to_damage(DamageType.NECROTIC)
        assert character.is_resistant_to_damage(DamageType.RADIANT)

    def test_kalashtar_mental_discipline(self, make_sources):
        sources = make_sources()
        sources.add_effect(KalashtarFeatures.MentalDiscipline())
        character = Character(sources)
        assert character.is_resistant_to_damage(DamageType.PSYCHIC)

    def test_warforged_construct_resilience_and_armor_bonus(self, make_sources):
        sources = make_sources(dexterity=14)  # +2 modifier
        sources.add_effect(WarForgedFeatures.ConstructResilience())
        sources.add_effect(WarForgedFeatures.IntegratedProtection())
        character = Character(sources)
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
        self, make_sources, damage_type_text, expected
    ):
        sources = make_sources()
        sources.add_effect(TieflingFeatures.FiendishResistance(damage_type_text))
        character = Character(sources)
        assert character.is_resistant_to_damage(expected)

    def test_dwarven_resilience_grants_poison_resistance(self, make_sources):
        sources = make_sources()
        sources.add_effect(DwarfFeatures.DwarvenResilience())
        character = Character(sources)
        assert character.is_resistant_to_damage(DamageType.POISON)

    def test_trace_of_undeath_grants_necrotic_resistance(self, make_sources):
        sources = make_sources()
        sources.add_effect(DhampirFeatures.TraceOfUndeath())
        character = Character(sources)
        assert character.is_resistant_to_damage(DamageType.NECROTIC)


# ── Gnomish Cunning: correct on its own, but never granted by either lineage ─


class TestGnomishCunning:
    def test_gnomish_cunning_feature_grants_advantage_on_mental_saves(
        self, make_sources
    ):
        sources = make_sources()
        sources.add_effect(GnomeFeatures.GnomishCunning())
        character = Character(sources)
        assert character.ledger.saving_throws.is_advantaged(Ability.INTELLIGENCE)
        assert character.ledger.saving_throws.is_advantaged(Ability.WISDOM)
        assert character.ledger.saving_throws.is_advantaged(Ability.CHARISMA)
        assert not character.ledger.saving_throws.is_advantaged(Ability.STRENGTH)
        assert not character.ledger.saving_throws.is_advantaged(Ability.DEXTERITY)
        assert not character.ledger.saving_throws.is_advantaged(Ability.CONSTITUTION)

    def test_forest_gnome_species_grants_gnomish_cunning(self):
        data = species_character(ForestGnomeSpeciesBuilder(Ability.INTELLIGENCE))
        assert data.get_features_by_type(GnomeFeatures.GnomishCunning)

    def test_rock_gnome_species_grants_gnomish_cunning(self):
        data = species_character(RockGnomeSpeciesBuilder())
        assert data.get_features_by_type(GnomeFeatures.GnomishCunning)


# ── Granted spells missing from otherwise-implemented traits ────────────────


class TestGrantedSpellsAndCantrips:
    def test_forest_gnome_spells(self):
        data = species_character(ForestGnomeSpeciesBuilder(Ability.WISDOM))
        assert "Minor Illusion" in spell_names(data)
        assert "Speak with Animals" in spell_names(data)

    def test_rock_gnome_spells(self):
        data = species_character(RockGnomeSpeciesBuilder())
        assert "Mending" in spell_names(data)
        assert "Prestidigitation" in spell_names(data)

    def test_species_writes_into_an_existing_sheet(self):
        # Species grant straight into the character's sources - and a species
        # spell the class already granted (Rock Gnome Prestidigitation on a
        # Wizard) is listed from both sources rather than failing the build.
        from CharacterContent.Spells.SpellLists import BardLevel0Spells

        sources = CharacterSources()
        grant(sources).add_cantrip(
            BardLevel0Spells.PRESTIDIGITATION, Ability.INTELLIGENCE
        )
        assert RockGnomeSpeciesBuilder().build(sources, Ability.INTELLIGENCE) is sources
        data = Character(sources)
        assert spell_names(data).count("Prestidigitation") == 2
        assert data.base_speed == GnomeFeatures.SPEED
        # The same spell twice from one grant is an error, found on read.
        grant(sources).add_cantrip(
            BardLevel0Spells.PRESTIDIGITATION, Ability.INTELLIGENCE
        )
        with pytest.raises(ValueError, match="already added"):
            Character(sources).spells

    def test_aasimar_light_cantrip(self):
        data = species_character(
            AasimarSpeciesBuilder(), spell_casting_ability=Ability.CHARISMA
        )
        assert "Light" in spell_names(data)

    def test_khoravar_knows_friends_cantrip(self):
        data = species_character(
            KhoravarSpeciesBuilder(
                size=CreatureSize.MEDIUM,
                skill_versatility=Skill.PERSUASION,
                spell_casting_ability=Ability.CHARISMA,
            )
        )
        assert "Friends" in spell_names(data)

    def test_hexblood_knows_disguise_self_and_hex(self):
        data = species_character(
            HexbloodSpeciesBuilder(
                size=CreatureSize.MEDIUM, spell_casting_ability=Ability.WISDOM
            )
        )
        names = spell_names(data)
        assert "Disguise Self" in names
        assert "Hex" in names


# ── Reborn: skill choice and resistance choice both unimplemented ──────────


class TestReborn:
    def test_reborn_grants_a_skill_proficiency(self, make_sources):
        data = species_character(
            RebornSpeciesBuilder(
                size=CreatureSize.MEDIUM,
                knowledge_skill=Skill.HISTORY,
                strange_endurance=DamageType.COLD,
            )
        )
        sources = make_sources()
        for feature in data.features:
            sources.add_effect(feature)
        character = Character(sources)
        assert character.ledger.skills.is_proficient(Skill.HISTORY)

    def test_reborn_grants_one_of_the_strange_endurance_resistances(self, make_sources):
        data = species_character(
            RebornSpeciesBuilder(
                size=CreatureSize.MEDIUM,
                knowledge_skill=Skill.HISTORY,
                strange_endurance=DamageType.COLD,
            )
        )
        sources = make_sources()
        for feature in data.features:
            sources.add_effect(feature)
        character = Character(sources)
        assert any(
            character.is_resistant_to_damage(dt)
            for dt in (DamageType.COLD, DamageType.NECROTIC, DamageType.POISON)
        )

    def test_reborn_knowledge_skill_feature_works_in_isolation(self, make_sources):
        # The helper class itself is correct; only the builder's wiring is missing.
        sources = make_sources()
        sources.add_effect(RebornFeatures.RebornKnowledgeSkill(Skill.ARCANA))
        character = Character(sources)
        assert character.ledger.skills.is_proficient(Skill.ARCANA)


# ── Dwarven Toughness: +1 max HP per character level ────────────────────────


class TestDwarvenToughness:
    @pytest.mark.parametrize(
        "level, expected_bonus", [(1, 1), (5, 5), (11, 11), (20, 20)]
    )
    def test_hit_point_bonus_equals_character_level(
        self, make_sources, level, expected_bonus
    ):
        sources = make_sources(levels={CharacterClass.FIGHTER: level})
        sources.add_effect(DwarfFeatures.DwarvenToughness())
        character = Character(sources)
        assert character.ledger.hit_points.bonuses.total(character) == expected_bonus


# ── Granted proficiencies (choice-validated) ────────────────────────────────


class TestGrantedProficiencies:
    def test_human_skillful_grants_chosen_skill(self, make_sources):
        sources = make_sources()
        sources.add_effect(HumanFeatures.Skillful(Skill.STEALTH))
        character = Character(sources)
        assert character.ledger.skills.is_proficient(Skill.STEALTH)

    def test_elf_keen_senses_restricted_to_pool(self, make_sources):
        sources = make_sources()
        sources.add_effect(ElfFeatures.KeenSenses(Skill.INSIGHT))
        character = Character(sources)
        assert character.ledger.skills.is_proficient(Skill.INSIGHT)
        with pytest.raises(ValueError):
            ElfFeatures.KeenSenses(Skill.ATHLETICS)

    def test_changeling_instincts_requires_exactly_two_skills(self):
        with pytest.raises(ValueError):
            ChangelingFeatures.ChangelingInstincts([Skill.DECEPTION])

    def test_warforged_specialized_design_grants_chosen_skill(self, make_sources):
        sources = make_sources()
        sources.add_effect(WarForgedFeatures.SpecializedDesign(Skill.PERCEPTION))
        character = Character(sources)
        assert character.ledger.skills.is_proficient(Skill.PERCEPTION)


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
        return species_character(DwarfSpeciesBuilder()).features

    def _human_features(self):
        return species_character(
            HumanSpeciesBuilder(
                origin_feat=OriginFeats.Tough(), skill_proficiency=Skill.PERCEPTION
            )
        ).features

    def _elf_features(self):
        return species_character(
            ElfSpeciesBuilder(ElvenLineage.HIGH_ELF, Skill.PERCEPTION), level=5
        ).features

    @pytest.mark.parametrize(
        "features_factory_name", ["_dwarf_features", "_human_features", "_elf_features"]
    )
    def test_no_ability_score_change(self, make_sources, features_factory_name):
        sources = make_sources(
            strength=13,
            dexterity=13,
            constitution=13,
            intelligence=13,
            wisdom=13,
            charisma=13,
        )
        features = getattr(self, features_factory_name)()
        for feature in features:
            sources.add_effect(feature)
        character = Character(sources)
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
        self, make_sources, dt
    ):
        sources = make_sources()
        sources.add_effect(RebornFeatures.StrangeEndurance(dt))
        options = {DamageType.COLD, DamageType.NECROTIC, DamageType.POISON}
        character = Character(sources)
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
