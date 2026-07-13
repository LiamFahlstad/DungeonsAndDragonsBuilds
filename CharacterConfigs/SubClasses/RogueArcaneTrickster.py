from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RogueSubclass
from Features.ClassFeatures.Rogue import RogueArcaneTricksterFeatures
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock


@attr.dataclass
class RogueArcaneTricksterLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueArcaneTricksterFeatures.Spellcasting())
        data.add_feature(RogueArcaneTricksterFeatures.MageHandLegerdemain())
        return data


@attr.dataclass
class RogueArcaneTricksterLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueArcaneTricksterFeatures.MagicalAmbush())
        return data


@attr.dataclass
class RogueArcaneTricksterLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueArcaneTricksterFeatures.VersatileTrickster())
        return data


@attr.dataclass
class RogueArcaneTricksterLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueArcaneTricksterFeatures.SpellThief())
        return data


class RogueArcaneTricksterCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass.ARCANE_TRICKSTER.value,
            skills=skills,
        )


class RogueArcaneTricksterMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.ARCANE_TRICKSTER.value,
            replace_spells=replace_spells,
        )
