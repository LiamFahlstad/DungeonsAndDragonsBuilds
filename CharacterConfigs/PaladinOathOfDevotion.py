import attr
from Definitions import Ability, PaladinSubclass, Skill, CharacterClass, FighterSubclass
from Features import BaseFeatures, GeneralFeats, Maneuvers, OriginFeats
import CharacterSheetCreator
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import FighterFeatures, PaladinFeatures
from StatBlocks.AbilitiesStatBlock import (
    StandardArrayAbilitiesStatBlock,
    AbilitiesStatBlock,
)
from StatBlocks.SavingThrowsStatBlock import PaladinSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class PaladinLevel1:
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon
    spell_1: str
    spell_2: str


@attr.dataclass
class PaladinLevel2:
    fighting_style: FightingStyles.FightingStyle
    spell: str


@attr.dataclass
class PaladinLevel3:
    spell: str


@attr.dataclass
class PaladinLevel4:
    general_feat: GeneralFeats.GeneralFeat
    spell: str


@attr.dataclass
class PaladinLevel5:
    spell: str


def create(
    paladin_level: int,
    abilities: AbilitiesStatBlock,
    skills: PaladinSkillsStatBlock,
    background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
    background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
    add_default_equipment: bool,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
    armor: list[Armor.AbstractArmor] = None,
    weapons: list[Weapons.AbstractWeapon] = None,
    paladin_level_1: PaladinLevel1 = None,
    paladin_level_2: PaladinLevel2 = None,
    paladin_level_3: PaladinLevel3 = None,
    paladin_level_4: PaladinLevel4 = None,
    paladin_level_5: PaladinLevel5 = None,
) -> CharacterSheetCreator.CharacterSheetData:

    if not isinstance(skills, PaladinSkillsStatBlock):
        raise ValueError("skills must be an instance of PaladinSkillsStatBlock")

    data = CharacterSheetCreator.CharacterSheetData(
        character_class=CharacterClass.PALADIN,
        level=paladin_level,
        character_subclass=PaladinSubclass.OATH_OF_DEVOTION.value,
        abilities=abilities,
        skills=skills,
        saving_throws=PaladinSavingThrowsStatBlock(),
        hit_die=PaladinFeatures.PALADIN_HIT_DIE,
        spell_casting_ability=Ability.CHARISMA,
    )

    # ================ LEVEL 0 ============= #
    channel_divinity_feature = None
    data.add_feature(PaladinFeatures.SpellSlots())
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
    if paladin_level >= 1:
        if paladin_level_1 is None:
            raise ValueError("paladin_level_1 must be provided for level 1 features.")
        # Weapon Mastery: Choose two proficient weapon types to use their mastery properties.
        # You can change your choices after a Long Rest.
        data.add_weapon_mastery(paladin_level_1.weapon_mastery_1)
        data.add_weapon_mastery(paladin_level_1.weapon_mastery_2)

        # Lay on Hands
        data.add_feature(PaladinFeatures.LayOnHands())

        # Add/Change prepared spells:
        data.add_spell(paladin_level_1.spell_1)
        data.add_spell(paladin_level_1.spell_2)

    # ================ LEVEL 2 ============= #
    if paladin_level >= 2:
        if paladin_level_2 is None:
            raise ValueError("paladin_level_2 must be provided for level 2 features.")

        # Choose one Fighting Style
        data.add_fighting_style(paladin_level_2.fighting_style)

        # Automatic feature
        data.add_feature(PaladinFeatures.PaladinsSmite())
        data.add_spell("Divine Smite")

        # Add prepared spells:
        data.add_spell(paladin_level_2.spell)

    # ================ LEVEL 3 ============= #
    if paladin_level >= 3:
        if paladin_level_3 is None:
            raise ValueError("paladin_level_3 must be provided for level 3 features.")

        # Automatic feature
        channel_divinity_feature = PaladinFeatures.ChannelDivinityFeature()
        channel_divinity_feature.add_spell("Divine Sense")

        # Oath of devotion features
        data.add_spell("Protection from Evil and Good")
        data.add_spell("Shield of Faith")

        # Add prepared spells:
        data.add_spell(paladin_level_3.spell)

    # ================ LEVEL 4 ============= #
    if paladin_level >= 4:
        if paladin_level_4 is None:
            raise ValueError("paladin_level_4 must be provided for level 4 features.")
        data.add_feature(paladin_level_4.general_feat)
        data.add_spell(paladin_level_4.spell)

    # ================ LEVEL 5 ============= #
    if paladin_level >= 5:
        # Automatic feature
        data.add_feature(PaladinFeatures.ExtraAttack())
        data.add_feature(PaladinFeatures.FaithfulSteed())
        data.add_spell("Find Steed")

        # Oath of vengeance features
        data.add_spell("Hold Person")
        data.add_spell("Misty Step")

        # Add/Change prepared spells:
        data.add_spell(paladin_level_5.spell)

    # ================ LEVEL 6 ============= #
    if paladin_level >= 6:
        # Automatic feature
        data.add_feature(PaladinFeatures.AuraOfProtection())

    ##########################################
    # ============ LEAVE AS IS ============= #
    ##########################################

    if channel_divinity_feature is not None:
        data.add_feature(channel_divinity_feature)

    return data
