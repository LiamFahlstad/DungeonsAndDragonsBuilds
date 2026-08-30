from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import FeatureUses, Feature, FeatureActivation, ActionType, RegainedOn, FeatureTarget
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class MoteOfPotential(Feature):
    def __init__(self):
        super().__init__(name="Mote of Potential", origin="College of Creation Bard Level 3", activation=FeatureActivation(duration="Until Bardic Inspiration Die is Lost", range="5 Feet"), usage_tags=["damage", "buff"])

    def target(
        self, character_stat_block: CharacterStatBlock
    ) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Give a creature a Bardic Inspiration die"),
            ("Mote Effect: Ability Check", "Roll die again, choose which roll to use"),
            ("Mote Effect: Attack Roll", "Targets within 5 ft make CON save or take thunder damage equal to die roll"),
            ("Mote Effect: Saving Throw", "Creature gains temp HP equal to die roll + CHA modifier (min 1)"),
            ("Duration", "Until Bardic Inspiration die is lost"),
        ]

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you join the College of Creation at 3rd level, whenever you give a creature a Bardic Inspiration die, you can utter a note from the Song of Creation to create a Tiny mote of potential, which orbits within 5 feet of that creature. The mote is intangible and invulnerable, and it lasts until the Bardic Inspiration die is lost. The mote looks like a musical note, a star, a flower, or another symbol of art or life that you choose.\n"
            "\n"
            "When the creature uses the Bardic Inspiration die, the mote provides an additional effect based on whether the die benefits an ability check, an attack roll, or a saving throw, as detailed below:\n"
            "\n"
            "Ability Check. When the creature rolls the Bardic Inspiration die to add it to an ability check, the creature can roll the Bardic Inspiration die again and choose which roll to use, as the mote pops and emits colorful, harmless sparks for a moment.\n"
            "\n"
            "Attack Roll. Immediately after the creature rolls the Bardic Inspiration die to add it to an attack roll against a target, the mote thunderously shatters. The target and each creature of your choice that you can see within 5 feet of it must succeed on a Constitution saving throw against your spell save DC or take thunder damage equal to the number rolled on the Bardic Inspiration die.\n"
            "\n"
            "Saving Throw. Immediately after the creature rolls the Bardic Inspiration die and adds it to a saving throw, the mote vanishes with the sound of soft music, causing the creature to gain temporary hit points equal to the number rolled on the Bardic Inspiration die plus your Charisma modifier (minimum of 1 temporary hit point)."
        )
        return description


class PerformanceOfCreation(Feature):
    def __init__(self):
        super().__init__(name="Performance of Creation", origin="College of Creation Bard Level 3", activation=FeatureActivation(action_type=ActionType.ACTION, duration="Proficiency Bonus Hours", range="10 Feet"), usage_tags=["utility"], uses=FeatureUses(max_uses=1, regain_all_on="long rest"))

    def target(
        self, character_stat_block: CharacterStatBlock
    ) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Also at 3rd level, as an action, you can channel the magic of the Song of Creation to create one nonmagical item of your choice in an unoccupied space within 10 feet of you. The item must appear on a surface or in a liquid that can support it. The gp value of the item can't be more than 20 times your bard level, and the item must be Medium or smaller. The item glimmers softly, and a creature can faintly hear music when touching it. The created item disappears after a number of hours equal to your proficiency bonus. For examples of items you can create, see the equipment chapter of the Player's Handbook.\n"
            "\n"
            "Once you create an item with this feature, you can't do so again until you finish a long rest, unless you expend a spell slot of 2nd level or higher to use this feature again. You can have only one item created by this feature at a time; if you use this action and already have an item from this feature, the first one immediately vanishes.\n"
            "\n"
            "The size of the item you can create with this feature increases by one size category when you reach 6th level (Large) and 14th level (Huge)."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class AnimatingPerformance(Feature):
    def __init__(self):
        super().__init__(name="Animating Performance", origin="College of Creation Bard Level 6", activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Hour or Until Reduced to 0 HP or Death", range="30 Feet"), usage_tags=["utility"], uses=FeatureUses(max_uses=1, regain_all_on="long rest"))

    def target(
        self, character_stat_block: CharacterStatBlock
    ) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "By 6th level, as an action, you can animate one Large or smaller nonmagical item within 30 feet of you that isn't being worn or carried. The animate item uses the Dancing Item stat block, which uses your proficiency bonus (PB). The item is friendly to you and your companions and obeys your commands. It lives for 1 hour, until it is reduced to 0 hit points, or until you die.\n"
            "\n"
            "In combat, the item shares your initiative count, but it takes its turn immediately after yours. It can move and use its reaction on its own, but the only action it takes on its turn is the Dodge action, unless you take a bonus action on your turn to command it to take another action. That action can be one in its stat block or some other action. If you are incapacitated, the item can take any action of its choice, not just Dodge.\n"
            "\n"
            "When you use your Bardic Inspiration feature, you can command the item as part of the same bonus action you use for Bardic Inspiration.\n"
            "\n"
            "Once you animate an item with this feature, you can't do so again until you finish a long rest, unless you expend a spell slot of 3rd level or higher to use this feature again. You can have only one item animated by this feature at a time; if you use this action and already have a dancing item from this feature, the first one immediately becomes inanimate.\n"
            "\n"
            "Dancing Item\n"
            "Large or smaller construct\n"
            "Armor Class: 16 (natural armor)\n"
            "Hit Points: 10 + 5 times your bard level\n"
            "Speed: 30 ft., fly 30 ft. (hover)\n"
            "STR\tDEX\tCON\tINT\tWIS\tCHA\n"
            "18 (+4)\t14 (+2)\t16 (+3)\t4 (−3)\t10 (+0)\t6 (−2)\n"
            "Damage Immunities: poison, psychic\n"
            "Condition Immunities: charmed, exhaustion, poisoned, frightened\n"
            "Senses: darkvision 60 ft., passive Perception 10\n"
            "Languages: understands the languages you speak\n"
            "Challenge: —\n"
            "Proficiency Bonus (PB): equals your bonus\n"
            "Immutable Form. The item is immune to any spell or effect that would alter its form.\n"
            "Irrepressible Dance. When any creature starts its turn within 10 feet of the item, the item can increase or decrease (your choice) the walking speed of that creature by 10 feet until the end of the turn, provided the item isn't incapacitated.\n"
            "Actions\n"
            "Force-Empowered Slam. Melee Weapon Attack: your spell attack modifier to hit, reach 5 ft., one target you can see. Hit: 1d10 + PB force damage."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class CreativeCrescendo(Feature):
    def __init__(self):
        super().__init__(name="Creative Crescendo", origin="College of Creation Bard Level 14", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 14th level, when you use your Performance of Creation feature, you can create more than one item at once. The number of items equals your Charisma modifier (minimum of two items). If you create an item that would exceed that number, you choose which of the previously created items disappears. Only one of these items can be of the maximum size you can create; the rest must be Small or Tiny.\n"
            "\n"
            "You are no longer limited by gp value when creating items with Performance of Creation."
        )
        return description
