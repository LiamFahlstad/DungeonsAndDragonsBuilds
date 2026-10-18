from Core.Definitions import DamageType, SORCERER_HIT_DIE, Ability
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
)
from Model.Content.Improvements import DamageResistance
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    Table,
    dc_formula,
)


class PsionicSpells(Feature):
    def __init__(self):
        super().__init__(name="Psionic Spells", origin="Aberrant Sorcerer Level 3")

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
                        "Arms of Hadar, Calm Emotions, Detect Thoughts, Dissonant Whispers, Mind Sliver",
                    ),
                    ("5", "Hunger of Hadar, Sending"),
                    ("7", "Evard's Black Tentacles, Summon Aberration"),
                    ("9", "Rary's Telepathic Bond, Telekinesis"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Psionic Spells table, you thereafter always have the listed spells prepared.\n"
            "Psionic Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Arms of Hadar, Calm Emotions, Detect Thoughts, Dissonant Whispers, Mind Sliver\n"
            "5	Hunger of Hadar, Sending\n"
            "7	Evard's Black Tentacles, Summon Aberration\n"
            "9	Rary's Telepathic Bond, Telekinesis"
        )
        return description


class TelepathicSpeech(Feature):
    def __init__(self):
        super().__init__(
            name="Telepathic Speech",
            origin="Aberrant Sorcerer Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="Minutes Equal to Sorcerer Level",
                range="30 Feet",
            ),
            usage_tags=["utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Link your mind to another creature's."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Target", "One creature you can see within 30 feet"),
                    ("Range", "Charisma modifier miles (minimum 1 mile) between you"),
                    (
                        "Language",
                        "You each must mentally use a language the other knows",
                    ),
                    (
                        "Duration",
                        "Sorcerer level minutes; ends early if you connect with a different creature",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can form a telepathic connection between your mind and the mind of another. As a Bonus Action, choose one creature you can see within 30 feet of yourself. You and the chosen creature can communicate telepathically with each other while the two of you are within a number of miles of each other equal to your Charisma modifier (minimum of 1 mile). To understand each other, you each must mentally use a language the other knows.\n"
            "The telepathic connection lasts for a number of minutes equal to your Sorcerer level. It ends early if you use this ability to form a connection with a different creature."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class PsionicSorcery(Feature):
    def __init__(self):
        super().__init__(name="Psionic Sorcery", origin="Aberrant Sorcerer Level 6")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spells", "Any level 1+ spell from your Psionic Spells feature"),
                    (
                        "Cost",
                        "A spell slot as normal, or Sorcery Points equal to the spell's level",
                    ),
                    (
                        "With Sorcery Points",
                        "No Verbal or Somatic components, and no Material components unless the spell consumes them or they have a cost",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you cast any level 1+ spell from your Psionic Spells feature, you can cast it by expending a spell slot as normal or by spending a number of Sorcery Points equal to the spell’s level. If you cast the spell using Sorcery Points, it requires no Verbal or Somatic components, and it requires no Material components unless they are consumed by the spell or have a cost specified in it."
        return description


class PsychicDefenses(Feature):
    def __init__(self):
        super().__init__(
            name="Psychic Defenses",
            origin="Aberrant Sorcerer Level 6",
            passive=True,
            usage_tags=["buff"],
        )
        self._resistance = DamageResistance(DamageType.PSYCHIC)

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Resistance", "Psychic damage"),
                    (
                        "Advantage",
                        "On saving throws to avoid or end the Charmed or Frightened condition",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You have Resistance to Psychic damage, and you have Advantage on saving throws to avoid or end the Charmed or Frightened condition."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class RevelationInFlesh(Feature):
    def __init__(self):
        super().__init__(
            name="Revelation in Flesh",
            origin="Aberrant Sorcerer Level 14",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="10 Minutes"
            ),
            usage_tags=["buff", "utility"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Unleash the aberrant truth hidden within your body."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Cost", "1 or more Sorcery Points; one benefit below per point"),
                    ("Duration", "10 minutes"),
                )
            ),
            Option(
                "Benefits",
                (
                    Facts(
                        (
                            (
                                "Aquatic Adaptation",
                                "Swim Speed equal to twice your Speed, and you can breathe underwater",
                            ),
                            (
                                "Glistening Flight",
                                "Fly Speed equal to your Speed, and you can hover",
                            ),
                            (
                                "See the Invisible",
                                "See Invisible creatures within 60 feet that aren't behind Total Cover",
                            ),
                            (
                                "Wormlike Movement",
                                "You and your gear can move through spaces as narrow as 1 inch, and you can spend 5 feet of movement to escape nonmagical restraints or the Grappled condition",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can unleash the aberrant truth hidden within yourself. As a Bonus Action, you can spend 1 Sorcery Point or more to magically alter your body for 10 minutes. For each Sorcery Point you spend, you gain one of the following benefits of your choice, the effects of which last until the alteration ends.\n"
            "Aquatic Adaptation. You gain a Swim Speed equal to twice your Speed, and you can breathe underwater. Gills grow from your neck or flare behind your ears, and your fingers become webbed or you grow wriggling cilia.\n"
            "Glistening Flight. You gain a Fly Speed equal to your Speed, and you can hover. As you fly, your skin glistens with mucus or otherworldly light.\n"
            "See the Invisible. You can see any Invisible creature within 60 feet of yourself that isn’t behind Total Cover. Your eyes also turn black or become writhing sensory tendrils.\n"
            "Wormlike Movement. Your body, along with any equipment you are wearing or carrying, becomes slimy and pliable. You can move through any space as narrow as 1 inch, and you can spend 5 feet of movement to escape from nonmagical restraints or the Grappled condition."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class WarpingImplosion(Feature):
    def __init__(self):
        super().__init__(
            name="Warping Implosion",
            origin="Aberrant Sorcerer Level 18",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, range="120 Feet"
            ),
            usage_tags=["damage", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Teleport away and leave a space-warping implosion behind."),
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Teleport", "To an unoccupied space you can see within 120 feet"),
                    ("Area", "Each creature within 30 feet of the space you left"),
                    (
                        "Save",
                        f"Strength save against your spell save DC ({dc_formula(Ability.CHARISMA)})",
                    ),
                    (
                        "Failed",
                        "3d10 Force damage, and pulled straight toward the space you left, into the nearest unoccupied space to it",
                    ),
                    ("Succeeded", "Half the damage only"),
                    (
                        "Limit",
                        "Once per Long Rest; spend 5 Sorcery Points (no action required) to use it again",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can unleash a space-warping anomaly. As a Magic action, you teleport to an unoccupied space you can see within 120 feet of yourself. Immediately after you disappear, each creature within 30 feet of the space you left must make a Strength saving throw against your spell save DC. On a failed save, a creature takes 3d10 Force damage and is pulled straight toward the space you left, ending in an unoccupied space as close to your former space as possible. On a successful save, the creature takes half as much damage only.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.AREA
