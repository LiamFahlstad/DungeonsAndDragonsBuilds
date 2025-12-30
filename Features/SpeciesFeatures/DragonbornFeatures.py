from enum import Enum

import Definitions
from Definitions import Ability, CreatureSize
from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

SPEED = 30  # Given by your species
SIZE = CreatureSize.MEDIUM  # Given by your species


class DragonColor(str, Enum):
    BLACK = "Black"
    BLUE = "Blue"
    BRASS = "Brass"
    BRONZE = "Bronze"
    COPPER = "Copper"
    GOLD = "Gold"
    GREEN = "Green"
    RED = "Red"
    SILVER = "Silver"
    WHITE = "White"


class Darkvision(TextFeature):
    def __init__(self):
        super().__init__(name="Darkvision", origin="Gnome Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "You have Darkvision with a range of 60 feet."


class DamageResistance(TextFeature):
    def __init__(self, dragon_color: DragonColor):
        self.color = dragon_color
        self.damage_type = get_damage_type_from_color(dragon_color)
        super().__init__(name="Damage Resistance", origin="Dragonborn Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return f"You have Resistance against {self.damage_type.value} damage because your Draconic Ancestry is {self.color.value} dragon."


class BreathWeapon(TextFeature):
    def __init__(self, dragon_color: DragonColor):
        self.color = dragon_color
        self.damage_type = get_damage_type_from_color(dragon_color)
        super().__init__(name="Breath Weapon", origin="Dragonborn Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        constitution_modifier = character_stat_block.get_ability_modifier(
            Ability.CONSTITUTION
        )
        proficiency_bonus = character_stat_block.get_proficiency_bonus()

        if character_stat_block.character_level < 5:
            damage = "1d10"
        elif character_stat_block.character_level < 11:
            damage = "2d10"
        elif character_stat_block.character_level < 17:
            damage = "3d10"
        else:
            damage = "4d10"

        text = (
            f"When you take the Attack action on your turn, you can replace one of your attacks with an exhalation of magical energy in either a 15-foot Cone or a 30-foot Line that is 5 feet wide (choose the shape each time). Each creature in that area must make a Dexterity saving throw (DC 8 plus your Constitution modifier and Proficiency Bonus = {8 + constitution_modifier + proficiency_bonus}).\n"
            f"On a failed save, a creature takes {damage} {self.damage_type} damage because your Draconic Ancestry is {self.color.value} dragon."
        )
        return text


class DraconicFlight(TextFeature):
    def __init__(self):
        super().__init__(name="Dragonic Flight", origin="Dragonborn Trait")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = "When you reach character level 5, you can channel draconic magic to give yourself temporary flight. As a Bonus Action, you sprout spectral wings on your back that last for 10 minutes or until you retract the wings (no action required) or have the Incapacitated condition. During that time, you have a Fly Speed equal to your Speed. Your wings appear to be made of the same energy as your Breath Weapon. Once you use this trait, you can't use it again until you finish a Long Rest."
        return text


def get_damage_type_from_color(dragon_color: DragonColor) -> Definitions.DamageType:
    dragon_damage_type = {
        DragonColor.BLACK: Definitions.DamageType.ACID,
        DragonColor.BLUE: Definitions.DamageType.LIGHTNING,
        DragonColor.BRASS: Definitions.DamageType.FIRE,
        DragonColor.BRONZE: Definitions.DamageType.LIGHTNING,
        DragonColor.COPPER: Definitions.DamageType.ACID,
        DragonColor.GOLD: Definitions.DamageType.FIRE,
        DragonColor.GREEN: Definitions.DamageType.POISON,
        DragonColor.RED: Definitions.DamageType.FIRE,
        DragonColor.SILVER: Definitions.DamageType.COLD,
        DragonColor.WHITE: Definitions.DamageType.COLD,
    }
    return dragon_damage_type[dragon_color]
