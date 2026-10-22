from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
)
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class IllusionSavant(Feature):
    def __init__(self):
        super().__init__(name="Illusion Savant", origin="Illusionist Wizard Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Add Illusion spells to your spellbook for free."),
            Facts(
                (
                    (
                        "Now",
                        "Two Wizard Illusion spells, each no higher than level 2",
                    ),
                    (
                        "New spell slot levels",
                        "Whenever you gain access to a new level of spell slots in this class, one Wizard Illusion spell of a level you have slots for",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose two Wizard spells from the Illusion school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Illusion school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class ImprovedIllusions(Feature):
    def __init__(self):
        super().__init__(name="Improved Illusions", origin="Illusionist Wizard Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Components", "Cast Illusion spells without Verbal components"),
                    ("Range", "Illusion spells with a range of 10+ feet gain 60 feet"),
                    (
                        "Minor Illusion",
                        "You know it (or another Wizard cantrip if you already do); it doesn't count against your cantrips known",
                    ),
                    (
                        "Casting it",
                        "Create both a sound and an image with one casting, and cast it as a Bonus Action",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can cast Illusion spells without providing Verbal components, and if an Illusion spell you cast has a range of 10+ feet, the range increases by 60 feet.\n"
            "You also know the Minor Illusion cantrip. If you already know it, you learn a different Wizard cantrip of your choice. The cantrip doesn't count against your number of cantrips known. You can create both a sound and an image with a single casting of Minor Illusion, and you can cast it as a Bonus Action."
        )
        return description


class PhantasmalCreatures(Feature):
    def __init__(self):
        super().__init__(
            name="Phantasmal Creatures", origin="Illusionist Wizard Level 6"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Always prepared", "Summon Beast and Summon Fey"),
                    (
                        "Illusion",
                        "When you cast either, you can change its school to Illusion; the creature appears spectral",
                    ),
                    (
                        "Free casting",
                        "Cast the Illusion version of each without a spell slot, once per Long Rest; the creature has half its Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You always have the Summon Beast and Summon Fey spells prepared. Whenever you cast either spell, you can change its school to Illusion, which causes the summoned creature to appear spectral. You can cast the Illusion version of each spell without expending a spell slot, but casting it without a slot halves the creature's Hit Points. Once you cast either spell without a spell slot, you must finish a Long Rest before you can cast the spell in that way again."
        return description


class IllusorySelf(Feature):
    def __init__(self):
        super().__init__(
            name="Illusory Self",
            origin="Illusionist Wizard Level 10",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-rest box is in the panel below.
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "A creature hits you with an attack roll"),
                    (
                        "Effect",
                        "An illusory duplicate interposes itself: the attack automatically misses, then the illusion dissipates",
                    ),
                    (
                        "Restore",
                        "Expend a level 2+ spell slot (no action required) to regain the use",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When a creature hits you with an attack roll, you can take a Reaction to interpose an illusory duplicate of yourself between the attacker and yourself. The attack automatically misses you, then the illusion dissipates.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest. You can also restore your use of it by expending a level 2+ spell slot (no action required)."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class IllusoryReality(Feature):
    def __init__(self):
        super().__init__(
            name="Illusory Reality",
            origin="Illusionist Wizard Level 14",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Minute"
            ),
            usage_tags=["buff"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "Give your illusions a semi-reality, like a bridge you can cross."
            ),
            Facts(
                (
                    ("Trigger", "You cast an Illusion spell with a spell slot"),
                    ("Action", "Bonus Action on your turn while the spell lasts"),
                    (
                        "Effect",
                        "One inanimate, nonmagical object in the illusion becomes real for 1 minute; it can't deal damage or impose conditions",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You have learned to weave shadow magic into your illusions to give them a semi-reality. When you cast an Illusion spell with a spell slot, you can choose one inanimate, nonmagical object that is part of the illusion and make that object real. You can do this on your turn as a Bonus Action while the spell is ongoing. The object remains real for 1 minute, during which it can't deal damage or give any conditions. For example, you can create an illusion of a bridge over a chasm and then make it real and cross it."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT
