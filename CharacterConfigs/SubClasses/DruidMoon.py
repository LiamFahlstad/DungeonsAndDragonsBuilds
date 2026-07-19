from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidCustomStarterClassArgs,
    DruidMulticlassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import DruidSubclass
from Features.SubClassFeatures.Druid import DruidMoonFeatures
from Spells.SpellLists import (
    DruidLevel0Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
)
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock


@attr.dataclass
class DruidMoonLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidMoonFeatures.CircleForms())
        data.add_feature(DruidMoonFeatures.CircleOfTheMoonSpells())
        data.add_spell(DruidLevel0Spells.STARRY_WISP)
        data.add_spell(DruidLevel1Spells.CURE_WOUNDS)
        data.add_spell(DruidLevel2Spells.MOONBEAM)
        return data


@attr.dataclass
class DruidMoonLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel3Spells.CONJURE_ANIMALS)
        return data


@attr.dataclass
class DruidMoonLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        circle_forms: DruidMoonFeatures.CircleForms = data.get_features_by_type(
            DruidMoonFeatures.CircleForms
        )[0]
        circle_forms.extend_feature(DruidMoonFeatures.ImprovedCircleForms())
        return data


@attr.dataclass
class DruidMoonLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel4Spells.FOUNT_OF_MOONLIGHT)
        return data


@attr.dataclass
class DruidMoonLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel5Spells.MASS_CURE_WOUNDS)
        return data


@attr.dataclass
class DruidMoonLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidMoonFeatures.MoonlightStep())
        return data


@attr.dataclass
class DruidMoonLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidMoonFeatures.LunarForm())
        return data


class DruidMoonCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: DruidSkillsStatBlock,
    ):
        super().__init__(
            subclass=DruidSubclass.MOON.value,
            skills=skills,
        )


class DruidMoonMulticlassBuilder(DruidMulticlassBuilder):

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
