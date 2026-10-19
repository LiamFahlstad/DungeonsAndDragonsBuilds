from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import ClericSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Cleric import ClericArcanaFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Spells.SpellLists import (
    WizardLevel0Spells,
    WizardLevel1Spells,
    WizardLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
    WizardLevel5Spells,
    WizardLevel6Spells,
    WizardLevel7Spells,
    WizardLevel8Spells,
    WizardLevel9Spells,
)
from Model.CharacterSources import SpellSource


@attr.dataclass
class ClericArcanaLevel3(ClassBuilder.SubclassLevel3):
    skill: Skill
    cantrip_1: WizardLevel0Spells
    cantrip_2: WizardLevel0Spells

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel1Spells.DETECT_MAGIC)
        data.add_spell(WizardLevel1Spells.MAGIC_MISSILE)
        data.add_spell(WizardLevel2Spells.MAGIC_WEAPON)
        data.add_spell(WizardLevel2Spells.NYSTULS_MAGIC_AURA)
        data.add_feature(
            ClericArcanaFeatures.ModifyMagic(), extends=ClericFeatures.ChannelDivinity
        )
        data.add_feature(
            ClericArcanaFeatures.StudentOfArcana(
                self.skill, self.cantrip_1, self.cantrip_2
            )
        )
        data.add_cantrip(self.cantrip_1, source=SpellSource.CHOSEN)
        data.add_cantrip(self.cantrip_2, source=SpellSource.CHOSEN)


@attr.dataclass
class ClericArcanaLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel3Spells.COUNTERSPELL)
        data.add_spell(WizardLevel3Spells.DISPEL_MAGIC)


@attr.dataclass
class ClericArcanaLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericArcanaFeatures.DispellingRecovery())


@attr.dataclass
class ClericArcanaLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel4Spells.ARCANE_EYE)
        data.add_spell(WizardLevel4Spells.LEOMUNDS_SECRET_CHEST)


@attr.dataclass
class ClericArcanaLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel5Spells.BIGBYS_HAND)
        data.add_spell(WizardLevel5Spells.TELEPORTATION_CIRCLE)


@attr.dataclass
class ClericArcanaLevel17(ClassBuilder.SubclassLevel17):
    spell_6: WizardLevel6Spells
    spell_7: WizardLevel7Spells
    spell_8: WizardLevel8Spells
    spell_9: WizardLevel9Spells

    def add_features(
        self,
        data: Grants,
    ) -> None:
        spells = [self.spell_6, self.spell_7, self.spell_8, self.spell_9]
        data.add_feature(ClericArcanaFeatures.MagicalMastery(spells))
        for spell in spells:
            data.add_spell(spell, source=SpellSource.CHOSEN)


class ClericArcanaCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass.ARCANA.value,
            skills=skills,
        )


class ClericArcanaMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.ARCANA.value,
            replace_spells=replace_spells,
        )
