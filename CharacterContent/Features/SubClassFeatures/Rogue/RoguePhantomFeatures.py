from Core.Definitions import ROGUE_HIT_DIE
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Utils import StringUtils
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class WailsFromTheGrave(Feature):
    def __init__(self):
        super().__init__(
            name="Wails from the Grave",
            origin="Phantom Rogue Level 3",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["damage"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Dexterity modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "Right after you deal Sneak Attack damage to a creature on your turn",
                    ),
                    (
                        "Target",
                        "A second creature you can see within 30 feet of the first",
                    ),
                    (
                        "Damage",
                        "Roll half your Sneak Attack dice (round up): Necrotic damage",
                    ),
                    ("Uses", "Dexterity modifier (minimum once) per Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Immediately after you deal Sneak Attack damage to a creature on your turn, you can target a second creature that you can see within 30 feet of the first creature. Roll half the number of Sneak Attack damage dice for your level (round up), and the second creature takes Necrotic damage equal to the roll's total as wails of the dead sound around it.\n"
            "You can use this feature a number of times equal to your Dexterity modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_dexterity_modifier())


class WhispersOfTheDead(Feature):
    def __init__(self):
        super().__init__(name="Whispers of the Dead", origin="Phantom Rogue Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("When", "You finish a Short or Long Rest"),
                    (
                        "Effect",
                        "Gain one skill or tool proficiency you lack, shared by a ghostly presence",
                    ),
                    (
                        "Duration",
                        "Until you use this benefit again to choose a different proficiency",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Whenever you finish a Short or Long Rest, you can choose one skill or tool proficiency that you lack and gain it, as a ghostly presence shares its knowledge with you. You lose this proficiency when you use this benefit again to choose a different proficiency."
        return description


class TokensOfTheDeparted(Feature):
    def __init__(self):
        super().__init__(
            name="Tokens of the Departed",
            origin="Phantom Rogue Level 9",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Spirits of the dead leave you soul trinkets with resonant power."
            ),
            Facts(
                (
                    (
                        "Trinkets",
                        "You gain two soul trinkets: Tiny objects whose form the DM picks or has you roll on the Player's Handbook Trinkets table. Finish a Long Rest with fewer than two and you gain trinkets until you have two.",
                    ),
                    (
                        "Maximum",
                        "2; 3 from Rogue level 13; 4 from level 17. Gaining one at the maximum destroys and replaces an old one.",
                    ),
                    (
                        "Gain more",
                        "Reaction when a creature you can see within 30 feet of you dies; the trinket appears on your person",
                    ),
                    (
                        "Distance",
                        "A trinket more than 30 feet from you teleports back to your person",
                    ),
                )
            ),
            Option(
                "Using trinkets",
                (
                    Facts(
                        (
                            (
                                "Life Essence",
                                "While you have at least one: Advantage on Death Saving Throws and Constitution saving throws",
                            ),
                            (
                                "Death's Knell",
                                "When you deal Sneak Attack damage on your turn, destroy one to use Wails from the Grave without expending a use",
                            ),
                            (
                                "Spirit Query",
                                "Magic action: destroy one to cast Augury with no components, using Constitution as the spellcasting modifier. If you know the creature the trinket came from, ask its spirit one question instead; it appears and answers as concisely as it can, in a language it knew in life.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
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
        super().__init__(
            name="Voice of Death",
            origin="Phantom Rogue Level 9",
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Free casting",
                        "Cast Speak with Dead once without a spell slot or components; regain this when you finish a Short or Long Rest",
                    ),
                    ("Spellcasting modifier", "Dexterity"),
                    (
                        "Soul trinket",
                        "Target one of your Tokens of the Departed instead of a corpse; the spirit of the creature tied to it answers",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can cast Speak with Dead once without a spell slot, requiring no spell components and using Dexterity as the spellcasting modifier. You regain the ability to cast it this way when you finish a Short or Long Rest.\n"
            "When you cast the spell, you can target one of your soul trinkets from Tokens of the Departed instead of a corpse, allowing the spirit of the creature associated with the trinket to answer."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


class GhostWalk(Feature):
    def __init__(self):
        super().__init__(
            name="Ghost Walk",
            origin="Phantom Rogue Level 13",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="10 Minutes"
            ),
            usage_tags=["buff", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Assume a spectral form."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Duration",
                        "10 minutes, or until you end it (no action required)",
                    ),
                    (
                        "Recharge",
                        "Once per Long Rest, or destroy one of your soul trinkets (no action required) to restore it",
                    ),
                    ("Flight", "Fly Speed 10 feet, and you can hover"),
                    ("Hazy Form", "Attack rolls against you have Disadvantage"),
                    (
                        "Incorporeal Movement",
                        "Move through creatures and objects as Difficult Terrain; take 1d10 Force damage if you end your turn inside one",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you assume a spectral form, gaining the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest unless you destroy one of your soul trinkets from Tokens of the Departed (no action required) to restore your use of it.\n"
            "Flight. You gain a Fly Speed of 10 feet and can hover.\n"
            "Hazy Form. Attack rolls have Disadvantage against you.\n"
            "Incorporeal Movement. You can move through creatures and objects as if they were Difficult Terrain, but you take 1d10 Force damage if you end your turn inside a creature or an object."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DeathsFriend(Feature):
    def __init__(self):
        super().__init__(
            name="Death's Friend",
            origin="Phantom Rogue Level 17",
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Death's Lament",
                        "When you use Wails from the Grave, deal its Necrotic damage to both the first and the second creature",
                    ),
                    (
                        "Draw of Death",
                        "When you roll Initiative with no soul trinkets left, gain one for your Tokens of the Departed",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your association with death has become so close that you gain the following benefits.\n"
            "Death's Lament. When you use Wails from the Grave, you can deal the feature's Necrotic damage to both the first and the second creature.\n"
            "Draw of Death. When you roll Initiative, you gain one soul trinket for your Tokens of the Departed if you have none remaining."
        )
        return description
