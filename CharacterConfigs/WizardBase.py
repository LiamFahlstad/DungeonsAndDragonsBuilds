import attr
from Definitions import Ability, CharacterClass
from Features import BaseFeatures, GeneralFeats, Maneuvers, OriginFeats
import CharacterSheetCreator
from Features import Armor
from Features import Backgrounds
from Features import FightingStyles
from Features import Weapons
from Features.ClassFeatures import FighterFeatures, WizardFeatures, WizardFeatures
from Features.ClassFeatures import SpellSlots
from StatBlocks.AbilitiesStatBlock import (
    StandardArrayAbilitiesStatBlock,
    AbilitiesStatBlock,
)
from StatBlocks.SavingThrowsStatBlock import WizardSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock
from Spells.Definitions import (
    WizardLevel0Spells,
    WizardLevel1Spells,
    WizardLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
    WarlockLevel2Spells,
)


@attr.dataclass
class WizardLevel1:
    cantrip_1: WizardLevel0Spells
    cantrip_2: WizardLevel0Spells
    cantrip_3: WizardLevel0Spells
    spell_1: WizardLevel1Spells
    spell_2: WizardLevel1Spells
    spell_3: WizardLevel1Spells
    spell_4: WizardLevel1Spells


@attr.dataclass
class WizardLevel2:
    fighting_style: FightingStyles.FightingStyle
    spell: WizardLevel1Spells


@attr.dataclass
class WizardLevel3:
    spell: WizardLevel1Spells


@attr.dataclass
class WizardLevel4:
    general_feat: GeneralFeats.GeneralFeat
    spell: WizardLevel1Spells


@attr.dataclass
class WizardLevel5:
    spell: WizardLevel1Spells | WizardLevel2Spells


@attr.dataclass
class WizardLevel7:
    spell: WizardLevel1Spells | WizardLevel2Spells


@attr.dataclass
class WizardLevel8:
    general_feat: GeneralFeats.GeneralFeat


@attr.dataclass
class WizardLevel9:
    spell: WizardLevel1Spells | WizardLevel2Spells | WizardLevel3Spells


@attr.dataclass
class WizardLevel11:
    spell: WizardLevel1Spells | WizardLevel2Spells | WizardLevel3Spells


@attr.dataclass
class WizardLevel12:
    general_feat: GeneralFeats.GeneralFeat


@attr.dataclass
class WizardLevel13:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
    )


@attr.dataclass
class WizardLevel15:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
    )


@attr.dataclass
class WizardLevel16:
    general_feat: GeneralFeats.GeneralFeat


@attr.dataclass
class WizardLevel17:
    spell_1: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
    )
    spell_2: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
    )


@attr.dataclass
class WizardLevel19:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
    )


def get_character_sheet_creator_base(
    wizard_level: int,
    abilities: AbilitiesStatBlock,
    skills: WizardSkillsStatBlock,
    background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
    background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
    add_default_equipment: bool,
    origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
    armor: list[Armor.AbstractArmor] = None,
    weapons: list[Weapons.AbstractWeapon] = None,
):
    data = CharacterSheetCreator.CharacterSheetData(
        character_class=CharacterClass.WIZARD,
        level=wizard_level,
        abilities=abilities,
        skills=skills,
        saving_throws=WizardSavingThrowsStatBlock(),
        hit_die=WizardFeatures.WIZARD_HIT_DIE,
        spell_casting_ability=Ability.INTELLIGENCE,
    )

    # ================ LEVEL 0 ============= #
    data.add_feature(SpellSlots.SpellSlots(SpellSlots.CasterType.FULL_CASTER))
    data.add_feature(background_ability_bonuses)
    data.add_feature(background_skill_proficiencies)

    ### Equipment ###

    if add_default_equipment:
        # Starting armor
        # No starting armor for Wizards

        # Starting weapons
        data.add_weapon(Weapons.Dagger(player_is_proficient=True))
        data.add_weapon(Weapons.Quarterstaff(player_is_proficient=True))

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
    wizard_level_1: WizardLevel1, data: CharacterSheetCreator.CharacterSheetData
) -> tuple[CharacterSheetCreator.CharacterSheetData, WizardFeatures.LayOnHands]:
    # Lay on Hands
    lay_on_hands = WizardFeatures.LayOnHands()

    # Add/Change prepared cantrips:
    data.add_cantrip(wizard_level_1.cantrip_1)
    data.add_cantrip(wizard_level_1.cantrip_2)
    data.add_cantrip(wizard_level_1.cantrip_3)

    # Add/Change prepared spells:
    data.add_spell(wizard_level_1.spell_1)
    data.add_spell(wizard_level_1.spell_2)
    data.add_spell(wizard_level_1.spell_3)
    data.add_spell(wizard_level_1.spell_4)
    return data, lay_on_hands


