from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import MultiAbilityArmorClass, SkillProficiencyChoice
from Core.Definitions import Ability, Skill
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import MAX_ABILITY_MODIFIER
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, dc_formula


class ElementalSmite(Feature):
    def __init__(self):
        super().__init__(
            name="Elemental Smite",
            origin="Oath of the Noble Genies Paladin Level 3",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["damage", "control", "buff"],
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.CHARISMA)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Add a genie's power to your Divine Smite."),
            Facts(
                (
                    ("Trigger", "Immediately after you cast Divine Smite"),
                    ("Cost", "One use of Channel Divinity"),
                    ("Save DC", f"Your spell save DC ({dc_formula(Ability.CHARISMA)})"),
                )
            ),
            Option(
                "Effects (choose one)",
                (
                    Facts(
                        (
                            (
                                "Dao's Crush",
                                "The Smite's target is Grappled (escape against your Save DC) and Restrained while Grappled",
                            ),
                            (
                                "Djinni's Escape",
                                "Teleport up to 30 feet to a space you can see. Until the end of your next turn: Resistance to Bludgeoning, Piercing and Slashing damage, and Immunity to Grappled, Prone and Restrained.",
                            ),
                            (
                                "Efreeti's Fury",
                                "The target takes +2d4 Fire damage, and another creature you can see within 30 feet takes 2d4 Fire damage",
                            ),
                            (
                                "Marid's Surge",
                                "The target and each creature of your choice in a 10-foot Emanation from you make a Strength save. Failed: pushed 15 feet away from you and Prone.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Immediately after you cast Divine Smite, you can expend one use of your Channel Divinity and invoke one of the following effects.\n"
            "Dao's Crush. Earth rises up around the target of your Divine Smite. The target has the Grappled condition (escape DC equal to your spell save DC). While Grappled, the target has the Restrained condition.\n"
            "Djinni's Escape. You teleport to an unoccupied space you can see within 30 feet of yourself and take on a semi-incorporeal form, which lasts until the end of your next turn. While in this form, you have Resistance to Bludgeoning, Piercing, and Slashing damage, and you have Immunity to the Grappled, Prone, and Restrained conditions.\n"
            "Efreeti's Fury. The target of your Divine Smite takes an extra 2d4 Fire damage, and fire jumps from the target to another creature you can see within 30 feet of yourself. The second creature also takes 2d4 Fire damage.\n"
            "Marid's Surge. The target of your Divine Smite and each creature of your choice in a 10-foot Emanation originating from you make a Strength saving throw against your spell save DC. On a failed save, a creature is pushed 15 feet straight away from you and has the Prone condition."
        )
        return description


class GenieSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Genie Spells", origin="Oath of the Noble Genies Paladin Level 3"
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach a Paladin level specified in the Genie Spells table, you thereafter always have the listed spells prepared\n"
            "Genie Spells\n"
            "Paladin Level	Spells\n"
            "3	Chromatic Orb, Elementalism, Thunderous Smite\n"
            "5	Mirror Image, Phantasmal Force\n"
            "9	Fly, Gaseous Form\n"
            "13	Conjure Minor Elementals, Summon Elemental\n"
            "17	Banishing Smite, Contact Other Plane"
        )
        return description


class GeniesSplendor(Feature):
    VALID_SKILLS = [
        Skill.ACROBATICS,
        Skill.INTIMIDATION,
        Skill.PERFORMANCE,
        Skill.PERSUASION,
    ]

    def __init__(self, skill: Skill):
        self.skill = skill
        super().__init__(
            name="Genie's Splendor",
            origin="Oath of the Noble Genies Paladin Level 3",
            usage_tags=["buff"],
        )
        # "When you aren't wearing any armor, your base Armor Class equals 10
        # plus your Dexterity and Charisma modifiers. You can use a Shield..."
        self._ac = MultiAbilityArmorClass(10, [Ability.DEXTERITY, Ability.CHARISMA])
        self._skill = SkillProficiencyChoice(
            [skill], self.VALID_SKILLS, count=1, error_prefix="Genie's Splendor"
        )

    def apply(self, ledger_writer: LedgerWriter):
        self._ac.apply(ledger_writer)
        self._skill.apply(ledger_writer)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you aren't wearing any armor, your base Armor Class equals 10 plus your Dexterity and Charisma modifiers. You can use a Shield and still gain this benefit.\n"
            "You also gain proficiency in one of the following skills of your choice: Acrobatics, Intimidation, Performance, or Persuasion. "
            f"You chose {self.skill.value}."
        )
        return description


class AuraOfElementalShielding(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Elemental Shielding",
            origin="Oath of the Noble Genies Paladin Level 7",
            usage_tags=["buff"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder. You and your allies have Resistance to that damage type while in your Aura of Protection.\n"
            "At the start of each of your turns, you can change the damage type affected by this feature to one of the other listed options (no action required)."
        )
        return description


class ElementalRebuke(Feature):
    def __init__(self):
        super().__init__(
            name="Elemental Rebuke",
            origin="Oath of the Noble Genies Paladin Level 15",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["damage", "buff"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Charisma modifier.",
            ),
        )

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.CHARISMA)

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_charisma_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph("Turn an attack's force back on the attacker."),
            Facts(
                (
                    ("Action", "Reaction"),
                    ("Trigger", "You're hit by an attack roll"),
                    ("Effect", "Halve the attack's damage to you (round down)"),
                    (
                        "Save",
                        f"The attacker makes a Dexterity save against your spell save DC ({dc_formula(Ability.CHARISMA)})",
                    ),
                    (
                        "Failed",
                        "2d10 + Charisma modifier damage: Acid, Cold, Fire, Lightning or Thunder (your choice)",
                    ),
                    ("Succeeded", "Half damage"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you are hit by an attack roll, you can take a Reaction to halve the attack's damage against yourself (round down) and force the attacker to make a Dexterity saving throw against your spell save DC. On a failed save, the attacker takes damage equal to 2d10 plus your Charisma modifier of one of the following types (your choice): Acid, Cold, Fire, Lightning, or Thunder. On a successful save, the attacker takes half as much damage.\n"
            "You can use this feature a number of times equal to your Charisma modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description


class NobleScion(Feature):
    def __init__(self):
        super().__init__(
            name="Noble Scion",
            origin="Oath of the Noble Genies Paladin Level 20",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="10 Minutes or Until Ended",
            ),
            usage_tags=["buff", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you gain the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Flight. You have a Fly Speed of 60 feet and can hover.\n"
            "Minor Wish. When you or an ally in your Aura of Protection fails a D20 Test, you can take a Reaction to make you or that ally succeed instead."
        )
        return description
