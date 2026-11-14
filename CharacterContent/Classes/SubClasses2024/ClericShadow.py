from typing import Optional

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from Model.Grants import Grants
from Core.Definitions import ClericSubclass, Skill
from CharacterContent.Features.SubClassFeatures.Cleric import ClericShadowFeatures
from CharacterContent.Features.ClassFeatures.Cleric import ClericFeatures
from CharacterContent.Spells.SpellLists import (
    ConjurationLevel4Spells,
    DivinationLevel2Spells,
    EnchantmentLevel1Spells,
    EnchantmentLevel5Spells,
    NecromancyLevel3Spells,
    WizardLevel2Spells,
    ClericLevel1Spells,
    ClericLevel4Spells,
    ClericLevel5Spells,
)


@attr.dataclass
class ClericShadowLevel3(ClassBuilder.SubclassLevel3):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(WizardLevel2Spells.CROWN_OF_MADNESS)
        data.add_spell(EnchantmentLevel1Spells.DISSONANT_WHISPERS)
        data.add_spell(DivinationLevel2Spells.MIND_SPIKE)
        data.add_spell(ClericLevel1Spells.SHADOW_WORD_PAIN)
        data.add_feature(ClericShadowFeatures.ShadowDomainSpells())
        data.add_feature(
            ClericShadowFeatures.Shadowform(),
            extends=ClericFeatures.ChannelDivinity,
        )
        data.add_feature(ClericShadowFeatures.DevouringPlague())


@attr.dataclass
class ClericShadowLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(NecromancyLevel3Spells.SUMMON_UNDEAD)
        data.add_spell(NecromancyLevel3Spells.VAMPIRIC_TOUCH)


@attr.dataclass
class ClericShadowLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_feature(ClericShadowFeatures.Dispersion())


@attr.dataclass
class ClericShadowLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(ConjurationLevel4Spells.EVARDS_BLACK_TENTACLES)
        data.add_spell(ClericLevel4Spells.PSYCHIC_HORROR)


@attr.dataclass
class ClericShadowLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        data.add_spell(EnchantmentLevel5Spells.DOMINATE_PERSON)
        data.add_spell(ClericLevel5Spells.VOID_ERUPTION)


@attr.dataclass
class ClericShadowLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: Grants,
    ) -> None:
        # Shadowform is a Channel Divinity extension, which a type parent
        # can't match, so its upgrade is granted on its own.
        data.add_feature(ClericShadowFeatures.VampiricEmbrace())


class ClericShadowCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: list[Skill],
    ):
        super().__init__(
            subclass=ClericSubclass.SHADOW.value,
            skills=skills,
        )


class ClericShadowMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.SHADOW.value,
            replace_spells=replace_spells,
        )
