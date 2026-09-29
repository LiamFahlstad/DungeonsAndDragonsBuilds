from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import BardSubclass2014
from CharacterContent.Features.CombatFeatures import FightingStyles
from CharacterContent.Features.SubClassFeatures2014.Bard import BardSwordsFeatures
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class BardSwordsLevel3(ClassBuilder.SubclassLevel3):
    fighting_style: FightingStyles.FightingStyle

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardSwordsFeatures.BonusProficiencies())
        data.add_feature(BardSwordsFeatures.BladeFlourish())
        data.add_fighting_style(self.fighting_style)
        return data


@attr.dataclass
class BardSwordsLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardSwordsFeatures.ExtraAttack())
        return data


@attr.dataclass
class BardSwordsLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        blade_flourish: BardSwordsFeatures.BladeFlourish = data.get_features_by_type(
            BardSwordsFeatures.BladeFlourish
        )[0]
        blade_flourish.extend_feature(BardSwordsFeatures.MastersFlourish())
        return data


class BardSwordsCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: BardSkillsStatBlock,
    ):
        super().__init__(
            subclass=BardSubclass2014.SWORD.value,
            skills=skills,
        )


class BardSwordsMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.SWORD.value,
            replace_spells=replace_spells,
        )
