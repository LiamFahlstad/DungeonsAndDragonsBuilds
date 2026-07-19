from Definitions import ARTIFICER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ArtilleristToolsOfTheTrade(Feature):
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


class ArtilleristSpells(Feature):
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


class EldritchCannon(Feature):
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


class ArcaneFirearm(Feature):
    def __init__(self):
        super().__init__(name="Arcane Firearm", origin="Artillerist Artificer Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you finish a Long Rest, you can use Woodcarver's Tools to carve special sigils into a Rod, Staff, Wand, or Martial Ranged weapon and thereby turn it into your Arcane Firearm. The sigils disappear from the object if you later carve them on a different item. The sigils otherwise last indefinitely.\n"
            "You can use your Arcane Firearm as a Spellcasting Focus for your Artificer spells. When you cast an Artificer spell through the firearm, roll 1d8, and you gain a bonus to one of the spell's damage rolls equal to the number rolled."
        )
        return description


class ExplosiveCannon(Feature):
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


class FortifiedPosition(Feature):
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
