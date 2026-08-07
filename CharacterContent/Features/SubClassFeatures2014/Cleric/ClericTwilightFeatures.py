import Core.Definitions as Definitions
from Core.Definitions import Ability
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class BonusProficiencies(Feature):
    def __init__(self):
        super().__init__(name="Bonus Proficiencies", origin="Twilight Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain proficiency with martial weapons and heavy armor."
        return description


class TwilightDomainSpells(Feature):
    def __init__(self):
        super().__init__(name="Twilight Domain Spells", origin="Twilight Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your connection to this divine domain ensures you always have certain spells ready. When you reach a Cleric level specified in the Twilight Domain Spells table, you thereafter always have the listed spells prepared.\n"
            "Twilight Domain Spells\n"
            "Cleric Level\tSpells\n"
            "1st\tFaerie Fire, Sleep\n"
            "3rd\tMoonbeam, See Invisibility\n"
            "5th\tAura of Vitality, Leomund's Tiny Hut\n"
            "7th\tAura of Life, Greater Invisibility\n"
            "9th\tCircle of Power, Mislead"
        )
        return description


class EyesOfNight(Feature):
    def __init__(self):
        super().__init__(name="Eyes of Night", origin="Twilight Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        creatures = max(1, wis_mod)
        description = (
            "You can see through the deepest gloom. You have darkvision out to a range of 300 feet. In that radius, you can see in dim light as if it were bright light and in darkness as if it were dim light.\n"
            f"As an action, you can magically share the darkvision of this feature with willing creatures you can see within 10 feet of you, up to a number of creatures equal to your Wisdom modifier (minimum of one creature, {creatures}). The shared darkvision lasts for 1 hour. Once you share it, you can't do so again until you finish a long rest, unless you expend a spell slot of any level to share it again."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wis_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        creatures = max(1, wis_mod)
        return [
            ("Personal Darkvision", "300 feet"),
            ("Action", "Action"),
            ("Sharing Range", "10 feet"),
            ("Targets to Share", f"Wisdom modifier (minimum 1) – {creatures}"),
            ("Shared Duration", "1 hour"),
            ("Recharge", "Long rest (or expend a spell slot)"),
        ]


class VigilantBlessing(Feature):
    def __init__(self):
        super().__init__(name="Vigilant Blessing", origin="Twilight Domain Cleric Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The night has taught you to be vigilant. As an action, you give one creature you touch (including possibly yourself) advantage on the next initiative roll the creature makes. This benefit ends immediately after the roll or if you use this feature again."
        return description


class TwilightSanctuaryChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Twilight Sanctuary",
            origin="Twilight Domain Cleric Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can use your Channel Divinity to refresh your allies with soothing twilight.\n"
            "As an action, you present your holy symbol, and a sphere of twilight emanates from you. The sphere is centered on you, has a 30-foot radius, and is filled with dim light. The sphere moves with you, and it lasts for 1 minute or until you are incapacitated or die. Whenever a creature (including you) ends its turn in the sphere, you can grant that creature one of these benefits:\n"
            "    * You grant it temporary hit points equal to 1d6 plus your cleric level.\n"
            "    * You end one effect on it causing it to be charmed or frightened."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Area", "30-foot radius sphere centered on you"),
            ("Light", "Dim light"),
            ("Movement", "Moves with you"),
            ("Duration", "1 minute or until you are incapacitated or die"),
            ("Effect per Turn", "Choose: grant 1d6 + cleric level temp HP, or remove charmed/frightened"),
        ]


class StepsOfNight(Feature):
    def __init__(self):
        super().__init__(name="Steps of Night", origin="Twilight Domain Cleric Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "You can draw on the mystical power of night to rise into the air. As a bonus action when you are in dim light or darkness, you can magically give yourself a flying speed equal to your walking speed for 1 minute. You can use this bonus action a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return [
            ("Action", "Bonus action"),
            ("Condition", "In dim light or darkness"),
            ("Effect", "Flying speed = walking speed"),
            ("Duration", "1 minute"),
            ("Uses", f"Proficiency bonus ({proficiency_bonus})"),
            ("Recharge", "Long rest"),
        ]


class DivineStrike(Feature):
    def __init__(self):
        super().__init__(name="Divine Strike", origin="Twilight Domain Cleric Level 8")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain the ability to infuse your weapon strikes with divine energy. Once on each of your turns when you hit a creature with a weapon attack, you can cause the attack to deal an extra 1d8 radiant damage. When you reach 14th level, the extra damage increases to 2d8."
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
            ("Damage Type", "Radiant"),
            ("Damage", f"{damage} radiant"),
        ]


class TwilightShroud(Feature):
    def __init__(self):
        super().__init__(name="Twilight Shroud", origin="Twilight Domain Cleric Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The twilight that you summon offers a protective embrace: you and your allies have half cover while in the sphere created by your Twilight Sanctuary."
        return description
