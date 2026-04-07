import Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import FighterLevel1
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardLevel1,
    WizardLevel2,
    WizardLevel3,
    WizardLevel4,
)
from CharacterConfigs.SubClasses.FighterBattleMaster import (
    FighterBattleMasterNonGenericStarterClassArgs,
)
from CharacterConfigs.SubClasses.WizardBladesinger import (
    WizardBladesingerLevel3,
    WizardBladesingerMulticlassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, FightingStyles, GeneralFeats, OriginFeats, Weapons
from SpeciesConfigs import Elf
from Spells import Definitions as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterBattleMasterNonGenericStarterClassArgs(
            skills=FighterSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: False,
                    Skill.HISTORY: True,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERCEPTION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=1,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=15,
            wisdom=10,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.ARCANA,
                Skill.STEALTH,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.Longsword(
                player_is_proficient=True,
                player_has_mastery=True,
                ability=Ability.INTELLIGENCE,
            ),
            Weapons.Shortsword(
                player_is_proficient=True,
                player_has_mastery=True,
                ability=Ability.INTELLIGENCE,
            ),
            Weapons.Scimitar(
                player_is_proficient=True,
                player_has_mastery=True,
                ability=Ability.INTELLIGENCE,
            ),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    weapon_mastery_3=Weapons.Shortsword(),
                    fighting_style=FightingStyles.TwoWeaponFighting(),
                ),
            },
            subclass_features_by_level={},
        ),
    )


def get_multiclass_builder():
    return WizardBladesingerMulticlassBuilder(
        wizard_level=3,
        wizard_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevel1(
                    cantrip_1=SpellDefinitions.WizardLevel0Spells.MINOR_ILLUSION,
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


class MutliclassTestCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Multiclass Test",
            starter_class_builder=get_starter_class_builder(),
            multiclass_builders=[get_multiclass_builder()],
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
