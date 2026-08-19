from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import Ability, BarbarianSubclass
from CharacterContent.Features.SubClassFeatures.Barbarian import BarbarianPathOfTheWildHeartFeatures
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures
from CharacterContent.Spells.SpellLists import (
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel5Spells,
)
from StatBlocks.SkillsStatBlock import BarbarianSkillsStatBlock


@attr.dataclass
class BarbarianWildHeartLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheWildHeartFeatures.AnimalSpeaker())
        data.add_spell(
            DruidLevel2Spells.BEAST_SENSE,
            Ability.WISDOM,
            additional_ruling="Ritual only",
        )
        data.add_spell(
            DruidLevel1Spells.SPEAK_WITH_ANIMALS,
            Ability.WISDOM,
            additional_ruling="Ritual only",
        )
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.extend_feature(BarbarianPathOfTheWildHeartFeatures.RageOfTheWilds())
        return data


@attr.dataclass
class BarbarianWildHeartLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheWildHeartFeatures.AspectOfTheWilds())
        return data


@attr.dataclass
class BarbarianWildHeartLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BarbarianPathOfTheWildHeartFeatures.NatureSpeaker())
        data.add_spell(
            DruidLevel5Spells.COMMUNE_WITH_NATURE,
            Ability.WISDOM,
            additional_ruling="Ritual only",
        )
        return data


@attr.dataclass
class BarbarianWildHeartLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.extend_feature(BarbarianPathOfTheWildHeartFeatures.PowerOfTheWilds())
        return data


class BarbarianWildHeartCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: BarbarianSkillsStatBlock,
    ):
        super().__init__(
            subclass=BarbarianSubclass.PATH_OF_THE_WILD_HEART.value,
            skills=skills,
        )


class BarbarianWildHeartMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass.PATH_OF_THE_WILD_HEART.value,
            replace_spells=replace_spells,
        )
