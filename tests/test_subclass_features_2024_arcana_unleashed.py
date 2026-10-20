"""
Arcana Unleashed 2024 subclasses: Arcana Domain Cleric, Arcane Archer Fighter,
Vestige Warlock, and the Conjurer / Enchanter / Necromancer / Transmuter Wizards.

Expected values are transcribed from SourceTexts/SubclassTexts2024/
(arcana_domain.txt, arcane_archer.txt, vestige_patron.txt, conjurer.txt,
enchanter.txt, necromancer.txt, transmuter.txt) and the 2024 PHB tables (the
proficiency bonus by level, the Wizard slot table's "new level of spell slots"
levels, the Cleric domain tables quoted in life/light/trickery/war_domain.txt),
and are quoted in comments next to each assertion. Nothing is read off the
engine's own output.

Example builds (Builds/Examples/Y2024_*) are rebuilt at lower class levels by
lowering the starter builder's base_class_level, which makes ClassBuilder skip
every level above it.

Edition asserted: 2024 (Arcana Unleashed targets the 2024 PHB; subclasses start
at level 3).
"""

import importlib
from collections import Counter

import pytest

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.SubClasses2024 import (
    ClericArcana,
    FighterArcaneArcher,
    WarlockVestige,
    WizardConjurer,
    WizardEnchanter,
    WizardNecromancer,
    WizardTransmuter,
)
from CharacterContent.Features.SubClassFeatures.Cleric import ClericArcanaFeatures
from CharacterContent.Features.SubClassFeatures.Fighter import (
    FighterArcaneArcherFeatures as ArcherF,
)
from CharacterContent.Features.SubClassFeatures.Warlock import WarlockVestigeFeatures
from CharacterContent.Features.SubClassFeatures.Wizard import (
    WizardConjurerFeatures,
    WizardEnchanterFeatures,
    WizardNecromancerFeatures,
    WizardTransmuterFeatures,
)
from CharacterContent.Spells import SpellLists as SL
from Core.Definitions import (
    Ability,
    CharacterClass,
    CreatureSize,
    DamageType,
    Skill,
    WarlockVestigeDomain,
    WarlockVestigeType,
)
from Model.Character import Character
from Model.CharacterSources import CharacterSources
from Model.Content.Feature import ActionType, RegainedOn
from tests._grants import apply_level

# ---------------------------------------------------------------------------
# Helpers


def build_example(module_name: str, class_level: int | None = None) -> Character:
    """Build an example character, optionally capping the starter class level."""
    module = importlib.import_module(f"Builds.Examples.{module_name}")
    builder_class = [
        value
        for value in vars(module).values()
        if isinstance(value, type)
        and issubclass(value, CharacterBuilder)
        and value is not CharacterBuilder
    ][0]
    builder = builder_class()
    if class_level is not None:
        builder.starter_class_builder.base_class_level = class_level
    return builder.build().validate()


def feature_names(character: Character) -> list[str]:
    return [f.name for f in character.iter_features_with_extensions()]


def spell_levels(character: Character) -> dict[str, int]:
    return {spell.name: spell.grant_level for spell in character.spells}


# proficiency bonus by character level, PHB class-table column (typed here)
PHB_PROFICIENCY = {
    **{level: 2 for level in range(1, 5)},
    **{level: 3 for level in range(5, 9)},
    **{level: 4 for level in range(9, 13)},
    **{level: 5 for level in range(13, 17)},
    **{level: 6 for level in range(17, 21)},
}

# ---------------------------------------------------------------------------
# Feature grant levels, straight from each text's "Level N:" headings

CLERIC = "Y2024_Cleric_Arcana_MaelisRuneward"
ARCHER = "Y2024_Fighter_ArcaneArcher_SylvaineFarshot"
VESTIGE = "Y2024_Warlock_Vestige_OrsolyaHollowvow"
CONJURER = "Y2024_Wizard_Conjuration_CorvinFarsummon"
ENCHANTER = "Y2024_Wizard_Enchantment_SeraphineSilvertongue"
NECROMANCER = "Y2024_Wizard_Necromancy_MordecaiAshgrave"
TRANSMUTER = "Y2024_Wizard_Transmutation_AlistairFormbend"

# (module, {feature name: level the text grants it}, all-time options excluded)
FEATURE_LEVELS = {
    CLERIC: {
        # arcana_domain.txt
        "Modify Magic": 3,
        "Student of Arcana": 3,
        "Dispelling Recovery": 6,
        "Magical Mastery": 17,
    },
    ARCHER: {
        # arcane_archer.txt
        "Arcane Archer Lore": 3,
        "Arcane Shot": 3,
        "Curving Shot": 7,
        "Magical Ammunition": 7,
        "Ever-Ready Shot": 10,
        "Indomitable Teleport": 15,
        "Masterful Shots": 18,
    },
    VESTIGE: {
        # vestige_patron.txt
        "Vestige Companion": 3,
        "Vestige Spells": 3,
        "Vestige Power": 6,
        "Vestige Recovery": 10,
        "Semblance of Life": 14,
    },
    CONJURER: {
        # conjurer.txt
        "Benign Transposition": 3,
        "Conjuration Savant": 3,
        "Distant Transposition": 6,
        "Durable Summons": 6,
        "Focused Conjuration": 10,
        "Splintered Summons": 14,
    },
    ENCHANTER: {
        # enchanter.txt
        "Enchanting Conversationalist": 3,
        "Enchantment Savant": 3,
        "Hypnotic Presence": 3,
        "Split Enchantment": 6,
        "Instinctive Charm": 10,
        "Alter Memories": 14,
    },
    NECROMANCER: {
        # necromancer.txt
        "Necromancy Savant": 3,
        "Necromancy Spellbook": 3,
        "Grave Power": 6,
        "Undead Thralls": 6,
        "Harvest Undead": 10,
        "Death's Master": 14,
    },
    TRANSMUTER: {
        # transmuter.txt
        "Transmutation Savant": 3,
        "Transmuter's Stone": 3,
        "Wondrous Alteration": 3,
        "Empowered Transmutation": 6,
        "Potent Stone": 10,
        "Shape-Shifter": 10,
        "Master Transmuter": 14,
    },
}

