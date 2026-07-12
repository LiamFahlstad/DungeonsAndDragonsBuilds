from typing import Type

import Definitions
from Combat.Definitions import ExtendedCombatantData
from Features.ClassFeatures.Druid.WildShapeForms import format_wild_shape_form
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

DRUID_HIT_DIE = 8


class Spellcasting(Feature):
    def __init__(self):
        super().__init__(name="Spellcasting", origin="Druid Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Spellcasting\n"
            "    * Replacing Cantrips: Change one when you gain a Druid level.\n"
            "    * Replacing Spells: Change one when you finish a Long Rest.\n"
            "    * Regaining Spell Slots: You regain all expended spell slots when you finish a Long Rest.\n"
            "    * Spellcasting Ability: Wisdom"
        )
        return description


class Druidic(Feature):
    def __init__(self):
        super().__init__(name="Druidic", origin="Druid Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know Druidic, the secret language of Druids. While learning this ancient tongue, you also unlocked the magic of communicating with animals; you always have the Speak with Animals spell prepared.\n"
            "You can use Druidic to leave hidden messages. You and others who know Druidic automatically spot such a message. Others spot the message's presence with a successful DC 15 Intelligence (Investigation) check but can't decipher it without magic."
        )
        return description


class PrimalOrder(Feature):
    def __init__(self):
        super().__init__(name="Primal Order", origin="Druid Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have dedicated yourself to one of the following sacred roles of your choice.\n"
            "Magician. You know one extra cantrip from the Druid spell list. In addition, your mystical connection to nature gives you a bonus to your Intelligence (Arcana or Nature) checks. The bonus equals your Wisdom modifier (minimum bonus of +1).\n"
            "Warden. Trained for battle, you gain proficiency with Martial weapons and training with Medium armor."
        )
        return description


class WildShape(Feature):
    def __init__(self, known_forms: list[Type[ExtendedCombatantData]]):
        super().__init__(name="Wild Shape", origin="Druid Level 2")
        self.known_forms = known_forms

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        druid_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.DRUID
        )
        if druid_level >= 17:
            uses = 4
        elif druid_level >= 6:
            uses = 3
        else:
            uses = 2
        known_forms_lines = "\n".join(
            format_wild_shape_form(form, character_stat_block)
            for form in self.known_forms
        )
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
            "Objects. Your ability to handle objects is determined by the form's limbs rather than your own. In addition, you choose whether your equipment falls in your space, merges into your new form, or is worn by it. Worn equipment functions as normal, but the DM decides whether it's practical for the new form to wear a piece of equipment based on the creature's size and shape. Your equipment doesn't change size or shape to match the new form, and any equipment that the new form can't wear must either fall to the ground or merge with the form. Equipment that merges with the form has no effect while you're in that form.\n"
            "\nKnown Forms:\n" + known_forms_lines
        )
        return StringUtils.add_boxes(
            description, uses, regain_x_on=(1, "short rest"), regain_all_on="long rest"
        )


class AdditionalWildShapeForms(Feature):
    def __init__(self, known_forms: list[Type[ExtendedCombatantData]], origin: str):
        super().__init__(name="Additional Known Forms", origin=origin)
        self.known_forms = known_forms

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "\n".join(
            format_wild_shape_form(form, character_stat_block)
            for form in self.known_forms
        )


class WildCompanion(Feature):
    def __init__(self):
        super().__init__(name="Wild Companion", origin="Druid Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can summon a nature spirit that assumes an animal form to aid you. As a Magic action, you can expend a spell slot or a use of Wild Shape to cast the Find Familiar spell without Material components.\n"
            "When you cast the spell in this way, the familiar is Fey and disappears when you finish a Long Rest."
        )
        return description


class WildResurgence(Feature):
    def __init__(self):
        super().__init__(name="Wild Resurgence", origin="Druid Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Once on each of your turns, if you have no uses of Wild Shape left, you can give yourself one use by expending a spell slot (no action required).\n"
            "In addition, you can expend one use of Wild Shape (no action required) to give yourself a level 1 spell slot, but you can't do so again until you finish a Long Rest."
        )
        return description


class ElementalFury(Feature):
    def __init__(self):
        super().__init__(name="Elemental Fury", origin="Druid Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The might of the elements flows through you. You gain one of the following options of your choice.\n"
            "Potent Spellcasting. Add your Wisdom modifier to the damage you deal with any Druid cantrip.\n"
            "Primal Strike. Once on each of your turns when you hit a creature with an attack roll using a weapon or a Beast form's attack in Wild Shape, you can cause the target to take an extra 1d8 Cold, Fire, Lightning, or Thunder damage (choose when you hit)."
        )
        return description


class ImprovedElementalFury(Feature):
    def __init__(self):
        super().__init__(name="Improved Elemental Fury", origin="Druid Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The option you chose for Elemental Fury grows more powerful, as detailed below.\n"
            "Potent Spellcasting. When you cast a Druid cantrip with a range of 10 feet or greater, the spell's range increases by 300 feet.\n"
            "Primal Strike. The extra damage of your Primal Strike increases to 2d8."
        )
        return description


class BeastSpells(Feature):
    def __init__(self):
        super().__init__(name="Beast Spells", origin="Druid Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "While using Wild Shape, you can cast spells in Beast form, except for any spell that has a Material component with a cost specified or that consumes its Material component."
        return description


class Archdruid(Feature):
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
