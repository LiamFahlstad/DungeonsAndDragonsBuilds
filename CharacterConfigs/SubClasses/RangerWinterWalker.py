from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import RangerSubclass
from Features.ClassFeatures.Ranger import RangerWinterWalkerFeatures
from Spells.Definitions import (
    AbjurationLevel3Spells,
    BardLevel4Spells,
    ClericLevel4Spells,
    ConjurationLevel1Spells,
    EnchantmentLevel2Spells,
    EvocationLevel4Spells,
    EvocationLevel5Spells,
    TransmutationLevel2Spells,
    WizardLevel3Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import RangerSkillsStatBlock


@attr.dataclass
class WinterWalkerRangerLevel3(ClassBuilder.SubclassLevel3):
    level: int = attr.field(init=False, default=3)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerWinterWalkerFeatures.FrigidExplorer())
        data.add_feature(RangerWinterWalkerFeatures.WinterWalkerSpells())
        data.add_feature(RangerWinterWalkerFeatures.HuntersRime())
        data.add_spell(ConjurationLevel1Spells.ICE_KNIFE)
        return data


@attr.dataclass
class WinterWalkerRangerLevel5(ClassBuilder.SubclassLevel5):
    level: int = attr.field(init=False, default=5)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(EnchantmentLevel2Spells.HOLD_PERSON)
        return data


@attr.dataclass
class WinterWalkerRangerLevel7(ClassBuilder.SubclassLevel7):
    level: int = attr.field(init=False, default=7)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerWinterWalkerFeatures.FortifyingSoul())
        return data


@attr.dataclass
class WinterWalkerRangerLevel9(ClassBuilder.SubclassLevel9):
    level: int = attr.field(init=False, default=9)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(AbjurationLevel3Spells.REMOVE_CURSE)
        return data


@attr.dataclass
class WinterWalkerRangerLevel11(ClassBuilder.SubclassLevel11):
    level: int = attr.field(init=False, default=11)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerWinterWalkerFeatures.ChillingRetribution())
        return data


@attr.dataclass
class WinterWalkerRangerLevel13(ClassBuilder.SubclassLevel13):
    level: int = attr.field(init=False, default=13)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(EvocationLevel4Spells.ICE_STORM)
        return data


@attr.dataclass
class WinterWalkerRangerLevel15(ClassBuilder.SubclassLevel15):
    level: int = attr.field(init=False, default=15)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerWinterWalkerFeatures.FrozenHaunt())
        return data


@attr.dataclass
class WinterWalkerRangerLevel17(ClassBuilder.SubclassLevel17):
    level: int = attr.field(init=False, default=17)

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(EvocationLevel5Spells.CONE_OF_COLD)
        return data


class RangerWinterWalkerCustomStarterClassArgs(RangerCustomStarterClassArgs):
    def __init__(
        self,
        skills: RangerSkillsStatBlock,
    ):
        super().__init__(
            subclass=RangerSubclass.WINTER_WALKER.value,
            skills=skills,
        )


class WinterWalkerRangerMulticlassBuilder(RangerMulticlassBuilder):

    def __init__(
        self,
        ranger_level_features: ClassBuilder.BaseClassLevelFeatures,
        ranger_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            ranger_level_features=ranger_level_features,
            ranger_level=ranger_level,
            subclass=RangerSubclass.WINTER_WALKER.value,
            replace_spells=replace_spells,
        )
