"""Example build: Bard College of Swords (2014 rules). Demonstrates the subclass up through level 14."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
    BardLevel4,
    BardLevel5,
    BardLevel6,
    BardLevel7,
    BardLevel8,
    BardLevel9,
    BardLevel10,
    BardLevel11,
    BardLevel12,
    BardLevel13,
    BardLevel14,
)
from CharacterContent.Classes.SubClasses2014.BardSwords import (
    BardSwordsCustomStarterClassArgs,
    BardSwordsLevel3,
    BardSwordsLevel6,
    BardSwordsLevel14,
)
from CharacterContent.Features.CombatFeatures import FightingStyles
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Features.CharacterFeats import OriginFeats as SpeciesOriginFeats
from CharacterContent.Items import Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    BardLevel4Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from CharacterContent.ToolProficiencies.Proficiencies import Bagpipes, Drum, Horn
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BardSwordsCustomStarterClassArgs(
            skills=BardSkillsStatBlock(
                proficiencies={
                    Skill.PERFORMANCE: True,
                    Skill.ACROBATICS: True,
                    Skill.PERSUASION: True,
                }
            ),
        ),
        base_class_level=14,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=10,
            dexterity=15,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=13,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Musician(),
        armor=[],
        weapons=[
            Weapons.Rapier(player_has_mastery=True),
        ],
        tool_proficiencies=[
            Drum(),
            Horn(),
            Bagpipes(),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.VICIOUS_MOCKERY,
                    cantrip_2=BardLevel0Spells.MAGE_HAND,
                    spell_1=BardLevel1Spells.HEALING_WORD,
                    spell_2=BardLevel1Spells.FAERIE_FIRE,
                    spell_3=BardLevel1Spells.SLEEP,
                    spell_4=BardLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                ),
                2: BardLevel2(
                    spell=BardLevel1Spells.DISSONANT_WHISPERS,
                    skill_expertise_1=Skill.PERFORMANCE,
                    skill_expertise_2=Skill.PERSUASION,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.AID,
                ),
                4: BardLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                    cantrip=BardLevel0Spells.MINOR_ILLUSION,
                    spell=BardLevel2Spells.ENHANCE_ABILITY,
                ),
                5: BardLevel5(
                    spell_1=BardLevel3Spells.BESTOW_CURSE,
                    spell_2=BardLevel3Spells.FEAR,
                ),
                6: BardLevel6(
                    spell=BardLevel3Spells.DISPEL_MAGIC,
                ),
                7: BardLevel7(
                    spell=BardLevel2Spells.LESSER_RESTORATION,
                ),
                8: BardLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CONSTITUTION, 2)]),
                    spell=BardLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: BardLevel9(
                    spell_1=BardLevel4Spells.CHARM_MONSTER,
                    spell_2=BardLevel4Spells.POLYMORPH,
                    skill_expertise_1=Skill.PERFORMANCE,
                    skill_expertise_2=Skill.PERSUASION,
                ),
                10: BardLevel10(
                    cantrip=BardLevel0Spells.PRESTIDIGITATION,
                    spell=BardLevel4Spells.GREATER_INVISIBILITY,
                ),
                11: BardLevel11(
                    spell=BardLevel4Spells.CONFUSION,
                ),
                12: BardLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 1), (Ability.WISDOM, 1)]),
                ),
                13: BardLevel13(
                    spell=BardLevel4Spells.DIMENSION_DOOR,
                ),
                14: BardLevel14(),
            },
            subclass_features_by_level={
                3: BardSwordsLevel3(fighting_style=FightingStyles.Dueling()),
                6: BardSwordsLevel6(),
                14: BardSwordsLevel14(),
            },
        ),
    )


class Y2014BardSwordsPerrinBladesongCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Perrin Bladesong",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                origin_feat=SpeciesOriginFeats.Tough(),
                skill_proficiency=Skill.INSIGHT,
            ),
        )
