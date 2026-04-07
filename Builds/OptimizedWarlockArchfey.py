from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockLevel1,
    WarlockLevel2,
    WarlockLevel3,
    WarlockLevel4,
    WarlockLevel5,
)
from CharacterConfigs.SubClasses.WarlockArchfey import (
    ArchfeyWarlockLevel3,
    ArchfeyWarlockLevel5,
    WarlockArchfeyNonGenericStarterClassArgs,
)
from Definitions import Ability, Skill
from Features import Backgrounds, GeneralFeats, OriginFeats
from Invocations.Definitions import (
    InvocationsLevel0,
    InvocationsLevel2,
    InvocationsLevel5,
)
from SpeciesConfigs import Human
from Spells.Definitions import (
    WarlockLevel0Spells,
    WarlockLevel1Spells,
    WarlockLevel2Spells,
    WarlockLevel3Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=WarlockArchfeyNonGenericStarterClassArgs(
            skills=WarlockSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.DECEPTION: False,
                    Skill.HISTORY: True,
                    Skill.INTIMIDATION: False,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=10,
            constitution=14,
            intelligence=12,
            wisdom=13,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 1),
                (Ability.CHARISMA, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.RELIGION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Lucky(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WarlockLevel1(
                    cantrip_1=WarlockLevel0Spells.ELDRITCH_BLAST,
                    cantrip_2=WarlockLevel0Spells.MAGE_HAND,
                    spell_1=WarlockLevel1Spells.CHARM_PERSON,
                    spell_2=WarlockLevel1Spells.HEX,
                    eldritch_invocation=InvocationsLevel0.ELDRITCH_MIND,  # InvocationsLevel0.ELDRITCH_MIND,
                ),
                2: WarlockLevel2(
                    spell=WarlockLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                    eldritch_invocation_1=InvocationsLevel2.AGONIZING_BLAST,
                    eldritch_invocation_2=InvocationsLevel2.REPELLING_BLAST,
                ),
                3: WarlockLevel3(
                    spell=WarlockLevel2Spells.INVISIBILITY,
                ),
                4: WarlockLevel4(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=4,
                        ability=Ability.CHARISMA,
                    ),
                    cantrip=WarlockLevel0Spells.MINOR_ILLUSION,
                    spell=WarlockLevel2Spells.SPIDER_CLIMB,
                ),
                5: WarlockLevel5(
                    spell=WarlockLevel3Spells.MAJOR_IMAGE,
                    eldritch_invocation_1=InvocationsLevel5.GAZE_OF_TWO_MINDS,
                    eldritch_invocation_2=InvocationsLevel5.ONE_WITH_SHADOWS,
                ),
            },
            subclass_features_by_level={
                3: ArchfeyWarlockLevel3(),
                5: ArchfeyWarlockLevel5(),
            },
        ),
        replace_spells={},
    )


class OptimizedWarlockArchfeyCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Warlock Archfey",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.DECEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.ANIMAL_HANDLING,
                        Skill.MEDICINE,
                        Skill.PERSUASION,
                    ]
                ),
            ),
        )
