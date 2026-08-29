from Core.Definitions import BARD_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import FeatureUses, Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class PsychicBlades(Feature):
    def __init__(self):
        super().__init__(name="Psychic Blades", origin="College of Whispers Bard Level 3", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if character_stat_block.character_level < 5:
            psychic_damage = "2d6"
        elif character_stat_block.character_level < 10:
            psychic_damage = "3d6"
        elif character_stat_block.character_level < 15:
            psychic_damage = "5d6"
        else:
            psychic_damage = "8d6"

        description = (
            "When you join the College of Whispers at 3rd level, you gain the ability to make your weapon attacks magically toxic to a creature's mind.\n"
            "\n"
            f"When you hit a creature with a weapon attack, you can expend one use of your Bardic Inspiration to deal an additional {psychic_damage} psychic damage to that target. You can do so only once per round on your turn.\n"
            "\n"
            "The psychic damage increases when you reach certain levels in this class, increasing to 3d6 at 5th level, 5d6 at 10th level, and 8d6 at 15th level."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        if character_stat_block.character_level < 5:
            psychic_damage = "2d6"
        elif character_stat_block.character_level < 10:
            psychic_damage = "3d6"
        elif character_stat_block.character_level < 15:
            psychic_damage = "5d6"
        else:
            psychic_damage = "8d6"

        return [
            ("Trigger", "Hit a creature with a weapon attack"),
            ("Cost", "1 Bardic Inspiration use"),
            ("Damage", f"{psychic_damage} psychic"),
            ("Limit", "Once per round on your turn"),
        ]


class WordsOfTerror(Feature):
    def __init__(self):
        super().__init__(name="Words of Terror", origin="College of Whispers Bard Level 3", duration="1 Hour or Until Attacked or Damaged", usage_tags=["control"])

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Requirement", "Speak to humanoid alone for 1+ minute"),
            ("Trigger", "End of conversation"),
            ("Save", "Wisdom save vs Spell Save DC"),
            ("Effect (Fail)", "Frightened of you or creature of your choice for 1 hour (or until attacked/damaged)"),
            ("Effect (Success)", "Target has no hint of attempt"),
            ("Recharge", "Short or long rest"),
        ]

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, you learn to infuse innocent-seeming words with an insidious magic that can inspire terror.\n"
            "\n"
            "If you speak to a humanoid alone for at least 1 minute, you can attempt to seed paranoia and fear into its mind. At the end of the conversation, the target must succeed on a Wisdom saving throw against your spell save DC or be frightened of you or another creature of your choice. The target is frightened in this way for 1 hour, until it is attacked or damaged, or until it witnesses its allies being attacked or damaged.\n"
            "\n"
            "If the target succeeds on its saving throw, the target has no hint that you tried to frighten it.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short rest or long rest."
        )
        return description


class MantleOfWhispers(Feature):
    def __init__(self):
        super().__init__(name="Mantle of Whispers", origin="College of Whispers Bard Level 6", action_type="action", duration="1 Hour or Until Ended", range="30 Feet", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 6th level, you gain the ability to adopt a humanoid's persona. When a humanoid dies within 30 feet of you, you can magically capture its shadow using your reaction. You retain this shadow until you use it or you finish a long rest.\n"
            "\n"
            "You can use the shadow as an action. When you do so, it vanishes, magically transforming into a disguise that appears on you. You now look like the dead person, but healthy and alive. This disguise lasts for 1 hour or until you end it as a bonus action.\n"
            "\n"
            "While you're in the disguise, you gain access to all information that the humanoid would freely share with a casual acquaintance. Such information includes general details on its background and personal life, but doesn't include secrets. The information is enough that you can pass yourself off as the person by drawing on its memories.\n"
            "\n"
            "Another creature can see through this disguise by succeeding on a Wisdom (Insight) check contested by your Charisma (Deception) check. You gain a +5 bonus to your check.\n"
            "\n"
            "Once you capture a shadow with this feature, you can't capture another one with it until you finish a short or long rest."
        )
        return description


class ShadowLore(Feature):
    def __init__(self):
        super().__init__(name="Shadow Lore", origin="College of Whispers Bard Level 14", action_type="action", duration="8 Hours or Until Attacked or Damaged", range="30 Feet", usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 14th level, you gain the ability to weave dark magic into your words and tap into a creature's deepest fears.\n"
            "\n"
            "As an action, you magically whisper a phrase that only one creature of your choice within 30 feet of you can hear. The target must make a Wisdom saving throw against your spell save DC. It automatically succeeds if it doesn't share a language with you or if it can't hear you. On a successful saving throw, your whisper sounds like unintelligible mumbling and has no effect.\n"
            "\n"
            "If the target fails its saving throw, it is charmed by you for the next 8 hours or until you or your allies attack or damage it. It interprets the whispers as a description of its most mortifying secret.\n"
            "\n"
            "While you gain no knowledge of this secret, the target is convinced you know it. While charmed in this way, the creature obeys your commands for fear that you will reveal its secret. It won't risk its life for you or fight for you, unless it was already inclined to do so. It grants you favors and gifts it would offer to a close friend.\n"
            "\n"
            "When the effect ends, the creature has no understanding of why it held you in such fear.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "30 feet"),
            ("Target", "One creature you can see"),
            ("Save", "Wisdom save vs Spell Save DC"),
            ("Effect (Fail)", "Charmed for 8 hours or until attacked/damaged; obeys your commands"),
            ("Effect (Success)", "No effect"),
            ("Cost", "Reusable with long rest"),
        ]
