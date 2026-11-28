from Model.Content.CombatAdjustments import (
    Adjustment,
    AddToOneDamageRoll,
    Applies,
    Rows,
    Spells,
)
from Core.Definitions import DamageType
import Core.Definitions as Definitions
from Model.Content.CombatEffect import (
    CombatDamage,
    CombatEffect,
    CombatHitPoints,
    CombatTargets,
)
from Model.Content.Feature import (
    Feature,
    FeatureUses,
    FeatureActivation,
    ActionType,
    RegainedOn,
    FeatureTarget,
)
from Model.Content.Improvements import DamageResistance
from Model.Ledger.LedgerWriter import LedgerWriter
from Core.Rules import levels_gained
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Paragraph, Table


class CelestialSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Celestial Spells", origin="Celestial Patron Warlock Level 3"
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Warlock level shown, you always have these spells prepared."
            ),
            Table(
                ("Warlock level", "Spells"),
                (
                    (
                        "3",
                        "Aid, Cure Wounds, Guiding Bolt, Lesser Restoration, Light, Sacred Flame",
                    ),
                    ("5", "Daylight, Revivify"),
                    ("7", "Guardian of Faith, Wall of Fire"),
                    ("9", "Greater Restoration, Summon Celestial"),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "The magic of your patron ensures you always have certain spells ready; when you reach a Warlock level specified in the Celestial Spells table, you thereafter always have the listed spells prepared."
        return description

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # Its spells are in the picker as spells.
        return []


class HealingLight(Feature):
    def __init__(self):
        super().__init__(
            name="Healing Light",
            origin="Celestial Patron Warlock Level 3",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="60 Feet"
            ),
            usage_tags=["heal"],
            # The pool of d6s: 1 plus your Warlock level.
            uses=FeatureUses(
                max_uses=21,
                regain_all_on="long rest",
                current_formula="Current amount: 1 plus your Warlock level (d6s).",
                gained_at=levels_gained(lambda level: 1 + level, from_level=3),
            ),
        )

    def number_of_uses(self, character: CharacterView) -> int:
        return 1 + character.get_class_level(Definitions.CharacterClass.WARLOCK)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Channel celestial energy to heal wounds."),
            Facts(
                (
                    (
                        "Pool",
                        "1 + Warlock level d6s; regain all when you finish a Long Rest",
                    ),
                    ("Action", "Bonus Action"),
                    ("Range", "60 feet"),
                    ("Target", "You or one creature you can see"),
                    (
                        "Spend",
                        "Up to Charisma modifier (minimum one) dice from the pool; the target regains Hit Points equal to the total rolled",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the ability to channel celestial energy to heal wounds. You have a pool of d6s to fuel this healing. The number of dice in the pool equals 1 plus your Warlock level.\n"
            "As a Bonus Action, you can heal yourself or one creature you can see within 60 feet of yourself, expending dice from the pool. The maximum number of dice you can expend at once equals your Charisma modifier (minimum of one die). Roll the dice you expend, and restore a number of Hit Points equal to the roll's total. Your pool regains all expended dice when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # How many dice to spend is the player's choice: a row per count, up
        # to the Charisma modifier (minimum one), each spending that many
        # dice from the pool.
        most = max(1, character.get_charisma_modifier())
        return [
            CombatEffect(
                name=f"Healing Light: {count}d6",
                healing=CombatHitPoints(f"{count}d6"),
                targets=CombatTargets(1),
                uses_spent=count,
                notes=("The target can be you, or a creature you can see.",),
            )
            for count in range(1, most + 1)
        ]


class RadiantSoul(Feature):
    def __init__(self):
        super().__init__(
            name="Radiant Soul",
            origin="Celestial Patron Warlock Level 6",
            usage_tags=["buff", "damage"],
        )
        self._resistance = DamageResistance(DamageType.RADIANT)

    def apply(self, ledger_writer: LedgerWriter):
        self._resistance.apply(ledger_writer)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Resistance", "Radiant damage"),
                    (
                        "Damage",
                        "Once per turn, when a spell you cast deals Radiant or Fire damage, add your Charisma modifier to its damage against one of its targets",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "Your link to your patron allows you to serve as a conduit for radiant energy. You have Resistance to Radiant damage. Once per turn, when a spell you cast deals Radiant or Fire damage, you can add your Charisma modifier to that spell's damage against one of the spell's targets."
        return description

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # The Resistance is on the sheet; the damage is added to the spells'
        # rows (combat_adjustments).
        return []

    def combat_adjustments(self, character: CharacterView) -> tuple[Adjustment, ...]:
        # A spell (or a feature's casting of one) that deals Radiant or Fire
        # damage, on any turn: once per turn and against one of its targets,
        # which the GM picks, of the type the spell deals.
        types = (DamageType.RADIANT, DamageType.FIRE)
        bonus = AddToOneDamageRoll(
            character.get_charisma_modifier(),
            types,
            when="you add Radiant Soul to this target (once per turn, one target)",
        )
        applies = Applies(spells=Spells(), deals=types, rows=Rows.ALL)
        return (Adjustment(applies, (bonus,)),)


class CelestialResilience(Feature):
    untriggered = "Magical Cunning's 1-minute rite and the rests happen outside the fight: pick it as the fight starts."

    def __init__(self):
        super().__init__(
            name="Celestial Resilience",
            origin="Celestial Patron Warlock Level 10",
            usage_tags=["heal"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You use Magical Cunning or finish a Short or Long Rest",
                    ),
                    ("You", "Warlock level + Charisma modifier Temporary Hit Points"),
                    (
                        "Others",
                        "Up to five creatures you can see each gain half your Warlock level + Charisma modifier Temporary Hit Points",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You gain Temporary Hit Points whenever you use your Magical Cunning feature or finish a Short or Long Rest. These Temporary Hit Points equal your Warlock level plus your Charisma modifier. Additionally, choose up to five creatures you can see when you gain the points. Those creatures each gain Temporary Hit Points equal to half your Warlock level plus your Charisma modifier."
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def combat_effects(self, character: CharacterView) -> list[CombatEffect]:
        # An extension of Magical Cunning: gaining the points spends none of
        # its uses (the rite or the rest does).
        level = character.get_class_level(Definitions.CharacterClass.WARLOCK)
        charisma = character.get_charisma_modifier()
        when = (
            "When you use Magical Cunning or finish a Short or Long Rest: pick"
            " it as the fight starts if one came just before."
        )
        return [
            CombatEffect(
                name="Celestial Resilience: you",
                temp_hp=CombatHitPoints(str(max(0, level + charisma))),
                targets_self=True,
                spends_use=False,
                notes=(when,),
            ),
            CombatEffect(
                name="Celestial Resilience: others",
                temp_hp=CombatHitPoints(str(max(0, level // 2 + charisma))),
                targets=CombatTargets(5),
                spends_use=False,
                notes=(
                    "Up to five creatures you can see as you gain your own"
                    " points (Celestial Resilience: you).",
                ),
            ),
        ]


class SearingVengeance(Feature):
    def __init__(self):
        super().__init__(
            name="Searing Vengeance",
            origin="Celestial Patron Warlock Level 14",
            activation=FeatureActivation(range="60 Feet"),
            usage_tags=["heal", "damage", "control"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    (
                        "Trigger",
                        "You or an ally within 60 feet is about to make a Death Saving Throw",
                    ),
                    (
                        "Revive",
                        "It regains half its Hit Point maximum and can end the Prone condition on itself",
                    ),
                    (
                        "Burst",
                        "Each creature of your choice within 30 feet of it takes 2d8 + Charisma modifier Radiant damage and is Blinded until the end of the turn",
                    ),
                    ("Limit", "Once per Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you or an ally within 60 feet of you is about to make a Death Saving Throw, you can unleash radiant energy to save the creature. The creature regains Hit Points equal to half its Hit Point maximum and can end the Prone condition on itself. Each creature of your choice that is within 30 feet of the creature takes Radiant damage equal to 2d8 plus your Charisma modifier, and each has the Blinded condition until the end of the current turn.\n"
            "Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY
