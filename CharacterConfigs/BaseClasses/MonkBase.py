from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Ability, CharacterClass
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import MonkFeatures
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import MonkSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class MonkLevel1(ClassBuilder.BaseClassLevel1):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.MartialArts())
        return data


@attr.dataclass
class MonkLevel2(ClassBuilder.BaseClassLevel2):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus = MonkFeatures.MonksFocus()
        monks_focus.add_feature(MonkFeatures.FlurryOfBlows())
        monks_focus.add_feature(MonkFeatures.PatientDefense())
        monks_focus.add_feature(MonkFeatures.StepOfTheWind())
        data.add_feature(monks_focus)
        data.add_feature(MonkFeatures.UnarmoredDefense())
        data.add_feature(MonkFeatures.UnarmoredDefenseText())
        data.add_feature(MonkFeatures.UncannyMetabolism())
        return data


@attr.dataclass
class MonkLevel3(ClassBuilder.BaseClassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.add_feature(MonkFeatures.DeflectAttacks())
        return data


@attr.dataclass
class MonkLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_feature(MonkFeatures.SlowFall())
        return data


@attr.dataclass
class MonkLevel5(ClassBuilder.BaseClassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.add_feature(MonkFeatures.StunningStrike())
        data.add_feature(MonkFeatures.ExtraAttack())
        return data


@attr.dataclass
class MonkLevel6(ClassBuilder.BaseClassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.EmpoweredStrikes())
        return data


@attr.dataclass
class MonkLevel7(ClassBuilder.BaseClassLevel7):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.Evasion())
        return data


@attr.dataclass
class MonkLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class MonkLevel9(ClassBuilder.BaseClassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.AcrobaticMovement())
        return data


@attr.dataclass
class MonkLevel10(ClassBuilder.BaseClassLevel10):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.HeightenedFocus())
        data.add_feature(MonkFeatures.SelfRestoration())
        return data


@attr.dataclass
class MonkLevel11(ClassBuilder.BaseClassLevel11):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class MonkLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class MonkLevel13(ClassBuilder.BaseClassLevel13):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.DeflectEnergy())
        return data


@attr.dataclass
class MonkLevel14(ClassBuilder.BaseClassLevel14):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.DisciplinedSurvivorSavingThrows())
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.add_feature(MonkFeatures.DisciplinedSurvivorMartialFocus())

        return data


@attr.dataclass
class MonkLevel15(ClassBuilder.BaseClassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkFeatures.PerfectFocus())
        return data


@attr.dataclass
class MonkLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class MonkLevel17(ClassBuilder.BaseClassLevel17):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class MonkLevel18(ClassBuilder.BaseClassLevel18):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.add_feature(MonkFeatures.SuperiorDefense())
        return data


@attr.dataclass
class MonkLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoon

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class MonkLevel20(ClassBuilder.BaseClassLevel20):
    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(MonkFeatures.BodyAndMind())
        return data


class MonkStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        monk_skills: MonkSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Weapons.Spear(player_is_proficient=True),
            Weapons.Dagger(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.MONK,
            base_class_level_features=monk_level_features,
            base_class_level=monk_level,
            subclass=subclass,
            abilities=abilities,
            skills=monk_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=MonkSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor_proficiencies=[],
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
        )


class MonkMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.MONK,
            base_class_level_features=monk_level_features,
            base_class_level=monk_level,
            subclass=subclass,
            replace_spells=replace_spells,
            spell_casting_ability=Ability.WISDOM,
        )
