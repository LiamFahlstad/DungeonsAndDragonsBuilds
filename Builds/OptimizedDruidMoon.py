from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidLevel1,
    DruidLevel2,
    DruidLevel3,
    DruidLevel4,
    DruidLevel5,
    DruidLevel6,
    DruidLevel7,
    DruidLevel8,
    DruidLevel9,
    DruidLevel10,
    DruidLevel11,
    DruidLevel12,
    DruidLevel13,
    DruidLevel14,
    DruidLevel15,
    DruidLevel16,
    DruidLevel17,
    DruidLevel18,
    DruidLevel19,
    DruidLevel20,
)
from CharacterConfigs.SubClasses.DruidMoon import (
    MoonDruidLevel3,
    MoonDruidLevel5,
    MoonDruidLevel6,
    MoonDruidLevel7,
    MoonDruidLevel9,
    MoonDruidLevel10,
    MoonDruidLevel14,
    MoonDruidStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from SpeciesConfigs import Gnome
from Spells.Definitions import (
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    DruidLevel6Spells,
    DruidLevel7Spells,
    DruidLevel8Spells,
    DruidLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


def get_starter_class_builder():
    return MoonDruidStarterClassBuilder(
        druid_level=20,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=10,
            wisdom=15,
            charisma=12,
        ),
        # Choose two skills to be proficient in
        druid_skills=DruidSkillsStatBlock(
            proficiencies={
                Skill.ARCANA: True,
                Skill.ANIMAL_HANDLING: False,
                Skill.INSIGHT: False,
                Skill.MEDICINE: False,
                Skill.NATURE: False,
                Skill.PERCEPTION: True,
                Skill.RELIGION: False,
                Skill.SURVIVAL: False,
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
                Skill.INTIMIDATION,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        druid_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: DruidLevel1(
                    cantrip_1=DruidLevel0Spells.THUNDERCLAP,
                    cantrip_2=DruidLevel0Spells.SHILLELAGH,
                    spell_1=DruidLevel1Spells.ENTANGLE,
                    spell_2=DruidLevel1Spells.FAERIE_FIRE,
                    spell_3=DruidLevel1Spells.ANIMAL_FRIENDSHIP,
                    spell_4=DruidLevel1Spells.GOODBERRY,
                ),
                2: DruidLevel2(
                    spell=DruidLevel1Spells.HEALING_WORD,
                ),
                3: DruidLevel3(
                    spell=DruidLevel1Spells.CHARM_PERSON,
                ),
                4: DruidLevel4(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=4,
                        ability=Ability.WISDOM,
                    ),
                    cantrip=DruidLevel0Spells.ELEMENTALISM,
                    spell=DruidLevel2Spells.AID,
                ),
                5: DruidLevel5(
                    spell_1=DruidLevel3Spells.CALL_LIGHTNING,
                    spell_2=DruidLevel3Spells.AURA_OF_VITALITY,
                ),
                6: DruidLevel6(
                    spell=DruidLevel3Spells.DISPEL_MAGIC,
                ),
                7: DruidLevel7(
                    spell=DruidLevel2Spells.LESSER_RESTORATION,
                ),
                8: DruidLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                    spell=DruidLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: DruidLevel9(
                    spell_1=DruidLevel5Spells.CONTAGION,
                    spell_2=DruidLevel5Spells.GEAS,
                ),
                10: DruidLevel10(
                    spell=DruidLevel5Spells.ANTILIFE_SHELL,
                ),
                11: DruidLevel11(
                    spell=DruidLevel6Spells.CONJURE_FEY,
                ),
                12: DruidLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                13: DruidLevel13(
                    spell=DruidLevel7Spells.FIRE_STORM,
                ),
                14: DruidLevel14(spell=DruidLevel7Spells.MIRAGE_ARCANE),
                15: DruidLevel15(
                    spell=DruidLevel7Spells.REGENERATE,
                ),
                16: DruidLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                    spell_1=DruidLevel8Spells.EARTHQUAKE,
                    spell_2=DruidLevel8Spells.ANIMAL_SHAPES,
                ),
                17: DruidLevel17(
                    spell=DruidLevel9Spells.STORM_OF_VENGEANCE,
                ),
                19: DruidLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=DruidLevel9Spells.SHAPECHANGE,
                ),
                18: DruidLevel18(
                    spell=DruidLevel9Spells.TRUE_RESURRECTION,
                ),
                20: DruidLevel20(
                    spell=DruidLevel9Spells.FORESIGHT,
                ),
            },
            subclass_features_by_level={
                3: MoonDruidLevel3(),
                5: MoonDruidLevel5(),
                6: MoonDruidLevel6(),
                7: MoonDruidLevel7(),
                9: MoonDruidLevel9(),
                10: MoonDruidLevel10(),
                14: MoonDruidLevel14(),
            },
        ),
        replace_spells={},
    )


class OptimizedMoonDruidCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Moon Druid",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.ForestGnomeSpeciesBuilder(
                spell_casting_ability=Ability.WISDOM
            ),
        )
