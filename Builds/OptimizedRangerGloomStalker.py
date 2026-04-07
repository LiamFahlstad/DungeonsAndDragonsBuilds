from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerLevel1,
    RangerLevel2,
    RangerLevel3,
)
from CharacterConfigs.SubClasses.RangerGloomStalker import (
    RangerGloomStalkerLevel3,
    RangerGloomStalkerNonGenericStarterClassArgs,
)
from Definitions import Ability, Skill
from Features import Backgrounds, FightingStyles, OriginFeats, Weapons
from Features.SpeciesFeatures import DragonbornFeatures
from SpeciesConfigs import Dragonborn
from Spells.Definitions import RangerLevel1Spells
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=RangerGloomStalkerNonGenericStarterClassArgs(
            skills=RangerSkillsStatBlock(
                proficiencies={
                    Skill.ANIMAL_HANDLING: False,
                    Skill.ATHLETICS: False,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: True,
                    Skill.NATURE: False,
                    Skill.PERCEPTION: True,
                    Skill.STEALTH: True,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=13,
            intelligence=12,
            wisdom=14,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.WISDOM, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SLEIGHT_OF_HAND,
                Skill.SURVIVAL,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: RangerLevel1(
                    weapon_mastery_1=Weapons.Longbow(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    spell_1=RangerLevel1Spells.ENSNARING_STRIKE,
                    spell_2=RangerLevel1Spells.FOG_CLOUD,
                ),
                2: RangerLevel2(
                    skill=Skill.STEALTH,
                    fighting_style=FightingStyles.Archery(),
                    spell=RangerLevel1Spells.ENTANGLE,
                ),
                3: RangerLevel3(
                    spell=RangerLevel1Spells.JUMP,
                ),
            },
            subclass_features_by_level={
                3: RangerGloomStalkerLevel3(),
            },
        ),
        replace_spells={},
    )


class OptimizedRangerGloomStalkerCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Ranger Gloom Stalker",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dragonborn.DragonbornSpeciesBuilder(
                DragonbornFeatures.DragonColor.RED
            ),
        )
