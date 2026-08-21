from Core.Definitions import Ability, CharacterClass, DamageType, SORCERER_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import DamageResistance
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class PsionicSpells(Feature):
    def __init__(self):
        super().__init__(name="Psionic Spells", origin="Aberrant Sorcerer Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach a Sorcerer level specified in the Psionic Spells table, you thereafter always have the listed spells prepared.\n"
            "Psionic Spells\n"
            "Sorcerer Level	Spells\n"
            "3	Arms of Hadar, Calm Emotions, Detect Thoughts, Dissonant Whispers, Mind Sliver\n"
            "5	Hunger of Hadar, Sending\n"
            "7	Evard's Black Tentacles, Summon Aberration\n"
            "9	Rary's Telepathic Bond, Telekinesis"
        )
        return description


class TelepathicSpeech(Feature):
    def __init__(self):
        super().__init__(name="Telepathic Speech", origin="Aberrant Sorcerer Level 3", action_type="bonus_action", duration="Minutes Equal to Sorcerer Level", range="30 Feet")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can form a telepathic connection between your mind and the mind of another. As a Bonus Action, choose one creature you can see within 30 feet of yourself. You and the chosen creature can communicate telepathically with each other while the two of you are within a number of miles of each other equal to your Charisma modifier (minimum of 1 mile). To understand each other, you each must mentally use a language the other knows.\n"
            "The telepathic connection lasts for a number of minutes equal to your Sorcerer level. It ends early if you use this ability to form a connection with a different creature."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        charisma_modifier = character_stat_block.get_ability_modifier(Ability.CHARISMA)
        sorcerer_level = character_stat_block.get_class_level(CharacterClass.SORCERER)
        distance = max(1, charisma_modifier)
        return [
            ("Trigger", "Bonus Action"),
            ("Range", "30 feet (to establish)"),
            ("Distance", f"{distance} mile(s) apart"),
            ("Effect", "Telepathic communication (must share a language)"),
            ("Duration", f"{sorcerer_level} minutes"),
            ("Ending", "Establish connection with different creature"),
        ]


class PsionicSorcery(Feature):
    def __init__(self):
        super().__init__(name="Psionic Sorcery", origin="Aberrant Sorcerer Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast any level 1+ spell from your Psionic Spells feature, you can cast it by expending a spell slot as normal or by spending a number of Sorcery Points equal to the spell’s level. If you cast the spell using Sorcery Points, it requires no Verbal or Somatic components, and it requires no Material components unless they are consumed by the spell or have a cost specified in it."
        return description


class PsychicDefenses(Feature):
    def __init__(self):
        super().__init__(name="Psychic Defenses", origin="Aberrant Sorcerer Level 6", skippable_in_concise=True, usage_tags=["buff"])
        self._resistance = DamageResistance(DamageType.PSYCHIC, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._resistance.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Resistance to Psychic damage, and you have Advantage on saving throws to avoid or end the Charmed or Frightened condition."
        return description


class RevelationInFlesh(Feature):
    def __init__(self):
        super().__init__(name="Revelation in Flesh", origin="Aberrant Sorcerer Level 14", action_type="bonus_action", duration="10 Minutes", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can unleash the aberrant truth hidden within yourself. As a Bonus Action, you can spend 1 Sorcery Point or more to magically alter your body for 10 minutes. For each Sorcery Point you spend, you gain one of the following benefits of your choice, the effects of which last until the alteration ends.\n"
            "Aquatic Adaptation. You gain a Swim Speed equal to twice your Speed, and you can breathe underwater. Gills grow from your neck or flare behind your ears, and your fingers become webbed or you grow wriggling cilia.\n"
            "Glistening Flight. You gain a Fly Speed equal to your Speed, and you can hover. As you fly, your skin glistens with mucus or otherworldly light.\n"
            "See the Invisible. You can see any Invisible creature within 60 feet of yourself that isn’t behind Total Cover. Your eyes also turn black or become writhing sensory tendrils.\n"
            "Wormlike Movement. Your body, along with any equipment you are wearing or carrying, becomes slimy and pliable. You can move through any space as narrow as 1 inch, and you can spend 5 feet of movement to escape from nonmagical restraints or the Grappled condition."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus Action"),
            ("Cost", "1+ Sorcery Points (1 per benefit)"),
            ("Duration", "10 minutes"),
            ("Aquatic Adaptation", "Swim Speed = 2x Speed, breathe underwater"),
            ("Glistening Flight", "Fly Speed = Speed, can hover"),
            ("See the Invisible", "See Invisible creatures within 60 feet"),
            ("Wormlike Movement", "Move through 1-inch spaces, escape restraints/grapple"),
        ]


class WarpingImplosion(Feature):
    def __init__(self):
        super().__init__(name="Warping Implosion", origin="Aberrant Sorcerer Level 18", action_type="action", range="120 Feet", usage_tags=["damage", "control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can unleash a space-warping anomaly. As a Magic action, you teleport to an unoccupied space you can see within 120 feet of yourself. Immediately after you disappear, each creature within 30 feet of the space you left must make a Strength saving throw against your spell save DC. On a failed save, a creature takes 3d10 Force damage and is pulled straight toward the space you left, ending in an unoccupied space as close to your former space as possible. On a successful save, the creature takes half as much damage only.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Magic action"),
            ("Range", "120 feet (teleport destination)"),
            ("Effect Area", "30-foot radius around former position"),
            ("Save", "Strength save (spell save DC)"),
            ("Failed Save", "3d10 Force damage + pulled to former space"),
            ("Successful Save", "Half damage only"),
            ("Recharge", "Long Rest or 5 Sorcery Points"),
        ]
