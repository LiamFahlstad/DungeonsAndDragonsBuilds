from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import PaladinSubclass2014
from CharacterContent.Features.SubClassFeatures2014.Paladin import PaladinCrownFeatures
from CharacterContent.Spells.SpellLists import (
    PaladinLevel1Spells,
    PaladinLevel2Spells,
    PaladinLevel3Spells,
    ClericLevel3Spells,
    PaladinLevel4Spells,
    ClericLevel4Spells,
    PaladinLevel5Spells,
)
from StatBlocks.SkillsStatBlock import PaladinSkillsStatBlock


@attr.dataclass
class PaladinCrownLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinCrownFeatures.CrownSpells())
        data.add_feature(PaladinCrownFeatures.ChampionChallenge())
        data.add_feature(PaladinCrownFeatures.TurnTheTide())
        data.add_spell(PaladinLevel1Spells.COMMAND)
        data.add_spell(PaladinLevel1Spells.COMPELLED_DUEL)
        return data


@attr.dataclass
class PaladinCrownLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel2Spells.WARDING_BOND)
        data.add_spell(PaladinLevel2Spells.ZONE_OF_TRUTH)
        return data


@attr.dataclass
class PaladinCrownLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinCrownFeatures.DivineAllegiance())
        return data


@attr.dataclass
class PaladinCrownLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel3Spells.AURA_OF_VITALITY)
        data.add_spell(ClericLevel3Spells.SPIRIT_GUARDIANS)
        return data


@attr.dataclass
class PaladinCrownLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel4Spells.BANISHMENT)
        data.add_spell(ClericLevel4Spells.GUARDIAN_OF_FAITH)
        return data


@attr.dataclass
class PaladinCrownLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinCrownFeatures.UnyieldingSaint())
        return data


@attr.dataclass
class PaladinCrownLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(PaladinLevel5Spells.CIRCLE_OF_POWER)
        data.add_spell(PaladinLevel5Spells.GEAS)
        return data


@attr.dataclass
class PaladinCrownLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(PaladinCrownFeatures.ExaltedChampion())
        return data


class PaladinCrownCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: PaladinSkillsStatBlock,
    ):
        super().__init__(
            subclass=PaladinSubclass2014.CROWN.value,
            skills=skills,
        )


class PaladinCrownMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass2014.CROWN.value,
            replace_spells=replace_spells,
        )