# Class levels worth building at: just below and at every feature level.
BOUNDARY_LEVELS = {
    CLERIC: [2, 3, 5, 6, 16, 17, 18],
    ARCHER: [2, 3, 6, 7, 9, 10, 14, 15, 17, 18],
    VESTIGE: [2, 3, 5, 6, 9, 10, 13, 14, 15],
    CONJURER: [2, 3, 5, 6, 9, 10, 13, 14, 20],
    ENCHANTER: [2, 3, 5, 6, 9, 10, 13, 14, 20],
    NECROMANCER: [2, 3, 5, 6, 9, 10, 13, 14, 20],
    TRANSMUTER: [2, 3, 5, 6, 9, 10, 13, 14, 20],
}


@pytest.mark.parametrize(
    "module, level",
    [(m, lvl) for m, levels in BOUNDARY_LEVELS.items() for lvl in levels],
)
def test_subclass_features_granted_exactly_once_at_their_text_level(module, level):
    # Each feature appears once from the level its heading names, and never
    # before it (subclasses start at 3 in the 2024 engine).
    character = build_example(module, level)
    table = FEATURE_LEVELS[module]
    expected = sorted(name for name, at in table.items() if at <= level)
    actual = sorted(name for name in feature_names(character) if name in table)
    assert actual == expected


@pytest.mark.parametrize("module", list(FEATURE_LEVELS))
def test_grant_stamps_carry_the_text_level(module):
    # The level recorded on each grant is the level the text gives.
    character = build_example(module)
    stamps = {}
    for feature in character.iter_features_with_extensions():
        if feature.name in FEATURE_LEVELS[module]:
            stamps[feature.name] = character.stamp_of(feature).level
    assert stamps == FEATURE_LEVELS[module]


@pytest.mark.parametrize(
    "class_level, options",
    [
        (2, 0),
        (3, 2),
        (6, 2),
        (7, 3),
        (9, 3),
        (10, 4),
        (14, 4),
        (15, 5),
        (17, 5),
        (18, 6),
    ],
)
def test_arcane_shot_options_known_by_fighter_level(class_level, options):
    # arcane_archer.txt: "You learn two Arcane Shot options" at 3, "an
    # additional ... option ... when you reach Fighter levels 7, 10, 15, and 18".
    character = build_example(ARCHER, class_level)
    known = [
        f
        for f in character.iter_features_with_extensions()
        if f.origin == "Arcane Shot Option"
    ]
    assert len(known) == options
    assert len({f.name for f in known}) == options


def test_arcane_shot_options_attach_to_arcane_shot():
    character = build_example(ARCHER)
    shot = character.get_features_by_type(ArcherF.ArcaneShot)[0]
    attached = {f.name for f in character.extensions_of(shot)}
    options = {
        f.name
        for f in character.iter_features_with_extensions()
        if f.origin == "Arcane Shot Option"
    }
    assert options and options <= attached
    # Ever-Ready Shot (level 10) refines Arcane Shot too.
    assert "Ever-Ready Shot" in attached


def test_examples_validate_and_idempotent_rebuild():
    # Rebuilding a Character from its own (copied) sources changes nothing.
    for module in FEATURE_LEVELS:
        character = build_example(module)
        again = Character(character.sources)
        assert feature_names(again) == feature_names(character)
        assert spell_levels(again) == spell_levels(character)
        for skill in Skill:
            assert again.get_skill_bonus(skill) == character.get_skill_bonus(skill)


# ---------------------------------------------------------------------------
# Spell tables: always-prepared and savant picks


def _vestige_sources():
    return CharacterSources(spell_casting_ability=Ability.CHARISMA)


# Cleric Domain Spells tables (life/light/trickery/war_domain.txt), which
# vestige_patron.txt tells the Warlock to use at the same levels.
VESTIGE_DOMAIN_TABLES = {
    WarlockVestigeDomain.LIFE: {
        3: ["Aid", "Bless", "Cure Wounds", "Lesser Restoration"],
        5: ["Mass Healing Word", "Revivify"],
        7: ["Aura of Life", "Death Ward"],
        9: ["Greater Restoration", "Mass Cure Wounds"],
    },
    WarlockVestigeDomain.LIGHT: {
        3: ["Burning Hands", "Faerie Fire", "Scorching Ray", "See Invisibility"],
        5: ["Daylight", "Fireball"],
        7: ["Arcane Eye", "Wall of Fire"],
        9: ["Flame Strike", "Scrying"],
    },
    WarlockVestigeDomain.TRICKERY: {
        3: ["Charm Person", "Disguise Self", "Invisibility", "Pass without Trace"],
        5: ["Hypnotic Pattern", "Nondetection"],
        7: ["Confusion", "Dimension Door"],
        9: ["Dominate Person", "Modify Memory"],
    },
    WarlockVestigeDomain.WAR: {
        3: ["Guiding Bolt", "Magic Weapon", "Shield of Faith", "Spiritual Weapon"],
        5: ["Crusader's Mantle", "Spirit Guardians"],
        7: ["Fire Shield", "Freedom of Movement"],
        9: ["Hold Monster", "Steel Wind Strike"],
    },
}


