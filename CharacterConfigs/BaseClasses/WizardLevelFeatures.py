from typing import TypeAlias

import attr

from CharacterConfigs.BaseClasses.import ClassBuilder
from CharacterSheetCreator import CharacterSheetData
from Definitions import Skill
from Features import GeneralFeats
from Features.ClassFeatures import WizardFeatures
from Spells.Definitions import (
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

WizardSpellsUpTo2: TypeAlias = WizardLevel1Spells | WizardLevel2Spells

WizardSpellsUpTo3: TypeAlias = WizardSpellsUpTo2 | WizardLevel3Spells

WizardSpellsUpTo4: TypeAlias = WizardSpellsUpTo3 | WizardLevel4Spells

WizardSpellsUpTo5: TypeAlias = WizardSpellsUpTo4 | WizardLevel5Spells

WizardSpellsUpTo6: TypeAlias = WizardSpellsUpTo5 | WizardLevel6Spells

WizardSpellsUpTo7: TypeAlias = WizardSpellsUpTo6 | WizardLevel7Spells

WizardSpellsUpTo8: TypeAlias = WizardSpellsUpTo7 | WizardLevel8Spells

WizardSpellsUpTo9: TypeAlias = WizardSpellsUpTo8 | WizardLevel9Spells


@attr.dataclass
class WizardLevel1(ClassBuilder.BaseClassLevel1):
    cantrip_1: WizardLevel0Spells
    cantrip_2: WizardLevel0Spells
    cantrip_3: WizardLevel0Spells
    spell_1: WizardLevel1Spells
    spell_2: WizardLevel1Spells
    spell_3: WizardLevel1Spells
    spell_4: WizardLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.RitualAdept())
        data.add_feature(WizardFeatures.ArcaneRecovery())
        data.add_cantrip(self.cantrip_1)
        data.add_cantrip(self.cantrip_2)
        data.add_cantrip(self.cantrip_3)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_spell(self.spell_3)
        data.add_spell(self.spell_4)
        return data


@attr.dataclass
class WizardLevel2(ClassBuilder.BaseClassLevel2):
    skill_to_expertise_in: Skill
    spell: WizardLevel1Spells

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.Scholar(self.skill_to_expertise_in))
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel3(ClassBuilder.BaseClassLevel3):
    spell: WizardSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel4(ClassBuilder.BaseClassLevel4):
    general_feat: GeneralFeats.GeneralFeat
    cantrip: WizardLevel0Spells
    spell: WizardSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_cantrip(self.cantrip)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel5(ClassBuilder.BaseClassLevel5):
    spell_1: WizardSpellsUpTo3
    spell_2: WizardSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.MemorizeSpell())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WizardLevel6(ClassBuilder.BaseClassLevel6):
    spell: WizardSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel7(ClassBuilder.BaseClassLevel7):
    spell: WizardSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel8(ClassBuilder.BaseClassLevel8):
    general_feat: GeneralFeats.GeneralFeat
    spell: WizardSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel9(ClassBuilder.BaseClassLevel9):
    spell_1: WizardSpellsUpTo5
    spell_2: WizardSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WizardLevel10(ClassBuilder.BaseClassLevel10):
    spell: WizardSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel11(ClassBuilder.BaseClassLevel11):
    spell: WizardSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel12(ClassBuilder.BaseClassLevel12):
    general_feat: GeneralFeats.GeneralFeat

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        return data


@attr.dataclass
class WizardLevel13(ClassBuilder.BaseClassLevel13):
    spell: WizardSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel14(ClassBuilder.BaseClassLevel14):
    spell: WizardSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel15(ClassBuilder.BaseClassLevel15):
    spell: WizardSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel16(ClassBuilder.BaseClassLevel16):
    general_feat: GeneralFeats.GeneralFeat
    spell_1: WizardSpellsUpTo8
    spell_2: WizardSpellsUpTo8

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(self.general_feat)
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WizardLevel17(ClassBuilder.BaseClassLevel17):
    spell: WizardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel18(ClassBuilder.BaseClassLevel18):
    spell: WizardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SpellMastery())
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel19(ClassBuilder.BaseClassLevel19):
    spell: WizardSpellsUpTo9

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardLevel20(ClassBuilder.BaseClassLevel20):
    spell: WizardSpellsUpTo9

    def add_features(self, data: CharacterSheetData) -> CharacterSheetData:
        data.add_feature(WizardFeatures.SignatureSpells())
        data.add_spell(self.spell)
        return data
