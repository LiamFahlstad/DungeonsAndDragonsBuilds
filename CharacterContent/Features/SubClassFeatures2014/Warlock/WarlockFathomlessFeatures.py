import Core.Definitions as Definitions
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureUses,
    FeatureTarget,
    FeatureDice,
)
from Model.Content.Improvements import DamageResistance
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_PROFICIENCY_BONUS, levels_gained, proficiency_bonus
from Model.View import CharacterView
from Core.Definitions import CharacterClass
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class ExpandedSpellList(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List", origin="The Fathomless Patron Warlock Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "These spells are added to the Warlock spell list for you when you learn a Warlock spell."
            ),
            Table(
                ("Spell level", "Spells"),
                (
                    ("1", "Create or Destroy Water, Thunderwave"),
                    ("2", "Gust of Wind, Silence"),
                    ("3", "Lightning Bolt, Sleet Storm"),
                    ("4", "Control Water, Summon Elemental (Water only)"),
                    ("5", "Bigby's Hand (appears as a tentacle), Cone of Cold"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The Fathomless lets you choose from an expanded list of spells when you learn a Warlock spell. The following spells are added to the Warlock spell list for you.\n"
            "Fathomless Expanded Spells\n"
            "Spell Level\tSpells\n"
            "1st\tCreate or Destroy Water, Thunderwave\n"
            "2nd\tGust of Wind, Silence\n"
            "3rd\tLightning Bolt, Sleet Storm\n"
            "4th\tControl Water, Summon Elemental (Water only)\n"
            "5th\tBigby's Hand (appears as a tentacle), Cone of Cold"
        )
        return description


TENTACLE_DICE = FeatureDice(
    "Tentacle Cold Damage",
    (
        (3, "1d8"),
        (10, "2d8"),
    ),
    CharacterClass.WARLOCK,
)


class TentacleOfTheDeep(Feature):
    def __init__(self):
        super().__init__(
            name="Tentacle of the Deep",
            origin="The Fathomless Patron Warlock Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="1 Minute or Until Another Tentacle Created",
                range="60 Feet",
            ),
            usage_tags=["damage", "control", "summon"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=levels_gained(proficiency_bonus, from_level=3),
            ),
            dice=TENTACLE_DICE,
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses and the tentacle's damage dice are in the panel below.
        return [
            Paragraph("Summon a spectral tentacle that strikes at your foes."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Range",
                        "A point you can see within 60 feet; the tentacle is 10 feet long",
                    ),
                    ("Duration", "1 minute, or until you create another"),
                    (
                        "Attack",
                        "When you create it: a melee spell attack against one creature within 10 feet of it",
                    ),
                    (
                        "Hit",
                        "Tentacle Cold Damage dice (see Dice below) cold damage, and its speed drops by 10 feet until the start of your next turn",
                    ),
                    (
                        "Again",
                        "Bonus Action on your turn: move it up to 30 feet and repeat the attack",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        damage = TENTACLE_DICE.at(character)
        description = (
            "You can magically summon a spectral tentacle that strikes at your foes. As a bonus action, you create a 10-foot-long tentacle at a point you can see within 60 feet of you. The tentacle lasts for 1 minute or until you use this feature to create another tentacle.\n"
            "\n"
            f"When you create the tentacle, you can make a melee spell attack against one creature within 10 feet of it. On a hit, the target takes 1d8 cold damage, and its speed is reduced by 10 feet until the start of your next turn. When you reach 10th level in this class, the damage increases to 2d8.\n"
            "\n"
            "As a bonus action on your turn, you can move the tentacle up to 30 feet and repeat the attack.\n"
            "\n"
            "You can summon the tentacle a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest.\n"
            f"Your tentacle right now: {self._spell_attack(character):+} to hit, {damage} cold damage."
        )
        return description

    @staticmethod
    def _spell_attack(character: CharacterView) -> int:
        return character.calculate_attack_bonus_for_ability(
            Definitions.Ability.CHARISMA
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()


class GiftOfTheSea(Feature):
    def __init__(self):
        super().__init__(
            name="Gift of the Sea",
            origin="The Fathomless Patron Warlock Level 3",
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Swim Speed", "40 feet"),
                    ("Breathing", "You can breathe underwater"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain a swimming speed of 40 feet, and you can breathe underwater."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class OceanicSoul(Feature):
    def __init__(self):
        super().__init__(
            name="Oceanic Soul",
            origin="The Fathomless Patron Warlock Level 6",
            usage_tags=["buff", "utility"],
        )
        # "You gain resistance to cold damage."
        self._resistance = DamageResistance(Definitions.DamageType.COLD)

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You are now even more at home in the depths."),
            Facts(
                (
                    ("Resistance", "Cold damage"),
                    (
                        "Underwater speech",
                        "While you're fully submerged, any fully submerged creature can understand your speech, and you can understand theirs",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You are now even more at home in the depths. You gain resistance to cold damage. In addition, when you are fully submerged, any creature that is also fully submerged can understand your speech, and you can understand theirs."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


GUARDIAN_COIL_DICE = FeatureDice(
    "Damage Reduction",
    (
        (6, "1d8"),
        (10, "2d8"),
    ),
    CharacterClass.WARLOCK,
)


class GuardianCoil(Feature):
    def __init__(self):
        super().__init__(
            name="Guardian Coil",
            origin="The Fathomless Patron Warlock Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="10 Feet"
            ),
            usage_tags=["buff"],
            dice=GUARDIAN_COIL_DICE,
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The damage reduction die by Warlock level is in the panel below.
        return [
            Paragraph(
                "Your Tentacle of the Deep interposes itself between you or others and harm."
            ),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "You or a creature you can see takes damage while within 10 feet of the tentacle",
                    ),
                    (
                        "Effect",
                        "Reduce the damage to one of those creatures by your Guardian Coil die (below)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your Tentacle of the Deep can defend you and others, interposing itself between them and harm. When you or a creature you can see takes damage while within 10 feet of the tentacle, you can use your reaction to choose one of those creatures and reduce the damage to that creature by 1d8. When you reach 10th level in this class, the damage reduced by the tentacle increases to 2d8."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class GraspingTentacles(Feature):
    def __init__(self):
        super().__init__(
            name="Grasping Tentacles",
            origin="The Fathomless Patron Warlock Level 10",
            usage_tags=["heal"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest free casting is in the panel below.
        return [
            Facts(
                (
                    (
                        "Spell",
                        "Evard's Black Tentacles; a Warlock spell for you that doesn't count against your spells known",
                    ),
                    ("Free casting", "Cast it once without a spell slot"),
                    (
                        "Temporary HP",
                        "Equal to your Warlock level, whenever you cast it",
                    ),
                    ("Concentration", "Damage can't break your Concentration on it"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn the spell Evard's Black Tentacles. It counts as a Warlock spell for you, but it doesn't count against the number of spells you know. You can also cast it once without using a spell slot, and you regain the ability to do so when you finish a long rest.\n"
            "\n"
            "Whenever you cast this spell, your patron's magic bolsters you, granting you a number of temporary hit points equal to your Warlock level. Moreover, damage can't break your concentration on this spell."
        )
        return description


class FathomlessPlunge(Feature):
    def __init__(self):
        super().__init__(
            name="Fathomless Plunge",
            origin="The Fathomless Patron Warlock Level 14",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="30 Feet"
            ),
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Action", "Action"),
                    (
                        "Target",
                        "You and up to five willing creatures you can see within 30 feet",
                    ),
                    (
                        "Destination",
                        "Up to 1 mile away, in or within 30 feet of a body of water you've seen (pond size or larger); everyone appears within 30 feet of each other",
                    ),
                    ("Limit", "Once per short or long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can magically open temporary conduits to watery destinations. As an action, you can teleport yourself and up to five other willing creatures that you can see within 30 feet of you. Amid a whirl of tentacles, you all vanish and then reappear up to 1 mile away in a body of water you've seen (pond size or larger) or within 30 feet of it, each of you appearing in an unoccupied space within 30 feet of the others.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
