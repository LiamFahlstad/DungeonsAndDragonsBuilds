from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import (
    ArtificerMulticlassBuilder,
    ArtificerCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import ArtificerSubclass2014
from Features.SubClassFeatures2014.Artificer import ArtificerArtilleristFeatures
from Spells.SpellLists import (
    BardLevel1Spells,
    BardLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    SorcererLevel1Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


@attr.dataclass
class ArtificerArtilleristLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerArtilleristFeatures.ArtilleristToolsOfTheTrade())
        data.add_feature(ArtificerArtilleristFeatures.ArtilleristSpells())
        data.add_feature(ArtificerArtilleristFeatures.EldritchCannon())
        data.add_spell(SorcererLevel1Spells.SHIELD)
        data.add_spell(BardLevel1Spells.THUNDERWAVE)
        return data


@attr.dataclass
class ArtificerArtilleristLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerArtilleristFeatures.ArcaneFirearm())
        data.add_spell(SorcererLevel2Spells.SCORCHING_RAY)
        data.add_spell(BardLevel2Spells.SHATTER)
        return data


@attr.dataclass
class ArtificerArtilleristLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerArtilleristFeatures.ExplosiveCannon())
        data.add_spell(SorcererLevel3Spells.FIREBALL)
        data.add_spell(DruidLevel3Spells.WIND_WALL)
        return data


@attr.dataclass
class ArtificerArtilleristLevel13(ClassBuilder.SubclassLevel13):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel4Spells.ICE_STORM)
        data.add_spell(DruidLevel4Spells.WALL_OF_FIRE)
        return data


@attr.dataclass
class ArtificerArtilleristLevel15(ClassBuilder.SubclassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerArtilleristFeatures.FortifiedPosition())
        return data


@attr.dataclass
class ArtificerArtilleristLevel17(ClassBuilder.SubclassLevel17):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel5Spells.CONE_OF_COLD)
        data.add_spell(WizardLevel5Spells.WALL_OF_FORCE)
        return data


class ArtificerArtilleristCustomStarterClassArgs(ArtificerCustomStarterClassArgs):
    def __init__(
        self,
        skills: ArtificerSkillsStatBlock,
    ):
        super().__init__(
            subclass=ArtificerSubclass2014.ARTILLERIST.value,
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
            subclass=ArtificerSubclass2014.ARTILLERIST.value,
            replace_spells=replace_spells,
        )
