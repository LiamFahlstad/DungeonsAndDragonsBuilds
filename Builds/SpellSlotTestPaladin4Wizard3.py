from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
    PaladinLevel4,
)
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardLevel1,
    WizardLevel2,
    WizardLevel3,
)
from CharacterConfigs.SubClasses.PaladinGlory import (
    PaladinGloryLevel3,
    PaladinGloryCustomStarterClassArgs,
)
from CharacterConfigs.SubClasses.WizardBladesinger import (
    WizardBladesingerLevel3,
    WizardBladesingerMulticlassBuilder,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Human
from Spells import Definitions as SpellDefs
from Spells.Definitions import PaladinLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


# Paladin 4 / Wizard 3 multiclass (the PHB example scenario).
# Expected spell slots: {1: 4, 2: 3, 3: 2}
#   effective caster level = floor(4/2) + 3 = 2 + 3 = 5 → full caster level 5
def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinGloryCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: True,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=4,
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=10,
            constitution=14,
            intelligence=15,
            wisdom=8,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [(Ability.INTELLIGENCE, 2), (Ability.CHARISMA, 1)]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [Skill.ARCANA, Skill.HISTORY]
        ),
        # No armor so Wizard Bladesinger subclass check passes.
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[Weapons.Longsword(player_is_proficient=True)],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Javelin(),
                    spell_1=PaladinLevel1Spells.DETECT_POISON_AND_DISEASE,
                    spell_2=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.Defense(),
                    spell=PaladinLevel1Spells.SHIELD_OF_FAITH,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.BLESS,
                ),
                4: PaladinLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]
                    ),
                    spell=PaladinLevel1Spells.CURE_WOUNDS,
                ),
            },
            subclass_features_by_level={
                3: PaladinGloryLevel3(),
            },
        ),
    )


def get_multiclass_builder():
    return WizardBladesingerMulticlassBuilder(
        wizard_level=3,
        wizard_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevel1(
                    cantrip_1=SpellDefs.WizardLevel0Spells.MAGE_HAND,
                    cantrip_2=SpellDefs.WizardLevel0Spells.PRESTIDIGITATION,
                    cantrip_3=SpellDefs.WizardLevel0Spells.TRUE_STRIKE,
                    spell_1=SpellDefs.WizardLevel1Spells.MAGE_ARMOR,
                    spell_2=SpellDefs.WizardLevel1Spells.SHIELD,
                    spell_3=SpellDefs.WizardLevel1Spells.MAGIC_MISSILE,
                    spell_4=SpellDefs.WizardLevel1Spells.ALARM,
                ),
                2: WizardLevel2(
                    skill_to_expertise_in=Skill.ARCANA,
                    spell=SpellDefs.WizardLevel1Spells.BURNING_HANDS,
                ),
                3: WizardLevel3(
                    spell=SpellDefs.WizardLevel2Spells.MIRROR_IMAGE,
                ),
            },
            subclass_features_by_level={
                3: WizardBladesingerLevel3(),
            },
        ),
    )


class SpellSlotTestPaladin4Wizard3CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Spell Slot Test Paladin 4 Wizard 3",
            starter_class_builder=get_starter_class_builder(),
            multiclass_builders=[get_multiclass_builder()],
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[Skill.INVESTIGATION, Skill.NATURE, Skill.SURVIVAL]
                ),
            ),
        )
