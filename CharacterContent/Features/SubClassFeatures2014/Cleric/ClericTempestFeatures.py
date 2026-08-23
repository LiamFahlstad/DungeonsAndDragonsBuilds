import Core.Definitions as Definitions
from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiencies", origin="Tempest Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with martial weapons and heavy armor."
        return description


class WrathOfTheStorm(Feature):
    def __init__(self):
        super().__init__(
            name="Wrath of the Storm",
            origin="Tempest Domain Cleric Level 3",
            action_type="reaction",
            range="5 Feet",
            usage_tags=["damage"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wis_mod)
        description = (
            "You can thunderously rebuke attackers. When a creature within 5 feet of you that you can see hits you with an attack, you can use your reaction to cause the creature to make a Dexterity saving throw. The creature takes 2d8 lightning or thunder damage (your choice) on a failed saving throw, and half as much damage on a successful one.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (a minimum of once). You regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wis_mod)
        return [
            ("Trigger", "When creature within 5 feet hits you with attack"),
            ("Action", "Reaction"),
            ("Save", "Dexterity saving throw"),
            ("Damage (Failed)", "2d8 lightning or thunder (your choice)"),
            ("Damage (Successful)", "Half damage"),
            ("Uses", f"Wisdom modifier (minimum 1) – {uses}"),
            ("Recharge", "Long rest"),
        ]


class TempestDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Tempest Domain Spells", origin="Tempest Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Tempest Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Tempest Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tFog Cloud, Thunderwave\n"
            "3rd\tGust of Wind, Shatter\n"
            "5th\tCall Lightning, Sleet Storm\n"
            "7th\tControl Water, Ice Storm\n"
            "9th\tDestructive Wave, Insect Plague"
        )
        return description


class DestructiveWrathChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Destructive Wrath",
            origin="Tempest Domain Cleric Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can use your Channel Divinity to wield the power of the storm with unchecked ferocity.\nWhen you roll lightning or thunder damage, you can use your Channel Divinity to deal maximum damage, instead of rolling."
        return description


class ThunderousStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Thunderous Strike",
            origin="Tempest Domain Cleric Level 6",
            range="10 Feet",
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you deal lightning damage to a Large or smaller creature, you can also push it up to 10 feet away from you."
        return description


class DivineStrike(Feature):
    def __init__(self):
        super().__init__(name="Divine Strike", origin="Tempest Domain Cleric Level 8", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain the ability to infuse your weapon strikes with divine energy. Once on each of your turns when you hit a creature with a weapon attack, you can cause the attack to deal an extra 1d8 thunder damage to the target. When you reach 14th level, the extra damage increases to 2d8."
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
            ("Damage Type", "Thunder"),
            ("Damage", f"{damage} thunder"),
        ]


class Stormborn(Feature):
    def __init__(self):
        super().__init__(name="Stormborn", origin="Tempest Domain Cleric Level 17", usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have a flying speed equal to your current walking speed whenever you are not underground or indoors."
        return description