@pytest.mark.parametrize("domain", list(VESTIGE_DOMAIN_TABLES))
def test_vestige_spells_follow_the_chosen_domain_table(domain):
    # vestige_patron.txt: "When you reach a Warlock level equal to a Cleric level
    # listed on the Domain Spells table ... you thereafter always have the listed
    # spells prepared."
    table = VESTIGE_DOMAIN_TABLES[domain]
    sources = _vestige_sources()
    builders = {
        3: WarlockVestige.WarlockVestigeLevel3(WarlockVestigeType.UNDEAD, domain),
        5: WarlockVestige.WarlockVestigeLevel5(domain),
        7: WarlockVestige.WarlockVestigeLevel7(domain),
        9: WarlockVestige.WarlockVestigeLevel9(domain),
    }
    running = {}
    for level in (3, 5, 7, 9):
        apply_level(builders[level], sources)
        for spell in table[level]:
            running[spell] = level
        assert spell_levels(Character(sources)) == running


def test_vestige_has_no_spell_grant_at_other_levels():
    # Rows exist only at 3, 5, 7 and 9: no other Vestige builder grants spells.
    for builder in (
        WarlockVestige.WarlockVestigeLevel6(),
        WarlockVestige.WarlockVestigeLevel10(),
        WarlockVestige.WarlockVestigeLevel14(),
    ):
        sources = _vestige_sources()
        apply_level(builder, sources)
        assert Character(sources).spells == []


def test_vestige_domain_choices_are_the_four_the_text_allows():
    # "Select one of the following Cleric domains: Life, Light, Trickery, or War."
    assert {d.name for d in WarlockVestigeDomain} == {
        "LIFE",
        "LIGHT",
        "TRICKERY",
        "WAR",
    }


def test_arcana_domain_spells_are_not_granted_early():
    # arcana_domain.txt table: each tier arrives only at its own Cleric level.
    from tests.test_subclass_features_2024 import _cleric_data_with_channel_divinity

    sources = _cleric_data_with_channel_divinity()
    apply_level(
        ClericArcana.ClericArcanaLevel3(
            Skill.ARCANA,
            SL.WizardLevel0Spells.FIRE_BOLT,
            SL.WizardLevel0Spells.MAGE_HAND,
        ),
        sources,
    )
    assert {s.name for s in Character(sources).spells} == {
        "Detect Magic",
        "Magic Missile",
        "Magic Weapon",
        "Nystul's Magic Aura",
        "Fire Bolt",
        "Mage Hand",
    }
    apply_level(ClericArcana.ClericArcanaLevel5(), sources)
    levels = spell_levels(Character(sources))
    assert levels["Counterspell"] == levels["Dispel Magic"] == 5
    assert "Arcane Eye" not in levels and "Bigby's Hand" not in levels


def test_arcana_domain_cantrips_are_wizard_cantrips_chosen_not_prepared(make_sources):
    # "You learn two Wizard cantrips of your choice." Nothing else at level 3
    # besides the four prepared domain spells; the skill is the one chosen.
    from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
    from tests._grants import grant

    sources = make_sources(levels={CharacterClass.CLERIC: 3}, wisdom=14)
    sources.spell_casting_ability = Ability.WISDOM
    grant(sources).add_feature(ClericFeatures.ChannelDivinity())
    apply_level(
        ClericArcana.ClericArcanaLevel3(
            Skill.HISTORY,
            SL.WizardLevel0Spells.FIRE_BOLT,
            SL.WizardLevel0Spells.MAGE_HAND,
        ),
        sources,
    )
    character = Character(sources).validate()
    assert character.is_proficient_in_skill(Skill.HISTORY)
    assert not character.is_proficient_in_skill(Skill.ARCANA)
    assert len(character.spells) == 4 + 2
    assert [f.name for f in character.iter_features_with_extensions()] == [
        "Channel Divinity",
        "Modify Magic",
        "Student of Arcana",
    ]


def test_magical_mastery_adds_one_wizard_spell_each_of_levels_6_to_9():
    # arcana_domain.txt Level 17: "four Wizard spells, one from each of levels
    # 6, 7, 8, and 9. You thereafter always have those spells prepared."
    sources = CharacterSources(spell_casting_ability=Ability.WISDOM)
    apply_level(
        ClericArcana.ClericArcanaLevel17(
            SL.WizardLevel6Spells.DISINTEGRATE,
            SL.WizardLevel7Spells.TELEPORT,
            SL.WizardLevel8Spells.MIND_BLANK,
            SL.WizardLevel9Spells.TIME_STOP,
        ),
        sources,
    )
    character = Character(sources)
    assert spell_levels(character) == {
        "Disintegrate": 17,
        "Teleport": 17,
        "Mind Blank": 17,
        "Time Stop": 17,
    }
    assert [f.name for f in character.features] == ["Magical Mastery"]


