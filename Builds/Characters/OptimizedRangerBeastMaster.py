from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
    RangerLevel4,
    RangerLevel5,
    RangerLevel6,
    RangerLevel7,
    RangerLevel8,
    RangerLevel9,
    RangerLevel10,
    RangerLevel11,
    RangerLevel12,
    RangerLevel13,
    RangerLevel14,
    RangerLevel15,
    RangerLevel16,
    RangerLevel17,
    RangerLevel18,
    RangerLevel19,
    RangerLevel20,
)
from CharacterConfigs.SubClasses.RangerBeastMaster import (
    RangerBeastMasterLevel3,
    RangerBeastMasterLevel7,
    RangerBeastMasterLevel11,
    RangerBeastMasterLevel15,
    RangerBeastMasterCustomStarterClassArgs,
)
from Definitions import Ability, DamageType, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Features.ClassFeatures.PrimalCompanions import CompanionType
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Gnome
from Spells.Definitions import (
    RangerLevel1Spells,
    RangerLevel2Spells,
    RangerLevel3Spells,
    RangerLevel4Spells,
    RangerLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerBeastMasterCustomStarterClassArgs(
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
        base_class_level=20,
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
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    spell_1=RangerLevel1Spells.CURE_WOUNDS,
                    spell_2=RangerLevel1Spells.ENSNARING_STRIKE,
                ),
                2: RangerLevel2(
                    skill=Skill.PERCEPTION,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.ANIMAL_FRIENDSHIP,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.GOODBERRY,
                ),
                4: RangerLevel4(
                    general_feat=GeneralFeats.Sharpshooter(
                        character_level=4,
                        ability=Ability.DEXTERITY,
                    ),
                    spell=RangerLevel1Spells.ENTANGLE,
                ),
                5: RangerLevel5(
                    spell=RangerLevel2Spells.BARKSKIN,
                ),
                6: RangerLevel6(),
                7: RangerLevel7(
                    spell=RangerLevel2Spells.LESSER_RESTORATION,
                ),
                8: RangerLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                9: RangerLevel9(
                    skill_1=Skill.ATHLETICS,
                    skill_2=Skill.INVESTIGATION,
                    spell=RangerLevel3Spells.CONJURE_ANIMALS,
                ),
                10: RangerLevel10(),
                11: RangerLevel11(
                    spell=RangerLevel3Spells.DISPEL_MAGIC,
                ),
                12: RangerLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                13: RangerLevel13(
                    spell=RangerLevel4Spells.CONJURE_WOODLAND_BEINGS,
                ),
                14: RangerLevel14(),
                15: RangerLevel15(
                    spell=RangerLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                16: RangerLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                17: RangerLevel17(
                    spell_1=RangerLevel5Spells.SWIFT_QUIVER,
                    spell_2=RangerLevel5Spells.CONJURE_VOLLEY,
                ),
                18: RangerLevel18(),
                19: RangerLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=RangerLevel5Spells.GREATER_RESTORATION,
                ),
                20: RangerLevel20(),
            },
            subclass_features_by_level={
                3: RangerBeastMasterLevel3(
                    companion_type=CompanionType.BEAST_OF_THE_LAND,
                    damage_type=DamageType.SLASHING,
                ),
                7: RangerBeastMasterLevel7(),
                11: RangerBeastMasterLevel11(),
                15: RangerBeastMasterLevel15(),
            },
        ),
        replace_spells={},
    )


class OptimizedRangerBeastMasterCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Ranger Beast Master",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.RockGnomeSpeciesBuilder(),
        )
