from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WarlockBase import (
    WarlockMulticlassBuilder,
    WarlockCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WarlockSubclass
from Features.ClassFeatures.Warlock import WarlockGreatOldOneFeatures
from Spells.Definitions import (
    BardLevel1Spells,
    BardLevel5Spells,
    SorcererLevel2Spells,
    SorcererLevel3Spells,
    SorcererLevel4Spells,
    SorcererLevel5Spells,
    WarlockLevel1Spells,
    WarlockLevel3Spells,
    WarlockLevel4Spells,
)
from StatBlocks.SkillsStatBlock import WarlockSkillsStatBlock


@attr.dataclass
class GreatOldOneWarlockLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockGreatOldOneFeatures.GreatOldOneSpells())
        data.add_feature(WarlockGreatOldOneFeatures.AwakenedMind())
        data.add_feature(WarlockGreatOldOneFeatures.PsychicSpells())
        data.add_spell(SorcererLevel2Spells.DETECT_THOUGHTS)
        data.add_spell(BardLevel1Spells.DISSONANT_WHISPERS)
        data.add_spell(SorcererLevel2Spells.PHANTASMAL_FORCE)
        data.add_spell(WarlockLevel1Spells.TASHAS_HIDEOUS_LAUGHTER)
        return data


@attr.dataclass
class GreatOldOneWarlockLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel3Spells.CLAIRVOYANCE)
        data.add_spell(WarlockLevel3Spells.HUNGER_OF_HADAR)
        return data


@attr.dataclass
class GreatOldOneWarlockLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockGreatOldOneFeatures.ClairvoyantCombatant())
        return data


@attr.dataclass
class GreatOldOneWarlockLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel4Spells.CONFUSION)
        data.add_spell(WarlockLevel4Spells.SUMMON_ABERRATION)
        return data


@attr.dataclass
class GreatOldOneWarlockLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(BardLevel5Spells.MODIFY_MEMORY)
        data.add_spell(SorcererLevel5Spells.TELEKINESIS)
        return data


@attr.dataclass
class GreatOldOneWarlockLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockGreatOldOneFeatures.EldritchHex())
        data.add_feature(WarlockGreatOldOneFeatures.ThoughtShield())
        return data


@attr.dataclass
class GreatOldOneWarlockLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WarlockGreatOldOneFeatures.CreateThrall())
        return data


class WarlockGreatOldOneCustomStarterClassArgs(WarlockCustomStarterClassArgs):
    def __init__(
        self,
        skills: WarlockSkillsStatBlock,
    ):
        super().__init__(
            subclass=WarlockSubclass.THE_GREAT_OLD_ONE.value,
            skills=skills,
        )


class GreatOldOneWarlockMulticlassBuilder(WarlockMulticlassBuilder):

    def __init__(
        self,
        warlock_level_features: ClassBuilder.BaseClassLevelFeatures,
        warlock_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            warlock_level_features=warlock_level_features,
            warlock_level=warlock_level,
            subclass=WarlockSubclass.THE_GREAT_OLD_ONE.value,
            replace_spells=replace_spells,
        )
