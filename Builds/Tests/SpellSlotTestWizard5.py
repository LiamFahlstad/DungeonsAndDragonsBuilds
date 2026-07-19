from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardLevel1,
    WizardLevel2,
    WizardLevel3,
    WizardLevel4,
    WizardLevel5,
)
from CharacterConfigs.SubClasses2024.WizardBladesinger import (
    WizardBladeSingerCustomStarterClassArgs,
    WizardBladesingerLevel3,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Weapons
from SpeciesConfigs import Human
from Spells import SpellLists as SpellDefs
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


# Wizard 5 (full caster).
# Expected spell slots: {1: 4, 2: 3, 3: 2}
def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=WizardBladeSingerCustomStarterClassArgs(
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
        base_class_level=5,
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=15,
            wisdom=10,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [(Ability.INTELLIGENCE, 2), (Ability.DEXTERITY, 1)]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [Skill.ACROBATICS, Skill.STEALTH]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[
            Weapons.Longsword(player_is_proficient=True, ability=Ability.INTELLIGENCE)
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevel1(
                    cantrip_1=SpellDefs.WizardLevel0Spells.TRUE_STRIKE,
                    cantrip_2=SpellDefs.WizardLevel0Spells.MAGE_HAND,
                    cantrip_3=SpellDefs.WizardLevel0Spells.PRESTIDIGITATION,
                    spell_1=SpellDefs.WizardLevel1Spells.MAGE_ARMOR,
                    spell_2=SpellDefs.WizardLevel1Spells.SHIELD,
                    spell_3=SpellDefs.WizardLevel1Spells.MAGIC_MISSILE,
                    spell_4=SpellDefs.WizardLevel1Spells.SLEEP,
                ),
                2: WizardLevel2(
                    skill_to_expertise_in=Skill.ARCANA,
                    spell=SpellDefs.WizardLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                ),
                3: WizardLevel3(
                    spell=SpellDefs.WizardLevel2Spells.MIRROR_IMAGE,
                ),
                4: WizardLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.INTELLIGENCE, 2)]
                    ),
                    cantrip=SpellDefs.WizardLevel0Spells.TOLL_THE_DEAD,
                    spell=SpellDefs.WizardLevel2Spells.ROPE_TRICK,
                ),
                5: WizardLevel5(
                    spell_1=SpellDefs.WizardLevel3Spells.FIREBALL,
                    spell_2=SpellDefs.WizardLevel3Spells.COUNTERSPELL,
                ),
            },
            subclass_features_by_level={
                3: WizardBladesingerLevel3(),
            },
        ),
    )


class SpellSlotTestWizard5CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Spell Slot Test Wizard 5",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[Skill.INVESTIGATION, Skill.NATURE, Skill.SURVIVAL]
                ),
            ),
        )
