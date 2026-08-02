from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RangerBase import (
    RangerMulticlassBuilder,
    RangerCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import RangerSubclass
from CharacterContent.Features.SubClassFeatures.Ranger import RangerWinterWalkerFeatures
from CharacterContent.Spells.SpellLists import (
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
class RangerWinterWalkerLevel3(ClassBuilder.SubclassLevel3):

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
class RangerWinterWalkerLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(EnchantmentLevel2Spells.HOLD_PERSON)
        return data


@attr.dataclass
class RangerWinterWalkerLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerWinterWalkerFeatures.FortifyingSoul())
        return data


@attr.dataclass
class RangerWinterWalkerLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(AbjurationLevel3Spells.REMOVE_CURSE)
        return data


@attr.dataclass
class RangerWinterWalkerLevel11(ClassBuilder.SubclassLevel11):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerWinterWalkerFeatures.ChillingRetribution())
        return data


@attr.dataclass
class RangerWinterWalkerLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(EvocationLevel4Spells.ICE_STORM)
        return data


@attr.dataclass
class RangerWinterWalkerLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RangerWinterWalkerFeatures.FrozenHaunt())
        return data


@attr.dataclass
class RangerWinterWalkerLevel17(ClassBuilder.SubclassLevel17):

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


class RangerWinterWalkerMulticlassBuilder(RangerMulticlassBuilder):

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
