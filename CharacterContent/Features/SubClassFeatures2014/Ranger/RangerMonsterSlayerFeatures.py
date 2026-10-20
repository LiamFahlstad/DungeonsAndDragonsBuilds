from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Core.Definitions import Ability
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table, dc_formula


class MonsterSlayerMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Monster Slayer Magic", origin="Monster Slayer Ranger Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Learned", "The spells below, from the Ranger level shown"),
                    (
                        "Spells known",
                        "They're Ranger spells for you but don't count against your Ranger spells known",
                    ),
                )
            ),
            Table(
                ("Ranger level", "Spell"),
                (
                    ("3", "Protection from Evil and Good"),
                    ("5", "Zone of Truth"),
                    ("9", "Magic Circle"),
                    ("13", "Banishment"),
                    ("17", "Hold Monster"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Starting at 3rd level, you learn an additional spell when you reach certain levels in this class, as shown in the Monster Slayer Spells table. The spell counts as a ranger spell for you, but it doesn't count against the number of ranger spells you know.\n"
            "Monster Slayer Spells\n"
            "Ranger Level	Spells\n"
            "3	Protection from Evil and Good\n"
            "5	Zone of Truth\n"
            "9	Magic Circle\n"
            "13	Banishment\n"
            "17	Hold Monster"
        )
        return description


class HuntersSense(Feature):
    def __init__(self):
        super().__init__(
            name="Hunter's Sense",
            origin="Monster Slayer Ranger Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="60 Feet"
            ),
            usage_tags=["utility"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Action"),
                    ("Range", "60 feet"),
                    ("Target", "One creature you can see"),
                    (
                        "Effect",
                        "Learn its damage immunities, resistances and vulnerabilities. A creature hidden from divination seems to have none.",
                    ),
                    ("Uses", "Wisdom modifier (minimum once) per long rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 3rd level, you gain the ability to peer at a creature and magically discern how best to hurt it. As an action, choose one creature you can see within 60 feet of you. You immediately learn whether the creature has any damage immunities, resistances, or vulnerabilities and what they are. If the creature is hidden from divination magic, you sense that it has no damage immunities, resistances, or vulnerabilities.\n"
            "\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once). You regain all expended uses of it when you finish a long rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class SlayersPrey(Feature):
    def __init__(self):
        super().__init__(
            name="Slayer's Prey",
            origin="Monster Slayer Ranger Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Until Short or Long Rest",
                range="60 Feet",
            ),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Focus your ire on one foe, increasing the harm you inflict on it."
            ),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Target", "One creature you can see within 60 feet"),
                    (
                        "Extra damage",
                        "1d6 from the weapon, the first time each turn you hit the target with a weapon attack",
                    ),
                    (
                        "Duration",
                        "Until you finish a Short or Long Rest; ends early if you designate a different creature",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Starting at 3rd level, you can focus your ire on one foe, increasing the harm you inflict on it. As a bonus action, you designate one creature you can see within 60 feet of you as the target of this feature. The first time each turn that you hit that target with a weapon attack, it takes an extra 1d6 damage from the weapon.\n"
            "\n"
            "This benefit lasts until you finish a short or long rest. It ends early if you designate a different creature."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SupernaturalDefense(Feature):
    def __init__(self):
        super().__init__(
            name="Supernatural Defense",
            origin="Monster Slayer Ranger Level 7",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "You gain extra resilience against your prey's assaults on your mind and body."
            ),
            Facts(
                (
                    (
                        "Trigger",
                        "The target of your Slayer's Prey forces you to make a saving throw, or you make an ability check to escape its grapple",
                    ),
                    ("Effect", "Add 1d6 to your roll"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "At 7th level, you gain extra resilience against your prey's assaults on your mind and body. Whenever the target of your Slayer's Prey forces you to make a saving throw and whenever you make an ability check to escape that target's grapple, add 1d6 to your roll."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class MagicUsersNemesis(Feature):
    def __init__(self):
        super().__init__(
            name="Magic-User's Nemesis",
            origin="Monster Slayer Ranger Level 11",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="60 Feet"
            ),
            usage_tags=["control"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        wisdom_modifier = character.get_wisdom_modifier()
        return 8 + proficiency_bonus + wisdom_modifier

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Short-or-Long-Rest box is in the panel below.
        return [
            Paragraph("Thwart someone else's magic."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "You see a creature within 60 feet casting a spell or teleporting",
                    ),
                    (
                        "Save",
                        f"Wisdom, against your spell save DC ({dc_formula(Ability.WISDOM)})",
                    ),
                    ("Failed save", "Its spell or teleport fails and is wasted"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "At 11th level, you gain the ability to thwart someone else's magic. When you see a creature casting a spell or teleporting within 60 feet of you, you can use your reaction to try to magically foil it. The creature must succeed on a Wisdom saving throw against your spell save DC, or its spell or teleport fails and is wasted.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SlayersCounter(Feature):
    def __init__(self):
        super().__init__(
            name="Slayer's Counter",
            origin="Monster Slayer Ranger Level 15",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Counterattack when your prey tries to sabotage you."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "The target of your Slayer's Prey forces you to make a saving throw",
                    ),
                    (
                        "Effect",
                        "Make one weapon attack against it, immediately before the saving throw",
                    ),
                    (
                        "On a hit",
                        "Your save automatically succeeds, in addition to the attack's normal effects",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "At 15th level, you gain the ability to counterattack when your prey tries to sabotage you. If the target of your Slayer's Prey forces you to make a saving throw, you can use your reaction to make one weapon attack against the quarry. You make this attack immediately before making the saving throw. If the attack hits, your save automatically succeeds, in addition to the attack's normal effects."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
