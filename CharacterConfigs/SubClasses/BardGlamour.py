from typing import Optional

import attr

import Spells.Definitions as SpellDefinitions
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.BardBase import (
    BardMulticlassBuilder,
    BardStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import BardSubclass
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import BardFeatures
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import BardSkillsStatBlock


@attr.dataclass
class BardGlamourLevel3(ClassBuilder.SubclassLevel3):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.BardLevel1Spells.CHARM_PERSON)
        data.add_spell(SpellDefinitions.BardLevel2Spells.MIRROR_IMAGE)
        data.add_feature(BardFeatures.BeguilingMagic())
        data.add_feature(BardFeatures.MantleOfInspiration())
        return data


@attr.dataclass
class BardGlamourLevel6(ClassBuilder.SubclassLevel6):
    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_spell(SpellDefinitions.BardLevel1Spells.COMMAND)
        bardic_inspiration: BardFeatures.BardicInspiration = data.get_features_by_type(
            BardFeatures.BardicInspiration
        )[0]
        bardic_inspiration.add_feature(BardFeatures.MantleOfMajesty())
        return data


@attr.dataclass
class BardGlamourLevel14(ClassBuilder.SubclassLevel14):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(BardFeatures.UnbreakableMajesty())
        return data


class BardGlamourStarterClassBuilder(BardStarterClassBuilder):

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
            subclass=BardSubclass.GLAMOUR.value,
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
