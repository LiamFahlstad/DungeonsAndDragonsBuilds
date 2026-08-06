"""Example build: Fighter Samurai (2014 rules)."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
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
from CharacterContent.Classes.BaseClasses.ClassBuilder import (
    BaseClassLevelFeatures,
    StarterClassBuilder,
)
from CharacterContent.Classes.SubClasses2014.FighterSamurai import (
    FighterSamuraiCustomStarterClassArgs,
    FighterSamuraiLevel3,
    FighterSamuraiLevel7,
    FighterSamuraiLevel10,
    FighterSamuraiLevel15,
    FighterSamuraiLevel18,
)
from CharacterContent.Features.SubClassFeatures2014.Fighter import FighterSamuraiFeatures
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Species import Human
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterSamuraiCustomStarterClassArgs(
            skills=FighterSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: False,
                    Skill.ATHLETICS: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERCEPTION: True,
                    Skill.PERSUASION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=18,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
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
                (Ability.STRENGTH, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERFORMANCE,
                Skill.INTIMIDATION,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Tough(),
        armor=[
            Armor.ChainMailArmor(),
        ],
        weapons=[
            Weapons.Longsword(),
            Weapons.Longbow(),
        ],
        base_class_level_features=BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Longbow(),
                    weapon_mastery_3=Weapons.Shortsword(),
                    fighting_style=FightingStyles.Dueling(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Handaxe(),
                    general_feat=GeneralFeats.Observant(
                        character_level=4,
                        ability=Ability.WISDOM,
                    ),
                ),
                5: FighterLevel5(),
                6: FighterLevel6(
                    general_feat=GeneralFeats.Resilient(
                        character_level=6,
                        ability=Ability.WISDOM,
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
                    weapon_mastery=Weapons.Longsword(),
                ),
                11: FighterLevel11(),
                12: FighterLevel12(
                    general_feat=GeneralFeats.Resilient(
                        character_level=12,
                        ability=Ability.WISDOM,
                    )
                ),
                13: FighterLevel13(),
                14: FighterLevel14(
                    general_feat=GeneralFeats.Resilient(
                        character_level=14,
                        ability=Ability.CONSTITUTION,
                    )
                ),
                15: FighterLevel15(),
                16: FighterLevel16(
                    weapon_mastery=Weapons.Longbow(),
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
                3: FighterSamuraiLevel3(),
                7: FighterSamuraiLevel7(),
                10: FighterSamuraiLevel10(),
                15: FighterSamuraiLevel15(),
                18: FighterSamuraiLevel18(),
            },
        ),
    )


class Y2014FighterSamuraiKaitoStormedgeCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Kaito Stormedge",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.INSIGHT,
                origin_feat=OriginFeats.Skilled(
                    skills=[
                        Skill.SURVIVAL,
                        Skill.HISTORY,
                        Skill.ACROBATICS,
                    ]
                ),
            ),
        )
