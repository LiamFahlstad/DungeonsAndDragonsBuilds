from Core.Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Artificer Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Spellcasting:\n"
            "    * Tools Required: You produce your Artificer spells through tools. You can use Thieves' Tools, Tinker's Tools, or another kind of Artisan's Tools with which you have proficiency as a Spellcasting Focus, and you must have one of those focuses in hand when you cast an Artificer spell.\n"
            "    * Cantrips: You know two Artificer cantrips of your choice. Whenever you finish a Long Rest, you can replace one of your cantrips with another Artificer cantrip of your choice. When you reach Artificer levels 10 and 14, you learn another Artificer cantrip of your choice.\n"
            "    * Spell Slots: The Artificer Features table shows how many spell slots you have to cast your level 1+ spells. You regain all expended slots when you finish a Long Rest.\n"
            "    * Prepared Spells: To start, choose two level 1 Artificer spells. The number of spells on your list increases as you gain Artificer levels. Whenever you finish a Long Rest, you can change your list of prepared spells.\n"
            "    * Spellcasting Ability: Intelligence is your spellcasting ability for your Artificer spells."
        )
        return description


class TinkersMagic(Feature):
    def __init__(self):
        super().__init__(name="Tinker's Magic", origin="Artificer Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(
            Ability.INTELLIGENCE
        )
        uses = max(1, intelligence_modifier)
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
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class ReplicateMagicItem(Feature):
    def __init__(self):
        super().__init__(name="Replicate Magic Item", origin="Artificer Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
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
            "Ring of the Ram"
        )
        return description


class MagicItemTinker(Feature):
    def __init__(self):
        super().__init__(name="Magic Item Tinker", origin="Artificer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Replicate Magic Item feature gains the following options.\n"
            "Charge Magic Item. As a Bonus Action, you can touch a magic item within 5 feet of yourself that you created with Replicate Magic Item and that uses charges. You expend a level 1+ spell slot and recharge the item. The number of charges the item regains is equal to the level of spell slot expended.\n"
            "Drain Magic Item. As a Bonus Action, you can touch a magic item within 5 feet of yourself that you created with Replicate Magic Item and cause the item to vanish, converting its magical energy into a spell slot. The slot is level 1 if the item is Common or level 2 if the item is Uncommon or Rare. Once you use this feature, you can't do so again until you finish a Long Rest. Any spell slot you create with this feature vanishes when you finish a Long Rest.\n"
            "Transmute Magic Item. As a Magic action, you can touch one magic item within 5 feet of yourself that you created with Replicate Magic Item and transform it into a different magic item. The resulting item must be based on a magic item plan you know. Once you use this feature, you can't do so again until you finish a Long Rest."
        )
        return description


class FlashofGenius(Feature):
    def __init__(self):
        super().__init__(name="Flash of Genius", origin="Artificer Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(
            Ability.INTELLIGENCE
        )
        uses = max(1, intelligence_modifier)
        description = (
            "When you or a creature you can see within 30 feet of you fails an ability check or a saving throw, you can take a Reaction to add a bonus to the roll, potentially causing it to succeed. The bonus equals your Intelligence modifier (minimum of +1).\n"
            "You can take this Reaction a number of times equal to your Intelligence modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class MagicItemAdept(Feature):
    def __init__(self):
        super().__init__(name="Magic Item Adept", origin="Artificer Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can now attune to up to four magic items at once."
        return description


class SpellStoringItem(Feature):
    def __init__(self):
        super().__init__(name="Spell-storing Item", origin="Artificer Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you finish a Long Rest, you can touch one Simple or Martial weapon or one item that you can use as a Spellcasting Focus, and you store a spell in it, choosing a level 1, 2, or 3 Artificer spell that has a casting time of an action and doesn't require a Material component that is consumed by the spell (you needn't have the spell prepared).\n"
            "While holding the object, a creature can take a Magic action to produce the spell's effect from it, using your spellcasting ability modifier. If the spell requires Concentration, the creature must concentrate. Once a creature has used the object to produce the spell's effect, the object can't be used this way again until the start of the creature's next turn.\n"
            "The spell stays in the object until it's been used a number of times equal to twice your Intelligence modifier (minimum of twice) or until you use this feature again to store a spell in an object."
        )
        return description


class AdvancedArtifice(Feature):
    def __init__(self):
        super().__init__(name="Advanced Artifice", origin="Artificer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Magic Item Savant. You can now attune to up to five magic items at once.\n"
            "Refreshed Genius. When you finish a Short Rest, you regain one expended use of your Flash of Genius feature."
        )
        return description


class MagicItemMaster(Feature):
    def __init__(self):
        super().__init__(name="Magic Item Master", origin="Artificer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can now attune to up to six magic items at once."
        return description


class SoulOfArtifice(Feature):
    def __init__(self):
        super().__init__(name="Soul of Artifice", origin="Artificer Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have developed a mystical connection to your magic items, which you can draw on for aid. You gain the following benefits.\n"
            "Cheat Death. If you're reduced to 0 Hit Points but not killed outright, you can disintegrate any number of Uncommon or Rare magic items created by your Replicate Magic Item feature. If you do so, your Hit Points instead change to a number equal to 20 times the number of magic items disintegrated.\n"
            "Magical Guidance. When you finish a Short Rest, you regain all expended uses of your Flash of Genius if you have Attunement to at least one magic item."
        )
        return description
