import Core.Definitions as Definitions
from Core.Definitions import SORCERER_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature, FeatureActivation, ActionType
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class PsionicSpells(Feature):
    def __init__(self):
        super().__init__(name="Psionic Spells", origin="Aberrant Mind Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You learn additional spells when you reach certain levels in this class, as shown on the Psionic Spells table. Each of these spells counts as a sorcerer spell for you, but it doesn't count against the number of sorcerer spells you know.\n"
            "\n"
            "Whenever you gain a sorcerer level, you can replace one spell you gained from this feature with another spell of the same level. The new spell must be a divination or an enchantment spell from the sorcerer, warlock, or wizard spell list.\n"
            "\n"
            "Psionic Spells\n"
            "Sorcerer Level\tSpells\n"
            "1st\tArms of Hadar, Dissonant Whispers, Mind Sliver\n"
            "3rd\tCalm Emotions, Detect Thoughts\n"
            "5th\tHunger of Hadar, Sending\n"
            "7th\tEvard's Black Tentacles, Summon Aberration\n"
            "9th\tRary's Telepathic Bond, Telekinesis"
        )
        return description


class TelepathicSpeech(Feature):
    def __init__(self):
        super().__init__(name="Telepathic Speech", origin="Aberrant Mind Sorcerer Level 3", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="Sorcerer Level Minutes", range="30 Feet"), usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can form a telepathic connection between your mind and the mind of another. As a bonus action, choose one creature you can see within 30 feet of you. You and the chosen creature can speak telepathically with each other while the two of you are within a number of miles of each other equal to your Charisma modifier (minimum of 1 mile). To understand each other, you each must speak mentally in a language the other knows.\n"
            "\n"
            "The telepathic connection lasts for a number of minutes equal to your sorcerer level. It ends early if you are incapacitated or die or if you use this ability to form a connection with a different creature."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        charisma_modifier = character_stat_block.get_charisma_modifier()
        sorcerer_level = character_stat_block.get_class_level(Definitions.CharacterClass.SORCERER)
        return [
            ("Action", "Bonus action"),
            ("Range", "30 feet"),
            ("Distance", f"Charisma modifier miles (min 1 mile) = {max(1, charisma_modifier)} mile(s)"),
            ("Duration", f"{sorcerer_level} minute(s)"),
            ("Ends Early", "If incapacitated, dead, or you form another connection"),
        ]


class PsionicSorcery(Feature):
    def __init__(self):
        super().__init__(name="Psionic Sorcery", origin="Aberrant Mind Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast any spell of 1st level or higher from your Psionic Spells feature, you can cast it by expending a spell slot as normal or by spending a number of sorcery points equal to the spell's level. If you cast the spell using sorcery points, it requires no verbal or somatic components, and it requires no material components, unless they are consumed by the spell."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("What", "Cast spells from Psionic Spells (1st level or higher)"),
            ("Cost", "Spell slot OR sorcery points equal to spell level"),
            ("Verbal Component", "Not required if using sorcery points"),
            ("Somatic Component", "Not required if using sorcery points"),
            ("Material Component", "Waived if using sorcery points (unless consumed)"),
        ]


class PsychicDefenses(Feature):
    def __init__(self):
        super().__init__(name="Psychic Defenses", origin="Aberrant Mind Sorcerer Level 6", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You gain resistance to psychic damage, and you have advantage on saving throws against being charmed or frightened."
        return description


class RevelationInFlesh(Feature):
    def __init__(self):
        super().__init__(name="Revelation in Flesh", origin="Aberrant Mind Sorcerer Level 14", activation=FeatureActivation(action_type=ActionType.BONUS_ACTION, duration="10 Minutes", range="60 Feet"), usage_tags=["utility"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can unleash the aberrant truth hidden within yourself. As a bonus action, you can spend 1 or more sorcery points to magically transform your body for 10 minutes. For each sorcery point you spend, you can gain one of the following benefits of your choice, the effects of which last until the transformation ends:\n"
            "\n"
            "    * You can see any invisible creature within 60 feet of you, provided it isn't behind total cover. Your eyes also turn black or become writhing sensory tendrils.\n"
            "    * You gain a flying speed equal to your walking speed and can hover. As you fly, your skin glistens with mucus or shines with an otherworldly light.\n"
            "    * You gain a swimming speed equal to twice your walking speed, and you can breathe underwater. Moreover, gills grow from your neck or fan out from behind your ears, your fingers become webbed, or you grow writhing cilia that extend through your clothing.\n"
            "    * Your body, along with any equipment you are wearing or carrying, becomes slimy and pliable. You can move through any space as narrow as 1 inch without squeezing, and you can spend 5 feet of movement to escape from nonmagical restraints or being grappled."
        )
        return description


class WarpingImplosion(Feature):
    def __init__(self):
        super().__init__(name="Warping Implosion", origin="Aberrant Mind Sorcerer Level 18", activation=FeatureActivation(action_type=ActionType.ACTION, range="120 Feet"), usage_tags=["damage", "control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can unleash your aberrant power as a space-warping anomaly. As an action, you can teleport to an unoccupied space you can see within 120 feet of you. Immediately after you disappear, each creature within 30 feet of the space you left must make a Strength saving throw against your spell save DC. On a failed save, a creature takes 3d10 force damage and is pulled straight toward the space you left, ending in an unoccupied space as close to your former space as possible. On a successful save, the creature takes half as much damage and isn't pulled.\n"
            "\n"
            "Once you use this feature, you can't do so again until you finish a long rest, unless you spend 5 sorcery points to use it again."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Action"),
            ("Teleport Range", "120 feet"),
            ("Save", "Strength saving throw vs spell save DC"),
            ("On Failed Save", "3d10 force damage and pulled to your former space"),
            ("On Successful Save", "Half damage, not pulled"),
            ("Recharge", "Long rest or 5 sorcery points"),
        ]
