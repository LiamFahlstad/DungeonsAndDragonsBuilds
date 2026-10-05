from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Model.Character import Character
from Core.Definitions import BardSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Bard import BardCreationFeatures
from CharacterContent.Features.ClassFeatures.Bard import BardFeatures


@attr.dataclass
class BardCreationLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            BardCreationFeatures.MoteOfPotential(),
            extends=BardFeatures.BardicInspiration,
        )
        data.add_feature(BardCreationFeatures.PerformanceOfCreation())
        return data


@attr.dataclass
class BardCreationLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(BardCreationFeatures.AnimatingPerformance())
        return data


@attr.dataclass
class BardCreationLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            BardCreationFeatures.CreativeCrescendo(),
            extends=BardCreationFeatures.PerformanceOfCreation,
        )
        return data


class BardCreationCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BardSubclass2014.CREATION.value,
            skills=skills,
        )


class BardCreationMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass2014.CREATION.value,
            replace_spells=replace_spells,
        )
