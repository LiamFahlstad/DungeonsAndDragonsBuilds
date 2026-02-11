from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinLevel1,
    PaladinLevel2,
    PaladinLevel3,
)
from CharacterConfigs.SubClasses.PaladinGlory import (
    GloryPaladinLevel3,
    GloryPaladinStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import Backgrounds, FightingStyles, OriginFeats, Weapons
from SpeciesConfigs import Human
from Spells.Definitions import PaladinLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


def get_starter_class_builder():
    return GloryPaladinStarterClassBuilder(
        paladin_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=13,
            dexterity=10,
            constitution=15,
            intelligence=12,
            wisdom=8,
            charisma=14,
        ),
        # Choose two skills to be proficient in
        paladin_skills=PaladinSkillsStatBlock(
            proficiencies={
                Skill.ATHLETICS: True,
                Skill.INSIGHT: False,
                Skill.INTIMIDATION: False,
                Skill.MEDICINE: True,
                Skill.PERSUASION: False,
                Skill.RELIGION: False,
            }
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.CONSTITUTION, 1),
                (Ability.CHARISMA, 2),
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
        weapons=[
            Weapons.Morningstar(player_is_proficient=True),
        ],
        paladin_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: PaladinLevel1(
                    weapon_mastery_1=Weapons.Handaxe(),
                    weapon_mastery_2=Weapons.Morningstar(),
                    spell_1=PaladinLevel1Spells.SHIELD_OF_FAITH,
                    spell_2=PaladinLevel1Spells.THUNDEROUS_SMITE,
                ),
                2: PaladinLevel2(
                    fighting_style=FightingStyles.Defense(),
                    spell=PaladinLevel1Spells.COMPELLED_DUEL,
                ),
                3: PaladinLevel3(
                    spell=PaladinLevel1Spells.BLESS,
                ),
            },
            subclass_features_by_level={
                3: GloryPaladinLevel3(),
            },
        ),
        replace_spells={},
    )


class RodericAshelmCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Roderic Ashelm",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.SURVIVAL,
                origin_feat=OriginFeats.Lucky(),
            ),
        )
