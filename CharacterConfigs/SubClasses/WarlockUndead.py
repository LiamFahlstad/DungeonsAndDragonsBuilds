from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WarlockSubclass
from Features.ClassFeatures.Warlock import WarlockUndeadFeatures
from Spells.Definitions import (
    BardLevel3Spells,
    BardLevel4Spells,
    DruidLevel5Spells,
    SorcererLevel1Spells,
    SorcererLevel2Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
    WarlockLevel1Spells,
    WarlockLevel3Spells,
)
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class UndeadWarlockLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockUndeadFeatures.UndeadSpells())
        data.add_feature(WarlockUndeadFeatures.FormOfDread())
        data.add_spell(WarlockLevel1Spells.BANE)
        data.add_spell(SorcererLevel2Spells.BLINDNESS_DEAFNESS)
        data.add_spell(SorcererLevel2Spells.PHANTASMAL_FORCE)
        data.add_spell(SorcererLevel1Spells.RAY_OF_SICKNESS)
        return data


@attr.dataclass
class UndeadWarlockLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel3Spells.SPEAK_WITH_DEAD)
        data.add_spell(WarlockLevel3Spells.SUMMON_UNDEAD)
        return data


@attr.dataclass
class UndeadWarlockLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockUndeadFeatures.GraveTouched())
        return data


@attr.dataclass
class UndeadWarlockLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel4Spells.GREATER_INVISIBILITY)
        data.add_spell(BardLevel4Spells.PHANTASMAL_KILLER)
        return data


@attr.dataclass
class UndeadWarlockLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel5Spells.ANTILIFE_SHELL)
        data.add_spell(SorcererLevel5Spells.CLOUDKILL)
        return data


@attr.dataclass
class UndeadWarlockLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockUndeadFeatures.NecroticHusk())
        return data


@attr.dataclass
class UndeadWarlockLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockUndeadFeatures.SuperiorDread())
        return data


class WarlockUndeadCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass.THE_UNDEAD.value,
            skills=skills,
        )


class UndeadWarlockMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_UNDEAD.value,
            replace_spells=replace_spells,
        )
