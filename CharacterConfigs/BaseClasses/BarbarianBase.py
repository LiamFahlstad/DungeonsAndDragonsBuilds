from typing import Optional

import attr

import Definitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import CharacterClass
from Features import Armor, Backgrounds, EpicBoon, GeneralFeats, OriginFeats, Weapons
from Features.ClassFeatures import BarbarianFeatures
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SavingThrowsStatBlock import BarbarianSavingThrowsStatBlock
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


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
        if not data.armors:
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
        unarmored_defense_text: BarbarianFeatures.UnarmoredDefenseText = (
            data.get_features_by_type(BarbarianFeatures.UnarmoredDefenseText)[0]
        )
        unarmored_defense_text.add_feature(BarbarianFeatures.FastMovement())
        data.add_feature(BarbarianFeatures.ExtraAttack())
        return data


@attr.dataclass
class BarbarianLevel6(ClassBuilder.BaseClassLevel6):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel7(ClassBuilder.BaseClassLevel7):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.FeralInstinct())
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.InstinctivePounce())
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
        reckless_attack: BarbarianFeatures.RecklessAttack = data.get_features_by_type(
            BarbarianFeatures.RecklessAttack
        )[0]
        reckless_attack.add_feature(BarbarianFeatures.BrutalStrike())
        return data


@attr.dataclass
class BarbarianLevel10(ClassBuilder.BaseClassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel11(ClassBuilder.BaseClassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.RelentlessRage())
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
        reckless_attack: BarbarianFeatures.RecklessAttack = data.get_features_by_type(
            BarbarianFeatures.RecklessAttack
        )[0]
        reckless_attack.add_feature(BarbarianFeatures.ImprovedBrutalStrike1())
        return data


@attr.dataclass
class BarbarianLevel14(ClassBuilder.BaseClassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        return data


@attr.dataclass
class BarbarianLevel15(ClassBuilder.BaseClassLevel15):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.add_feature(BarbarianFeatures.PersistentRage())
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
        reckless_attack: BarbarianFeatures.RecklessAttack = data.get_features_by_type(
            BarbarianFeatures.RecklessAttack
        )[0]
        reckless_attack.add_feature(BarbarianFeatures.ImprovedBrutalStrike2())
        return data


@attr.dataclass
class BarbarianLevel18(ClassBuilder.BaseClassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.IndomitableMight())
        return data


@attr.dataclass
class BarbarianLevel19(ClassBuilder.BaseClassLevel19):
    epic_boon: EpicBoon.EpicBoonCharacterFeature | EpicBoon.EpicBoonTextFeature

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.epic_boon)
        return data


@attr.dataclass
class BarbarianLevel20(ClassBuilder.BaseClassLevel20):

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(BarbarianFeatures.PrimalChampion())
        return data


class BarbarianStarterClassBuilder(ClassBuilder.StarterClassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        subclass: str,
        abilities: AbilitiesStatBlock,
        barbarian_skills: BarbarianSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        default_equipment = [
            Weapons.Greataxe(player_is_proficient=True),
        ]
        super().__init__(
            base_class=CharacterClass.BARBARIAN,
            base_class_level_features=barbarian_level_features,
            base_class_level=barbarian_level,
            subclass=subclass,
            abilities=abilities,
            skills=barbarian_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            saving_throws=BarbarianSavingThrowsStatBlock(),
            add_default_equipment=add_default_equipment,
            default_equipment=default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class BarbarianMulticlassBuilder(ClassBuilder.MulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        subclass: str,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        self.subclass = subclass
        super().__init__(
            base_class=CharacterClass.BARBARIAN,
            base_class_level_features=barbarian_level_features,
            base_class_level=barbarian_level,
            subclass=subclass,
            replace_spells=replace_spells,
        )
