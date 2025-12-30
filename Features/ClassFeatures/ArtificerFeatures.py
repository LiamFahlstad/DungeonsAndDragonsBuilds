from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

ARTIFICER_HIT_DIE = 8


class TinkersMagic(TextFeature):
    def __init__(self):
        super().__init__(name="Tinker's Magic", origin="Artificer Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
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


class ReplicateMagicItem(TextFeature):
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
            "Wraps of Unarmed Power +1\n"
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


class MagicItemTinker(TextFeature):
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


class FlashofGenius(TextFeature):
    def __init__(self):
        super().__init__(name="Flash of Genius", origin="Artificer Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you or a creature you can see within 30 feet of you fails an ability check or a saving throw, you can take a Reaction to add a bonus to the roll, potentially causing it to succeed. The bonus equals your Intelligence modifier (minimum of +1).\n"
            "You can take this Reaction a number of times equal to your Intelligence modifier (minimum of once). You regain all expended uses when you finish a Long Rest."
        )
        return description


class MagicItemAdept(TextFeature):
    def __init__(self):
        super().__init__(name="Magic Item Adept", origin="Artificer Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can now attune to up to four magic items at once."
        return description


class SpellStoringItem(TextFeature):
    def __init__(self):
        super().__init__(name="Spell-storing Item", origin="Artificer Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you finish a Long Rest, you can touch one Simple or Martial weapon or one item that you can use as a Spellcasting Focus, and you store a spell in it, choosing a level 1, 2, or 3 Artificer spell that has a casting time of an action and doesn't require a Material component that is consumed by the spell (you needn't have the spell prepared).\n"
            "While holding the object, a creature can take a Magic action to produce the spell's effect from it, using your spellcasting ability modifier. If the spell requires Concentration, the creature must concentrate. Once a creature has used the object to produce the spell's effect, the object can't be used this way again until the start of the creature's next turn.\n"
            "The spell stays in the object until it's been used a number of times equal to twice your Intelligence modifier (minimum of twice) or until you use this feature again to store a spell in an object."
        )
        return description


class AdvancedArtifice(TextFeature):
    def __init__(self):
        super().__init__(name="Advanced Artifice", origin="Artificer Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Magic Item Savant. You can now attune to up to five magic items at once.\n"
            "Refreshed Genius. When you finish a Short Rest, you regain one expended use of your Flash of Genius feature."
        )
        return description


class MagicItemMaster(TextFeature):
    def __init__(self):
        super().__init__(name="Magic Item Master", origin="Artificer Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can now attune to up to six magic items at once."
        return description


class SoulOfArtifice(TextFeature):
    def __init__(self):
        super().__init__(name="Soul of Artifice", origin="Artificer Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have developed a mystical connection to your magic items, which you can draw on for aid. You gain the following benefits.\n"
            "Cheat Death. If you're reduced to 0 Hit Points but not killed outright, you can disintegrate any number of Uncommon or Rare magic items created by your Replicate Magic Item feature. If you do so, your Hit Points instead change to a number equal to 20 times the number of magic items disintegrated.\n"
            "Magical Guidance. When you finish a Short Rest, you regain all expended uses of your Flash of Genius if you have Attunement to at least one magic item."
        )
        return description


### Alchemist Artificer Features ###


class AlchemistToolsOfTheTrade(TextFeature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade", origin="Alchemist Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Alchemist's Supplies and the Herbalism Kit. If you already have one of these proficiencies, you gain proficiency with one other type of Artisan's Tools of your choice (or with two other types if you have both).\n"
            "Potion Crafting. When you brew a potion using the crafting rules in the Dungeon Master's Guide, the amount of time required to craft it is halved."
        )
        return description


class AlchemistSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Alchemist Spells", origin="Alchemist Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Alchemist Spells table, you thereafter always have the listed spells prepared.\n"
            "Alchemist Spells\n"
            "Artificer Level	Spells\n"
            "3	Healing Word, Ray of Sickness\n"
            "5	Flaming Sphere, Melf's Acid Arrow\n"
            "9	Gaseous Form, Mass Healing Word\n"
            "13	Death Ward, Vitriolic Sphere\n"
            "17	Cloudkill, Raise Dead"
        )
        return description


class ExperimentalElixir(TextFeature):
    def __init__(self):
        super().__init__(
            name="Experimental Elixir", origin="Alchemist Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you finish a Long Rest while holding Alchemist's Supplies, you can use that tool to magically produce two elixirs. For each elixir, roll on the Experimental Elixir table for the elixir's effect, which is triggered when someone drinks the elixir. The elixir appears in a vial, and the vial vanishes when the elixir is drunk or poured out. If any elixir remains when you finish a Long Rest, the elixir and its vial vanish.\n"
            "Drinking an Elixir. As a Bonus Action, a creature can drink the elixir or administer it to another creature within 5 feet of itself.\n"
            "Creating Additional Elixirs. As a Magic action while holding Alchemist's Supplies, you can expend one spell slot to create another elixir. When you do so, you choose its effect from the Experimental Elixir table rather than rolling.\n"
            "When you reach certain Artificer levels, you can make an additional elixir at the end of each Long Rest: a total of three at level 5, four at level 9, and five at level 15.\n"
            "Experimental Elixir\n"
            "D6	Effect\n"
            "1	Healing. The drinker regains a number of Hit Points equal to 2d8 plus your Intelligence modifier. The number of Hit Points restored increases by 1d8 when you reach Artificer levels 9 (3d8) and 15 (4d8).\n"
            "2	Swiftness. The drinker's Speed increases by 10 feet for 1 hour. This bonus increases when you reach Artificer levels 9 (15 feet) and 15 (20 feet).\n"
            "3	Resilience. The drinker gains a +1 bonus to AC for 10 minutes. The duration increases when you reach Artificer levels 9 (1 hour) and 15 (8 hours).\n"
            "4	Boldness. The drinker can roll 1d4 and add the number rolled to every attack roll and saving throw it makes for the next minute. The duration increases when you reach Artificer levels 9 (10 minutes) and 15 (1 hour).\n"
            "5	Flight. The drinker gains a Fly Speed of 10 feet for 10 minutes. The Fly Speed increases when you reach Artificer levels 9 (20 feet) and 15 (30 feet).\n"
            "6	You determine the elixir's effect by choosing one of the other rows in this table."
        )
        return description


class AlchemicalSavant(TextFeature):
    def __init__(self):
        super().__init__(name="Alchemical Savant", origin="Alchemist Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever you cast a spell using your Alchemist's Supplies as the Spellcasting Focus, you gain a bonus to one roll of the spell. That roll must restore Hit Points or be a damage roll that deals Acid, Fire, or Poison damage. The bonus equals your Intelligence modifier (minimum bonus of +1)."
        return description


class RestorativeReagents(TextFeature):
    def __init__(self):
        super().__init__(
            name="Restorative Reagents", origin="Alchemist Artificer Level 9"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can cast Lesser Restoration without expending a spell slot and without preparing the spell, provided you use Alchemist's Supplies as the Spellcasting Focus. You can do so a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        return description


class ChemicalMastery(TextFeature):
    def __init__(self):
        super().__init__(name="Chemical Mastery", origin="Alchemist Artificer Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Alchemical Eruption. When you cast an Artificer spell that deals Acid, Fire, or Poison damage to a target, you can also deal 2d8 Force damage to that target. You can use this benefit only once on each of your turns.\n"
            "Chemical Resistance. You gain Resistance to Acid damage and Poison damage. You also gain Immunity to the Poisoned condition.\n"
            "Conjured Cauldron. You can cast Tasha's Bubbling Cauldron without expending a spell slot, without preparing the spell, and without Material components, provided you use Alchemist's Supplies as the Spellcasting Focus. Once you use this feature, you can't use it again until you finish a Long Rest."
        )
        return description


### Armorer Artificer Features ###


class ArmorerToolsOfTheTrade(TextFeature):
    def __init__(self):
        super().__init__(name="Tools of the Trade", origin="Armorer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Armor Training. You gain training with Heavy armor.\n"
            "Tool Proficiency. You gain proficiency with Smith's Tools. If you already have this tool proficiency, you gain proficiency with one other type of Artisan's Tools of your choice.\n"
            "Armor Crafting. When you craft nonmagical or magic armor, the amount of time required to craft it is halved."
        )
        return description


class ArmorerSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Armorer Spells", origin="Armorer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Armorer Spells table, you thereafter always have the listed spells prepared.\n"
            "Armorer Spells\n"
            "Artificer Level	Spells\n"
            "3	Magic Missile, Thunderwave\n"
            "5	Mirror Image, Shatter\n"
            "9	Hypnotic Pattern, Lightning Bolt\n"
            "13	Fire Shield, Greater Invisibility\n"
            "17	Passwall, Wall of Force"
        )
        return description


class ArcaneArmor(TextFeature):
    def __init__(self):
        super().__init__(name="Arcane Armor", origin="Armorer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action while you have Smith's Tools in hand, you can turn a suit of armor you are wearing into Arcane Armor. The armor continues to be Arcane Armor until you don another suit of armor or you die.\n"
            "You gain the following benefits while wearing your Arcane Armor.\n"
            "No Strength Requirement. If the armor normally has a Strength requirement, the Arcane Armor lacks this requirement for you.\n"
            "Quick Don and Doff. You can don or doff the armor as a Utilize action. The armor can't be removed against your will.\n"
            "Spellcasting Focus. You can use the Arcane Armor as a Spellcasting Focus for your Artificer spells."
        )
        return description


class ArmorModel(TextFeature):
    def __init__(self):
        super().__init__(name="Armor Model", origin="Armorer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can customize your Arcane Armor. When you do so, choose one of the following armor models: Dreadnaught, Guardian, or Infiltrator. The model you choose gives you special benefits while you wear it.\n"
            "Each model includes a special weapon. When you attack with that weapon, you can add your Intelligence modifier, instead of your Strength or Dexterity modifier, to the attack and damage rolls.\n"
            "You can change the armor's model whenever you finish a Short or Long Rest if you have Smith's Tools in hand.\n"
            "Dreadnaught.\n"
            "You design your armor to become a towering juggernaut in battle. It has the following features:\n"
            "Force Demolisher. An arcane wrecking ball or sledgehammer projects from your armor. The demolisher counts as a Simple Melee weapon with the Reach property, and it deals 1d10 Force damage on a hit. If you hit a creature that is at least one size smaller than you with the demolisher, you can push the creature up to 10 feet straight away from yourself or pull the creature up to 10 feet toward yourself.\n"
            "Giant Stature. As a Bonus Action, you transform and enlarge your armor for 1 minute. For the duration, your reach increases by 5 feet, and if you are smaller than Large, you become Large, along with anything you are wearing. If there isn't enough room for you to increase your size, your size doesn't change. You can use this Bonus Action a number of times equal to your Intelligence modifier (minimum of once). You regain all expended uses when you finish a Long Rest.\n"
            "Guardian.\n"
            "You design your armor to be in the front line of conflict. It has the following features:\n"
            "Thunder Pulse. You can discharge concussive blasts with strikes from your armor. The pulse counts as a Simple Melee weapon and deals 1d8 Thunder damage on a hit. A creature hit by the pulse has Disadvantage on attack rolls against targets other than you until the start of your next turn.\n"
            "Defensive Field. While Bloodied, you can take a Bonus Action to gain Temporary Hit Points equal to your Artificer level. You lose these Temporary Hit Points if you doff the armor.\n"
            "Infiltrator.\n"
            "You customize your armor for subtler undertakings. It has the following features:\n"
            "Lightning Launcher. A gemlike node appears on your armor, from which you can shoot bolts of lightning. The launcher counts as a Simple Ranged weapon with a normal range of 90 feet and a long range of 300 feet, and it deals 1d6 Lightning damage on a hit. Once on each of your turns when you hit a creature with the launcher, you can deal an extra 1d6 Lightning damage to that target.\n"
            "Powered Steps. Your Speed increases by 5 feet.\n"
            "Dampening Field. You have Advantage on Dexterity (Stealth) checks. If the armor imposes Disadvantage on such checks, the Advantage and Disadvantage cancel each other, as normal."
        )
        return description


class ArmorerExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Armorer Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn."
        return description


class ImprovedArmorer(TextFeature):
    def __init__(self):
        super().__init__(name="Improved Armorer", origin="Armorer Artificer Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Armor Replication. You learn an additional plan for your Replicate Magic Item feature, and it must be in the Armor category. If you replace that plan, you must replace it with another Armor plan.\n"
            "In addition, you can create an additional item with that feature, and the item must also be in the Armor category.\n"
            "Improved Arsenal. You gain a +1 bonus to attack and damage rolls made with the special weapon of your Arcane Armor model."
        )
        return description


class PerfectedArmor(TextFeature):
    def __init__(self):
        super().__init__(name="Perfected Armor", origin="Armorer Artificer Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Arcane Armor gains additional benefits based on its model, as detailed below.\n"
            "Dreadnaught. The damage die of your Force Demolisher increases to 2d6 Force damage.\n"
            "In addition, when you use your Giant Stature, your reach increases by 10 feet, your size can increase to Large or Huge (your choice), and you have Advantage on Strength checks and Strength saving throws for the duration.\n"
            "Guardian. The damage die of your Thunder Pulse increases to 1d10 Thunder damage.\n"
            "In addition, when a Huge or smaller creature you can see ends its turn within 30 feet of you, you can take a Reaction to magically force that creature to make a Strength saving throw against your spell save DC. On a failed save, you pull the creature up to 25 feet directly toward you to an unoccupied space. If you pull the target to a space within 5 feet of yourself, you can make a melee weapon attack against it as part of this Reaction.\n"
            "You can take this Reaction a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "Infiltrator. The damage die of your Lightning Launcher increases to 2d6 Lightning damage. Any creature that takes Lightning damage from your Lightning Launcher glimmers with magical light until the start of your next turn. The glimmering creature sheds Dim Light in a 5-foot radius, and it has Disadvantage on attack rolls against you, as the light jolts it if it attacks you.\n"
            "Additionally, as a Bonus Action, you can gain a Fly Speed equal to twice your Speed until the end of the current turn. You can take this Bonus Action a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description


### Artillerist Artificer Features ###


class ArtilleristToolsOfTheTrade(TextFeature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade", origin="Artillerist Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Ranged Weaponry. You gain proficiency with Martial Ranged weapons.\n"
            "Tool Proficiency. You gain proficiency with Woodcarver's Tools. If you already have this proficiency, you gain proficiency with one other type of Artisan's Tools of your choice.\n"
            "Wand Crafting. When you craft a magic Wand, the amount of time required to craft it is halved."
        )
        return description


class ArtilleristSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Artillerist Spells", origin="Artillerist Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Artillerist Spells table, you thereafter always have the listed spells prepared.\n"
            "Artillerist Spells\n"
            "Artificer Level	Spells\n"
            "3	Shield, Thunderwave\n"
            "5	Scorching Ray, Shatter\n"
            "9	Fireball, Wind Wall\n"
            "13	Ice Storm, Wall of Fire\n"
            "17	Cone of Cold, Wall of Force"
        )
        return description


class EldritchCannon(TextFeature):
    def __init__(self):
        super().__init__(name="Eldritch Cannon", origin="Artillerist Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Using Smith's Tools or Woodcarver's Tools, you can take a Magic action to create a Small or Tiny Eldritch Cannon in an unoccupied space on a horizontal surface within 5 feet of yourself. The cannon's game statistics appear below. You determine its appearance, including whether you carry it or not (and your choice of legs or wheels, for the latter). It disappears if it is reduced to 0 Hit Points or after 1 hour. You can dismiss it early as a Magic action.\n"
            "Once you create a cannon, you can't do so again until you finish a Long Rest or expend a spell slot to create one. You can have only one cannon at a time and can't create one while you already have one.\n"
            "Eldritch Cannon\n"
            "Small or Tiny Object\n"
            "Armor Class: 18\n"
            "Hit Points: 5 × your Artificer level (casting Mending on the cannon restores 2d6 Hit Points to it)\n"
            "Immunities: Poison, Psychic\n"
            "Activate Cannon (Requires You to be within 60 Feet of the Cannon): As a Bonus Action, you order the cannon to use the Flamethrower, Force Ballista, or Protector option below; you can direct the cannon to move up to 15 feet before or after that option:\n"
            "Flamethrower: The cannon exhales fire in a 15-foot Cone. Each creature in that area makes a Dexterity saving throw against your spell save DC, taking 2d8 Fire damage on a failed save or half as much damage on a successful one. Flammable objects in the Cone that aren't being worn or carried start burning.\n"
            "Force Ballista: Make a ranged spell attack originating from the cannon at one creature or object within 120 feet of it. On a hit, the target takes 2d8 Force damage, and if the target is a creature, it is pushed up to 5 feet away from the cannon.\n"
            "Protector: The cannon emits a burst of positive energy that grants itself and each creature of your choice within 10 feet of it a number of Temporary Hit Points equal to 1d8 plus your Intelligence modifier (minimum of 1)."
        )
        return description


class ArcaneFirearm(TextFeature):
    def __init__(self):
        super().__init__(name="Arcane Firearm", origin="Artillerist Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you finish a Long Rest, you can use Woodcarver's Tools to carve special sigils into a Rod, Staff, Wand, or Martial Ranged weapon and thereby turn it into your Arcane Firearm. The sigils disappear from the object if you later carve them on a different item. The sigils otherwise last indefinitely.\n"
            "You can use your Arcane Firearm as a Spellcasting Focus for your Artificer spells. When you cast an Artificer spell through the firearm, roll 1d8, and you gain a bonus to one of the spell's damage rolls equal to the number rolled."
        )
        return description


class ExplosiveCannon(TextFeature):
    def __init__(self):
        super().__init__(
            name="Explosive Cannon", origin="Artillerist Artificer Level 9"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Every Eldritch Cannon you create is now more destructive. You gain the following benefits.\n"
            "Detonate. When your cannon takes damage, you can take a Reaction to command the cannon to detonate if you are within 60 feet of it. Doing so destroys the cannon and forces each creature within 20 feet of it to make a Dexterity saving throw against your spell save DC, taking 3d10 Force damage on a failed save or half as much damage on a successful one.\n"
            "Firepower. The cannon's damage rolls and the number of Temporary Hit Points granted by Protector increase by 1d8."
        )
        return description


class FortifiedPosition(TextFeature):
    def __init__(self):
        super().__init__(
            name="Fortified Position", origin="Artillerist Artificer Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You're a master at forming well-defended emplacements using your Eldritch Cannon. You gain the following benefits.\n"
            "Double Firepower. You can now have two cannons at the same time, and you can create two with the same Magic action. (If you expend a spell slot to create the first cannon, you must expend another spell slot to create the second.) You can activate both of them with the same Bonus Action, ordering them to use the same activation option or different ones. You can't create a third cannon while you have two.\n"
            "Shimmering Field Projection. You and your allies have Half Cover while within 10 feet of your Eldritch Cannon."
        )
        return description


### Battle Smith Artificer Features ###


class BattleSmithToolsOfTheTrade(TextFeature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade", origin="Battle Smith Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Smith's Tools. If you already have this proficiency, you gain proficiency with one other type of Artisan's Tools of your choice.\n"
            "Weapon Crafting. When you craft a nonmagical or magic weapon, the amount of time required to craft it is halved."
        )
        return description


class BattleSmithSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Battle Smith spells", origin="Battle Smith Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Battle Smith Spells table, you thereafter always have the listed spells prepared.\n"
            "Battle Smith Spells\n"
            "Artificer Level	Spells\n"
            "3	Heroism, Shield\n"
            "5	Shining Smite, Warding Bond\n"
            "9	Aura of Vitality, Conjure Barrage\n"
            "13	Aura of Purity, Fire Shield\n"
            "17	Banishing Smite, Mass Cure Wounds"
        )
        return description


class BattleReady(TextFeature):
    def __init__(self):
        super().__init__(name="Battle Ready", origin="Battle Smith Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your combat training and your experiments with magic have paid off in two ways.\n"
            "Arcane Empowerment. When you attack with a magic weapon, you can use your Intelligence modifier, instead of your Strength or Dexterity modifier, for the attack and damage rolls.\n"
            "Weapon Knowledge. You gain proficiency with Martial weapons. You can use a weapon with which you have proficiency as a Spellcasting Focus for your Artificer spells."
        )
        return description


class SteelDefender(TextFeature):
    def __init__(self):
        super().__init__(name="Steel Defender", origin="Battle Smith Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your tinkering has borne you a companion, a Steel Defender (see the stat block). You determine the defender's appearance and whether it has two legs or four; your choices don't affect the defender's game statistics.\n"
            "The defender is Friendly to you and your allies and obeys you. It vanishes if you die.\n"
            "The Defender in Combat. In combat, the defender acts during your turn. It can move and take its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action. If you have the Incapacitated condition, the defender acts on its own and isn't limited to the Dodge action.\n"
            "Restoring or Replacing the Defender. If the defender has died within the last hour, you can take a Magic action to touch it and expend a spell slot. The defender returns to life after 1 minute with all its Hit Points restored.\n"
            "Whenever you finish a Long Rest, you can create a new defender if you have Smith's Tools in hand. If you already have a defender from this feature, the first one vanishes.\n"
            "Steel Defender\n"
            "Medium Construct\n"
            "Armor Class: 12 + your Intelligence modifier\n"
            "Hit Points: HP 5 + five times your Artificer level (the defender has a number of Hit Dice [d8s] equal to your Artificer level)\n"
            "Speed: Speed 40 ft.\n"
            "STR (Mod/Save)	DEX (Mod/Save)	CON (Mod/Save)	INT (Mod/Save)	WIS (Mod/Save)	CHA (Mod/Save)\n"
            "14 (+2/+2)	12 (+1/+1)	14 (+2/+2)	4 (−3/-3)	10 (+0/+0)	6 (-2/-2)\n"
            "Immunities: Poison; Charmed, Exhaustion, Poisoned\n"
            "Senses: Darkvision 60 ft., Passive Perception 10\n"
            "Languages: Understands the languages you know\n"
            "Challenge Rating: None (XP 0; PB equals your Proficiency Bonus)\n"
            "Traits\n"
            "Steel Bond. Add your Proficiency Bonus to any ability check or saving throw the Steel Defender makes.\n"
            "Actions\n"
            "Force-Empowered Rend. Melee Attack Roll: Bonus equals your spell attack modifier, reach 5 ft. Hit: 1d8 + 2 plus your Intelligence modifier Force damage.\n"
            "Repair (3/Day). The defender, or one Construct or object it can see within 5 feet of it, regains a number of Hit Points equal to 2d8 plus your Intelligence modifier.\n"
            "Reactions\n"
            "Deflect Attack. Trigger: A creature the defender can see within 5 feet of it makes an attack roll targeting a different creature. Response: The triggering creature makes the attack roll with Disadvantage."
        )
        return description


class BattleSmithExtraAttack(TextFeature):
    def __init__(self):
        super().__init__(name="Extra Attack", origin="Battle Smith Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can attack twice instead of once whenever you take the Attack action on your turn. You can forgo one of your attacks when you take the Attack action to command your Steel Defender to take the Force-Empowered Rend action."
        return description


class ArcaneJolt(TextFeature):
    def __init__(self):
        super().__init__(name="Arcane Jolt", origin="Battle Smith Artificer Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When either you hit a target with an attack roll using a magic weapon or your Steel Defender hits a target, you can channel magical energy through the strike to create one of the following effects:\n"
            "Destructive Energy. The target takes an extra 2d6 Force damage.\n"
            "Restorative Energy. Choose one creature or object you can see within 30 feet of the target. Healing energy flows into the chosen recipient, restoring 2d6 Hit Points to it.\n"
            "You can use this energy a number of times equal to your Intelligence modifier (minimum of once), but you can do so no more than once per turn. You regain all expended uses when you finish a Long Rest."
        )
        return description


class ImprovedDefender(TextFeature):
    def __init__(self):
        super().__init__(
            name="Improved Defender", origin="Battle Smith Artificer Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Arcane Jolt and Steel Defender have become more powerful, granting these benefits.\n"
            "Improved Jolt. The extra damage and healing of your Arcane Jolt both increase to 4d6.\n"
            "Improved Deflection. Whenever your Steel Defender uses its Deflect Attack, the attacker takes Force damage equal to 1d4 plus your Intelligence modifier."
        )
        return description


### Cartographer Artificer Features ###


class CartographerToolsOfTheTrade(TextFeature):
    def __init__(self):
        super().__init__(
            name="Tools of the Trade", origin="Cartographer Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Tool Proficiency. You gain proficiency with Calligrapher's Supplies and Cartographer's Tools. If you already have one of these proficiencies, you gain proficiency with one other type of Artisan's Tools of your choice (or with two other types if you have both).\n"
            "Scroll Crafting. When you scribe a Spell Scroll using the crafting rules in the Player's Handbook, the amount of time required to craft it is halved."
        )
        return description


class CartographerSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Cartographer Spells", origin="Cartographer Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Cartographer Spells table, you thereafter always have the listed spells prepared.\n"
            "Cartographer Spells\n"
            "Artificer Level	Spells\n"
            "3	Faerie Fire, Guiding Bolt, Healing Word\n"
            "5	Locate Object, Mind Spike\n"
            "9	Call Lightning, Clairvoyance\n"
            "13	Banishment, Locate Creature\n"
            "17	Scrying, Teleportation Circle"
        )
        return description


class AdventurersAtlas(TextFeature):
    def __init__(self):
        super().__init__(
            name="Adventurer's Atlas", origin="Cartographer Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you finish a Long Rest while holding Cartographer's Tools, you can use that tool to create a set of magical maps by touching at least two creatures (one of whom can be yourself), up to a maximum number of creatures equal to 1 plus your Intelligence modifier (minimum of two creatures). Each target receives a magical map, which constantly updates to show the relative position of all the map holders but is illegible to all others. The maps last until you die or until you use this feature again, at which point any existing maps created by this feature immediately vanish.\n"
            "While carrying the map, a target gains the following benefits.\n"
            "Awareness. The target adds 1d4 to its Initiative rolls.\n"
            "Positioning. The target knows the location of all other map holders that are on the same plane of existence as itself. When casting a spell or creating another effect that requires being able to see the effect's target, a map holder can target another map holder regardless of sight or cover, so long as the other map holder is still within the effect's range."
        )
        return description


class MappingMagic(TextFeature):
    def __init__(self):
        super().__init__(name="Mapping Magic", origin="Cartographer Artificer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Illuminated Cartography. You can cast Faerie Fire without expending a spell slot, outlining the affected creatures as if in ink. You can do so a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "Portal Jump. On your turn, you can spend an amount of movement equal to half your Speed (round down) to teleport to an unoccupied space you can see within 10 feet of yourself or within 5 feet of a creature that is within 30 feet of you and holding one of your Adventurer's Atlas maps. You can't use this benefit if your Speed is 0."
        )
        return description


class GuidedPrecision(TextFeature):
    def __init__(self):
        super().__init__(
            name="Guided Precision", origin="Cartographer Artificer Level 5"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Once per turn, whenever you cast a spell from your Cartographer Spells list or hit a creature affected by your Faerie Fire with an attack roll, you can add your Intelligence modifier to one damage roll of the spell or attack.\n"
            "In addition, taking damage can't cause you to lose Concentration on Faerie Fire."
        )
        return description


class IngeniousMovement(TextFeature):
    def __init__(self):
        super().__init__(
            name="Ingenious Movement", origin="Cartographer Artificer Level 9"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use your Flash of Genius, you or a willing creature of your choice that you can see within 30 feet of yourself can teleport up to 30 feet to an unoccupied space you can see as part of that same Reaction."
        return description


class SuperiorAtlas(TextFeature):
    def __init__(self):
        super().__init__(
            name="Superior Atlas", origin="Cartographer Artificer Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Adventurer's Atlas improves, gaining the following benefits.\n"
            "Safe Haven. When a map holder would be reduced to 0 Hit Points but not killed outright, that creature can destroy its map. The creature's Hit Points instead change to a number equal to twice your Artificer level, and the creature is teleported to an unoccupied space within 5 feet of you or another map holder of its choice.\n"
            "Unerring Path. If you are one of the map holders for your Adventurer's Atlas, you can cast Find the Path without expending a spell slot, without preparing the spell, and without needing spell components. Once you use this benefit, you can't use it again until you finish a Long Rest."
        )
        return description
