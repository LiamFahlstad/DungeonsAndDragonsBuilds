"""
Feats under CharacterContent/Features/CharacterFeats/: origin feats
(OriginFeats.py), general feats (GeneralFeats.py), backgrounds
(Backgrounds.py) and epic boons (EpicBoon.py).

Expected values come from the 2024 PHB feat text (which the engine's own
`get_description()` strings happen to quote closely - the *numbers* below are
independently hand-derived from the rule, not copied from running the code):

- Half-feats ("Actor", "Durable", ...): "+1 to <ability>, to a maximum of 20."
  Level 4+ prerequisite (2024 PHB general feats).
- Tough: "You gain 2 additional Hit Points for each level you have. Whenever
  you gain a new level, you gain 2 additional Hit Points." -> total bonus is
  2 * character level (using total character level for multiclass, since the
  feat says "each level you have", not "each level in the class you took it
  with").
- Alert (2024 PHB): "you can add your Proficiency Bonus to the [Initiative]
  roll." Proficiency bonus by level is the 2024 PHB table (2/3/4/5/6 for
  levels 1-4/5-8/9-12/13-16/17-20), transcribed here rather than computed
  with the engine's own formula.
- Resilient: "+1 to the chosen ability, to a maximum of 20" + "you gain
  saving throw proficiency with the chosen ability."
- Skilled / Free Background Skill Proficiency: proficiency in a specific
  count of skills, validated against the full skill list.
- Magic Initiate: two cantrips + one level 1 spell from a single class list
  (Cleric, Druid, or Wizard), validated against that class's spell list.
- Familiar Friend (Arcana Unleashed 2026 homebrew): the feat's own
  description says "You can cast it once...and you regain the ability to
  cast it in this way when you finish a Long Rest" (Find Familiar) - i.e.
  ONE use per long rest, independent of Proficiency Bonus.

No real Epic Boon is implemented in this codebase (EpicBoon.py only has a
`DummyEpicBoon` placeholder with no ability score or cap-at-30 logic), so
there is nothing rules-bearing to test there beyond that it's a harmless
no-op; this is called out in the test report rather than encoded as a bug.
"""

import pytest

from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    EpicBoon,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Spells.SpellLists import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    DruidLevel0Spells,
    DruidLevel1Spells,
    WizardLevel0Spells,
    WizardLevel1Spells,
)
from Core.Definitions import Ability, CharacterClass, Sense, Skill

STR, DEX, CON, INT, WIS, CHA = (
    Ability.STRENGTH,
    Ability.DEXTERITY,
    Ability.CONSTITUTION,
    Ability.INTELLIGENCE,
    Ability.WISDOM,
    Ability.CHARISMA,
)

# 2024 PHB proficiency bonus by character level, transcribed from the table
# (not derived from the engine's own formula).
PHB_PROFICIENCY_BONUS = {
    1: 2,
    2: 2,
    3: 2,
    4: 2,
    5: 3,
    6: 3,
    7: 3,
    8: 3,
    9: 4,
    10: 4,
    11: 4,
    12: 4,
    13: 5,
    14: 5,
    15: 5,
    16: 5,
    17: 6,
    18: 6,
    19: 6,
    20: 6,
}


def xfail_bug(reason: str):
    return pytest.mark.xfail(strict=True, reason=f"BUG: {reason}")


# ---------------------------------------------------------------------------
# Origin feats
# ---------------------------------------------------------------------------


class TestSkilled:
    def test_grants_three_skill_proficiencies(self, make_character):
        character = make_character()
        chosen = [Skill.ATHLETICS, Skill.ARCANA, Skill.PERSUASION]
        OriginFeats.Skilled(chosen).apply(character)
        for skill in chosen:
            assert character.is_proficient_in_skill(skill)
        assert not character.is_proficient_in_skill(Skill.STEALTH)

    def test_rejects_wrong_count(self):
        with pytest.raises(ValueError):
            OriginFeats.Skilled([Skill.ATHLETICS, Skill.ARCANA])

    def test_rejects_duplicate_skills(self):
        with pytest.raises(ValueError):
            OriginFeats.Skilled([Skill.ATHLETICS, Skill.ATHLETICS, Skill.ARCANA])


