from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BarbarianBase import (
    BarbarianMulticlassBuilder,
    BarbarianCustomStarterClassArgs,
)
from Model.Character import Character
from Core.Definitions import BarbarianSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Barbarian import (
    BarbarianPathOfWildMagicFeatures,
)
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures


@attr.dataclass
class BarbarianWildMagicLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(BarbarianPathOfWildMagicFeatures.MagicAwareness())
        data.add_feature(
            BarbarianPathOfWildMagicFeatures.WildSurge(), extends=BarbarianFeatures.Rage
        )
        return data


@attr.dataclass
class BarbarianWildMagicLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(BarbarianPathOfWildMagicFeatures.BolsteringMagic())
        return data


@attr.dataclass
class BarbarianWildMagicLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            BarbarianPathOfWildMagicFeatures.UnstableBacklash(),
            extends=BarbarianFeatures.Rage,
        )
        return data


@attr.dataclass
class BarbarianWildMagicLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            BarbarianPathOfWildMagicFeatures.ControlledSurge(),
            extends=BarbarianFeatures.Rage,
        )
        return data


class BarbarianWildMagicCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BarbarianSubclass2014.PATH_OF_WILD_MAGIC.value,
            skills=skills,
        )


class BarbarianWildMagicMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass2014.PATH_OF_WILD_MAGIC.value,
            replace_spells=replace_spells,
        )
