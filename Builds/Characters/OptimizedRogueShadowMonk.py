from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import (
    MonkLevel1,
    MonkLevel2,
    MonkLevel3,
    MonkLevel4,
    MonkLevel5,
    MonkLevel6,
    MonkLevel7,
    MonkLevel8,
    MonkLevel9,
    MonkLevel10,
    MonkLevel11,
    MonkLevel12,
    MonkLevel13,
    MonkLevel14,
    MonkLevel15,
    MonkLevel16,
    MonkLevel17,
    MonkLevel18,
    MonkLevel19,
)
from CharacterConfigs.BaseClasses.RogueBase import RogueCustomStarterClassArgs, RogueLevel1
from CharacterConfigs.SubClasses2024.MonkShadow import (
    MonkShadowLevel3,
    MonkShadowLevel6,
    MonkShadowLevel11,
    MonkShadowLevel17,
    MonkShadowMulticlassBuilder,
)
from Core.Definitions import Ability, RogueSubclass, Skill
from Features.CharacterFeats import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Features.Equipment import Weapons
from SpeciesConfigs import Halfing
from StatBlocks.AbilitiesStatBlock import PointBuyAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RogueCustomStarterClassArgs(
            # This build only ever takes 1 level of Rogue before dipping into
            # Monk for the rest of its career, so the Rogue subclass (chosen
            # at Rogue level 3) is never actually reached. The value below is
            # therefore a placeholder - it's immediately overwritten by the
            # Monk multiclass builder's "Warrior of Shadow" subclass once the
            # sheets are merged (see CharacterBuilder.build()/merge_with()).
            subclass=RogueSubclass.THIEF.value,
            skills=RogueSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: False,
                    Skill.DECEPTION: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.INVESTIGATION: False,
                    Skill.PERCEPTION: True,
                    Skill.PERSUASION: False,
                    Skill.SLEIGHT_OF_HAND: True,
                    Skill.STEALTH: True,
                }
            ),
        ),
        base_class_level=1,
        # Point Buy (27 points), reverse-engineered so that, after the +2
        # Dex/+1 Wis background bonus below and the four +2 Monk ASIs applied
        # in the multiclass builder (Dex, Wis, Dex, Wis), the final array is
        # Dex 21 / Wis 20 / Con 14 / Int 10 / Str 8 / Cha 8.
        abilities=PointBuyAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=14,
            intelligence=10,
            wisdom=15,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 2),
                (Ability.WISDOM, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.INVESTIGATION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.TavernBrawler(),
        armor=[],
        weapons=[
            Weapons.Shortbow(player_is_proficient=True),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RogueLevel1(
                    skill_1=Skill.ACROBATICS,
                    skill_2=Skill.STEALTH,
                    weapon_mastery_1=Weapons.Dagger(player_is_proficient=True),
                    weapon_mastery_2=Weapons.Shortbow(player_is_proficient=True),
                ),
            },
            subclass_features_by_level={},
        ),
    )


def get_monk_multiclass_builder():
    return MonkShadowMulticlassBuilder(
        monk_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                # Unlike a same-class resumption (e.g. Paladin picked back up
                # after a Warlock dip), Monk level 1 here is NOT granted by
                # the starter class builder - the starter class is Rogue, so
                # every Monk level from 1 to 19 is new and must be declared.
                1: MonkLevel1(),
                2: MonkLevel2(),
                3: MonkLevel3(),
                4: MonkLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.DEXTERITY, 2)]
                    ),
                ),
                5: MonkLevel5(),
                6: MonkLevel6(),
                7: MonkLevel7(),
                8: MonkLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.WISDOM, 2)]
                    ),
                ),
                9: MonkLevel9(),
                10: MonkLevel10(),
                11: MonkLevel11(),
                12: MonkLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.DEXTERITY, 2)]
                    ),
                ),
                13: MonkLevel13(),
                14: MonkLevel14(),
                15: MonkLevel15(),
                16: MonkLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.WISDOM, 2)]
                    ),
                ),
                17: MonkLevel17(),
                18: MonkLevel18(),
                # Monk level 19 is this character's capstone (character level
                # 20 = Rogue 1 + Monk 19), trading away the true Monk 20
                # "Body and Mind" feature for the Epic Boon below. Only a
                # DummyEpicBoon placeholder exists in this engine - there is
                # no "Boon of the Night Spirit" implemented, so its +1 Dex is
                # folded into the ability array above instead.
                19: MonkLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                ),
            },
            subclass_features_by_level={
                3: MonkShadowLevel3(),
                6: MonkShadowLevel6(),
                11: MonkShadowLevel11(),
                17: MonkShadowLevel17(),
            },
        ),
        monk_level=19,
    )


class OptimizedRogueShadowMonkCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Rogue Shadow Monk",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Halfing.HalflingSpeciesBuilder(),
            multiclass_builders=[
                get_monk_multiclass_builder(),
            ],
        )
