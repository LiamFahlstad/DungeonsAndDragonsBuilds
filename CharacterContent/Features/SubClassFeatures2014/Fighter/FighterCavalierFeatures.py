from Core.Definitions import CharacterClass, MAX_ABILITY_MODIFIER
from CharacterContent.Features.Core.BaseFeatures import FeatureUses, Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BonusProficiency(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiency", origin="Cavalier Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency in one of the following skills of your choice: Animal Handling, History, Insight, Performance, or Persuasion. Alternatively, you learn one language of your choice."
        return description


class BornToTheSaddle(Feature):
    def __init__(self):
        super().__init__(name="Born to the Saddle", origin="Cavalier Fighter Level 3", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your mastery as a rider becomes apparent. You have advantage on saving throws made to avoid falling off your mount. If you fall off your mount and descend no more than 10 feet, you can land on your feet if you're not incapacitated.\n"
            "Finally, mounting or dismounting a creature costs you only 5 feet of movement, rather than half your speed."
        )
        return description


class UnwaveringMark(Feature):
    def __init__(self):
        super().__init__(name="Unwavering Mark", origin="Cavalier Fighter Level 3", activation=FeatureActivation(duration="Until End of Your Next Turn", range="5 Feet"), usage_tags=["damage", "control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can menace your foes, foiling their attacks and punishing them for harming others. When you hit a creature with a melee weapon attack, you can mark the creature until the end of your next turn. This effect ends early if you are incapacitated or you die, or if someone else marks the creature.\n"
            "While it is within 5 feet of you, a creature marked by you has disadvantage on any attack roll that doesn't target you.\n"
            "In addition, if a creature marked by you deals damage to anyone other than you, you can make a special melee weapon attack against the marked creature as a bonus action on your next turn. You have advantage on the attack roll, and if it hits, the attack's weapon deals extra damage to the target equal to half your fighter level.\n"
            "You regain all expended uses of it when you finish a long rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        strength_modifier = character_stat_block.get_strength_modifier()
        uses = max(1, strength_modifier)
        fighter_level = character_stat_block.get_class_level(CharacterClass.FIGHTER)
        extra_damage = fighter_level // 2

        return [
            ("Trigger", "Hit a creature with melee weapon attack"),
            ("Mark Effect", "Disadvantage on attacks not targeting you (5 ft, until end of your next turn)"),
            ("Bonus Action", "Make special melee attack against marked creature with advantage"),
            ("Extra Damage", f"{extra_damage} (half your fighter level)"),
            ("Uses", f"{uses} (Strength modifier, minimum 1)"),
            ("Regain", "Long rest"),
        ]


class WardingManeuver(Feature):
    def __init__(self):
        super().__init__(name="Warding Maneuver", origin="Cavalier Fighter Level 7", activation=FeatureActivation(action_type=ActionType.REACTION, range="5 Feet"), usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn to fend off strikes directed at you, your mount, or other creatures nearby. If you or a creature you can see within 5 feet of you is hit by an attack, you can roll 1d8 as a reaction if you're wielding a melee weapon or a shield. Roll the die, and add the number rolled to the target's AC against that attack. If the attack still hits, the target has resistance against the attack's damage.\n"
            "You regain all expended uses of it when you finish a long rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        constitution_modifier = character_stat_block.get_constitution_modifier()
        uses = max(1, constitution_modifier)

        return [
            ("Trigger", "You or ally within 5 feet is hit by an attack"),
            ("Action", "Reaction (must wield melee weapon or shield)"),
            ("Effect", "Roll 1d8, add to target's AC; or resistance if still hits"),
            ("Uses", f"{uses} (Constitution modifier, minimum 1)"),
            ("Regain", "Long rest"),
        ]


class HoldTheLine(Feature):
    def __init__(self):
        super().__init__(name="Hold the Line", origin="Cavalier Fighter Level 10", activation=FeatureActivation(duration="Until End of Current Turn", range="5 Feet"), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You become a master of locking down your enemies. Creatures provoke an opportunity attack from you when they move 5 feet or more while within your reach, and if you hit a creature with an opportunity attack, the target's speed is reduced to 0 until the end of the current turn."
        return description


class FerociousCharger(Feature):
    def __init__(self):
        super().__init__(name="Ferocious Charger", origin="Cavalier Fighter Level 15", usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can run down your foes, whether you're mounted or not. If you move at least 10 feet in a straight line right before attacking a creature and you hit it with the attack, that target must succeed on a Strength saving throw (DC 8 + your proficiency bonus + your Strength modifier) or be knocked prone. You can use this feature only once on each of your turns."
        )
        return description

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        strength_modifier = character_stat_block.get_strength_modifier()
        return 8 + proficiency_bonus + strength_modifier

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        dc = self.calculate_dc(character_stat_block)

        return [
            ("Trigger", "Move 10+ feet in straight line, then hit with attack"),
            ("Effect", f"Target must succeed on Strength save (DC {dc}) or be knocked prone"),
            ("Frequency", "Once per turn"),
        ]


class VigilantDefender(Feature):
    def __init__(self):
        super().__init__(name="Vigilant Defender", origin="Cavalier Fighter Level 18", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You respond to danger with extraordinary vigilance. In combat, you get a special reaction that you can take once on every creature's turn, except your turn. You can use this special reaction only to make an opportunity attack, and you can't use it on the same turn that you take your normal reaction."
        return description
