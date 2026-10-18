from Core.Definitions import SORCERER_HIT_DIE
from Model.Content.Feature import Feature, FeatureActivation, FeatureTarget, FeatureUses
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table


class SpellfireSpells(Feature):
    def __init__(self):
        super().__init__(name="Spellfire Spells", origin="Spellfire Sorcerer Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Sorcerer level shown, you always have these spells prepared."
            ),
            Table(
                ("Sorcerer level", "Spells"),
                (
                    (
                        "3",
                        "Cure Wounds, Guiding Bolt, Lesser Restoration, Scorching Ray",
                    ),
                    ("5", "Aura of Vitality, Dispel Magic"),
                    ("7", "Fire Shield, Wall of Fire"),
                    ("9", "Flame Strike, Greater Restoration"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Spellfire Spells table, you thereafter always have the listed spells prepared.\n"
            "Spellfire Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Cure Wounds, Guiding Bolt, Lesser Restoration, Scorching Ray\n"
            "5	Aura of Vitality, Dispel Magic\n"
            "7	Fire Shield, Wall of Fire\n"
            "9	Greater Restoration, Flame Strike"
        )
        return description


class SpellfireBurst(Feature):
    def __init__(self):
        super().__init__(
            name="Spellfire Burst",
            origin="Spellfire Sorcerer Level 3",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["heal", "damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You spend at least 1 Sorcery Point as part of a Magic action or a Bonus Action on your turn",
                    ),
                    ("Limit", "Once per turn"),
                )
            ),
            Option(
                "Bolstering Flames",
                (
                    Facts(
                        (
                            (
                                "Target",
                                "You or one creature you can see within 30 feet",
                            ),
                            (
                                "Effect",
                                "1d4 + Charisma modifier Temporary Hit Points (+ Sorcerer level from level 14, Honed Spellfire)",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Radiant Fire",
                (
                    Facts(
                        (
                            ("Target", "One creature you can see within 30 feet"),
                            (
                                "Damage",
                                "1d4 Fire or Radiant damage, your choice (1d8 from Sorcerer level 14, Honed Spellfire)",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you spend at least 1 Sorcery Point as part of a Magic action or a Bonus Action on your turn, you can unleash one of the following magical effects of your choice. You can do so only once per turn.\n"
            "Bolstering Flames. You or one creature you can see within 30 feet of yourself gains Temporary Hit Points equal to 1d4 plus your Charisma modifier.\n"
            "Radiant Fire. One creature you can see within 30 feet of yourself takes 1d4 Fire or Radiant damage (your choice)."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class AbsorbSpells(Feature):
    def __init__(self):
        super().__init__(name="Absorb Spells", origin="Spellfire Sorcerer Level 6")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Always prepared", "Counterspell"),
                    (
                        "Absorb",
                        "When a target fails its save against your Counterspell, regain 1d4 Sorcery Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You always have Counterspell prepared.\n"
            "Additionally, whenever a target fails the saving throw against a Counterspell you cast, you regain 1d4 Sorcery Points."
        )
        return description


class HonedSpellfire(Feature):
    def __init__(self):
        super().__init__(name="Honed Spellfire", origin="Spellfire Sorcerer Level 14")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your Spellfire Burst improves."),
            Facts(
                (
                    (
                        "Bolstering Flames",
                        "Add your Sorcerer level to the Temporary Hit Points",
                    ),
                    ("Radiant Fire", "Damage increases to 1d8"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your Spellfire Burst improves. You add your Sorcerer level to the Temporary Hit Points gained from Bolstering Flames, and the damage of your Radiant Fire increases to 1d8."
        return description


class CrownOfSpellfire(Feature):
    def __init__(self):
        super().__init__(
            name="Crown of Spellfire",
            origin="Spellfire Sorcerer Level 18",
            usage_tags=["buff", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Infuse an Innate Sorcery with spellfire."),
            Facts(
                (
                    ("Trigger", "When you use Innate Sorcery; lasts while it's active"),
                    (
                        "Limit",
                        "Once per Long Rest; spend 5 Sorcery Points (no action required) to use it again",
                    ),
                )
            ),
            Option(
                "While active",
                (
                    Facts(
                        (
                            (
                                "Burning Life Force",
                                "Once per turn when an attack roll hits you, expend up to your Charisma modifier (minimum 1) Hit Point Dice and reduce the damage by their total",
                            ),
                            ("Flight", "Fly Speed of 60 feet, and you can hover"),
                            (
                                "Spell Avoidance",
                                "Against a spell or magical effect whose save halves the damage: no damage on a success, half on a failure (not while Incapacitated)",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use Innate Sorcery, you can alter it and infuse yourself with the essence of spellfire, gaining the following benefits while this use of Innate Sorcery is active. Once you use this feature to alter Innate Sorcery, you can’t use it again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it.\n"
            "Burning Life Force. Once per turn when you are hit by an attack roll, you can expend a number of Hit Point Dice, up to a maximum equal to your Charisma modifier (minimum of one). Roll the expended dice, and reduce the amount of damage from that attack equal to the total rolled.\n"
            "Flight. You gain a Fly Speed of 60 feet and can hover.\n"
            "Spell Avoidance. When you’re subjected to a spell or magical effect that allows you to make a saving throw to take only half damage, you instead take no damage if you succeed on the save and only half damage if you fail. You can’t use this benefit if you have the Incapacitated condition."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF
