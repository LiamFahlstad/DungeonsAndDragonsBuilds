import Core.Definitions as Definitions
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class ExpandedSpellList(Feature):
    def __init__(self):
        super().__init__(
            name="Expanded Spell List", origin="The Fathomless Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The Fathomless lets you choose from an expanded list of spells when you learn a Warlock spell. The following spells are added to the Warlock spell list for you.\n"
            "Fathomless Expanded Spells\n"
            "Spell Level\tSpells\n"
            "1st\tCreate or Destroy Water, Thunderwave\n"
            "2nd\tGust of Wind, Silence\n"
            "3rd\tLightning Bolt, Sleet Storm\n"
            "4th\tControl Water, Summon Elemental (Water only)\n"
            "5th\tBigby's Hand (appears as a tentacle), Cone of Cold"
        )
        return description


class TentacleOfTheDeep(Feature):
    def __init__(self):
        super().__init__(
            name="Tentacle of the Deep", origin="The Fathomless Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        damage = "2d8" if warlock_level >= 10 else "1d8"
        description = (
            "You can magically summon a spectral tentacle that strikes at your foes. As a bonus action, you create a 10-foot-long tentacle at a point you can see within 60 feet of you. The tentacle lasts for 1 minute or until you use this feature to create another tentacle.\n"
            "\n"
            f"When you create the tentacle, you can make a melee spell attack against one creature within 10 feet of it. On a hit, the target takes {damage} cold damage, and its speed is reduced by 10 feet until the start of your next turn. When you reach 10th level in this class, the damage increases to 2d8.\n"
            "\n"
            "As a bonus action on your turn, you can move the tentacle up to 30 feet and repeat the attack.\n"
            "\n"
            f"You can summon the tentacle a number of times equal to your proficiency bonus ({proficiency_bonus}), and you regain all expended uses when you finish a long rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus, regain_all_on="long rest", max_box_count=6, current_formula="Current amount: equal to your proficiency bonus.")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        damage = "2d8" if warlock_level >= 10 else "1d8"
        return [
            ("Action", "Bonus action to summon"),
            ("Range", "60 feet from you"),
            ("Attack", f"Melee spell attack within 10 feet of tentacle"),
            ("Damage", f"{damage} cold + 10 feet speed reduction"),
            ("Movement", "Bonus action to move up to 30 feet, repeat attack"),
            ("Uses", f"Proficiency bonus ({proficiency_bonus})"),
            ("Recharge", "Long rest"),
        ]


class GiftOfTheSea(Feature):
    def __init__(self):
        super().__init__(
            name="Gift of the Sea", origin="The Fathomless Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain a swimming speed of 40 feet, and you can breathe underwater."
        return description


class OceanicSoul(Feature):
    def __init__(self):
        super().__init__(
            name="Oceanic Soul", origin="The Fathomless Patron Warlock Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You are now even more at home in the depths. You gain resistance to cold damage. In addition, when you are fully submerged, any creature that is also fully submerged can understand your speech, and you can understand theirs."
        )
        return description


class GuardianCoil(Feature):
    def __init__(self):
        super().__init__(
            name="Guardian Coil", origin="The Fathomless Patron Warlock Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        damage = "2d8" if warlock_level >= 10 else "1d8"
        description = (
            f"Your Tentacle of the Deep can defend you and others, interposing itself between them and harm. When you or a creature you can see takes damage while within 10 feet of the tentacle, you can use your reaction to choose one of those creatures and reduce the damage to that creature by {damage}. When you reach 10th level in this class, the damage reduced by the tentacle increases to 2d8."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        damage = "2d8" if warlock_level >= 10 else "1d8"
        return [
            ("Trigger", "Damage taken within 10 feet of tentacle"),
            ("Type", "Reaction"),
            ("Effect", f"Reduce damage to chosen creature by {damage}"),
        ]


class GraspingTentacles(Feature):
    def __init__(self):
        super().__init__(
            name="Grasping Tentacles", origin="The Fathomless Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        description = (
            "You learn the spell Evard's Black Tentacles. It counts as a Warlock spell for you, but it doesn't count against the number of spells you know. You can also cast it once without using a spell slot, and you regain the ability to do so when you finish a long rest.\n"
            "\n"
            f"Whenever you cast this spell, your patron's magic bolsters you, granting you a number of temporary hit points equal to your Warlock level ({warlock_level}). Moreover, damage can't break your concentration on this spell."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        warlock_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.WARLOCK
        )
        return [
            ("Spell", "Evard's Black Tentacles"),
            ("Counts", "Warlock spell, doesn't count against known"),
            ("Casting", "Once per long rest without spell slot"),
            ("Temp HP", f"Warlock level ({warlock_level})"),
            ("Concentration", "Damage can't break it"),
        ]


class FathomlessPlunge(Feature):
    def __init__(self):
        super().__init__(
            name="Fathomless Plunge", origin="The Fathomless Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can magically open temporary conduits to watery destinations. As an action, you can teleport yourself and up to five other willing creatures that you can see within 30 feet of you. Amid a whirl of tentacles, you all vanish and then reappear up to 1 mile away in a body of water you've seen (pond size or larger) or within 30 feet of it, each of you appearing in an unoccupied space within 30 feet of the others.\n"
            "\n"
            "Once you use this feature, you can't use it again until you finish a short or long rest."
        )
        return StringUtils.add_boxes(description, 1, regain_all_on="short or long rest")

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Range", "See creatures within 30 feet"),
            ("Effect", "Teleport self + up to 5 willing creatures"),
            ("Distance", "Up to 1 mile"),
            ("Destination", "Body of water (pond size+) or within 30 feet"),
            ("Recharge", "Short or long rest"),
        ]
