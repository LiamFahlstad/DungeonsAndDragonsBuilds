import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
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
        super().__init__(
            name="Eyes of Night",
            origin="Twilight Domain Cleric Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Hour", range="10 Feet"),
            usage_tags=["utility"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can see through the deepest gloom. You have darkvision out to a range of 300 feet. In that radius, you can see in dim light as if it were bright light and in darkness as if it were dim light.\n"
            "As an action, you can magically share the darkvision of this feature with willing creatures you can see within 10 feet of you, up to a number of creatures equal to your Wisdom modifier (minimum of one creature). The shared darkvision lasts for 1 hour. Once you share it, you can't do so again until you finish a long rest, unless you expend a spell slot of any level to share it again."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        wis_mod = character_stat_block.get_wisdom_modifier()
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
        super().__init__(
            name="Vigilant Blessing",
            origin="Twilight Domain Cleric Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The night has taught you to be vigilant. As an action, you give one creature you touch (including possibly yourself) advantage on the next initiative roll the creature makes. This benefit ends immediately after the roll or if you use this feature again."
        return description


class TwilightSanctuaryChannelDivinity(Feature):
    def __init__(self):
        super().__init__(
            name="Channel Divinity: Twilight Sanctuary",
            origin="Twilight Domain Cleric Level 3",
            activation=FeatureActivation(action_type=ActionType.ACTION, duration="1 Minute or Until You Are Incapacitated or Die", range="Self (30-Foot-Radius Sphere)"),
            usage_tags=["heal", "buff"],
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
        super().__init__(
            name="Steps of Night",
            origin="Twilight Domain Cleric Level 6",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="1 Minute"),
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=Definitions.MAX_PROFICIENCY_BONUS, regain_all_on="long rest", current_formula="Current amount: equal to your proficiency bonus."))

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can draw on the mystical power of night to rise into the air. As a bonus action when you are in dim light or darkness, you can magically give yourself a flying speed equal to your walking speed for 1 minute. You regain all expended uses when you finish a long rest."
        )
        return description