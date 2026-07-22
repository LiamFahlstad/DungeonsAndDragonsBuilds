"""Example build: Barbarian Path of the Berserker (2014 rules)."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses.BarbarianBase import (
    BarbarianLevel1,
    BarbarianLevel2,
    BarbarianLevel3,
    BarbarianLevel4,
    BarbarianLevel5,
    BarbarianLevel6,
    BarbarianLevel7,
    BarbarianLevel8,
    BarbarianLevel9,
    BarbarianLevel10,
    BarbarianLevel11,
    BarbarianLevel12,
    BarbarianLevel13,
    BarbarianLevel14,
    BarbarianLevel15,
    BarbarianLevel16,
    BarbarianLevel17,
    BarbarianLevel18,
    BarbarianLevel19,
    BarbarianLevel20,
)
from CharacterConfigs.BaseClasses.ClassBuilder import (
    BaseClassLevelFeatures,
    StarterClassBuilder,
)
from CharacterConfigs.SubClasses2014.BarbarianPathOfTheBerserker import (
    BarbarianBerserkerCustomStarterClassArgs,
    BarbarianBerserkerLevel3,
    BarbarianBerserkerLevel6,
    BarbarianBerserkerLevel10,
    BarbarianBerserkerLevel14,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Features.Equipment import Weapons
from SpeciesConfigs import Orc
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BarbarianBerserkerCustomStarterClassArgs(
            skills=BarbarianSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: True,
                    Skill.INTIMIDATION: True,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=13,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 1),
                (Ability.STRENGTH, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.Greataxe(player_is_proficient=True, player_has_mastery=True),
        ],
        base_class_level_features=BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BarbarianLevel1(
                    weapon_mastery_1=Weapons.Handaxe(),
                    weapon_mastery_2=Weapons.Greataxe(),
                ),
                2: BarbarianLevel2(),
                3: BarbarianLevel3(
                    skill=Skill.SURVIVAL,
                ),
                4: BarbarianLevel4(
                    general_feat=GeneralFeats.Sentinel(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    )
                ),
                5: BarbarianLevel5(),
                6: BarbarianLevel6(),
                7: BarbarianLevel7(),
                8: BarbarianLevel8(
                    general_feat=GeneralFeats.Sentinel(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    )
                ),
                9: BarbarianLevel9(),
                10: BarbarianLevel10(),
                11: BarbarianLevel11(),
                12: BarbarianLevel12(
                    general_feat=GeneralFeats.Sentinel(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    )
                ),
                13: BarbarianLevel13(),
                14: BarbarianLevel14(),
                15: BarbarianLevel15(),
                16: BarbarianLevel16(
                    general_feat=GeneralFeats.Sentinel(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    )
                ),
                17: BarbarianLevel17(),
                18: BarbarianLevel18(),
                19: BarbarianLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                ),
                20: BarbarianLevel20(),
            },
            subclass_features_by_level={
                3: BarbarianBerserkerLevel3(),
                6: BarbarianBerserkerLevel6(),
                10: BarbarianBerserkerLevel10(),
                14: BarbarianBerserkerLevel14(),
            },
        ),
    )


class ExampleBarbarianBerserker2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Berserker Barbarian",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Orc.OrcSpeciesBuilder(),
        )
