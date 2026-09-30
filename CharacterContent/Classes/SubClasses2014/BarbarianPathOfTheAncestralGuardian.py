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
    BarbarianPathOfTheAncestralGuardianFeatures,
)
from CharacterContent.Features.ClassFeatures.Barbarian import BarbarianFeatures


@attr.dataclass
class BarbarianAncestralGuardianLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.extend_feature(
            BarbarianPathOfTheAncestralGuardianFeatures.AncestralProtectors()
        )
        return data


@attr.dataclass
class BarbarianAncestralGuardianLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.extend_feature(BarbarianPathOfTheAncestralGuardianFeatures.SpiritShield())
        return data


@attr.dataclass
class BarbarianAncestralGuardianLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(
            BarbarianPathOfTheAncestralGuardianFeatures.ConsultTheSpirits()
        )
        return data


@attr.dataclass
class BarbarianAncestralGuardianLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        rage: BarbarianFeatures.Rage = data.get_features_by_type(
            BarbarianFeatures.Rage
        )[0]
        rage.extend_feature(
            BarbarianPathOfTheAncestralGuardianFeatures.VengefulAncestors()
        )
        return data


class BarbarianAncestralGuardianCustomStarterClassArgs(BarbarianCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BarbarianSubclass2014.PATH_OF_THE_ANCESTRAL_GUARDIAN.value,
            skills=skills,
        )


class BarbarianAncestralGuardianMulticlassBuilder(BarbarianMulticlassBuilder):

    def __init__(
        self,
        barbarian_level_features: ClassBuilder.BaseClassLevelFeatures,
        barbarian_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            barbarian_level_features=barbarian_level_features,
            barbarian_level=barbarian_level,
            subclass=BarbarianSubclass2014.PATH_OF_THE_ANCESTRAL_GUARDIAN.value,
            replace_spells=replace_spells,
        )
