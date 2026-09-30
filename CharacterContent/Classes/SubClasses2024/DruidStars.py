from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.DruidBase import (
    DruidCustomStarterClassArgs,
    DruidMulticlassBuilder,
)
from Model.Character import Character
from Core.Definitions import DruidSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Druid import DruidStarsFeatures
from CharacterContent.Spells.SpellLists import DruidLevel0Spells, EvocationLevel1Spells


@attr.dataclass
class DruidStarsLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(DruidStarsFeatures.StarMap())
        data.add_feature(DruidStarsFeatures.StarryForm())
        data.add_spell(DruidLevel0Spells.GUIDANCE)
        data.add_spell(EvocationLevel1Spells.GUIDING_BOLT)
        return data


@attr.dataclass
class DruidStarsLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(DruidStarsFeatures.CosmicOmen())
        return data


@attr.dataclass
class DruidStarsLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        starry_form: DruidStarsFeatures.StarryForm = data.get_features_by_type(
            DruidStarsFeatures.StarryForm
        )[0]
        starry_form.extend_feature(DruidStarsFeatures.TwinklingConstellations())
        return data


@attr.dataclass
class DruidStarsLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        starry_form: DruidStarsFeatures.StarryForm = data.get_features_by_type(
            DruidStarsFeatures.StarryForm
        )[0]
        starry_form.extend_feature(DruidStarsFeatures.FullOfStars())
        return data


class DruidStarsCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=DruidSubclass.STARS.value,
            skills=skills,
        )


class DruidStarsMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass.STARS.value,
            replace_spells=replace_spells,
        )
