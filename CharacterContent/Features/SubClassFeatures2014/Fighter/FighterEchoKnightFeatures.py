from Core.Definitions import MAX_ABILITY_MODIFIER
from CharacterContent.Features.Core.BaseFeatures import FeatureUses, Feature, FeatureActivation, ActionType, RegainedOn
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class ManifestEcho(Feature):
    def __init__(self):
        super().__init__(name="Manifest Echo", origin="Echo Knight Fighter Level 3", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, range="15 Feet"), usage_tags=["damage", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, you can use a bonus action to magically manifest an echo of yourself in an unoccupied space you can see within 15 feet of you. This echo is a magical, translucent, gray image of you that lasts until it is destroyed, until you dismiss it as a bonus action, until you manifest another echo, or until you're incapacitated.\n"
            "\n"
            "Your echo has AC 14 + your proficiency bonus, 1 hit point, and immunity to all conditions. If it has to make a saving throw, it uses your saving throw bonus for the roll. It is the same size as you, and it occupies its space. On your turn, you can mentally command the echo to move up to 30 feet in any direction (no action required). If your echo is ever more than 30 feet from you at the end of your turn, it is destroyed.\n"
            "\n"
            "As a bonus action, you can teleport, magically swapping places with your echo at a cost of 15 feet of your movement, regardless of the distance between the two of you.\n"
            "\n"
            "When you take the Attack action on your turn, any attack you make with that action can originate from your space or the echo's space. You make this choice for each attack.\n"
            "\n"
            "When a creature that you can see within 5 feet of your echo moves at least 5 feet away from it, you can use your reaction to make an opportunity attack against that creature as if you were in the echo's space."
        )
        return description


class UnleashIncarnation(Feature):
    def __init__(self):
        super().__init__(name="Unleash Incarnation", origin="Echo Knight Fighter Level 3", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, you can heighten your echo's fury. Whenever you take the Attack action, you can make one additional melee attack from the echo's position.\n"
            "\n"
            "You regain all expended uses when you finish a long rest."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        constitution_modifier = character_stat_block.get_constitution_modifier()
        uses = max(1, constitution_modifier)

        return [
            ("Trigger", "You take the Attack action"),
            ("Effect", "Make one additional melee attack from echo's position"),
            ("Uses", f"{uses} (Constitution modifier, minimum 1)"),
            ("Regain", "Long rest"),
        ]


class EchoAvatar(Feature):
    def __init__(self):
        super().__init__(name="Echo Avatar", origin="Echo Knight Fighter Level 7", activation=FeatureActivation(action_type=ActionType.ACTION, duration="Up to 10 Minutes", range="1,000 Feet"), usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 7th level, you can temporarily transfer your consciousness to your echo. As an action, you can see through your echo's eyes and hear through its ears. During this time, you are deafened and blinded. You can sustain this effect for up to 10 minutes, and you can end it at any time (requires no action). While your echo is being used in this way, it can be up to 1,000 feet away from you without being destroyed."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Effect", "See/hear through echo; you are deafened and blinded"),
            ("Duration", "Up to 10 minutes (can end at any time)"),
            ("Range", "Echo can be up to 1,000 feet away without being destroyed"),
        ]


class ShadowMartyr(Feature):
    def __init__(self):
        super().__init__(name="Shadow Martyr", origin="Echo Knight Fighter Level 10", activation=FeatureActivation(action_type=ActionType.REACTION, range="5 Feet"), usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 10th level, you can make your echo throw itself in front of an attack directed at another creature that you can see. Before the attack roll is made, you can use your reaction to teleport the echo to an unoccupied space within 5 feet of the targeted creature. The attack roll that triggered the reaction is instead made against your echo.\n\nOnce you use this feature, you can't use it again until you finish a short or long rest."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Attack directed at creature you can see"),
            ("Action", "Reaction (before attack roll)"),
            ("Effect", "Teleport echo to 5 ft of target; attack targets echo instead"),
            ("Uses", "1 per short or long rest"),
        ]


class ReclaimPotential(Feature):
    def __init__(self):
        super().__init__(name="Reclaim Potential", origin="Echo Knight Fighter Level 15", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "By 15th level, you've learned to absorb the fleeting magic of your echo. When an echo of yours is destroyed by taking damage, you can gain a number of temporary hit points equal to 2d6 + your Constitution modifier, provided you don't already have temporary hit points.\n"
            "\n"
            "You regain all expended uses when you finish a long rest."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        constitution_modifier = character_stat_block.get_constitution_modifier()
        uses = max(1, constitution_modifier)

        return [
            ("Trigger", "Echo destroyed by taking damage"),
            ("Effect", "Gain 2d6 + your Constitution modifier temporary HP"),
            ("Condition", "Only if you don't already have temporary HP"),
            ("Uses", f"{uses} (Constitution modifier, minimum 1)"),
            ("Regain", "Long rest"),
        ]


class LegionOfOne(Feature):
    def __init__(self):
        super().__init__(name="Legion of One", origin="Echo Knight Fighter Level 18", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION), usage_tags=["damage", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 18th level, you can use a bonus action to create two echoes with your Manifest Echo feature, and these echoes can co-exist. If you try to create a third echo, the previous two echoes are destroyed. Anything you can do from one echo's position can be done from the other's instead.\n"
            "\n"
            "In addition, when you roll initiative and have no uses of your Unleash Incarnation feature left, you regain one use of that feature."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.INITIATIVE_ROLL
