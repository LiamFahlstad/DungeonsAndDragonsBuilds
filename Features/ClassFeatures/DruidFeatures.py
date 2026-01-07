from Features.BaseFeatures import TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock

BARBARIAN_HIT_DIE = 8


class Spellcasting(TextFeature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Druid Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Spellcasting\n"
            " * Replacing Cantrips: Change one when you gain a Druid level.\n"
            " * Replacing Spells: Change one when you finish a Long Rest.\n"
            " * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
            " * Spellcasting Ability: Wisdom"
        )
        return description


class Druidic(TextFeature):
    def __init__(self):
        super().__init__(name="Druidic", origin="Druid Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know Druidic, the secret language of Druids. While learning this ancient tongue, you also unlocked the magic of communicating with animals; you always have the Speak with Animals spell prepared.\n"
            "You can use Druidic to leave hidden messages. You and others who know Druidic automatically spot such a message. Others spot the message's presence with a successful DC 15 Intelligence (Investigation) check but can't decipher it without magic."
        )
        return description


class PrimalOrder(TextFeature):
    def __init__(self):
        super().__init__(name="Primal Order", origin="Druid Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have dedicated yourself to one of the following sacred roles of your choice.\n"
            "Magician. You know one extra cantrip from the Druid spell list. In addition, your mystical connection to nature gives you a bonus to your Intelligence (Arcana or Nature) checks. The bonus equals your Wisdom modifier (minimum bonus of +1).\n"
            "Warden. Trained for battle, you gain proficiency with Martial weapons and training with Medium armor."
        )
        return description


class WildShape(TextFeature):
    def __init__(self):
        super().__init__(name="Wild Shape", origin="Druid Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The power of nature allows you to assume the form of an animal. As a Bonus Action, you shape-shift into a Beast form that you have learned for this feature (see “Known Forms” below). You stay in that form for a number of hours equal to half your Druid level or until you use Wild Shape again, have the Incapacitated condition, or die. You can also leave the form early as a Bonus Action.\n"
            "Number of Uses. You can use Wild Shape twice. You regain one expended use when you finish a Short Rest, and you regain all expended uses when you finish a Long Rest.\n"
            "You gain additional uses when you reach certain Druid levels, as shown in the Wild Shape column of the Druid Features table.\n"
            "Known Forms. You know four Beast forms for this feature, chosen from among Beast stat blocks that have a maximum Challenge Rating of 1/4 and that lack a Fly Speed (see appendix B for stat block options). The Rat, Riding Horse, Spider, and Wolf are recommended. Whenever you finish a Long Rest, you can replace one of your known forms with another eligible form.\n"
            "When you reach certain Druid levels, your number of known forms and the maximum Challenge Rating for those forms increases, as shown in the Beast Shapes table. In addition, starting at level 8, you can adopt a form that has a Fly Speed.\n"
            "When choosing known forms, you may look in the Monster Manual or elsewhere for eligible Beasts if the Dungeon Master permits you to do so.\n"
            "Rules While Shape-Shifted. While in a form, you retain your personality, memories, and ability to speak, and the following rules apply:\n"
            "Temporary Hit Points. When you assume a Wild Shape form, you gain a number of Temporary Hit Points equal to your Druid level.\n"
            "Game Statistics. Your game statistics are replaced by the Beast's stat block, but you retain your creature type; Hit Points; Hit Point Dice; Intelligence, Wisdom, and Charisma scores; class features; languages; and feats. You also retain your skill and saving throw proficiencies and use your Proficiency Bonus for them, in addition to gaining the proficiencies of the creature. If a skill or saving throw modifier in the Beast's stat block is higher than yours, use the one in the stat block.\n"
            "No Spellcasting. You can't cast spells, but shape-shifting doesn't break your Concentration or otherwise interfere with a spell you've already cast.\n"
            "Objects. Your ability to handle objects is determined by the form's limbs rather than your own. In addition, you choose whether your equipment falls in your space, merges into your new form, or is worn by it. Worn equipment functions as normal, but the DM decides whether it's practical for the new form to wear a piece of equipment based on the creature's size and shape. Your equipment doesn't change size or shape to match the new form, and any equipment that the new form can't wear must either fall to the ground or merge with the form. Equipment that merges with the form has no effect while you're in that form."
        )
        return description


class WildCompanion(TextFeature):
    def __init__(self):
        super().__init__(name="Wild Companion", origin="Druid Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can summon a nature spirit that assumes an animal form to aid you. As a Magic action, you can expend a spell slot or a use of Wild Shape to cast the Find Familiar spell without Material components.\n"
            "When you cast the spell in this way, the familiar is Fey and disappears when you finish a Long Rest."
        )
        return description


