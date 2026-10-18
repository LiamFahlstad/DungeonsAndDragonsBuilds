from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
    FeatureDice,
)
from Model.Content.Improvements import (
    SkillBonus,
    GrantArmorTraining,
    GrantWeaponProficiency,
)
from Core.Definitions import Ability, CharacterClass, Skill, ArmorType
from CharacterContent.Items.Weapons import WeaponProficiency
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    dc_formula,
)
from Model.View import CharacterView
from Model.Ledger.LedgerWriter import LedgerWriter


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Cleric Level 1")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spellcasting ability", "Wisdom"),
                    ("Save DC", dc_formula(Ability.WISDOM)),
                    ("Spell attack", "Wisdom modifier + Proficiency Bonus"),
                    ("Cantrips", "Replace one whenever you gain a Cleric level"),
                    (
                        "Prepared spells",
                        "Change them whenever you finish a Long Rest",
                    ),
                    ("Spell slots", "Regain all when you finish a Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Spellcasting:\n"
            "    * Replacing cantrips: Whenever you gain a Cleric level\n"
            "    * Replacing prepared spells: Whenever you finish a Long Rest\n"
            "    * Spellcasting Ability: Wisdom\n"
            "    * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class DivineOrderProtector(Feature):
    def __init__(self):
        super().__init__(name="Divine Order: Protector", origin="Cleric Level 1")

    def apply(self, ledger_writer: LedgerWriter):
        # "...proficiency with Martial weapons and training with Heavy armor."
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)
        GrantArmorTraining([ArmorType.HEAVY]).apply(ledger_writer)

    def get_description(self, character: CharacterView) -> str:
        description = "Trained for battle, you gain proficiency with Martial weapons and training with Heavy armor."
        return description


