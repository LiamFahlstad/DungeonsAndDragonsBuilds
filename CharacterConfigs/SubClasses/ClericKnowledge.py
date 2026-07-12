from typing import Optional

import attr

from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClericBase import (
    ClericMulticlassBuilder,
    ClericCustomStarterClassArgs,
)
from CharacterSheetCreator import CharacterSheetData
from Definitions import ClericSubclass, Skill
from Features.ClassFeatures.Cleric import ClericKnowledgeFeatures, ClericFeatures
from Spells.SpellLists import (
    ClericLevel1Spells,
    ClericLevel3Spells,
    ClericLevel4Spells,
    DivinationLevel1Spells,
    DivinationLevel2Spells,
    DivinationLevel3Spells,
    DivinationLevel4Spells,
    DivinationLevel5Spells,
    EnchantmentLevel4Spells,
    WarlockLevel5Spells,
)
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
        channel_divinity.extend_feature(ClericKnowledgeFeatures.MindMagic())
        data.add_feature(
            ClericKnowledgeFeatures.BlessingsOfKnowledge(self.skill_1, self.skill_2)
        )
        return data


@attr.dataclass
class ClericKnowledgeLevel5(ClassBuilder.SubclassLevel5):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        additional_ruling = "As a Magic action, you can expend one use of your Channel Divinity to cast this spell. As part of that action, you cast that spell without expending a spell slot or needing Material components."

        data.add_spell(ClericLevel3Spells.DISPEL_MAGIC)
        data.add_spell(DivinationLevel2Spells.NONDETECTION)
        data.add_spell(
            DivinationLevel3Spells.TONGUES,
            additional_ruling=additional_ruling,
        )
        return data


@attr.dataclass
class ClericKnowledgeLevel6(ClassBuilder.SubclassLevel6):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericKnowledgeFeatures.UnfetteredMind())
        return data


@attr.dataclass
class ClericKnowledgeLevel7(ClassBuilder.SubclassLevel7):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        additional_ruling = "As a Magic action, you can expend one use of your Channel Divinity to cast this spell. As part of that action, you cast that spell without expending a spell slot or needing Material components."

        data.add_spell(
            DivinationLevel4Spells.ARCANE_EYE,
            additional_ruling=additional_ruling,
        )
        data.add_spell(ClericLevel4Spells.BANISHMENT)
        data.add_spell(EnchantmentLevel4Spells.CONFUSION)
        return data


@attr.dataclass
class ClericKnowledgeLevel9(ClassBuilder.SubclassLevel9):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        additional_ruling = "As a Magic action, you can expend one use of your Channel Divinity to cast this spell. As part of that action, you cast that spell without expending a spell slot or needing Material components."

        data.add_spell(
            DivinationLevel5Spells.LEGEND_LORE,
            additional_ruling=additional_ruling,
        )
        data.add_spell(
            DivinationLevel5Spells.SCRYING,
            additional_ruling=additional_ruling,
        )
        data.add_spell(
            WarlockLevel5Spells.SYNAPTIC_STATIC,
        )
        return data


@attr.dataclass
class ClericKnowledgeLevel17(ClassBuilder.SubclassLevel17):

    def add_features(
        self,
        data: CharacterSheetData,
    ) -> CharacterSheetData:
        data.add_feature(ClericKnowledgeFeatures.DivineForeknowledge())
        return data


class ClericKnowledgeCustomStarterClassArgs(ClericCustomStarterClassArgs):
    def __init__(
        self,
        skills: ClericSkillsStatBlock,
    ):
        super().__init__(
            subclass=ClericSubclass.KNOWLEDGE.value,
            skills=skills,
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
