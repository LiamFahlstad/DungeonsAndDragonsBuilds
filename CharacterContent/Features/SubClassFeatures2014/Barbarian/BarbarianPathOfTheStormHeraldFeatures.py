import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock


def _flat_damage_value(barbarian_level: int) -> int:
    if barbarian_level >= 20:
        return 6
    if barbarian_level >= 15:
        return 5
    if barbarian_level >= 10:
        return 4
    if barbarian_level >= 5:
        return 3
    return 2


def _dice_damage_value(barbarian_level: int) -> str:
    if barbarian_level >= 20:
        return "4d6"
    if barbarian_level >= 15:
        return "3d6"
    if barbarian_level >= 10:
        return "2d6"
    return "1d6"


class StormAura(Feature):
    def __init__(self, environment: Definitions.BarbarianStormEnvironment):
        super().__init__(name="Storm Aura", origin="Path Of The Storm Herald Barbarian Level 3", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="While You Rage", range="10 Feet"), usage_tags=["damage", "heal", "control"])
        self.environment = environment

    def calculate_dc(self, character_stat_block: CharacterStatBlock) -> int:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        constitution_modifier = character_stat_block.get_constitution_modifier()
        return 8 + proficiency_bonus + constitution_modifier

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you select this path at 3rd level, you emanate a stormy, magical aura while you rage. The aura extends 10 feet from you in every direction, but not through total cover.\n"
            "\n"
            "Your aura has an effect that activates when you enter your rage, and you can activate the effect again on each of your turns as a bonus action. Choose desert, sea, or tundra. Your aura's effect depends on that chosen environment, as detailed below. You can change your environment choice whenever you gain a level in this class.\n"
            "\n"
            "If your aura's effects require a saving throw, the DC equals 8 + your proficiency bonus + your Constitution modifier.\n"
            "\n"
            "Desert. When this effect is activated, all other creatures in your aura take 2 fire damage each. The damage increases when you reach certain levels in this class, increasing to 3 at 5th level, 4 at 10th level, 5 at 15th level, and 6 at 20th level.\n"
            "\n"
            "Sea. When this effect is activated, you can choose one other creature you can see in your aura. The target must make a Dexterity saving throw. The target takes 1d6 lightning damage on a failed save, or half as much damage on a successful one. The damage increases when you reach certain levels in this class, increasing to 2d6 at 10th level, 3d6 at 15th level, and 4d6 at 20th level.\n"
            "\n"
            "Tundra. When this effect is activated, each creature of your choice in your aura gains 2 temporary hit points, as icy spirits inure it to suffering. The temporary hit points increase when you reach certain levels in this class, increasing to 3 at 5th level, 4 at 10th level, 5 at 15th level, and 6 at 20th level.\n"
            "\n"
            f"You have chosen the {self.environment.value} environment."
        )
        return description


class StormSoul(Feature):
    def __init__(self, environment: Definitions.BarbarianStormEnvironment):
        super().__init__(name="Storm Soul", origin="Path Of The Storm Herald Barbarian Level 6", usage_tags=["utility", "buff"])
        self.environment = environment

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The storm grants you benefits even when your aura isn't active. The benefits are based on the environment you chose for your Storm Aura.\n"
            "\n"
            "Desert. You gain resistance to fire damage, and you don't suffer the effects of extreme heat, as described in the Dungeon Master's Guide. Moreover, as an action, you can touch a flammable object that isn't being worn or carried by anyone else and set it on fire.\n"
            "\n"
            "Sea. You gain resistance to lightning damage, and you can breathe underwater. You also gain a swimming speed of 30 feet.\n"
            "\n"
            "Tundra. You gain resistance to cold damage, and you don't suffer the effects of extreme cold, as described in the Dungeon Master's Guide. Moreover, as an action, you can touch water and turn a 5-foot cube of it into ice, which melts after 1 minute. This action fails if a creature is in the cube.\n"
            "\n"
            f"You have chosen the {self.environment.value} environment, so you gain that environment's benefits."
        )
        return description


class ShieldingStorm(Feature):
    def __init__(self):
        super().__init__(name="Shielding Storm", origin="Path Of The Storm Herald Barbarian Level 10", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn to use your mastery of the storm to protect others. Each creature of your choice has the damage resistance you gained from the Storm Soul feature while the creature is in your Storm Aura."
        )
        return description


class RagingStorm(Feature):
    def __init__(self, environment: Definitions.BarbarianStormEnvironment):
        super().__init__(name="Raging Storm", origin="Path Of The Storm Herald Barbarian Level 14", activation=FeatureActivation(action_type=ActionType.REACTION), usage_tags=["damage", "control"])
        self.environment = environment

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The power of the storm you channel grows mightier, lashing out at your foes. The effect is based on the environment you chose for your Storm Aura.\n"
            "\n"
            "Desert. Immediately after a creature in your aura hits you with an attack, you can use your reaction to force that creature to make a Dexterity saving throw. On a failed save, the creature takes fire damage equal to half your Barbarian level.\n"
            "\n"
            "Sea. When you hit a creature in your aura with an attack, you can use your reaction to force that creature to make a Strength saving throw. On a failed save, the creature is knocked prone, as if struck by a wave.\n"
            "\n"
            "Tundra. Whenever the effect of your Storm Aura is activated, you can choose one creature you can see in the aura. That creature must succeed on a Strength saving throw, or its speed is reduced to 0 until the start of your next turn, as magical frost covers it.\n"
            "\n"
            f"You have chosen the {self.environment.value} environment, so you gain that environment's benefit."
        )
        return description
