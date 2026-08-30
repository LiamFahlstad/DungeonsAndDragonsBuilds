from Core.Definitions import MAX_ABILITY_MODIFIER, ROGUE_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType, RegainedOn, FeatureTarget
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class WailsFromTheGrave(Feature):
    def __init__(self):
        super().__init__(name="Wails from the Grave", origin="Phantom Rogue Level 3", activation=FeatureActivation(range="30 Feet"), usage_tags=["damage"], uses=FeatureUses(max_uses=MAX_ABILITY_MODIFIER, regain_all_on="long rest", current_formula="Current amount: equal to your Dexterity modifier."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Immediately after you deal Sneak Attack damage to a creature on your turn, you can target a second creature that you can see within 30 feet of the first creature. Roll half the number of Sneak Attack damage dice for your level (round up), and the second creature takes Necrotic damage equal to the roll's total as wails of the dead sound around it.\n"
            "You can use this feature a number of times based on your Dexterity modifier, and you regain all expended uses when you finish a Long Rest."
        )
        return description


    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
    def number_of_uses(self, character_stat_block: CharacterStatBlock) -> int:
        return max(1, character_stat_block.get_dexterity_modifier())
    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        uses = self.number_of_uses(character_stat_block)
        return [
            ("Trigger", "After you deal Sneak Attack damage on your turn"),
            ("Target", "Second creature within 30 feet of the first"),
            ("Damage", f"Necrotic: half your Sneak Attack damage dice (rounded up)"),
            ("Uses", f"{uses} uses (Dexterity modifier, minimum 1)"),
            ("Recharge", "Long Rest"),
        ]


class WhispersOfTheDead(Feature):
    def __init__(self):
        super().__init__(name="Whispers of the Dead", origin="Phantom Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you finish a Short or Long Rest, you can choose one skill or tool proficiency that you lack and gain it, as a ghostly presence shares its knowledge with you. You lose this proficiency when you use this benefit again to choose a different proficiency."
        return description


class TokensOfTheDeparted(Feature):
    def __init__(self):
        super().__init__(name="Tokens of the Departed", origin="Phantom Rogue Level 9", activation=FeatureActivation(range="30 Feet"), usage_tags=["buff", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The spirits of the dead are drawn to you, and echoes of their past lives magically manifest as strange curios with resonant power.\n"
            "You gain two soul trinkets. A soul trinket is a Tiny object (the DM determines the trinket's form or has you roll on the Trinkets table in the Player's Handbook to generate it). If you move more than 30 feet from a trinket, the trinket immediately teleports to you, appearing somewhere on your person.\n"
            "Using Soul Trinkets. You can use soul trinkets in the following ways:\n"
            "Death's Knell. When you deal Sneak Attack damage on your turn, you can destroy one soul trinket and immediately use Wails from the Grave without expending a use of that feature.\n"
            "Life Essence. While you have at least one soul trinket, you have Advantage on Death Saving Throws and Constitution saving throws.\n"
            "Spirit Query. You can take a Magic action to destroy one soul trinket and immediately cast the Augury spell, requiring no spell components and using Constitution as the spellcasting modifier. If you know the creature with which the trinket is associated, you can ask the creature's spirit one question instead of casting the spell. In this case, the spirit appears to you and answers as concisely as possible in a language it knew in life.\n"
            "Gaining Additional Soul Trinkets. When a creature you can see within 30 feet of you dies, you can take a Reaction to gain another soul trinket, claiming a sliver of that creature's departing spirit. The new trinket appears somewhere on your person.\n"
            "You can have a maximum of two soul trinkets at a time. If you try to gain a soul trinket while at your maximum, one of your existing trinkets is immediately destroyed and replaced by the new trinket. The maximum number of soul trinkets you can have increases when you reach Rogue levels 13 (three trinkets) and 17 (four trinkets).\n"
            "Whenever you finish a Long Rest with fewer than two soul trinkets, you gain soul trinkets until you have two."
        )
        return description


class VoiceOfDeath(Feature):
    def __init__(self):
        super().__init__(name="Voice of Death", origin="Phantom Rogue Level 9", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast Speak with Dead once without a spell slot, requiring no spell components and using Dexterity as the spellcasting modifier. You regain the ability to cast it this way when you finish a Short or Long Rest.\n"
            "When you cast the spell, you can target one of your soul trinkets from Tokens of the Departed instead of a corpse, allowing the spirit of the creature associated with the trinket to answer."
        )
        return description



    def regained_on(self, character_stat_block: CharacterStatBlock) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT
class GhostWalk(Feature):
    def __init__(self):
        super().__init__(name="Ghost Walk", origin="Phantom Rogue Level 13", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="10 Minutes"), usage_tags=["buff", "utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you assume a spectral form, gaining the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest unless you destroy one of your soul trinkets from Tokens of the Departed (no action required) to restore your use of it.\n"
            "Flight. You gain a Fly Speed of 10 feet and can hover.\n"
            "Hazy Form. Attack rolls have Disadvantage against you.\n"
            "Incorporeal Movement. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object."
        )
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DeathsFriend(Feature):
    def __init__(self):
        super().__init__(name="Death's Friend", origin="Phantom Rogue Level 17", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your association with death has become so close that you gain the following benefits.\n"
            "Death's Lament. When you use Wails from the Grave, you can deal the feature's Necrotic damage to both the first and the second creature.\n"
            "Draw of Death. When you roll Initiative, you gain one soul trinket for your Tokens of the Departed if you have none remaining."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Death's Lament", "Wails from the Grave deals damage to both first and second creature"),
            ("Draw of Death", "Gain one soul trinket on Initiative if you have none"),
        ]
