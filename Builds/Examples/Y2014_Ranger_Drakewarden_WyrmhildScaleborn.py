"""Example build: Ranger Drakewarden (2014 rules). Demonstrates the subclass up through level 17."""

from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
    RangerLevel4,
    RangerLevel5,
    RangerLevel6,
    RangerLevel7,
    RangerLevel8,
    RangerLevel9,
    RangerLevel10,
    RangerLevel11,
    RangerLevel12,
    RangerLevel13,
    RangerLevel14,
    RangerLevel15,
    RangerLevel16,
    RangerLevel17,
)
from CharacterContent.Classes.SubClasses2014.RangerDrakewarden import (
    RangerDrakewardenLevel3,
    RangerDrakewardenLevel7,
    RangerDrakewardenLevel11,
    RangerDrakewardenLevel15,
    RangerDrakewardenCustomStarterClassArgs,
)
from Core.Definitions import Ability, DamageType, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Weapons
from CharacterContent.Species import Human
from CharacterContent.Spells.SpellLists import RangerLevel1Spells, RangerLevel2Spells, RangerLevel3Spells, RangerLevel4Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerDrakewardenCustomStarterClassArgs(
            skills=RangerSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: True,
                    Skill.ATHLETICS: True,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: False,
                    Skill.NATURE: True,
                    Skill.PERCEPTION: False,
                    Skill.STEALTH: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=17,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=12,
            dexterity=14,
            constitution=13,
            intelligence=8,
            wisdom=15,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SURVIVAL,
                Skill.ARCANA,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Tough(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    spell_1=RangerLevel1Spells.CURE_WOUNDS,
                    spell_2=RangerLevel1Spells.ENSNARING_STRIKE,
                ),
                2: RangerLevel2(
                    skill_expertise=Skill.ANIMAL_HANDLING,
                    fighting_style=FightingStyles.Dueling(),
                    spell=RangerLevel1Spells.LONGSTRIDER,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.GOODBERRY,
                ),
                4: RangerLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.WISDOM, 1),
                            (Ability.CONSTITUTION, 1),
                        ]),
                    spell=RangerLevel1Spells.ENTANGLE,
                ),
                5: RangerLevel5(
                    spell=RangerLevel2Spells.BARKSKIN,
                ),
                6: RangerLevel6(),
                7: RangerLevel7(
                    spell=RangerLevel2Spells.SPIKE_GROWTH,
                ),
                8: RangerLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.WISDOM, 1),
                            (Ability.STRENGTH, 1),
                        ]),
                ),
                9: RangerLevel9(
                    skill_expertise_1=Skill.ATHLETICS,
                    skill_expertise_2=Skill.NATURE,
                    spell_1=RangerLevel3Spells.CONJURE_ANIMALS,
                    spell_2=RangerLevel2Spells.LESSER_RESTORATION,
                ),
                10: RangerLevel10(),
                11: RangerLevel11(
                    spell=RangerLevel3Spells.LIGHTNING_ARROW,
                ),
                12: RangerLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.WISDOM, 1),
                            (Ability.CONSTITUTION, 1),
                        ]),
                ),
                13: RangerLevel13(
                    spell=RangerLevel4Spells.LOCATE_CREATURE,
                ),
                14: RangerLevel14(),
                15: RangerLevel15(
                    spell=RangerLevel4Spells.GUARDIAN_OF_NATURE,
                ),
                16: RangerLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.WISDOM, 1),
                            (Ability.STRENGTH, 1),
                        ]),
                ),
                17: RangerLevel17(
                    spell_1=RangerLevel2Spells.GUST_OF_WIND,
                    spell_2=RangerLevel3Spells.WATER_WALK,
                ),
            },
            subclass_features_by_level={
                3: RangerDrakewardenLevel3(
                    damage_type=DamageType.FIRE,
                    language="Ignan",
                ),
                7: RangerDrakewardenLevel7(),
                11: RangerDrakewardenLevel11(),
                15: RangerDrakewardenLevel15(),
            },
        ),
        replace_spells={},
    )


class Y2014RangerDrakewardenWyrmhildScalebornCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Wyrmhild Scaleborn",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                skill_proficiency=Skill.INSIGHT,
                origin_feat=OriginFeats.Alert(),
            ),
        )
