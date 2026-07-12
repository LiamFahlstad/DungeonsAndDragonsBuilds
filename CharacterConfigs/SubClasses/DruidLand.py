from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.DruidBase import (
    DruidCustomStarterClassArgs,
    DruidMulticlassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import DruidLandType, DruidSubclass
from Features.ClassFeatures.Druid import DruidLandFeatures
from Spells.Definitions import (
    AbjurationLevel4Spells,
    ConjurationLevel1Spells,
    ConjurationLevel2Spells,
    ConjurationLevel3Spells,
    ConjurationLevel5Spells,
    EnchantmentLevel1Spells,
    EnchantmentLevel2Spells,
    EvocationLevel0Spells,
    EvocationLevel1Spells,
    EvocationLevel3Spells,
    EvocationLevel4Spells,
    EvocationLevel5Spells,
    IllusionLevel2Spells,
    NecromancyLevel1Spells,
    NecromancyLevel4Spells,
    TransmutationLevel4Spells,
)
from StatBlocks.SkillsStatBlock import DruidSkillsStatBlock

# Circle Spells granted by the Circle of the Land Spells feature, keyed by chosen
# land type and the Druid level at which they are gained (3, 5, 7, and 9).
_LEVEL_3_CIRCLE_SPELLS: dict[DruidLandType, list[str]] = {
    DruidLandType.ARID: [
        EvocationLevel0Spells.FIRE_BOLT,
        EvocationLevel1Spells.BURNING_HANDS,
        IllusionLevel2Spells.BLUR,
    ],
    DruidLandType.POLAR: [
        EvocationLevel0Spells.RAY_OF_FROST,
        ConjurationLevel1Spells.FOG_CLOUD,
        EnchantmentLevel2Spells.HOLD_PERSON,
    ],
    DruidLandType.TEMPERATE: [
        EvocationLevel0Spells.SHOCKING_GRASP,
        EnchantmentLevel1Spells.SLEEP,
        ConjurationLevel2Spells.MISTY_STEP,
    ],
    DruidLandType.TROPICAL: [
        EvocationLevel0Spells.ACID_SPLASH,
        NecromancyLevel1Spells.RAY_OF_SICKNESS,
        ConjurationLevel2Spells.WEB,
    ],
}

_LEVEL_5_CIRCLE_SPELLS: dict[DruidLandType, str] = {
    DruidLandType.ARID: EvocationLevel3Spells.FIREBALL,
    DruidLandType.POLAR: ConjurationLevel3Spells.SLEET_STORM,
    DruidLandType.TEMPERATE: EvocationLevel3Spells.LIGHTNING_BOLT,
    DruidLandType.TROPICAL: ConjurationLevel3Spells.STINKING_CLOUD,
}

_LEVEL_7_CIRCLE_SPELLS: dict[DruidLandType, str] = {
    DruidLandType.ARID: NecromancyLevel4Spells.BLIGHT,
    DruidLandType.POLAR: EvocationLevel4Spells.ICE_STORM,
    DruidLandType.TEMPERATE: AbjurationLevel4Spells.FREEDOM_OF_MOVEMENT,
    DruidLandType.TROPICAL: TransmutationLevel4Spells.POLYMORPH,
}

_LEVEL_9_CIRCLE_SPELLS: dict[DruidLandType, str] = {
    DruidLandType.ARID: EvocationLevel5Spells.WALL_OF_STONE,
    DruidLandType.POLAR: EvocationLevel5Spells.CONE_OF_COLD,
    DruidLandType.TEMPERATE: ConjurationLevel5Spells.TREE_STRIDE,
    DruidLandType.TROPICAL: ConjurationLevel5Spells.INSECT_PLAGUE,
}


@attr.dataclass
class DruidLandLevel3(ClassBuilder.SubclassLevel3):
    land_type: DruidLandType

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidLandFeatures.CircleOfTheLandSpells(land_type=self.land_type))
        data.add_feature(DruidLandFeatures.LandsAid())
        for spell in _LEVEL_3_CIRCLE_SPELLS[self.land_type]:
            data.add_spell(spell)
        return data


@attr.dataclass
class DruidLandLevel5(ClassBuilder.SubclassLevel5):
    land_type: DruidLandType

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(_LEVEL_5_CIRCLE_SPELLS[self.land_type])
        return data


@attr.dataclass
class DruidLandLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidLandFeatures.NaturalRecovery())
        return data


@attr.dataclass
class DruidLandLevel7(ClassBuilder.SubclassLevel7):
    land_type: DruidLandType

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(_LEVEL_7_CIRCLE_SPELLS[self.land_type])
        return data


@attr.dataclass
class DruidLandLevel9(ClassBuilder.SubclassLevel9):
    land_type: DruidLandType

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(_LEVEL_9_CIRCLE_SPELLS[self.land_type])
        return data


@attr.dataclass
class DruidLandLevel10(ClassBuilder.SubclassLevel10):
    land_type: DruidLandType

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidLandFeatures.NaturesWard(land_type=self.land_type))
        return data


@attr.dataclass
class DruidLandLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(DruidLandFeatures.NaturesSanctuary())
        return data


class DruidLandCustomStarterClassArgs(DruidCustomStarterClassArgs):
    def __init__(
        self,
        skills: DruidSkillsStatBlock,
    ):
        super().__init__(
            subclass=DruidSubclass.LAND.value,
            skills=skills,
        )


class DruidLandMulticlassBuilder(DruidMulticlassBuilder):

    def __init__(
        self,
        druid_level_features: ClassBuilder.BaseClassLevelFeatures,
        druid_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            druid_level_features=druid_level_features,
            druid_level=druid_level,
            subclass=DruidSubclass.LAND.value,
            replace_spells=replace_spells,
        )
