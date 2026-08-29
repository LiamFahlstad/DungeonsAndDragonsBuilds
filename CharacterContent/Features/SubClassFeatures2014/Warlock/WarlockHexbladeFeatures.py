import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class HexbladeExpandedSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List", origin="Hexblade Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Hexblade lets you choose from an expanded list of spells when you learn a Warlock spell. The following spells are added to the Warlock spell list for you.\n"
            "Hexblade Expanded Spells\n"
            "Spell Level\tSpells\n"
            "1st\tShield, Wrathful Smite\n"
            "2nd\tBlur, Branding Smite\n"
            "3rd\tBlink, Elemental Weapon\n"
            "4th\tPhantasmal Killer, Staggering Smite\n"
            "5th\tBanishing Smite, Cone of Cold"
        )
        return description


class HexbladesCurse(Feature):
    def __init__(self):
        super().__init__(
            name="Hexblade's Curse",
            origin="Hexblade Patron Warlock Level 3",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="1 Minute", range="30 Feet"),
            usage_tags=["buff", "damage"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, choose one creature you can see within 30 feet of yourself. The target is cursed for 1 minute. The curse ends early if the target dies, you die, or you have the Incapacitated condition. Until the curse ends, you gain the following benefits.\n"
            "    * You gain a bonus to damage rolls against the cursed target. The bonus equals your Proficiency Bonus.\n"
            "    * Any attack roll you make against the cursed target is a Critical Hit on a roll of 19 or 20 on the d20.\n"
            "    * If the cursed target dies, you regain Hit Points equal to your Warlock level plus your Charisma modifier (minimum of 1 Hit Point).\n"
            "You can't use this feature again until you finish a Short or Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        return [
            ("Action", "Bonus Action"),
            ("Range", "30 feet"),
            (
                "Duration",
                "1 minute (ends on target death, your death, or incapacitation)",
            ),
            ("Damage Bonus", f"Proficiency bonus ({proficiency_bonus})"),
            ("Critical Hit", "On 19-20"),
            ("Target Death", "Regain HP = Warlock level + Charisma modifier (min 1)"),
            ("Recharge", "Short or long rest"),
        ]


class HexWarrior(Feature):
    def __init__(self):
        super().__init__(
            name="Hex Warrior",
            origin="Hexblade Patron Warlock Level 3",
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You acquire the training necessary to effectively arm yourself for battle. You gain proficiency with Medium Armor, Shields, and Martial weapons.\n"
            "The influence of your patron also allows you to mystically channel your will through a particular weapon. Whenever you finish a Long Rest, you can touch one weapon that you are proficient with and that lacks the Two-Handed property. When you attack with that weapon, you can use your Charisma modifier, instead of Strength or Dexterity, for the attack and damage rolls. This benefit lasts until you finish a Long Rest. If you later gain the Pact of the Blade feature, this benefit extends to every pact weapon you conjure with that feature, no matter the weapon's type."
        )
        return description


class AccursedSpecter(Feature):
    def __init__(self):
        super().__init__(
            name="Accursed Specter",
            origin="Hexblade Patron Warlock Level 6",
            activation=FeatureActivation(duration="Until End of Next Long Rest"),
            usage_tags=["damage", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can curse the soul of a person you slay, temporarily binding it in your service. When you slay a Humanoid, you can cause its spirit to rise from its corpse as a Specter. When the Specter appears, it gains Temporary Hit Points equal to half your Warlock level. Roll initiative for the Specter, which has its own turns. It obeys your verbal commands, and it gains a special bonus to its attack rolls equal to your Charisma modifier (minimum of +0).\n"
            "The Specter remains in your service until the end of your next Long Rest, at which point it vanishes to the afterlife.\n"
            "Once you bind a Specter with this feature, you can't use the feature again until you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        return [
            ("Trigger", "Slay a Humanoid"),
            ("Effect", "Specter rises from corpse"),
            ("Temp HP", f"Half Warlock level ({warlock_level // 2})"),
            ("Action", "Rolls initiative, has own turns"),
            ("Attack Bonus", "Charisma modifier (min +0)"),
            ("Duration", "Until end of next Long Rest"),
            ("Recharge", "Long rest"),
        ]


class ArmorOfHexes(Feature):
    def __init__(self):
        super().__init__(
            name="Armor of Hexes",
            origin="Hexblade Patron Warlock Level 10",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your hex grows more powerful. If the target cursed by your Hexblade's Curse hits you with an attack roll, you can use your Reaction to roll a d6. On a 4 or higher, the attack instead misses you, regardless of its roll."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Cursed creature hits you with attack roll"),
            ("Type", "Reaction"),
            ("Effect", "Roll d6; on 4+ attack misses"),
        ]


class MasterOfHexes(Feature):
    def __init__(self):
        super().__init__(
            name="Master of Hexes",
            origin="Hexblade Patron Warlock Level 14",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["control"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can spread your Hexblade's Curse from a slain creature to another creature. When the creature cursed by your Hexblade's Curse dies, you can apply the curse to a different creature you can see within 30 feet of yourself, provided you don't have the Incapacitated condition. When you apply the curse in this way, you don't regain Hit Points from the death of the previously cursed creature."
        return description
