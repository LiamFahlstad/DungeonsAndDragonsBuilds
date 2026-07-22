"""Example build: Sorcerer Storm Sorcery (2014 rules). Demonstrates storm-themed elemental spellcasting."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.SorcererBase import (
    SorcererLevel1,
    SorcererLevel2,
    SorcererLevel3,
    SorcererLevel4,
    SorcererLevel5,
    SorcererLevel6,
    SorcererLevel7,
    SorcererLevel8,
    SorcererLevel9,
    SorcererLevel10,
    SorcererLevel11,
    SorcererLevel12,
    SorcererLevel13,
    SorcererLevel14,
    SorcererLevel15,
    SorcererLevel16,
    SorcererLevel17,
    SorcererLevel18,
)
from CharacterConfigs.SubClasses2014.SorcererStormSorcery import (
    SorcererStormSorceryCustomStarterClassArgs,
    SorcererStormSorceryLevel3,
    SorcererStormSorceryLevel6,
    SorcererStormSorceryLevel14,
    SorcererStormSorceryLevel18,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Weapons
from SpeciesConfigs import Human
from Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import SorcererSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=SorcererStormSorceryCustomStarterClassArgs(
            skills=SorcererSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.DECEPTION: True,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=18,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=10,
            wisdom=12,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERSUASION,
                Skill.INSIGHT,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Lucky(),
        weapons=[
            Weapons.Dagger(player_is_proficient=True),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: SorcererLevel1(
                    cantrip_1=SpellDefinitions.SorcererLevel0Spells.SHOCKING_GRASP,
                    cantrip_2=SpellDefinitions.SorcererLevel0Spells.FIRE_BOLT,
                    cantrip_3=SpellDefinitions.SorcererLevel0Spells.LIGHT,
                    cantrip_4=SpellDefinitions.SorcererLevel0Spells.PRESTIDIGITATION,
                    spell_1=SpellDefinitions.SorcererLevel1Spells.SHIELD,
                    spell_2=SpellDefinitions.SorcererLevel1Spells.THUNDERWAVE,
                ),
                2: SorcererLevel2(
                    spell_1=SpellDefinitions.SorcererLevel1Spells.FOG_CLOUD,
                    spell_2=SpellDefinitions.SorcererLevel1Spells.EXPEDITIOUS_RETREAT,
                ),
                3: SorcererLevel3(
                    spell_1=SpellDefinitions.SorcererLevel2Spells.GUST_OF_WIND,
                    spell_2=SpellDefinitions.SorcererLevel2Spells.DUST_DEVIL,
                ),
                4: SorcererLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]
                    ),
                    cantrip=SpellDefinitions.SorcererLevel0Spells.MAGE_HAND,
                    spell=SpellDefinitions.SorcererLevel2Spells.BLUR,
                ),
                5: SorcererLevel5(
                    spell_1=SpellDefinitions.SorcererLevel3Spells.COUNTERSPELL,
                    spell_2=SpellDefinitions.SorcererLevel3Spells.LIGHTNING_BOLT,
                ),
                6: SorcererLevel6(
                    spell=SpellDefinitions.SorcererLevel3Spells.BLINK,
                ),
                7: SorcererLevel7(
                    spell=SpellDefinitions.SorcererLevel4Spells.GREATER_INVISIBILITY,
                ),
                8: SorcererLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]
                    ),
                    spell=SpellDefinitions.SorcererLevel4Spells.DIMENSION_DOOR,
                ),
                9: SorcererLevel9(
                    spell_1=SpellDefinitions.SorcererLevel5Spells.CONE_OF_COLD,
                    spell_2=SpellDefinitions.SorcererLevel5Spells.CONTROL_WINDS,
                ),
                10: SorcererLevel10(
                    cantrip=SpellDefinitions.SorcererLevel0Spells.THUNDERCLAP,
                    spell=SpellDefinitions.SorcererLevel5Spells.CLOUDKILL,
                ),
                11: SorcererLevel11(
                    spell=SpellDefinitions.SorcererLevel5Spells.TELEKINESIS,
                ),
                12: SorcererLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.WISDOM, 2)]
                    ),
                ),
                13: SorcererLevel13(
                    spell=SpellDefinitions.SorcererLevel5Spells.HOLD_MONSTER,
                ),
                14: SorcererLevel14(),
                15: SorcererLevel15(
                    spell=SpellDefinitions.SorcererLevel5Spells.ANIMATE_OBJECTS,
                ),
                16: SorcererLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CONSTITUTION, 2)]
                    ),
                ),
                17: SorcererLevel17(
                    spell=SpellDefinitions.SorcererLevel5Spells.SUMMON_DRACONIC_SPIRIT,
                ),
                18: SorcererLevel18(
                    spell=SpellDefinitions.SorcererLevel5Spells.TELEPORTATION_CIRCLE,
                ),
            },
            subclass_features_by_level={
                3: SorcererStormSorceryLevel3(),
                6: SorcererStormSorceryLevel6(),
                14: SorcererStormSorceryLevel14(),
                18: SorcererStormSorceryLevel18(),
            },
        ),
    )


class ExampleSorcererStormSorcery2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Storm Sorcerer",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.ARCANA,
                origin_feat=OriginFeats.Lucky(),
            ),
        )
