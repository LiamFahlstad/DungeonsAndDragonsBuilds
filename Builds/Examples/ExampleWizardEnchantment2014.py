"""Example build: Wizard School of Enchantment (2014 rules). Demonstrates the subclass through level 14."""

import Core.Definitions as Definitions
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
)
from CharacterContent.Classes.SubClasses2014.WizardEnchantment import (
    WizardEnchantmentLevel3,
    WizardEnchantmentLevel6,
    WizardEnchantmentLevel10,
    WizardEnchantmentLevel14,
    WizardEnchantmentCustomStarterClassArgs,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Species import Gnome
from CharacterContent.Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=WizardEnchantmentCustomStarterClassArgs(
            skills=WizardSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: True,
                    Skill.INVESTIGATION: False,
                    Skill.MEDICINE: False,
                    Skill.NATURE: False,
                    Skill.RELIGION: False,
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
                (Ability.CHARISMA, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERSUASION,
                Skill.DECEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevel1(
                    cantrip_1=SpellDefinitions.WizardLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.WizardLevel0Spells.MAGE_HAND,
                    cantrip_3=SpellDefinitions.WizardLevel0Spells.FRIENDS,
                    spell_1=SpellDefinitions.WizardLevel1Spells.CHARM_PERSON,
                    spell_2=SpellDefinitions.WizardLevel1Spells.SLEEP,
                    spell_3=SpellDefinitions.WizardLevel1Spells.DETECT_MAGIC,
                    spell_4=SpellDefinitions.WizardLevel1Spells.COMPREHEND_LANGUAGES,
                ),
                2: WizardLevel2(
                    skill_expertise=Skill.ARCANA,
                    spell=SpellDefinitions.WizardLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                ),
                3: WizardLevel3(
                    spell=SpellDefinitions.WizardLevel2Spells.HOLD_PERSON,
                ),
                4: WizardLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]),
                    cantrip=SpellDefinitions.WizardLevel0Spells.MIND_SLIVER,
                    spell=SpellDefinitions.WizardLevel2Spells.SUGGESTION,
                ),
                5: WizardLevel5(
                    spell_1=SpellDefinitions.WizardLevel3Spells.HYPNOTIC_PATTERN,
                    spell_2=SpellDefinitions.WizardLevel3Spells.FEAR,
                ),
                6: WizardLevel6(
                    spell=SpellDefinitions.WizardLevel3Spells.SLOW,
                ),
                7: WizardLevel7(
                    spell=SpellDefinitions.WizardLevel4Spells.CHARM_MONSTER,
                ),
                8: WizardLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]),
                    spell=SpellDefinitions.WizardLevel4Spells.CONFUSION,
                ),
                9: WizardLevel9(
                    spell_1=SpellDefinitions.WizardLevel5Spells.DOMINATE_PERSON,
                    spell_2=SpellDefinitions.WizardLevel5Spells.MODIFY_MEMORY,
                ),
                10: WizardLevel10(
                    cantrip=SpellDefinitions.WizardLevel0Spells.MESSAGE,
                    spell=SpellDefinitions.WizardLevel5Spells.SEEMING,
                ),
                11: WizardLevel11(
                    spell=SpellDefinitions.WizardLevel6Spells.MASS_SUGGESTION,
                ),
                12: WizardLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CHARISMA, 2),
                        ]),
                ),
                13: WizardLevel13(
                    spell=SpellDefinitions.WizardLevel7Spells.PROJECT_IMAGE,
                ),
                14: WizardLevel14(
                    spell=SpellDefinitions.WizardLevel7Spells.MIRAGE_ARCANE,
                ),
            },
            subclass_features_by_level={
                3: WizardEnchantmentLevel3(),
                6: WizardEnchantmentLevel6(),
                10: WizardEnchantmentLevel10(),
                14: WizardEnchantmentLevel14(),
            },
        ),
        replace_spells={},
    )


class ExampleWizardEnchantment2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Wizard Enchantment",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.RockGnomeSpeciesBuilder(),
        )
