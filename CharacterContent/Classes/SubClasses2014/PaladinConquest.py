from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.PaladinBase import (
    PaladinMulticlassBuilder,
    PaladinCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import PaladinSubclass2014, Skill
from CharacterContent.Features.SubClassFeatures2014.Paladin import (
    PaladinConquestFeatures,
)
from CharacterContent.Spells.SpellLists import (
    WarlockLevel1Spells,
    PaladinLevel1Spells,
    ClericLevel2Spells,
    WizardLevel3Spells,
    DruidLevel4Spells,
    WizardLevel5Spells,
)


@attr.dataclass
class PaladinConquestLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinConquestFeatures.ConquestSpells())
        data.add_feature(PaladinConquestFeatures.ConqueringPresence())
        data.add_feature(PaladinConquestFeatures.GuidedStrike())
        data.add_spell(WarlockLevel1Spells.ARMOR_OF_AGATHYS)
        data.add_spell(PaladinLevel1Spells.COMMAND)


@attr.dataclass
class PaladinConquestLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(ClericLevel2Spells.HOLD_PERSON)
        data.add_spell(ClericLevel2Spells.SPIRITUAL_WEAPON)


@attr.dataclass
class PaladinConquestLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinConquestFeatures.AuraOfConquest())


@attr.dataclass
class PaladinConquestLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel3Spells.BESTOW_CURSE)
        data.add_spell(WizardLevel3Spells.FEAR)


@attr.dataclass
class PaladinConquestLevel13(ClassBuilder.SubclassLevel13):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(DruidLevel4Spells.DOMINATE_BEAST)
        data.add_spell(DruidLevel4Spells.STONESKIN)


@attr.dataclass
class PaladinConquestLevel15(ClassBuilder.SubclassLevel15):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinConquestFeatures.ScornfulRebuke())


@attr.dataclass
class PaladinConquestLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel5Spells.CLOUDKILL)
        data.add_spell(WizardLevel5Spells.DOMINATE_PERSON)


@attr.dataclass
class PaladinConquestLevel18(ClassBuilder.SubclassLevel18):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(
            PaladinConquestFeatures.AuraOfConquestExpansion(),
            extends=PaladinConquestFeatures.AuraOfConquest,
        )


@attr.dataclass
class PaladinConquestLevel20(ClassBuilder.SubclassLevel20):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(PaladinConquestFeatures.InvincibleConqueror())


class PaladinConquestCustomStarterClassArgs(PaladinCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=PaladinSubclass2014.CONQUEST.value,
            skills=skills,
        )


class PaladinConquestMulticlassBuilder(PaladinMulticlassBuilder):

    def __init__(
        self,
        paladin_level_features: ClassBuilder.BaseClassLevelFeatures,
        paladin_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            paladin_level_features=paladin_level_features,
            paladin_level=paladin_level,
            subclass=PaladinSubclass2014.CONQUEST.value,
            replace_spells=replace_spells,
        )