class TestAlert:
    @pytest.mark.parametrize(
        "level", [1, 4, 5, 8, 9, 12, 13, 16, 17, 20], ids=lambda l: f"level_{l}"
    )
    def test_initiative_gains_proficiency_bonus(self, make_character, level):
        # 2024 PHB Alert: "you can add your Proficiency Bonus to the roll."
        character = make_character(dexterity=16, levels={CharacterClass.FIGHTER: level})
        dex_modifier = 3  # DEX 16 -> +3
        expected_pb = PHB_PROFICIENCY_BONUS[level]
        OriginFeats.Alert().apply(character)
        assert character.initiative == dex_modifier + expected_pb

    def test_no_initiative_bonus_without_the_feat(self, make_character):
        character = make_character(dexterity=16, levels={CharacterClass.FIGHTER: 5})
        assert character.initiative == 3


class TestTough:
    @pytest.mark.parametrize(
        "level,expected_bonus",
        [(1, 2), (4, 8), (5, 10), (11, 22), (20, 40)],
        ids=lambda v: str(v),
    )
    def test_hit_point_bonus_scales_with_level(
        self, make_character, level, expected_bonus
    ):
        # "You gain 2 additional Hit Points for each level you have."
        character = make_character(levels={CharacterClass.FIGHTER: level})
        OriginFeats.Tough().apply(character)
        assert character.combat.hit_points_bonus == expected_bonus

    def test_hit_point_bonus_uses_total_character_level_when_multiclassed(
        self, make_character
    ):
        # Fighter 3 / Wizard 2 = character level 5, even though neither class
        # alone reached level 5: the feat scales off total level, "each level
        # you have", not levels in a single class.
        character = make_character(
            levels={CharacterClass.FIGHTER: 3, CharacterClass.WIZARD: 2}
        )
        OriginFeats.Tough().apply(character)
        assert character.combat.hit_points_bonus == 10

    def test_full_hit_points_level_1_fighter(self, make_character):
        # Fighter d10 hit die, CON 10 (+0): 10 + 0, then Tough's +2*1.
        character = make_character(constitution=10, levels={CharacterClass.FIGHTER: 1})
        OriginFeats.Tough().apply(character)
        assert character.calculate_hit_points() == 12

    def test_full_hit_points_level_5_fighter(self, make_character):
        # Fighter d10 (avg 6), CON 14 (+2): 10+2, then 4*(6+2) = 32 -> 44,
        # then Tough's +2*5 = 10 -> 54.
        character = make_character(constitution=14, levels={CharacterClass.FIGHTER: 5})
        OriginFeats.Tough().apply(character)
        assert character.calculate_hit_points() == 54

    def test_full_hit_points_level_20_fighter(self, make_character):
        # Fighter d10 (avg 6), CON 20 (+5): 10+5, then 19*(6+5) = 209 -> 224,
        # then Tough's +2*20 = 40 -> 264.
        character = make_character(constitution=20, levels={CharacterClass.FIGHTER: 20})
        OriginFeats.Tough().apply(character)
        assert character.calculate_hit_points() == 264


class TestMagicInitiate:
    def test_cleric_variant_prepares_chosen_spells(self, make_character):
        feat = OriginFeats.MagicInitiateCleric(
            cantrip_1=ClericLevel0Spells.SACRED_FLAME,
            cantrip_2=ClericLevel0Spells.GUIDANCE,
            spell=ClericLevel1Spells.BLESS,
            spell_casting_ability=WIS,
        )
        assert feat.get_spells() == ["Sacred Flame", "Guidance", "Bless"]
        assert feat.get_spell_casting_ability() == WIS

    def test_wizard_variant_prepares_chosen_spells(self, make_character):
        feat = OriginFeats.MagicInitiateWizard(
            cantrip_1=WizardLevel0Spells.FIRE_BOLT,
            cantrip_2=WizardLevel0Spells.MAGE_HAND,
            spell=WizardLevel1Spells.BURNING_HANDS,
            spell_casting_ability=INT,
        )
        assert feat.get_spells() == ["Fire Bolt", "Mage Hand", "Burning Hands"]

    def test_druid_variant_prepares_chosen_spells(self, make_character):
        feat = OriginFeats.MagicInitiateDruid(
            cantrip_1=DruidLevel0Spells.PRODUCE_FLAME,
            cantrip_2=DruidLevel0Spells.GUIDANCE,
            spell=DruidLevel1Spells.CURE_WOUNDS,
            spell_casting_ability=WIS,
        )
        assert feat.get_spells() == ["Produce Flame", "Guidance", "Cure Wounds"]

    def test_rejects_cantrip_not_on_chosen_class_list(self):
        with pytest.raises(ValueError):
            OriginFeats.MagicInitiateWizard(
                cantrip_1="Not A Real Spell",
                cantrip_2=WizardLevel0Spells.MAGE_HAND,
                spell=WizardLevel1Spells.BURNING_HANDS,
                spell_casting_ability=INT,
            )

    def test_rejects_level_1_spell_from_wrong_class_list(self):
        with pytest.raises(ValueError):
            OriginFeats.MagicInitiateCleric(
                cantrip_1=ClericLevel0Spells.SACRED_FLAME,
                cantrip_2=ClericLevel0Spells.GUIDANCE,
                spell=WizardLevel1Spells.BURNING_HANDS,  # not a Cleric spell
                spell_casting_ability=WIS,
            )

    def test_base_class_rejects_non_cleric_druid_wizard(self):
        with pytest.raises(ValueError):
            OriginFeats.MagicInitiate(
                cantrip_1="Vicious Mockery",
                cantrip_2="Vicious Mockery",
                spell="Healing Word",
                spell_casting_ability=CHA,
                character_class=CharacterClass.BARD,
            )


