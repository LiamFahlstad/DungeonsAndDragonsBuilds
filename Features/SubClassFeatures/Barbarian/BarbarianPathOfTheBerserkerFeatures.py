import Definitions
from Definitions import BARBARIAN_HIT_DIE
from Features.ClassFeatures.Barbarian.BarbarianFeatures import get_rage_damage_bonus
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class Frenzy(Feature):
    def __init__(self):
        super().__init__(
            name="Frenzy", origin="Path Of The Berserker Barbarian Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        rage_damage_bonus = get_rage_damage_bonus(
            character_stat_block.get_class_level(Definitions.CharacterClass.BARBARIAN)
        )
        description = f"If you use Reckless Attack while your Rage is active, you deal extra damage to the first target you hit on your turn with a Strength-based attack. To determine the extra damage, roll a number of d6s equal to your Rage Damage bonus ({rage_damage_bonus}), and add them together. The damage has the same type as the weapon or Unarmed Strike used for the attack."
        return description


class MindlessRage(Feature):
    def __init__(self):
        super().__init__(
            name="Mindless Rage", origin="Path Of The Berserker Barbarian Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Immunity to the Charmed and Frightened conditions while your Rage is active. If you're Charmed or Frightened when you enter your Rage, the condition ends on you."
        return description


class Retaliation(Feature):
    def __init__(self):
        super().__init__(
            name="Retaliation", origin="Path Of The Berserker Barbarian Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you take damage from a creature that is within 5 feet of you, you can take a Reaction to make one melee attack against that creature, using a weapon or an Unarmed Strike."
        return description


class IntimidatingPresence(Feature):
    def __init__(self):
        super().__init__(
            name="Intimidating Presence",
            origin="Path Of The Berserker Barbarian Level 14",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can strike terror into others with your menacing presence and primal power. When you do so, each creature of your choice in a 30-foot Emanation originating from you must make a Wisdom saving throw (DC 8 plus your Strength modifier and Proficiency Bonus). On a failed save, a creature has the Frightened condition for 1 minute. At the end of each of the Frightened creature's turns, the creature repeats the save, ending the effect on itself on a success.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a use of your Rage (no action required) to restore your use of it."
        )
        return description
