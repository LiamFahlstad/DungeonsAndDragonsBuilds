from CharacterContent.Features.ClassFeatures.ClassProficiencies import (
    CLASS_SKILL_CHOICES,
)
from Core.Definitions import CharacterClass, Skill
from Model.Content.Feature import (
    Feature,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Content.Improvements import SkillProficiencyChoice
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph


class ModifyMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Modify Magic",
            origin="Arcana Domain Cleric Level 3",
            usage_tags=["buff", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "When you cast a spell, expend one use of your Channel Divinity (no action required) to change the spell in one of these ways."
            ),
            Option(
                "Fortifying Spell",
                (
                    Facts(
                        (
                            ("Target", "One target of the spell"),
                            (
                                "Effect",
                                "It gains Temporary Hit Points equal to 2d8 + your Cleric level",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Tenacious Spell",
                (
                    Facts(
                        (
                            (
                                "Trigger",
                                "The spell forces a saving throw, and a creature you can see succeeds on it",
                            ),
                            (
                                "Effect",
                                "Roll 1d6 and subtract the number rolled from that target's first saving throw against the spell's effect",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can use your Channel Divinity to alter your spells as you cast them. When you cast a spell, you can expend one use of your Channel Divinity and change the spell in one of the following ways (no action required).\n"
            "    * Fortifying Spell: One target of the spell gains a number of Temporary Hit Points equal to 2d8 plus your Cleric level.\n"
            "    * Tenacious Spell: When you cast a spell that forces a creature to make a saving throw, and a creature you can see succeeds on that saving throw, roll 1d6 and subtract the number rolled from the target's first saving throw against the spell's effect."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class StudentOfArcana(Feature):
    SKILL_POOL = [Skill.ARCANA] + [
        skill
        for skill in CLASS_SKILL_CHOICES[CharacterClass.CLERIC][0]
        if skill != Skill.ARCANA
    ]

    def __init__(self, skill: Skill, cantrip_1: str, cantrip_2: str):
        super().__init__(
            name="Student of Arcana",
            origin="Arcana Domain Cleric Level 3",
            passive=True,
        )
        self._skill = skill
        self._cantrip_1 = cantrip_1
        self._cantrip_2 = cantrip_2
        self._proficiency_choice = SkillProficiencyChoice(
            [skill],
            self.SKILL_POOL,
            count=1,
            error_prefix="Student of Arcana",
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._proficiency_choice.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Magical Knowledge", f"Proficiency in {self._skill.value}"),
                    (
                        "Cantrips",
                        f"Two Wizard cantrips: {self._cantrip_1} and {self._cantrip_2}. Whenever you gain a Cleric level, you can replace one with another Wizard cantrip.",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            f"    * Magical Knowledge: You gain proficiency in the Arcana skill or one skill of your choice from the skills available to Clerics at level 1. You chose {self._skill.value}.\n"
            f"    * Cantrips: You learn two Wizard cantrips of your choice. Whenever you gain a Cleric level, you can replace one of these cantrips with another Wizard cantrip. You chose {self._cantrip_1} and {self._cantrip_2}."
        )
        return description


class DispellingRecovery(Feature):
    def __init__(self):
        super().__init__(
            name="Dispelling Recovery",
            origin="Arcana Domain Cleric Level 6",
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-rest box is in the panel below.
        return [
            Paragraph("Follow up healing or curing magic with a free Dispel Magic."),
            Facts(
                (
                    (
                        "Trigger",
                        "Immediately after you cast a spell with a spell slot that restores Hit Points to a creature or ends a condition on a creature",
                    ),
                    (
                        "Effect",
                        "Cast Dispel Magic as part of that action, Bonus Action or Reaction, without expending a spell slot",
                    ),
                    (
                        "Restore",
                        "Expend one use of Channel Divinity (no action required)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Immediately after you cast a spell with a spell slot that restores Hit Points to a creature or ends a condition on a creature, you can cast Dispel Magic as part of that action, Bonus Action, or Reaction, and without expending a spell slot.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest. You also restore your use of it by expending one use of Channel Divinity (no action required)."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class MagicalMastery(Feature):
    def __init__(self, spells: list[str]):
        super().__init__(
            name="Magical Mastery",
            origin="Arcana Domain Cleric Level 17",
            passive=True,
        )
        self._spells = spells

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Spells",
                        f"Four Wizard spells, one each of levels 6, 7, 8 and 9, always prepared: {', '.join(self._spells)}",
                    ),
                    (
                        "Replace",
                        "Whenever you gain a Cleric level, replace one with another Wizard spell of the same level",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = f"You learn four Wizard spells, one from each of levels 6, 7, 8, and 9. You thereafter always have those spells prepared. Whenever you gain a Cleric level, you can replace one of these spells with another Wizard spell of the same level. You chose {', '.join(self._spells)}."
        return description
