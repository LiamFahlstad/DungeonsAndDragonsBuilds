from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from Model.Character import Character
from Core.Definitions import BardSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Bard import BardSpiritsFeatures
from CharacterContent.Spells.SpellLists import ClericLevel0Spells, ClericLevel3Spells


@attr.dataclass
class BardSpiritsLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(BardSpiritsFeatures.Channeler())
        data.add_feature(BardSpiritsFeatures.SpiritsFromBeyond())
        data.add_cantrip(ClericLevel0Spells.GUIDANCE)
        return data


@attr.dataclass
class BardSpiritsLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: Character,
    ) -> Character:
        data.add_feature(BardSpiritsFeatures.EmpoweredChanneling())
        data.add_spell(ClericLevel3Spells.SPIRIT_GUARDIANS)
        return data


@attr.dataclass
class BardSpiritsLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: Character,
    ) -> Character:
        spirits_from_beyond: BardSpiritsFeatures.SpiritsFromBeyond = (
            data.get_features_by_type(BardSpiritsFeatures.SpiritsFromBeyond)[0]
        )
        spirits_from_beyond.extend_feature(BardSpiritsFeatures.MysticalConnection())
        return data


class BardSpiritsCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=BardSubclass.SPIRITS.value,
            skills=skills,
        )


class BardSpiritsMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass.SPIRITS.value,
            replace_spells=replace_spells,
        )
