from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.DruidBase import (
    DruidCustomStarterClassArgs,
    DruidMulticlassBuilder,
)
from Model.Character import Character
from Core.Definitions import DruidSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Druid import DruidSeaFeatures
from CharacterContent.Spells.SpellLists import (
    ArtificerLevel0Spells,
    BardLevel5Spells,
    DruidLevel1Spells,
    DruidLevel2Spells,
    DruidLevel3Spells,
    DruidLevel4Spells,
    DruidLevel5Spells,
    SorcererLevel3Spells,
)


@attr.dataclass
class DruidSeaLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(DruidSeaFeatures.CircleOfTheSeaSpells())
        data.add_feature(DruidSeaFeatures.WrathOfTheSea())
        data.add_spell(
            DruidLevel1Spells.FOG_CLOUD, source="Circle of the Sea Spells table"
        )
        data.add_spell(
            DruidLevel2Spells.GUST_OF_WIND, source="Circle of the Sea Spells table"
        )
        data.add_spell(
            ArtificerLevel0Spells.RAY_OF_FROST, source="Circle of the Sea Spells table"
        )
        data.add_spell(
            DruidLevel1Spells.THUNDERWAVE, source="Circle of the Sea Spells table"
        )
        return data


@attr.dataclass
class DruidSeaLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(
            SorcererLevel3Spells.LIGHTNING_BOLT, source="Circle of the Sea Spells table"
        )
        data.add_spell(
            DruidLevel3Spells.WATER_BREATHING, source="Circle of the Sea Spells table"
        )
        return data


@attr.dataclass
class DruidSeaLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        wrath_of_the_sea: DruidSeaFeatures.WrathOfTheSea = data.get_features_by_type(
            DruidSeaFeatures.WrathOfTheSea
        )[0]
        wrath_of_the_sea.extend_feature(DruidSeaFeatures.AquaticAffinity())
        return data


@attr.dataclass
class DruidSeaLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(
            DruidLevel4Spells.CONTROL_WATER, source="Circle of the Sea Spells table"
        )
        data.add_spell(
            DruidLevel4Spells.ICE_STORM, source="Circle of the Sea Spells table"
        )
        return data


@attr.dataclass
class DruidSeaLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_spell(
            DruidLevel5Spells.CONJURE_ELEMENTAL, source="Circle of the Sea Spells table"
        )
        data.add_spell(
            BardLevel5Spells.HOLD_MONSTER, source="Circle of the Sea Spells table"
        )
        return data


@attr.dataclass
class DruidSeaLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        wrath_of_the_sea: DruidSeaFeatures.WrathOfTheSea = data.get_features_by_type(
            DruidSeaFeatures.WrathOfTheSea
        )[0]
        wrath_of_the_sea.extend_feature(DruidSeaFeatures.Stormborn())
        return data


@attr.dataclass
class DruidSeaLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        wrath_of_the_sea: DruidSeaFeatures.WrathOfTheSea = data.get_features_by_type(
            DruidSeaFeatures.WrathOfTheSea
        )[0]
        wrath_of_the_sea.extend_feature(DruidSeaFeatures.OceanicGift())
        return data


class DruidSeaCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=DruidSubclass.SEA.value,
            skills=skills,
        )


class DruidSeaMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass.SEA.value,
            replace_spells=replace_spells,
        )