class WildResurgence(TextFeature):
    def __init__(self):
        super().__init__(name="Wild Resurgence", origin="Druid Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Once on each of your turns, if you have no uses of Wild Shape left, you can give yourself one use by expending a spell slot (no action required).\n"
            "In addition, you can expend one use of Wild Shape (no action required) to give yourself a level 1 spell slot, but you can't do so again until you finish a Long Rest."
        )
        return description


class ElementalFury(TextFeature):
    def __init__(self):
        super().__init__(name="Elemental Fury", origin="Druid Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The might of the elements flows through you. You gain one of the following options of your choice.\n"
            "Potent Spellcasting. Add your Wisdom modifier to the damage you deal with any Druid cantrip.\n"
            "Primal Strike. Once on each of your turns when you hit a creature with an attack roll using a weapon or a Beast form's attack in Wild Shape, you can cause the target to take an extra 1d8 Cold, Fire, Lightning, or Thunder damage (choose when you hit)."
        )
        return description


class ImprovedElementalFury(TextFeature):
    def __init__(self):
        super().__init__(name="Improved Elemental Fury", origin="Druid Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The option you chose for Elemental Fury grows more powerful, as detailed below.\n"
            "Potent Spellcasting. When you cast a Druid cantrip with a range of 10 feet or greater, the spell's range increases by 300 feet.\n"
            "Primal Strike. The extra damage of your Primal Strike increases to 2d8."
        )
        return description


