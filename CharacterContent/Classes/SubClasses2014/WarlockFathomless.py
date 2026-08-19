from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import WarlockSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Warlock import WarlockFathomlessFeatures
from CharacterContent.Spells.SpellLists import ConjurationLevel4Spells
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class WarlockFathomlessLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFathomlessFeatures.ExpandedSpellList())
        data.add_feature(WarlockFathomlessFeatures.TentacleOfTheDeep())
        data.add_feature(WarlockFathomlessFeatures.GiftOfTheSea())
        return data


@attr.dataclass
class WarlockFathomlessLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFathomlessFeatures.OceanicSoul())
        tentacle_of_the_deep: WarlockFathomlessFeatures.TentacleOfTheDeep = data.get_features_by_type(
            WarlockFathomlessFeatures.TentacleOfTheDeep
        )[0]
        tentacle_of_the_deep.extend_feature(WarlockFathomlessFeatures.GuardianCoil())
        return data


@attr.dataclass
class WarlockFathomlessLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFathomlessFeatures.GraspingTentacles())
        data.add_spell(
            ConjurationLevel4Spells.EVARDS_BLACK_TENTACLES,
            additional_ruling="Doesn't count against the number of Warlock spells known",
        )
        return data


@attr.dataclass
class WarlockFathomlessLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFathomlessFeatures.FathomlessPlunge())
        return data


class WarlockFathomlessCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass2014.THE_FATHOMLESS.value,
            skills=skills,
        )


class WarlockFathomlessMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass2014.THE_FATHOMLESS.value,
            replace_spells=replace_spells,
        )
