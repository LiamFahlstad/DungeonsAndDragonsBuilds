from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
    PaladinLevel4,
    PaladinLevel5,
)
from CharacterConfigs.SubClasses2024.PaladinGlory import (
    PaladinGloryCustomStarterClassArgs,
    PaladinGloryLevel3,
    PaladinGloryLevel5,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Human
from Spells.SpellLists import PaladinLevel1Spells, PaladinLevel2Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


# Paladin 5 (half caster, single class).
# Expected spell slots: {1: 4, 2: 2}  — (5+1)//2 = 3 → full caster level 3
def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinGloryCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.MEDICINE: True,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=5,
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=10,
            constitution=13,
            intelligence=8,
            wisdom=12,
            charisma=14,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [(Ability.STRENGTH, 2), (Ability.CHARISMA, 1)]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [Skill.INTIMIDATION, Skill.PERSUASION]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Javelin(),
                    spell_1=PaladinLevel1Spells.DETECT_POISON_AND_DISEASE,
                    spell_2=PaladinLevel1Spells.DIVINE_FAVOR,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.Defense(),
                    spell=PaladinLevel1Spells.SHIELD_OF_FAITH,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.BLESS,
                ),
                4: PaladinLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [(Ability.CHARISMA, 2)]
                    ),
                    spell=PaladinLevel1Spells.CURE_WOUNDS,
                ),
                5: PaladinLevel5(
                    spell=PaladinLevel2Spells.ZONE_OF_TRUTH,
                ),
            },
            subclass_features_by_level={
                3: PaladinGloryLevel3(),
                5: PaladinGloryLevel5(),
            },
        ),
    )


class SpellSlotTestPaladin5CharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Spell Slot Test Paladin 5",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.PERCEPTION,
                origin_feat=OriginFeats.Skilled(
                    skills=[Skill.INVESTIGATION, Skill.NATURE, Skill.SURVIVAL]
                ),
            ),
        )
