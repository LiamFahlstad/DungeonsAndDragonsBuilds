from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
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
from CharacterConfigs.SubClasses.ClericLight import (
    LightClericLevel3,
    LightClericLevel6,
    LightClericLevel17,
    LightClericStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from SpeciesConfigs import Gnome
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
    return LightClericStarterClassBuilder(
        cleric_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=10,
            wisdom=15,
            charisma=12,
        ),
        # Choose two skills to be proficient in
        cleric_skills=ClericSkillsStatBlock(
            proficiencies={
                Skill.HISTORY: False,
                Skill.INSIGHT: True,
                Skill.MEDICINE: False,
                Skill.PERSUASION: True,
                Skill.RELIGION: False,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.MEDICINE,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        cleric_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: ClericLevel1(
                    cantrip_1=ClericLevel0Spells.GUIDANCE,
                    cantrip_2=ClericLevel0Spells.LIGHT,
                    cantrip_3=ClericLevel0Spells.RESISTANCE,
                    spell_1=ClericLevel1Spells.HEALING_WORD,
                    spell_2=ClericLevel1Spells.BANE,
                    spell_3=ClericLevel1Spells.CREATE_OR_DESTROY_WATER,
                    spell_4=ClericLevel1Spells.GUIDING_BOLT,
                ),
                2: ClericLevel2(
                    spell=ClericLevel1Spells.BLESS,
                ),
                3: ClericLevel3(
                    spell=ClericLevel1Spells.COMMAND,
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
                3: LightClericLevel3(),
                6: LightClericLevel6(),
                17: LightClericLevel17(),
            },
        ),
        replace_spells={},
    )


class OptimizedLightClericCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Light Cleric",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.ForestGnomeSpeciesBuilder(
                spell_casting_ability=Ability.WISDOM
            ),
        )
