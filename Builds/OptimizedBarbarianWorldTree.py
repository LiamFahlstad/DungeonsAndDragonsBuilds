from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
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
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.SubClasses.BarbarianPathOfTheWorldTree import (
    BarbarianWorldTreeLevel3,
    BarbarianWorldTreeLevel6,
    BarbarianWorldTreeLevel10,
    BarbarianWorldTreeLevel14,
    BarbarianWorldTreeNonGenericStarterClassArgs,
)
from Definitions import Ability, Skill
from Features import Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.SpeciesFeatures import GoliathFeatures
from SpeciesConfigs import Goliath
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BarbarianWorldTreeNonGenericStarterClassArgs(
            skills=BarbarianSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: True,
                    Skill.INTIMIDATION: False,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=4,  # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=13,
            constitution=14,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.STRENGTH, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.PERFORMANCE,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.WarPick(player_is_proficient=True),
            Weapons.LightCrossbow(player_is_proficient=True),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BarbarianLevel1(
                    weapon_mastery_1=Weapons.LightCrossbow(),
                    weapon_mastery_2=Weapons.WarPick(),
                ),
                2: BarbarianLevel2(),
                3: BarbarianLevel3(
                    skill=Skill.PERCEPTION,
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
                3: BarbarianWorldTreeLevel3(),
                6: BarbarianWorldTreeLevel6(),
                10: BarbarianWorldTreeLevel10(),
                14: BarbarianWorldTreeLevel14(),
            },
        ),
    )


class OptimizedBarbarianWorldTreeCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized World Tree Barbarian",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Goliath.GoliathSpeciesBuilder(
                giant_ancestry_type=GoliathFeatures.GiantAncestryType.HILL_GIANT,
            ),
        )
