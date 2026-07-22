from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import PaladinSubclass2014
from Features.SubClassFeatures2014.Paladin import PaladinVengeanceFeatures
from Spells.SpellLists import (
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    PaladinLevel4Spells,
    RangerLevel1Spells,
    SorcererLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class VengeancePaladinLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinVengeanceFeatures.VengeanceSpells())
        data.add_feature(PaladinVengeanceFeatures.AbjureEnemy())
        data.add_feature(PaladinVengeanceFeatures.VowOfEnmity())
        data.add_spell(ClericLevel1Spells.BANE)
        data.add_spell(RangerLevel1Spells.HUNTERS_MARK)
        return data


@attr.dataclass
class VengeancePaladinLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel2Spells.HOLD_PERSON)
        data.add_spell(SorcererLevel2Spells.MISTY_STEP)
        return data


@attr.dataclass
class VengeancePaladinLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinVengeanceFeatures.RelentlessAvenger())
        return data


@attr.dataclass
class VengeancePaladinLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel3Spells.HASTE)
        data.add_spell(ClericLevel3Spells.PROTECTION_FROM_ENERGY)
        return data


@attr.dataclass
class VengeancePaladinLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel4Spells.BANISHMENT)
        data.add_spell(WizardLevel4Spells.DIMENSION_DOOR)
        return data


@attr.dataclass
class VengeancePaladinLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinVengeanceFeatures.SoulOfVengeance())
        return data


@attr.dataclass
class VengeancePaladinLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(WizardLevel5Spells.HOLD_MONSTER)
        data.add_spell(WizardLevel5Spells.SCRYING)
        return data


@attr.dataclass
class VengeancePaladinLevel20(ClassBuilder.SubclassLevel20):

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
            subclass=PaladinSubclass2014.VENGEANCE.value,
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
            subclass=PaladinSubclass2014.VENGEANCE.value,
            replace_spells=replace_spells,
        )
