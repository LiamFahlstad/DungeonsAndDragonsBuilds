from Definitions import WARLOCK_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ReplacingEldritchInvocations(Feature):
    def __init__(self):
        super().__init__(
            name="Replacing Eldritch Invocations", origin="Warlock Level 1"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Replacing and Gaining Invocations. Whenever you gain a Warlock level, you can replace one of your invocations with another one for which you qualify. You can't replace an invocation if it's a prerequisite for another invocation that you have.\n"
            "When you gain certain Warlock levels, you gain more invocations of your choice, as shown in the Invocations column of the Warlock Features table.\n"
            "You can't pick the same invocation more than once unless its description says otherwise."
        )
        return description


class ReplacingCantripsAndSpells(Feature):
    def __init__(self):
        super().__init__(name="Replacing Cantrips and Spells", origin="Warlock Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you gain a Warlock level, you can replace one of your cantrips from this feature with another Warlock cantrip of your choice.\n"
            "Whenever you gain a Warlock level, you can replace one spell on your list with another Warlock spell of an eligible level."
        )
        return description


class RegainingSpellSlots(Feature):
    def __init__(self):
        super().__init__(name="Regaining Spell Slots", origin="Warlock Level 1")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You regain all expended Pact Magic spell slots when you finish a Short or Long Rest."
        return description


class MagicalCunning(Feature):
    def __init__(self):
        super().__init__(name="Magical Cunning", origin="Warlock Level 2")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You can perform an esoteric rite for 1 minute. At the end of it, you regain expended Pact Magic spell slots but no more than a number equal to half your maximum (round up). Once you use this feature, you can't do so again until you finish a Long Rest."
        return description


class ContactPatron(Feature):
    def __init__(self):
        super().__init__(name="Contact Patron", origin="Warlock Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "In the past, you usually contacted your patron through intermediaries. Now you can communicate directly; you always have the Contact Other Plane spell prepared. With this feature, you can cast the spell without expending a spell slot to contact your patron, and you automatically succeed on the spell's saving throw.\n"
            "Once you cast the spell with this feature, you can't do so in this way again until you finish a Long Rest."
        )
        return description


class MysticArcanum(Feature):
    def __init__(self):
        super().__init__(name="Mystic Arcanum", origin="Warlock Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your patron grants you a magical secret called an arcanum. Choose one level 6 Warlock spell as this arcanum.\n"
            "You can cast your arcanum spell once without expending a spell slot, and you must finish a Long Rest before you can cast it in this way again.\n"
            "As shown in the Warlock Features table, you gain another Warlock spell of your choice that can be cast in this way when you reach Warlock levels 13 (level 7 spell), 15 (level 8 spell), and 17 (level 9 spell). You regain all uses of your Mystic Arcanum when you finish a Long Rest.\n"
            "Whenever you gain a Warlock level, you can replace one of your arcanum spells with another Warlock spell of the same level."
        )
        return description


class EldritchMaster(Feature):
    def __init__(self):
        super().__init__(name="Eldritch Master", origin="Warlock Level 20")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you use your Magical Cunning feature, you regain all your expended Pact Magic spell slots."
        return description
