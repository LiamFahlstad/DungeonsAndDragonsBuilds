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
from Spells.Definitions import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
    WarlockLevel2Spells,
)


@attr.dataclass
class PaladinLevel1:
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon
    spell_1: PaladinLevel1Spells
    spell_2: PaladinLevel1Spells


@attr.dataclass
class PaladinLevel2:
    fighting_style: FightingStyles.FightingStyle
    spell: PaladinLevel1Spells


@attr.dataclass
class PaladinLevel3:
    spell: PaladinLevel1Spells


@attr.dataclass
class PaladinLevel4:
    general_feat: GeneralFeats.GeneralFeat
    spell: PaladinLevel1Spells


@attr.dataclass
class PaladinLevel5:
    spell: PaladinLevel1Spells | PaladinLevel2Spells


def get_character_sheet_creator_base(
    paladin_level: int,
    abilities: AbilitiesStatBlock,
    skills: PaladinSkillsStatBlock,
    background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
    background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
    add_default_equipment: bool,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
    armor: list[Armor.AbstractArmor] = None,
    weapons: list[Weapons.AbstractWeapon] = None,
):
    data = CharacterSheetCreator.CharacterSheetData(
        character_class=CharacterClass.PALADIN,
        level=paladin_level,
        abilities=abilities,
        skills=skills,
        saving_throws=PaladinSavingThrowsStatBlock(),
        hit_die=PaladinFeatures.PALADIN_HIT_DIE,
        spell_casting_ability=Ability.CHARISMA,
    )

    # ================ LEVEL 0 ============= #
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

    return data


def get_level_1_features(
    paladin_level_1: PaladinLevel1, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    # Weapon Mastery: Choose two proficient weapon types to use their mastery properties.
    # You can change your choices after a Long Rest.
    data.add_weapon_mastery(paladin_level_1.weapon_mastery_1)
    data.add_weapon_mastery(paladin_level_1.weapon_mastery_2)

    # Lay on Hands
    data.add_feature(PaladinFeatures.LayOnHands())

    # Add/Change prepared spells:
    data.add_spell(paladin_level_1.spell_1)
    data.add_spell(paladin_level_1.spell_2)
    return data


def get_level_2_features(
    paladin_level_2: PaladinLevel2, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    # Choose one Fighting Style
    data.add_fighting_style(paladin_level_2.fighting_style)

    # Automatic feature
    data.add_feature(PaladinFeatures.PaladinsSmite())
    data.add_spell(PaladinLevel1Spells.DIVINE_SMITE)

    # Add prepared spells:
    data.add_spell(paladin_level_2.spell)
    return data


def get_level_3_features(
    paladin_level_3: PaladinLevel3, data: CharacterSheetCreator.CharacterSheetData
) -> tuple[
    CharacterSheetCreator.CharacterSheetData, PaladinFeatures.ChannelDivinityFeature
]:

    # Automatic feature
    channel_divinity_feature = PaladinFeatures.ChannelDivinityFeature()
    channel_divinity_feature.add_spell("Divine Sense")

    # Add prepared spells:
    data.add_spell(paladin_level_3.spell)
    return data, channel_divinity_feature


def get_level_4_features(
    paladin_level_4: PaladinLevel4, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    data.add_feature(paladin_level_4.general_feat)
    data.add_spell(paladin_level_4.spell)
    return data


def get_level_5_features(
    paladin_level_5: PaladinLevel5, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    # Automatic feature
    data.add_feature(PaladinFeatures.ExtraAttack())
    data.add_feature(PaladinFeatures.FaithfulSteed())
    data.add_spell(PaladinLevel2Spells.FIND_STEED)

    # Oath of vengeance features
    data.add_spell(WarlockLevel2Spells.HOLD_PERSON)
    data.add_spell(WarlockLevel2Spells.MISTY_STEP)

    # Add/Change prepared spells:
    data.add_spell(paladin_level_5.spell)
    return data
