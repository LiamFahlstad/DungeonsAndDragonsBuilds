from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import PaladinSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Paladin import PaladinWatchersFeatures
from CharacterContent.Features.ClassFeatures.Paladin import PaladinFeatures
from CharacterContent.Spells.SpellLists import (
    PaladinLevel1Spells,
    RangerLevel1Spells,
    DruidLevel2Spells,
    WizardLevel2Spells,
    WizardLevel3Spells,
    PaladinLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class PaladinWatchersLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinWatchersFeatures.WatchersSpells())
        channel_divinity_feature: PaladinFeatures.ChannelDivinity = (
            data.get_features_by_type(PaladinFeatures.ChannelDivinity)[0]
        )
        channel_divinity_feature.extend_feature(PaladinWatchersFeatures.WatchersWill())
        channel_divinity_feature.extend_feature(PaladinWatchersFeatures.AbjureTheExtraplanar())
        data.add_spell(PaladinLevel1Spells.DETECT_MAGIC)
        data.add_spell(RangerLevel1Spells.ALARM)
        return data


@attr.dataclass
class PaladinWatchersLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(DruidLevel2Spells.MOONBEAM)
        data.add_spell(WizardLevel2Spells.SEE_INVISIBILITY)
        return data


@attr.dataclass
class PaladinWatchersLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinWatchersFeatures.AuraOfTheSentinel())
        return data


@attr.dataclass
class PaladinWatchersLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.COUNTERSPELL)
        data.add_spell(WizardLevel3Spells.NONDETECTION)
        return data


@attr.dataclass
class PaladinWatchersLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel4Spells.AURA_OF_PURITY)
        data.add_spell(PaladinLevel4Spells.BANISHMENT)
        return data


@attr.dataclass
class PaladinWatchersLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinWatchersFeatures.VigilantRebuke())
        return data


@attr.dataclass
class PaladinWatchersLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.HOLD_MONSTER)
        data.add_spell(WizardLevel5Spells.SCRYING)
        return data


@attr.dataclass
class PaladinWatchersLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        aura_of_the_sentinel: PaladinWatchersFeatures.AuraOfTheSentinel = (
            data.get_features_by_type(PaladinWatchersFeatures.AuraOfTheSentinel)[0]
        )
        aura_of_the_sentinel.extend_feature(PaladinWatchersFeatures.AuraOfTheSentinelExpansion())
        return data


@attr.dataclass
class PaladinWatchersLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinWatchersFeatures.MortalBulwark())
        return data


class PaladinWatchersCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: PaladinSkillsStatBlock,
    ):
        super().__init__(
            subclass=PaladinSubclass2014.WATCHERS.value,
            skills=skills,
        )


class PaladinWatchersMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass2014.WATCHERS.value,
            replace_spells=replace_spells,
        )
