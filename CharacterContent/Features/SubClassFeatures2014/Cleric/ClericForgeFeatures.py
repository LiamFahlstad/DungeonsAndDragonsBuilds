import Core.Definitions as Definitions
from Core.Definitions import DamageType
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import DamageImmunity, DamageResistance
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Proficiencies", origin="Forge Domain Cleric Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with heavy armor and smith's tools."
        return description


class BlessingOfTheForge(Feature):
    def __init__(self):
        super().__init__(name="Blessing of the Forge", origin="Forge Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to imbue magic into a weapon or armor. At the end of a long rest, you can touch one nonmagical object that is a suit of armor or a simple or martial weapon. Until the end of your next long rest or until you die, the object becomes a magic item, granting a +1 bonus to AC if it's armor or a +1 bonus to attack and damage rolls if it's a weapon.\n"
            "Once you use this feature, you can't use it again until you finish a long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "At end of long rest"),
            ("Action", "Touch"),
            ("Target", "One nonmagical armor or weapon"),
            ("Bonus", "+1 to AC (armor) or +1 to attack and damage (weapon)"),
            ("Duration", "Until end of next long rest or until you die"),
            ("Uses", "1"),
            ("Recharge", "Long rest"),
        ]


class ForgeDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Forge Domain Spells", origin="Forge Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Forge Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Forge Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tIdentify, Searing Smite\n"
            "3rd\tHeat Metal, Magic Weapon\n"
            "5th\tElemental Weapon, Protection from Energy\n"
            "7th\tFabricate, Wall of Fire\n"
            "9th\tAnimate Objects, Creation"
        )
        return description


class ArtisansBlessingChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Artisan's Blessing",
            origin="Forge Domain Cleric Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to create simple items.\n"
            "You conduct an hour-long ritual that crafts a nonmagical item that must include some metal: a simple or martial weapon, a suit of armor, ten pieces of ammunition, a set of tools, or another metal object. The creation is completed at the end of the hour, coalescing in an unoccupied space of your choice on a surface within 5 feet of you.\n"
            "The thing you create can be something that is worth no more than 100 gp. As part of this ritual, you must lay out metal, which can include coins, with a value equal to the creation. The metal irretrievably coalesces and transforms into the creation at the ritual's end, magically forming even nonmetal parts of the creation.\n"
            "The ritual can create a duplicate of a nonmagical item that contains metal, such as a key, if you possess the original during the ritual."
        )
        return description


class SoulOfTheForge(Feature):
    def __init__(self):
        super().__init__(name="Soul of the Forge", origin="Forge Domain Cleric Level 6", skippable_in_concise=True)
        self._resistance = DamageResistance(DamageType.FIRE, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._resistance.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your mastery of the forge grants you special abilities.\n"
            "You gain resistance to fire damage.\n"
            "While wearing heavy armor, you gain a +1 bonus to AC."
        )
        return description


class DivineStrike(Feature):
    def __init__(self):
        super().__init__(name="Divine Strike", origin="Forge Domain Cleric Level 8")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to infuse your weapon strikes with the fiery power of the forge. Once on each of your turns when you hit a creature with a weapon attack, you can cause the attack to deal an extra 1d8 fire damage to the target. When you reach 14th level, the extra damage increases to 2d8."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        import Core.Definitions as Definitions
        cleric_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.CLERIC
        )
        damage = "2d8" if cleric_level >= 14 else "1d8"
        return [
            ("Trigger", "On weapon attack hit (once per turn)"),
            ("Damage Type", "Fire"),
            ("Damage", f"{damage} fire"),
        ]


class SaintOfForgeAndFire(Feature):
    def __init__(self):
        super().__init__(
            name="Saint of Forge and Fire", origin="Forge Domain Cleric Level 17", skippable_in_concise=True
        )
        # Only the fire immunity is unconditional; the bludgeoning/piercing/
        # slashing resistance is gated on wearing heavy armor AND only
        # applies to nonmagical attacks (no magical/nonmagical qualifier
        # exists on DamageResistance), so it stays prose-only.
        self._immunity = DamageImmunity(DamageType.FIRE, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._immunity.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your blessed affinity with fire and metal becomes more powerful.\n"
            "You gain immunity to fire damage.\n"
            "While wearing heavy armor, you have resistance to bludgeoning, piercing, and slashing damage from nonmagical attacks."
        )
        return description
