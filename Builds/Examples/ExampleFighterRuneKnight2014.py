"""Example build: Fighter Rune Knight (2014 rules)."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
    FighterLevel5,
    FighterLevel6,
    FighterLevel7,
    FighterLevel8,
    FighterLevel9,
    FighterLevel10,
    FighterLevel11,
    FighterLevel12,
    FighterLevel13,
    FighterLevel14,
    FighterLevel15,
    FighterLevel16,
    FighterLevel17,
    FighterLevel18,
    FighterLevel19,
    FighterLevel20,
)
from CharacterConfigs.BaseClasses.ClassBuilder import (
    BaseClassLevelFeatures,
    StarterClassBuilder,
)
from CharacterConfigs.SubClasses2014.FighterRuneKnight import (
    FighterRuneKnightCustomStarterClassArgs,
    FighterRuneKnightLevel3,
    FighterRuneKnightLevel7,
    FighterRuneKnightLevel10,
    FighterRuneKnightLevel15,
    FighterRuneKnightLevel18,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Armor, Weapons
from SpeciesConfigs import Human
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterRuneKnightCustomStarterClassArgs(
            skills=FighterSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: False,
                    Skill.ANIMAL_HANDLING: True,
                    Skill.ATHLETICS: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERCEPTION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=18,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=12,
            constitution=14,
            intelligence=8,
            wisdom=10,
            charisma=13,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.STRENGTH, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.HISTORY,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        armor=[
            Armor.ChainMailArmor(),
        ],
        weapons=[
            Weapons.Longsword(),
            Weapons.Handaxe(),
        ],
        base_class_level_features=BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Handaxe(),
                    weapon_mastery_3=Weapons.Greataxe(),
                    fighting_style=FightingStyles.Defense(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Shortsword(),
                    general_feat=GeneralFeats.GreatWeaponMaster(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    )
                ),
                5: FighterLevel5(),
                6: FighterLevel6(
                    general_feat=GeneralFeats.Sentinel(
                        character_level=6,
                        ability=Ability.STRENGTH,
                    )
                ),
                7: FighterLevel7(),
                8: FighterLevel8(
                    general_feat=GeneralFeats.Durable(
                        character_level=8,
                        ability=Ability.CONSTITUTION,
                    )
                ),
                9: FighterLevel9(),
                10: FighterLevel10(
                    weapon_mastery=Weapons.Flail(),
                ),
                11: FighterLevel11(),
                12: FighterLevel12(
                    general_feat=GeneralFeats.Resilient(
                        character_level=12,
                        ability=Ability.CONSTITUTION,
                    )
                ),
                13: FighterLevel13(),
                14: FighterLevel14(
                    general_feat=GeneralFeats.Sentinel(
                        character_level=14,
                        ability=Ability.STRENGTH,
                    )
                ),
                15: FighterLevel15(),
                16: FighterLevel16(
                    weapon_mastery=Weapons.Warhammer(),
                    general_feat=GeneralFeats.GreatWeaponMaster(
                        character_level=16,
                        ability=Ability.STRENGTH,
                    )
                ),
                17: FighterLevel17(),
                18: FighterLevel18(),
                19: FighterLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                ),
                20: FighterLevel20(),
            },
            subclass_features_by_level={
                3: FighterRuneKnightLevel3(),
                7: FighterRuneKnightLevel7(),
                10: FighterRuneKnightLevel10(),
                15: FighterRuneKnightLevel15(),
                18: FighterRuneKnightLevel18(),
            },
        ),
    )


class ExampleFighterRuneKnight2014CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Fighter Rune Knight",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.SURVIVAL,
                        Skill.INSIGHT,
                        Skill.HISTORY,
                    ]
                ),
            ),
        )
