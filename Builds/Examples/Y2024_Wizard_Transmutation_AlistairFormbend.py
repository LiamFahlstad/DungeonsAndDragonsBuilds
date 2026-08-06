"""Example build: Wizard School of Transmutation. Built to character level 20 to exercise every subclass feature."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardLevel1,
    WizardLevel2,
    WizardLevel3,
    WizardLevel4,
    WizardLevel5,
    WizardLevel6,
    WizardLevel7,
    WizardLevel8,
    WizardLevel9,
    WizardLevel10,
    WizardLevel11,
    WizardLevel12,
    WizardLevel13,
    WizardLevel14,
    WizardLevel15,
    WizardLevel16,
    WizardLevel17,
    WizardLevel18,
    WizardLevel19,
    WizardLevel20,
)
from CharacterContent.Classes.SubClasses2024.WizardTransmuter import (
    WizardTransmuterCustomStarterClassArgs,
    WizardTransmuterLevel3,
    WizardTransmuterLevel5,
    WizardTransmuterLevel6,
    WizardTransmuterLevel7,
    WizardTransmuterLevel9,
    WizardTransmuterLevel10,
    WizardTransmuterLevel11,
    WizardTransmuterLevel13,
    WizardTransmuterLevel14,
    WizardTransmuterLevel15,
    WizardTransmuterLevel17,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from CharacterContent.Items import Weapons
from CharacterContent.Species import Gnome
from CharacterContent.Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=WizardTransmuterCustomStarterClassArgs(
            skills=WizardSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.INVESTIGATION: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.MEDICINE: False,
                    Skill.NATURE: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=15,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERCEPTION,
                Skill.SLEIGHT_OF_HAND,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.Quarterstaff(ability=Ability.INTELLIGENCE),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevel1(
                    cantrip_1=SpellDefinitions.WizardLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.WizardLevel0Spells.MAGE_HAND,
                    cantrip_3=SpellDefinitions.WizardLevel0Spells.PRESTIDIGITATION,
                    spell_1=SpellDefinitions.WizardLevel1Spells.MAGE_ARMOR,
                    spell_2=SpellDefinitions.WizardLevel1Spells.SHIELD,
                    spell_3=SpellDefinitions.WizardLevel1Spells.MAGIC_MISSILE,
                    spell_4=SpellDefinitions.WizardLevel1Spells.FEATHER_FALL,
                ),
                2: WizardLevel2(
                    skill_expertise=Skill.ARCANA,
                    spell=SpellDefinitions.WizardLevel1Spells.FIND_FAMILIAR,
                ),
                3: WizardLevel3(
                    spell=SpellDefinitions.WizardLevel2Spells.MIRROR_IMAGE,
                ),
                4: WizardLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.INTELLIGENCE, 2)]
                    ),
                    cantrip=SpellDefinitions.WizardLevel0Spells.RAY_OF_FROST,
                    spell=SpellDefinitions.WizardLevel2Spells.MISTY_STEP,
                ),
                5: WizardLevel5(
                    spell_1=SpellDefinitions.WizardLevel3Spells.COUNTERSPELL,
                    spell_2=SpellDefinitions.WizardLevel3Spells.HASTE,
                ),
                6: WizardLevel6(
                    spell=SpellDefinitions.WizardLevel3Spells.DISPEL_MAGIC,
                ),
                7: WizardLevel7(
                    spell=SpellDefinitions.WizardLevel4Spells.DIMENSION_DOOR,
                ),
                8: WizardLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CONSTITUTION, 2)]
                    ),
                    spell=SpellDefinitions.WizardLevel4Spells.BANISHMENT,
                ),
                9: WizardLevel9(
                    spell_1=SpellDefinitions.WizardLevel5Spells.WALL_OF_FORCE,
                    spell_2=SpellDefinitions.WizardLevel5Spells.CLOUDKILL,
                ),
                10: WizardLevel10(
                    cantrip=SpellDefinitions.WizardLevel0Spells.SHOCKING_GRASP,
                    spell=SpellDefinitions.WizardLevel5Spells.TELEPORTATION_CIRCLE,
                ),
                11: WizardLevel11(
                    spell=SpellDefinitions.WizardLevel6Spells.CHAIN_LIGHTNING,
                ),
                12: WizardLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.INTELLIGENCE, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                13: WizardLevel13(
                    spell=SpellDefinitions.WizardLevel7Spells.TELEPORT,
                ),
                14: WizardLevel14(
                    spell=SpellDefinitions.WizardLevel7Spells.FORCECAGE,
                ),
                15: WizardLevel15(
                    spell=SpellDefinitions.WizardLevel8Spells.DOMINATE_MONSTER,
                ),
                16: WizardLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.INTELLIGENCE, 2)]
                    ),
                    spell_1=SpellDefinitions.WizardLevel8Spells.ANTIMAGIC_FIELD,
                    spell_2=SpellDefinitions.WizardLevel8Spells.MIND_BLANK,
                ),
                17: WizardLevel17(
                    spell=SpellDefinitions.WizardLevel9Spells.METEOR_SWARM,
                ),
                18: WizardLevel18(
                    spell=SpellDefinitions.WizardLevel9Spells.FORESIGHT,
                ),
                19: WizardLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=SpellDefinitions.WizardLevel9Spells.WISH,
                ),
                20: WizardLevel20(
                    spell=SpellDefinitions.WizardLevel9Spells.TIME_STOP,
                ),
            },
            subclass_features_by_level={
                3: WizardTransmuterLevel3(
                    spell_1=SpellDefinitions.TransmutationLevel1Spells.EXPEDITIOUS_RETREAT,
                    spell_2=SpellDefinitions.TransmutationLevel2Spells.ENLARGE_REDUCE,
                ),
                5: WizardTransmuterLevel5(
                    spell=SpellDefinitions.TransmutationLevel3Spells.FLY,
                ),
                6: WizardTransmuterLevel6(),
                7: WizardTransmuterLevel7(
                    spell=SpellDefinitions.TransmutationLevel4Spells.STONESKIN,
                ),
                9: WizardTransmuterLevel9(
                    spell=SpellDefinitions.TransmutationLevel5Spells.TELEKINESIS,
                ),
                10: WizardTransmuterLevel10(),
                11: WizardTransmuterLevel11(
                    spell=SpellDefinitions.TransmutationLevel6Spells.TENSERS_TRANSFORMATION,
                ),
                13: WizardTransmuterLevel13(
                    spell=SpellDefinitions.TransmutationLevel7Spells.REGENERATE,
                ),
                14: WizardTransmuterLevel14(),
                15: WizardTransmuterLevel15(
                    spell=SpellDefinitions.TransmutationLevel8Spells.ANIMAL_SHAPES,
                ),
                17: WizardTransmuterLevel17(
                    spell=SpellDefinitions.TransmutationLevel8Spells.EARTHQUAKE,
                ),
            },
        ),
    )


class Y2024WizardTransmutationAlistairFormbendCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Alistair Formbend",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.RockGnomeSpeciesBuilder(),
        )
