from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ArtificerBase import (
    ArtificerMulticlassBuilder,
    ArtificerCustomStarterClassArgs,
)
from Builds.CharacterSheetCreator import CharacterSheetData
from Core.Definitions import ArtificerSubclass
from Features.SubClassFeatures.Artificer import ArtificerAlchemistFeatures
from Spells.SpellLists import (
    ClericLevel1Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
    SorcererLevel3Spells,
    SorcererLevel5Spells,
    WizardLevel1Spells,
    WizardLevel2Spells,
    WizardLevel4Spells,
)
from StatBlocks.SkillsStatBlock import ArtificerSkillsStatBlock


@attr.dataclass
class ArtificerAlchemistLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerAlchemistFeatures.AlchemistToolsOfTheTrade())
        data.add_feature(ArtificerAlchemistFeatures.AlchemistSpells())
        data.add_feature(ArtificerAlchemistFeatures.ExperimentalElixir())
        data.add_spell(ClericLevel1Spells.HEALING_WORD)
        data.add_spell(WizardLevel1Spells.RAY_OF_SICKNESS)
        return data


@attr.dataclass
class ArtificerAlchemistLevel5(ClassBuilder.SubclassLevel5):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerAlchemistFeatures.AlchemicalSavant())
        data.add_spell(WizardLevel2Spells.FLAMING_SPHERE)
        data.add_spell(WizardLevel2Spells.MELFS_ACID_ARROW)
        return data


@attr.dataclass
class ArtificerAlchemistLevel9(ClassBuilder.SubclassLevel9):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerAlchemistFeatures.RestorativeReagents())
        data.add_spell(SorcererLevel3Spells.GASEOUS_FORM)
        data.add_spell(ClericLevel3Spells.MASS_HEALING_WORD)
        return data


@attr.dataclass
class ArtificerAlchemistLevel13(ClassBuilder.SubclassLevel13):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(ClericLevel4Spells.DEATH_WARD)
        data.add_spell(WizardLevel4Spells.VITRIOLIC_SPHERE)
        return data


@attr.dataclass
class ArtificerAlchemistLevel15(ClassBuilder.SubclassLevel15):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ArtificerAlchemistFeatures.ChemicalMastery())
        return data


@attr.dataclass
class ArtificerAlchemistLevel17(ClassBuilder.SubclassLevel17):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SorcererLevel5Spells.CLOUDKILL)
        data.add_spell(ClericLevel5Spells.RAISE_DEAD)
        return data


class ArtificerAlchemistCustomStarterClassArgs(ArtificerCustomStarterClassArgs):
    def __init__(
        self,
        skills: ArtificerSkillsStatBlock,
    ):
        super().__init__(
            subclass=ArtificerSubclass.ALCHEMIST.value,
            skills=skills,
        )


class ArtificerAlchemistMulticlassBuilder(ArtificerMulticlassBuilder):

    def __init__(
        self,
        artificer_level_features: ClassBuilder.BaseClassLevelFeatures,
        artificer_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            artificer_level_features=artificer_level_features,
            artificer_level=artificer_level,
            subclass=ArtificerSubclass.ALCHEMIST.value,
            replace_spells=replace_spells,
        )