class TestEmeraldEnclaveFledgling:
    def test_always_prepares_speak_with_animals(self):
        feat = OriginFeats.EmeraldEnclaveFledgling(spell_casting_ability=WIS)
        assert feat.get_spells() == [DruidLevel1Spells.SPEAK_WITH_ANIMALS]
        assert feat.get_spell_casting_ability() == WIS

    @pytest.mark.parametrize("bad_ability", [STR, DEX, CON])
    def test_rejects_physical_spellcasting_ability(self, bad_ability):
        with pytest.raises(ValueError):
            OriginFeats.EmeraldEnclaveFledgling(spell_casting_ability=bad_ability)


class TestFamiliarFriend:
    def test_always_prepares_find_familiar(self):
        feat = OriginFeats.FamiliarFriend(spell_casting_ability=INT)
        assert feat.get_spells() == ["Find Familiar"]

    @pytest.mark.parametrize("bad_ability", [STR, DEX, CON])
    def test_rejects_physical_spellcasting_ability(self, bad_ability):
        with pytest.raises(ValueError):
            OriginFeats.FamiliarFriend(spell_casting_ability=bad_ability)

    def test_number_of_uses_is_one_per_long_rest(self, make_character):
        character = make_character(levels={CharacterClass.WIZARD: 5})
        feat = OriginFeats.FamiliarFriend(spell_casting_ability=INT)
        assert feat.number_of_uses(character) == 1


class TestPurpleDragonRook:
    def test_grants_proficiency_in_chosen_skill(self, make_character):
        character = make_character()
        OriginFeats.PurpleDragonRook(Skill.INSIGHT).apply(character)
        assert character.is_proficient_in_skill(Skill.INSIGHT)

    def test_rejects_skill_outside_entreat_pool(self):
        with pytest.raises(ValueError):
            OriginFeats.PurpleDragonRook(Skill.ATHLETICS)


class TestCrafter:
    def test_accepts_valid_tool_choices(self):
        feat = OriginFeats.Crafter(["Smith", "Weaver", "Woodcarver"])
        text = feat.get_tool_choices()
        assert "Smith's Tools" in text
        assert "Weaver's Tools" in text

    def test_rejects_unknown_tool(self):
        # Crafter defers validation to get_tool_choices() rather than
        # __init__ - the constructor itself doesn't check the tool names.
        feat = OriginFeats.Crafter(["Smith", "NotARealTool"])
        with pytest.raises(ValueError):
            feat.get_tool_choices()


# ---------------------------------------------------------------------------
# General feats: shared half-feat shape (+1 ability capped at 20, level 4+)
# ---------------------------------------------------------------------------

