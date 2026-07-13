from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import PaladinSubclass
from Features.ClassFeatures.Paladin import PaladinAncientsFeatures, PaladinFeatures
from Spells.SpellLists import (
    ConjurationLevel1Spells,
    ConjurationLevel2Spells,
    DivinationLevel1Spells,
    DruidLevel2Spells,
    RangerLevel3Spells,
    RangerLevel5Spells,
    WizardLevel4Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class AncientsPaladinLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        channel_divinity_feature: PaladinFeatures.ChannelDivinity = (
            data.get_features_by_type(PaladinFeatures.ChannelDivinity)[0]
        )
        channel_divinity_feature.extend_feature(PaladinAncientsFeatures.NaturesWrath())
        data.add_spell(ConjurationLevel1Spells.ENSNARING_STRIKE)
        data.add_spell(DivinationLevel1Spells.SPEAK_WITH_ANIMALS)
        return data


@attr.dataclass
class AncientsPaladinLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ConjurationLevel2Spells.MISTY_STEP)
        data.add_spell(DruidLevel2Spells.MOONBEAM)
        return data


@attr.dataclass
class AncientsPaladinLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinAncientsFeatures.AuraOfWarding())
        return data


@attr.dataclass
class AncientsPaladinLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(RangerLevel3Spells.PLANT_GROWTH)
        data.add_spell(RangerLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class AncientsPaladinLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel4Spells.ICE_STORM)
        data.add_spell(WizardLevel4Spells.STONESKIN)
        return data


@attr.dataclass
class AncientsPaladinLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinAncientsFeatures.UndyingSentinel())
        return data


@attr.dataclass
class AncientsPaladinLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(RangerLevel5Spells.COMMUNE_WITH_NATURE)
        data.add_spell(RangerLevel5Spells.TREE_STRIDE)
        return data


@attr.dataclass
class AncientsPaladinLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinAncientsFeatures.ElderChampion())
        return data


class PaladinAncientsCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: PaladinSkillsStatBlock,
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_THE_ANCIENTS.value,
            skills=skills,
        )


class AncientsPaladinMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_THE_ANCIENTS.value,
            replace_spells=replace_spells,
        )
