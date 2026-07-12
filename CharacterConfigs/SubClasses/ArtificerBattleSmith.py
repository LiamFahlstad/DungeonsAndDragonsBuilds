from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import (
    ArtificerMulticlassBuilder,
    ArtificerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ArtificerSubclass
from Features.ClassFeatures.Artificer import ArtificerBattleSmithFeatures
from Spells.Definitions import (
    ArtificerLevel1Spells,
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    PaladinLevel4Spells,
    PaladinLevel5Spells,
    RangerLevel3Spells,
    SorcererLevel4Spells,
    ArtificerLevel5Spells,
)
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


@attr.dataclass
class ArtificerBattleSmithLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerBattleSmithFeatures.BattleSmithToolsOfTheTrade())
        data.add_feature(ArtificerBattleSmithFeatures.BattleSmithSpells())
        data.add_feature(ArtificerBattleSmithFeatures.BattleReady())
        data.add_feature(ArtificerBattleSmithFeatures.SteelDefender())
        data.add_spell(PaladinLevel1Spells.HEROISM)
        data.add_spell(ArtificerLevel1Spells.SHIELD)
        return data


@attr.dataclass
class ArtificerBattleSmithLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerBattleSmithFeatures.BattleSmithExtraAttack())
        data.add_spell(PaladinLevel2Spells.SHINING_SMITE)
        data.add_spell(PaladinLevel2Spells.WARDING_BOND)
        return data


@attr.dataclass
class ArtificerBattleSmithLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerBattleSmithFeatures.ArcaneJolt())
        data.add_spell(PaladinLevel3Spells.AURA_OF_VITALITY)
        data.add_spell(RangerLevel3Spells.CONJURE_BARRAGE)
        return data


@attr.dataclass
class ArtificerBattleSmithLevel13(ClassBuilder.SubclassLevel13):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel4Spells.AURA_OF_PURITY)
        data.add_spell(SorcererLevel4Spells.FIRE_SHIELD)
        return data


@attr.dataclass
class ArtificerBattleSmithLevel15(ClassBuilder.SubclassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerBattleSmithFeatures.ImprovedDefender())
        return data


@attr.dataclass
class ArtificerBattleSmithLevel17(ClassBuilder.SubclassLevel17):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel5Spells.BANISHING_SMITE)
        data.add_spell(ArtificerLevel5Spells.MASS_CURE_WOUNDS)
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
