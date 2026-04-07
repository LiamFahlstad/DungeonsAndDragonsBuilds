from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.FighterBase import (
    FighterLevel1,
    FighterLevel2,
    FighterLevel3,
    FighterLevel4,
    FighterLevel5,
)
from CharacterConfigs.SubClasses.FighterChampion import (
    FighterChampionLevel3,
    FighterChampionStarterClassBuilder,
)
from Definitions import Ability, Skill
from Features import (
    Armor,
    Backgrounds,
    FightingStyles,
    GeneralFeats,
    Maneuvers,
    OriginFeats,
    Weapons,
)
from Items import Items
from SpeciesConfigs import Dwarf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


def get_starter_class_builder():
    return FighterChampionStarterClassBuilder(
        fighter_level=3,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=8,
            wisdom=12,
            charisma=10,
        ),
        # Choose two skills to be proficient in
        fighter_skills=FighterSkillsStatBlock(
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
            Weapons.Shortsword(player_is_proficient=True),
            Weapons.Scimitar(player_is_proficient=True),
            Weapons.Longbow(player_is_proficient=True),
        ],
        items=[
            (Items.RobeOfLevitation(), 1),
        ],
        fighter_level_features=ClassBuilder.BaseClassLevelFeatures(
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
                    general_feat=GeneralFeats.Sentinel(
                        character_level=4,
                        ability=Ability.STRENGTH,
                    ),
                ),
                5: FighterLevel5(),
            },
            subclass_features_by_level={
                3: FighterChampionLevel3(
                    maneuver_1=Maneuvers.GoadingAttack(),
                    maneuver_2=Maneuvers.PushingAttack(),
                    maneuver_3=Maneuvers.Riposte(),
                ),
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
