from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import WarlockSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Warlock import WarlockTheUndyingFeatures
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class WarlockTheUndyingLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheUndyingFeatures.UndyingExpandedSpells())
        data.add_feature(WarlockTheUndyingFeatures.AmongTheDead())
        return data


@attr.dataclass
class WarlockTheUndyingLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheUndyingFeatures.DefyDeath())
        return data


@attr.dataclass
class WarlockTheUndyingLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheUndyingFeatures.UndyingNature())
        return data


@attr.dataclass
class WarlockTheUndyingLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockTheUndyingFeatures.IndestructibleLife())
        return data


class WarlockTheUndyingCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass2014.THE_UNDYING.value,
            skills=skills,
        )


class WarlockTheUndyingMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass2014.THE_UNDYING.value,
            replace_spells=replace_spells,
        )
