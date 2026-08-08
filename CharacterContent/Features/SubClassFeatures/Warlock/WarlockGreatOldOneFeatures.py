from Core.Definitions import DamageType, WARLOCK_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import DamageResistance
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class GreatOldOneSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Great Old One Spells", origin="Great Old One Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The magic of your patron ensures you always have certain spells ready; when you reach a Warlock level specified in the Great Old One Spells table, you thereafter always have the listed spells prepared."
        return description


class AwakenedMind(Feature):
    def __init__(self):
        super().__init__(
            name="Awakened Mind", origin="Great Old One Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can form a telepathic connection between your mind and the mind of another. As a Bonus Action, choose one creature you can see within 30 feet of yourself. You and the chosen creature can communicate telepathically with each other while the two of you are within a number of miles of each other equal to your Charisma modifier (minimum of 1 mile). To understand each other, you each must mentally use a language the other knows.\n"
            "The telepathic connection lasts for a number of minutes equal to your Warlock level. It ends early if you use this feature to connect with a different creature."
        )
        return description


class PsychicSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Psychic Spells", origin="Great Old One Patron Warlock Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you cast a Warlock spell that deals damage, you can change its damage type to Psychic. In addition, when you cast a Warlock spell that is an Enchantment or Illusion, you can do so without Verbal or Somatic components."
        return description


class ClairvoyantCombatant(Feature):
    def __init__(self):
        super().__init__(
            name="Clairvoyant Combatant", origin="Great Old One Patron Warlock Level 6"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you form a telepathic bond with a creature using your Awakened Mind, you can force that creature to make a Wisdom saving throw against your spell save DC. On a failed save, the creature has Disadvantage on attack rolls against you, and you have Advantage on attack rolls against that creature for the duration of the bond.\n"
            "Once you use this feature, you can't use it again until you finish a Short or Long Rest unless you expend a Pact Magic spell slot (no action required) to restore your use of it."
        )
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Trigger", "Form telepathic bond via Awakened Mind"),
            ("Save", "Wisdom save DC"),
            ("Effect on Fail", "Target has Disadvantage on attacks vs you; you have Advantage vs target"),
            ("Duration", "For duration of telepathic bond"),
            ("Recharge", "Short or Long Rest or expend Pact Magic spell slot"),
        ]


class EldritchHex(Feature):
    def __init__(self):
        super().__init__(
            name="Eldritch Hex", origin="Great Old One Patron Warlock Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your alien patron grants you a powerful curse. You always have the Hex spell prepared. When you cast Hex and choose an ability, the target also has Disadvantage on saving throws of the chosen ability for the duration of the spell."
        return description


class ThoughtShield(Feature):
    def __init__(self):
        super().__init__(
            name="Thought Shield", origin="Great Old One Patron Warlock Level 10"
        )
        self._resistance = DamageResistance(DamageType.PSYCHIC, self.name)

    def apply(self, character_stat_block: CharacterStatBlock):
        self._resistance.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Your thoughts can't be read by telepathy or other means unless you allow it. You also have Resistance to Psychic damage, and whenever a creature deals Psychic damage to you, that creature takes the same amount of damage that you take."
        return description


class CreateThrall(Feature):
    def __init__(self):
        super().__init__(
            name="Create Thrall", origin="Great Old One Patron Warlock Level 14"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you cast Summon Aberration, you can modify it so that it doesn't require Concentration. If you do so, the spell's duration becomes 1 minute for that casting, and when summoned, the Aberration has a number of Temporary Hit Points equal to your Warlock level plus your Charisma modifier.\n"
            "In addition, the first time each turn the Aberration hits a creature under the effect of your Hex, the Aberration deals extra Psychic damage to the target equal to the bonus damage of that spell."
        )
        return description

    def get_concise_description(
        self, character_stat_block: CharacterStatBlock
    ) -> str:
        return (
            "When casting Summon Aberration, remove Concentration requirement (duration 1 min instead); the Aberration gains Temp HP = Warlock level + CHA mod. First time each turn the Aberration hits a creature under your Hex, it deals extra Psychic damage equal to that spell's bonus damage."
        )
