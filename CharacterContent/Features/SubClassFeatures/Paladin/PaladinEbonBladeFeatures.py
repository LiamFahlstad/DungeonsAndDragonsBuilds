from Core.Definitions import DamageType
from Core.Rules import MAX_ABILITY_MODIFIER
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
from Model.View import CharacterView
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table

# The source text grants Death Coil at Paladin level 1 and Runic Smite at
# level 2; subclasses start at level 3 here, so both come with the level-3
# grant.

_ORIGIN_3 = "Oath of the Ebon Blade Paladin Level 3"


class DeathCoil(Feature):
    def __init__(self):
        super().__init__(
            name="Death Coil",
            origin=_ORIGIN_3,
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, range="60 Feet"
            ),
            usage_tags=["damage", "heal"],
            uses=FeatureUses(
                max_uses=1 + MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: one plus your Charisma modifier (minimum of one die).",
            ),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, 1 + character.get_charisma_modifier())

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The pool's d8s are the boxes in the panel below.
        return [
            Paragraph(
                "Replaces Lay On Hands. Your creature type becomes Undead, and you manipulate negative energy."
            ),
            Facts(
                (
                    ("Pool", "d8s equal to 1 + your Charisma modifier (minimum 1)"),
                    ("Action", "Bonus Action"),
                    ("Range", "60 feet, a creature you can see"),
                    (
                        "Dice per use",
                        "Up to your Charisma modifier (minimum 1) from the pool",
                    ),
                    (
                        "Save",
                        "Constitution: Necrotic damage equal to the roll, half on a success",
                    ),
                    (
                        "Undead target",
                        "You can have it regain Hit Points equal to the roll instead",
                    ),
                    ("Recharge", "All dice on a Long Rest"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "This feature replaces the Lay On Hands feature of the Paladin class.\n"
            "Your creature type becomes Undead.\n"
            "You also gain the ability to manipulate negative energy. You have a pool of d8s to fuel this ability. The number of dice in the pool equals one plus your Charisma modifier (minimum of one die).\n"
            "As a Bonus Action, you can target a creature you can see within 60 feet of yourself and force it to make a Constitution saving throw, expending dice from the pool. The maximum number of dice you can expend at once equals your Charisma modifier (minimum of one die). Roll the dice you expend. The target takes Necrotic damage equal to the roll's total on a failed save or half as much damage on a successful one. If the target is an Undead, you can choose to have it regain Hit Points equal to the roll's total instead. Your pool regains all expended dice when you finish a Long Rest."
        )
        return description


class RunicSmite(Feature):
    # Rune Strike is a World of Warcraft spell that isn't in the spell data
    # yet, so this doesn't declare it in granted_spells().
    def __init__(self):
        super().__init__(
            name="Runic Smite",
            origin=_ORIGIN_3,
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Replaces Paladin's Smite."),
            Facts(
                (
                    ("Always prepared", "Rune Strike"),
                    (
                        "Free casting",
                        "Cast it once without a spell slot; regain this when you finish a Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "This feature replaces the Paladin's Smite feature of the Paladin class.\n"
            "You always have the Rune Strike spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest."
        )
        return description


class EbonBladeSpells(Feature):
    def __init__(self):
        super().__init__(name="Oath of the Ebon Blade Spells", origin=_ORIGIN_3)

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "From the Paladin level shown, you always have the Spells (All) prepared, plus the spells in the column of the rune inscribed on your weapon, if any."
            ),
            Table(
                ("Paladin level", "All", "Blood", "Frost", "Unholy"),
                (
                    (
                        "3",
                        "Death Grip",
                        "Vampiric Blood",
                        "Chains of Ice",
                        "Scourge Strike",
                    ),
                    (
                        "5",
                        "Death and Decay",
                        "Spiritual Weapon",
                        "Frostscythe",
                        "Ray of Enfeeblement",
                    ),
                    (
                        "9",
                        "Summon Undead",
                        "Leeching Strike",
                        "Remorseless Winter",
                        "Bestow Curse",
                    ),
                    (
                        "13",
                        "Freedom of Movement",
                        "Evard's Black Tentacles",
                        "Ice Storm",
                        "Blight",
                    ),
                    (
                        "17",
                        "Circle of Power",
                        "Bonestorm",
                        "Cone of Cold",
                        "Contagion",
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "The magic of your oath and your Runeforging feature ensure you always have certain spells ready; when you reach a Paladin level specified in the Oath of the Ebon Blade Spells table, you thereafter always have the spell in the Spells (All) column prepared. You also have the additional spells listed in the column matching the rune you have inscribed on your weapon, if any.\n"
            "Oath of the Ebon Blade Spells\n"
            "Paladin Level\tSpells (All)\tSpells (Blood)\tSpells (Frost)\tSpells (Unholy)\n"
            "3\tDeath Grip\tVampiric Blood\tChains of Ice\tScourge Strike\n"
            "5\tDeath and Decay\tSpiritual Weapon\tFrostscythe\tRay of Enfeeblement\n"
            "9\tSummon Undead\tLeeching Strike\tRemorseless Winter\tBestow Curse\n"
            "13\tFreedom of Movement\tEvard's Black Tentacles\tIce Storm\tBlight\n"
            "17\tCircle of Power\tBonestorm\tCone of Cold\tContagion"
        )
        return description


class Runeforging(Feature):
    def __init__(self):
        super().__init__(
            name="Runeforging",
            origin=_ORIGIN_3,
            usage_tags=["heal", "damage"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph(
                "When you finish a Long Rest, inscribe one rune on a melee weapon you are holding, or transfer it to a different weapon. Whenever you gain a level, you can replace it with a different rune."
            ),
            Option(
                "Blood",
                (
                    Facts(
                        (
                            (
                                "Temporary Hit Points",
                                "Charisma modifier + Paladin level, when you inscribe the rune and whenever you finish a Long Rest with it inscribed",
                            ),
                            (
                                "Again",
                                "Whenever you reduce an enemy to 0 Hit Points while wielding the weapon",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Frost",
                (
                    Facts(
                        (
                            (
                                "Ignore Resistance",
                                "Cold damage from your weapon attacks, Paladin spells and Paladin features",
                            ),
                            (
                                "Light extra attack",
                                "On a hit, an extra 1d4 Cold damage",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Unholy",
                (
                    Facts(
                        (
                            (
                                "Ignore Resistance",
                                "Necrotic damage from your weapon attacks, Paladin spells and Paladin features",
                            ),
                            (
                                "Heavy weapon",
                                "The first creature you hit with it each turn takes extra Necrotic damage equal to your Charisma modifier (minimum 1)",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you finish a Long Rest, you can inscribe one of the following runes on a melee weapon you are holding, or you can transfer the rune to a different weapon. Whenever you gain a level, you can replace it with a different rune.\n"
            "Blood. When you inscribe this rune on your weapon, and whenever you finish a Long Rest while the rune is inscribed on your weapon, you gain Temporary Hit Points equal to your Charisma modifier plus your Paladin level. While you are wielding your inscribed weapon, you gain these Temporary Hit Points whenever you reduce an enemy to 0 Hit Points.\n"
            "Frost. While you are wielding your inscribed weapon, damage from your weapon attacks, Paladin spells, and Paladin features ignores Resistance to Cold damage. When you make the extra attack of the Light property and hit while wielding your inscribed weapon, you deal an extra 1d4 Cold damage.\n"
            "Unholy. While you are wielding your inscribed weapon, damage from your weapon attacks, Paladin spells, and Paladin features ignores Resistance to Necrotic damage. If your inscribed weapon has the Heavy property, the first creature you hit with it each turn takes extra Necrotic damage equal to your Charisma modifier (minimum of 1)."
        )
        return description


class RunicPower(Feature):
    def __init__(self):
        super().__init__(
            name="Runic Power",
            origin=_ORIGIN_3,
            usage_tags=["heal", "damage", "control"],
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Trigger", "Immediately after you cast Rune Strike"),
                    ("Cost", "One use of Channel Divinity"),
                    ("Effect", "Depends on the rune inscribed on your weapon"),
                )
            ),
            Option(
                "Blood",
                (
                    Facts(
                        (
                            (
                                "Heal",
                                "Regain Hit Points equal to the Necrotic damage dealt with your Rune Strike",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Frost",
                (
                    Facts(
                        (
                            (
                                "Damage",
                                "2d6 Cold to the target and each enemy in a 10-foot Emanation from it",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Unholy",
                (
                    Facts(
                        (
                            ("Duration", "Until the end of your next turn"),
                            (
                                "Curse",
                                "The target's next saving throw subtracts 1d6, then the curse ends",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Immediately after you cast Rune Strike, you can expend one use of your Channel Divinity to gain one of the following benefits based on the rune inscribed on your weapon.\n"
            "Blood. You regain a number of Hit Points equal to the Necrotic damage dealt with your Rune Strike.\n"
            "Frost. Frost covers your weapon and shatters on impact. The target of your Rune Strike and each enemy in a 10-foot Emanation originating from the target take 2d6 Cold damage.\n"
            "Unholy. The target of your Rune Strike is cursed until the end of your next turn. The next time the cursed target makes a saving throw, it subtracts 1d6 from the roll, and the curse ends."
        )
        return description


class UndeadSteed(Feature):
    # The source text calls this "Faithful Steed"; it extends the base
    # feature of that name, so it gets a distinct card title.
    def __init__(self):
        super().__init__(
            name="Undead Steed",
            origin="Oath of the Ebon Blade Paladin Level 5",
            usage_tags=["utility"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Ghostly Stride's once-per-Long-Rest box is in the panel below.
        return [
            Paragraph(
                "When you cast Find Steed, the Otherworldly Steed can be Undead."
            ),
            Facts(
                (
                    ("Otherworldly Slam", "Deals Necrotic damage"),
                    (
                        "Ghostly Stride",
                        "Bonus Action, once per Long Rest: the steed and its rider move through creatures and objects this turn as if they were Difficult Terrain",
                    ),
                    (
                        "Ending inside an object",
                        "Steed and rider each take 5 (1d10) Force damage",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "In addition to the benefits of the Paladin's Faithful Steed feature, when you cast Find Steed, the Otherworldly Steed can be Undead. An Undead steed deals Necrotic damage with its Otherworldly Slam action and has this Bonus Action:\n"
            "Ghostly Stride (Undead Only; Recharges After a Long Rest). The steed and its rider can move through other creatures and objects this turn as if they were Difficult Terrain. Both steed and rider take 5 (1d10) Force damage if they end their turn inside an object."
        )
        return description


class AuraOfDeathlyEndurance(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Deathly Endurance",
            origin="Oath of the Ebon Blade Paladin Level 7",
            usage_tags=["buff"],
        )
        self._resistances = [
            DamageResistance(DamageType.COLD),
            DamageResistance(DamageType.NECROTIC),
            DamageResistance(DamageType.PSYCHIC),
        ]

    def apply(self, ledger_writer: LedgerWriter):
        # You are always in your own aura; the allies' share is situational.
        for resistance in self._resistances:
            resistance.apply(ledger_writer)

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Who", "You and your allies in your Aura of Protection"),
                    ("Resistance", "Cold, Necrotic and Psychic damage"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = "You and your allies have Resistance to Cold, Necrotic, and Psychic damage while in your Aura of Protection."
        return description


class RunicStrikes(Feature):
    def __init__(self):
        super().__init__(
            name="Runic Strikes",
            origin="Oath of the Ebon Blade Paladin Level 11",
            usage_tags=["damage"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Replaces Radiant Strikes."),
            Facts(
                (
                    (
                        "Trigger",
                        "You hit with an attack roll using a Melee weapon or an Unarmed Strike",
                    ),
                    ("Extra damage", "1d8 Necrotic"),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "This feature replaces the Paladin's Radiant Strikes feature.\n"
            "When you hit a target with an attack roll using a Melee weapon or an Unarmed Strike, the target takes an extra 1d8 Necrotic damage."
        )
        return description


class ImprovedDeathCoil(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Death Coil",
            origin="Oath of the Ebon Blade Paladin Level 14",
            usage_tags=["damage", "heal"],
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.CREATURE

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Replaces Restoring Touch."),
            Facts(
                (
                    (
                        "Damage",
                        "Extra Necrotic damage equal to your Charisma modifier (minimum 1), whether or not the target fails its save",
                    ),
                    (
                        "Undead healing",
                        "Regains extra Hit Points equal to your Paladin level",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "This feature replaces the Paladin's Restoring Touch feature.\n"
            "When you use Death Coil to deal damage, the target takes extra Necrotic damage equal to your Charisma modifier (minimum of 1) whether or not it fails its saving throw. If the target is an Undead, and you have it regain Hit Points, it regains additional Hit Points equal to your Paladin level."
        )
        return description


class RunicMastery(Feature):
    def __init__(self):
        super().__init__(
            name="Runic Mastery",
            origin="Oath of the Ebon Blade Paladin Level 15",
            usage_tags=["buff", "damage"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Paragraph(
                "Invoke the power of the rune inscribed on your weapon. The effect depends on the rune."
            ),
            Option(
                "Blood",
                (
                    Facts(
                        (
                            ("Action", "Reaction"),
                            (
                                "Trigger",
                                "A creature hits another creature you can see within 10 feet of you with an attack roll",
                            ),
                            (
                                "Effect",
                                "Reduce the damage the target takes by your Paladin level",
                            ),
                            ("Cost", "You lose Hit Points equal to your Paladin level"),
                        )
                    ),
                ),
            ),
            Option(
                "Frost",
                (
                    Facts(
                        (
                            ("Trigger", "Replace one attack of your Attack action"),
                            ("Area", "30-foot Cone"),
                            (
                                "Save",
                                "Dexterity against your spell save DC: 8d6 Cold damage, half on a success",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Unholy",
                (
                    Facts(
                        (
                            (
                                "Summon Undead",
                                "No Concentration; the duration becomes 1 minute",
                            ),
                            (
                                "Temporary Hit Points",
                                "The spirit gets Paladin level + Charisma modifier",
                            ),
                            (
                                "Extra damage",
                                "The first time each turn the spirit hits, extra Necrotic damage equal to half your Paladin level (round up)",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You can invoke the power of the rune inscribed on your weapon. Once you use this feature, you can't do so again until you finish a Long Rest. The effect depends on the rune you have inscribed.\n"
            "Blood. When a creature hits another creature you can see within 10 feet of you with an attack roll, you can take a Reaction to reduce the damage the target takes by your Paladin level. You then lose a number of Hit Points equal to your Paladin level.\n"
            "Frost. When you take the Attack action on your turn, you can replace one attack with an exhalation of frost magic in a 30-foot Cone. Each creature in that area makes a Dexterity saving throw against your spell save DC. A creature takes 8d6 Cold damage on a failed save or half as much damage on a successful one.\n"
            "Unholy. When you cast Summon Undead, you can modify it so that the spell doesn't require Concentration. If you do so, the spell's duration becomes 1 minute for that casting, and when summoned, the Undead Spirit has a number of Temporary Hit Points equal to your Paladin level plus your Charisma modifier. In addition, the first time each turn the spirit hits a creature, the spirit deals extra Necrotic damage equal to half your Paladin level (round up)."
        )
        return description


class AspectOfTheHorsemen(Feature):
    def __init__(self):
        super().__init__(
            name="Aspect of the Horsemen",
            origin="Oath of the Ebon Blade Paladin Level 20",
            activation=FeatureActivation(
                action_type=ActionType.BONUS_ACTION, duration="10 Minutes"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(max_uses=1, regain_all_on="long rest"),
        )

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # The once-per-Long-Rest box is in the panel below.
        return [
            Facts(
                (
                    ("Action", "Bonus Action"),
                    (
                        "Duration",
                        "10 minutes, or until you end it (no action required)",
                    ),
                    (
                        "Recharge",
                        "Once per Long Rest, or expend a level 5 spell slot (no action required) to restore it",
                    ),
                )
            ),
            Option(
                "Benefits",
                (
                    Facts(
                        (
                            (
                                "Generate Runic Power",
                                "Restore a use of Runic Mastery by expending a level 4 spell slot (no action required)",
                            ),
                            (
                                "Runeforging",
                                "Runic Power and Runic Mastery can use any rune's effect, not just your inscribed rune's",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "As a Bonus Action, you gain the benefits below for 10 minutes or until you end them (no action required). Once you use this feature, you can't use it again until you finish a Long Rest. You can also restore your use of it by expending a level 5 spell slot (no action required).\n"
            "Generate Runic Power. You can restore a use of your Runic Mastery by expending a level 4 spell slot (no action required).\n"
            "Runeforging. When you use your Runic Power and Runic Mastery features, you can choose any effect, not just the one that corresponds to the rune inscribed on your weapon."
        )
        return description
