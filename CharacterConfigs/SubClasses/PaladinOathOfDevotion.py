import CharacterSheetCreator
from CharacterConfigs.BaseClasses import PaladinBase
from Definitions import PaladinSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import PaladinFeatures
from Spells.Definitions import PaladinLevel1Spells
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


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
    paladin_level_1: PaladinBase.PaladinLevel1 = None,
    paladin_level_2: PaladinBase.PaladinLevel2 = None,
    paladin_level_3: PaladinBase.PaladinLevel3 = None,
    paladin_level_4: PaladinBase.PaladinLevel4 = None,
    paladin_level_5: PaladinBase.PaladinLevel5 = None,
    paladin_level_7: PaladinBase.PaladinLevel7 = None,
    paladin_level_8: PaladinBase.PaladinLevel8 = None,
    paladin_level_9: PaladinBase.PaladinLevel9 = None,
    paladin_level_11: PaladinBase.PaladinLevel11 = None,
    paladin_level_12: PaladinBase.PaladinLevel12 = None,
    paladin_level_13: PaladinBase.PaladinLevel13 = None,
    paladin_level_15: PaladinBase.PaladinLevel15 = None,
    paladin_level_16: PaladinBase.PaladinLevel16 = None,
    paladin_level_17: PaladinBase.PaladinLevel17 = None,
    paladin_level_19: PaladinBase.PaladinLevel19 = None,
    replace_spells: dict[str, str] = None,
) -> CharacterSheetCreator.CharacterSheetData:

    if not isinstance(skills, PaladinSkillsStatBlock):
        raise ValueError("skills must be an instance of PaladinSkillsStatBlock")

    data = PaladinBase.get_character_sheet_creator_base(
        paladin_level=paladin_level,
        abilities=abilities,
        skills=skills,
        background_ability_bonuses=background_ability_bonuses,
        background_skill_proficiencies=background_skill_proficiencies,
        add_default_equipment=add_default_equipment,
        origin_feat=origin_feat,
        armor=armor,
        weapons=weapons,
    )
    data.character_subclass = PaladinSubclass.OATH_OF_DEVOTION.value
    channel_divinity_feature = None
    aura_of_protection = None
    lay_on_hands = None

    # ================ LEVEL 1 ============= #
    if paladin_level >= 1:
        if paladin_level_1 is None:
            raise ValueError("paladin_level_1 must be provided for level 1 features.")
        data, lay_on_hands = PaladinBase.get_level_1_features(
            paladin_level_1=paladin_level_1,
            data=data,
        )

    # ================ LEVEL 2 ============= #
    if paladin_level >= 2:
        if paladin_level_2 is None:
            raise ValueError("paladin_level_2 must be provided for level 2 features.")

        data = PaladinBase.get_level_2_features(
            paladin_level_2=paladin_level_2,
            data=data,
        )

    # ================ LEVEL 3 ============= #
    if paladin_level >= 3:
        if paladin_level_3 is None:
            raise ValueError("paladin_level_3 must be provided for level 3 features.")

        data, channel_divinity_feature = PaladinBase.get_level_3_features(
            paladin_level_3=paladin_level_3,
            data=data,
        )

        # Oath of devotion features
        data.add_spell(PaladinLevel1Spells.PROTECTION_FROM_EVIL_AND_GOOD)
        data.add_spell(PaladinLevel1Spells.SHIELD_OF_FAITH)
        channel_divinity_feature.add_spell("Sacred Weapon")

    # ================ LEVEL 4 ============= #
    if paladin_level >= 4:
        if paladin_level_4 is None:
            raise ValueError("paladin_level_4 must be provided for level 4 features.")

        data = PaladinBase.get_level_4_features(
            paladin_level_4=paladin_level_4,
            data=data,
        )

    # ================ LEVEL 5 ============= #
    if paladin_level >= 5:
        if paladin_level_5 is None:
            raise ValueError("paladin_level_5 must be provided for level 5 features.")

        data = PaladinBase.get_level_5_features(
            paladin_level_5=paladin_level_5,
            data=data,
        )

        # Oath of glory features
        # data.add_spell(ClericLevel2Spells.ENHANCE_ABILITY)
        # data.add_spell(PaladinLevel2Spells.MAGIC_WEAPON)

    # ================ LEVEL 6 ============= #
    if paladin_level >= 6:
        # Automatic feature
        aura_of_protection = PaladinBase.get_level_6_features()

    # ================ LEVEL 7 ============= #
    if paladin_level >= 7:
        if paladin_level_7 is None:
            raise ValueError("paladin_level_7 must be provided for level 7 features.")
        # Automatic feature
        aura_of_protection.add_feature(PaladinFeatures.AuraOfDevotion())
        data.add_spell(paladin_level_7.spell)

    # ================ LEVEL 8 ============= #
    if paladin_level >= 8:
        # Automatic feature
        data = PaladinBase.get_level_8_features(
            paladin_level_8=paladin_level_8,
            data=data,
        )

    # ================ LEVEL 9 ============= #
    if paladin_level >= 9:
        if paladin_level_9 is None:
            raise ValueError("paladin_level_9 must be provided for level 9 features.")

        # Automatic feature
        channel_divinity_feature = PaladinBase.get_level_9_features(
            channel_divinity_feature=channel_divinity_feature,
        )
        data.add_spell(paladin_level_9.spell)

        # Oath of glory features
        # data.add_spell(WizardLevel3Spells.HASTE)
        # data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)

    # ================ LEVEL 10 ============= #
    if paladin_level >= 10:
        aura_of_protection.add_feature(PaladinFeatures.AuraOfCourage())

    # ================ LEVEL 11 ============= #
    if paladin_level >= 11:
        if paladin_level_11 is None:
            raise ValueError("paladin_level_11 must be provided for level 11 features.")

        data = PaladinBase.get_level_11_features(data=data)
        data.add_spell(paladin_level_11.spell)

    # ================ LEVEL 12 ============= #
    if paladin_level >= 12:
        # Automatic feature
        data = PaladinBase.get_level_12_features(
            paladin_level_12=paladin_level_12,
            data=data,
        )

    # ================ LEVEL 13 ============= #
    if paladin_level >= 13:
        if paladin_level_13 is None:
            raise ValueError("paladin_level_13 must be provided for level 13 features.")

        data.add_spell(paladin_level_13.spell)

        # Oath of glory features
        # data.add_spell(BardLevel4Spells.COMPULSION)
        # data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)

    # ================ LEVEL 14 ============= #
    if paladin_level >= 14:
        lay_on_hands = PaladinBase.get_level_14_features(lay_on_hands=lay_on_hands)

    # ================ LEVEL 15 ============= #
    if paladin_level >= 15:
        if paladin_level_15 is None:
            raise ValueError("paladin_level_15 must be provided for level 15 features.")

        data.add_feature(PaladinFeatures.SmiteOfProtection())
        data.add_spell(paladin_level_15.spell)

    # ================ LEVEL 16 ============= #
    if paladin_level >= 16:
        # Automatic feature
        data = PaladinBase.get_level_16_features(
            paladin_level_16=paladin_level_16,
            data=data,
        )

    # ================ LEVEL 17 ============= #
    if paladin_level >= 17:
        if paladin_level_17 is None:
            raise ValueError("paladin_level_17 must be provided for level 17 features.")

        # data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        # data.add_spell(WizardLevel5Spells.YOLANDE_S_REGAL_PRESENCE)
        data.add_spell(paladin_level_17.spell_1)
        data.add_spell(paladin_level_17.spell_2)

    # ================ LEVEL 18 ============= #
    if paladin_level >= 18:
        aura_of_protection = PaladinBase.get_level_18_features(
            aura_of_protection=aura_of_protection,
        )

    # ================ LEVEL 19 ============= #
    if paladin_level >= 19:
        if paladin_level_19 is None:
            raise ValueError("paladin_level_19 must be provided for level 19 features.")

        data.add_spell(paladin_level_19.spell)

    # ================ LEVEL 20 ============= #
    if paladin_level >= 20:
        data.add_feature(PaladinFeatures.HolyNimbus())

    ##########################################
    # ============ LEAVE AS IS ============= #
    ##########################################

    if channel_divinity_feature is not None:
        data.add_feature(channel_divinity_feature)

    if aura_of_protection is not None:
        data.add_feature(aura_of_protection)

    if lay_on_hands is not None:
        data.add_feature(lay_on_hands)

    data.replace_spells(replace_spells or {})
    return data
