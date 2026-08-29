from enum import Enum
from typing import Type

from CharacterContent.Features.ClassFeatures.Druid.WildShapeForms import (
    format_wild_shape_form,
)
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureUses, FeatureActivation
from CharacterContent.Features.Core.Improvements import GrantLanguage
from Combat.Definitions import ExtendedCombatantData
from Core.Definitions import Language
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class PrimalOrderType(str, Enum):
    MAGICIAN = "Magician"
    WARDEN = "Warden"


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

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Replacing Cantrips", "Change one when you gain a Druid level"),
            ("Replacing Spells", "Change one when you finish a Long Rest"),
            ("Regaining Spell Slots", "Regain all expended slots on Long Rest"),
            ("Spellcasting Ability", "Wisdom"),
        ]


class Druidic(Feature):
    def __init__(self):
        super().__init__(name="Druidic", origin="Druid Level 1")
        self._language = GrantLanguage(Language.DRUIDIC, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._language.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You know Druidic, the secret language of Druids. While learning this ancient tongue, you also unlocked the magic of communicating with animals; you always have the Speak with Animals spell prepared.\n"
            "You can use Druidic to leave hidden messages. You and others who know Druidic automatically spot such a message. Others spot the message's presence with a successful DC 15 Intelligence (Investigation) check but can't decipher it without magic."
        )
        return description


class PrimalOrder(Feature):
    def __init__(self, order: PrimalOrderType = PrimalOrderType.MAGICIAN):
        super().__init__(
            name="Primal Order", origin="Druid Level 1", usage_tags=["buff"]
        )
        self.order = order

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        if self.order == PrimalOrderType.WARDEN:
            return (
                "Warden. Trained for battle, you gain proficiency with Martial weapons "
                "and training with Medium armor."
            )
        return (
            "Magician. You know one extra cantrip from the Druid spell list. In addition, "
            "your mystical connection to nature gives you a bonus to your Intelligence "
            "(Arcana or Nature) checks. The bonus equals your Wisdom modifier (minimum bonus of +1)."
        )


class WildShape(Feature):
    def __init__(self, known_forms: list[Type[ExtendedCombatantData]]):
        super().__init__(
            name="Wild Shape",
            origin="Druid Level 2",
            activation=FeatureActivation(action_type="bonus_action", duration="Until You Leave Form or are Incapacitated"),
            usage_tags=["heal"],
            uses=FeatureUses(
                max_uses=4,
                regain_x_on=(1, "short rest"),
                regain_all_on="long rest",
                current_formula="Current amount: determined by your Druid level — 2 uses at levels 2-5, 3 at 6-16, 4 at 17+.",
            ),
        )
        self.known_forms = known_forms

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        known_forms_lines = "\n".join(
            format_wild_shape_form(form, character_stat_block)
            for form in self.known_forms
        )
        description = (
            "The power of nature allows you to assume the form of an animal. As a Bonus Action, you shape-shift into a Beast form that you have learned for this feature (see “Known Forms” below). You stay in that form for a number of hours equal to half your Druid level or until you use Wild Shape again, have the Incapacitated condition, or die. You can also leave the form early as a Bonus Action.\n"
            "Number of Uses. You can use Wild Shape. You regain one expended use when you finish a Short Rest, and you regain all expended uses when you finish a Long Rest.\n"
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
        return description

    def get_resource_tiles(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, list[tuple[str, str]]]]:
        uses_by_level = {}
        for level in range(2, 21):
            if level >= 17:
                uses_by_level[level] = 4
            elif level >= 6:
                uses_by_level[level] = 3
            else:
                uses_by_level[level] = 2
        steps = [
            (f"Lv {level_range}", str(value))
            for level_range, value in StringUtils.compress_level_progression(
                uses_by_level
            )
        ]
        return [("Wild Shape Uses", steps)]


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
        super().__init__(
            name="Wild Companion",
            origin="Druid Level 2",
            activation=FeatureActivation(action_type="action", duration="Until Long Rest"),
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can summon a nature spirit that assumes an animal form to aid you. As a Magic action, you can expend a spell slot or a use of Wild Shape to cast the Find Familiar spell without Material components.\n"
            "When you cast the spell in this way, the familiar is Fey and disappears when you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            (
                "What",
                "Cast Find Familiar by expending a spell slot or a use of Wild Shape",
            ),
            ("Casting Time", "Magic action"),
            ("Cost", "1 spell slot or 1 Wild Shape use"),
            ("Components", "None (Material components waived)"),
            ("Duration", "Familiar is Fey; disappears on Long Rest"),
        ]


class WildResurgence(Feature):
    def __init__(self):
        super().__init__(name="Wild Resurgence", origin="Druid Level 5")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Once on each of your turns, if you have no uses of Wild Shape left, you can give yourself one use by expending a spell slot (no action required).\n"
            "In addition, you can expend one use of Wild Shape (no action required) to give yourself a level 1 spell slot, but you can't do so again until you finish a Long Rest."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            (
                "Option 1",
                "Expend spell slot (no action, once per turn) if no Wild Shape uses left → gain 1 Wild Shape use",
            ),
            (
                "Option 2",
                "Expend 1 Wild Shape use (no action, once per Long Rest) → gain 1 level 1 spell slot",
            ),
        ]


class PotentSpellcasting(Feature):
    def __init__(self):
        super().__init__(
            name="Potent Spellcasting", origin="Druid Level 7", usage_tags=["damage"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Add your Wisdom modifier to the damage you deal with any Druid cantrip."
        )
        return description


class PrimalStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Primal Strike", origin="Druid Level 7", usage_tags=["damage"]
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Once on each of your turns when you hit a creature with an attack roll using a weapon or a Beast "
            "form's attack in Wild Shape, you can cause the target to take an extra 1d8 Cold, Fire, Lightning, "
            "or Thunder damage (choose when you hit)."
        )
        return description


class ImprovedPotentSpellcasting(Feature):
    def __init__(self):
        super().__init__(name="Improved Potent Spellcasting", origin="Druid Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast a Druid cantrip with a range of 10 feet or greater, the spell's range increases by 300 feet."
        return description


class ImprovedPrimalStrike(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Primal Strike",
            origin="Druid Level 15",
            usage_tags=["damage"],
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The extra damage of your Primal Strike increases to 2d8."
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

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            (
                "Evergreen Wild Shape",
                "On Initiative roll with no Wild Shape uses left: regain 1 use",
            ),
            (
                "Nature Magician",
                "Convert unexpended Wild Shape uses to spell slot (no action, 2 spell levels per use, once per Long Rest)",
            ),
            ("Longevity", "Age 1 year for every 10 years that pass"),
        ]
