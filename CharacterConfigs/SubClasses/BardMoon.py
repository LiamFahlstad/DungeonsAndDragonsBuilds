from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import BardSubclass, Skill
from Features.ClassFeatures import BardMoonFeatures
from Spells.Definitions import DruidLevel0Spells, DruidLevel2Spells
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class BardMoonLevel3(ClassBuilder.SubclassLevel3):
    cantrip: DruidLevel0Spells
    skill: Skill

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardMoonFeatures.MoonsInspiration())
        data.add_feature(BardMoonFeatures.PrimalLore(skill=self.skill))
        data.add_cantrip(self.cantrip)
        return data


@attr.dataclass
class BardMoonLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel2Spells.MOONBEAM)
        data.add_feature(BardMoonFeatures.BlessingOfMoonlight())
        return data


@attr.dataclass
class BardMoonLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardMoonFeatures.EventidesSplendor())
        return data


class BardMoonCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: BardSkillsStatBlock,
    ):
        super().__init__(
            subclass=BardSubclass.MOON.value,
            skills=skills,
        )


class BardMoonMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass.MOON.value,
            replace_spells=replace_spells,
        )
