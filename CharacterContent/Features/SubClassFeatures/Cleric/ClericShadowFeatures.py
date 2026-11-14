from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    FeatureTarget,
    RegainedOn,
)
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class ShadowDomainSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Shadow Domain Spells", origin="Shadow Domain Cleric Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The spells ClericShadow.py grants at each Cleric level.
        return [
            Paragraph(
                "From the Cleric level shown, you always have these spells prepared."
            ),
            Table(
                ("Cleric level", "Spells"),
                (
                    (
                        "3",
                        "Crown of Madness, Dissonant Whispers, Mind Spike, Shadow Word: Pain",
                    ),
                    ("5", "Summon Undead, Vampiric Touch"),
                    ("7", "Evard's Black Tentacles, Psychic Horror"),
                    ("9", "Dominate Person, Void Eruption"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your connection to this domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Shadow Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Cleric Level\tSpells\n"
            "3\tCrown of Madness, Dissonant Whispers, Mind Spike, Shadow Word: Pain\n"
            "5\tSummon Undead, Vampiric Touch\n"
            "7\tEvard's Black Tentacles, Psychic Horror\n"
            "9\tDominate Person, Void Eruption"
        )
        return description


class Shadowform(Feature):
    def __init__(self):
        super().__init__(
            name="Shadowform",
            origin="Shadow Domain Cleric Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Minute", range="Self"
            ),
            usage_tags=["buff", "damage"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Use Channel Divinity to take on a shadowy form."),
            Facts(
                (
                    ("Cost", "One use of Channel Divinity"),
                    ("Action", "Bonus Action"),
                    (
                        "Shadow Stealth",
                        "While in Dim Light or Darkness, you can take the Hide action as a Bonus Action",
                    ),
                    (
                        "Void Empowerment",
                        "When you cast a spell with a spell slot that deals Psychic or Necrotic damage, add 1d6 to one damage roll of the spell",
                    ),
                    (
                        "Duration",
                        "1 minute; ends early if you dismiss it (no action required), have the Incapacitated condition, or deal Radiant damage with a spell",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can expend a use of your Channel Divinity to take on a shadowy form that grants you the following benefits:\n"
            "Shadow Stealth. While you are in an area of Dim Light or Darkness, you can take the Hide action as a Bonus Action.\n"
            "Void Empowerment. When you cast a spell using a spell slot that deals Psychic or Necrotic damage, you can add 1d6 to one damage roll of the spell.\n"
            "The form lasts for 1 minute, but it ends early if you dismiss it (no action required), if you have the Incapacitated condition, or if you deal Radiant damage with a spell."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DevouringPlague(Feature):
    def __init__(self):
        super().__init__(
            name="Devouring Plague",
            origin="Shadow Domain Cleric Level 3",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["damage", "heal"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Wisdom modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The uses panel doesn't give the minimum, so Uses spells it out.
        return [
            Paragraph("Feed on a creature's failed saving throw."),
            Facts(
                (
                    (
                        "Trigger",
                        "A creature you can see within 30 feet of you fails a saving throw",
                    ),
                    ("Damage", "1d10 Necrotic damage to that creature"),
                    (
                        "Healing",
                        "You regain Hit Points equal to the Necrotic damage dealt",
                    ),
                    ("Uses", "Wisdom modifier (minimum once) per Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When a creature you can see within 30 feet of you fails a saving throw, you can cause that creature to take 1d10 Necrotic damage. If you do, you regain Hit Points equal to the Necrotic damage dealt.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_wisdom_modifier())


class Dispersion(Feature):
    def __init__(self):
        super().__init__(
            name="Dispersion",
            origin="Shadow Domain Cleric Level 6",
            activation=FeatureActivation(
                action_type=ActionType.REACTION,
                duration="Until the end of your next turn",
                range="Self",
            ),
            usage_tags=["buff", "heal", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Disperse into shadowy energy when you're hit."),
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "You are hit by an attack roll"),
                    (
                        "Effect",
                        "Until the end of your next turn: Resistance to all damage (including the triggering attack), Fly Speed of 40 feet, and you can't take any action, Bonus Action, or Reaction",
                    ),
                    (
                        "When it ends",
                        "Spend up to half your total Hit Point Dice, regaining Hit Points as if you finished a Short Rest",
                    ),
                    ("Uses", "Once per Short or Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you are hit by an attack roll, you can take a Reaction to disperse into shadowy energy. Until the end of your next turn, you have Resistance to all damage (including the damage from the triggering attack); you can't take any action, Bonus Action, or Reaction; and you have a Fly Speed of 40 feet. When the effect ends, you can spend up to half of your total Hit Point Dice, regaining Hit Points as if you had finished a Short Rest.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def number_of_uses(self, character: CharacterView) -> int:
        return 1


class VampiricEmbrace(Feature):
    def __init__(self):
        super().__init__(
            name="Vampiric Embrace",
            origin="Shadow Domain Cleric Level 17",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("While", "Your Shadowform is active"),
                    (
                        "Effect",
                        "Whenever you roll 1d6 to add extra damage to a spell, one creature of your choice within 30 feet of you regains that many Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "While your Shadowform is active, whenever you roll 1d6 to add extra damage to a spell, one creature of your choice within 30 feet of you regains that many Hit Points."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
