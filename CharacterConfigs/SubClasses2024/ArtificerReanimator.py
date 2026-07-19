from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import (
    ArtificerMulticlassBuilder,
    ArtificerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ArtificerSubclass
from Features.SubClassFeatures.Artificer import ArtificerReanimatorFeatures
from Spells.SpellLists import (
    ArtificerLevel2Spells,
    BardLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    NecromancyLevel0Spells,
    NecromancyLevel1Spells,
    SorcererLevel3Spells,
    WizardLevel1Spells,
)
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


@attr.dataclass
class ArtificerReanimatorLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerReanimatorFeatures.ReanimatorSpells())
        data.add_feature(ArtificerReanimatorFeatures.ReanimatorsSkillSet())
        data.add_feature(ArtificerReanimatorFeatures.ReanimatedCompanion())
        data.add_cantrip(NecromancyLevel0Spells.SPARE_THE_DYING)
        data.add_spell(NecromancyLevel1Spells.FALSE_LIFE)
        data.add_spell(WizardLevel1Spells.WITCH_BOLT)
        return data


@attr.dataclass
class ArtificerReanimatorLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerReanimatorFeatures.StrangeModifications())
        data.add_spell(BardLevel2Spells.BLINDNESS_DEAFNESS)
        data.add_spell(ArtificerLevel2Spells.ENHANCE_ABILITY)
        return data


@attr.dataclass
class ArtificerReanimatorLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerReanimatorFeatures.ImprovedReanimation())
        data.add_feature(ArtificerReanimatorFeatures.MacabreModifications())
        data.add_spell(ClericLevel3Spells.ANIMATE_DEAD)
        data.add_spell(SorcererLevel3Spells.LIGHTNING_BOLT)
        return data


@attr.dataclass
class ArtificerReanimatorLevel13(ClassBuilder.SubclassLevel13):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel4Spells.BLIGHT)
        data.add_spell(ClericLevel4Spells.DEATH_WARD)
        return data


@attr.dataclass
class ArtificerReanimatorLevel15(ClassBuilder.SubclassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerReanimatorFeatures.RefinedReanimation())
        return data


@attr.dataclass
class ArtificerReanimatorLevel17(ClassBuilder.SubclassLevel17):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel5Spells.ANTILIFE_SHELL)
        data.add_spell(ClericLevel5Spells.RAISE_DEAD)
        return data


class ArtificerReanimatorCustomStarterClassArgs(ArtificerCustomStarterClassArgs):
    def __init__(
        self,
        skills: ArtificerSkillsStatBlock,
    ):
        super().__init__(
            subclass=ArtificerSubclass.REANIMATOR.value,
            skills=skills,
        )


class ArtificerReanimatorMulticlassBuilder(ArtificerMulticlassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            artificer_level_features=artificer_level_features,
            artificer_level=artificer_level,
            subclass=ArtificerSubclass.REANIMATOR.value,
            replace_spells=replace_spells,
        )
