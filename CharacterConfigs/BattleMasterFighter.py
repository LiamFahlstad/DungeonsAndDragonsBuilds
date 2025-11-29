from Definitions import Ability, Skill, CharacterClass, FighterSubclass
from Features import BaseFeatures, GeneralFeats, Maneuvers, OriginFeats
import CharacterSheetCreator
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import FighterFeatures
import StatBlocks

DATA = CharacterSheetCreator.CharacterSheetData()

##########################################
# ================ CHANGE ============== #
##########################################

# ================ GENERAL ============= #

DATA.character_class = CharacterClass.FIGHTER
DATA.level = 5
DATA.character_subclass = FighterSubclass.BATTLE_MASTER

# ================ LEVEL 0 ============= #

# Distribute 15, 14, 13, 12, 10, 8 among your abilities.
DATA.abilities = StatBlocks.StandardArrayAbilitiesStatBlock(
    strength=14,
    dexterity=12,
    constitution=15,
    intelligence=8,
    wisdom=10,
    charisma=13,
)

# Choose two skills to be proficient in
DATA.skills = StatBlocks.FighterSkillsStatBlock(
    proficiencies={
        Skill.ACROBATICS: True,
        Skill.ANIMAL_HANDLING: False,
        Skill.ATHLETICS: True,
        Skill.HISTORY: False,
        Skill.INSIGHT: False,
        Skill.INTIMIDATION: False,
        Skill.PERCEPTION: False,
        Skill.SURVIVAL: False,
    }
)

# Leave as is: Paladin specific saving throws
DATA.saving_throws = StatBlocks.FighterSavingThrowsStatBlock()

# Leave as is: Paladin specific combat stats
DATA.hit_die = FighterFeatures.FIGHTER_HIT_DIE

DATA.add_feature(
    # Free background feature
    # Distribute +2 and +1 to two different ability scores
    # OR +1 to three different ability scores
    Backgrounds.FreeBackgroundAbilityBonus(
        [
            (Ability.STRENGTH, 1),
            (Ability.CONSTITUTION, 2),
        ]
    )
)

DATA.add_feature(
    # Free background feature
    # Distribute +2 and +1 to two different ability scores
    # OR +1 to three different ability scores
    Backgrounds.FreeBackgroundSkillProficiency(
        [
            Skill.INTIMIDATION,
            Skill.PERSUASION,
        ]
    )
)

# Starting armor
DATA.add_armor(Armor.ChainMailArmor())
DATA.add_armor(Armor.ShieldArmor())

# Starting weapons
DATA.add_weapon(Weapons.Longsword(player_is_proficient=True))
DATA.add_weapon(Weapons.Javelin(player_is_proficient=True))

# Origin feat
DATA.add_feature(OriginFeats.Tough())


# ================ LEVEL 1 ============= #
if DATA.level >= 1:
    # 3 weapon masteries
    DATA.add_weapon_mastery(Weapons.Longsword)
    DATA.add_weapon_mastery(Weapons.Flail)
    DATA.add_weapon_mastery(Weapons.Greatsword)

    # 1 fighting style
    DATA.add_fighting_style(FightingStyles.Defense())

    # Automatic feature
    DATA.add_feature(FighterFeatures.SecondWind())

# ================ LEVEL 2 ============= #
if DATA.level >= 2:
    # Automatic feature
    DATA.add_feature(FighterFeatures.ActionSurge())

# ================ LEVEL 3 ============= #
if DATA.level >= 3:
    # Automatic feature
    if DATA.character_subclass == FighterSubclass.BATTLE_MASTER:
        superiority_dice = FighterFeatures.SuperiorityDice()
        superiority_dice.add_maneuver(Maneuvers.GoadingAttack())
        superiority_dice.add_maneuver(Maneuvers.PushingAttack())
        superiority_dice.add_maneuver(Maneuvers.Riposte())

# ================ LEVEL 4 ============= #
if DATA.level >= 4:
    # Automatic feature
    DATA.add_feature(
        GeneralFeats.AbilityScoreImprovement(
            [
                (Ability.STRENGTH, 1),
                (Ability.CONSTITUTION, 1),
            ]
        )
    )

# ================ LEVEL 4 ============= #
if DATA.level >= 5:
    # Automatic feature
    DATA.add_feature(FighterFeatures.ExtraAttack())

##########################################
# ========== MANUAL ADDITIONS ========== #
##########################################

# DATA.add_weapon(Weapons.Handaxe(player_is_proficient=True))
# DATA.add_weapon(Weapons.LightHammer(player_is_proficient=True))

##########################################
# ============ LEAVE AS IS ============= #
##########################################

if DATA.level >= 3 and DATA.character_subclass == FighterSubclass.BATTLE_MASTER:
    DATA.add_feature(superiority_dice)
