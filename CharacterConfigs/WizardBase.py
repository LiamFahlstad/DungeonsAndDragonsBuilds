import attr
from Definitions import Ability, CharacterClass, Skill
from Features import GeneralFeats, OriginFeats
import CharacterSheetCreator
from Features import Armor
from Features import Backgrounds
from Features import Weapons
from Features.ClassFeatures import WizardFeatures, WizardFeatures
from Features.ClassFeatures import SpellSlots
from StatBlocks.AbilitiesStatBlock import (
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
    WizardLevel6Spells,
    WizardLevel7Spells,
    WizardLevel8Spells,
    WizardLevel9Spells,
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
    skill_to_expertise_in: Skill
    spell: WizardLevel1Spells


@attr.dataclass
class WizardLevel3:
    spell: WizardLevel1Spells | WizardLevel2Spells


@attr.dataclass
class WizardLevel4:
    general_feat: GeneralFeats.GeneralFeat
    cantrip: WizardLevel0Spells
    spell: WizardLevel1Spells | WizardLevel2Spells


@attr.dataclass
class WizardLevel5:
    spell_1: WizardLevel1Spells | WizardLevel2Spells | WizardLevel3Spells
    spell_2: WizardLevel1Spells | WizardLevel2Spells | WizardLevel3Spells


@attr.dataclass
class WizardLevel6:
    spell: WizardLevel1Spells | WizardLevel2Spells | WizardLevel3Spells


@attr.dataclass
class WizardLevel7:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
    )


@attr.dataclass
class WizardLevel8:
    general_feat: GeneralFeats.GeneralFeat
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
    )


@attr.dataclass
class WizardLevel9:
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
class WizardLevel10:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
    )


@attr.dataclass
class WizardLevel11:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
    )


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
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
    )


@attr.dataclass
class WizardLevel14:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
    )


@attr.dataclass
class WizardLevel15:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
        | WizardLevel8Spells
    )


@attr.dataclass
class WizardLevel16:
    general_feat: GeneralFeats.GeneralFeat
    spell_1: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
        | WizardLevel8Spells
    )
    spell_2: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
        | WizardLevel8Spells
    )


@attr.dataclass
class WizardLevel17:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
        | WizardLevel8Spells
        | WizardLevel9Spells
    )


@attr.dataclass
class WizardLevel18:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
        | WizardLevel8Spells
        | WizardLevel9Spells
    )


@attr.dataclass
class WizardLevel18:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
        | WizardLevel8Spells
        | WizardLevel9Spells
    )


@attr.dataclass
class WizardLevel19:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
        | WizardLevel8Spells
        | WizardLevel9Spells
    )


@attr.dataclass
class WizardLevel20:
    spell: (
        WizardLevel1Spells
        | WizardLevel2Spells
        | WizardLevel3Spells
        | WizardLevel4Spells
        | WizardLevel5Spells
        | WizardLevel6Spells
        | WizardLevel7Spells
        | WizardLevel8Spells
        | WizardLevel9Spells
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
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(WizardFeatures.RitualAdept())
    data.add_feature(WizardFeatures.ArcaneRecovery())
    data.add_cantrip(wizard_level_1.cantrip_1)
    data.add_cantrip(wizard_level_1.cantrip_2)
    data.add_cantrip(wizard_level_1.cantrip_3)
    data.add_spell(wizard_level_1.spell_1)
    data.add_spell(wizard_level_1.spell_2)
    data.add_spell(wizard_level_1.spell_3)
    data.add_spell(wizard_level_1.spell_4)
    return data


def get_level_2_features(
    wizard_level_2: WizardLevel2, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(WizardFeatures.Scholar(wizard_level_2.skill_to_expertise_in))
    data.add_spell(wizard_level_2.spell)
    return data


def get_level_3_features(
    wizard_level_3: WizardLevel3, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_3.spell)
    return data


def get_level_4_features(
    wizard_level_4: WizardLevel4, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(wizard_level_4.general_feat)
    data.add_cantrip(wizard_level_4.cantrip)
    data.add_spell(wizard_level_4.spell)
    return data


def get_level_5_features(
    wizard_level_5: WizardLevel5, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(WizardFeatures.MemorizeSpell())
    data.add_spell(wizard_level_5.spell_1)
    data.add_spell(wizard_level_5.spell_2)
    return data


def get_level_6_features(
    wizard_level_6: WizardLevel6, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_6.spell)
    return data


def get_level_7_features(
    wizard_level_7: WizardLevel7, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_7.spell)
    return data


def get_level_8_features(
    wizard_level_8: WizardLevel8, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(wizard_level_8.general_feat)
    data.add_spell(wizard_level_8.spell)
    return data


def get_level_9_features(
    wizard_level_9: WizardLevel9, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_9.spell_1)
    data.add_spell(wizard_level_9.spell_2)
    return data


def get_level_10_features(
    wizard_level_10: WizardLevel10, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_10.spell)
    return data


def get_level_11_features(
    wizard_level_11: WizardLevel11, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_11.spell)
    return data


def get_level_12_features(
    wizard_level_12: WizardLevel12, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(wizard_level_12.general_feat)
    return data


def get_level_13_features(
    wizard_level_13: WizardLevel13, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_13.spell)
    return data


def get_level_14_features(
    wizard_level_14: WizardLevel14, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_14.spell)
    return data


def get_level_15_features(
    wizard_level_15: WizardLevel15, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_spell(wizard_level_15.spell)
    return data


def get_level_16_features(
    wizard_level_16: WizardLevel16, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(wizard_level_16.general_feat)
    data.add_spell(wizard_level_16.spell_1)
    data.add_spell(wizard_level_16.spell_2)
    return data


def get_level_17_features(
    wizard_level_17: WizardLevel17, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    data.add_spell(wizard_level_17.spell)
    return data


def get_level_18_features(
    wizard_level_18: WizardLevel18, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(WizardFeatures.SpellMastery())
    data.add_spell(wizard_level_18.spell)
    return data


def get_level_19_features(
    wizard_level_19: WizardLevel19, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:

    data.add_spell(wizard_level_19.spell)
    return data


def get_level_20_features(
    wizard_level_20: WizardLevel20, data: CharacterSheetCreator.CharacterSheetData
) -> CharacterSheetCreator.CharacterSheetData:
    data.add_feature(WizardFeatures.SignatureSpells())
    data.add_spell(wizard_level_20.spell)
    return data
