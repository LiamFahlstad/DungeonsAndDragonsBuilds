from CharacterContent.Features.Core.BaseFeatures import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class CelestialExpandedSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List", origin="The Celestial Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Celestial lets you choose from an expanded list of spells when you learn a Warlock spell. The following spells are added to the Warlock spell list for you.\n"
            "Celestial Expanded Spells\n"
            "Spell Level\tSpells\n"
            "1st\tCure Wounds, Guiding Bolt\n"
            "2nd\tFlaming Sphere, Lesser Restoration\n"
            "3rd\tDaylight, Revivify\n"
            "4th\tGuardian of Faith, Wall of Fire\n"
            "5th\tFlame Strike, Greater Restoration"
        )
        return description


class BonusCantrips(Feature):
    def __init__(self):
        super().__init__(
            name="Bonus Cantrips", origin="The Celestial Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You learn the Light and Sacred Flame cantrips. They count as Warlock cantrips for you, but they don't count against your number of cantrips known."
        return description


class HealingLight(Feature):
    def __init__(self):
        super().__init__(
            name="Healing Light",
            origin="The Celestial Patron Warlock Level 3",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, range="60 Feet"),
            usage_tags=["heal"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to channel celestial energy to heal wounds. You have a pool of d6s that you spend to fuel this healing. The number of dice in the pool equals 1 + your Warlock level.\n"
            "As a Bonus Action, you can heal one creature you can see within 60 feet of you, spending dice from the pool. The maximum number of dice you can spend at once equals your Charisma modifier (minimum of one die). Roll the dice you spend, add them together, and restore a number of Hit Points equal to the total.\n"
            "Your pool regains all expended dice when you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus Action"),
            ("Range", "60 feet"),
            ("Resource", "Pool of d6s = 1 + Warlock level"),
            ("Cost", "Up to Charisma modifier dice (min 1)"),
            ("Effect", "Heal target HP equal to dice total"),
            ("Recharge", "Long rest"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class RadiantSoul(Feature):
    def __init__(self):
        super().__init__(
            name="Radiant Soul",
            origin="The Celestial Patron Warlock Level 6",
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your link to the Celestial allows you to serve as a conduit for radiant energy. You have resistance to radiant damage, and when you cast a spell that deals radiant or fire damage, you add your Charisma modifier to one radiant or fire damage roll of that spell against one of its targets."
        return description

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class CelestialResistance(Feature):
    def __init__(self):
        super().__init__(
            name="Celestial Resistance",
            origin="The Celestial Patron Warlock Level 10",
            usage_tags=["heal"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain temporary hit points whenever you finish a Short or Long Rest. These temporary hit points equal your Warlock level + your Charisma modifier. Additionally, choose up to five creatures you can see at the end of the rest. Those creatures each gain temporary hit points equal to half your Warlock level + your Charisma modifier."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Finish short or long rest"),
            ("Your Temp HP", "Warlock level + Charisma modifier"),
            ("Others Temp HP", "Half Warlock level + Charisma modifier"),
            ("Who", "Up to 5 creatures you can see"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class SearingVengeance(Feature):
    def __init__(self):
        super().__init__(
            name="Searing Vengeance",
            origin="The Celestial Patron Warlock Level 14",
            activation=FeatureActivation(duration="Until End of Current Turn", range="30 Feet"),
            usage_tags=["heal", "damage", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The radiant energy you channel allows you to resist death. When you have to make a death saving throw at the start of your turn, you can instead spring back to your feet with a burst of radiant energy. You regain hit points equal to half your hit point maximum, and then you stand up if you so choose. Each creature of your choice that is within 30 feet of you takes radiant damage equal to 2d8 + your Charisma modifier, and is blinded until the end of the current turn.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Death saving throw at start of turn"),
            ("Effect", "Regain HP = half hit point maximum"),
            ("Action", "Stand up (optional)"),
            ("Area", "30 feet around you"),
            ("Damage", "2d8 + Charisma modifier Radiant"),
            ("Condition", "Blinded until end of current turn"),
            ("Recharge", "Long rest"),
        ]

    def target(self, character_stat_block: CharacterStatBlock) -> "FeatureTarget | None":
        return FeatureTarget.AREA
