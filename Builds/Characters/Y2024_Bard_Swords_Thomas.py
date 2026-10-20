"""Build for Thomas, a level 3 College of Swords Bard (Human, Entertainer).

Adapted from a 2014 Variant Human build to the 2024 engine:
- Variant Human -> Human. War Caster is a level 4+ General feat in 2024, so
  Human's bonus origin feat is Lucky instead (advantage on a failed
  concentration save is the closest stand-in).
- Two shortswords -> two scimitars. The 2024 Bard only has Simple weapon
  proficiency and Swords grants the scimitar; damage is identical (1d6, Light,
  Finesse), and either scimitar doubles as a spellcasting focus.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.SubClasses2014.BardSwords import (
    BardSwordsCustomStarterClassArgs,
    BardSwordsLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
)
from CharacterContent.ToolProficiencies.Proficiencies import Lute
from Core.Definitions import Ability, Skill
from Model.AbilityScores import PointBuyAbilityScores

# Tactics:
# - Opening turn: Faerie Fire on a group, or Heat Metal on an armored foe.
# - Melee turns: attack with one scimitar, then Bonus Action off-hand attack.
# - Spend Bardic Inspiration on Defensive Flourish when expecting attacks.
# - Dissonant Whispers or Tasha's Hideous Laughter when disabling beats damage.
# - Keep the Bonus Action free for Healing Word when an ally drops.


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BardSwordsCustomStarterClassArgs(
            skills=[
                Skill.PERSUASION,
                Skill.DECEPTION,
                Skill.INSIGHT,
            ],
        ),
        base_class_level=3,
        # Final: STR 8 / DEX 16 / CON 14 / INT 8 / WIS 12 / CHA 14
        # after the Entertainer bonuses (+2 CHA, +1 DEX).
        abilities=PointBuyAbilityScores(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=14,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        # Entertainer: Acrobatics + Performance.
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ACROBATICS,
                Skill.PERFORMANCE,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Musician(),
        armor=[Armor.ScaleMailArmor()],
        weapons=[
            Weapons.Scimitar(player_has_mastery=False),
            Weapons.Scimitar(player_has_mastery=False),
        ],
        tool_proficiencies=[Lute()],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.VICIOUS_MOCKERY,
                    cantrip_2=BardLevel0Spells.MINOR_ILLUSION,
                    spell_1=BardLevel1Spells.DISSONANT_WHISPERS,
                    spell_2=BardLevel1Spells.HEALING_WORD,
                    spell_3=BardLevel1Spells.FAERIE_FIRE,
                    spell_4=BardLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                ),
                2: BardLevel2(
                    # Only 1st-level slots at Bard 2: Sleep is a placeholder
                    # swapped for Heat Metal at level 3 (replace_spells).
                    spell=BardLevel1Spells.SLEEP,
                    skill_expertise_1=Skill.PERSUASION,
                    skill_expertise_2=Skill.PERCEPTION,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.SHATTER,
                ),
            },
            subclass_features_by_level={
                3: BardSwordsLevel3(
                    fighting_style=FightingStyles.TwoWeaponFighting(),
                ),
            },
        ),
        replace_spells={
            BardLevel1Spells.SLEEP: BardLevel2Spells.HEAT_METAL,
        },
    )


class Y2024BardSwordsThomasCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Thomas",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Lucky(),
            ),
        )
