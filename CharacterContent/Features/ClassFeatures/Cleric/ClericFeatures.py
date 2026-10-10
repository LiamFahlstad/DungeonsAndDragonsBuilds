from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Content.Improvements import (
    SkillBonus,
    GrantArmorTraining,
    GrantWeaponProficiency,
)
from Core.Definitions import CharacterClass, Skill, ArmorType
from CharacterContent.Items.Weapons import WeaponProficiency
from Model.View import CharacterView
from Model.Ledger.LedgerWriter import LedgerWriter
from Utils import StringUtils


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Cleric Level 1")

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Spellcasting:\n"
            "    * Replacing cantrips: Whenever you gain a Cleric level\n"
            "    * Replacing prepared spells: Whenever you finish a Long Rest\n"
            "    * Spellcasting Ability: Wisdom\n"
            "    * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
        )
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            ("Replacing Cantrips", "Whenever you gain a Cleric level"),
            ("Replacing Prepared Spells", "Whenever you finish a Long Rest"),
            ("Spellcasting Ability", "Wisdom"),
            ("Regaining Spell Slots", "All expended slots return on Long Rest"),
        ]

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

    def get_description(self, character: CharacterView) -> str:
        description = f"You know one extra cantrip from the Cleric spell list: {self.extra_cantrip}. Your mystical connection to the divine gives you a bonus to your Intelligence (Arcana or Religion) checks equal to your Wisdom modifier (minimum bonus of +1)."
        return description


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
                current_formula="Current amount: determined by your character level — 2 uses at levels 1-5, 3 at 6-17, 4 at 18+.",
            ),
        )

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can channel divine energy directly from the Outer Planes to fuel magical effects. You start with two such effects: Divine Spark and Turn Undead, each of which is described below. Each time you use this class's Channel Divinity, choose which Channel Divinity effect from this class to create. You gain additional effect options at higher Cleric levels.\n"
            "You can use this class's Channel Divinity. You regain one of its expended uses when you finish a Short Rest, and you regain all expended uses when you finish a Long Rest. You gain additional uses when you reach certain Cleric levels, as shown in the Channel Divinity column of the Cleric Features table.\n"
            "If a Channel Divinity effect requires a saving throw, the DC equals the spell save DC from this class's Spellcasting feature.\n"
            "Divine Spark. As a Magic action, you point your Holy Symbol at another creature you can see within 30 feet of yourself and focus divine energy at it. Roll 1d8 and add your Wisdom modifier. You either restore Hit Points to the creature equal to that total or force the creature to make a Constitution saving throw. On a failed save, the creature takes Necrotic or Radiant damage (your choice) equal to that total. On a successful save, the creature takes half as much damage (round down).\n"
            "You roll an additional d8 when you reach Cleric levels 7 (2d8), 13 (3d8), and 18 (4d8).\n"
            "Turn Undead. As a Magic action, you present your Holy Symbol and censure Undead creatures. Each Undead of your choice within 30 feet of you must make a Wisdom saving throw. If the creature fails its save, it has the Frightened and Incapacitated conditions for 1 minute. For that duration, it tries to move as far from you as it can on its turns. This effect ends early on the creature if it takes any damage, if you have the Incapacitated condition, or if you die."
        )
        return description

    def get_resource_tiles(
        self, character: CharacterView
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        uses_by_level = {}
        for level in range(2, 21):
            if level >= 18:
                uses_by_level[level] = 4
            elif level >= 6:
                uses_by_level[level] = 3
            else:
                uses_by_level[level] = 2
        steps = [
            (f"Lv {level_range}", str(value))
            for level_range, value in StringUtils.compress_level_progression(
                uses_by_level
            )
        ]
        return [("Channel Divinity Uses", steps)]

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

    def get_description(self, character: CharacterView) -> str:
        description = "You can call on your deity or pantheon to intervene on your behalf. As a Magic action, choose any Cleric spell of level 5 or lower that doesn't require a Reaction to cast. As part of the same action, you cast that spell without expending a spell slot or needing Material components. You can't use this feature again until you finish a Long Rest."
        return description

    def get_table_description(self, character: CharacterView) -> list[tuple[str, str]]:
        return [
            (
                "What",
                "Cast any Cleric spell of level 5 or lower (no Reaction required)",
            ),
            ("Casting Time", "Magic action"),
            ("Cost", "No spell slot or Material components"),
            ("Recharge", "Long Rest"),
        ]


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