def get_level_2_features(
    wizard_level_2: WizardLevel2, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    # Choose one Fighting Style
    data.add_fighting_style(wizard_level_2.fighting_style)

    # Automatic feature
    data.add_feature(WizardFeatures.WizardsSmite())
    data.add_spell(WizardLevel1Spells.DIVINE_SMITE)

    # Add prepared spells:
    data.add_spell(wizard_level_2.spell)
    return data


def get_level_3_features(
    wizard_level_3: WizardLevel3, data: CharacterSheetCreator.CharacterSheetData
) -> tuple[
    CharacterSheetCreator.CharacterSheetData, WizardFeatures.ChannelDivinityFeature
]:

    # Automatic feature
    channel_divinity_feature = WizardFeatures.ChannelDivinityFeature()
    channel_divinity_feature.add_spell("Divine Sense")

    # Add prepared spells:
    data.add_spell(wizard_level_3.spell)
    return data, channel_divinity_feature


def get_level_4_features(
    wizard_level_4: WizardLevel4, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    data.add_feature(wizard_level_4.general_feat)
    data.add_spell(wizard_level_4.spell)
    return data


def get_level_5_features(
    wizard_level_5: WizardLevel5, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    # Automatic feature
    data.add_feature(WizardFeatures.ExtraAttack())
    data.add_feature(WizardFeatures.FaithfulSteed())
    data.add_spell(WizardLevel2Spells.FIND_STEED)

    # Oath of vengeance features
    data.add_spell(WarlockLevel2Spells.HOLD_PERSON)
    data.add_spell(WarlockLevel2Spells.MISTY_STEP)

    # Add/Change prepared spells:
    data.add_spell(wizard_level_5.spell)
    return data


def get_level_6_features():
    # Automatic feature
    return WizardFeatures.AuraOfProtection()


def get_level_8_features(
    wizard_level_8: WizardLevel8, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    data.add_feature(wizard_level_8.general_feat)
    return data


def get_level_9_features(
    channel_divinity_feature: WizardFeatures.ChannelDivinityFeature,
):
    channel_divinity_feature.add_spell("Abjure Foes")
    return channel_divinity_feature


def get_level_10_features(
    aura_of_protection: WizardFeatures.AuraOfProtection,
):
    aura_of_protection.add_feature(WizardFeatures.AuraOfCourage())
    return aura_of_protection


def get_level_11_features(
    data: CharacterSheetCreator.CharacterSheetData,
) -> CharacterSheetCreator.CharacterSheetData:

    data.add_feature(WizardFeatures.RadiantStrikes())
    return data


def get_level_12_features(
    wizard_level_12: WizardLevel12, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    data.add_feature(wizard_level_12.general_feat)
    return data


def get_level_14_features(
    lay_on_hands: WizardFeatures.LayOnHands,
) -> WizardFeatures.LayOnHands:

    lay_on_hands.add_feature(WizardFeatures.RestoringTouch())
    return lay_on_hands


def get_level_16_features(
    wizard_level_16: WizardLevel16, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    data.add_feature(wizard_level_16.general_feat)
    return data


def get_level_18_features(
    aura_of_protection: WizardFeatures.AuraOfProtection,
) -> WizardFeatures.AuraOfProtection:

    aura_of_protection.add_feature(WizardFeatures.AuraOfExpansion())
    return aura_of_protection
