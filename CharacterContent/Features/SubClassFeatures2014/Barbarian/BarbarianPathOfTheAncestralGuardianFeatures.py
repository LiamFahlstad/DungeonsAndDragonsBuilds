import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType, FeatureTarget, RegainedOn
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


def _spirit_shield_dice(barbarian_level: int) -> str:
    if barbarian_level >= 14:
        return "4d6"
    if barbarian_level >= 10:
        return "3d6"
    return "2d6"


class AncestralProtectors(Feature):
    def __init__(self):
        super().__init__(name="Ancestral Protectors", origin="Path Of The Ancestral Guardian Barbarian Level 3", activation=FeatureActivation(duration="Until the Start of Your Next Turn"), usage_tags=["control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting when you choose this path at 3rd level, spectral warriors appear when you enter your rage. While you're raging, the first creature you hit with an attack on your turn becomes the target of the warriors, which hinder its attacks. Until the start of your next turn, that target has disadvantage on any attack roll that isn't against you, and when the target hits a creature other than you with an attack, that creature has resistance to the damage dealt by the attack. The effect on the target ends early if your rage ends."
        )
        return description

    def get_concise_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "When you rage, spectral warriors target the first creature you hit each turn. That target has disadvantage on attacks not against you; creatures it hits gain resistance to the damage dealt."
        )

    def target(
        self, character_stat_block: CharacterStatBlock
    ) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SpiritShield(Feature):
    def __init__(self):
        super().__init__(name="Spirit Shield", origin="Path Of The Ancestral Guardian Barbarian Level 6", activation=FeatureActivation(action_type=ActionType.REACTION, duration="Ends When Your Rage Ends", range="30 Feet"), usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Beginning at 6th level, the guardian spirits that aid you can provide supernatural protection to those you defend. If you are raging and another creature you can see within 30 feet of you takes damage, you can use your reaction to reduce that damage by 2d6.\n"
            "\n"
            "When you reach certain levels in this class, you can reduce the damage by more: by 3d6 at 10th level and by 4d6 at 14th level."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        barbarian_level = character_stat_block.get_class_level(Definitions.CharacterClass.BARBARIAN)
        dice = _spirit_shield_dice(barbarian_level)
        return [
            ("When", "You're raging; another creature within 30 feet takes damage"),
            ("Action", "Reaction"),
            ("Effect", f"Reduce that damage by {dice}"),
            ("Duration", "Ends when your rage ends"),
        ]

    def target(
        self, character_stat_block: CharacterStatBlock
    ) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ConsultTheSpirits(Feature):
    def __init__(self):
        super().__init__(name="Consult the Spirits", origin="Path Of The Ancestral Guardian Barbarian Level 10", usage_tags=["utility"], uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 10th level, you gain the ability to consult with your ancestral spirits. When you do so, you cast the Augury or Clairvoyance spell, without using a spell slot or material components. Rather than creating a spherical sensor, this use of clairvoyance invisibly summons one of your ancestral spirits to the chosen location. Wisdom is your spellcasting ability for these spells.\n"
            "\n"
            "After you cast either spell in this way, you can't use this feature again until you finish a short or long rest."
        )
        return description

    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST