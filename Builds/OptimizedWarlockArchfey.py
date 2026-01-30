from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import FighterLevel1
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockLevel1,
    WarlockLevel2,
    WarlockLevel3,
    WarlockLevel4,
    WarlockLevel5,
)
from CharacterConfigs.SubClasses.FighterBattleMaster import (
    BattleMasterFighterStarterClassBuilder,
)
from CharacterConfigs.SubClasses.WarlockArchfey import (
    ArchfeyWarlockLevel3,
    ArchfeyWarlockLevel5,
    ArchfeyWarlockMulticlassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, FightingStyles, GeneralFeats, OriginFeats, Weapons
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
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    return BattleMasterFighterStarterClassBuilder(
        fighter_level=1,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=12,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=15,
        ),
        # Choose two skills to be proficient in
        fighter_skills=FighterSkillsStatBlock(
            proficiencies={
                Skill.ACROBATICS: True,
                Skill.ANIMAL_HANDLING: False,
                Skill.ATHLETICS: True,
                Skill.HISTORY: False,
                Skill.INSIGHT: False,
                Skill.INTIMIDATION: False,
                Skill.PERCEPTION: False,
                Skill.SURVIVAL: False,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 2),
                (Ability.CHARISMA, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.Greatsword(
                player_is_proficient=True,
                ability=Ability.CHARISMA,
            ),
        ],
        fighter_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Flail(),
                    weapon_mastery_3=Weapons.Greatsword(),
                    fighting_style=FightingStyles.Defense(),
                ),
            },
            subclass_features_by_level={},
        ),
    )


def get_multiclass_builder():
    return ArchfeyWarlockMulticlassBuilder(
        warlock_level=5,
        warlock_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WarlockLevel1(
                    cantrip_1=WarlockLevel0Spells.TRUE_STRIKE,
                    cantrip_2=WarlockLevel0Spells.MAGE_HAND,
                    spell_1=WarlockLevel1Spells.CHARM_PERSON,
                    spell_2=WarlockLevel1Spells.HEX,
                    eldritch_invocation=InvocationsLevel0.PACT_OF_THE_BLADE,  # InvocationsLevel0.ELDRITCH_MIND,
                ),
                2: WarlockLevel2(
                    spell=WarlockLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                    eldritch_invocation_1=InvocationsLevel2.AGONIZING_BLAST,
                    eldritch_invocation_2=InvocationsLevel2.REPELLING_BLAST,
                ),
                3: WarlockLevel3(
                    spell=WarlockLevel2Spells.MIRROR_IMAGE,
                ),
                4: WarlockLevel4(
                    general_feat=GeneralFeats.GreatWeaponMaster(
                        character_level=4,
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
        replace_spells={
            WarlockLevel1Spells.TASHAS_HIDEOUS_LAUGHTER: WarlockLevel3Spells.HUNGER_OF_HADAR,
            WarlockLevel1Spells.CHARM_PERSON: WarlockLevel2Spells.SUGGESTION,
        },
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
                        Skill.NATURE,
                    ]
                ),
            ),
            multiclass_builders=[get_multiclass_builder()],
        )
