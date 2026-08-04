from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import WarlockSubclass2014, WarlockGenieKind
from CharacterContent.Features.SubClassFeatures2014.Warlock import WarlockTheGenieFeatures
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class WarlockTheGenieLevel3(ClassBuilder.SubclassLevel3):
    genie_kind: WarlockGenieKind

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheGenieFeatures.GenieExpandedSpells(kind=self.genie_kind))
        data.add_feature(WarlockTheGenieFeatures.GeniesVessel(kind=self.genie_kind))
        return data


@attr.dataclass
class WarlockTheGenieLevel6(ClassBuilder.SubclassLevel6):
    genie_kind: WarlockGenieKind

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheGenieFeatures.ElementalGift(kind=self.genie_kind))
        return data


@attr.dataclass
class WarlockTheGenieLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheGenieFeatures.SanctuaryVessel())
        return data


@attr.dataclass
class WarlockTheGenieLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheGenieFeatures.LimitedWish())
        return data


class WarlockTheGenieCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass2014.THE_GENIE.value,
            skills=skills,
        )


class WarlockTheGenieMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass2014.THE_GENIE.value,
            replace_spells=replace_spells,
        )
