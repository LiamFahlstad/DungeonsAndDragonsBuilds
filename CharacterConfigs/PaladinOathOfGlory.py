from typing import Optional
import attr
from CharacterConfigs.PaladinBase import (
    ClassLevelBase,
    PaladinBase,
    PaladinLevel1,
    PaladinLevel10,
    PaladinLevel11,
    PaladinLevel12,
    PaladinLevel13,
    PaladinLevel14,
    PaladinLevel15,
    PaladinLevel16,
    PaladinLevel17,
    PaladinLevel18,
    PaladinLevel19,
    PaladinLevel2,
    PaladinLevel20,
    PaladinLevel3,
    PaladinLevel4,
    PaladinLevel5,
    PaladinLevel6,
    PaladinLevel7,
    PaladinLevel8,
    PaladinLevel9,
    PaladinSubclassLevel13,
    PaladinSubclassLevel15,
    PaladinSubclassLevel17,
    PaladinSubclassLevel20,
    PaladinSubclassLevel3,
    PaladinSubclassLevel5,
    PaladinSubclassLevel7,
    PaladinSubclassLevel9,
)
from Definitions import Ability, PaladinSubclass, Skill, CharacterClass, FighterSubclass
from Features import BaseFeatures, GeneralFeats, Maneuvers, OriginFeats
from CharacterSheetCreator import CharacterSheetData
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
    BardLevel4Spells,
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)


@attr.dataclass
class GloryPaladinLevel3(PaladinSubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: PaladinFeatures.ChannelDivinity = (
            data.get_features_by_type(PaladinFeatures.ChannelDivinity)[0]
        )
        channel_divinity_feature.add_feature(PaladinFeatures.InspiringSmite())
        channel_divinity_feature.add_feature(PaladinFeatures.PeerlessAthlete())
        data.add_spell(ClericLevel1Spells.GUIDING_BOLT)
        data.add_spell(PaladinLevel1Spells.HEROISM)
        return data


@attr.dataclass
class GloryPaladinLevel5(PaladinSubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.ENHANCE_ABILITY)
        data.add_spell(PaladinLevel2Spells.MAGIC_WEAPON)
        return data


@attr.dataclass
class GloryPaladinLevel7(PaladinSubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: PaladinFeatures.AuraOfProtection = (
            data.get_features_by_type(PaladinFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(PaladinFeatures.AuraOfAlacrity())
        return data


@attr.dataclass
class GloryPaladinLevel9(PaladinSubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class GloryPaladinLevel13(PaladinSubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.COMPULSION)
        data.add_spell(ClericLevel4Spells.FREEDOM_OF_MOVEMENT)
        return data


@attr.dataclass
class GloryPaladinLevel15(PaladinSubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.GloriousDefense())
        return data


@attr.dataclass
class GloryPaladinLevel17(PaladinSubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.LEGEND_LORE)
        data.add_spell(WizardLevel5Spells.YOLANDES_REGAL_PRESENCE)
        return data


@attr.dataclass
class GloryPaladinLevel20(PaladinSubclassLevel20):
    level: int = attr.field(init=False, default=20)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinFeatures.LivingLegend())
        return data


class PaladinOathOfGlory(PaladinBase):

    def __init__(
        self,
        paladin_level: int,
        abilities: AbilitiesStatBlock,
        skills: PaladinSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        paladin_level_1: Optional[PaladinLevel1] = None,
        paladin_level_2: Optional[PaladinLevel2] = None,
        paladin_level_3: Optional[PaladinLevel3] = None,
        paladin_level_4: Optional[PaladinLevel4] = None,
        paladin_level_5: Optional[PaladinLevel5] = None,
        paladin_level_6: Optional[PaladinLevel6] = None,
        paladin_level_7: Optional[PaladinLevel7] = None,
        paladin_level_8: Optional[PaladinLevel8] = None,
        paladin_level_9: Optional[PaladinLevel9] = None,
        paladin_level_10: Optional[PaladinLevel10] = None,
        paladin_level_11: Optional[PaladinLevel11] = None,
        paladin_level_12: Optional[PaladinLevel12] = None,
        paladin_level_13: Optional[PaladinLevel13] = None,
        paladin_level_14: Optional[PaladinLevel14] = None,
        paladin_level_15: Optional[PaladinLevel15] = None,
        paladin_level_16: Optional[PaladinLevel16] = None,
        paladin_level_17: Optional[PaladinLevel17] = None,
        paladin_level_18: Optional[PaladinLevel18] = None,
        paladin_level_19: Optional[PaladinLevel19] = None,
        paladin_level_20: Optional[PaladinLevel20] = None,
        glory_paladin_level_3: Optional[GloryPaladinLevel3] = None,
        glory_paladin_level_5: Optional[GloryPaladinLevel5] = None,
        glory_paladin_level_7: Optional[GloryPaladinLevel7] = None,
        glory_paladin_level_9: Optional[GloryPaladinLevel9] = None,
        glory_paladin_level_13: Optional[GloryPaladinLevel13] = None,
        glory_paladin_level_15: Optional[GloryPaladinLevel15] = None,
        glory_paladin_level_17: Optional[GloryPaladinLevel17] = None,
        glory_paladin_level_20: Optional[GloryPaladinLevel20] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_GLORY,
            abilities=abilities,
            skills=skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            paladin_level_1=paladin_level_1,
            paladin_level_2=paladin_level_2,
            paladin_level_3=paladin_level_3,
            paladin_level_4=paladin_level_4,
            paladin_level_5=paladin_level_5,
            paladin_level_6=paladin_level_6,
            paladin_level_7=paladin_level_7,
            paladin_level_8=paladin_level_8,
            paladin_level_9=paladin_level_9,
            paladin_level_10=paladin_level_10,
            paladin_level_11=paladin_level_11,
            paladin_level_12=paladin_level_12,
            paladin_level_13=paladin_level_13,
            paladin_level_14=paladin_level_14,
            paladin_level_15=paladin_level_15,
            paladin_level_16=paladin_level_16,
            paladin_level_17=paladin_level_17,
            paladin_level_18=paladin_level_18,
            paladin_level_19=paladin_level_19,
            paladin_level_20=paladin_level_20,
            paladin_subclass_level_3=glory_paladin_level_3,
            paladin_subclass_level_5=glory_paladin_level_5,
            paladin_subclass_level_7=glory_paladin_level_7,
            paladin_subclass_level_9=glory_paladin_level_9,
            paladin_subclass_level_13=glory_paladin_level_13,
            paladin_subclass_level_15=glory_paladin_level_15,
            paladin_subclass_level_17=glory_paladin_level_17,
            paladin_subclass_level_20=glory_paladin_level_20,
            replace_spells=replace_spells,
        )
