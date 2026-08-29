from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses
from Core.Definitions import Ability
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class AdjustDensity(Feature):
    def __init__(self):
        super().__init__(
            name="Adjust Density",
            origin="Graviturgy Wizard Level 3",
            action_type="action",
            duration="Up To 1 Minute Or Until Concentration Ends",
            range="30 Feet",
            usage_tags=["buff", "control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 2nd level, as an action, you can magically alter the weight of one object or creature you can see within 30 feet of you. The object or creature must be Large or smaller. The target's weight is halved or doubled for up to 1 minute or until your concentration ends (as if you were concentrating on a spell).\n"
            "\n"
            "While the weight of a creature is halved by this effect, the creature's speed increases by 10 feet, it can jump twice as far as normal, and it has disadvantage on Strength checks and Strength saving throws.\n"
            "\n"
            "While the weight of a creature is doubled by this effect, the creature's speed is reduced by 10 feet, and it has advantage on Strength checks and Strength saving throws.\n"
            "\n"
            "Upon reaching 10th level in this class, you can target an object or a creature that is Huge or smaller."
        )
        return description


class GravityWell(Feature):
    def __init__(self):
        super().__init__(
            name="Gravity Well",
            origin="Graviturgy Wizard Level 6",
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach 6th level, whenever you cast a spell on a creature, you can move the target 5 feet to an unoccupied space of your choice if the target is willing to move, the spell hits it with an attack, or it fails a saving throw against the spell."
        return description


class ViolentAttraction(Feature):
    def __init__(self):
        super().__init__(
            name="Violent Attraction",
            origin="Graviturgy Wizard Level 10",
            action_type="reaction",
            range="60 Feet",
            usage_tags=["damage"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        int_mod = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        uses = max(1, int_mod)
        description = (
            "At 10th level, when another creature that you can see within 60 feet of you hits with a weapon attack, you can use your reaction to increase the attack's velocity, causing the attack's target to take an extra 1d10 damage of the weapon's type.\n"
            "\n"
            "Alternatively, if a creature within 60 feet of you takes damage from a fall, you can use your reaction to increase the fall's damage by 2d10.\n"
            "\n"
            "You can use this feature a minimum of once per long rest, and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class EventHorizon(Feature):
    def __init__(self):
        super().__init__(
            name="Event Horizon",
            origin="Graviturgy Wizard Level 14",
            action_type="action",
            duration="1 Minute Or Until Concentration Ends",
            range="30 Feet",
            usage_tags=["damage", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 14th level, as an action, you can magically emit a powerful field of gravitational energy that tugs at other creatures for up to 1 minute or until your concentration ends (as if you were concentrating on a spell). For the duration, whenever a creature hostile to you starts its turn within 30 feet of you, it must make a Strength saving throw against your spell save DC. On a failed save, it takes 2d10 force damage, and its speed is reduced to 0 until the start of its next turn. On a successful save, it takes half as much damage, and every foot it moves this turn costs 2 extra feet of movement.\n"
            "\n"
            "Once you use this feature, you can't do so again until you finish a long rest or until you expend a spell slot of 3rd level or higher on it."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Duration", "1 minute or until concentration ends"),
            ("Range", "30 feet"),
            ("Trigger", "Hostile creature starts its turn within range"),
            ("Save", "Strength saving throw vs spell save DC"),
            ("On Fail", "2d10 force damage, speed 0 until start of next turn"),
            ("On Success", "Half damage, movement costs 2 extra feet per foot"),
            ("Recharge", "Long rest or 3rd+ level spell slot"),
        ]
