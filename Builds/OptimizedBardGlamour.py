from Builds import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BardBase import (
    BardLevel1,
    BardLevel2,
    BardLevel3,
    BardLevel4,
    BardLevel5,
    BardLevel6,
    BardLevel7,
    BardLevel8,
    BardLevel9,
    BardLevel10,
    BardLevel11,
    BardLevel12,
    BardLevel13,
    BardLevel14,
    BardLevel15,
    BardLevel16,
    BardLevel17,
    BardLevel18,
    BardLevel19,
    BardLevel20,
)
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.SubClasses.BardGlamour import (
    BardGlamourLevel3,
    BardGlamourLevel6,
    BardGlamourLevel14,
    BardGlamourNonGenericStarterClassArgs,
)
from Definitions import Ability, Skill
from Features import Backgrounds, EpicBoon, GeneralFeats, OriginFeats
from Items import Items, Packs
from SpeciesConfigs import Aasimar
from Spells.Definitions import (
    BardLevel0Spells,
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    BardLevel4Spells,
    BardLevel5Spells,
    BardLevel6Spells,
    BardLevel7Spells,
    BardLevel8Spells,
    BardLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=BardGlamourNonGenericStarterClassArgs(
            skills=BardSkillsStatBlock(
                proficiencies={
                    Skill.PERFORMANCE: True,
                    Skill.PERSUASION: True,
                    Skill.DECEPTION: True,
                }
            ),
        ),
        base_class_level=4,  # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=13,
            constitution=14,
            intelligence=10,
            wisdom=12,
            charisma=15,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CHARISMA, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Musician(),
        armor=[],
        weapons=[],
        items=Packs.Entertainers().get_items() + [(Items.Typewriter(), 1)],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: BardLevel1(
                    cantrip_1=BardLevel0Spells.VICIOUS_MOCKERY,
                    cantrip_2=BardLevel0Spells.MAGE_HAND,
                    spell_1=BardLevel1Spells.HEALING_WORD,
                    spell_2=BardLevel1Spells.FAERIE_FIRE,
                    spell_3=BardLevel1Spells.SLEEP,
                    spell_4=BardLevel1Spells.TASHAS_HIDEOUS_LAUGHTER,
                ),
                2: BardLevel2(
                    spell=BardLevel1Spells.DISSONANT_WHISPERS,
                    skill_1=Skill.PERFORMANCE,
                    skill_2=Skill.PERSUASION,
                ),
                3: BardLevel3(
                    spell=BardLevel2Spells.AID,
                ),
                4: BardLevel4(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=4,
                        ability=Ability.CHARISMA,
                    ),
                    cantrip=BardLevel0Spells.MINOR_ILLUSION,
                    spell=BardLevel2Spells.ENHANCE_ABILITY,
                ),
                5: BardLevel5(
                    spell_1=BardLevel3Spells.BESTOW_CURSE,
                    spell_2=BardLevel3Spells.FEAR,
                ),
                6: BardLevel6(
                    spell=BardLevel3Spells.DISPEL_MAGIC,
                ),
                7: BardLevel7(
                    spell=BardLevel2Spells.LESSER_RESTORATION,
                ),
                8: BardLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                    spell=BardLevel4Spells.FREEDOM_OF_MOVEMENT,
                ),
                9: BardLevel9(
                    spell_1=BardLevel5Spells.ALUSTRIELS_MOONCLOAK,
                    spell_2=BardLevel5Spells.GEAS,
                    skill_1=Skill.STEALTH,
                    skill_2=Skill.PERCEPTION,
                ),
                10: BardLevel10(
                    cantrip=BardLevel0Spells.VICIOUS_MOCKERY,
                    spell=BardLevel5Spells.SEEMING,
                ),
                11: BardLevel11(
                    spell=BardLevel6Spells.TRUE_SEEING,
                ),
                12: BardLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CHARISMA, 1),
                            (Ability.CONSTITUTION, 1),
                        ]
                    ),
                ),
                13: BardLevel13(
                    spell=BardLevel7Spells.MORDENKAINENS_SWORD,
                ),
                14: BardLevel14(),
                15: BardLevel15(
                    spell=BardLevel7Spells.REGENERATE,
                ),
                16: BardLevel16(
                    general_feat=GeneralFeats.WarCaster(
                        character_level=16,
                        ability=Ability.CHARISMA,
                    ),
                ),
                17: BardLevel17(
                    spell=BardLevel9Spells.PRISMATIC_WALL,
                ),
                19: BardLevel19(
                    epic_boon=EpicBoon.DummyEpicBoon(),
                    spell=BardLevel8Spells.BEFUDDLEMENT,
                ),
                18: BardLevel18(
                    spell=BardLevel9Spells.TRUE_POLYMORPH,
                ),
                20: BardLevel20(
                    spell=BardLevel9Spells.FORESIGHT,
                ),
            },
            subclass_features_by_level={
                3: BardGlamourLevel3(),
                6: BardGlamourLevel6(),
                14: BardGlamourLevel14(),
            },
        ),
        replace_spells={
            # Replace the default spell choices with better ones
            BardLevel1Spells.SLEEP: BardLevel2Spells.ENHANCE_ABILITY,
        },
    )


class OptimizedBardGlamourCharacterBuilder(CharacterBuilder.CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Glamour Bard",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Aasimar.AasimarSpeciesBuilder(character_level=3),
        )
