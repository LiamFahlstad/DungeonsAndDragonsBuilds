from typing import Optional

import attr

import Spells.Definitions as SpellDefinitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import BardSubclass, Skill
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import BardFeatures
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class LoreBardLevel3(ClassBuilder.SubclassLevel3):
    skill_1: Skill
    skill_2: Skill
    skill_3: Skill

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(
            BardFeatures.BonusProficiencies(self.skill_1, self.skill_2, self.skill_3)
        )
        data.add_feature(BardFeatures.CuttingWords())
        return data


@attr.dataclass
class LoreBardLevel6(ClassBuilder.SubclassLevel6):
    spell: (
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
        data.add_spell(self.spell)
        data.add_feature(BardFeatures.MagicalDiscoveries())
        return data


@attr.dataclass
class LoreBardLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        bardic_inspiration: BardFeatures.BardicInspiration = data.get_features_by_type(
            BardFeatures.BardicInspiration
        )[0]
        bardic_inspiration.add_feature(BardFeatures.PeerlessSkill())
        return data


class LoreBardStarterClassBuilder(BardStarterClassBuilder):

    def __init__(
        self,
        bard_level_features: ClassBuilder.BaseClassLevelFeatures,
        bard_level: int,
        abilities: AbilitiesStatBlock,
        bard_skills: BardSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            bard_level_features=bard_level_features,
            bard_level=bard_level,
            subclass=BardSubclass.LORE.value,
            abilities=abilities,
            bard_skills=bard_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class LoreBardMulticlassBuilder(BardMulticlassBuilder):

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
