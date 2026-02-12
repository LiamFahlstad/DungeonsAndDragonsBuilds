from typing import Optional

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import CharacterClass
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import FighterFeatures
from Features.FightingStyles import FightingStyle
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
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
        second_wind.add_feature(FighterFeatures.TacticalMind())
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
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class FighterLevel5(ClassBuilder.BaseClassLevel5):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(FighterFeatures.ExtraAttack())
        second_wind: FighterFeatures.SecondWind = data.get_features_by_type(
            FighterFeatures.SecondWind
        )[0]
        second_wind.add_feature(FighterFeatures.TacticalShift())
        return data


@attr.dataclass
class FighterLevel6(ClassBuilder.BaseClassLevel6):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
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
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class FighterLevel9(ClassBuilder.BaseClassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(FighterFeatures.Indomitable())
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
        extra_attack.add_feature(FighterFeatures.TwoExtraAttacks())
        return data


@attr.dataclass
class FighterLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
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
    epic_boon: EpicBoon.EpicBoonCharacterFeature | EpicBoon.EpicBoonTextFeature

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.epic_boon)
        return data


@attr.dataclass
class FighterLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        extra_attack: FighterFeatures.ExtraAttack = data.get_features_by_type(
            FighterFeatures.ExtraAttack
        )[0]
        extra_attack.add_feature(FighterFeatures.ThreeExtraAttacks())
        return data


class FighterStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        fighter_skills: FighterSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Weapons.Greatsword(player_is_proficient=True),
            Weapons.Longsword(player_is_proficient=True),
            Weapons.Flail(player_is_proficient=True),
            Armor.ChainMailArmor(),
            Armor.ShieldArmor(),
        ]
        super().__init__(
            base_class=CharacterClass.FIGHTER,
            base_class_level_features=fighter_level_features,
            base_class_level=fighter_level,
            subclass=subclass,
            abilities=abilities,
            skills=fighter_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=FighterSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor_proficiencies=[
                Definitions.ArmorType.LIGHT,
                Definitions.ArmorType.MEDIUM,
                Definitions.ArmorType.HEAVY,
            ],
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class FighterMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        fighter_level_features: ClassBuilder.BaseClassLevelFeatures,
        fighter_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.FIGHTER,
            base_class_level_features=fighter_level_features,
            base_class_level=fighter_level,
            subclass=subclass,
            replace_spells=replace_spells,
        )
