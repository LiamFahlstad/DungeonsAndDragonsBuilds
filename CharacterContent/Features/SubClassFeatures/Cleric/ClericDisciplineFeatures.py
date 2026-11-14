from Core.Definitions import Ability, DamageType
from Model.Content.CombatEffect import CombatDamage, CombatEffect, EffectRoll
from Model.Content.Feature import (
    Feature,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class DisciplineDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Discipline Domain Spells", origin="Discipline Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The spells ClericDiscipline.py grants at each Cleric level.
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    (
                        "3",
                        "Arcane Vigor, Guiding Bolt, Magic Weapon, Shield of Faith",
                    ),
                    ("5", "Prayer of Mending, Protection from Energy"),
                    ("7", "Guardian of Faith, Stoneskin"),
                    ("9", "Circle of Power, Destructive Wave"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Discipline Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Cleric Level\tSpells\n"
            "3\tArcane Vigor, Guiding Bolt, Magic Weapon, Shield of Faith\n"
            "5\tPrayer of Mending, Protection from Energy\n"
            "7\tGuardian of Faith, Stoneskin\n"
            "9\tCircle of Power, Destructive Wave"
        )
        return description


class HolyBolt(Feature):
    def __init__(self):
        super().__init__(
            name="Holy Bolt",
            origin="Discipline Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="60 Feet"
            ),
            usage_tags=["damage", "heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Use Channel Divinity to hurl a bolt of holy energy."),
            Facts(
                (
                    ("Cost", "One use of Channel Divinity"),
                    ("Action", "Bonus Action, presenting your Holy Symbol"),
                    (
                        "Attack",
                        "Ranged spell attack against one creature within 60 feet",
                    ),
                    ("Hit", "2d10 + Wisdom modifier Radiant damage"),
                    (
                        "Healing",
                        "On a hit, a creature you can see within 60 feet regains 1d10 + Wisdom modifier Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "As a Bonus Action, you present your Holy Symbol and expend a use of your Channel Divinity to make a ranged spell attack, hurling a bolt of holy energy targeting one creature within 60 feet of yourself. On a hit, the target takes Radiant damage equal to 2d10 plus your Wisdom modifier, and you can choose a creature you can see within 60 feet of yourself to regain Hit Points equal to 1d10 plus your Wisdom modifier."
        return description

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # A use of Channel Divinity, which it's granted as an extension of.
        wisdom = character.get_wisdom_modifier()
        return [
            CombatEffect(
                roll=EffectRoll.ATTACK,
                action_type=ActionType.BONUS_ACTION,
                damage=(CombatDamage(f"2d10 + {wisdom}", DamageType.RADIANT),),
                notes=(
                    "On a hit, a creature you can see within 60 feet of you"
                    f" regains 1d10 + {wisdom} Hit Points.",
                ),
            )
        ]

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Atonement(Feature):
    def __init__(self):
        super().__init__(
            name="Atonement",
            origin="Discipline Domain Cleric Level 3",
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your healing blesses allies, and your damage heals them."),
            Facts(
                (
                    (
                        "Blessing",
                        "When a level 1+ spell you cast restores Hit Points, each creature it heals is blessed until the end of your next turn",
                    ),
                    (
                        "Healing",
                        "Whenever you cast a damaging spell with a spell slot, each blessed creature regains Hit Points equal to that slot's level",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When a level 1+ spell you cast restores Hit Points to one or more creatures, each of those creatures gains a blessing that lasts until the end of your next turn. Whenever you cast a spell that deals damage to a creature using a spell slot, each blessed creature regains additional Hit Points equal to the level of the spell slot you used to cast the damaging spell."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class LuminousBarrier(Feature):
    def __init__(self):
        super().__init__(
            name="Luminous Barrier",
            origin="Discipline Domain Cleric Level 6",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["heal", "buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Use Channel Divinity to ward the creatures your Atonement blessed."
            ),
            Facts(
                (
                    ("Cost", "One use of Channel Divinity"),
                    ("Action", "Bonus Action"),
                    ("Target", "Each creature blessed by your Atonement"),
                    ("Temporary HP", "Cleric level + Wisdom modifier"),
                    (
                        "Resistance",
                        "All damage, while it has Temporary Hit Points from this feature",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "As a Bonus Action, you can expend a use of your Channel Divinity to place a magical ward of glowing light on each creature blessed by your Atonement. Each affected creature gains a number of Temporary Hit Points equal to your Cleric level plus your Wisdom modifier. While a creature has Temporary Hit Points gained from this feature, it has Resistance to all damage."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class UltimatePenitence(Feature):
    def __init__(self):
        super().__init__(
            name="Ultimate Penitence",
            origin="Discipline Domain Cleric Level 17",
            usage_tags=["damage", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your Holy Bolt grows more powerful."),
            Facts(
                (
                    (
                        "Ascending Step",
                        "When you use Holy Bolt, you can teleport to an unoccupied space you can see within 30 feet before you make an attack roll",
                    ),
                    (
                        "Ascending Volley",
                        "When you use Holy Bolt, you can expend a spell slot as part of the Bonus Action to hurl one additional bolt per slot level, at one creature or several; roll each attack separately",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Holy Bolt grows more powerful as detailed below.\n"
            "Ascending Step. When you use Holy Bolt, you can teleport to an unoccupied space you can see within 30 feet before you make an attack roll.\n"
            "Ascending Volley. When you use Holy Bolt, you can expend a spell slot as part of the Bonus Action to hurl a number of additional bolts equal to the spell slot level expended. You can direct the bolts to hit one creature or several. Make a separate attack roll for each bolt."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
