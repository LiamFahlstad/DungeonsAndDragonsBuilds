from Core.Definitions import (
    Ability,
)
from Model.Content.Feature import Feature, FeatureActivation, FeatureTarget, RegainedOn
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table, dc_formula


class Channeler(Feature):
    def __init__(self):
        super().__init__(name="Channeler", origin="College of Spirits Bard Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Guiding Whispers", "You know Guidance; its range is 60 feet"),
                    (
                        "Spiritual Focus",
                        "You gain playing cards (Gaming Set) and proficiency with them. Use them, an Arcane Focus (crystal or orb), a Candle or an Ink Pen as your Bard Spellcasting Focus.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You learn how to contact spirits beyond the grave, letting their power and knowledge flow through you. You gain the following benefits.\n"
            "Guiding Whispers. You know the Guidance cantrip. It has a range of 60 feet when you cast it.\n"
            "Spiritual Focus. You employ tools that aid you in channeling spirits. You gain a Gaming Set (playing cards). You have proficiency with this Gaming Set, and you can use it or one of the following items as a Spellcasting Focus for your Bard spells: Arcane Focus (crystal or orb), Candle, or Ink Pen."
        )
        return description


class SpiritsFromBeyond(Feature):
    def __init__(self):
        super().__init__(
            name="Spirits from Beyond",
            origin="College of Spirits Bard Level 3",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["damage", "heal", "buff", "control"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.CHARISMA)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Channel a spirit of the dead when you give out Bardic Inspiration, then unleash it on a creature."
            ),
            Facts(
                (
                    (
                        "Channel",
                        "When you take a Bonus Action to give a creature a Bardic Inspiration die, roll that die and channel the spirit with that number",
                    ),
                    (
                        "Choose instead",
                        "Bonus Action, expending a use of Bardic Inspiration: channel a spirit of your choice whose number is no higher than your Bardic Inspiration die's highest number (a d8 reaches the Shade)",
                    ),
                    ("Lasts", "Until you unleash it or finish a Short or Long Rest"),
                    (
                        "Unleash",
                        "Magic action. Target one creature you can see within 30 feet.",
                    ),
                    (
                        "Save DC",
                        f"Your Bard spell save DC ({dc_formula(Ability.CHARISMA)})",
                    ),
                )
            ),
            Option(
                "Spirits from Beyond",
                (
                    Paragraph("Die = your Bardic Inspiration die."),
                    Table(
                        ("Roll", "Spirit", "Effect"),
                        (
                            (
                                "1",
                                "Beloved",
                                "The target regains Hit Points equal to one roll of the die + your Charisma modifier.",
                            ),
                            (
                                "2",
                                "Sharpshooter",
                                "The target takes Force damage equal to one roll of the die + your Charisma modifier.",
                            ),
                            (
                                "3",
                                "Avenger",
                                "Until the end of your next turn, any creature that hits the target with a melee attack roll takes Force damage equal to one roll of the die.",
                            ),
                            (
                                "4",
                                "Renegade",
                                "The target can immediately take a Reaction to teleport up to 30 feet to an unoccupied space it can see.",
                            ),
                            (
                                "5",
                                "Fortune Teller",
                                "The target has Advantage on D20 Tests until the start of your next turn.",
                            ),
                            (
                                "6",
                                "Wayfarer",
                                "The target gains Temporary Hit Points equal to one roll of the die + your Bard level. While it has them, its Speed increases by 10 feet.",
                            ),
                            (
                                "7",
                                "Trickster",
                                "Wisdom save. Failed: Psychic damage equal to two rolls of the die, and Charmed until the start of your next turn. Succeeded: half the damage only.",
                            ),
                            (
                                "8",
                                "Shade",
                                "The target is Invisible until the end of its next turn, or until it makes an attack roll, deals damage or casts a spell. When that ends, each creature in a 5-foot Emanation from it makes a Constitution save or takes Necrotic damage equal to two rolls of the die.",
                            ),
                            (
                                "9",
                                "Arsonist",
                                "Dexterity save. Fire damage equal to four rolls of the die; half on a success.",
                            ),
                            (
                                "10",
                                "Coward",
                                "The target and each creature of your choice in a 30-foot Emanation from it make a Wisdom save. Failed: Frightened until the start of your next turn; while Frightened, its Speed is halved (round down) and it can take an action or a Bonus Action, not both.",
                            ),
                            (
                                "11",
                                "Brute",
                                "Each creature of your choice in a 30-foot Emanation from the target makes a Strength save. Failed: Thunder damage equal to three rolls of the die, and Prone. Succeeded: half the damage only.",
                            ),
                            (
                                "12",
                                "Priest",
                                "The target regains Hit Points equal to two rolls of the die, and one condition of your choice ends on it: Blinded, Charmed, Deafened, Paralyzed, Poisoned or Stunned.",
                            ),
                        ),
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can call forth spirits of the dead to empower you and your allies. When you take a Bonus Action to give a creature a Bardic Inspiration die, you can call forth the powers of a random spirit. To determine the spirit you channel, roll the Bardic Inspiration die and refer to the Spirits from Beyond table. The spirit remains channeled until you unleash it or until you finish a Short or Long Rest.\n"
            "Controlled Channeling. As a Bonus Action, you can expend a use of your Bardic Inspiration and channel a specific spirit. When you do so, choose the spirit from the Spirits from Beyond table rather than rolling. The chosen spirit's corresponding number must be less than or equal to the highest number on your Bardic Inspiration die; for example, if your Bardic Inspiration die is a d8, you can choose to channel any spirit up to (and including) the Shade.\n"
            "Unleashing a Spirit. As a Magic action, you can unleash one of your channeled spirits. Choose one creature you can see within 30 feet of yourself as the spirit's target. The spirit then takes effect; if a spirit's effect requires a saving throw, the DC equals your Bard spell save DC.\n"
            "Spirits From Beyond\n"
            "Bardic Insp. Die	Spirit\n"
            "1	Beloved. The target regains Hit Points equal to one roll of your Bardic Inspiration die plus your Charisma modifier.\n"
            "2	Sharpshooter. The target takes Force damage equal to a roll of your Bardic Inspiration die plus your Charisma modifier.\n"
            "3	Avenger. Until the end of your next turn, any creature that hits the target with a melee attack roll takes Force damage equal to a roll of your Bardic Inspiration die.\n"
            "4	Renegade. The target can immediately take a Reaction to teleport up to 30 feet to an unoccupied space it can see.\n"
            "5	Fortune Teller. The target has Advantage on D20 Tests until the start of your next turn.\n"
            "6	Wayfarer. The target gains Temporary Hit Points equal to a roll of your Bardic Inspiration die plus your Bard level. While it has these Temporary Hit Points, the target's Speed increases by 10 feet.\n"
            "7	Trickster. The target makes a Wisdom saving throw. On a failed save, the target takes Psychic damage equal to two rolls of your Bardic Inspiration die and has the Charmed condition until the start of your next turn. On a successful save, the target takes half as much damage only.\n"
            "8	Shade. The target gains the Invisible condition until the end of its next turn or until the target makes an attack roll, deals damage, or casts a spell. When the invisibility ends, each creature in a 5-foot Emanation originating from the target must succeed on a Constitution saving throw or take Necrotic damage equal to two rolls of your Bardic Inspiration die.\n"
            "9	Arsonist. The target makes a Dexterity saving throw, taking Fire damage equal to four rolls of your Bardic Inspiration die on a failed save or half as much on a successful one.\n"
            "10	Coward. The target and each creature of your choice in a 30-foot Emanation originating from the target must succeed on a Wisdom saving throw or have the Frightened condition until the start of your next turn. While a creature is Frightened, its Speed is halved (round down), and it can take either an action or a Bonus Action, not both.\n"
            "11	Brute. Each creature of your choice in a 30-foot Emanation originating from the target makes a Strength saving throw. On a failed save, a creature takes Thunder damage equal to three rolls of your Bardic Inspiration die and has the Prone condition. On a successful save, a creature takes half as much damage only.\n"
            "12	Priest. The target regains Hit Points equal to two rolls of your Bardic Inspiration die, and one of the following conditions of your choice ends on the target: Blinded, Charmed,Deafened, Paralyzed, Poisoned or Stunned."
        )
        return description


class EmpoweredChanneling(Feature):
    def __init__(self):
        super().__init__(
            name="Empowered Channeling",
            origin="College of Spirits Bard Level 6",
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Power from Beyond",
                        "Once per turn, when a Bard spell you cast with a spell slot deals damage or restores Hit Points, roll 1d6 and add it to one damage roll or to the healing",
                    ),
                    (
                        "Spiritual Manifestation",
                        "You always have Spirit Guardians prepared and can cast it once per Long Rest without a spell slot",
                    ),
                    (
                        "Guarding spirits",
                        "When you cast Spirit Guardians, you and allies in its Emanation can have Half Cover. Once per Short or Long Rest.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your ability to channel spirits improves. You gain the following benefits.\n"
            "Power from Beyond. Once per turn, when you cast a Bard spell with a spell slot that deals damage or restores Hit Points, roll 1d6. You gain a bonus equal to the number rolled to one of the spell's damage rolls or to the total Hit Points the spell restores.\n"
            "Spiritual Manifestation. You always have the Spirit Guardians spell prepared. You can cast the spell once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest.\n"
            "Whenever you cast the spell, you can modify it so the spirits also guard against worldly threats. When you cast the spell in this way, you and allies within the spell's Emanation have Half Cover. Once you modify the spell in this way, you can't do so again until you finish a Short or Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class MysticalConnection(Feature):
    def __init__(self):
        super().__init__(
            name="Mystical Connection", origin="College of Spirits Bard Level 14"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You roll on the Spirits from Beyond table"),
                    ("Effect", "Roll the die twice and choose which effect to bestow"),
                    ("Doubles", "If both dice match, choose any effect on the table"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain mastery over the spirits you call forth. Whenever you roll on the Spirits from Beyond table, you can roll the die twice and choose which of the two effects to bestow. If you roll the same number on both dice, you can instead choose any effect on the table."
        return description
