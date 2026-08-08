import Core.Definitions as Definitions
from Core.Definitions import Language
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import GrantLanguage
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class SpeechOfTheWoods(Feature):
    def __init__(self):
        super().__init__(name="Speech of the Woods", origin="Circle of the Shepherd Druid Level 3")
        self._language = GrantLanguage(Language.SYLVAN, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._language.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 2nd level, you gain the ability to converse with beasts and many fey.\n"
            "\n"
            "You learn to speak, read, and write Sylvan. In addition, beasts can understand your speech, and you gain the ability to decipher their noises and motions. Most beasts lack the intelligence to convey or understand sophisticated concepts, but a friendly beast could relay what it has seen or heard in the recent past. This ability doesn't grant you any special friendship with beasts, though you can combine this ability with gifts to curry favor with them as you would with any nonplayer character."
        )
        return description


class SpiritTotem(Feature):
    def __init__(self):
        super().__init__(name="Spirit Totem", origin="Circle of the Shepherd Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        druid_level = character_stat_block.get_class_level(Definitions.CharacterClass.DRUID)
        temp_hp = 5 + druid_level
        description = (
            "Starting at 2nd level, you gain the ability to call forth nature spirits and use them to influence the world around you.\n"
            "\n"
            "As a bonus action, you can magically summon an incorporeal spirit to a point you can see within 60 feet of you. The spirit creates an aura in a 30-foot radius around that point. It counts as neither a creature nor an object, though it has the spectral appearance of the creature it represents. As a bonus action, you can move the spirit up to 60 feet to a point you can see.\n"
            "\n"
            "The spirit persists for 1 minute. Once you use this feature, you can't use it again until you finish a short or long rest.\n"
            "\n"
            "The effect of the spirit's aura depends on the type of spirit you summon from the options below.\n"
            "\n"
            f"    * Bear Spirit. The bear spirit grants you and your allies its might and endurance. Each creature of your choice in the aura when the spirit appears gains temporary hit points equal to 5 + your druid level ({temp_hp}). In addition, you and your allies gain advantage on Strength checks and Strength saving throws while in the aura.\n"
            "    * Hawk Spirit. The hawk spirit is a consummate hunter, aiding you and your allies with its keen sight. When a creature makes an attack roll against a target in the spirit's aura, you can use your reaction to grant advantage to that attack roll. In addition, you and your allies have advantage on Wisdom (Perception) checks while in the aura.\n"
            "    * Unicorn Spirit. The unicorn spirit lends its protection to those nearby. You and your allies gain advantage on all ability checks made to detect creatures in the spirit's aura. In addition, if you cast a spell using a spell slot that restores hit points to any creature inside or outside the aura, each creature of your choice in the aura also regains hit points equal to your druid level."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")


class MightySummoner(Feature):
    def __init__(self):
        super().__init__(name="Mighty Summoner", origin="Circle of the Shepherd Druid Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Beasts and fey that you conjure are more resilient than normal. Any beast or fey summoned or created by a spell that you cast gains two benefits:\n"
            "\n"
            "    * The creature appears with more hit points than normal: 2 extra hit points per Hit Die it has.\n"
            "    * The damage from its natural weapons is considered magical for the purpose of overcoming immunity and resistance to nonmagical attacks and damage."
        )
        return description


class GuardianSpirit(Feature):
    def __init__(self):
        super().__init__(name="Guardian Spirit", origin="Circle of the Shepherd Druid Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your Spirit Totem safeguards the beasts and fey that you call forth with your magic. When a beast or fey that you summoned or created with a spell ends its turn in your Spirit Totem aura, that creature regains a number of hit points equal to half your druid level."
        return description


class FaithfulSummons(Feature):
    def __init__(self):
        super().__init__(name="Faithful Summons", origin="Circle of the Shepherd Druid Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The nature spirits you commune with protect you when you are the most defenseless. If you are reduced to 0 hit points or are incapacitated against your will, you can immediately gain the benefits of Conjure Animals as if it were cast with a 9th-level spell slot. It summons four beasts of your choice that are challenge rating 2 or lower. The conjured beasts appear within 20 feet of you. If they receive no commands from you, they protect you from harm and attack your foes. The spell lasts for 1 hour, requiring no concentration, or until you dismiss it (no action required).\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Reduced to 0 HP or incapacitated against your will"),
            ("Effect", "Cast Conjure Animals (9th-level); summon four CR 2 or lower beasts within 20 feet"),
            ("Behavior", "Without commands, beasts protect you and attack foes"),
            ("Duration", "1 hour, no concentration; dismiss as free action"),
            ("Regain", "Long rest"),
        ]