# (feat class, a valid ability per its own PHB text, an ability NOT on its list)
HALF_FEATS = [
    (GeneralFeats.Athlete, STR, CHA),
    (GeneralFeats.Athlete, DEX, CHA),
    (GeneralFeats.Chef, CON, STR),
    (GeneralFeats.Chef, WIS, STR),
    (GeneralFeats.CrossbowExpert, DEX, STR),
    (GeneralFeats.Crusher, STR, DEX),
    (GeneralFeats.Crusher, CON, DEX),
    (GeneralFeats.DefensiveDuelist, DEX, STR),
    (GeneralFeats.DualWielder, STR, CHA),
    (GeneralFeats.Durable, CON, STR),
    (GeneralFeats.ElementalAdept, INT, STR),
    (GeneralFeats.ElementalAdept, WIS, STR),
    (GeneralFeats.FeyTouched, CHA, STR),
    (GeneralFeats.Grappler, STR, CHA),
    (GeneralFeats.GreatWeaponMaster, STR, DEX),
    (GeneralFeats.InspiringLeader, WIS, STR),
    (GeneralFeats.InspiringLeader, CHA, STR),
    (GeneralFeats.KeenMind, INT, STR),
    (GeneralFeats.MageSlayer, STR, CHA),
    (GeneralFeats.MageSlayer, DEX, CHA),
    (GeneralFeats.MountedCombatant, WIS, CHA),
    (GeneralFeats.Observant, WIS, STR),
    (GeneralFeats.Piercer, DEX, CHA),
    (GeneralFeats.Poisoner, DEX, STR),
    (GeneralFeats.Poisoner, INT, STR),
    (GeneralFeats.PolearmMaster, STR, CHA),
    (GeneralFeats.RitualCaster, WIS, STR),
    (GeneralFeats.Sentinel, DEX, CHA),
    (GeneralFeats.ShadowTouched, CHA, STR),
    (GeneralFeats.Sharpshooter, DEX, STR),
    (GeneralFeats.ShieldMaster, STR, DEX),
    (GeneralFeats.Slasher, STR, CHA),
    (GeneralFeats.Speedy, DEX, STR),
    (GeneralFeats.SpellSniper, WIS, STR),
    (GeneralFeats.Telekinetic, CHA, STR),
    (GeneralFeats.Telepathic, CHA, STR),
    (GeneralFeats.WarCaster, INT, STR),
    (GeneralFeats.WeaponMaster, DEX, CHA),
]


@pytest.mark.parametrize(
    "feat_class,ability,other_ability",
    HALF_FEATS,
    ids=[f"{c.__name__}_{a.name}" for c, a, _ in HALF_FEATS],
)
class TestHalfFeatShape:
    def test_grants_plus_one_to_chosen_ability(
        self, make_character, feat_class, ability, other_ability
    ):
        character = make_character(**{ability.name.lower(): 14})
        feat_class(character_level=4, ability=ability).apply(character)
        assert character.get_ability_score(ability) == 15

    def test_capped_at_20(self, make_character, feat_class, ability, other_ability):
        character = make_character(**{ability.name.lower(): 20})
        feat_class(character_level=4, ability=ability).apply(character)
        assert character.get_ability_score(ability) == 20

    def test_rejects_ability_not_on_its_list(self, feat_class, ability, other_ability):
        with pytest.raises(ValueError):
            feat_class(character_level=4, ability=other_ability)

    def test_rejects_character_below_level_4(self, feat_class, ability, other_ability):
        with pytest.raises(ValueError):
            feat_class(character_level=3, ability=ability)


class TestResilient:
    def test_grants_ability_increase_and_save_proficiency(self, make_character):
        character = make_character(wisdom=14)
        assert not character.is_proficient_in_saving_throw(WIS)
        GeneralFeats.Resilient(character_level=4, ability=WIS).apply(character)
        assert character.get_ability_score(WIS) == 15
        assert character.is_proficient_in_saving_throw(WIS)

    def test_save_proficiency_still_granted_when_score_already_20(self, make_character):
        character = make_character(wisdom=20)
        GeneralFeats.Resilient(character_level=4, ability=WIS).apply(character)
        assert character.get_ability_score(WIS) == 20
        assert character.is_proficient_in_saving_throw(WIS)

    def test_any_ability_is_a_valid_choice(self, make_character):
        # Unlike most half-feats, Resilient's ability list is "any ability".
        character = make_character(strength=10)
        GeneralFeats.Resilient(character_level=4, ability=STR).apply(character)
        assert character.get_ability_score(STR) == 11
        assert character.is_proficient_in_saving_throw(STR)


class TestSkillExpert:
    def test_grants_ability_bonus_proficiency_and_expertise(self, make_character):
        character = make_character(intelligence=14)
        GeneralFeats.SkillExpert(
            character_level=4, ability=INT, skill=Skill.ARCANA
        ).apply(character)
        assert character.get_ability_score(INT) == 15
        assert character.is_proficient_in_skill(Skill.ARCANA)
        assert character.has_expertise_in_skill(Skill.ARCANA)

    def test_does_not_double_grant_if_already_proficient(self, make_character):
        character = make_character(intelligence=14)
        character.skills.add_skill_proficiency(Skill.ARCANA)
        # Should not raise, and should still add expertise on top of the
        # pre-existing proficiency.
        GeneralFeats.SkillExpert(
            character_level=4, ability=INT, skill=Skill.ARCANA
        ).apply(character)
        assert character.has_expertise_in_skill(Skill.ARCANA)

    def test_any_ability_is_a_valid_choice(self, make_character):
        character = make_character(charisma=10)
        GeneralFeats.SkillExpert(
            character_level=4, ability=CHA, skill=Skill.PERSUASION
        ).apply(character)
        assert character.get_ability_score(CHA) == 11


