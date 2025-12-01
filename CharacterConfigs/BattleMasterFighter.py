from pyexpat import features
import attr
from Definitions import Ability, Skill, CharacterClass, FighterSubclass
from Features import BaseFeatures, GeneralFeats, Maneuvers, OriginFeats
import CharacterSheetCreator
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import FighterFeatures
from StatBlocks.AbilitiesStatBlock import (
    StandardArrayAbilitiesStatBlock,
    AbilitiesStatBlock,
)
from StatBlocks.SavingThrowsStatBlock import FighterSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterLevel1:
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon
    weapon_mastery_3: Weapons.AbstractWeapon
    fighting_style: FightingStyles.FightingStyle


@attr.dataclass
class FighterLevel3:
    maneuver_1: Maneuvers.Maneuver
    maneuver_2: Maneuvers.Maneuver
    maneuver_3: Maneuvers.Maneuver


@attr.dataclass
class FighterLevel4:
    general_feat: GeneralFeats.GeneralFeat


def create_battle_master_fighter_data(
    fighter_level: int,
    abilities: AbilitiesStatBlock,
    skills: FighterSkillsStatBlock,
    background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
    background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
    add_default_equipment: bool,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
    armor: list[Armor.AbstractArmor] = None,
    weapons: list[Weapons.AbstractWeapon] = None,
    fighter_level_1: FighterLevel1 = None,
    fighter_level_3: FighterLevel3 = None,
    fighter_level_4: FighterLevel4 = None,
) -> CharacterSheetCreator.CharacterSheetData:

    if not isinstance(skills, FighterSkillsStatBlock):
        raise ValueError("skills must be an instance of FighterSkillsStatBlock")

    data = CharacterSheetCreator.CharacterSheetData(
        character_class=CharacterClass.FIGHTER,
        level=fighter_level,
        character_subclass=FighterSubclass.BATTLE_MASTER.value,
        abilities=abilities,
        skills=skills,
        saving_throws=FighterSavingThrowsStatBlock(),
        hit_die=FighterFeatures.FIGHTER_HIT_DIE,
    )

    # ================ LEVEL 0 ============= #
    superiority_dice = None
    data.add_feature(background_ability_bonuses)
    data.add_feature(background_skill_proficiencies)

    ### Equipment ###

    if add_default_equipment:
        # Starting armor
        data.add_armor(Armor.ChainMailArmor())
        data.add_armor(Armor.ShieldArmor())

        # Starting weapons
        data.add_weapon(Weapons.Longsword(player_is_proficient=True))
        data.add_weapon(Weapons.Javelin(player_is_proficient=True))

    if armor is not None:
        for a in armor:
            data.add_armor(a)

    if weapons is not None:
        for w in weapons:
            data.add_weapon(w)

    # Origin feat
    data.add_feature(origin_feat)

    # ================ LEVEL 1 ============= #
    if fighter_level >= 1:
        if fighter_level_1 is None:
            raise ValueError("fighter_level_1 must be provided for level 1 features.")

        # 3 weapon masteries
        data.add_weapon_mastery(fighter_level_1.weapon_mastery_1)
        data.add_weapon_mastery(fighter_level_1.weapon_mastery_2)
        data.add_weapon_mastery(fighter_level_1.weapon_mastery_3)

        # 1 fighting style
        data.add_fighting_style(fighter_level_1.fighting_style)

        # Automatic feature
        data.add_feature(FighterFeatures.SecondWind())

    # ================ LEVEL 2 ============= #
    if fighter_level >= 2:
        data.add_feature(FighterFeatures.ActionSurge())

    # ================ LEVEL 3 ============= #
    if fighter_level >= 3:
        if fighter_level_3 is None:
            raise ValueError("fighter_level_3 must be provided for level 3 features.")
        if data.character_subclass == FighterSubclass.BATTLE_MASTER:
            superiority_dice = FighterFeatures.SuperiorityDice()
            superiority_dice.add_maneuver(fighter_level_3.maneuver_1)
            superiority_dice.add_maneuver(fighter_level_3.maneuver_2)
            superiority_dice.add_maneuver(fighter_level_3.maneuver_3)

    # ================ LEVEL 4 ============= #
    if fighter_level >= 4:
        if fighter_level_4 is None:
            raise ValueError("fighter_level_4 must be provided for level 4 features.")
        data.add_feature(fighter_level_4.general_feat)

    # ================ LEVEL 4 ============= #
    if fighter_level >= 5:
        data.add_feature(FighterFeatures.ExtraAttack())

    ##########################################
    # ============ LEAVE AS IS ============= #
    ##########################################

    if superiority_dice is not None:
        data.add_feature(superiority_dice)

    return data
