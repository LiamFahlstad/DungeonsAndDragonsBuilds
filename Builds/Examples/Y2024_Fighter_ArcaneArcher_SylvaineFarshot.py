"""Example build: Fighter Arcane Archer. Built to character level 18 to exercise every subclass feature."""

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
    FighterLevel16,
    FighterLevel17,
    FighterLevel18,
)
from CharacterContent.Classes.BaseClasses.ClassBuilder import (
    BaseClassLevelFeatures,
    StarterClassBuilder,
)
from CharacterContent.Classes.SubClasses2024.FighterArcaneArcher import (
    FighterArcaneArcherCustomStarterClassArgs,
    FighterArcaneArcherLevel3,
    FighterArcaneArcherLevel7,
    FighterArcaneArcherLevel10,
    FighterArcaneArcherLevel15,
    FighterArcaneArcherLevel18,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import (
    Backgrounds,
    GeneralFeats,
    OriginFeats,
)
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Features.SubClassFeatures.Fighter import (
    FighterArcaneArcherFeatures,
)
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import TransmutationLevel0Spells
from Model.AbilityScores import StandardArrayAbilityScores


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterArcaneArcherCustomStarterClassArgs(
            skills=[
                Skill.ACROBATICS,
                Skill.PERCEPTION,
            ],
        ),
        base_class_level=18,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilityScores(
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
                Skill.SLEIGHT_OF_HAND,
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
                    ),
                ),
                5: FighterLevel5(),
                6: FighterLevel6(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                ),
                7: FighterLevel7(),
                8: FighterLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.INTELLIGENCE, 2),
                        ]
                    ),
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
                        ]
                    ),
                ),
                13: FighterLevel13(),
                14: FighterLevel14(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                15: FighterLevel15(),
                16: FighterLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                    weapon_mastery=Weapons.Handaxe(),
                ),
                17: FighterLevel17(),
                18: FighterLevel18(),
            },
            subclass_features_by_level={
                3: FighterArcaneArcherLevel3(
                    cantrip=TransmutationLevel0Spells.PRESTIDIGITATION,
                    arcane_shot_option_1=FighterArcaneArcherFeatures.BurstingShot(),
                    arcane_shot_option_2=FighterArcaneArcherFeatures.GraspingShot(),
                    # Already proficient in Nature (Skilled), so a Fighter skill instead.
                    skill_2=Skill.INSIGHT,
                ),
                7: FighterArcaneArcherLevel7(
                    arcane_shot_option=FighterArcaneArcherFeatures.SeekingShot(),
                ),
                10: FighterArcaneArcherLevel10(
                    arcane_shot_option=FighterArcaneArcherFeatures.BanishingShot(),
                ),
                15: FighterArcaneArcherLevel15(
                    arcane_shot_option=FighterArcaneArcherFeatures.PiercingShot(),
                ),
                18: FighterArcaneArcherLevel18(
                    arcane_shot_option=FighterArcaneArcherFeatures.ShadowShot(),
                ),
            },
        ),
    )


class Y2024FighterArcaneArcherSylvaineFarshotCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Sylvaine Farshot",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.HISTORY,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.SURVIVAL,
                        Skill.NATURE,
                        Skill.STEALTH,
                    ]
                ),
            ),
        )
