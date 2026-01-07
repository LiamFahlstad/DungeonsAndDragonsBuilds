from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidMulticlassBuilder,
    DruidStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import DruidSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import DruidFeatures
from Spells.Definitions import (
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


@attr.dataclass
class MoonDruidLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.CircleForms())
        data.add_feature(DruidFeatures.CircleoftheMoonSpells())
        data.add_spell(DruidLevel0Spells.STARRY_WISP)
        data.add_spell(DruidLevel1Spells.CURE_WOUNDS)
        data.add_spell(DruidLevel2Spells.MOONBEAM)
        return data


@attr.dataclass
class MoonDruidLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel3Spells.CONJURE_ANIMALS)
        return data


@attr.dataclass
class MoonDruidLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.ImprovedCircleForms())
        return data


@attr.dataclass
class MoonDruidLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel4Spells.FOUNT_OF_MOONLIGHT)
        return data


@attr.dataclass
class MoonDruidLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel5Spells.MASS_CURE_WOUNDS)
        return data


@attr.dataclass
class MoonDruidLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.MoonlightStep())
        return data


@attr.dataclass
class MoonDruidLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidFeatures.LunarForm())
        return data


class MoonDruidStarterClassBuilder(DruidStarterClassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        abilities: AbilitiesStatBlock,
        druid_skills: DruidSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginCharacterFeat | OriginFeats.OriginTextFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass.MOON.value,
            abilities=abilities,
            druid_skills=druid_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class MoonDruidMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass.MOON.value,
            replace_spells=replace_spells,
        )