def _savant_builders():
    """(school, subclass builder classes by level, spells to pick per level)."""
    return {
        "Conjuration": (
            {
                3: WizardConjurer.WizardConjurerLevel3,
                5: WizardConjurer.WizardConjurerLevel5,
                7: WizardConjurer.WizardConjurerLevel7,
                9: WizardConjurer.WizardConjurerLevel9,
                11: WizardConjurer.WizardConjurerLevel11,
                13: WizardConjurer.WizardConjurerLevel13,
                15: WizardConjurer.WizardConjurerLevel15,
                17: WizardConjurer.WizardConjurerLevel17,
            },
        ),
        "Enchantment": (
            {
                3: WizardEnchanter.WizardEnchanterLevel3,
                5: WizardEnchanter.WizardEnchanterLevel5,
                7: WizardEnchanter.WizardEnchanterLevel7,
                9: WizardEnchanter.WizardEnchanterLevel9,
                11: WizardEnchanter.WizardEnchanterLevel11,
                13: WizardEnchanter.WizardEnchanterLevel13,
                15: WizardEnchanter.WizardEnchanterLevel15,
                17: WizardEnchanter.WizardEnchanterLevel17,
            },
        ),
        "Necromancy": (
            {
                3: WizardNecromancer.WizardNecromancerLevel3,
                5: WizardNecromancer.WizardNecromancerLevel5,
                7: WizardNecromancer.WizardNecromancerLevel7,
                9: WizardNecromancer.WizardNecromancerLevel9,
                11: WizardNecromancer.WizardNecromancerLevel11,
                13: WizardNecromancer.WizardNecromancerLevel13,
                15: WizardNecromancer.WizardNecromancerLevel15,
                17: WizardNecromancer.WizardNecromancerLevel17,
            },
        ),
        "Transmutation": (
            {
                3: WizardTransmuter.WizardTransmuterLevel3,
                5: WizardTransmuter.WizardTransmuterLevel5,
                7: WizardTransmuter.WizardTransmuterLevel7,
                9: WizardTransmuter.WizardTransmuterLevel9,
                11: WizardTransmuter.WizardTransmuterLevel11,
                13: WizardTransmuter.WizardTransmuterLevel13,
                15: WizardTransmuter.WizardTransmuterLevel15,
                17: WizardTransmuter.WizardTransmuterLevel17,
            },
        ),
    }


# Wizard class table, "new level of spell slots": 2nd-level slots arrive at Wizard
# level 3, 3rd at 5, 4th at 7, 5th at 9, 6th at 11, 7th at 13, 8th at 15, 9th at 17.
# Savant: "two ... no higher than level 2" at 3, then one per new slot level.
SAVANT_MAX_SPELL_LEVEL = {3: 2, 5: 3, 7: 4, 9: 5, 11: 6, 13: 7, 15: 8, 17: 9}


@pytest.mark.parametrize(
    "school", ["Conjuration", "Enchantment", "Necromancy", "Transmutation"]
)
def test_savant_pick_levels_are_one_per_new_slot_level(school):
    builders = _savant_builders()[school][0]
    assert sorted(builders) == sorted(SAVANT_MAX_SPELL_LEVEL)
    for level, builder_class in builders.items():
        assert builder_class.__name__.endswith(f"Level{level}")


def _annotation_levels(builder_class, field_name):
    """Spell levels permitted by a builder field's type annotation, read off the
    names of the school enums in the union (e.g. ConjurationLevel3Spells -> 3)."""
    import attr
    import re

    annotation = attr.fields_dict(builder_class)[field_name].type
    members = getattr(annotation, "__args__", None) or (annotation,)
    levels = set()
    for member in members:
        match = re.search(r"Level(\d)Spells", member.__name__)
        levels.add(int(match.group(1)))
    return levels


@pytest.mark.parametrize(
    "school", ["Conjuration", "Enchantment", "Necromancy", "Transmutation"]
)
def test_savant_picks_are_capped_by_the_slot_levels_available(school):
    # conjurer.txt etc.: "The chosen spell must be of a level for which you have
    # spell slots" (level 3: "no higher than level 2").
    builders = _savant_builders()[school][0]
    for level, builder_class in builders.items():
        fields = ["spell_1", "spell_2"] if level == 3 else ["spell"]
        for name in fields:
            assert max(_annotation_levels(builder_class, name)) == (
                SAVANT_MAX_SPELL_LEVEL[level]
            ), (school, level)


def test_conjurer_savant_grants_two_then_one_per_tier():
    sources = CharacterSources(spell_casting_ability=Ability.INTELLIGENCE)
    apply_level(
        WizardConjurer.WizardConjurerLevel3(
            SL.ConjurationLevel1Spells.GREASE,
            SL.ConjurationLevel2Spells.CLOUD_OF_DAGGERS,
        ),
        sources,
    )
    assert spell_levels(Character(sources)) == {"Grease": 3, "Cloud of Daggers": 3}
    apply_level(
        WizardConjurer.WizardConjurerLevel5(SL.ConjurationLevel3Spells.SUMMON_FEY),
        sources,
    )
    apply_level(
        WizardConjurer.WizardConjurerLevel17(SL.ConjurationLevel9Spells.GATE), sources
    )
    assert spell_levels(Character(sources)) == {
        "Grease": 3,
        "Cloud of Daggers": 3,
        "Summon Fey": 5,
        "Gate": 17,
    }


def test_necromancer_adds_find_familiar_at_3_and_animate_dead_at_6():
    # necromancer.txt: "Undead Familiar. The Find Familiar spell appears in your
    # spellbook" (Level 3); Undead Thralls: "You always have Animate Dead
    # prepared" (Level 6).
    sources = CharacterSources(spell_casting_ability=Ability.INTELLIGENCE)
    apply_level(
        WizardNecromancer.WizardNecromancerLevel3(
            SL.NecromancyLevel1Spells.CAUSE_FEAR,
            SL.NecromancyLevel2Spells.RAY_OF_ENFEEBLEMENT,
        ),
        sources,
    )
    levels = spell_levels(Character(sources))
    assert levels == {"Cause Fear": 3, "Ray of Enfeeblement": 3, "Find Familiar": 3}
    apply_level(WizardNecromancer.WizardNecromancerLevel6(), sources)
    assert spell_levels(Character(sources))["Animate Dead"] == 6


def test_transmuter_always_prepares_alter_self_at_3_and_polymorph_at_10():
    # transmuter.txt: Wondrous Alteration "You always have the Alter Self spell
    # prepared" (3); Shape-Shifter "You always have the Polymorph spell prepared" (10).
    sources = CharacterSources(spell_casting_ability=Ability.INTELLIGENCE)
    apply_level(
        WizardTransmuter.WizardTransmuterLevel3(
            SL.TransmutationLevel1Spells.CATAPULT,
            SL.TransmutationLevel2Spells.BLINDNESS_DEAFNESS,
        ),
        sources,
    )
    assert spell_levels(Character(sources)) == {
        "Alter Self": 3,
        "Catapult": 3,
        "Blindness/Deafness": 3,
    }
    apply_level(WizardTransmuter.WizardTransmuterLevel10(), sources)
    assert spell_levels(Character(sources))["Polymorph"] == 10


