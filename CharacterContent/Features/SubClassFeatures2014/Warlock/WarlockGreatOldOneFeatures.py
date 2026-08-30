from CharacterContent.Features.Core.BaseFeatures import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from CharacterContent.Features.Core.Improvements import DamageResistance
from Core.Definitions import DamageType
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class GreatOldOneExpandedSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List",
            origin="The Great Old One Patron Warlock Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Great Old One lets you choose from an expanded list of spells when you learn a Warlock spell. The following spells are added to the Warlock spell list for you.\n"
            "Great Old One Expanded Spells\n"
            "Spell Level\tSpells\n"
            "1st\tDissonant Whispers, Tasha's Hideous Laughter\n"
            "2nd\tDetect Thoughts, Phantasmal Force\n"
            "3rd\tClairvoyance, Sending\n"
            "4th\tDominate Beast, Evard's Black Tentacles\n"
            "5th\tDominate Person, Telekinesis"
        )
        return description


class AwakenedMind(Feature):
    def __init__(self):
        super().__init__(
            name="Awakened Mind",
            origin="The Great Old One Patron Warlock Level 3",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["utility"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your alien knowledge gives you the ability to touch the minds of other creatures. You can telepathically speak to any creature you can see within 30 feet of yourself. You don't need to share a language with the creature for it to understand your telepathic utterances, but the creature must be able to understand at least one language."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class EntropicWard(Feature):
    def __init__(self):
        super().__init__(
            name="Entropic Ward",
            origin="The Great Old One Patron Warlock Level 6",
            activation=FeatureActivation(action_type=ActionType.REACTION, duration="Until End of Next Turn"),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn to magically ward yourself against attack and to turn an enemy's failed strike into good luck for yourself. When a creature makes an attack roll against you, you can use your Reaction to impose Disadvantage on that roll. If the attack misses you, your next attack roll against the creature has Advantage if you make it before the end of your next turn.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Creature makes attack roll against you"),
            ("Type", "Reaction"),
            ("Effect", "Impose Disadvantage on the roll"),
            (
                "Bonus",
                "If misses, your next attack on it has Advantage (by end of next turn)",
            ),
            ("Recharge", "Short or long rest"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class ThoughtShield(Feature):
    def __init__(self):
        super().__init__(
            name="Thought Shield",
            origin="The Great Old One Patron Warlock Level 10",
            usage_tags=["buff"],
        )
        self._resistance = DamageResistance(DamageType.PSYCHIC, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._resistance.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your thoughts can't be read by telepathy or other means unless you allow it. You also have Resistance to Psychic damage, and whenever a creature deals Psychic damage to you, that creature takes the same amount of damage that you do."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class CreateThrall(Feature):
    def __init__(self):
        super().__init__(
            name="Create Thrall",
            origin="The Great Old One Patron Warlock Level 14",
            activation=FeatureActivation(action_type=ActionType.ACTION, duration="Until Remove Curse or Charmed Removed", range="Touch"),
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to infect a Humanoid's mind with the alien magic of your patron. You can use your action to touch an Incapacitated Humanoid. That creature is then charmed by you until a Remove Curse spell is cast on it, the Charmed condition is removed from it, or you use this feature again.\n"
            "You can communicate telepathically with the charmed creature as long as the two of you are on the same plane of existence."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action to touch Incapacitated Humanoid"),
            ("Effect", "Charm target"),
            ("Duration", "Until Remove Curse, Charmed removed, or feature used again"),
            ("Bonus", "Telepathic communication on same plane"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
