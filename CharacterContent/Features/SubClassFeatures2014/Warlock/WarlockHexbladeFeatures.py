from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    FeatureTarget,
)
from Model.Content.Improvements import GrantArmorTraining, GrantWeaponProficiency
from CharacterContent.Items.Weapons import WeaponProficiency
from Core.Definitions import ArmorType, CharacterClass
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph


class HexbladeExpandedSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List", origin="Hexblade Patron Warlock Level 3"
        )

    def get_description(self, character: CharacterView) -> str:
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
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION,
                duration="1 Minute",
                range="30 Feet",
            ),
            usage_tags=["buff", "damage"],
            uses=FeatureUses(max_uses=1, regain_all_on="short or long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-rest box is in the panel below.
        return [
            Paragraph("Curse a foe with your patron's power."),
            Facts(
                (
                    ("Action", "Bonus Action"),
                    ("Range", "30 feet"),
                    ("Target", "One creature you can see"),
                    (
                        "Duration",
                        "1 minute; ends early if the target dies, you die, or you're Incapacitated",
                    ),
                    ("Damage", "+ Proficiency Bonus to damage rolls against it"),
                    ("Critical", "Your attack rolls against it crit on 19 or 20"),
                    (
                        "If it dies",
                        "You regain Warlock level + Charisma modifier Hit Points (minimum 1)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, choose one creature you can see within 30 feet of yourself. The target is cursed for 1 minute. The curse ends early if the target dies, you die, or you have the Incapacitated condition. Until the curse ends, you gain the following benefits.\n"
            "    * You gain a bonus to damage rolls against the cursed target. The bonus equals your Proficiency Bonus.\n"
            "    * Any attack roll you make against the cursed target is a Critical Hit on a roll of 19 or 20 on the d20.\n"
            "    * If the cursed target dies, you regain Hit Points equal to your Warlock level plus your Charisma modifier (minimum of 1 Hit Point).\n"
            "You can't use this feature again until you finish a Short or Long Rest."
        )
        level = character.get_class_level(CharacterClass.WARLOCK)
        description += f"\nRight now: +{character.get_proficiency_bonus()} damage; regain {max(1, level + character.get_charisma_modifier())} hit points when the target dies."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class HexWarrior(Feature):
    def __init__(self):
        super().__init__(
            name="Hex Warrior",
            origin="Hexblade Patron Warlock Level 3",
            usage_tags=["buff"],
        )

    def apply(self, ledger_writer: LedgerWriter):
        # "You gain proficiency with Medium Armor, Shields, and Martial weapons."
        GrantWeaponProficiency([WeaponProficiency.MARTIAL]).apply(ledger_writer)
        GrantArmorTraining([ArmorType.MEDIUM, ArmorType.SHIELD]).apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Training",
                        "Proficiency with Medium Armor, Shields and Martial weapons",
                    ),
                    (
                        "Hex weapon",
                        "After each Long Rest, touch a weapon you're proficient with that isn't Two-Handed. Until your next Long Rest, use Charisma instead of Strength or Dexterity for its attack and damage rolls.",
                    ),
                    (
                        "Pact of the Blade",
                        "If you gain it, this applies to every pact weapon you conjure, whatever its type",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You acquire the training necessary to effectively arm yourself for battle. You gain proficiency with Medium Armor, Shields, and Martial weapons.\n"
            "The influence of your patron also allows you to mystically channel your will through a particular weapon. Whenever you finish a Long Rest, you can touch one weapon that you are proficient with and that lacks the Two-Handed property. When you attack with that weapon, you can use your Charisma modifier, instead of Strength or Dexterity, for the attack and damage rolls. This benefit lasts until you finish a Long Rest. If you later gain the Pact of the Blade feature, this benefit extends to every pact weapon you conjure with that feature, no matter the weapon's type."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class AccursedSpecter(Feature):
    def __init__(self):
        super().__init__(
            name="Accursed Specter",
            origin="Hexblade Patron Warlock Level 6",
            activation=FeatureActivation(duration="Until End of Next Long Rest"),
            usage_tags=["damage", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph("Bind the soul of a humanoid you slay."),
            Facts(
                (
                    ("Trigger", "You slay a Humanoid"),
                    (
                        "Specter",
                        "Its spirit rises as a Specter with half your Warlock level in Temporary Hit Points",
                    ),
                    (
                        "In combat",
                        "Roll initiative for it; it takes its own turns and obeys your verbal commands",
                    ),
                    (
                        "Attack bonus",
                        "+ Charisma modifier (minimum +0) to its attack rolls",
                    ),
                    ("Lasts", "Until the end of your next Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can curse the soul of a person you slay, temporarily binding it in your service. When you slay a Humanoid, you can cause its spirit to rise from its corpse as a Specter. When the Specter appears, it gains Temporary Hit Points equal to half your Warlock level. Roll initiative for the Specter, which has its own turns. It obeys your verbal commands, and it gains a special bonus to its attack rolls equal to your Charisma modifier (minimum of +0).\n"
            "The Specter remains in your service until the end of your next Long Rest, at which point it vanishes to the afterlife.\n"
            "Once you bind a Specter with this feature, you can't use the feature again until you finish a Long Rest."
        )
        level = character.get_class_level(CharacterClass.WARLOCK)
        description += f"\nRight now: {level // 2} temporary hit points, +{max(0, character.get_charisma_modifier())} to its attack rolls."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class ArmorOfHexes(Feature):
    def __init__(self):
        super().__init__(
            name="Armor of Hexes",
            origin="Hexblade Patron Warlock Level 10",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "Your hex grows more powerful. If the target cursed by your Hexblade's Curse hits you with an attack roll, you can use your Reaction to roll a d6. On a 4 or higher, the attack instead misses you, regardless of its roll."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class MasterOfHexes(Feature):
    def __init__(self):
        super().__init__(
            name="Master of Hexes",
            origin="Hexblade Patron Warlock Level 14",
            activation=FeatureActivation(range="30 Feet"),
            usage_tags=["control"],
        )

    def get_description(self, character: CharacterView) -> str:
        description = "You can spread your Hexblade's Curse from a slain creature to another creature. When the creature cursed by your Hexblade's Curse dies, you can apply the curse to a different creature you can see within 30 feet of yourself, provided you don't have the Incapacitated condition. When you apply the curse in this way, you don't regain Hit Points from the death of the previously cursed creature."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
