from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
    FighterLevel5,
)
from CharacterContent.Classes.SubClasses2024.FighterChampion import (
    FighterChampionCustomStarterClassArgs,
    FighterChampionLevel3,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Items
from CharacterContent.Species import Dwarf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=FighterChampionCustomStarterClassArgs(
            skills=FighterSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ANIMAL_HANDLING: True,
                    Skill.ATHLETICS: False,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INTIMIDATION: False,
                    Skill.PERCEPTION: False,
                    Skill.SURVIVAL: False,
                }
            ),
        ),
        base_class_level=4,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.DEXTERITY, 1),
                (Ability.STRENGTH, 2),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INTIMIDATION,
                Skill.ATHLETICS,
            ]
        ),
        add_default_equipment=False,
        origin_feat=OriginFeats.SavageAttacker(),
        armor=[
            Armor.LeatherArmor(),
        ],
        weapons=[
            Weapons.Shortsword(),
            Weapons.Scimitar(),
            Weapons.Longbow(),
        ],
        items=[(Items.RobeOfLevitation(), 1), (Items.HobbyHorse(), 1)],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: FighterLevel1(
                    weapon_mastery_1=Weapons.Shortsword(),
                    weapon_mastery_2=Weapons.Scimitar(),
                    weapon_mastery_3=Weapons.Longbow(),
                    fighting_style=FightingStyles.Archery(),
                ),
                2: FighterLevel2(),
                3: FighterLevel3(),
                4: FighterLevel4(
                    weapon_mastery=Weapons.Handaxe(),
                    general_feat=GeneralFeats.MountedCombatant(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    ),
                ),
                5: FighterLevel5(),
            },
            subclass_features_by_level={
                3: FighterChampionLevel3(),
            },
        ),
    )


class OptimizedFighterChampionCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Optimized Fighter Champion",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Dwarf.DwarfSpeciesBuilder(),
        )