class TestSkulker:
    def test_grants_ten_foot_blindsight(self, make_character):
        character = make_character(dexterity=14)
        GeneralFeats.Skulker(character_level=4, ability=DEX).apply(character)
        assert character.get_sense_range(Sense.BLINDSIGHT) == 10

    def test_rejects_ability_not_dexterity(self):
        with pytest.raises(ValueError):
            GeneralFeats.Skulker(character_level=4, ability=STR)


class TestSavingThrowDCFeats:
    @pytest.mark.parametrize(
        "level,ability_score,expected_pb",
        [(4, 16, 2), (5, 16, 3), (9, 16, 4), (13, 16, 5), (17, 16, 6)],
    )
    def test_actor_dc_is_8_plus_charisma_mod_plus_proficiency(
        self, make_character, level, ability_score, expected_pb
    ):
        # DC 8 plus Charisma modifier and Proficiency Bonus. CHA 16 -> +3.
        character = make_character(
            charisma=ability_score, levels={CharacterClass.FIGHTER: level}
        )
        feat = GeneralFeats.Actor(character_level=4, ability=CHA)
        assert feat.calculate_dc(character) == 8 + 3 + expected_pb

    def test_shield_master_dc_is_8_plus_strength_mod_plus_proficiency(
        self, make_character
    ):
        # STR 18 -> +4, level 5 -> proficiency bonus +3.
        character = make_character(strength=18, levels={CharacterClass.FIGHTER: 5})
        feat = GeneralFeats.ShieldMaster(character_level=4, ability=STR)
        assert feat.calculate_dc(character) == 8 + 4 + 3

    def test_telekinetic_dc_uses_the_ability_increased_by_the_feat(
        self, make_character
    ):
        # DC uses the modifier of whichever ability (INT/WIS/CHA) was chosen
        # for this instance of the feat, not always the same one.
        character = make_character(
            wisdom=16, charisma=10, levels={CharacterClass.WIZARD: 5}
        )
        feat = GeneralFeats.Telekinetic(character_level=4, ability=WIS)
        assert feat.calculate_dc(character) == 8 + 3 + 3  # WIS 16 (+3), PB +3

    def test_poisoner_dc_uses_the_ability_increased_by_the_feat(self, make_character):
        character = make_character(
            dexterity=10, intelligence=18, levels={CharacterClass.ROGUE: 9}
        )
        feat = GeneralFeats.Poisoner(character_level=4, ability=INT)
        assert feat.calculate_dc(character) == 8 + 4 + 4  # INT 18 (+4), PB +4


# ---------------------------------------------------------------------------
# Backgrounds
# ---------------------------------------------------------------------------


class TestFreeBackgroundSkillProficiency:
    def test_grants_two_skill_proficiencies(self, make_character):
        character = make_character()
        chosen = [Skill.HISTORY, Skill.NATURE]
        Backgrounds.FreeBackgroundSkillProficiency(chosen).apply(character)
        for skill in chosen:
            assert character.is_proficient_in_skill(skill)

    def test_rejects_wrong_count(self):
        with pytest.raises(ValueError):
            Backgrounds.FreeBackgroundSkillProficiency([Skill.HISTORY])

    def test_rejects_duplicate_skills(self):
        with pytest.raises(ValueError):
            Backgrounds.FreeBackgroundSkillProficiency([Skill.HISTORY, Skill.HISTORY])


# ---------------------------------------------------------------------------
# Epic boons
# ---------------------------------------------------------------------------


class TestEpicBoon:
    def test_dummy_epic_boon_is_a_harmless_placeholder(self, make_character):
        # No real Epic Boon (ability score increase to a cap of 30, etc.) is
        # implemented anywhere in this codebase - EpicBoon.py only contains
        # this placeholder. Documented here rather than encoded as a bug;
        # see the test report for the "needs content" note.
        character = make_character(strength=20)
        boon = EpicBoon.DummyEpicBoon()
        boon.apply(character)
        assert character.get_ability_score(STR) == 20
        assert boon.name == "Epic Boon"
