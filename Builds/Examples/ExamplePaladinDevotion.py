"""Example build: Paladin Oath of Devotion."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
)
from CharacterConfigs.SubClasses.PaladinDevotion import (
    DevotionPaladinLevel3,
    PaladinDevotionCustomStarterClassArgs,
)
from Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, OriginFeats
from Features.Combat import FightingStyles
from Features.Equipment import Weapons
from SpeciesConfigs import Human
from Spells.SpellLists import PaladinLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=PaladinDevotionCustomStarterClassArgs(
            skills=PaladinSkillsStatBlock(
                proficiencies={
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: True,
                    Skill.INTIMIDATION: False,
                    Skill.MEDICINE: False,
                    Skill.PERSUASION: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=8,
            constitution=13,
            intelligence=10,
            wisdom=12,
            charisma=14,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 2),
                (Ability.CHARISMA, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.RELIGION,
                Skill.MEDICINE,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[
            Weapons.Longsword(player_is_proficient=True, ability=Ability.STRENGTH),
        ],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Longsword(),
                    weapon_mastery_2=Weapons.Handaxe(),
                    spell_1=PaladinLevel1Spells.THUNDEROUS_SMITE,
                    spell_2=PaladinLevel1Spells.COMMAND,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.Defense(),
                    spell=PaladinLevel1Spells.BLESS,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.CURE_WOUNDS,
                ),
            },
            subclass_features_by_level={
                3: DevotionPaladinLevel3(),
            },
        ),
        replace_spells={},
    )


class ExamplePaladinDevotionCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Paladin Devotion",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.MEDICINE,
                origin_feat=OriginFeats.Alert(),
            ),
        )
