import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class Frenzy(Feature):
    def __init__(self):
        super().__init__(
            name="Frenzy", origin="Path Of The Berserker Barbarian Level 3", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="For the Duration of Your Rage"), usage_tags=["damage"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can go into a frenzy when you rage. If you do so, for the duration of your rage you can make a single melee weapon attack as a bonus action on each of your turns after this one. When your rage ends, you suffer one level of exhaustion."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "When you rage, choose to enter frenzy"),
            ("Benefit", "Make one melee weapon attack as bonus action each turn"),
            ("Duration", "For the duration of your rage"),
            ("Cost", "One level of exhaustion when rage ends"),
        ]


class MindlessRage(Feature):
    def __init__(self):
        super().__init__(
            name="Mindless Rage", origin="Path Of The Berserker Barbarian Level 6", usage_tags=["buff"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can't be charmed or frightened while raging. If you are charmed or frightened when you enter your rage, the effect is suspended for the duration of the rage."
        return description


class IntimidatingPresence(Feature):
    def __init__(self):
        super().__init__(
            name="Intimidating Presence",
            origin="Path Of The Berserker Barbarian Level 10",
            activation=FeatureActivation(action_type=ActionType.ACTION, duration="Until End of Your Next Turn", range="30 Feet"), usage_tags=["control"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your action to frighten someone with your menacing presence. When you do so, choose one creature that you can see within 30 feet of you. If the creature can see or hear you, it must succeed on a Wisdom saving throw (DC equal to 8 + your proficiency bonus + your Charisma modifier) or be frightened of you until the end of your next turn. On subsequent turns, you can use your action to extend the duration of this effect on the frightened creature until the end of your next turn. This effect ends if the creature ends its turn out of line of sight or more than 60 feet away from you.\n"
            "If the creature succeeds on its saving throw, you can't use this feature on that creature again for 24 hours."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        charisma_modifier = character_stat_block.get_ability_modifier(Definitions.Ability.CHARISMA)
        dc = 8 + proficiency_bonus + charisma_modifier
        return [
            ("Action", "Action"),
            ("Range", "30 feet (creature must see/hear you)"),
            ("Save", f"Wisdom DC {dc}"),
            ("On Failure", "Frightened until end of your next turn"),
            ("Extend", "Use action on subsequent turns to extend"),
            ("Ends If", "Creature ends turn out of sight or >60 feet away"),
            ("Cooldown", "24 hours if save succeeds"),
        ]


class Retaliation(Feature):
    def __init__(self):
        super().__init__(
            name="Retaliation", origin="Path Of The Berserker Barbarian Level 14", activation=FeatureActivation(action_type=ActionType.REACTION, range="5 Feet"), usage_tags=["damage"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take damage from a creature that is within 5 feet of you, you can use your reaction to make a melee weapon attack against that creature."
        return description
