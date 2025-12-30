import attr

import Definitions
from CharacterConfigs.CharacterClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Features import GeneralFeats, Weapons
from Features.ClassFeatures import RogueFeatures


@attr.dataclass
class RogueLevel1(ClassBuilder.BaseClassLevel1):
    skill_1: Definitions.Skill
    skill_2: Definitions.Skill
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)

        data.add_feature(RogueFeatures.Expertise(self.skill_1, self.skill_2))
        data.add_feature(RogueFeatures.SneakAttack())
        data.add_feature(RogueFeatures.ThievesCant())
        data.add_feature(RogueFeatures.WeaponMastery())
        return data


@attr.dataclass
class RogueLevel2(ClassBuilder.BaseClassLevel2):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.CunningAction())
        return data


@attr.dataclass
class RogueLevel3(ClassBuilder.BaseClassLevel3):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.SteadyAim())
        return data


@attr.dataclass
class RogueLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class RogueLevel5(ClassBuilder.BaseClassLevel5):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.UncannyDodge())
        return data


@attr.dataclass
class RogueLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel7(ClassBuilder.BaseClassLevel7):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.ReliableTalent())
        return data


@attr.dataclass
class RogueLevel8(ClassBuilder.BaseClassLevel8):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel9(ClassBuilder.BaseClassLevel9):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel10(ClassBuilder.BaseClassLevel10):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel11(ClassBuilder.BaseClassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.ImprovedCunningStrike())
        return data


@attr.dataclass
class RogueLevel12(ClassBuilder.BaseClassLevel12):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel13(ClassBuilder.BaseClassLevel13):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.add_feature(RogueFeatures.CunningStrike())
        data.add_feature(RogueFeatures.DeviousStrikes())
        return data


@attr.dataclass
class RogueLevel15(ClassBuilder.BaseClassLevel15):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.SlipperyMind())
        return data


@attr.dataclass
class RogueLevel16(ClassBuilder.BaseClassLevel16):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel17(ClassBuilder.BaseClassLevel17):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class RogueLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueFeatures.Elusive())
        return data


@attr.dataclass
class RogueLevel19(ClassBuilder.BaseClassLevel19):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:

        return data


@attr.dataclass
class RogueLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(RogueFeatures.StrokeOfLuck())
        return data
