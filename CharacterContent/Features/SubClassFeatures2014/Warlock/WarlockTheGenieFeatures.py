import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

_WRATH_DAMAGE_TYPE = {
    Definitions.WarlockGenieKind.DAO: "bludgeoning",
    Definitions.WarlockGenieKind.DJINNI: "thunder",
    Definitions.WarlockGenieKind.EFREETI: "fire",
    Definitions.WarlockGenieKind.MARID: "cold",
}


class GenieExpandedSpells(Feature):
    def __init__(self, kind: Definitions.WarlockGenieKind):
        super().__init__(
            name="Expanded Spell List", origin="The Genie Patron Warlock Level 3"
        )
        self.kind = kind

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Genie lets you choose from an expanded list of spells when you learn a Warlock spell. The Genie Expanded Spells table shows the genie spells that are added to the Warlock spell list for you, along with the spells associated in the table with your patron's kind: Dao, Djinni, Efreeti, or Marid.\n"
            "Genie Expanded Spells\n"
            "Spell Level\tGenie Spells\tDao Spells\tDjinni Spells\tEfreeti Spells\tMarid Spells\n"
            "1st\tDetect Evil and Good\tSanctuary\tThunderwave\tBurning Hands\tFog Cloud\n"
            "2nd\tPhantasmal Force\tSpike Growth\tGust of Wind\tScorching Ray\tBlur\n"
            "3rd\tCreate Food and Water\tMeld into Stone\tWind Wall\tFireball\tSleet Storm\n"
            "4th\tPhantasmal Killer\tStone Shape\tGreater Invisibility\tFire Shield\tControl Water\n"
            "5th\tCreation\tWall of Stone\tSeeming\tFlame Strike\tCone of Cold\n"
            "9th\tWish\t—\t—\t—\t—\n"
            f"You have chosen the {self.kind.value} kind, so the Genie spells and the {self.kind.value} spells are always added to your Warlock spell list."
        )
        return description


class GeniesVessel(Feature):
    def __init__(self, kind: Definitions.WarlockGenieKind):
        super().__init__(
            name="Genie's Vessel", origin="The Genie Patron Warlock Level 3"
        )
        self.kind = kind

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        vessel_hp = warlock_level + proficiency_bonus
        damage_type = _WRATH_DAMAGE_TYPE[self.kind]
        description = (
            "Also at 1st level, your patron gifts you a magical vessel that grants you a measure of the genie's power. The vessel is a Tiny object, and you can use it as a spellcasting focus for your Warlock spells. You decide what the object is (an oil lamp, an urn, a ring with a compartment, a stoppered bottle, a hollow statuette, an ornate lantern, or another vessel of your choice).\n"
            "\n"
            "While you are touching the vessel, you can use it in the following ways:\n"
            "\n"
            "Bottled Respite. As an action, you can magically vanish and enter your vessel, which remains in the space you left. The interior of the vessel is an extradimensional space in the shape of a 20-foot-radius cylinder, 20 feet high, and resembles your vessel. The interior is appointed with cushions and low tables and is a comfortable temperature. While inside, you can hear the area around your vessel as if you were in its space. You can remain inside the vessel up to a number of hours equal to twice your proficiency bonus. You exit the vessel early if you use a bonus action to leave, if you die, or if the vessel is destroyed. When you exit the vessel, you appear in the unoccupied space closest to it. Any objects left in the vessel remain there until carried out, and if the vessel is destroyed, every object stored there harmlessly appears in the unoccupied spaces closest to the vessel's former space. Once you enter the vessel, you can't enter again until you finish a long rest.\n"
            "\n"
            f"Genie's Wrath. Once during each of your turns when you hit with an attack roll, you can deal extra damage to the target equal to your proficiency bonus ({proficiency_bonus}). The type of this damage is determined by your patron: bludgeoning (Dao), thunder (Djinni), fire (Efreeti), or cold (Marid).\n"
            "\n"
            f"The vessel's AC equals your spell save DC. Its hit points equal your Warlock level plus your proficiency bonus ({vessel_hp}), and it is immune to poison and psychic damage.\n"
            "\n"
            "If the vessel is destroyed or you lose it, you can perform a 1-hour ceremony to receive a replacement from your patron. This ceremony can be performed during a short or long rest, and the previous vessel is destroyed if it still exists. The vessel vanishes in a flare of elemental power when you die.\n"
            "\n"
            f"You have chosen the {self.kind.value} kind, so your Genie's Wrath deals {damage_type} damage."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")


class ElementalGift(Feature):
    def __init__(self, kind: Definitions.WarlockGenieKind):
        super().__init__(
            name="Elemental Gift", origin="The Genie Patron Warlock Level 6"
        )
        self.kind = kind

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        damage_type = _WRATH_DAMAGE_TYPE[self.kind]
        description = (
            "At 6th level, you begin to take on characteristics of your patron's kind. You now have resistance to a damage type determined by your patron's kind: bludgeoning (Dao), thunder (Djinni), fire (Efreeti), or cold (Marid).\n"
            "\n"
            "In addition, as a bonus action, you can give yourself a flying speed of 30 feet that lasts for 10 minutes, during which you can hover. You can use this bonus action a number of times equal to your proficiency bonus, and you regain all expended uses when you finish a long rest.\n"
            "\n"
            f"You have chosen the {self.kind.value} kind, so you have resistance to {damage_type} damage. You can use the flying speed bonus action a number of times equal to your proficiency bonus ({proficiency_bonus})."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        damage_type = _WRATH_DAMAGE_TYPE[self.kind]
        return [
            ("Resistance", f"{damage_type.capitalize()} damage"),
            ("Action", "Bonus action for flying speed"),
            ("Flying Speed", "30 feet"),
            ("Duration", "10 minutes (can hover)"),
            ("Uses", f"Proficiency bonus ({proficiency_bonus})"),
            ("Recharge", "Long rest"),
        ]


class SanctuaryVessel(Feature):
    def __init__(self):
        super().__init__(
            name="Sanctuary Vessel", origin="The Genie Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "At 10th level, when you enter your Genie's Vessel via the Bottled Respite feature, you can now choose up to five willing creatures that you can see within 30 feet of you, and the chosen creatures are drawn into the vessel with you.\n"
            "\n"
            "As a bonus action, you can eject any number of creatures from the vessel, and everyone is ejected if you leave or die or if the vessel is destroyed.\n"
            "\n"
            f"In addition, anyone (including you) who remains within the vessel for at least 10 minutes gains the benefit of finishing a short rest, and anyone can add your proficiency bonus ({proficiency_bonus}) to the number of hit points they regain if they spend any Hit Dice as part of a short rest there."
        )
        return description


class LimitedWish(Feature):
    def __init__(self):
        super().__init__(
            name="Limited Wish", origin="The Genie Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 14th level, you entreat your patron to grant you a small wish. As an action, you can speak your desire to your Genie's Vessel, requesting the effect of one spell that is 6th level or lower and has a casting time of 1 action. The spell can be from any class's spell list, and you don't need to meet the requirements in that spell, including costly components: the spell simply takes effect as part of this action.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish 1d4 long rests."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="1d4 long rests")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action (speak to Genie's Vessel)"),
            ("Spell Level", "6th level or lower"),
            ("Casting Time", "1 action"),
            ("Source", "Any class's spell list"),
            ("Requirements", "Don't need to meet spell requirements"),
            ("Components", "Costly components waived"),
            ("Recharge", "1d4 long rests"),
        ]
