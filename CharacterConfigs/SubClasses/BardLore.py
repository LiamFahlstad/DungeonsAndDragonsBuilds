from typing import Optional

import attr

import Spells.Definitions as SpellDefinitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import BardSubclass, Skill
from Features.ClassFeatures.Bard import BardLoreFeatures
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class BardLoreLevel3(ClassBuilder.SubclassLevel3):
    skill_1: Skill
    skill_2: Skill
    skill_3: Skill

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(
            BardLoreFeatures.BonusProficiencies(self.skill_1, self.skill_2, self.skill_3)
        )
        data.add_feature(BardLoreFeatures.CuttingWords())
        return data


@attr.dataclass
class BardLoreLevel6(ClassBuilder.SubclassLevel6):
    spell_1: (
        SpellDefinitions.ClericLevel1Spells
        | SpellDefinitions.ClericLevel2Spells
        | SpellDefinitions.ClericLevel3Spells
        | SpellDefinitions.DruidLevel1Spells
        | SpellDefinitions.DruidLevel2Spells
        | SpellDefinitions.DruidLevel3Spells
        | SpellDefinitions.WizardLevel1Spells
        | SpellDefinitions.WizardLevel2Spells
        | SpellDefinitions.WizardLevel3Spells
    )
    spell_2: (
        SpellDefinitions.ClericLevel1Spells
        | SpellDefinitions.ClericLevel2Spells
        | SpellDefinitions.ClericLevel3Spells
        | SpellDefinitions.DruidLevel1Spells
        | SpellDefinitions.DruidLevel2Spells
        | SpellDefinitions.DruidLevel3Spells
        | SpellDefinitions.WizardLevel1Spells
        | SpellDefinitions.WizardLevel2Spells
        | SpellDefinitions.WizardLevel3Spells
    )

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(self.spell_1)
        data.add_spell(self.spell_2)
        data.add_feature(BardLoreFeatures.MagicalDiscoveries())
        return data


@attr.dataclass
class BardLoreLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        bardic_inspiration: BardLoreFeatures.BardicInspiration = data.get_features_by_type(
            BardLoreFeatures.BardicInspiration
        )[0]
        bardic_inspiration.extend_feature(BardLoreFeatures.PeerlessSkill())
        return data


class BardLoreCustomStarterClassArgs(BardCustomStarterClassArgs):
    def __init__(
        self,
        skills: BardSkillsStatBlock,
    ):
        super().__init__(
            subclass=BardSubclass.LORE.value,
            skills=skills,
        )


class BardLoreMulticlassBuilder(BardMulticlassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass.LORE.value,
            replace_spells=replace_spells,
        )
