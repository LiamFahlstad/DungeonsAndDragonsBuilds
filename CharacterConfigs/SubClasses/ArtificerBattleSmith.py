from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import (
    ArtificerMulticlassBuilder,
    ArtificerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ArtificerSubclass
from Features.ClassFeatures import ArtificerFeatures
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


@attr.dataclass
class ArtificerBattleSmithLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.BattleSmithToolsOfTheTrade())
        data.add_feature(ArtificerFeatures.BattleSmithSpells())
        data.add_feature(ArtificerFeatures.BattleReady())
        data.add_feature(ArtificerFeatures.SteelDefender())
        return data


@attr.dataclass
class ArtificerBattleSmithLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.BattleSmithExtraAttack())
        return data


@attr.dataclass
class ArtificerBattleSmithLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.ArcaneJolt())
        return data


@attr.dataclass
class ArtificerBattleSmithLevel15(ClassBuilder.SubclassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.ImprovedDefender())
        return data


class ArtificerBattleSmithCustomStarterClassArgs(ArtificerCustomStarterClassArgs):
    def __init__(
        self,
        skills: ArtificerSkillsStatBlock,
    ):
        super().__init__(
            subclass=ArtificerSubclass.BATTLE_SMITH.value,
            skills=skills,
        )


class ArtificerBattleSmithMulticlassBuilder(ArtificerMulticlassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            artificer_level_features=artificer_level_features,
            artificer_level=artificer_level,
            subclass=ArtificerSubclass.BATTLE_SMITH.value,
            replace_spells=replace_spells,
        )
