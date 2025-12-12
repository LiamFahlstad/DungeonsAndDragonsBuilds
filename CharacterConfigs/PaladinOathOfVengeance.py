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
from CharacterConfigs import PaladinBase
from Spells.Definitions import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
    RangerLevel1Spells,
    WarlockLevel1Spells,
)


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
    data.character_subclass = PaladinSubclass.OATH_OF_VENGEANCE.value
    channel_divinity_feature = None

    # ================ LEVEL 1 ============= #
    if paladin_level >= 1:
        if paladin_level_1 is None:
            raise ValueError("paladin_level_1 must be provided for level 1 features.")
        data = PaladinBase.get_level_1_features(
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

        # Oath of vengeance features
        data.add_spell(WarlockLevel1Spells.BANE)
        data.add_spell(RangerLevel1Spells.HUNTERS_MARK)
        channel_divinity_feature.add_spell("Vow of Enmity")

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

    # ================ LEVEL 6 ============= #
    if paladin_level >= 6:
        # Automatic feature
        data.add_feature(PaladinFeatures.AuraOfProtection())

    ##########################################
    # ============ LEAVE AS IS ============= #
    ##########################################

    if channel_divinity_feature is not None:
        data.add_feature(channel_divinity_feature)

    data.replace_spells(replace_spells or {})
    return data
