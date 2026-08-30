from Core.Definitions import CLERIC_HIT_DIE, MAX_ABILITY_MODIFIER
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class LightDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Light Domain Spells", origin="Light Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Light Domain Spells table, you thereafter always have the listed spells prepared."
        return description


class RadianceOfTheDawn(Feature):
    def __init__(self):
        super().__init__(
            name="Radiance of the Dawn", origin="Light Domain Cleric Level 3", activation=FeatureActivation(action_type=ActionType.ACTION, range="30-Foot Emanation"), usage_tags=["damage"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "As a Magic action, you present your Holy Symbol and expend a use of your Channel Divinity to emit a flash of light in a 30-foot Emanation originating from yourself. Any magical Darkness—such as that created by the Darkness spell—in that area is dispelled. Additionally, each creature of your choice in that area must make a Constitution saving throw, taking Radiant damage equal to 2d10 plus your Cleric level on a failed save or half as much damage on a successful one."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("What", "Emit flash of light"),
            ("Trigger", "Magic action, Holy Symbol, Channel Divinity"),
            ("Area", "30-foot Emanation from yourself"),
            ("Effect 1", "Dispel magical Darkness"),
            ("Effect 2", "Constitution save; 2d10 + Cleric level Radiant damage on fail (half on success)"),
        ]


class WardingFlare(Feature):
    def __init__(self):
        super().__init__(name="Warding Flare", origin="Light Domain Cleric Level 3", activation=FeatureActivation(action_type=ActionType.REACTION, range="30 Feet"), usage_tags=["control"], uses=FeatureUses(max_uses=MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Wisdom modifier."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When a creature that you can see within 30 feet of yourself makes an attack roll, you can take a Reaction to impose Disadvantage on the attack roll, causing light to flare before it hits or misses.\n"
            "You can use this feature a number of times based on your Wisdom modifier. You regain all expended uses when you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wisdom_modifier = character_stat_block.get_wisdom_modifier()
        uses = max(1, wisdom_modifier)
        return [
            ("What", "Impose Disadvantage on attack roll"),
            ("Trigger", "Reaction when creature within 30 feet attacks"),
            ("Effect", "Disadvantage on the triggering attack"),
            ("Uses", f"{uses} (Wisdom modifier, minimum 1)"),
            ("Recharge", "Long Rest"),
        ]


class ImprovedWardingFlare(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Warding Flare", origin="Light Domain Cleric Level 6", usage_tags=["heal"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You regain all expended uses of your Warding Flare when you finish a Short or Long Rest.\n"
            "In addition, whenever you use Warding Flare, you can give the target of the triggering attack a number of Temporary Hit Points equal to 2d6 plus your Wisdom modifier."
        )
        return description


class CoronaOfLight(Feature):
    def __init__(self):
        super().__init__(name="Corona of Light", origin="Light Domain Cleric Level 17", activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Minute", range="60-Foot Radius"), usage_tags=["control"], uses=FeatureUses(max_uses=MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Wisdom modifier."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you cause yourself to emit an aura of sunlight that lasts for 1 minute or until you dismiss it (no action required). You emit Bright Light in a 60-foot radius and Dim Light for an additional 30 feet. Your enemies in the Bright Light have Disadvantage on saving throws against your Radiance of the Dawn and any spell that deals Fire or Radiant damage.\n"
            "You can use this feature a number of times based on your Wisdom modifier, and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wisdom_modifier = character_stat_block.get_wisdom_modifier()
        uses = max(1, wisdom_modifier)
        return [
            ("What", "Emit aura of sunlight"),
            ("Trigger", "Magic action"),
            ("Duration", "1 minute or dismiss (no action)"),
            ("Light", "60-foot Bright Light, +30 feet Dim Light"),
            ("Effect", "Enemies in Bright Light have Disadvantage on saves vs Radiance/Fire/Radiant"),
            ("Uses", f"{uses} (Wisdom modifier, minimum 1)"),
            ("Recharge", "Long Rest"),
        ]
