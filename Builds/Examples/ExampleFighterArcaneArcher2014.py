"""Example build: Fighter Arcane Archer (2014 rules). Demonstrates the subclass up through level 15."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
    FighterLevel5,
    FighterLevel6,
    FighterLevel7,
    FighterLevel8,
    FighterLevel9,
    FighterLevel10,
    FighterLevel11,
    FighterLevel12,
    FighterLevel13,
    FighterLevel14,
    FighterLevel15,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import (
    BaseClassLevelFeatures,
    StarterClassBuilder,
)
from CharacterContent.Classes.SubClasses2014.FighterArcaneArcher import (
    FighterArcaneArcherCustomStarterClassArgs,
    FighterArcaneArcherLevel3,
    FighterArcaneArcherLevel7,
    FighterArcaneArcherLevel15,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Human
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterArcaneArcherCustomStarterClassArgs(
            skills=FighterSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: False,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERCEPTION: True,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=15,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=10,
            dexterity=15,
            constitution=14,
            intelligence=13,
            wisdom=12,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.INTELLIGENCE, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ARCANA,
                Skill.INVESTIGATION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.StuddedLeatherArmor(),
        ],
        weapons=[
            Weapons.Longbow(ability=Ability.DEXTERITY),
            Weapons.Shortsword(),
        ],
        base_class_level_features=BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Shortsword(),
                    weapon_mastery_3=Weapons.Dagger(),
                    fighting_style=FightingStyles.Archery(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Dagger(),
                    general_feat=GeneralFeats.Sharpshooter(
                        character_level=4,
                        ability=Ability.DEXTERITY,
                    )
                ),
                5: FighterLevel5(),
                6: FighterLevel6(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]),
                ),
                7: FighterLevel7(),
                8: FighterLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.INTELLIGENCE, 2),
                        ]),
                ),
                9: FighterLevel9(),
                10: FighterLevel10(
                    weapon_mastery=Weapons.Longbow(),
                ),
                11: FighterLevel11(),
                12: FighterLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]),
                ),
                13: FighterLevel13(),
                14: FighterLevel14(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]),
                ),
                15: FighterLevel15(),
            },
            subclass_features_by_level={
                3: FighterArcaneArcherLevel3(
                    skill=Skill.ARCANA,
                    cantrip="Prestidigitation",
                ),
                7: FighterArcaneArcherLevel7(),
                15: FighterArcaneArcherLevel15(),
            },
        ),
    )


class ExampleFighterArcaneArcher2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Fighter Arcane Archer",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.SURVIVAL,
                        Skill.NATURE,
                        Skill.STEALTH,
                    ]
                ),
            ),
        )