# ---------------------------------------------------------------------------
# Uses, recharge, activation, DC


@pytest.mark.parametrize(
    "intelligence, expected",
    # modifier = floor((score - 10) / 2); "(minimum of once)".
    [(1, 1), (8, 1), (10, 1), (11, 1), (12, 1), (13, 1), (14, 2), (16, 3), (20, 5)],
)
@pytest.mark.parametrize(
    "feature_class, character_class",
    [
        (WizardConjurerFeatures.BenignTransposition, CharacterClass.WIZARD),
        (WizardEnchanterFeatures.HypnoticPresence, CharacterClass.WIZARD),
        (WizardTransmuterFeatures.EmpoweredTransmutation, CharacterClass.WIZARD),
        (ArcherF.ArcaneShot, CharacterClass.FIGHTER),
    ],
    ids=[
        "BenignTransposition",
        "HypnoticPresence",
        "EmpoweredTransmutation",
        "ArcaneShot",
    ],
)
def test_intelligence_modifier_uses_have_a_minimum_of_one(
    make_character, feature_class, character_class, intelligence, expected
):
    character = make_character(intelligence=intelligence, levels={character_class: 10})
    assert feature_class().number_of_uses(character) == expected


@pytest.mark.parametrize(
    "intelligence, expected",
    # enchanter.txt Split Enchantment: "a number of times equal to your
    # Intelligence modifier" - no minimum stated (unlike its siblings).
    [(8, 0), (10, 0), (11, 0), (12, 1), (14, 2), (18, 4), (20, 5)],
)
def test_split_enchantment_uses_equal_intelligence_modifier_without_minimum(
    make_character, intelligence, expected
):
    character = make_character(
        intelligence=intelligence, levels={CharacterClass.WIZARD: 10}
    )
    assert (
        WizardEnchanterFeatures.SplitEnchantment().number_of_uses(character) == expected
    )


@pytest.mark.parametrize("wizard_level", [3, 6, 10, 14, 18])
@pytest.mark.parametrize("intelligence", [8, 16, 20])
def test_enchanter_save_dcs_are_8_plus_proficiency_plus_intelligence(
    make_character, wizard_level, intelligence
):
    # enchanter.txt: Hypnotic Presence / Instinctive Charm / Alter Memories all use
    # "your spell save DC" = 8 + proficiency bonus + spellcasting modifier (INT).
    # Modifier by hand: 8 -> -1, 16 -> +3, 20 -> +5.
    modifier = {8: -1, 16: 3, 20: 5}[intelligence]
    character = make_character(
        intelligence=intelligence, levels={CharacterClass.WIZARD: wizard_level}
    )
    expected = 8 + PHB_PROFICIENCY[wizard_level] + modifier
    for feature in (
        WizardEnchanterFeatures.HypnoticPresence(),
        WizardEnchanterFeatures.InstinctiveCharm(),
        WizardEnchanterFeatures.AlterMemories(),
    ):
        assert feature.calculate_dc(character) == expected, feature.name


@pytest.mark.parametrize("fighter_level", [3, 7, 10, 15, 18])
def test_arcane_shot_dc_uses_proficiency_bonus_for_each_level(
    make_character, fighter_level
):
    # arcane_archer.txt: "the DC equals 8 plus your Intelligence modifier and
    # Proficiency Bonus". INT 14 (+2).
    character = make_character(
        intelligence=14, levels={CharacterClass.FIGHTER: fighter_level}
    )
    expected = 8 + 2 + PHB_PROFICIENCY[fighter_level]
    assert ArcherF.ArcaneShot().calculate_dc(character) == expected
    for option in (
        ArcherF.BanishingShot(),
        ArcherF.GraspingShot(),
        ArcherF.PiercingShot(),
        ArcherF.SeekingShot(),
    ):
        assert option.calculate_dc(character) == expected, option.name


# (feature factory, action type, uses, regained_on) from each text.
RECHARGE_TABLE = [
    # conjurer.txt
    (
        WizardConjurerFeatures.BenignTransposition,
        ActionType.BONUS_ACTION,
        RegainedOn.LONG_REST,
    ),
    (WizardConjurerFeatures.SplinteredSummons, None, RegainedOn.LONG_REST),
    # enchanter.txt
    (WizardEnchanterFeatures.HypnoticPresence, ActionType.ACTION, RegainedOn.LONG_REST),
    (WizardEnchanterFeatures.SplitEnchantment, None, RegainedOn.LONG_REST),
    (
        WizardEnchanterFeatures.InstinctiveCharm,
        ActionType.REACTION,
        RegainedOn.LONG_REST,
    ),
    # necromancer.txt
    (WizardNecromancerFeatures.UndeadThralls, None, RegainedOn.LONG_REST),
    (WizardNecromancerFeatures.DeathsMaster, None, RegainedOn.LONG_REST),
    # transmuter.txt
    (WizardTransmuterFeatures.EmpoweredTransmutation, None, RegainedOn.LONG_REST),
    # arcana_domain.txt: "until you finish a Short or Long Rest"
    (ClericArcanaFeatures.DispellingRecovery, None, RegainedOn.SHORT_OR_LONG_REST),
    # arcane_archer.txt
    (ArcherF.ArcaneShot, None, RegainedOn.SHORT_OR_LONG_REST),
    (ArcherF.MagicalAmmunition, ActionType.ACTION, RegainedOn.SHORT_OR_LONG_REST),
    (ArcherF.EverReadyShot, None, RegainedOn.INITIATIVE_ROLL),
    # vestige_patron.txt: "until you finish a Long Rest"
    (WarlockVestigeFeatures.VestigeRecovery, ActionType.REACTION, RegainedOn.LONG_REST),
    (WarlockVestigeFeatures.SemblanceOfLife, None, RegainedOn.LONG_REST),
]


