"""
Build for Thomas, a level 3 College of Valor Bard.

Based on Clover's build (Y2024_Bard_Valor_Clover) with the species changed
from Human to Khoravar (the 2024 Eberron half-elf). Ability scores,
background and Skilled origin feat are unchanged; spells and armor/weapons
(Breastplate + Shield, Shortsword + Scimitar, Heavy Crossbow) were picked
for Thomas.

Species changes vs. Clover:
- Human's Skillful (Stealth) becomes Khoravar's Skill Versatility (Stealth).
- Human's bonus origin feat (Magic Initiate: Wizard) is dropped, since
  Khoravar has no bonus feat. Fey Gift (Friends cantrip, Charisma) is gained.
"""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.SubClasses2024.BardValor import (
    BardValorCustomStarterClassArgs,
    BardValorLevel3,
)
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Items import Armor, Items, Weapons
from CharacterContent.Species import Khoravar
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
)
from CharacterContent.ToolProficiencies.Proficiencies import Lute
from Core.Definitions import Ability, CreatureSize, Skill
from Model.AbilityScores import PointBuyAbilityScores

# Tactics:
# - Prioritize control and support spells over weapon attacks when they can swing the encounter.
# - Use Faerie Fire against groups to give the party advantage on attacks.
# - Use Dissonant Whispers to damage and force an enemy to flee, potentially triggering allies' opportunity attacks.
# - Use Tasha's Hideous Laughter or Suggestion to take a single dangerous enemy out of the fight.
# - Cast Invisibility to scout ahead or get himself or an ally out of trouble.
# - Use Healing Word to revive fallen allies without sacrificing your action.
# - When no important spell is needed, attack with your shortsword and True Strike.
# - Stay at medium range when possible


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BardValorCustomStarterClassArgs(
            skills=[
                Skill.NATURE,
                Skill.PERFORMANCE,
                Skill.PERSUASION,
            ],
        ),
        base_class_level=3,
        abilities=PointBuyAbilityScores(
            strength=8,
            dexterity=14,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=15,
        ),
        # Background ability bonus/skills/tool: see module docstring - not
        # mechanically specified in chat, kept/adapted from the prior version.
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 1),
                (Ability.DEXTERITY, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.ANIMAL_HANDLING,
            ]
        ),
        add_default_equipment=False,
        # Skilled: proficiency in 3 skills of choice.
        origin_feat=OriginFeats.Skilled(
            skills=[
                Skill.SLEIGHT_OF_HAND,
                Skill.INVESTIGATION,
                Skill.ACROBATICS,
            ]
        ),
        # No Starting Equipment: all his gear is issued by the Kingdom Saving
        # Agency instead (see __init__), so none of it is paid for out of his
        # starting gold.
        armor=[],
        weapons=[],
        tool_proficiencies=[
            Lute(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.VICIOUS_MOCKERY,
                    cantrip_2=BardLevel0Spells.TRUE_STRIKE,
                    spell_1=BardLevel1Spells.HEALING_WORD,
                    spell_2=BardLevel1Spells.DISSONANT_WHISPERS,
                    spell_3=BardLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                    spell_4=BardLevel1Spells.FAERIE_FIRE,
                ),
                2: BardLevel2(
                    # Only 1st-level slots at Bard 2, so Sleep is prepared
                    # here and swapped for Invisibility at level 3 (replace_spells).
                    spell=BardLevel1Spells.SLEEP,
                    skill_expertise_1=Skill.PERSUASION,
                    skill_expertise_2=Skill.PERFORMANCE,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.SUGGESTION,
                ),
            },
            subclass_features_by_level={
                3: BardValorLevel3(),
            },
        ),
        replace_spells={
            BardLevel1Spells.SLEEP: BardLevel2Spells.INVISIBILITY,
        },
    )


class Y2024BardValorThomasCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Thomas",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Khoravar.KhoravarSpeciesBuilder(
                size=CreatureSize.MEDIUM,
                skill_versatility=Skill.STEALTH,
                spell_casting_ability=Ability.CHARISMA,
            ),
        )
        # Kingdom Saving Agency mission issue (the agency that recruited the
        # party): Thomas is the party's negotiator. Issued, not bought, so
        # none of it comes out of his starting gold.
        #
        # Breastplate: the best medium armor without Stealth disadvantage
        # (keeps Skill Versatility's Stealth worth having), and doesn't
        # duplicate Dessie's Scale Mail. AC 14 + Dex (max +2) + Shield = 18.
        # Two light finesse weapons off his +3 Dex: Shortsword (Vex) + Shield
        # when he needs AC, or drop the shield and dual-wield with the
        # Scimitar (Nick) for a bonus-action attack. Heavy Crossbow requested
        # by the player: Martial (covered by Valor), and his 16 Dex clears
        # the Heavy property's Dex 13 requirement.
        #
        # Only gear that can matter on the adventure; tools and light are
        # left to Dessie, healing and maps to Maggie, climbing gear to Hanna.
        # Fine clothes and perfume (advantage on Persuasion vs. Indifferent
        # creatures) get him through doors the others can't; ball bearings
        # are a Sleight of Hand trick for covering a retreat. Two Potions of
        # Healing, and a bigger purse than the others' travel money for
        # bribes and buying information.
        self.add_adventuring_gear(
            "Kingdom Saving Agency",
            armor=[
                Armor.BreastplateArmor(),
                Armor.ShieldArmor(),
            ],
            weapons=[
                Weapons.Shortsword(),
                Weapons.Scimitar(),
                Weapons.HeavyCrossbow(),
            ],
            items=[
                (Items.Lute(), 1),  # spellcasting focus
                (Items.Quiver(), 1),  # ammunition isn't tracked in this campaign
                (Items.FineClothes(), 1),
                (Items.Perfume(), 2),
                (Items.BallBearings(), 1),
                (Items.PotionOfHealing(), 2),
            ],
            gold=25,  # travel expenses + bribe purse
        )
