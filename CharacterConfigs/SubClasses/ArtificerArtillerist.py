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
from Spells.Definitions import (
    ArtificerLevel1Spells,
    ArtificerLevel2Spells,
    ArtificerLevel3Spells,
    ArtificerLevel4Spells,
    ArtificerLevel5Spells,
    DruidLevel3Spells,
)
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


@attr.dataclass
class ArtificerArtilleristLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.ArtilleristToolsOfTheTrade())
        data.add_feature(ArtificerFeatures.ArtilleristSpells())
        data.add_feature(ArtificerFeatures.EldritchCannon())
        data.add_spell(ArtificerLevel1Spells.SHIELD)
        data.add_spell(ArtificerLevel1Spells.THUNDERWAVE)
        return data


@attr.dataclass
class ArtificerArtilleristLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.ArcaneFirearm())
        data.add_spell(ArtificerLevel2Spells.SCORCHING_RAY)
        data.add_spell(ArtificerLevel2Spells.SHATTER)
        return data


@attr.dataclass
class ArtificerArtilleristLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.ExplosiveCannon())
        data.add_spell(ArtificerLevel3Spells.FIREBALL)
        data.add_spell(DruidLevel3Spells.WIND_WALL)
        return data


@attr.dataclass
class ArtificerArtilleristLevel13(ClassBuilder.SubclassLevel13):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ArtificerLevel4Spells.ICE_STORM)
        data.add_spell(ArtificerLevel4Spells.WALL_OF_FIRE)
        return data


@attr.dataclass
class ArtificerArtilleristLevel15(ClassBuilder.SubclassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerFeatures.FortifiedPosition())
        return data


@attr.dataclass
class ArtificerArtilleristLevel17(ClassBuilder.SubclassLevel17):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ArtificerLevel5Spells.CONE_OF_COLD)
        data.add_spell(ArtificerLevel5Spells.WALL_OF_FORCE)
        return data


class ArtificerArtilleristCustomStarterClassArgs(ArtificerCustomStarterClassArgs):
    def __init__(
        self,
        skills: ArtificerSkillsStatBlock,
    ):
        super().__init__(
            subclass=ArtificerSubclass.ARTILLERIST.value,
            skills=skills,
        )


class ArtificerArtilleristMulticlassBuilder(ArtificerMulticlassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            artificer_level_features=artificer_level_features,
            artificer_level=artificer_level,
            subclass=ArtificerSubclass.ARTILLERIST.value,
            replace_spells=replace_spells,
        )
