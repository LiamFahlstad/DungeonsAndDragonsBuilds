"""Example build: Wizard School of Necromancy (2014 rules). Demonstrates the subclass through level 14."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
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
)
from CharacterConfigs.SubClasses2014.WizardNecromancy import (
    NecromancyWizardLevel3,
    NecromancyWizardLevel6,
    NecromancyWizardLevel10,
    NecromancyWizardLevel14,
    WizardNecromancyCustomStarterClassArgs,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from SpeciesConfigs import Elf
from Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=WizardNecromancyCustomStarterClassArgs(
            skills=WizardSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: False,
                    Skill.MEDICINE: False,
                    Skill.NATURE: False,
                    Skill.RELIGION: True,
                }
            ),
        ),
        base_class_level=14,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=15,
            wisdom=10,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.RELIGION,
                Skill.INVESTIGATION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevel1(
                    cantrip_1=SpellDefinitions.WizardLevel0Spells.CHILL_TOUCH,
                    cantrip_2=SpellDefinitions.WizardLevel0Spells.MAGE_HAND,
                    cantrip_3=SpellDefinitions.WizardLevel0Spells.PRESTIDIGITATION,
                    spell_1=SpellDefinitions.WizardLevel1Spells.FALSE_LIFE,
                    spell_2=SpellDefinitions.WizardLevel1Spells.MAGIC_MISSILE,
                    spell_3=SpellDefinitions.WizardLevel1Spells.RAY_OF_SICKNESS,
                    spell_4=SpellDefinitions.WizardLevel1Spells.SHIELD,
                ),
                2: WizardLevel2(
                    skill_to_expertise_in=Skill.ARCANA,
                    spell=SpellDefinitions.WizardLevel1Spells.MAGE_ARMOR,
                ),
                3: WizardLevel3(
                    spell=SpellDefinitions.WizardLevel2Spells.RAY_OF_ENFEEBLEMENT,
                ),
                4: WizardLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]),
                    cantrip=SpellDefinitions.WizardLevel0Spells.TOLL_THE_DEAD,
                    spell=SpellDefinitions.WizardLevel2Spells.BLINDNESS_DEAFNESS,
                ),
                5: WizardLevel5(
                    spell_1=SpellDefinitions.WizardLevel3Spells.BESTOW_CURSE,
                    spell_2=SpellDefinitions.WizardLevel3Spells.VAMPIRIC_TOUCH,
                ),
                6: WizardLevel6(
                    spell=SpellDefinitions.WizardLevel3Spells.FEAR,
                ),
                7: WizardLevel7(
                    spell=SpellDefinitions.WizardLevel4Spells.BLIGHT,
                ),
                8: WizardLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]),
                    spell=SpellDefinitions.WizardLevel4Spells.PHANTASMAL_KILLER,
                ),
                9: WizardLevel9(
                    spell_1=SpellDefinitions.WizardLevel5Spells.DOMINATE_PERSON,
                    spell_2=SpellDefinitions.WizardLevel5Spells.ENERVATION,
                ),
                10: WizardLevel10(
                    cantrip=SpellDefinitions.WizardLevel0Spells.FROSTBITE,
                    spell=SpellDefinitions.WizardLevel5Spells.CLOUDKILL,
                ),
                11: WizardLevel11(
                    spell=SpellDefinitions.WizardLevel6Spells.CIRCLE_OF_DEATH,
                ),
                12: WizardLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CONSTITUTION, 2),
                        ]),
                ),
                13: WizardLevel13(
                    spell=SpellDefinitions.WizardLevel7Spells.FINGER_OF_DEATH,
                ),
                14: WizardLevel14(
                    spell=SpellDefinitions.WizardLevel7Spells.SIMULACRUM,
                ),
            },
            subclass_features_by_level={
                3: NecromancyWizardLevel3(),
                6: NecromancyWizardLevel6(),
                10: NecromancyWizardLevel10(),
                14: NecromancyWizardLevel14(),
            },
        ),
        replace_spells={},
    )


class ExampleWizardNecromancy2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Wizard Necromancy",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.HIGH_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
