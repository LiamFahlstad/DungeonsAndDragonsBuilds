from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericStarterClassBuilder,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ClericSubclass, Skill
from Features import Armor, Backgrounds, OriginFeats, Weapons
from Features.ClassFeatures import ClericFeatures
from Spells.Definitions import (
    ClericLevel1Spells,
    DivinationLevel1Spells,
    DivinationLevel2Spells,
)
from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
from StatBlocks.SkillsStatBlock import ClericSkillsStatBlock


@attr.dataclass
class ClericKnowledgeLevel3(ClassBuilder.SubclassLevel3):
    skill_1: Skill
    skill_2: Skill

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:

        additional_ruling = "As a Magic action, you can expend one use of your Channel Divinity to cast this spell. As part of that action, you cast that spell without expending a spell slot or needing Material components."

        data.add_spell(ClericLevel1Spells.COMMAND)
        data.add_spell(
            DivinationLevel1Spells.COMPREHEND_LANGUAGES,
            additional_ruling=additional_ruling,
        )
        data.add_spell(
            DivinationLevel1Spells.DETECT_MAGIC, additional_ruling=additional_ruling
        )
        data.add_spell(
            DivinationLevel2Spells.DETECT_THOUGHTS, additional_ruling=additional_ruling
        )
        data.add_spell(
            DivinationLevel1Spells.IDENTIFY, additional_ruling=additional_ruling
        )
        data.add_spell(
            DivinationLevel2Spells.MIND_SPIKE, additional_ruling=additional_ruling
        )

        channel_divinity: ClericFeatures.ChannelDivinity = data.get_features_by_type(
            ClericFeatures.ChannelDivinity
        )[0]
        channel_divinity.add_feature(ClericFeatures.MindMagic())
        data.add_feature(
            ClericFeatures.BlessingsOfKnowledge(self.skill_1, self.skill_2)
        )
        return data


@attr.dataclass
class ClericKnowledgeLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericFeatures.UnfetteredMind())
        return data


@attr.dataclass
class ClericKnowledgeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericFeatures.DivineForeknowledge())
        return data


class ClericKnowledgeStarterClassBuilder(ClericStarterClassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        abilities: AbilitiesStatBlock,
        cleric_skills: ClericSkillsStatBlock,
        background_ability_bonuses: Backgrounds.FreeBackgroundAbilityBonus,
        background_skill_proficiencies: Backgrounds.FreeBackgroundSkillProficiency,
        add_default_equipment: bool,
        origin_feat: OriginFeats.OriginFeat,
        armor: Optional[list[Armor.AbstractArmor]] = None,
        weapons: Optional[list[Weapons.AbstractWeapon]] = None,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.KNOWLEDGE.value,
            abilities=abilities,
            cleric_skills=cleric_skills,
            background_ability_bonuses=background_ability_bonuses,
            background_skill_proficiencies=background_skill_proficiencies,
            add_default_equipment=add_default_equipment,
            origin_feat=origin_feat,
            armor=armor,
            weapons=weapons,
            replace_spells=replace_spells,
        )


class ClericKnowledgeMulticlassBuilder(ClericMulticlassBuilder):

    def __init__(
        self,
        cleric_level_features: ClassBuilder.BaseClassLevelFeatures,
        cleric_level: int,
        replace_spells: Optional[dict[str, str]] = None,
    ):
        super().__init__(
            cleric_level_features=cleric_level_features,
            cleric_level=cleric_level,
            subclass=ClericSubclass.KNOWLEDGE.value,
            replace_spells=replace_spells,
        )
