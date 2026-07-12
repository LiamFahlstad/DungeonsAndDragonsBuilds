from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ClericSubclass
from Features.ClassFeatures.Cleric import ClericLifeFeatures, ClericFeatures
from Spells.SpellLists import (
    ClericLevel1Spells,
    ClericLevel2Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
)
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericLifeLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel1Spells.BLESS)
        data.add_spell(ClericLevel1Spells.CURE_WOUNDS)
        data.add_spell(ClericLevel2Spells.AID)
        data.add_spell(ClericLevel2Spells.LESSER_RESTORATION)

        channel_divinity: ClericFeatures.ChannelDivinity = data.get_features_by_type(
            ClericFeatures.ChannelDivinity
        )[0]
        channel_divinity.extend_feature(ClericLifeFeatures.PreserveLife())
        data.add_feature(ClericLifeFeatures.DiscipleofLife())
        return data


@attr.dataclass
class ClericLifeLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel3Spells.MASS_HEALING_WORD)
        data.add_spell(ClericLevel3Spells.REVIVIFY)
        return data


@attr.dataclass
class ClericLifeLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericLifeFeatures.BlessedHealer())
        return data


@attr.dataclass
class ClericLifeLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel4Spells.AURA_OF_LIFE)
        data.add_spell(ClericLevel4Spells.DEATH_WARD)
        return data


@attr.dataclass
class ClericLifeLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel5Spells.GREATER_RESTORATION)
        data.add_spell(ClericLevel5Spells.MASS_CURE_WOUNDS)
        return data


@attr.dataclass
class ClericLifeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericLifeFeatures.SupremeHealing())
        return data


class ClericLifeCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass.LIFE.value,
            skills=skills,
        )


class ClericLifeMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.LIFE.value,
            replace_spells=replace_spells,
        )
