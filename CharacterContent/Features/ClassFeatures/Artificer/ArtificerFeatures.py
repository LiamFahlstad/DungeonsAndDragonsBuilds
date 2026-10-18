from Model.Content.Feature import (
    Feature,
    FeatureActivation,
    FeatureTarget,
    FeatureUses,
    ActionType,
    RegainedOn,
)
from Core.Rules import MAX_ABILITY_MODIFIER, MAX_LEVEL
from Model.View import CharacterView
from Utils import StringUtils
from Model.Content.FeatureText import (
    Block,
    Facts,
    Option,
    Paragraph,
    Table,
    dc_formula,
)
from Core.Definitions import Ability


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Artificer Level 1")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Spellcasting ability", "Intelligence"),
                    ("Save DC", dc_formula(Ability.INTELLIGENCE)),
                    ("Spell attack", "Intelligence modifier + Proficiency Bonus"),
                    (
                        "Focus",
                        "Thieves' Tools, Tinker's Tools or other Artisan's Tools you're proficient with; you must hold one to cast an Artificer spell",
                    ),
                    (
                        "Cantrips",
                        "Two Artificer cantrips; one more at Artificer levels 10 and 14. Swap one after each Long Rest.",
                    ),
                    (
                        "Prepared spells",
                        "Start with two level 1 Artificer spells; the number grows with your Artificer level. Change the list after each Long Rest.",
                    ),
                    (
                        "Spell slots",
                        "As the Artificer Features table; regain all when you finish a Long Rest",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Spellcasting:\n"
            "    * Tools Required: You produce your Artificer spells through tools. You can use Thieves' Tools, Tinker's Tools, or another kind of Artisan's Tools with which you have proficiency as a Spellcasting Focus, and you must have one of those focuses in hand when you cast an Artificer spell.\n"
            "    * Cantrips: You know two Artificer cantrips of your choice. Whenever you finish a Long Rest, you can replace one of your cantrips with another Artificer cantrip of your choice. When you reach Artificer levels 10 and 14, you learn another Artificer cantrip of your choice.\n"
            "    * Spell Slots: The Artificer Features table shows how many spell slots you have to cast your level 1+ spells. You regain all expended slots when you finish a Long Rest.\n"
            "    * Prepared Spells: To start, choose two level 1 Artificer spells. The number of spells on your list increases as you gain Artificer levels. Whenever you finish a Long Rest, you can change your list of prepared spells.\n"
            "    * Spellcasting Ability: Intelligence is your spellcasting ability for your Artificer spells."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST


class TinkersMagic(Feature):
    def __init__(self):
        super().__init__(
            name="Tinker's Magic",
            origin="Artificer Level 1",
            activation=FeatureActivation(
                action_type=ActionType.ACTION,
                duration="Until Long Rest",
                range="5 Feet",
            ),
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses are in the panel below.
        return [
            Paragraph(
                "You know the Mending cantrip, and you can conjure mundane gear."
            ),
            Facts(
                (
                    ("Action", "Magic action, holding Tinker's Tools"),
                    ("Range", "An unoccupied space within 5 feet"),
                    ("Lasts", "Until you finish a Long Rest, then it vanishes"),
                )
            ),
            Option(
                "Items (choose one)",
                (
                    Paragraph(
                        "Ball Bearings, Basket, Bedroll, Bell, Blanket, Block and Tackle, "
                        "Bottle (Glass), Bucket, Caltrops, Candle, Crowbar, Flask, Grappling "
                        "Hook, Hunting Trap, Jug, Lamp, Manacles, Net, Oil, Paper, Parchment, "
                        "Pole, Pouch, Rope, Sack, Shovel, Spikes (Iron), String, Tinderbox, "
                        "Torch, Vial. See each item's rules in the Player's Handbook."
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You know the Mending cantrip.\n"
            "As a Magic action while holding Tinker's Tools, you can create one item in an unoccupied space within 5 feet of yourself, choosing the item from the following list:\n"
            "Ball Bearings	Flask	Pouch\n"
            "Basket	Grappling Hook	Rope\n"
            "Bedroll	Hunting Trap	Sack\n"
            "Bell	Jug	Shovel\n"
            "Blanket	Lamp	Spikes, Iron\n"
            "Block and Tackle	Manacles	String\n"
            "Bottle, Glass	Net	Tinderbox\n"
            "Bucket	Oil	Torch\n"
            "Caltrops	Paper	Vial\n"
            "Candle	Parchment\n"
            "Crowbar	Pole\n"
            "See the rules for the item in the Player's Handbook. The item lasts until you finish a Long Rest, at which point it vanishes.\n"
            "You can use this feature a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


# The Plans Known and Magic Items columns of the Artificer Features table,
# as {Artificer level: count from that level on}.
PLANS_KNOWN_GAINED_AT = {2: 4, 6: 5, 10: 6, 14: 7, 18: 8}
MAGIC_ITEMS_GAINED_AT = {2: 2, 6: 3, 10: 4, 14: 5, 18: 6}

# A plan that stands for any item of a kind: it can be learned more than
# once, a different item each time, and each counts as its own plan.
ANY_ITEM_MARK = "*"

# The Magic Item Plans tables as {lowest Artificer level: ((plan,
# attunement), ...)}; attunement is "Yes", "No" or "Varies".
MAGIC_ITEM_PLANS: dict[int, tuple[tuple[str, str], ...]] = {
    2: (
        ("Alchemy Jug", "No"),
        ("Bag of Holding", "No"),
        ("Cap of Water Breathing", "No"),
        ("Any Common magic item that isn't a Potion, a Scroll, or cursed", "Varies"),
        ("Goggles of Night", "No"),
        ("Manifold Tool", "Yes"),
        ("Repeating Shot", "Yes"),
        ("Returning Weapon", "No"),
        ("Rope of Climbing", "No"),
        ("Sending Stones", "No"),
        ("Shield +1", "No"),
        ("Wand of Magic Detection", "No"),
        ("Wand of Secrets", "No"),
        ("Wand of the War Mage +1", "Yes"),
        ("Weapon +1", "No"),
        ("Wraps of Unarmed Power +1", "No"),
    ),
    6: (
        ("Armor +1", "No"),
        ("Boots of Elvenkind", "No"),
        ("Boots of the Winding Path", "Yes"),
        ("Cloak of Elvenkind", "Yes"),
        ("Cloak of the Manta Ray", "No"),
        ("Dazzling Weapon", "Yes"),
        ("Eyes of Charming", "Yes"),
        ("Eyes of Minute Seeing", "No"),
        ("Gloves of Thievery", "No"),
        ("Helm of Awareness", "No"),
        ("Lantern of Revealing", "No"),
        ("Mind Sharpener", "Yes"),
        ("Necklace of Adaption", "Yes"),
        ("Pipes of Haunting", "No"),
        ("Repulsion Shield", "No"),
        ("Ring of Swimming", "No"),
        ("Ring of Water Walking", "No"),
        ("Sentinel Shield", "No"),
        ("Spell-Refueling Ring", "Yes"),
        ("Wand of Magic Missiles", "No"),
        ("Wand of Web", "Yes"),
        ("Weapon of Warning", "Yes"),
    ),
    10: (
        ("Armor of Resistance", "Yes"),
        ("Dagger of Venom", "No"),
        ("Elven Chain", "No"),
        ("Ring of Feather Falling", "Yes"),
        ("Ring of Jumping", "Yes"),
        ("Ring of Mind Shielding", "Yes"),
        ("Shield +2", "No"),
        ("Any Uncommon Wondrous Item that isn't cursed", "Varies"),
        ("Wand of the War Mage +2", "Yes"),
        ("Weapon +2", "No"),
        ("Wraps of Unarmed Power +2", "No"),
    ),
    14: (
        ("Armor +2", "No"),
        ("Arrow-Catching Shield", "Yes"),
        ("Flame Tongue", "Yes"),
        ("Any Rare Wondrous Item that isn't cursed", "Varies"),
        ("Ring of Free Action", "Yes"),
        ("Ring of Protection", "Yes"),
        ("Ring of the Ram", "Yes"),
    ),
}

# Fill-in rows on the printed card: one per plan known at level 20.
_WORKSHOP_ROWS = max(PLANS_KNOWN_GAINED_AT.values())


def _count_at(gained_at: dict[int, int], level: int) -> int:
    """The count from a {level: count} progression at an Artificer level
    (0 before the first entry)."""
    return max(
        (count for from_level, count in gained_at.items() if from_level <= level),
        default=0,
    )


def plans_known(artificer_level: int) -> int:
    return _count_at(PLANS_KNOWN_GAINED_AT, artificer_level)


def magic_items_allowed(artificer_level: int) -> int:
    return _count_at(MAGIC_ITEMS_GAINED_AT, artificer_level)


def _plan_html(plan: str, attunement: str) -> str:
    """A plan's catalogue entry: the name, then A when it needs Attunement
    or * when it stands for any item of a kind."""
    if plan.startswith("Any "):
        return f"{plan}{ANY_ITEM_MARK}"
    if attunement == "Yes":
        return f"{plan}<sup>A</sup>"
    return plan


class ReplicateMagicItem(Feature):
    def __init__(self):
        super().__init__(name="Replicate Magic Item", origin="Artificer Level 2")

    def get_resource_tiles(
        self, character: CharacterView
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        return [
            (label, self._steps(count_at))
            for label, count_at in (
                ("Plans Known", plans_known),
                ("Magic Items", magic_items_allowed),
            )
        ]

    @staticmethod
    def _steps(count_at) -> list[tuple[str, str]]:
        by_level = {level: count_at(level) for level in range(2, MAX_LEVEL + 1)}
        return [
            (f"Lv {levels}", value)
            for levels, value in StringUtils.compress_level_progression(by_level)
        ]

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Plans Known and Magic Items are in the Scaling rows below.
        return [
            Paragraph(
                "You know arcane plans, and each Long Rest you turn some of them into working magic items."
            ),
            Facts(
                (
                    (
                        "Plans",
                        "Plans Known (see Scaling below), from any plan table your Artificer level qualifies for. "
                        "Start with four from the level 2+ table; Bag of Holding, Cap of Water Breathing, Sending Stones and Wand of the War Mage are recommended.",
                    ),
                    (
                        "Swap a plan",
                        "Whenever you gain an Artificer level, replace one plan with another you qualify for. Items made from the old plan vanish at once.",
                    ),
                    (
                        "Make items",
                        "When you finish a Long Rest with Tinker's Tools in hand, make up to Magic Items (see Scaling below) items, each from a different plan you know",
                    ),
                    (
                        "Item limit",
                        "At most Magic Items (see Scaling below) exist at once; making another makes the oldest vanish as the new one appears",
                    ),
                    (
                        "Attunement",
                        "Attune the instant you make it, or later by the normal process",
                    ),
                    (
                        "Duration",
                        "Works like the normal item but isn't permanent: when you die, it vanishes after 1d4 days. "
                        "A container's contents appear harmlessly in and around its space when it vanishes.",
                    ),
                    (
                        "Focus",
                        "Any Wand or Weapon you make is a Spellcasting Focus, instead of Artisan's Tools",
                    ),
                )
            ),
            Option(
                "Magic Item Plans",
                (
                    Table(
                        ("Artificer level", "Plans"),
                        tuple(
                            (
                                f"{level}+",
                                ", ".join(
                                    _plan_html(plan, attunement)
                                    for plan, attunement in plans
                                ),
                            )
                            for level, plans in MAGIC_ITEM_PLANS.items()
                        ),
                    ),
                    Paragraph(
                        f"Plans marked <sup>A</sup> require Attunement; for those marked {ANY_ITEM_MARK} it varies by item, "
                        "and you can learn them more than once (a different item each time, each its own plan)"
                    ),
                ),
            ),
            Option(
                "Your workshop",
                (
                    Table(
                        ("Plan known", "Item made"),
                        (("&nbsp;", "&#9744;"),) * _WORKSHOP_ROWS,
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have learned arcane plans that you use to make magic items.\n"
            "Plans Known. When you gain this feature, choose four plans to learn from the Magic Item Plans (Artificer Level 2+) table. Bag of Holding, Cap of Water Breathing, Sending Stones, and Wand of the War Mage are recommended. Whenever you gain an Artificer level, you can replace one of the plans you know with a new plan for which you qualify.\n"
            "You learn another plan of your choice when you reach certain Artificer levels, as shown in the Plans Known column of the Artificer Features table. When you choose a plan to learn, you choose it from any Magic Item Plans table for which you qualify; your qualification is based on your Artificer level.\n"
            "Creating an Item. When you finish a Long Rest, you can create one or two different magic items if you have Tinker's Tools in hand. Each item is based on one of the plans you know for this feature.\n"
            "If a created item requires Attunement, you can attune yourself to it the instant you create it. If you decide to attune to the item later, you must do so using the normal process for Attunement.\n"
            "When you reach certain Artificer levels specified in the Magic Items column of the Artificer Features table, the number of magic items you can create at the end of a Long Rest increases. Each item you create must be based on a different plan you know.\n"
            "You can't have more magic items from this feature than the number shown in the Magic Items column of the Artificer Features table for your level. If you try to exceed your maximum number of magic items for this feature, the oldest item vanishes, and then the new item appears.\n"
            "Duration. A magic item created by this feature functions as the normal magic item, except its magic isn't permanent; when you die, the magic item vanishes after 1d4 days. If you replace a plan you know with a new plan, any magic item created with the replaced plan immediately vanishes.\n"
            "If an item that you created with this feature is a container, such as a Bag of Holding, and it vanishes, its contents harmlessly appear in and around its space.\n"
            "Spellcasting Focus. You can use any Wand or Weapon created by this feature as a Spellcasting Focus in lieu of using a set of Artisan's Tools.\n"
            "Magic Item Plans (Artificer Level 2+)\n"
            "Magic Item Plan	Attunement\n"
            "Alchemy Jug	No\n"
            "Bag of Holding	No\n"
            "Cap of Water Breathing	No\n"
            "Common magic item that isn't a Potion, a Scroll, or cursed (you can learn this option multiple times and must select a different item each time; each item selected counts as a different plan)	Varies\n"
            "Goggles of Night	No\n"
            "Manifold Tool	Yes\n"
            "Repeating Shot	Yes\n"
            "Returning Weapon	No\n"
            "Rope of Climbing	No\n"
            "Sending Stones	No\n"
            "Shield +1	No\n"
            "Wand of Magic Detection	No\n"
            "Wand of Secrets	No\n"
            "Wand of the War Mage +1	Yes\n"
            "Weapon +1	No\n"
            "Wraps of Unarmed Power +1	No\n"
            "Magic Item Plans (Artificer Level 6+)\n"
            "Magic Item Plan	Attunement\n"
            "Armor +1	No\n"
            "Boots of Elvenkind	No\n"
            "Boots of the Winding Path	Yes\n"
            "Cloak of Elvenkind	Yes\n"
            "Cloak of the Manta Ray	No\n"
            "Dazzling Weapon	Yes\n"
            "Eyes of Charming	Yes\n"
            "Eyes of Minute Seeing	No\n"
            "Gloves of Thievery	No\n"
            "Helm of Awareness	No\n"
            "Lantern of Revealing	No\n"
            "Mind Sharpener	Yes\n"
            "Necklace of Adaption	Yes\n"
            "Pipes of Haunting	No\n"
            "Repulsion Shield	No\n"
            "Ring of Swimming	No\n"
            "Ring of Water Walking	No\n"
            "Sentinel Shield	No\n"
            "Spell-Refueling Ring	Yes\n"
            "Wand of Magic Missiles	No\n"
            "Wand of Web	Yes\n"
            "Weapon of Warning	Yes\n"
            "Magic Item Plans (Artificer Level 10+)\n"
            "Magic Item Plan	Attunement\n"
            "Armor of Resistance	Yes\n"
            "Dagger of Venom	No\n"
            "Elven Chain	No\n"
            "Ring of Feather Falling	Yes\n"
            "Ring of Jumping	Yes\n"
            "Ring of Mind Shielding	Yes\n"
            "Shield +2	No\n"
            "Uncommon Wondrous Item that isn't cursed (you can learn this option multiple times and must select a different item each time; each item selected counts as a different plan)	Varies\n"
            "Wand of the War Mage +2	Yes\n"
            "Weapon +2	No\n"
            "Wraps of Unarmed Power +2	No\n"
            "Magic Item Plans (Artificer Level 14+)\n"
            "Magic Item Plan	Attunement\n"
            "Armor +2	No\n"
            "Arrow-Catching Shield	Yes\n"
            "Flame Tongue	Yes\n"
            "Rare Wondrous Item that isn't cursed (you can learn this option multiple times and must select a different item each time; each item selected counts as a different plan)	Varies\n"
            "Ring of Free Action	Yes\n"
            "Ring of Protection	Yes\n"
            "Ring of the Ram 	Yes"
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


class MagicItemTinker(Feature):
    def __init__(self):
        super().__init__(
            name="Magic Item Tinker",
            origin="Artificer Level 6",
            uses=FeatureUses(
                max_uses=1,
                regain_all_on="long rest",
                current_formula="Used by Drain Magic Item.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Drain Magic Item's once-per-Long-Rest box is in the panel below.
        return [
            Paragraph(
                "New options for items you made with Replicate Magic Item, each used by touching one within 5 feet of you."
            ),
            Option(
                "Charge Magic Item",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            ("Target", "A replicated item that uses charges"),
                            ("Cost", "A level 1+ spell slot"),
                            (
                                "Effect",
                                "The item regains charges equal to the slot's level",
                            ),
                        )
                    ),
                ),
            ),
            Option(
                "Drain Magic Item",
                (
                    Facts(
                        (
                            ("Action", "Bonus Action"),
                            (
                                "Effect",
                                "The item vanishes and becomes a spell slot: level 1 for a Common item, level 2 for an Uncommon or Rare one. The slot vanishes when you finish a Long Rest.",
                            ),
                            ("Limit", "Once per Long Rest"),
                        )
                    ),
                ),
            ),
            Option(
                "Transmute Magic Item",
                (
                    Facts(
                        (
                            ("Action", "Magic action"),
                            (
                                "Effect",
                                "Transform the item into a different magic item based on a plan you know",
                            ),
                            ("Limit", "Once per Long Rest"),
                        )
                    ),
                ),
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Your Replicate Magic Item feature gains the following options.\n"
            "Charge Magic Item. As a Bonus Action, you can touch a magic item within 5 feet of yourself that you created with Replicate Magic Item and that uses charges. You expend a level 1+ spell slot and recharge the item. The number of charges the item regains is equal to the level of spell slot expended.\n"
            "Drain Magic Item. As a Bonus Action, you can touch a magic item within 5 feet of yourself that you created with Replicate Magic Item and cause the item to vanish, converting its magical energy into a spell slot. The slot is level 1 if the item is Common or level 2 if the item is Uncommon or Rare. Once you use this feature, you can't do so again until you finish a Long Rest. Any spell slot you create with this feature vanishes when you finish a Long Rest.\n"
            "Transmute Magic Item. As a Magic action, you can touch one magic item within 5 feet of yourself that you created with Replicate Magic Item and transform it into a different magic item. The resulting item must be based on a magic item plan you know. Once you use this feature, you can't do so again until you finish a Long Rest."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


class FlashofGenius(Feature):
    def __init__(self):
        super().__init__(
            name="Flash of Genius",
            origin="Artificer Level 7",
            activation=FeatureActivation(
                action_type=ActionType.REACTION, range="30 Feet"
            ),
            usage_tags=["buff"],
            uses=FeatureUses(
                max_uses=MAX_ABILITY_MODIFIER,
                regain_all_on="long rest",
                current_formula="Current amount: equal to your Intelligence modifier.",
            ),
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        # Uses (Intelligence modifier, minimum of once) are in the panel below.
        return [
            Facts(
                (
                    ("Action", "Reaction"),
                    (
                        "Trigger",
                        "You or a creature you can see within 30 feet fails an ability check or a saving throw",
                    ),
                    (
                        "Effect",
                        "Add your Intelligence modifier (minimum +1) to the roll",
                    ),
                    (
                        "From Artificer level 14",
                        "Regain one expended use when you finish a Short Rest (Advanced Artifice)",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "When you or a creature you can see within 30 feet of you fails an ability check or a saving throw, you can take a Reaction to add a bonus to the roll, potentially causing it to succeed. The bonus equals your Intelligence modifier (minimum of +1).\n"
            "You can take this Reaction a number of times equal to your Intelligence modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return description

    def regained_on(self, character: CharacterView) -> "RegainedOn | None":
        return RegainedOn.LONG_REST

    def number_of_uses(self, character: CharacterView) -> int:
        return max(1, character.get_intelligence_modifier())

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class MagicItemAdept(Feature):
    def __init__(self):
        super().__init__(name="Magic Item Adept", origin="Artificer Level 10")

    def get_description(self, character: CharacterView) -> str:
        description = "You can now attune to up to four magic items at once."
        return description


class SpellStoringItem(Feature):
    def __init__(self):
        super().__init__(name="Spell-storing Item", origin="Artificer Level 11")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Paragraph("Store a spell in an item for anyone to use."),
            Facts(
                (
                    ("When", "Whenever you finish a Long Rest"),
                    (
                        "Item",
                        "One Simple or Martial weapon, or one item you can use as a Spellcasting Focus, that you touch",
                    ),
                    (
                        "Spell",
                        "A level 1-3 Artificer spell with a casting time of an action and no consumed Material component (it needn't be prepared)",
                    ),
                    (
                        "Using it",
                        "Whoever holds it takes a Magic action to produce the spell, using your spellcasting ability modifier (and concentrating if needed). A creature that does so can't do it again until the start of its next turn.",
                    ),
                    (
                        "Lasts",
                        "2 x Intelligence modifier uses (minimum 2), or until you store another spell",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "Whenever you finish a Long Rest, you can touch one Simple or Martial weapon or one item that you can use as a Spellcasting Focus, and you store a spell in it, choosing a level 1, 2, or 3 Artificer spell that has a casting time of an action and doesn't require a Material component that is consumed by the spell (you needn't have the spell prepared).\n"
            "While holding the object, a creature can take a Magic action to produce the spell's effect from it, using your spellcasting ability modifier. If the spell requires Concentration, the creature must concentrate. Once a creature has used the object to produce the spell's effect, the object can't be used this way again until the start of the creature's next turn.\n"
            "The spell stays in the object until it's been used a number of times equal to twice your Intelligence modifier (minimum of twice) or until you use this feature again to store a spell in an object."
        )
        return description

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.OBJECT


class AdvancedArtifice(Feature):
    def __init__(self):
        super().__init__(name="Advanced Artifice", origin="Artificer Level 14")

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    ("Magic Item Savant", "Attune to up to five magic items at once"),
                    (
                        "Refreshed Genius",
                        "When you finish a Short Rest, regain one expended use of Flash of Genius",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You gain the following benefits.\n"
            "Magic Item Savant. You can now attune to up to five magic items at once.\n"
            "Refreshed Genius. When you finish a Short Rest, you regain one expended use of your Flash of Genius feature."
        )
        return description


class MagicItemMaster(Feature):
    def __init__(self):
        super().__init__(name="Magic Item Master", origin="Artificer Level 18")

    def get_description(self, character: CharacterView) -> str:
        description = "You can now attune to up to six magic items at once."
        return description


class SoulOfArtifice(Feature):
    def __init__(self):
        super().__init__(
            name="Soul of Artifice", origin="Artificer Level 20", usage_tags=["heal"]
        )

    def get_improved_description(self, character: CharacterView) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Cheat Death",
                        "When you drop to 0 Hit Points but aren't killed outright, disintegrate any number of your Uncommon or Rare Replicate Magic Item items: your Hit Points become 20 x the number destroyed",
                    ),
                    (
                        "Magical Guidance",
                        "When you finish a Short Rest while attuned to at least one magic item, regain all uses of Flash of Genius",
                    ),
                )
            ),
        ]

    def get_description(self, character: CharacterView) -> str:
        description = (
            "You have developed a mystical connection to your magic items, which you can draw on for aid. You gain the following benefits.\n"
            "Cheat Death. If you're reduced to 0 Hit Points but not killed outright, you can disintegrate any number of Uncommon or Rare magic items created by your Replicate Magic Item feature. If you do so, your Hit Points instead change to a number equal to 20 times the number of magic items disintegrated.\n"
            "Magical Guidance. When you finish a Short Rest, you regain all expended uses of your Flash of Genius if you have Attunement to at least one magic item."
        )
        return description
