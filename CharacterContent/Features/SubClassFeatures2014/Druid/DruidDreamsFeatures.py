import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BalmOfTheSummerCourt(Feature):
    def __init__(self):
        super().__init__(name="Balm of the Summer Court", origin="Circle of Dreams Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        druid_level = character_stat_block.get_class_level(Definitions.CharacterClass.DRUID)
        half_druid_level = max(1, druid_level // 2)
        description = (
            "At 2nd level, you become imbued with the blessings of the Summer Court. You are a font of energy that offers respite from injuries. You have a pool of fey energy represented by a number of d6s equal to your druid level.\n"
            "\n"
            "As a bonus action, you can choose an ally you can see within 120 feet of you and spend a number of those dice equal to half your druid level or less. Roll the spent dice and add them together. The target regains a number of hit points equal to the total. The target also gains 1 temporary hit point per die spent.\n"
            "\n"
            "You regain the expended dice when you finish a long rest.\n"
            "\n"
            f"At your current Druid level, your pool contains {druid_level}d6, and you can spend up to {half_druid_level} of those dice at once."
        )
        return StringUtils.add_boxes(description, druid_level, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        druid_level = character_stat_block.get_class_level(Definitions.CharacterClass.DRUID)
        half_druid_level = max(1, druid_level // 2)
        return [
            ("What", "Heal an ally within 120 feet"),
            ("Action", "Bonus action"),
            ("Pool", f"{druid_level}d6 fey energy"),
            ("Cost", f"Spend up to {half_druid_level} dice"),
            ("Effect", "Roll spent dice; target regains HP equal to total + 1 temp HP per die"),
            ("Regain", "Long rest"),
        ]


class HearthOfMoonlightAndShadow(Feature):
    def __init__(self):
        super().__init__(name="Hearth of Moonlight and Shadow", origin="Circle of Dreams Druid Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 6th level, home can be wherever you are. During a short or long rest, you can invoke the shadowy power of the Gloaming Court to help guard your respite. At the start of the rest, you touch a point in space, and an invisible, 30-foot-radius sphere of magic appears, centered on that point. Total cover blocks the sphere.\n"
            "\n"
            "While within the sphere, you and your allies gain a +5 bonus to Dexterity (Stealth) and Wisdom (Perception) checks, and any light from open flames in the sphere (a campfire, torches, or the like) isn't visible outside it.\n"
            "\n"
            "The sphere vanishes at the end of the rest or when you leave the sphere."
        )
        return description


class HiddenPaths(Feature):
    def __init__(self):
        super().__init__(name="Hidden Paths", origin="Circle of Dreams Druid Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_mod = character_stat_block.get_ability_modifier(Definitions.Ability.WISDOM)
        uses = max(1, wisdom_mod)
        description = (
            "Starting at 10th level, you can use the hidden, magical pathways that some fey use to traverse space in a blink of an eye. As a bonus action on your turn, you can teleport up to 60 feet to an unoccupied space you can see. Alternatively, you can use your action to teleport one willing creature you touch up to 30 feet to an unoccupied space you can see.\n"
            "\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses of it when you finish a long rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wisdom_mod = character_stat_block.get_ability_modifier(Definitions.Ability.WISDOM)
        uses = max(1, wisdom_mod)
        return [
            ("Self", "Bonus action; teleport up to 60 feet"),
            ("Ally", "Action; teleport willing creature you touch up to 30 feet"),
            ("Uses", f"Wisdom modifier ({uses})"),
            ("Regain", "Long rest"),
        ]


class WalkerInDreams(Feature):
    def __init__(self):
        super().__init__(name="Walker in Dreams", origin="Circle of Dreams Druid Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 14th level, the magic of the Feywild grants you the ability to travel mentally or physically through dreamlands.\n"
            "\n"
            "When you finish a short rest, you can cast one of the following spells, without expending a spell slot or requiring material components: Dream (with you as the messenger), Scrying, or Teleportation Circle.\n"
            "\n"
            "This use of Teleportation Circle is special. Rather than opening a portal to a permanent teleportation circle, it opens a portal to the last location where you finished a long rest on your current plane of existence. If you haven't taken a long rest on your current plane, the spell fails but isn't wasted.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")
