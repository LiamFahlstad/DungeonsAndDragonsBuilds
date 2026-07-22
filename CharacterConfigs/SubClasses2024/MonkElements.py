from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import (
    MonkMulticlassBuilder,
    MonkCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import Ability, MonkSubclass
from Features.SubClassFeatures.Monk import MonkElementsFeatures
from Features.ClassFeatures.Monk import MonkFeatures
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


@attr.dataclass
class MonkElementsLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.extend_feature(MonkElementsFeatures.ElementalAttunement())
        data.add_feature(MonkElementsFeatures.ManipulateElements())
        return data


@attr.dataclass
class MonkElementsLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        monks_focus: MonkFeatures.MonksFocus = data.get_features_by_type(
            MonkFeatures.MonksFocus
        )[0]
        monks_focus.extend_feature(MonkElementsFeatures.ElementalBurst())
        return data


@attr.dataclass
class MonkElementsLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkElementsFeatures.StrideOfTheElements())
        return data


@attr.dataclass
class MonkElementsLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(MonkElementsFeatures.ElementalEpitome())
        return data


class MonkElementsCustomStarterClassArgs(MonkCustomStarterClassArgs):
    def __init__(
        self,
        skills: MonkSkillsStatBlock,
        monk_level: int,
        unarmed_strike: Ability,
    ):
        super().__init__(
            subclass=MonkSubclass.ELEMENTS.value,
            skills=skills,
            monk_level=monk_level,
            unarmed_strike=unarmed_strike,
        )


class MonkElementsMulticlassBuilder(MonkMulticlassBuilder):

    def __init__(
        self,
        monk_level_features: ClassBuilder.BaseClassLevelFeatures,
        monk_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            monk_level_features=monk_level_features,
            monk_level=monk_level,
            subclass=MonkSubclass.ELEMENTS.value,
            replace_spells=replace_spells,
        )
