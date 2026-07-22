"""Example build: Artificer Armorer (2014 rules). Demonstrates the subclass through level 17."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import (
    ArtificerLevel1,
    ArtificerLevel2,
    ArtificerLevel3,
    ArtificerLevel4,
    ArtificerLevel5,
    ArtificerLevel6,
    ArtificerLevel7,
    ArtificerLevel8,
    ArtificerLevel9,
    ArtificerLevel10,
    ArtificerLevel11,
    ArtificerLevel12,
    ArtificerLevel13,
    ArtificerLevel14,
    ArtificerLevel15,
    ArtificerLevel16,
    ArtificerLevel17,
)
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.SubClasses2014.ArtificerArmorer import (
    ArtificerArmorerCustomStarterClassArgs,
    ArtificerArmorerLevel3,
    ArtificerArmorerLevel5,
    ArtificerArmorerLevel9,
    ArtificerArmorerLevel13,
    ArtificerArmorerLevel15,
    ArtificerArmorerLevel17,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Equipment import Armor, Weapons
from SpeciesConfigs import Dwarf
from Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ArtificerArmorerCustomStarterClassArgs(
            skills=ArtificerSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.HISTORY: False,
                    Skill.NATURE: False,
                    Skill.INVESTIGATION: False,
                    Skill.MEDICINE: False,
                    Skill.PERCEPTION: True,
                    Skill.SLEIGHT_OF_HAND: False,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=10,
            constitution=15,
            intelligence=14,
            wisdom=12,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERCEPTION,
                Skill.INVESTIGATION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.ChainMailArmor(),
        ],
        weapons=[
            Weapons.Warhammer(player_is_proficient=True, ability=Ability.INTELLIGENCE),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ArtificerLevel1(
                    cantrip_1=SpellDefinitions.ArtificerLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.ArtificerLevel0Spells.MAGIC_STONE,
                    spell_1=SpellDefinitions.ArtificerLevel1Spells.CATAPULT,
                    spell_2=SpellDefinitions.ArtificerLevel1Spells.EXPEDITIOUS_RETREAT,
                ),
                2: ArtificerLevel2(
                    spell=SpellDefinitions.ArtificerLevel1Spells.ALARM,
                ),
                3: ArtificerLevel3(
                    spell=SpellDefinitions.ArtificerLevel1Spells.FEATHER_FALL,
                ),
                4: ArtificerLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]
                    ),
                    spell=SpellDefinitions.ArtificerLevel1Spells.GREASE,
                ),
                5: ArtificerLevel5(
                    spell=SpellDefinitions.ArtificerLevel2Spells.MAGIC_WEAPON,
                ),
                6: ArtificerLevel6(),
                7: ArtificerLevel7(
                    spell=SpellDefinitions.ArtificerLevel2Spells.HEAT_METAL,
                ),
                8: ArtificerLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                9: ArtificerLevel9(
                    spell_1=SpellDefinitions.ArtificerLevel3Spells.PROTECTION_FROM_ENERGY,
                    spell_2=SpellDefinitions.ArtificerLevel3Spells.HASTE,
                ),
                10: ArtificerLevel10(
                    cantrip=SpellDefinitions.ArtificerLevel0Spells.SHOCKING_GRASP,
                ),
                11: ArtificerLevel11(
                    spell=SpellDefinitions.ArtificerLevel3Spells.FLAME_ARROWS,
                ),
                12: ArtificerLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.STRENGTH, 2),
                        ]
                    ),
                ),
                13: ArtificerLevel13(
                    spell=SpellDefinitions.ArtificerLevel4Spells.STONESKIN,
                ),
                14: ArtificerLevel14(
                    cantrip=SpellDefinitions.ArtificerLevel0Spells.THUNDERCLAP,
                ),
                15: ArtificerLevel15(
                    spell=SpellDefinitions.ArtificerLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                16: ArtificerLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                17: ArtificerLevel17(
                    spell_1=SpellDefinitions.ArtificerLevel5Spells.WALL_OF_STONE,
                    spell_2=SpellDefinitions.ArtificerLevel5Spells.ANIMATE_OBJECTS,
                ),
            },
            subclass_features_by_level={
                3: ArtificerArmorerLevel3(),
                5: ArtificerArmorerLevel5(),
                9: ArtificerArmorerLevel9(),
                13: ArtificerArmorerLevel13(),
                15: ArtificerArmorerLevel15(),
                17: ArtificerArmorerLevel17(),
            },
        ),
    )


class ExampleArtificerArmorer2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Armorer Artificer",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
