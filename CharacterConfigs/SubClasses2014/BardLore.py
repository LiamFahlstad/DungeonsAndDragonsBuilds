from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import BardSubclass2014, Skill
from Features.SubClassFeatures2014.Bard import BardLoreFeatures
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class BardLoreLevel3(ClassBuilder.SubclassLevel3):
    skill_1: Skill
    skill_2: Skill
    skill_3: Skill

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(
            BardLoreFeatures.BonusProficiencies(self.skill_1, self.skill_2, self.skill_3)
        )
        data.add_feature(BardLoreFeatures.CuttingWords())
        return data


@attr.dataclass
class BardLoreLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardLoreFeatures.AdditionalMagicalSecrets())
        return data


@attr.dataclass
class BardLoreLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardLoreFeatures.PeerlessSkill())
        return data


class BardLoreCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: BardSkillsStatBlock,
    ):
        super().__init__(
            subclass=BardSubclass2014.LORE.value,
            skills=skills,
        )


class BardLoreMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.LORE.value,
            replace_spells=replace_spells,
        )