@pytest.mark.parametrize(
    "feature_class, action_type, regained",
    RECHARGE_TABLE,
    ids=[row[0].__name__ for row in RECHARGE_TABLE],
)
def test_recharge_and_action_cost(make_character, feature_class, action_type, regained):
    character = make_character(intelligence=10, levels={CharacterClass.WIZARD: 20})
    feature = feature_class()
    assert feature.regained_on(character) == regained
    if action_type is not None:
        assert feature.activation.action_type == action_type


@pytest.mark.parametrize(
    "feature_class",
    [
        WizardConjurerFeatures.SplinteredSummons,
        WizardEnchanterFeatures.InstinctiveCharm,
        WizardNecromancerFeatures.UndeadThralls,
        WizardNecromancerFeatures.DeathsMaster,
        ClericArcanaFeatures.DispellingRecovery,
        ArcherF.MagicalAmmunition,
        WarlockVestigeFeatures.VestigeRecovery,
        WarlockVestigeFeatures.SemblanceOfLife,
    ],
)
def test_once_per_rest_features_have_exactly_one_use(make_character, feature_class):
    # "Once you use this feature ... you can't do so again until you finish a ... Rest."
    assert feature_class().number_of_uses(make_character()) == 1


def test_ranges_and_durations_match_the_text(make_character):
    assert WizardConjurerFeatures.BenignTransposition().activation.range == "30 Feet"
    # conjurer.txt Distant Transposition: "increases to 60 feet"
    assert WizardConjurerFeatures.DistantTransposition().activation.range == "60 Feet"
    hypnotic = WizardEnchanterFeatures.HypnoticPresence().activation
    assert (hypnotic.range, hypnotic.duration) == ("10 Feet", "1 Minute")
    assert WizardEnchanterFeatures.InstinctiveCharm().activation.range == "30 Feet"
    assert ArcherF.CurvingShot().activation.action_type == ActionType.BONUS_ACTION
    assert ArcherF.CurvingShot().activation.range == "60 Feet"
    assert ArcherF.IndomitableTeleport().activation.range == "60 Feet"
    assert ArcherF.MasterfulShots().activation.action_type == ActionType.REACTION
    assert WizardNecromancerFeatures.HarvestUndead().activation.action_type == (
        ActionType.REACTION
    )
    assert WizardNecromancerFeatures.UndeadThralls().activation.range == "60 Feet"


@pytest.mark.parametrize(
    "fighter_level, die",
    # arcane_archer.txt: d6, "d8 at level 10, a d10 at level 15, and a d12 at level 18".
    [
        (3, "d6"),
        (9, "d6"),
        (10, "d8"),
        (14, "d8"),
        (15, "d10"),
        (17, "d10"),
        (18, "d12"),
        (20, "d12"),
    ],
)
def test_arcane_shot_die_is_read_from_fighter_level(make_character, fighter_level, die):
    character = make_character(levels={CharacterClass.FIGHTER: fighter_level})
    assert ArcherF.ARCANE_SHOT_DIE.at(character) == die


@pytest.mark.parametrize(
    "fighter_level, wizard_level, die",
    # Fighter 3 + Wizard 15 is character level 18, but the die follows FIGHTER level.
    [(3, 15, "d6"), (9, 11, "d6"), (10, 10, "d8"), (14, 6, "d8")],
)
def test_arcane_shot_die_ignores_other_class_levels(
    make_character, fighter_level, wizard_level, die
):
    character = make_character(
        levels={
            CharacterClass.FIGHTER: fighter_level,
            CharacterClass.WIZARD: wizard_level,
        }
    )
    assert ArcherF.ARCANE_SHOT_DIE.at(character) == die


# ---------------------------------------------------------------------------
# Skill and proficiency grants


@pytest.mark.parametrize(
    "skill", [Skill.DECEPTION, Skill.INTIMIDATION, Skill.PERSUASION]
)
@pytest.mark.parametrize(
    "intelligence, bonus",
    # "a bonus ... equal to your Intelligence modifier (minimum of +1)".
    [(8, 1), (10, 1), (12, 1), (14, 2), (20, 5)],
)
def test_conversationalist_bonus_is_intelligence_modifier_min_one(
    make_character, skill, intelligence, bonus
):
    from tests.test_subclass_features_2024 import apply_features

    character = apply_features(
        make_character(intelligence=intelligence, levels={CharacterClass.WIZARD: 3}),
        [WizardEnchanterFeatures.EnchantingConversationalist(skill)],
    )
    assert character.is_proficient_in_skill(skill)
    assert character.get_skill_bonus(skill) == bonus
    others = {Skill.DECEPTION, Skill.INTIMIDATION, Skill.PERSUASION} - {skill}
    for other in others:
        assert not character.is_proficient_in_skill(other)
        assert character.get_skill_bonus(other) == 0


def test_conversationalist_bonus_tracks_intelligence_changes(make_sources):
    # The bonus is a formula: rebuilding after an INT change must change it.
    from Model.AbilityScores import AbilityScores

    sources = make_sources(intelligence=10, levels={CharacterClass.WIZARD: 3})
    sources.add_effect(
        WizardEnchanterFeatures.EnchantingConversationalist(Skill.DECEPTION)
    )
    assert Character(sources).get_skill_bonus(Skill.DECEPTION) == 1
    sources.base_abilities = AbilityScores(10, 10, 10, 18, 10, 10)
    assert Character(sources).get_skill_bonus(Skill.DECEPTION) == 4


