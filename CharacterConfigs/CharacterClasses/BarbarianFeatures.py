import attr

import Definitions
from CharacterConfigs.CharacterClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Features import GeneralFeats, Weapons
from Features.ClassFeatures import BarbarianFeatures


@attr.dataclass
class BarbarianLevel1(ClassBuilder.BaseClassLevel1):
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(BarbarianFeatures.Rage())
        data.add_feature(BarbarianFeatures.UnarmoredDefense())
        data.add_feature(BarbarianFeatures.UnarmoredDefenseText())
        data.add_feature(BarbarianFeatures.WeaponMastery())
        return data


@attr.dataclass
class BarbarianLevel2(ClassBuilder.BaseClassLevel2):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.DangerSenseText())
        data.add_feature(BarbarianFeatures.DangerSense())
        data.add_feature(BarbarianFeatures.RecklessAttack())
        return data


@attr.dataclass
class BarbarianLevel3(ClassBuilder.BaseClassLevel3):
    skill: Definitions.Skill

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.PrimalKnowledgeSkillProficiency(self.skill))
        data.add_feature(BarbarianFeatures.PrimalKnowledge())
        return data


@attr.dataclass
class BarbarianLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        data.add_feature(self.general_feat)

        return data


@attr.dataclass
class BarbarianLevel5(ClassBuilder.BaseClassLevel5):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        # Automatic feature
        data.add_feature(BarbarianFeatures.ExtraAttack())
        data.add_feature(BarbarianFeatures.FaithfulSteed())

        # Oath of vengeance features

        return data


@attr.dataclass
class BarbarianLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.AuraOfProtection())
        return data


@attr.dataclass
class BarbarianLevel7(ClassBuilder.BaseClassLevel7):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        return data


@attr.dataclass
class BarbarianLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BarbarianLevel9(ClassBuilder.BaseClassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: BarbarianFeatures.ChannelDivinity = (
            data.get_features_by_type(BarbarianFeatures.ChannelDivinity)[0]
        )

        return data


@attr.dataclass
class BarbarianLevel10(ClassBuilder.BaseClassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: BarbarianFeatures.AuraOfProtection = (
            data.get_features_by_type(BarbarianFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(BarbarianFeatures.AuraOfCourage())
        return data


@attr.dataclass
class BarbarianLevel11(ClassBuilder.BaseClassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.RadiantStrikes())

        return data


@attr.dataclass
class BarbarianLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BarbarianLevel13(ClassBuilder.BaseClassLevel13):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        lay_on_hands: BarbarianFeatures.LayOnHands = data.get_features_by_type(
            BarbarianFeatures.LayOnHands
        )[0]
        lay_on_hands.add_feature(BarbarianFeatures.RestoringTouch())
        return data


@attr.dataclass
class BarbarianLevel15(ClassBuilder.BaseClassLevel15):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class BarbarianLevel17(ClassBuilder.BaseClassLevel17):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_protection: BarbarianFeatures.AuraOfProtection = (
            data.get_features_by_type(BarbarianFeatures.AuraOfProtection)[0]
        )
        aura_of_protection.add_feature(BarbarianFeatures.AuraExpansion())
        return data


@attr.dataclass
class BarbarianLevel19(ClassBuilder.BaseClassLevel19):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        return data


@attr.dataclass
class BarbarianLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data