class DivineOrderThaumaturge(Feature):
    def __init__(self, extra_cantrip: str):
        super().__init__(
            name="Divine Order: Thaumaturge",
            origin="Cleric Level 1",
            usage_tags=["buff"],
        )
        self.extra_cantrip = extra_cantrip

    def apply(self, ledger_writer: LedgerWriter):
        def bonus(cs: CharacterView) -> int:
            return max(1, cs.get_wisdom_modifier())

        SkillBonus(Skill.ARCANA, bonus).apply(ledger_writer)
        SkillBonus(Skill.RELIGION, bonus).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("A mystical connection to the divine."),
            Facts(
                (
                    (
                        "Extra cantrip",
                        f"{self.extra_cantrip}, from the Cleric spell list",
                    ),
                    (
                        "Arcana and Religion",
                        "+ Wisdom modifier (minimum +1) to Intelligence (Arcana or Religion) checks",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = f"You know one extra cantrip from the Cleric spell list: {self.extra_cantrip}. Your mystical connection to the divine gives you a bonus to your Intelligence (Arcana or Religion) checks equal to your Wisdom modifier (minimum bonus of +1)."
        return description


DIVINE_SPARK_DICE = FeatureDice(
    "Divine Spark",
    (
        (2, "1d8"),
        (7, "2d8"),
        (13, "3d8"),
        (18, "4d8"),
    ),
    CharacterClass.CLERIC,
    note="+ Wisdom modifier",
)


class ChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity",
            origin="Cleric Level 2",
            activation=FeatureActivation(
                action_type=ActionType.ACTION, duration="1 Minute", range="30 Feet"
            ),
            usage_tags=["heal", "damage", "control"],
            uses=FeatureUses(
                max_uses=4,
                regain_x_on=(1, "short rest"),
                regain_all_on="long rest",
                current_formula="Current amount: determined by your Cleric level — 2 uses at levels 1-5, 3 at 6-17, 4 at 18+.",
                gained_at=[2, 2, 6, 18],
            ),
            dice=DIVINE_SPARK_DICE,
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can channel divine energy directly from the Outer Planes to fuel magical effects. You start with two such effects: Divine Spark and Turn Undead, each of which is described below. Each time you use this class's Channel Divinity, choose which Channel Divinity effect from this class to create. You gain additional effect options at higher Cleric levels.\n"
            "You can use this class's Channel Divinity twice. You regain one of its expended uses when you finish a Short Rest, and you regain all expended uses when you finish a Long Rest. You gain additional uses when you reach certain Cleric levels, as shown in the Channel Divinity column of the Cleric Features table.\n"
            "If a Channel Divinity effect requires a saving throw, the DC equals the spell save DC from this class's Spellcasting feature.\n"
            "Divine Spark. As a Magic action, you point your Holy Symbol at another creature you can see within 30 feet of yourself and focus divine energy at it. Roll 1d8 and add your Wisdom modifier. You either restore Hit Points to the creature equal to that total or force the creature to make a Constitution saving throw. On a failed save, the creature takes Necrotic or Radiant damage (your choice) equal to that total. On a successful save, the creature takes half as much damage (round down).\n"
            "You roll an additional d8 when you reach Cleric levels 7 (2d8), 13 (3d8), and 18 (4d8).\n"
            "Turn Undead. As a Magic action, you present your Holy Symbol and censure Undead creatures. Each Undead of your choice within 30 feet of you must make a Wisdom saving throw. If the creature fails its save, it has the Frightened and Incapacitated conditions for 1 minute. For that duration, it tries to move as far from you as it can on its turns. This effect ends early on the creature if it takes any damage, if you have the Incapacitated condition, or if you die.\n"
            f"Right now: Divine Spark rolls {DIVINE_SPARK_DICE.at(character)} + {character.get_wisdom_modifier()}."
        )
        return description

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses, their recharge and the Divine Spark dice are in the card's
        # stats panel; this lays out the rest of the source text. Formulas
        # only - the sheet is printed once and kept as the Cleric levels up.
        return [
            Paragraph(
                "Channel divine energy to create one effect. Each time you use "
                "Channel Divinity, choose which effect: you start with Divine Spark "
                "and Turn Undead, and gain more options from your subclass and at "
                "higher Cleric levels."
            ),
            Facts(
                (
                    (
                        "Save DC",
                        f"{dc_formula(Ability.WISDOM)} (your Cleric spell save DC)",
                    ),
                )
            ),
            Option(
                "Divine Spark",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            ("Range", "30 feet"),
                            ("Target", "Another creature you can see"),
                            (
                                "Roll",
                                "Divine Spark dice (see Dice below) + Wisdom "
                                "modifier",
                            ),
                            (
                                "Heal",
                                "The creature regains Hit Points equal to the roll.",
                            ),
                            (
                                "Harm",
                                "Constitution save against your Save DC. Failed: "
                                "Necrotic or "
                                "Radiant damage (your choice) equal to the roll. "
                                "Succeeded: half as much (round down).",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Turn Undead",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            ("Range", "30 feet"),
                            ("Target", "Each Undead of your choice"),
                            ("Save", "Wisdom save against your Save DC"),
                            (
                                "Failed",
                                "Frightened and Incapacitated for 1 minute. On its "
                                "turns it moves as far away from you as it can.",
                            ),
                            (
                                "Ends early",
                                "For a creature that takes any damage; for all of "
                                "them if you have the Incapacitated condition or die.",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def calculate_dc(self, character: CharacterView) -> int:
        return character.calculate_difficulty_class_for_ability(Ability.WISDOM)

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.SHORT_OR_LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        cleric_level = character.get_class_level(CharacterClass.CLERIC)
        if cleric_level >= 18:
            return 4
        elif cleric_level >= 6:
            return 3
        else:
            return 2

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE


class SearUndead(Feature):
    def __init__(self):
        super().__init__(
            name="Sear Undead", origin="Cleric Level 5", usage_tags=["damage"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "You use Turn Undead"),
                    (
                        "Damage",
                        "Roll a number of d8s equal to your Wisdom modifier (minimum 1d8). Each Undead that fails its save takes the total as Radiant damage.",
                    ),
                    ("Turning", "The damage doesn't end the turn effect"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Whenever you use Turn Undead, you can roll a number of d8s equal to your Wisdom modifier (minimum of 1d8) and add the rolls together. Each Undead that fails its saving throw against that use of Turn Undead takes Radiant damage equal to the roll's total. This damage doesn't end the turn effect."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class DivineStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Divine Strike", origin="Cleric Level 7", usage_tags=["damage"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "Once on each of your turns, you hit a creature with an attack roll using a weapon",
                    ),
                    ("Damage", "Extra 1d8 Necrotic or Radiant damage (your choice)"),
                    (
                        "From Cleric level 14",
                        "2d8 instead (Improved Divine Strike)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Once on each of your turns when you hit a creature with an attack roll using a weapon, you can cause the target to take an extra 1d8 Necrotic or Radiant damage (your choice)."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class PotentSpellcasting(Feature):
    def __init__(self):
        super().__init__(
            name="Potent Spellcasting", origin="Cleric Level 7", usage_tags=["buff"]
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Add your Wisdom modifier to the damage you deal with any Cleric cantrip."
        )
        return description


class DivineIntervention(Feature):
    def __init__(self):
        super().__init__(
            name="Divine Intervention",
            origin="Cleric Level 10",
            activation=FeatureActivation(action_type=ActionType.ACTION),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Call on your deity or pantheon to intervene on your behalf."),
            Facts(
                (
                    ("Action", "Magic action"),
                    (
                        "Spell",
                        "Any Cleric spell of level 5 or lower that doesn't require a Reaction to cast",
                    ),
                    (
                        "Effect",
                        "Cast it as part of the same action, without expending a spell slot or needing Material components",
                    ),
                    ("Limit", "Once per Long Rest"),
                    (
                        "From Cleric level 20",
                        "You can choose Wish; if you do, you can't use Divine Intervention again until you finish 2d4 Long Rests (Greater Divine Intervention)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You can call on your deity or pantheon to intervene on your behalf. As a Magic action, choose any Cleric spell of level 5 or lower that doesn't require a Reaction to cast. As part of the same action, you cast that spell without expending a spell slot or needing Material components. You can't use this feature again until you finish a Long Rest."
        return description


class ImprovedDivineStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Divine Strike",
            origin="Cleric Level 14",
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "The extra damage of your Divine Strike increases to 2d8."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class ImprovedPotentSpellcasting(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Potent Spellcasting",
            origin="Cleric Level 14",
            activation=FeatureActivation(range="60 Feet"),
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You cast a Cleric cantrip and deal damage to a creature with it",
                    ),
                    ("Range", "Yourself or another creature within 60 feet"),
                    (
                        "Effect",
                        "Temporary Hit Points equal to twice your Wisdom modifier",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "When you cast a Cleric cantrip and deal damage to a creature with it, you can give vitality to yourself or another creature within 60 feet of yourself, granting a number of Temporary Hit Points equal to twice your Wisdom modifier."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class GreaterDivineIntervention(Feature):
    def __init__(self):
        super().__init__(name="Greater Divine Intervention", origin="Cleric Level 20")

    def get_description(self, character: CharacterView) -> str:
        description = "You can call on even more powerful divine intervention. When you use your Divine Intervention feature, you can choose Wish when you select a spell. If you do so, you can't use Divine Intervention again until you finish 2d4 Long Rests."
        return description
