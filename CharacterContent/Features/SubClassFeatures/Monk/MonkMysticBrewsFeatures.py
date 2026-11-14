from CharacterContent.Features.ClassFeatures.ClassProficiencies import (
    CLASS_SKILL_CHOICES,
)
from CharacterContent.Features.ClassFeatures.Monk.MonkFeatures import MARTIAL_ARTS_DIE
from CharacterContent.ToolProficiencies.Proficiencies import BrewersSupplies
from Core.Definitions import Ability, CharacterClass, DamageType, Skill
from Model.Content.CombatEffect import (
    CombatCondition,
    CombatDamage,
    CombatEffect,
    EffectRoll,
    TurnEdge,
    TurnOf,
)
from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Model.Content.Improvements import GrantToolProficiency, SkillProficiencyChoice
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, dc_formula


class BonusProficiencies(Feature):
    SKILL_POOL = [Skill.PERFORMANCE] + [
        skill
        for skill in CLASS_SKILL_CHOICES[CharacterClass.MONK][0]
        if skill != Skill.PERFORMANCE
    ]

    def __init__(self, skill: Skill = Skill.PERFORMANCE):
        """`skill` is Performance, or a Monk skill if you already have
        Performance."""
        super().__init__(
            name="Bonus Proficiencies",
            origin="Warrior of Mystic Brews Monk Level 3",
            passive=True,
        )
        self._skill = skill
        self._skill_proficiency = SkillProficiencyChoice(
            [skill], self.SKILL_POOL, count=1, error_prefix="Bonus Proficiencies"
        )
        self._tool_proficiency = GrantToolProficiency([BrewersSupplies()])

    def apply(self, ledger_writer: LedgerWriter):
        self._skill_proficiency.apply(ledger_writer)
        self._tool_proficiency.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        skill = f"Proficiency in {self._skill.value}"
        if self._skill != Skill.PERFORMANCE:
            skill += " (a Monk skill in place of Performance, which you already had)"
        return [
            Facts(
                (
                    ("Skill", skill),
                    ("Tool", "Brewer's Supplies, if you don't already have it"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain proficiency in the Performance skill, or if you already have it, you gain proficiency in one skill of your choice from the skills available to Monks at level 1. You also gain proficiency with Brewer's Supplies if you don't already have it.\n"
            f"You gained {self._skill.value}."
        )
        return description


class DrunkenTechnique(Feature):
    def __init__(self):
        super().__init__(
            name="Drunken Technique",
            origin="Warrior of Mystic Brews Monk Level 3",
            activation=FeatureActivation(duration="Until End of Current Turn"),
            usage_tags=["buff", "damage"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You twist and turn quickly as you move."),
            Facts(
                (
                    ("Trigger", "You expend a Focus Point on Patient Defense"),
                    ("Speed", "+10 feet until the end of the current turn"),
                    (
                        "Strike",
                        "Make one Unarmed Strike immediately after the Bonus Action",
                    ),
                    (
                        "From Monk level 17",
                        "You can also move up to your Speed and strike creatures you pass (Intoxicated Frenzy)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You twist and turn quickly as you move. Whenever you expend a Focus Point using Patient Defense, your Speed increases by 10 feet until the end of the current turn, and you can make one Unarmed Strike immediately after the Bonus Action."
        return description


class TipsySway(Feature):
    def __init__(self):
        super().__init__(
            name="Tipsy Sway",
            origin="Warrior of Mystic Brews Monk Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="5 Feet"
            ),
            usage_tags=["control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("You can move in sudden, swaying ways."),
            Option(
                "Leap to Your Feet",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "When you have the Prone condition, stand up by spending 5 feet of movement",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Redirect Attack",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            ("Cost", "1 Focus Point"),
                            ("Trigger", "An enemy misses you with a melee attack roll"),
                            (
                                "Effect",
                                "The attack hits one creature of your choice, other than the attacker, that you can see within 5 feet of yourself",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can move in sudden, swaying ways. You gain the following benefits.\n"
            "    * Leap to Your Feet. When you have the Prone condition, you can stand up by spending 5 feet of movement.\n"
            "    * Redirect Attack. When an enemy misses you with a melee attack roll, you can take a Reaction and spend 1 Focus Point to cause that attack to hit one creature of your choice, other than the attacker, that you can see within 5 feet of yourself."
        )
        return description


class MysticBrew(Feature):
    def __init__(self):
        super().__init__(
            name="Mystic Brew",
            origin="Warrior of Mystic Brews Monk Level 6",
            activation=FeatureActivation(duration="1 Hour (8 Hours if Enhanced)"),
            usage_tags=["damage", "control", "buff", "heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def calculate_dc(self, character: CharacterView) -> int | None:
        # Cinnamon Dragon's breath.
        return 8 + character.get_wisdom_modifier() + character.get_proficiency_bonus()

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Brew a magical beverage with Brewer's Supplies when you finish a rest."
            ),
            Facts(
                (
                    (
                        "Brew",
                        "When you finish a Short or Long Rest while holding Brewer's Supplies, produce one pint of a beverage below in a bottle or flask you hold or carry (otherwise it spills and vanishes)",
                    ),
                    (
                        "Leftovers",
                        "Any beverage still left when you finish a Short or Long Rest vanishes",
                    ),
                    (
                        "Drink",
                        "Only you benefit. Drink the full pint over 1 minute",
                    ),
                    (
                        "Duration",
                        "1 hour, or until you drink another magical beverage",
                    ),
                    (
                        "Enhance",
                        "When you create the beverage, spend 1 Focus Point to make the benefits last 8 hours",
                    ),
                )
            ),
            Option(
                "Cinnamon Dragon",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            ("Area", "30-foot Cone of toxic flames"),
                            (
                                "Save",
                                f"Dexterity ({dc_formula(Ability.WISDOM)})",
                            ),
                            (
                                "Failed",
                                "Fire damage equal to four rolls of your Martial Arts die, and the Poisoned condition until the end of its next turn",
                            ),
                            ("Succeeded", "Half damage only"),
                        )
                    ),
                ),
            ),
            Option(
                "Heavenly Spirit",
                (
                    Facts(
                        (
                            (
                                "Resistance",
                                "Two of Cold, Necrotic, Psychic or Radiant damage (your choice)",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Refreshing Dip",
                (
                    Facts(
                        (
                            (
                                "Pool",
                                "Dice of your Martial Arts die type; up to your Wisdom modifier + half your Monk level (round down)",
                            ),
                            (
                                "Use",
                                "Whenever you regain Hit Points, expend and roll one die to regain that many more",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you finish a Short or Long Rest while holding Brewer's Supplies, you can use that tool to magically produce one magical beverage, chosen from the following options: Cinnamon Dragon, Heavenly Spirit, or Refreshing Dip. A pint of the beverage appears in a bottle or flask you are holding or carrying; otherwise, the beverage spills out on the ground and then vanishes. If any beverage remains when you finish a Short or Long Rest, the beverage vanishes.\n"
            "Drinking a Magical Beverage. Only you can gain the benefits of drinking the beverage. You must drink the full pint of the beverage before gaining its benefit. You can spend 1 minute drinking the beverage. You then gain the benefits of the beverage for 1 hour or until you drink another magical beverage, as described below:\n"
            "    * Cinnamon Dragon. You can take a Magic action to exhale toxic flames in a 30-foot Cone. Each creature in the Cone makes a Dexterity saving throw (DC 8 plus your Wisdom modifier and Proficiency Bonus). On a failed save, a creature takes Fire damage equal to four rolls of your Martial Arts die and has the Poisoned condition until the end of its next turn. On a successful save, a creature takes half as much damage only.\n"
            "    * Heavenly Spirit. You gain Resistance to two of the following damage types of your choice: Cold, Necrotic, Psychic, or Radiant damage.\n"
            "    * Refreshing Dip. You have a pool of dice of the same type as your Martial Arts die. The maximum number of dice equals your Wisdom modifier plus half your Monk level (round down). Whenever you regain Hit Points, you can expend and roll one die from this pool to regain additional Hit Points equal to the number rolled.\n"
            "Enhancing a Magical Beverage. When you create a magical beverage, you can expend 1 Focus Point to extend the benefits' duration to 8 hours."
        )
        return description

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # Only Cinnamon Dragon's breath acts on a target; the other beverages
        # are passive while you have them.
        die = MARTIAL_ARTS_DIE.at(character)  # "1d8": four rolls are 4d8
        return [
            CombatEffect(
                name="Cinnamon Dragon breath",
                roll=EffectRoll.SAVE,
                save_ability=Ability.DEXTERITY,
                half_on_success=True,
                damage=(CombatDamage(f"4d{die.split('d')[1]}", DamageType.FIRE),),
                conditions=(
                    CombatCondition("Poisoned", until=(TurnEdge.END, TurnOf.TARGET)),
                ),
                action_type=ActionType.ACTION,
                spends_use=False,
                notes=(
                    "Only while you have drunk a Cinnamon Dragon beverage. A"
                    " 30-foot Cone; a creature that succeeds takes half damage"
                    " and isn't Poisoned.",
                ),
            )
        ]


class WizenedBrewer(Feature):
    def __init__(self):
        super().__init__(
            name="Wizened Brewer",
            origin="Warrior of Mystic Brews Monk Level 11",
            usage_tags=["buff", "damage"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("These beverages are added to your Mystic Brew options."),
            Option(
                "Blue Lightning",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Whenever you take a Reaction that isn't an Opportunity Attack or casting a spell, make one Unarmed Strike as part of it",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Drunkard's Luck",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "Gain Heroic Inspiration if you don't have it. When you make an ability check or saving throw without it, you can give yourself Heroic Inspiration",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Stumbling Monk",
                (
                    Facts(
                        (
                            (
                                "Effect",
                                "When you take a Bonus Action other than Patient Defense, you can also use Patient Defense immediately after it",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn more complex flavors. The following beverages are added to your Mystic Brew options:\n"
            "    * Blue Lightning. Whenever you take a Reaction that isn't making an Opportunity Attack or casting a spell, you can make one Unarmed Strike as part of that Reaction.\n"
            "    * Drunkard's Luck. You gain Heroic Inspiration if you don't already have it. In addition, you can give yourself Heroic Inspiration when you make an ability check or saving throw without it.\n"
            "    * Stumbling Monk. When you take a Bonus Action other than Patient Defense, you can also use Patient Defense immediately after that Bonus Action."
        )
        return description


class MasterBrewer(Feature):
    def __init__(self):
        super().__init__(
            name="Master Brewer",
            origin="Warrior of Mystic Brews Monk Level 17",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Brew",
                        "When you create a Mystic Brew beverage, choose two different options for one beverage",
                    ),
                    ("Drink", "You gain the effects of both options for the duration"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you create a magical beverage using your Mystic Brew feature, you can choose two different options and produce one magical beverage. Drinking the beverage provides the effects of both options for the duration."
        return description


class IntoxicatedFrenzy(Feature):
    def __init__(self):
        super().__init__(
            name="Intoxicated Frenzy",
            origin="Warrior of Mystic Brews Monk Level 17",
            usage_tags=["damage", "control"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "Immediately after you use Patient Defense"),
                    ("Move", "Up to your Speed"),
                    (
                        "Strikes",
                        "Whenever you enter a space within 5 feet of a creature during this move, make an Unarmed Strike against it (each creature at most once per turn)",
                    ),
                    (
                        "On a hit",
                        "The creature makes a Dexterity save or has the Prone condition",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Immediately after you use your Patient Defense, you can move up to your Speed. During this movement, whenever you enter a space within 5 feet of a creature, you can make an Unarmed Strike targeting that creature. In addition, when you hit a creature with an Unarmed Strike granted by this feature, the creature must succeed on a Dexterity saving throw or have the Prone condition. A creature can be targeted by an Unarmed Strike granted by this feature only once per turn."
        return description
