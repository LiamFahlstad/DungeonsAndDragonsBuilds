from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import BardSubclass2014
from Features.SubClassFeatures2014.Bard import BardEloquenceFeatures
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class BardEloquenceLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardEloquenceFeatures.SilverTongue())
        data.add_feature(BardEloquenceFeatures.UnsettlingWords())
        return data


@attr.dataclass
class BardEloquenceLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardEloquenceFeatures.UnfailingInspiration())
        data.add_feature(BardEloquenceFeatures.UniversalSpeech())
        return data


@attr.dataclass
class BardEloquenceLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardEloquenceFeatures.InfectiousInspiration())
        return data


class BardEloquenceCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: BardSkillsStatBlock,
    ):
        super().__init__(
            subclass=BardSubclass2014.ELOQUENCE.value,
            skills=skills,
        )


class BardEloquenceMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.ELOQUENCE.value,
            replace_spells=replace_spells,
        )
