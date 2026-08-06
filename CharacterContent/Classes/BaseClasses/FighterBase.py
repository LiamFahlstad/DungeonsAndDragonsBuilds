from typing import Optional

import attr

import Core.Definitions as Definitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import Ability, CharacterClass
from CharacterContent.Features.CharacterFeats import EpicBoon, GeneralFeats
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items import Packs
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Features.ClassFeatures.Fighter import FighterFeatures
from CharacterContent.Features.CombatFeatures.FightingStyles import FightingStyle
from StatBlocks.SavingThrowsStatBlock import FighterSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import FighterSkillsStatBlock


@attr.dataclass
class FighterLevel1(ClassBuilder.BaseClassLevel1):
    weapon_mastery_1: Weapons.AbstractWeapon
    weapon_mastery_2: Weapons.AbstractWeapon
    weapon_mastery_3: Weapons.AbstractWeapon
    fighting_style: FightingStyle

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery_1)
        data.add_weapon_mastery(self.weapon_mastery_2)
        data.add_weapon_mastery(self.weapon_mastery_3)
        data.add_fighting_style(self.fighting_style)

        data.add_feature(FighterFeatures.SecondWind())
        data.add_feature(FighterFeatures.FightingStyle())
        data.add_feature(FighterFeatures.WeaponMastery())
        return data


@attr.dataclass
class FighterLevel2(ClassBuilder.BaseClassLevel2):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(FighterFeatures.ActionSurge())
        second_wind: FighterFeatures.SecondWind = data.get_features_by_type(
            FighterFeatures.SecondWind
        )[0]
        second_wind.extend_feature(FighterFeatures.TacticalMind())
        return data


@attr.dataclass
class FighterLevel3(ClassBuilder.BaseClassLevel3):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class FighterLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    weapon_mastery: Weapons.AbstractWeapon

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery)
        self.general_feat.origin = f"Fighter Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class FighterLevel5(ClassBuilder.BaseClassLevel5):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(FighterFeatures.ExtraAttack())
        second_wind: FighterFeatures.SecondWind = data.get_features_by_type(
            FighterFeatures.SecondWind
        )[0]
        second_wind.extend_feature(FighterFeatures.TacticalShift())
        return data


@attr.dataclass
class FighterLevel6(ClassBuilder.BaseClassLevel6):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        self.general_feat.origin = f"Fighter Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class FighterLevel7(ClassBuilder.BaseClassLevel7):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class FighterLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        self.general_feat.origin = f"Fighter Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class FighterLevel9(ClassBuilder.BaseClassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterFeatures.Indomitable())
        weapon_mastery: FighterFeatures.WeaponMastery = data.get_features_by_type(
            FighterFeatures.WeaponMastery
        )[0]
        weapon_mastery.extend_feature(FighterFeatures.TacticalMaster())
        return data


@attr.dataclass
class FighterLevel10(ClassBuilder.BaseClassLevel10):
    weapon_mastery: Weapons.AbstractWeapon

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery)
        return data


@attr.dataclass
class FighterLevel11(ClassBuilder.BaseClassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        extra_attack: FighterFeatures.ExtraAttack = data.get_features_by_type(
            FighterFeatures.ExtraAttack
        )[0]
        extra_attack.extend_feature(FighterFeatures.TwoExtraAttacks())
        return data


@attr.dataclass
class FighterLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        self.general_feat.origin = f"Fighter Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class FighterLevel13(ClassBuilder.BaseClassLevel13):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(FighterFeatures.StudiedAttacks())
        return data


@attr.dataclass
class FighterLevel14(ClassBuilder.BaseClassLevel14):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        self.general_feat.origin = f"Fighter Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class FighterLevel15(ClassBuilder.BaseClassLevel15):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class FighterLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat
    weapon_mastery: Weapons.AbstractWeapon

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_weapon_mastery(self.weapon_mastery)
        self.general_feat.origin = f"Fighter Level {self.level}"
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class FighterLevel17(ClassBuilder.BaseClassLevel17):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class FighterLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class FighterLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        self.epic_boon.origin = f"Fighter Level {self.level}"
        data.add_feature(self.epic_boon)
        return data


@attr.dataclass
class FighterLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        extra_attack: FighterFeatures.ExtraAttack = data.get_features_by_type(
            FighterFeatures.ExtraAttack
        )[0]
        extra_attack.extend_feature(FighterFeatures.ThreeExtraAttacks())
        return data


class FighterCustomStarterClassArgs(ClassBuilder.CustomStarterClassArgs):
    def __init__(
        self,
        subclass: str,
        skills: FighterSkillsStatBlock,
        caster_type: Optional[SpellSlots.CasterType] = None,
    ):
        super().__init__(
            base_class=CharacterClass.FIGHTER,
            subclass=subclass,
            saving_throws=FighterSavingThrowsStatBlock(),
            default_equipment=[
                Weapons.Greatsword(),
                Weapons.Flail(),
                Armor.ChainMailArmor(),
                Armor.ShieldArmor(),
            ],
            skills=skills,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
                Definitions.ArmorType.MEDIUM,
                Definitions.ArmorType.HEAVY,
                Definitions.ArmorType.SHIELD,
            ],
            weapon_proficiencies=[
                Weapons.WeaponProficiency.SIMPLE,
                Weapons.WeaponProficiency.MARTIAL,
            ],
            spell_casting_ability=Ability.INTELLIGENCE if caster_type is not None else None,
            caster_type=caster_type,
            default_pack=Packs.DungeoneersPack(),
        )


class FighterMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
        caster_type: Optional[SpellSlots.CasterType] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.FIGHTER,
            base_class_level_features=fighter_level_features,
            base_class_level=fighter_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.INTELLIGENCE if caster_type is not None else None,
            caster_type=caster_type,
        )
