import Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardLevel1,
    WizardLevel2,
    WizardLevel3,
    WizardLevel4,
)
from CharacterConfigs.SubClasses.WizardBladesinger import (
    WizardBladesingerLevel3,
    WizardBladeSingerNonGenericStarterClassArgs,
)
from Definitions import Ability, Skill
from Features import Backgrounds, GeneralFeats, OriginFeats, Weapons
from SpeciesConfigs import Elf
from Spells import Definitions as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=WizardBladeSingerNonGenericStarterClassArgs(
            skills=WizardSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.HISTORY: True,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: False,
                    Skill.MEDICINE: False,
                    Skill.NATURE: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=13,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 1),
                (Ability.DEXTERITY, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ACROBATICS,
                Skill.STEALTH,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[
            Weapons.Longsword(player_is_proficient=True, ability=Ability.INTELLIGENCE),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevel1(
                    cantrip_1=SpellDefinitions.WizardLevel0Spells.TRUE_STRIKE,
                    cantrip_2=SpellDefinitions.WizardLevel0Spells.MAGE_HAND,
                    cantrip_3=SpellDefinitions.WizardLevel0Spells.PRESTIDIGITATION,
                    spell_1=SpellDefinitions.WizardLevel1Spells.MAGE_ARMOR,
                    spell_2=SpellDefinitions.WizardLevel1Spells.SHIELD,
                    spell_3=SpellDefinitions.WizardLevel1Spells.MAGIC_MISSILE,
                    spell_4=SpellDefinitions.WizardLevel1Spells.SLEEP,
                ),
                2: WizardLevel2(
                    skill_to_expertise_in=Skill.ARCANA,
                    spell=SpellDefinitions.WizardLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                ),
                3: WizardLevel3(
                    spell=SpellDefinitions.WizardLevel2Spells.MIRROR_IMAGE,
                ),
                4: WizardLevel4(
                    general_feat=GeneralFeats.DualWielder(
                        character_level=4, ability=Ability.DEXTERITY
                    ),
                    cantrip=SpellDefinitions.WizardLevel0Spells.TOLL_THE_DEAD,
                    spell=SpellDefinitions.WizardLevel2Spells.ROPE_TRICK,
                ),
            },
            subclass_features_by_level={
                3: WizardBladesingerLevel3(),
            },
        ),
    )


class OptimizedWizardBladesingerCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Wizard Bladesinger",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