class BeastSpells(TextFeature):
    def __init__(self):
        super().__init__(name="Beast Spells", origin="Druid Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While using Wild Shape, you can cast spells in Beast form, except for any spell that has a Material component with a cost specified or that consumes its Material component."
        return description


class Archdruid(TextFeature):
    def __init__(self):
        super().__init__(name="Archdruid", origin="Druid Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The vitality of nature constantly blooms within you, granting you the following benefits.\n"
            "Evergreen Wild Shape. Whenever you roll Initiative and have no uses of Wild Shape left, you regain one expended use of it.\n"
            "Nature Magician. You can convert uses of Wild Shape into a spell slot (no action required). Choose a number of your unexpended uses of Wild Shape and convert them into a single spell slot, with each use contributing 2 spell levels. For example, if you convert two uses of Wild Shape, you produce a level 4 spell slot. Once you use this benefit, you can't do so again until you finish a Long Rest.\n"
            "Longevity. The primal magic that you wield causes you to age more slowly. For every ten years that pass, your body ages only one year."
        )
        return description


### Circle of the Land Druid Features ###


class LandsAid(TextFeature):
    def __init__(self):
        super().__init__(name="Land's Aid", origin="Circle of the Land Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you can expend a use of your Wild Shape and choose a point within 60 feet of yourself. Vitality-giving flowers and life-draining thorns appear for a moment in a 10-foot-radius Sphere centered on that point. Each creature of your choice in the Sphere must make a Constitution saving throw against your spell save DC, taking 2d6 Necrotic damage on a failed save or half as much damage on a successful one. One creature of your choice in that area regains 2d6 Hit Points.\n"
            "The damage and healing increase by 1d6 when you reach Druid levels 10 (3d6) and 14 (4d6)."
        )
        return description


class NaturalRecovery(TextFeature):
    def __init__(self):
        super().__init__(
            name="Natural Recovery", origin="Circle of the Land Druid Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can cast one of the level 1+ spells that you have prepared from your Circle Spells feature without expending a spell slot, and you must finish a Long Rest before you do so again.\n"
            "In addition, when you finish a Short Rest, you can choose expended spell slots to recover. The spell slots can have a combined level that is equal to or less than half your Druid level (round up), and none of them can be level 6+. For example, if you're a level 6 Druid, you can recover up to three levels' worth of spell slots. You can recover a level 3 spell slot, a level 2 and a level 1 spell slot, or three level 1 spell slots. Once you recover spell slots with this feature, you can't do so again until you finish a Long Rest."
        )
        return description


class NaturesWard(TextFeature):
    def __init__(self):
        super().__init__(
            name="Nature's Ward", origin="Circle of the Land Druid Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You are immune to the Poisoned condition, and you have Resistance to a damage type associated with your current land choice in the Circle Spells feature, as shown in the Nature's Ward table."
        return description


class NaturesSanctuary(TextFeature):
    def __init__(self):
        super().__init__(
            name="Nature's Sanctuary", origin="Circle of the Land Druid Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Magic action, you can expend a use of your Wild Shape and cause spectral trees and vines to appear in a 15-foot Cube on the ground within 120 feet of yourself. They last there for 1 minute or until you have the Incapacitated condition or die. You and your allies have Half Cover while in that area, and your allies gain the current Resistance of your Nature's Ward while there.\n"
            "As a Bonus Action, you can move the Cube up to 60 feet to ground within 120 feet of yourself."
        )
        return description


### Circle of the Moon Druid Features ###


class CircleForms(TextFeature):
    def __init__(self):
        super().__init__(name="Circle Forms", origin="Circle of the Moon Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can channel lunar magic when you assume a Wild Shape form, granting you the benefits below.\n"
            "Challenge Rating. The maximum Challenge Rating for the form equals your Druid level divided by 3 (round down).\n"
            "Armor Class. Until you leave the form, your AC equals 13 plus your Wisdom modifier if that total is higher than the Beast's AC.\n"
            "Temporary Hit Points. You gain a number of Temporary Hit Points equal to three times your Druid level."
        )
        return description


class CircleoftheMoonSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Circle of the Moon Spells", origin="Circle of the Moon Druid Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Druid level specified in the Circle of the Moon Spells table, you thereafter always have the listed spells prepared.\n"
            "In addition, you can cast the spells from this feature while you're in a Wild Shape form."
        )
        return description


class ImprovedCircleForms(TextFeature):
    def __init__(self):
        super().__init__(
            name="Improved Circle Forms", origin="Circle of the Moon Druid Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "While in a Wild Shape form, you gain the following benefits.\n"
            "Lunar Radiance. Each of your attacks in a Wild Shape form can deal its normal damage type or Radiant damage. You make this choice each time you hit with those attacks.\n"
            "Increased Toughness. You can add your Wisdom modifier to your Constitution saving throws."
        )
        return description


class MoonlightStep(TextFeature):
    def __init__(self):
        super().__init__(
            name="Moonlight Step", origin="Circle of the Moon Druid Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You magically transport yourself, reappearing amid a burst of moonlight. As a Bonus Action, you teleport up to 30 feet to an unoccupied space you can see, and you have Advantage on the next attack roll you make before the end of this turn.\n"
            "You can use this feature a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest. You can also regain uses by expending a level 2+ spell slot for each use you want to restore (no action required)."
        )
        return description


class LunarForm(TextFeature):
    def __init__(self):
        super().__init__(name="Lunar Form", origin="Circle of the Moon Druid Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The power of the moon suffuses you, granting you the following benefits.\n"
            "Improved Lunar Radiance. Once per turn, you can deal an extra 2d10 Radiant damage to a target you hit with a Wild Shape form's attack.\n"
            "Shared Moonlight. Whenever you use Moonlight Step, you can also teleport one willing creature. That creature must be within 10 feet of you, and you teleport it to an unoccupied space you can see within 10 feet of your destination space."
        )
        return description


### Circle of the Sea Druid Features ###


class CircleOfTheSeaSpells(TextFeature):
    def __init__(self):
        super().__init__(
            name="Circle of the Sea Spells", origin="Circle of the Sea Druid Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you reach a Druid level specified in the Circle of the Sea Spells table, you thereafter always have the listed spells prepared."
        return description


class WrathOfTheSea(TextFeature):
    def __init__(self):
        super().__init__(
            name="Wrath of the Sea", origin="Circle of the Sea Druid Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can expend a use of your Wild Shape to manifest a 5-foot Emanation that takes the form of ocean spray that surrounds you for 10 minutes. It ends early if you dismiss it (no action required), manifest it again, or have the Incapacitated condition.\n"
            "When you manifest the Emanation and as a Bonus Action on your subsequent turns, you can choose another creature you can see in the Emanation. The target must succeed on a Constitution saving throw against your spell save DC or take Cold damage and, if the creature is Large or smaller, be pushed up to 15 feet away from you. To determine this damage, roll a number of d6s equal to your Wisdom modifier (minimum of one die)."
        )
        return description


class AquaticAffinity(TextFeature):
    def __init__(self):
        super().__init__(
            name="Aquatic Affinity", origin="Circle of the Sea Druid Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The size of the Emanation created by your Wrath of the Sea increases to 10 feet.\n"
            "In addition, you gain a Swim Speed equal to your Speed."
        )
        return description


class Stormborn(TextFeature):
    def __init__(self):
        super().__init__(name="Stormborn", origin="Circle of the Sea Druid Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Wrath of the Sea confers two more benefits while active, as detailed below.\n"
            "Flight. You gain a Fly Speed equal to your Speed.\n"
            "Resistance. You have Resistance to Cold, Lightning, and Thunder damage."
        )
        return description


class OceanicGift(TextFeature):
    def __init__(self):
        super().__init__(name="Oceanic Gift", origin="Circle of the Sea Druid Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Instead of manifesting the Emanation of Wrath of the Sea around yourself, you can manifest it around one willing creature within 60 feet of yourself. That creature gains all the benefits of the Emanation and uses your spell save DC and Wisdom modifier for it.\n"
            "In addition, you can manifest the Emanation around both the other creature and yourself if you expend two uses of your Wild Shape instead of one when manifesting it."
        )
        return description


### Circle of the Stars Druid Features ###


class StarMap(TextFeature):
    def __init__(self):
        super().__init__(name="Star Map", origin="Circle of the Stars Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You’ve created a star chart as part of your heavenly studies. It is a Tiny object, and you can use it as a Spellcasting Focus for your Druid spells. You determine its form by rolling on the Star Map table or by choosing one.\n"
            "While holding the map, you have the Guidance and Guiding Bolt spells prepared, and you can cast Guiding Bolt without expending a spell slot. You can cast it in that way a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest.\n"
            "If you lose the map, you can perform a 1-hour ceremony to magically create a replacement. This ceremony can be performed during a Short or Long Rest, and it destroys the previous map."
        )
        return description


class StarryForm(TextFeature):
    def __init__(self):
        super().__init__(name="Starry Form", origin="Circle of the Stars Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "As a Bonus Action, you can expend a use of your Wild Shape feature to take on a starry form rather than shape-shifting.\n"
            "While in your starry form, you retain your game statistics, but your body becomes luminous, your joints glimmer like stars, and glowing lines connect them as on a star chart. This form sheds Bright Light in a 10-foot radius and Dim Light for an additional 10 feet. The form lasts for 10 minutes. It ends early if you dismiss it (no action required), have the Incapacitated condition, or use this feature again.\n"
            "Whenever you assume your starry form, choose which of the following constellations glimmers on your body; your choice gives you certain benefits while in the form.\n"
            "Archer. A constellation of an archer appears on you. When you activate this form and as a Bonus Action on your subsequent turns while it lasts, you can make a ranged spell attack, hurling a luminous arrow that targets one creature within 60 feet of yourself. On a hit, the attack deals Radiant damage equal to 1d8 plus your Wisdom modifier.\n"
            "Chalice. A constellation of a life-giving goblet appears on you. Whenever you cast a spell using a spell slot that restores Hit Points to a creature, you or another creature within 30 feet of you can regain Hit Points equal to 1d8 plus your Wisdom modifier.\n"
            "Dragon. A constellation of a wise dragon appears on you. When you make an Intelligence or a Wisdom check or a Constitution saving throw to maintain Concentration, you can treat a roll of 9 or lower on the d20 as a 10."
        )
        return description


class CosmicOmen(TextFeature):
    def __init__(self):
        super().__init__(name="Cosmic Omen", origin="Circle of the Stars Druid Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you finish a Long Rest, you can consult your Star Map for omens and roll a die. Until you finish your next Long Rest, you gain access to a special Reaction based on whether you rolled an even or an odd number on the die:\n"
            "Weal (Even). Whenever a creature you can see within 30 feet of you is about to make a D20 Test, you can take a Reaction to roll 1d6 and add the number rolled to the total.\n"
            "Woe (Odd). Whenever a creature you can see within 30 feet of you is about to make a D20 Test, you can take a Reaction to roll 1d6 and subtract the number rolled from the total.\n"
            "You can use this Reaction a number of times equal to your Wisdom modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        )
        return description


class TwinklingConstellations(TextFeature):
    def __init__(self):
        super().__init__(
            name="Twinkling Constellations", origin="Circle of the Stars Druid Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The constellations of your Starry Form improve. The 1d8 of the Archer and the Chalice becomes 2d8, and while the Dragon is active, you have a Fly Speed of 20 feet and can hover.\n"
            "Moreover, at the start of each of your turns while in your Starry Form, you can change which constellation glimmers on your body."
        )
        return description


class FullOfStars(TextFeature):
    def __init__(self):
        super().__init__(
            name="Full of Stars", origin="Circle of the Stars Druid Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While in your Starry Form, you become partially incorporeal, giving you Resistance to Bludgeoning, Piercing, and Slashing damage."
        return description