def test_arcane_archer_lore_cantrip_uses_intelligence(make_sources):
    # "Intelligence is your spellcasting ability for it."
    sources = make_sources(levels={CharacterClass.FIGHTER: 3})
    sources.spell_casting_ability = Ability.WISDOM
    apply_level(
        FighterArcaneArcher.FighterArcaneArcherLevel3(
            cantrip=SL.TransmutationLevel0Spells.PRESTIDIGITATION,
            arcane_shot_option_1=ArcherF.BurstingShot(),
            arcane_shot_option_2=ArcherF.ShadowShot(),
        ),
        sources,
    )
    character = Character(sources).validate()
    assert [s.name for s in character.spells] == ["Prestidigitation"]
    assert character.spells[0].ability == Ability.INTELLIGENCE
    assert character.is_proficient_in_skill(Skill.ARCANA)
    assert character.is_proficient_in_skill(Skill.NATURE)


def test_arcane_archer_example_has_arcana_and_nature():
    character = build_example(ARCHER, 3)
    assert character.is_proficient_in_skill(Skill.ARCANA)
    assert character.is_proficient_in_skill(Skill.NATURE)


def test_arcane_archer_lore_replacement_skill_is_a_fighter_level_1_skill():
    # Fighter level-1 list (2024 PHB): Acrobatics, Animal Handling, Athletics,
    # History, Insight, Intimidation, Perception, Survival.
    for skill in (Skill.ACROBATICS, Skill.SURVIVAL, Skill.PERCEPTION):
        ArcherF.ArcaneArcherLore(
            SL.TransmutationLevel0Spells.DRUIDCRAFT, Skill.ARCANA, skill
        )
    for skill in (Skill.STEALTH, Skill.MEDICINE, Skill.RELIGION):
        with pytest.raises(ValueError):
            ArcherF.ArcaneArcherLore(
                SL.TransmutationLevel0Spells.DRUIDCRAFT, Skill.ARCANA, skill
            )
    with pytest.raises(ValueError):
        # Both skills named the same: that is one proficiency, not two.
        ArcherF.ArcaneArcherLore(
            SL.TransmutationLevel0Spells.DRUIDCRAFT, Skill.ARCANA, Skill.ARCANA
        )


def test_student_of_arcana_pool_is_arcana_plus_cleric_level_1_skills():
    # Cleric level-1 list (2024 PHB): History, Insight, Medicine, Persuasion, Religion.
    for skill in (
        Skill.ARCANA,
        Skill.HISTORY,
        Skill.INSIGHT,
        Skill.MEDICINE,
        Skill.PERSUASION,
        Skill.RELIGION,
    ):
        ClericArcanaFeatures.StudentOfArcana(skill, "Fire Bolt", "Mage Hand")
    for skill in (Skill.NATURE, Skill.ATHLETICS, Skill.STEALTH):
        with pytest.raises(ValueError):
            ClericArcanaFeatures.StudentOfArcana(skill, "Fire Bolt", "Mage Hand")


def test_necrotic_resistance_arrives_with_the_spellbook_not_before():
    from tests.test_subclass_features_2024 import apply_features  # noqa: F401

    for level, resistant in ((2, False), (3, True), (20, True)):
        character = build_example(NECROMANCER, level)
        assert character.is_resistant_to_damage(DamageType.NECROTIC) is resistant, level


def test_necrotic_resistance_is_only_necrotic():
    character = build_example(NECROMANCER)
    for damage_type in DamageType:
        if damage_type is DamageType.NECROTIC:
            continue
        assert not character.is_resistant_to_damage(damage_type), damage_type


# ---------------------------------------------------------------------------
# Vestige Companion stat block (vestige_patron.txt)


@pytest.mark.parametrize(
    "vestige_type, damage, power_name",
    [
        (WarlockVestigeType.CELESTIAL, DamageType.RADIANT, "Healing Touch"),
        (WarlockVestigeType.FIEND, DamageType.FIRE, "Fiendish Swap"),
        (WarlockVestigeType.UNDEAD, DamageType.NECROTIC, "Cursed Invocation"),
    ],
)
def test_vestige_stat_block_matches_the_text(
    make_character, vestige_type, damage, power_name
):
    # Warlock 5 (PB +3), CHA 16 (+3): AC 13+3=16, HP 4+4*5=24, spell attack 3+3=+6,
    # strike damage 1d6+3+3 = 1d6 + 6.
    character = make_character(charisma=16, levels={CharacterClass.WARLOCK: 5})
    vestige = WarlockVestigeFeatures._build_vestige(character, vestige_type)
    assert (vestige.ac, vestige.hp) == (16, 24)
    assert [vestige.ability_scores[a.short_name] for a in Ability] == [
        1,
        14,
        10,
        15,
        15,
        16,
    ]
    assert [vestige.saving_throws[a.short_name] for a in Ability] == [-5, 2, 0, 2, 2, 3]
    assert (vestige.speed_ground_ft, vestige.speed_fly_ft) == (5, 30)
    assert vestige.initiative_bonus == 2
    assert vestige.size == CreatureSize.SMALL
    assert vestige.senses == "Passive Perception 12"
    strike = vestige.actions[0]
    assert strike.name == "Vestige's Strike"
    assert "+6" in strike.description and "1d6 + 6" in strike.description
    assert damage.value in strike.description
    assert power_name in vestige.bonus_actions[0].name


def test_vestige_hit_points_scale_with_warlock_level(make_character):
    # "4 + four times your Warlock level"
    for level, hp in ((3, 16), (10, 44), (14, 60)):
        character = make_character(levels={CharacterClass.WARLOCK: level})
        vestige = WarlockVestigeFeatures._build_vestige(
            character, WarlockVestigeType.FIEND
        )
        assert vestige.hp == hp


