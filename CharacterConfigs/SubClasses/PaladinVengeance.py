from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import PaladinSubclass
from Features.ClassFeatures.Paladin import PaladinVengeanceFeatures
from Spells.SpellLists import (
    ClericLevel1Spells,
    RangerLevel1Spells,
    WarlockLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class PaladinVengeanceLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinVengeanceFeatures.VowOfEnmity())
        data.add_spell(ClericLevel1Spells.BANE)
        data.add_spell(RangerLevel1Spells.HUNTERS_MARK)
        return data


@attr.dataclass
class PaladinVengeanceLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WarlockLevel2Spells.HOLD_PERSON)
        data.add_spell(WarlockLevel2Spells.MISTY_STEP)
        return data


@attr.dataclass
class PaladinVengeanceLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinVengeanceFeatures.RelentlessAvenger())
        return data


@attr.dataclass
class PaladinVengeanceLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(WizardLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class PaladinVengeanceLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel4Spells.BANISHMENT)
        data.add_spell(WizardLevel4Spells.DIMENSION_DOOR)
        return data


@attr.dataclass
class PaladinVengeanceLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinVengeanceFeatures.SoulOfVengeance())
        return data


@attr.dataclass
class PaladinVengeanceLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.HOLD_MONSTER)
        data.add_spell(WizardLevel5Spells.SCRYING)
        return data


@attr.dataclass
class PaladinVengeanceLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinVengeanceFeatures.AvengingAngel())
        return data


class PaladinVengeanceCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: PaladinSkillsStatBlock,
    ):
        super().__init__(
            subclass=PaladinSubclass.OATH_OF_VENGEANCE.value,
            skills=skills,
        )


class PaladinVengeanceMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass.OATH_OF_VENGEANCE.value,
            replace_spells=replace_spells,
        )
