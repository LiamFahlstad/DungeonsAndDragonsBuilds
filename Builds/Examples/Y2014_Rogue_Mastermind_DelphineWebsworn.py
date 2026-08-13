"""Example build: Rogue Mastermind (2014 rules). Demonstrates the subclass up through level 17."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
    RogueLevel1,
    RogueLevel2,
    RogueLevel3,
    RogueLevel4,
    RogueLevel5,
    RogueLevel6,
    RogueLevel7,
    RogueLevel8,
    RogueLevel9,
    RogueLevel10,
    RogueLevel11,
    RogueLevel12,
    RogueLevel13,
    RogueLevel14,
    RogueLevel15,
    RogueLevel16,
    RogueLevel17,
)
from CharacterContent.Classes.SubClasses2014.RogueMastermind import (
    RogueMastermindCustomStarterClassArgs,
    RogueMastermindLevel3,
    RogueMastermindLevel9,
    RogueMastermindLevel13,
    RogueMastermindLevel17,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Items
from CharacterContent.ToolProficiencies.Proficiencies import ThievesTools as ThievesToolsProficiency, DisguiseKit as DisguiseKitProficiency, ForgeryKit as ForgeryKitProficiency, PlayingCards
from CharacterContent.Species import Human
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RogueMastermindCustomStarterClassArgs(
            skills=RogueSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: False,
                    Skill.ATHLETICS: False,
                    Skill.DECEPTION: True,
                    Skill.INSIGHT: True,
                    Skill.INTIMIDATION: False,
                    Skill.INVESTIGATION: True,
                    Skill.PERCEPTION: False,
                    Skill.SLEIGHT_OF_HAND: False,
                    Skill.STEALTH: True,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=14,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 1),
                (Ability.DEXTERITY, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.PERSUASION,
                Skill.HISTORY,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.Alert(),
        armor=[
            Armor.LeatherArmor(),
        ],
        weapons=[
            Weapons.Rapier(),
            Weapons.Shortsword(),
        ],
        items=[
            (Items.ThievesTools(), 1),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevel1(
                    skill_expertise_1=Definitions.Skill.DECEPTION,
                    skill_expertise_2=Definitions.Skill.INSIGHT,
                    weapon_mastery_1=Weapons.Rapier(),
                    weapon_mastery_2=Weapons.Shortsword(),
                ),
                2: RogueLevel2(),
                3: RogueLevel3(),
                4: RogueLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                5: RogueLevel5(),
                6: RogueLevel6(
                    skill_expertise_1=Definitions.Skill.STEALTH,
                    skill_expertise_2=Definitions.Skill.PERSUASION,
                ),
                7: RogueLevel7(),
                8: RogueLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 2)]),
                ),
                9: RogueLevel9(),
                10: RogueLevel10(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                11: RogueLevel11(),
                12: RogueLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.CHARISMA, 2)]),
                ),
                13: RogueLevel13(),
                14: RogueLevel14(),
                15: RogueLevel15(),
                16: RogueLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                17: RogueLevel17(),
            },
            subclass_features_by_level={
                3: RogueMastermindLevel3(),
                9: RogueMastermindLevel9(),
                13: RogueMastermindLevel13(),
                17: RogueMastermindLevel17(),
            },
        ),
        tool_proficiencies=[ThievesToolsProficiency(),
            DisguiseKitProficiency(),
            ForgeryKitProficiency(),
            PlayingCards()],
    )


class Y2014RogueMastermindDelphineWebswornCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Delphine Websworn",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Definitions.Skill.PERCEPTION,
                origin_feat=OriginFeats.Alert(),
            ),
        )
