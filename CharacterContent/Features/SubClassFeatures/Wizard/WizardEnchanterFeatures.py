from Core.Definitions import Ability, Skill
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Content.Improvements import SkillBonus, SkillProficiencyChoice
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, dc_formula


class EnchantingConversationalist(Feature):
    SKILL_POOL = [
        Skill.DECEPTION,
        Skill.INTIMIDATION,
        Skill.PERSUASION,
    ]

    def __init__(self, skill: Skill):
        super().__init__(
            name="Enchanting Conversationalist",
            origin="Enchanter Wizard Level 3",
            passive=True,
        )
        self._skill = skill
        self._proficiency_choice = SkillProficiencyChoice(
            [skill],
            self.SKILL_POOL,
            count=1,
            error_prefix="Enchanting Conversationalist",
        )

    def apply(self, ledger_writer: LedgerWriter):
        def bonus(cs: CharacterView) -> int:
            return max(1, cs.get_intelligence_modifier())

        self._proficiency_choice.apply(ledger_writer)
        SkillBonus(self._skill, bonus).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Skill", f"Proficiency in {self._skill.value}"),
                    (
                        "Bonus",
                        f"Add your Intelligence modifier (minimum of +1) to {self._skill.value} checks",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            f"You gain proficiency in one of the following skills of your choice: Deception, Intimidation, or Persuasion. You chose {self._skill.value}.\n"
            "In addition, when you make an ability check with the chosen skill, you gain a bonus to the check equal to your Intelligence modifier (minimum of +1)."
        )
        return description


class EnchantmentSavant(Feature):
    def __init__(self):
        super().__init__(name="Enchantment Savant", origin="Enchanter Wizard Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Add Enchantment spells to your spellbook for free."),
            Facts(
                (
                    (
                        "Now",
                        "Two Wizard Enchantment spells, each no higher than level 2",
                    ),
                    (
                        "New spell slot levels",
                        "Whenever you gain access to a new level of spell slots in this class, one Wizard Enchantment spell of a level you have slots for",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose two Wizard spells from the Enchantment school, each of which must be no higher than level 2, and add them to your spellbook for free.\n"
            "In addition, whenever you gain access to a new level of spell slots in this class, you can add one Wizard spell from the Enchantment school to your spellbook for free. The chosen spell must be of a level for which you have spell slots."
        )
        return description


class HypnoticPresence(Feature):
    def __init__(self):
        super().__init__(
            name="Hypnotic Presence",
            origin="Enchanter Wizard Level 3",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Minute", range="10 Feet"
            ),
            usage_tags=["control"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier (minimum of once).",
            ),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.INTELLIGENCE)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses (Intelligence modifier, minimum of once) are in the panel below.
        return [
            Paragraph(
                "Enthrall a creature with charming words and an enchanting gaze."
            ),
            Facts(
                (
                    ("Action", "Magic action"),
                    ("Range", "10 feet"),
                    (
                        "Target",
                        "One creature you can see, that can see or hear you",
                    ),
                    (
                        "Save",
                        f"Wisdom save against your spell save DC ({dc_formula(Ability.INTELLIGENCE)})",
                    ),
                    (
                        "Failed",
                        "Charmed for 1 minute; while Charmed, it has the Incapacitated condition and a Speed of 0",
                    ),
                    (
                        "Ends early",
                        "The target is more than 10 feet away from you, can neither see nor hear you, or takes damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your charming words and enchanting gaze can enthrall another creature. As a Magic action, choose one creature that you can see within 10 feet of yourself. If the target can see or hear you, it must succeed on a Wisdom saving throw against your spell save DC or have the Charmed condition for 1 minute or until the target is more than 10 feet away from you, the target can neither see nor hear you, or the target takes damage. While Charmed, the target has the Incapacitated condition and a Speed of 0.\n"
            "You can use this feature a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())


class SplitEnchantment(Feature):
    def __init__(self):
        super().__init__(
            name="Split Enchantment",
            origin="Enchanter Wizard Level 6",
            usage_tags=["control"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses (Intelligence modifier) are in the panel below.
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You use a spell slot to cast an Enchantment spell, such as Charm Person, that can target an additional creature when cast with a higher-level slot",
                    ),
                    ("Effect", "Increase the spell's effective level by 1"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you use a spell slot to cast an Enchantment spell, such as Charm Person, that can be cast with a higher-level spell slot to target an additional creature, you can increase the spell's effective level by 1.\n"
            "You can use this feature a number of times equal to your Intelligence modifier, and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(0, character.get_intelligence_modifier())


class InstinctiveCharm(Feature):
    def __init__(self):
        super().__init__(
            name="Instinctive Charm",
            origin="Enchanter Wizard Level 10",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.INTELLIGENCE)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Redirect an attack that hits you onto another creature."),
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "A creature you can see within 30 feet of you hits you with an attack roll",
                    ),
                    (
                        "Save",
                        f"The attacker makes a Wisdom save against your spell save DC ({dc_formula(Ability.INTELLIGENCE)})",
                    ),
                    (
                        "Failed",
                        "The attack misses instead. If another creature other than the attacker is within the attack's range, the attacker targets it with the same attack roll (you choose which one if several are)",
                    ),
                    (
                        "Restore",
                        "Cast an Enchantment spell with a spell slot",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When a creature within 30 feet of you that you can see hits you with an attack roll, you can take a Reaction to force the attacker to make a Wisdom saving throw against your spell save DC. On a failed save, the attack misses instead, and if there is another creature within range of the attack other than the attacker, the attacker targets that creature with the triggering attack, using the same attack roll. If multiple creatures are within the attack's range, you choose which one to target.\n"
            "Once you take this Reaction, you can't do so again until you finish a Long Rest. You can also restore your use of it by casting an Enchantment spell with a spell slot."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class AlterMemories(Feature):
    def __init__(self):
        super().__init__(
            name="Alter Memories",
            origin="Enchanter Wizard Level 14",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            usage_tags=["control", "utility"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.INTELLIGENCE)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Hide your magical influence and erase a creature's memories."),
            Facts(
                (
                    (
                        "Trigger",
                        "You cast an Enchantment spell that imposes the Charmed condition using a spell slot",
                    ),
                    (
                        "Unaware",
                        "Choose one creature targeted by the spell: it remains unaware of being Charmed by you",
                    ),
                    (
                        "Erase memories",
                        "Once before the spell ends, take a Magic action: the chosen creature makes an Intelligence save against your spell save DC",
                    ),
                    (
                        "Failed",
                        "It loses up to 1 + your Intelligence modifier hours of memories (minimum of 1 hour), no more than the spell's duration",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can make a creature unaware of your magical influence. When you cast an Enchantment spell that imposes the Charmed condition using a spell slot, you can choose one creature targeted by the spell. That creature remains unaware of being Charmed by you.\n"
            "In addition, once before the spell ends, you can take a Magic action to force the chosen creature to make an Intelligence saving throw against your spell save DC. On a failed save, you can make the creature lose a number of hours of its memories equal to 1 plus your Intelligence modifier (minimum of 1 hour lost). You can make the creature forget less time, and the amount of time can't exceed the duration of your Enchantment spell."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
