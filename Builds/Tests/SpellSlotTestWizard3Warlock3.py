from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockLevel1,
    WarlockLevel2,
    WarlockLevel3,
)
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardLevel1,
    WizardLevel2,
    WizardLevel3,
)
from CharacterConfigs.SubClasses2024.WarlockArchfey import (
    ArchfeyWarlockLevel3,
    ArchfeyWarlockMulticlassBuilder,
)
from CharacterConfigs.SubClasses2024.WizardBladesinger import (
    WizardBladeSingerCustomStarterClassArgs,
    WizardBladesingerLevel3,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, OriginFeats
from Features.Equipment import Weapons
from Invocations.Definitions import InvocationsLevel0, InvocationsLevel2
from SpeciesConfigs import Human
from Spells import SpellLists as SpellDefs
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


# Wizard 3 / Warlock 3 multiclass — two separate spell pools.
# Expected spell slots:    {1: 4, 2: 2}   (Wizard 3 full caster → level 3)
# Expected pact magic:     {2: 2}          (Warlock 3 → level 3 warlock table)
#
# Cantrips and spells are chosen to avoid any name collisions between the two classes.
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
        base_class_level=3,
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
                    # Safe cantrips: not in WarlockLevel0Spells
                    cantrip_1=SpellDefs.WizardLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefs.WizardLevel0Spells.SHOCKING_GRASP,
                    cantrip_3=SpellDefs.WizardLevel0Spells.RAY_OF_FROST,
                    # Safe spells: not in WarlockLevel1Spells, not added by Archfey subclass
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
                    spell=SpellDefs.WizardLevel2Spells.BLUR,
                ),
            },
            subclass_features_by_level={
                3: WizardBladesingerLevel3(),
            },
        ),
    )


def get_multiclass_builder():
    return ArchfeyWarlockMulticlassBuilder(
        warlock_level=3,
        warlock_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WarlockLevel1(
                    # Safe cantrips: not used by Wizard above
                    cantrip_1=SpellDefs.WarlockLevel0Spells.ELDRITCH_BLAST,
                    cantrip_2=SpellDefs.WarlockLevel0Spells.CHILL_TOUCH,
                    # Safe spells: not in WizardLevel1Spells
                    spell_1=SpellDefs.WarlockLevel1Spells.HEX,
                    spell_2=SpellDefs.WarlockLevel1Spells.ARMOR_OF_AGATHYS,
                    eldritch_invocation=InvocationsLevel0.ELDRITCH_MIND,
                ),
                2: WarlockLevel2(
                    spell=SpellDefs.WarlockLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                    eldritch_invocation_1=InvocationsLevel2.AGONIZING_BLAST,
                    eldritch_invocation_2=InvocationsLevel2.REPELLING_BLAST,
                ),
                3: WarlockLevel3(
                    # Safe: not in Wizard spells; MISTY_STEP is added by Archfey subclass
                    spell=SpellDefs.WarlockLevel2Spells.SPIDER_CLIMB,
                ),
            },
            subclass_features_by_level={
                3: ArchfeyWarlockLevel3(),
            },
        ),
    )


class SpellSlotTestWizard3Warlock3CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Spell Slot Test Wizard 3 Warlock 3",
            starter_class_builder=get_starter_class_builder(),
            multiclass_builders=[get_multiclass_builder()],
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[Skill.INVESTIGATION, Skill.NATURE, Skill.SURVIVAL]
                ),
            ),
        )
