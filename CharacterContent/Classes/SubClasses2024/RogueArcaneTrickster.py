from typing import Optional, TypeAlias

import attr

from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.RogueBase import (
    RogueMulticlassBuilder,
    RogueCustomStarterClassArgs,
)
from Builds.CharacterSheetAccumulator import CharacterSheetData
from Core.Definitions import RogueSubclass
from CharacterContent.Features.ClassFeatures import SpellSlots
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures
from CharacterContent.Features.SubClassFeatures.Rogue import RogueArcaneTricksterFeatures
from CharacterContent.Spells.SpellLists import (
    WizardLevel0Spells,
    WizardLevel1Spells,
    WizardLevel2Spells,
    WizardLevel3Spells,
    WizardLevel4Spells,
)
from StatBlocks.SkillsStatBlock import RogueSkillsStatBlock

# 2024 rules dropped the 2014 Enchantment/Illusion school restriction: prepared
# spells can be any Wizard spell of a level for which the Arcane Trickster has
# spell slots (see SourceTexts/SubclassTexts2024/arcane_trickster.txt).
ArcaneTricksterSpellsUpTo1: TypeAlias = WizardLevel1Spells

ArcaneTricksterSpellsUpTo2: TypeAlias = WizardLevel1Spells | WizardLevel2Spells

ArcaneTricksterSpellsUpTo3: TypeAlias = ArcaneTricksterSpellsUpTo2 | WizardLevel3Spells

ArcaneTricksterSpellsUpTo4: TypeAlias = ArcaneTricksterSpellsUpTo3 | WizardLevel4Spells


@attr.dataclass
class RogueArcaneTricksterLevel3(ClassBuilder.SubclassLevel3):
    cantrip_2: WizardLevel0Spells
    cantrip_3: WizardLevel0Spells
    spell_1: ArcaneTricksterSpellsUpTo1
    spell_2: ArcaneTricksterSpellsUpTo1
    spell_3: ArcaneTricksterSpellsUpTo1

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueArcaneTricksterFeatures.Spellcasting())
        data.add_feature(RogueArcaneTricksterFeatures.MageHandLegerdemain())
        data.add_cantrip(WizardLevel0Spells.MAGE_HAND)
        data.add_cantrip(self.cantrip_2)
        data.add_cantrip(self.cantrip_3)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_spell(self.spell_3)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel4(ClassBuilder.SubclassLevel4):
    spell: ArcaneTricksterSpellsUpTo1

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel7(ClassBuilder.SubclassLevel7):
    spell: ArcaneTricksterSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel8(ClassBuilder.SubclassLevel8):
    spell: ArcaneTricksterSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueArcaneTricksterFeatures.MagicalAmbush())
        return data


@attr.dataclass
class RogueArcaneTricksterLevel10(ClassBuilder.SubclassLevel10):
    cantrip: WizardLevel0Spells
    spell: ArcaneTricksterSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel11(ClassBuilder.SubclassLevel11):
    spell: ArcaneTricksterSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel13(ClassBuilder.SubclassLevel13):
    spell: ArcaneTricksterSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        sneak_attack_feature: RogueFeatures.SneakAttack = data.get_features_by_type(
            RogueFeatures.SneakAttack
        )[0]
        sneak_attack_feature.extend_feature(
            RogueArcaneTricksterFeatures.VersatileTrickster()
        )
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel14(ClassBuilder.SubclassLevel14):
    spell: ArcaneTricksterSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel16(ClassBuilder.SubclassLevel16):
    spell: ArcaneTricksterSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(RogueArcaneTricksterFeatures.SpellThief())
        return data


@attr.dataclass
class RogueArcaneTricksterLevel19(ClassBuilder.SubclassLevel19):
    spell: ArcaneTricksterSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class RogueArcaneTricksterLevel20(ClassBuilder.SubclassLevel20):
    spell: ArcaneTricksterSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


class RogueArcaneTricksterCustomStarterClassArgs(RogueCustomStarterClassArgs):
    def __init__(
        self,
        skills: RogueSkillsStatBlock,
    ):
        super().__init__(
            subclass=RogueSubclass.ARCANE_TRICKSTER.value,
            skills=skills,
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
        )


class RogueArcaneTricksterMulticlassBuilder(RogueMulticlassBuilder):

    def __init__(
        self,
        rogue_level_features: ClassBuilder.BaseClassLevelFeatures,
        rogue_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            rogue_level_features=rogue_level_features,
            rogue_level=rogue_level,
            subclass=RogueSubclass.ARCANE_TRICKSTER.value,
            replace_spells=replace_spells,
            caster_type=SpellSlots.CasterType.THIRD_CASTER,
        )
