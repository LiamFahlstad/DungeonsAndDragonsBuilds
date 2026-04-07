from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
    RangerLevel4,
    RangerLevel5,
)
from CharacterConfigs.SubClasses.RangerBeastMaster import (
    RangerBeastMasterLevel3,
    RangerBeastMasterNonGenericStarterClassArgs,
)
from Definitions import Ability, Skill
from Features import Backgrounds, FightingStyles, GeneralFeats, OriginFeats, Weapons
from SpeciesConfigs import Gnome
from Spells.Definitions import RangerLevel1Spells, RangerLevel2Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerBeastMasterNonGenericStarterClassArgs(
            skills=RangerSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: True,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: True,
                    Skill.STEALTH: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=10,
            dexterity=15,
            constitution=12,
            intelligence=14,
            wisdom=13,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.WISDOM, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SLEIGHT_OF_HAND,
                Skill.ACROBATICS,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Crater(artisans_tools=[]),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    spell_1=RangerLevel1Spells.CURE_WOUNDS,
                    spell_2=RangerLevel1Spells.FOG_CLOUD,
                ),
                2: RangerLevel2(
                    skill=Skill.ACROBATICS,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.JUMP,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.ALARM,
                ),
                4: RangerLevel4(
                    spell=RangerLevel1Spells.LONGSTRIDER,
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 1),
                            (Ability.INTELLIGENCE, 1),
                        ]
                    ),
                ),
                5: RangerLevel5(
                    spell=RangerLevel2Spells.PASS_WITHOUT_TRACE,
                ),
            },
            subclass_features_by_level={
                3: RangerBeastMasterLevel3(),
            },
        ),
        replace_spells={
            RangerLevel1Spells.ALARM: RangerLevel2Spells.SILENCE,
        },
    )


# if __name__ == "__main__":

#     BeastMasterBeastOfTheSky(
#         wisdom_modifier=character_sheet_data.get_ability_modifier(Ability.WISDOM),
#         base_class_level=character_sheet_data.get_level_for_class(CharacterClass.RANGER),
#         proficiency_bonus=character_sheet_data.character_level // 4 + 2,
#         spell_attack_modifier=character_sheet_data.calculate_attack_bonus_for_ability(
#             Ability.WISDOM
#         ),
#     ).write_to_file(output_path, mode="a")


class OptimizedRangerBeastMasterCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Ranger Beast Master",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.RockGnomeSpeciesBuilder(),
        )
