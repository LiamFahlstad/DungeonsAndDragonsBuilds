import Core.Definitions as Definitions
from Core.Definitions import Ability, DamageType
from Model.Content.Feature import (
    ActionType,
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    RegainedOn,
)
from Model.Content.Improvements import (
    DamageResistance,
    HitPointsBonus,
    MultiAbilityArmorClass,
)
from Model.Ledger.LedgerWriter import LedgerWriter
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class DraconicSpells(Feature):
    def __init__(self):
        super().__init__(name="Draconic Spells", origin="Draconic Sorcerer Level 3")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Sorcerer level shown, you always have these spells prepared."
            ),
            Table(
                ("Sorcerer level", "Spells"),
                (
                    ("3", "Alter Self, Chromatic Orb, Command, Dragon's Breath"),
                    ("5", "Fear, Fly"),
                    ("7", "Arcane Eye, Charm Monster"),
                    ("9", "Legend Lore, Summon Dragon"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Draconic Spells table, you thereafter always have the listed spells prepared.\n"
            "Draconic Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Alter Self, Chromatic Orb, Command, Dragon's Breath\n"
            "5	Fear, Fly\n"
            "7	Arcane Eye, Charm Monster\n"
            "9	Legend Lore, Summon Dragon"
        )
        return description


class DraconicResilience(Feature):
    def __init__(self):
        super().__init__(
            name="Draconic Resilience",
            origin="Draconic Sorcerer Level 3",
            passive=True,
            usage_tags=["buff"],
        )
        self._ac = MultiAbilityArmorClass(10, [Ability.DEXTERITY, Ability.CHARISMA])

    def apply(self, ledger_writer: LedgerWriter):
        # +1 HP per Sorcerer level: a formula, since effects can't read levels.
        HitPointsBonus(
            lambda character: character.get_class_level(
                Definitions.CharacterClass.SORCERER
            )
        ).apply(ledger_writer)
        self._ac.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Your draconic gift manifests as physical traits."),
            Facts(
                (
                    (
                        "Hit Point maximum",
                        "+3 at Sorcerer level 3, and +1 for each Sorcerer level after",
                    ),
                    (
                        "Armor Class",
                        "10 + Dexterity modifier + Charisma modifier while you aren't wearing armor",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The magic in your body manifests physical traits of your draconic gift. Your Hit Point maximum increases by 3, and it increases by 1 whenever you gain another Sorcerer level.\n"
            "Parts of you are also covered by dragon-like scales. While you aren’t wearing armor, your base Armor Class equals 10 plus your Dexterity and Charisma modifiers."
        )
        return description


ELEMENTAL_AFFINITY_TYPES = [
    DamageType.ACID,
    DamageType.COLD,
    DamageType.FIRE,
    DamageType.LIGHTNING,
    DamageType.POISON,
]


class ElementalAffinity(Feature):
    def __init__(self, damage_type: DamageType):
        if damage_type not in ELEMENTAL_AFFINITY_TYPES:
            raise ValueError(
                f"Elemental Affinity must be Acid, Cold, Fire, Lightning, or Poison, not {damage_type}."
            )
        self.damage_type = damage_type
        super().__init__(
            name="Elemental Affinity",
            origin="Draconic Sorcerer Level 6",
            usage_tags=["buff", "damage"],
        )
        self._resistance = DamageResistance(damage_type)

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Damage type",
                        f"{self.damage_type.value} (chosen from Acid, Cold, Fire, Lightning or Poison)",
                    ),
                    ("Resistance", f"{self.damage_type.value} damage"),
                    (
                        "Spells",
                        f"When you cast a spell that deals {self.damage_type.value} damage, add your Charisma modifier to one of its damage rolls",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            f"Your draconic magic has an affinity with a damage type associated with dragons. Choose one of those types: Acid, Cold, Fire, Lightning, or Poison. You chose {self.damage_type.value}.\n"
            "You have Resistance to that damage type, and when you cast a spell that deals damage of that type, you can add your Charisma modifier to one damage roll of that spell."
        )
        return description


class DragonWings(Feature):
    def __init__(self):
        super().__init__(
            name="Dragon Wings",
            origin="Draconic Sorcerer Level 14",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="1 Hour"
            ),
            usage_tags=["buff", "utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Duration",
                        "1 hour, or until you dismiss them (no action required)",
                    ),
                    ("Effect", "Draconic wings give you a Fly Speed of 60 feet"),
                    (
                        "Restore",
                        "Spend 3 Sorcery Points (no action required) to regain the use",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you can cause draconic wings to appear on your back. The wings last for 1 hour or until you dismiss them (no action required). For the duration, you have a Fly Speed of 60 feet.\n"
            "Once you use this feature, you can’t use it again until you finish a Long Rest unless you spend 3 Sorcery Points (no action required) to restore your use of it."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DragonCompanion(Feature):
    def __init__(self):
        super().__init__(name="Dragon Companion", origin="Draconic Sorcerer Level 18")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spell", "Summon Dragon, without a Material component"),
                    (
                        "Free casting",
                        "Cast it once without a spell slot; regain this when you finish a Long Rest",
                    ),
                    (
                        "No Concentration",
                        "When you start casting it, you can drop its Concentration; its duration becomes 1 minute for that casting",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can cast Summon Dragon without a Material component. You can also cast it once without a spell slot, and you regain the ability to cast it in this way when you finish a Long Rest.\n"
            "Whenever you start casting the spell, you can modify it so that it doesn’t require Concentration. If you do so, the spell’s duration becomes 1 minute for that casting."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST
