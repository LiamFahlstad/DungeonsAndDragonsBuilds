from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericLevel1,
    ClericLevel2,
    ClericLevel3,
    ClericLevel4,
    ClericLevel5,
    ClericLevel6,
    ClericLevel7,
    ClericLevel8,
    ClericLevel9,
    ClericLevel10,
    ClericLevel11,
    ClericLevel12,
    ClericLevel13,
    ClericLevel14,
    ClericLevel15,
    ClericLevel16,
    ClericLevel17,
    ClericLevel18,
    ClericLevel19,
    ClericLevel20,
)
from CharacterConfigs.SubClasses.ClericKnowledge import (
    ClericKnowledgeLevel3,
    ClericKnowledgeLevel6,
    ClericKnowledgeLevel17,
    ClericKnowledgeNonGenericStarterClassArgs,
)
from Definitions import Ability, Skill
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from SpeciesConfigs import Warforged
from Spells.Definitions import (
    ClericLevel0Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    ClericLevel6Spells,
    ClericLevel7Spells,
    ClericLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=ClericKnowledgeNonGenericStarterClassArgs(
            skills=ClericSkillsStatBlock(
                proficiencies={
                    Skill.HISTORY: True,
                    Skill.INSIGHT: True,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=8,
            constitution=14,
            intelligence=10,
            wisdom=15,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.STRENGTH, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[
            Armor.ChainMailArmor(),
        ],
        weapons=[
            Weapons.Warhammer(player_is_proficient=True, player_has_mastery=False),
            Weapons.Maul(player_is_proficient=True, player_has_mastery=False),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ClericLevel1(
                    cantrip_1=ClericLevel0Spells.GUIDANCE,
                    cantrip_2=ClericLevel0Spells.TOLL_THE_DEAD,
                    cantrip_3=ClericLevel0Spells.SACRED_FLAME,
                    spell_1=ClericLevel1Spells.HEALING_WORD,
                    spell_2=ClericLevel1Spells.BLESS,
                    spell_3=ClericLevel1Spells.CURE_WOUNDS,
                    spell_4=ClericLevel1Spells.GUIDING_BOLT,
                ),
                2: ClericLevel2(
                    spell=ClericLevel1Spells.SANCTUARY,
                ),
                3: ClericLevel3(
                    spell=ClericLevel2Spells.SPIRITUAL_WEAPON,
                ),
                4: ClericLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                    cantrip=ClericLevel0Spells.SPARE_THE_DYING,
                    spell=ClericLevel2Spells.AID,
                ),
                5: ClericLevel5(
                    spell_1=ClericLevel3Spells.BESTOW_CURSE,
                    spell_2=ClericLevel3Spells.AURA_OF_VITALITY,
                ),
                6: ClericLevel6(
                    spell=ClericLevel3Spells.DISPEL_MAGIC,
                ),
                7: ClericLevel7(
                    spell=ClericLevel2Spells.LESSER_RESTORATION,
                ),
                8: ClericLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                    spell=ClericLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: ClericLevel9(
                    spell_1=ClericLevel5Spells.FLAME_STRIKE,
                    spell_2=ClericLevel5Spells.GEAS,
                ),
                10: ClericLevel10(
                    cantrip=ClericLevel0Spells.MENDING,
                    spell=ClericLevel5Spells.CIRCLE_OF_POWER,
                ),
                11: ClericLevel11(
                    spell=ClericLevel6Spells.TRUE_SEEING,
                ),
                12: ClericLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                13: ClericLevel13(
                    spell=ClericLevel7Spells.CONJURE_CELESTIAL,
                ),
                14: ClericLevel14(),
                15: ClericLevel15(
                    spell=ClericLevel7Spells.REGENERATE,
                ),
                16: ClericLevel16(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=16,
                        ability=Ability.WISDOM,
                    ),
                ),
                17: ClericLevel17(
                    spell=ClericLevel9Spells.GATE,
                ),
                19: ClericLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=ClericLevel9Spells.MASS_HEAL,
                ),
                18: ClericLevel18(
                    spell=ClericLevel9Spells.POWER_WORD_HEAL,
                ),
                20: ClericLevel20(
                    spell=ClericLevel9Spells.ASTRAL_PROJECTION,
                ),
            },
            subclass_features_by_level={
                3: ClericKnowledgeLevel3(
                    skill_1=Skill.HISTORY,
                    skill_2=Skill.RELIGION,
                ),
                6: ClericKnowledgeLevel6(),
                17: ClericKnowledgeLevel17(),
            },
        ),
        replace_spells={ClericLevel1Spells.HEALING_WORD: ClericLevel2Spells.AUGURY},
    )


class OptimizedClericKnowledgeCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Knowledge Cleric",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Warforged.WarForgedSpeciesBuilder(
                skill=Skill.MEDICINE,
            ),
        )
