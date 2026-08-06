from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import BardSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Bard import BardWhispersFeatures
from CharacterContent.Features.ClassFeatures.Bard import BardFeatures
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class BardWhispersLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        bardic_inspiration: BardFeatures.BardicInspiration = data.get_features_by_type(
            BardFeatures.BardicInspiration
        )[0]
        bardic_inspiration.extend_feature(BardWhispersFeatures.PsychicBlades())
        data.add_feature(BardWhispersFeatures.WordsOfTerror())
        return data


@attr.dataclass
class BardWhispersLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardWhispersFeatures.MantleOfWhispers())
        return data


@attr.dataclass
class BardWhispersLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardWhispersFeatures.ShadowLore())
        return data


class BardWhispersCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: BardSkillsStatBlock,
    ):
        super().__init__(
            subclass=BardSubclass2014.WHISPERS.value,
            skills=skills,
        )


class BardWhispersMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.WHISPERS.value,
            replace_spells=replace_spells,
        )
