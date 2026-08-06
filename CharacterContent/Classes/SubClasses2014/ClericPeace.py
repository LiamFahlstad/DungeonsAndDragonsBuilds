from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import ClericSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericPeaceFeatures
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericPeaceLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericPeaceFeatures.ImplementOfPeace())
        data.add_feature(ClericPeaceFeatures.PeaceDomainSpells())
        data.add_feature(ClericPeaceFeatures.EmboldeningBond())
        data.add_feature(ClericPeaceFeatures.BalmOfPeaceChannelDivinity())
        return data


@attr.dataclass
class ClericPeaceLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        emboldening_bond: ClericPeaceFeatures.EmboldeningBond = data.get_features_by_type(
            ClericPeaceFeatures.EmboldeningBond
        )[0]
        emboldening_bond.extend_feature(ClericPeaceFeatures.ProtectiveBond())
        return data


@attr.dataclass
class ClericPeaceLevel8(ClassBuilder.SubclassLevel8):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericPeaceFeatures.PotentSpellcasting())
        return data


@attr.dataclass
class ClericPeaceLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        emboldening_bond: ClericPeaceFeatures.EmboldeningBond = data.get_features_by_type(
            ClericPeaceFeatures.EmboldeningBond
        )[0]
        emboldening_bond.extend_feature(ClericPeaceFeatures.ExpansiveBond())
        return data


class ClericPeaceCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass2014.PEACE.value,
            skills=skills,
        )


class ClericPeaceMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass2014.PEACE.value,
            replace_spells=replace_spells,
        )
