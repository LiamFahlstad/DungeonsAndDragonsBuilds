from Core.Definitions import SORCERER_HIT_DIE
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class TelepathicSpeech(Feature):
    def __init__(self):
        super().__init__(name="Telepathic Speech", origin="Aberrant Sorcery Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can form a telepathic connection between your mind and the mind of another. As a Bonus Action, choose one creature you can see within 30 feet of yourself. You and the chosen creature can communicate telepathically with each other while the two of you are within a number of miles of each other equal to your Charisma modifier (minimum of 1 mile). To understand each other, you each must mentally use a language the other knows.\n"
            "The telepathic connection lasts for a number of minutes equal to your Sorcerer level. It ends early if you use this ability to form a connection with a different creature."
        )
        return description


class PsionicSorcery(Feature):
    def __init__(self):
        super().__init__(name="Psionic Sorcery", origin="Aberrant Sorcery Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast any level 1+ spell from your Psionic Spells feature, you can cast it by expending a spell slot as normal or by spending a number of Sorcery Points equal to the spell’s level. If you cast the spell using Sorcery Points, it requires no Verbal or Somatic components, and it requires no Material components unless they are consumed by the spell or have a cost specified in it."
        return description


class PsychicDefenses(Feature):
    def __init__(self):
        super().__init__(name="Psychic Defenses", origin="Aberrant Sorcery Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You have Resistance to Psychic damage, and you have Advantage on saving throws to avoid or end the Charmed or Frightened condition."
        return description


class RevelationinFlesh(Feature):
    def __init__(self):
        super().__init__(name="Revelation in Flesh", origin="Aberrant Sorcery Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can unleash the aberrant truth hidden within yourself. As a Bonus Action, you can spend 1 Sorcery Point or more to magically alter your body for 10 minutes. For each Sorcery Point you spend, you gain one of the following benefits of your choice, the effects of which last until the alteration ends.\n"
            "Aquatic Adaptation. You gain a Swim Speed equal to twice your Speed, and you can breathe underwater. Gills grow from your neck or flare behind your ears, and your fingers become webbed or you grow wriggling cilia.\n"
            "Glistening Flight. You gain a Fly Speed equal to your Speed, and you can hover. As you fly, your skin glistens with mucus or otherworldly light.\n"
            "See the Invisible. You can see any Invisible creature within 60 feet of yourself that isn’t behind Total Cover. Your eyes also turn black or become writhing sensory tendrils.\n"
            "Wormlike Movement. Your body, along with any equipment you are wearing or carrying, becomes slimy and pliable. You can move through any space as narrow as 1 inch, and you can spend 5 feet of movement to escape from nonmagical restraints or the Grappled condition."
        )
        return description


class WarpingImplosion(Feature):
    def __init__(self):
        super().__init__(name="Warping Implosion", origin="Aberrant Sorcery Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can unleash a space-warping anomaly. As a Magic action, you teleport to an unoccupied space you can see within 120 feet of yourself. Immediately after you disappear, each creature within 30 feet of the space you left must make a Strength saving throw against your spell save DC. On a failed save, a creature takes 3d10 Force damage and is pulled straight toward the space you left, ending in an unoccupied space as close to your former space as possible. On a successful save, the creature takes half as much damage only.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest unless you spend 5 Sorcery Points (no action required) to restore your use of it."
        )
        return description
