import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class AcolyteOfNature(Feature):
    def __init__(self):
        super().__init__(name="Acolyte of Nature", origin="Nature Domain Cleric Level 3", skippable_in_concise=True)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn one cantrip of your choice from the druid spell list. This cantrip counts as a cleric cantrip for you, but it doesn't count against the number of cleric cantrips you know. You also gain proficiency in one of the following skills of your choice: Animal Handling, Nature, or Survival."
        )
        return description


class BonusProficiency(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiency", origin="Nature Domain Cleric Level 3", skippable_in_concise=True)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with heavy armor."
        return description


class NatureDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Nature Domain Spells", origin="Nature Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Nature Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Nature Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tAnimal Friendship, Speak with Animals\n"
            "3rd\tBarkskin, Spike Growth\n"
            "5th\tPlant Growth, Wind Wall\n"
            "7th\tDominate Beast, Grasping Vine\n"
            "9th\tInsect Plague, Tree Stride"
        )
        return description


class CharmAnimalsAndPlantsChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Charm Animals and Plants",
            origin="Nature Domain Cleric Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to charm animals and plants.\n"
            "As an action, you present your holy symbol and invoke the name of your deity. Each beast or plant creature that can see you within 30 feet of you must make a Wisdom saving throw. If the creature fails its saving throw, it is charmed by you for 1 minute or until it takes damage. While it is charmed by you, it is friendly to you and other creatures you designate."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "30 feet"),
            ("Target", "Beast or plant creature that can see you"),
            ("Save", "Wisdom saving throw"),
            ("Duration", "1 minute or until it takes damage"),
            ("Effect", "Charmed; friendly to you and creatures you designate"),
        ]


class DampenElements(Feature):
    def __init__(self):
        super().__init__(name="Dampen Elements", origin="Nature Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you or a creature within 30 feet of you takes acid, cold, fire, lightning, or thunder damage, you can use your reaction to grant resistance to the creature against that instance of the damage."
        return description


class DivineStrike(Feature):
    def __init__(self):
        super().__init__(name="Divine Strike", origin="Nature Domain Cleric Level 8")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain the ability to infuse your weapon strikes with divine energy. Once on each of your turns when you hit a creature with a weapon attack, you can cause the attack to deal an extra 1d8 cold, fire, or lightning damage (your choice) to the target. When you reach 14th level, the extra damage increases to 2d8."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        cleric_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.CLERIC
        )
        damage = "2d8" if cleric_level >= 14 else "1d8"
        return [
            ("Trigger", "On weapon attack hit (once per turn)"),
            ("Damage Type", "Cold, fire, or lightning (your choice)"),
            ("Damage", f"{damage} damage"),
        ]


class MasterOfNature(Feature):
    def __init__(self):
        super().__init__(name="Master of Nature", origin="Nature Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain the ability to command animals and plant creatures. While creatures are charmed by your Charm Animals and Plants feature, you can take a bonus action on your turn to verbally command what each of those creatures will do on its next turn."
        return description
