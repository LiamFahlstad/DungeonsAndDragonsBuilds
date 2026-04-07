from typing import Optional, TypeAlias

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.WizardBase import (
    WizardMulticlassBuilder,
    WizardStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import WizardSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import WizardFeatures
from Items import Items
from Spells.Definitions import (
    DivinationLevel1Spells,
    DivinationLevel2Spells,
    DivinationLevel3Spells,
    DivinationLevel4Spells,
    DivinationLevel5Spells,
    DivinationLevel6Spells,
    DivinationLevel7Spells,
    DivinationLevel8Spells,
    DivinationLevel9Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock

DivinationSpellsUpTo2: TypeAlias = DivinationLevel1Spells | DivinationLevel2Spells

DivinationSpellsUpTo3: TypeAlias = DivinationSpellsUpTo2 | DivinationLevel3Spells

DivinationSpellsUpTo4: TypeAlias = DivinationSpellsUpTo3 | DivinationLevel4Spells

DivinationSpellsUpTo5: TypeAlias = DivinationSpellsUpTo4 | DivinationLevel5Spells

DivinationSpellsUpTo6: TypeAlias = DivinationSpellsUpTo5 | DivinationLevel6Spells

DivinationSpellsUpTo7: TypeAlias = DivinationSpellsUpTo6 | DivinationLevel7Spells

DivinationSpellsUpTo8: TypeAlias = DivinationSpellsUpTo7 | DivinationLevel8Spells

DivinationSpellsUpTo9: TypeAlias = DivinationSpellsUpTo8 | DivinationLevel9Spells


@attr.dataclass
class WizardDivinerLevel3(ClassBuilder.SubclassLevel3):
    spell_1: DivinationSpellsUpTo2
    spell_2: DivinationSpellsUpTo2

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.DivinationSavant())
        data.add_feature(WizardFeatures.Portent())
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        return data


@attr.dataclass
class WizardDivinerLevel5(ClassBuilder.SubclassLevel5):
    spell: DivinationSpellsUpTo3

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardDivinerLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.ExpertDivination())
        return data


@attr.dataclass
class WizardDivinerLevel7(ClassBuilder.SubclassLevel7):
    spell: DivinationSpellsUpTo4

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardDivinerLevel9(ClassBuilder.SubclassLevel9):
    spell: DivinationSpellsUpTo5

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardDivinerLevel10(ClassBuilder.SubclassLevel10):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.TheThirdEye())
        return data


@attr.dataclass
class WizardDivinerLevel11(ClassBuilder.SubclassLevel11):
    spell: DivinationSpellsUpTo6

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardDivinerLevel13(ClassBuilder.SubclassLevel13):
    spell: DivinationSpellsUpTo7

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardDivinerLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(WizardFeatures.GreaterPortent())
        return data


@attr.dataclass
class WizardDivinerLevel15(ClassBuilder.SubclassLevel15):
    spell: DivinationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


@attr.dataclass
class WizardDivinerLevel17(ClassBuilder.SubclassLevel17):
    spell: DivinationSpellsUpTo8

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell)
        return data


class WizardDivinerStarterClassBuilder(WizardStarterClassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        abilities: AbilitiesStatBlock,
        wizard_skills: WizardSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
        items: Optional[list[tuple[Items.Item, int]]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.BLADESINGER.value,
            abilities=abilities,
            wizard_skills=wizard_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
            items=items,
        )


class WizardDivinerMulticlassBuilder(WizardMulticlassBuilder):

    def __init__(
        self,
        wizard_level_features: ClassBuilder.BaseClassLevelFeatures,
        wizard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            wizard_level_features=wizard_level_features,
            wizard_level=wizard_level,
            subclass=WizardSubclass.BLADESINGER.value,
            replace_spells=replace_spells,
        )
