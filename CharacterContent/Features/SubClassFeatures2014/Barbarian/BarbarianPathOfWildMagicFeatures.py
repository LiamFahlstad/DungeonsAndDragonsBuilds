import Core.Definitions as Definitions
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
)
from Core.Rules import MAX_PROFICIENCY_BONUS, levels_gained, proficiency_bonus
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table, dc_formula
from Core.Definitions import Ability


class MagicAwareness(Feature):
    def __init__(self):
        super().__init__(
            name="Magic Awareness",
            origin="Path Of Wild Magic Barbarian Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Until the End of Your Next Turn",
                range="60 Feet",
            ),
            usage_tags=["utility"],
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=levels_gained(proficiency_bonus, from_level=3),
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you choose this path at 3rd level, as an action, you can open your awareness to the presence of concentrated magic. Until the end of your next turn, you know the location of any spell or magic item within 60 feet of you that isn't behind total cover. When you sense a spell, you learn which school of magic it belongs to.\n"
            "\n"
            "You can use this feature a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()


class WildSurge(Feature):
    def __init__(self):
        super().__init__(
            name="Wild Surge",
            origin="Path Of Wild Magic Barbarian Level 3",
            usage_tags=["damage", "heal", "buff", "control", "utility"],
            activation=FeatureActivation(duration="Until Your Rage Ends"),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return (
            8
            + character.get_proficiency_bonus()
            + character.get_constitution_modifier()
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Wild magic erupts from you when you enter your rage."),
            Facts(
                (
                    ("Trigger", "You enter your rage: roll a d8 on the table below"),
                    ("Save DC", dc_formula(Ability.CONSTITUTION)),
                )
            ),
            Option(
                "Wild Magic",
                (
                    Table(
                        ("d8", "Effect"),
                        (
                            (
                                "1",
                                "Each creature of your choice you can see within 30 feet makes a Constitution save or takes 1d12 Necrotic damage. You gain 1d12 Temporary Hit Points.",
                            ),
                            (
                                "2",
                                "Teleport up to 30 feet to an unoccupied space you can see. Until your rage ends, repeat as a Bonus Action on each of your turns.",
                            ),
                            (
                                "3",
                                "A spirit appears within 5 feet of one creature you can see within 30 feet. At the end of the turn it explodes: each creature within 5 feet of it makes a Dexterity save or takes 1d6 Force damage. Until your rage ends, summon another as a Bonus Action on each of your turns.",
                            ),
                            (
                                "4",
                                "Until your rage ends, one weapon you hold deals Force damage and gains the Light and Thrown properties (range 20/60). If it leaves your hand, it reappears there at the end of the turn.",
                            ),
                            (
                                "5",
                                "Until your rage ends, a creature that hits you with an attack roll takes 1d6 Force damage.",
                            ),
                            (
                                "6",
                                "Until your rage ends, you have a +1 bonus to AC, and allies within 10 feet of you have it too.",
                            ),
                            (
                                "7",
                                "Until your rage ends, the ground within 15 feet of you is Difficult Terrain for your enemies.",
                            ),
                            (
                                "8",
                                "Another creature you can see within 30 feet makes a Constitution save or takes 1d6 Radiant damage and is Blinded until the start of your next turn. Until your rage ends, repeat as a Bonus Action on each of your turns.",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        proficiency_bonus = character.get_proficiency_bonus()
        con_mod = character.get_ability_modifier(Definitions.Ability.CONSTITUTION)
        dc = 8 + proficiency_bonus + con_mod
        description = (
            "Also at 3rd level, the magical energy roiling inside you sometimes erupts from you. When you enter your rage, roll on the Wild Magic table to determine the magical effect produced.\n"
            "\n"
            f"If the effect requires a saving throw, the DC equals 8 + your proficiency bonus + your Constitution modifier ({dc}).\n"
            "\n"
            "Wild Magic\n"
            "d8\tEffect\n"
            "1\tEach creature of your choice that you can see within 30 feet of you must succeed on a Constitution saving throw or take 1d12 necrotic damage. You also gain 1d12 temporary hit points.\n"
            "2\tYou teleport up to 30 feet to an unoccupied space you can see. Until your rage ends, you can use this effect again on each of your turns as a bonus action.\n"
            "3\tAn intangible spirit, which looks like a flumph or a pixie (your choice), appears within 5 feet of one creature of your choice that you can see within 30 feet of you. At the end of the current turn, the spirit explodes, and each creature within 5 feet of it must succeed on a Dexterity saving throw or take 1d6 force damage. Until your rage ends, you can use this effect again, summoning another spirit, on each of your turns as a bonus action.\n"
            "4\tMagic infuses one weapon of your choice that you are holding. Until your rage ends, the weapon's damage type changes to force, and it gains the light and thrown properties, with a normal range of 20 feet and a long range of 60 feet. If the weapon leaves your hand, the weapon reappears in your hand at the end of the current turn.\n"
            "5\tWhenever a creature hits you with an attack roll before your rage ends, that creature takes 1d6 force damage, as magic lashes out in retribution.\n"
            "6\tUntil your rage ends, you are surrounded by multicolored, protective lights; you gain a +1 bonus to AC, and while within 10 feet of you, your allies gain the same bonus.\n"
            "7\tFlowers and vines temporarily grow around you; until your rage ends, the ground within 15 feet of you is difficult terrain for your enemies.\n"
            "8\tA bolt of light shoots from your chest. Another creature of your choice that you can see within 30 feet of you must succeed on a Constitution saving throw or take 1d6 radiant damage and be blinded until the start of your next turn. Until your rage ends, you can use this effect again on each of your turns as a bonus action."
        )
        return description


class BolsteringMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Bolstering Magic",
            origin="Path Of Wild Magic Barbarian Level 6",
            usage_tags=["buff", "utility"],
            activation=FeatureActivation(
                action_type="action", duration="For 10 Minutes", range="Touch"
            ),
            uses=FeatureUses(
                max_uses=MAX_PROFICIENCY_BONUS,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your proficiency bonus.",
                gained_at=levels_gained(proficiency_bonus, from_level=6),
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph("Bolster yourself or a companion with wild magic."),
            Facts(
                (
                    ("Action", "Action"),
                    ("Target", "One creature you touch (can be you)"),
                )
            ),
            Option(
                "Choose one",
                (
                    Table(
                        ("Benefit", "Effect"),
                        (
                            (
                                "Boost",
                                "For 10 minutes, it adds a d3 to its attack rolls and ability checks",
                            ),
                            (
                                "Restore",
                                "Roll a d3: it regains one expended spell slot of that level or lower. A creature can receive this only once per long rest.",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Beginning at 6th level, you can harness your wild magic to bolster yourself or a companion. As an action, you can touch one creature (which can be yourself) and confer one of the following benefits of your choice to that creature:\n"
            "\n"
            "For 10 minutes, the creature can roll a d3 whenever making an attack roll or an ability check and add the number rolled to the d20 roll.\n"
            "\n"
            "Roll a d3. The creature regains one expended spell slot, the level of which equals the number rolled or lower (the creature's choice). Once a creature receives this benefit, that creature can't receive it again until after a long rest.\n"
            "\n"
            "You can take this action a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return description

    def number_of_uses(self, character: CharacterView) -> int:
        return character.get_proficiency_bonus()


class UnstableBacklash(Feature):
    def __init__(self):
        super().__init__(
            name="Unstable Backlash",
            origin="Path Of Wild Magic Barbarian Level 10",
            usage_tags=["damage", "heal", "buff", "control", "utility"],
            activation=FeatureActivation(action_type="reaction"),
        )

    def get_description(self, character: CharacterView) -> str:
        description = "At 10th level, when you are imperiled during your rage, the magic within you can lash out; immediately after you take damage or fail a saving throw while raging, you can use your reaction to roll on the Wild Magic table and immediately produce the effect rolled. This effect replaces your current Wild Magic effect."
        return description


class ControlledSurge(Feature):
    def __init__(self):
        super().__init__(
            name="Controlled Surge",
            origin="Path Of Wild Magic Barbarian Level 14",
            usage_tags=["damage", "heal", "buff", "control", "utility"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "At 14th level, whenever you roll on the Wild Magic table, you can roll the die twice and choose which of the two effects to unleash. If you roll the same number on both dice, you can ignore the number and choose any effect on the table."
        return description