@pytest.mark.parametrize("vestige_type", list(WarlockVestigeType))
def test_vestige_power_changes_the_divine_power_text_only_from_level_6(vestige_type):
    # vestige_patron.txt Level 6: "Your Vestige Companion now regains its use of
    # Divine Power whenever you finish a Short or Long Rest."
    before = WarlockVestigeFeatures._build_vestige(
        build_example(VESTIGE, 5), vestige_type
    )
    after = WarlockVestigeFeatures._build_vestige(
        build_example(VESTIGE, 6), vestige_type
    )
    assert "Short or Long Rest" not in before.bonus_actions[0].description
    assert "Short or Long Rest" in after.bonus_actions[0].description


# ---------------------------------------------------------------------------
# Multiclass


def _multiclass_character(wizard_level):
    from Builds.Examples import (
        Y2024_Fighter_ArcaneArcher_SylvaineFarshot as archer,
        Y2024_Wizard_Conjuration_CorvinFarsummon as conjurer,
    )
    from CharacterContent.Species import Gnome

    wizard = conjurer.get_starter_class_builder()
    wizard.base_class_level = 2
    fighter = archer.get_starter_class_builder()
    multiclass = FighterArcaneArcher.FighterArcaneArcherMulticlassBuilder(
        fighter_level_features=fighter.base_class_level_features,
        fighter_level=wizard_level,
    )
    builder = CharacterBuilder(
        name="Multiclass",
        starter_class_builder=wizard,
        species_builder=Gnome.RockGnomeSpeciesBuilder(),
        multiclass_builders=[multiclass],
    )
    return builder.build().validate()


@pytest.mark.parametrize(
    "fighter_level, expected_options", [(2, 0), (3, 2), (7, 3), (10, 4)]
)
def test_multiclass_archer_features_follow_fighter_level_not_character_level(
    fighter_level, expected_options
):
    # Wizard 2 + Fighter N: the subclass table counts Fighter levels only.
    character = _multiclass_character(fighter_level)
    names = feature_names(character)
    assert ("Arcane Shot" in names) == (fighter_level >= 3)
    assert ("Curving Shot" in names) == (fighter_level >= 7)
    assert ("Ever-Ready Shot" in names) == (fighter_level >= 10)
    options = [
        f
        for f in character.iter_features_with_extensions()
        if f.origin == "Arcane Shot Option"
    ]
    assert len(options) == expected_options
    assert character.character_level == 2 + fighter_level


def test_multiclass_archer_dc_uses_total_level_proficiency(make_character):
    # Wizard 2 + Fighter 7 = character level 9: proficiency +4 (levels 9-12).
    character = _multiclass_character(7)
    assert character.get_proficiency_bonus() == 4
    intelligence_modifier = character.get_intelligence_modifier()
    assert ArcherF.ArcaneShot().calculate_dc(character) == 8 + 4 + intelligence_modifier
    assert ArcherF.ARCANE_SHOT_DIE.at(character) == "d6"


# ---------------------------------------------------------------------------
# Content integrity


WIZARD_SPELL_NAMES = {
    m.value for n in range(0, 10) for m in getattr(SL, f"WizardLevel{n}Spells")
}


@pytest.mark.parametrize(
    "module",
    [
        CONJURER,
        ENCHANTER,
        NECROMANCER,
        pytest.param(
            TRANSMUTER,
            marks=pytest.mark.xfail(
                strict=True,
                reason="BUG: Builds/Examples/Y2024_Wizard_Transmutation_AlistairFormbend "
                "picks Regenerate (Bard/Cleric/Druid), Animal Shapes (Druid) and "
                "Earthquake (Cleric/Druid/Sorcerer) as Transmutation Savant spells; "
                "transmuter.txt: 'Wizard spells from the Transmutation school'. "
                "Edition: 2024 PHB spell lists.",
            ),
        ),
    ],
)
def test_example_spells_are_all_wizard_spells(module):
    # Savant: "Choose ... Wizard spells from the <school> school".
    outside = [
        name
        for name in spell_levels(build_example(module))
        if name not in WIZARD_SPELL_NAMES
    ]
    assert outside == []


def test_cleric_magical_mastery_example_adds_one_wizard_spell_per_level_6_to_9():
    # arcana_domain.txt Level 17: "four Wizard spells, one from each of levels 6, 7, 8, and 9".
    before = {s.name for s in build_example(CLERIC, 16).spells}
    wizard_by_level = {
        n: {m.value for m in getattr(SL, f"WizardLevel{n}Spells")} for n in (6, 7, 8, 9)
    }
    new = [s.name for s in build_example(CLERIC, 17).spells if s.name not in before]
    found = {
        n: [name for name in new if name in wizard_by_level[n]] for n in (6, 7, 8, 9)
    }
    # (A Cleric also prepares one level-9 spell of its own at 17, e.g. Gate,
    # which is on the Wizard list too - so level 9 may show two.)
    assert [len(found[n]) for n in (6, 7, 8)] == [1, 1, 1]
    assert len(found[9]) in (1, 2)


@pytest.mark.xfail(
    strict=True,
    reason="BUG: conjurer.txt Conjuration Savant says 'Wizard spells from the "
    "Conjuration school'; the builder accepts any Conjuration spell (Goodberry, "
    "a Druid spell) with no check. Same for the Enchanter, Necromancer and "
    "Transmuter savants.",
)
def test_savant_rejects_spells_that_are_not_on_the_wizard_list():
    with pytest.raises(ValueError):
        WizardConjurer.WizardConjurerLevel3(
            SL.ConjurationLevel1Spells.GOODBERRY,
            SL.ConjurationLevel2Spells.CLOUD_OF_DAGGERS,
        )
