from Definitions import Ability, Skill, CharacterClass, PaladinSubclass
from Features import GeneralFeats
import CharacterSheetCreator
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import PaladinFeatures
import StatBlocks

DATA = CharacterSheetCreator.CharacterSheetData()

##########################################
# ================ CHANGE ============== #
##########################################

# ================ GENERAL ============= #

DATA.character_name = "Vengeance"
DATA.character_class = CharacterClass.PALADIN
DATA.level = 6
DATA.character_subclass = PaladinSubclass.OATH_OF_VENGEANCE
DATA.spell_casting_ability = Ability.CHARISMA
DATA.add_feature(PaladinFeatures.SpellSlots())

# ================ LEVEL 0 ============= #

# Distribute 15, 14, 13, 12, 10, 8 among your abilities.
DATA.abilities = StatBlocks.StandardArrayAbilitiesStatBlock(
    strength=15,
    dexterity=10,
    constitution=14,
    intelligence=12,
    wisdom=8,
    charisma=13,
)

# Choose two skills to be proficient in
DATA.skills = StatBlocks.PaladinSkillsStatBlock(
    proficiencies={
        Skill.ATHLETICS: False,
        Skill.INSIGHT: True,
        Skill.INTIMIDATION: True,
        Skill.MEDICINE: False,
        Skill.PERSUASION: False,
        Skill.RELIGION: False,
    }
)

# Leave as is: Paladin specific saving throws
DATA.saving_throws = StatBlocks.PaladinSavingThrowsStatBlock()

# Leave as is: Paladin specific combat stats
DATA.hit_die = PaladinFeatures.PALADIN_HIT_DIE
DATA.speed = 30

DATA.add_feature(
    # Free background feature
    # Distribute +2 and +1 to two different ability scores
    # OR +1 to three different ability scores
    Backgrounds.FreeBackgroundAbilityBonus(
        [
            (Ability.STRENGTH, 2),
            (Ability.CONSTITUTION, 1),
        ]
    )
)

# Starting armor
DATA.add_armor(Armor.ChainMailArmor())
# DATA.add_armor(Armor.ShieldArmor())

# Starting weapons
# DATA.add_weapon(Weapons.Longsword(player_is_proficient=True))
# DATA.add_weapon(Weapons.Javelin(player_is_proficient=True))


# ================ LEVEL 1 ============= #
if DATA.level >= 1:
    # Weapon Mastery: Choose two proficient weapon types to use their mastery properties.
    # You can change your choices after a Long Rest.
    DATA.add_weapon_mastery(Weapons.Handaxe)
    DATA.add_weapon_mastery(Weapons.LightHammer)
    DATA.add_feature(PaladinFeatures.LayOnHands())

    # Add/Change prepared spells:
    DATA.add_spell("Cure Wounds")
    DATA.add_spell("Divine Favor")


# ================ LEVEL 2 ============= #
if DATA.level >= 2:
    # Choose one Fighting Style
    DATA.add_fighting_style(FightingStyles.TwoWeaponFighting())

    # Automatic feature
    DATA.add_feature(PaladinFeatures.PaladinsSmite())
    DATA.add_spell("Divine Smite")

    # Add/Change prepared spells:
    DATA.add_spell("Shield of Faith")

# ================ LEVEL 3 ============= #
if DATA.level >= 3:
    # Automatic feature
    channel_divinity_feature = PaladinFeatures.ChannelDivinityFeature()
    channel_divinity_feature.add_spell("Divine Sense")

    # Automatic feature
    if DATA.character_subclass == PaladinSubclass.OATH_OF_DEVOTION:
        DATA.add_spell("Protection from Evil and Good")
        DATA.add_spell("Shield of Faith")

    # Automatic feature
    if DATA.character_subclass == PaladinSubclass.OATH_OF_VENGEANCE:
        DATA.add_spell("Bane")
        DATA.add_spell("Hunter's Mark")
        channel_divinity_feature.add_spell("Vow of Enmity")

    # Add/Change prepared spells:
    DATA.add_spell("Bless")

# ================ LEVEL 4 ============= #
if DATA.level >= 4:
    # Choose one ability score to increase by 2
    # OR two ability scores to increase by 1 each
    DATA.add_feature(
        GeneralFeats.AbilityScoreImprovement(
            [
                (Ability.STRENGTH, 1),
                (Ability.CONSTITUTION, 1),
            ]
        )
    )

    # Add/Change prepared spells:
    # DATA.add_spell("Restoration")

# ================ LEVEL 5 ============= #
if DATA.level >= 5:
    # Automatic feature
    DATA.add_feature(PaladinFeatures.ExtraAttack())
    DATA.add_feature(PaladinFeatures.FaithfulSteed())
    DATA.add_spell("Find Steed")

    # Automatic feature
    if DATA.character_subclass == PaladinSubclass.OATH_OF_VENGEANCE:
        DATA.add_spell("Hold Person")
        DATA.add_spell("Misty Step")

    # Add/Change prepared spells:
    DATA.add_spell("Dispel Magic")

# ================ LEVEL 6 ============= #
if DATA.level >= 6:
    # Automatic feature
    DATA.add_feature(PaladinFeatures.AuraOfProtection())


##########################################
# ========== MANUAL ADDITIONS ========== #
##########################################

DATA.add_weapon(Weapons.Handaxe(player_is_proficient=True))
DATA.add_weapon(Weapons.LightHammer(player_is_proficient=True))

##########################################
# ============ LEAVE AS IS ============= #
##########################################

DATA.add_feature(channel_divinity_feature)
