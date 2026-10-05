from typing import Optional

import attr

import CharacterContent.Spells.SpellLists as SpellDefinitions
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Model.Character import Character
from Model.Grants import Grants
from Core.Definitions import BardSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Bard import BardGlamourFeatures
from CharacterContent.Features.ClassFeatures.Bard import BardFeatures


@attr.dataclass
class BardGlamourLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(SpellDefinitions.BardLevel1Spells.CHARM_PERSON)
        data.add_spell(SpellDefinitions.BardLevel2Spells.MIRROR_IMAGE)
        data.add_feature(BardGlamourFeatures.BeguilingMagic())
        data.add_feature(BardGlamourFeatures.MantleOfInspiration())
        return data


@attr.dataclass
class BardGlamourLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_spell(SpellDefinitions.BardLevel1Spells.COMMAND)
        data.add_feature(
            BardGlamourFeatures.MantleOfMajesty(),
            extends=BardFeatures.BardicInspiration,
        )
        return data


@attr.dataclass
class BardGlamourLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Grants,
    ) -> Grants:
        data.add_feature(BardGlamourFeatures.UnbreakableMajesty())
        return data


class BardGlamourCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BardSubclass.GLAMOUR.value,
            skills=skills,
        )


class BardGlamourMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass.GLAMOUR.value,
            replace_spells=replace_spells,
        )
