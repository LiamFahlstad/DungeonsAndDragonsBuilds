from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WarlockSubclass
from Features.ClassFeatures import WarlockFeatures
from Spells.Definitions import (
    BardLevel1Spells,
    BardLevel2Spells,
    BardLevel3Spells,
    BardLevel4Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
)
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class ArchfeyWarlockLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.ArchfeySpells())
        data.add_feature(WarlockFeatures.StepsOfTheFey())
        data.add_spell(BardLevel1Spells.FAERIE_FIRE)
        data.add_spell(BardLevel2Spells.CALM_EMOTIONS)
        data.add_spell(BardLevel2Spells.MISTY_STEP)
        data.add_spell(BardLevel2Spells.PHANTASMAL_FORCE)
        data.add_spell(BardLevel1Spells.SLEEP)
        return data


@attr.dataclass
class ArchfeyWarlockLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.BLINK)
        data.add_spell(BardLevel3Spells.PLANT_GROWTH)
        return data


@attr.dataclass
class ArchfeyWarlockLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.MistyEscape())
        return data


@attr.dataclass
class ArchfeyWarlockLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel4Spells.DOMINATE_BEAST)
        data.add_spell(SorcererLevel4Spells.GREATER_INVISIBILITY)
        return data


@attr.dataclass
class ArchfeyWarlockLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel5Spells.DOMINATE_PERSON)
        data.add_spell(SorcererLevel5Spells.SEEMING)
        return data


@attr.dataclass
class ArchfeyWarlockLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.BeguilingDefenses())
        return data


@attr.dataclass
class ArchfeyWarlockLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockFeatures.BewitchingMagic())
        return data


class WarlockArchfeyCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass.THE_ARCHFEY.value,
            skills=skills,
        )


class ArchfeyWarlockMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_ARCHFEY.value,
            replace_spells=replace_spells,
        )
