from Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils

ROGUE_HIT_DIE = 8


class Bloodthirst(Feature):
    def __init__(self):
        super().__init__(name="Bloodthirst", origin="Scion of the Three Rogue Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(
            Ability.INTELLIGENCE
        )
        uses = max(1, intelligence_modifier)
        description = "When an enemy you can see within 30 feet of yourself takes damage and is Bloodied after taking that damage but not killed outright, you can take a Reaction and teleport to an unoccupied space you can see within 5 feet of that enemy. You can then make one melee attack. You can use this feature a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest."
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class DreadAllegiance(Feature):
    def __init__(self):
        super().__init__(
            name="Dread Allegiance", origin="Scion of the Three Rogue Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Choose one of the Dead Three: Bane, Bhaal, or Myrkul. You gain Resistance to one type of damage and the ability to cast a cantrip, as detailed in the table below; Intelligence is your spellcasting ability for this cantrip. When you finish a Long Rest, you can change your choice.\n"
            "God	Damage Resistance	Cantrip\n"
            "Bane	Psychic	Minor Illusion\n"
            "Bhaal	Poison	Blade Ward\n"
            "Myrkul	Necrotic	Chill Touch"
        )
        return description


class StrikeFear(Feature):
    def __init__(self):
        super().__init__(name="Strike Fear", origin="Scion of the Three Rogue Level 9")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following Cunning Strike option.\n"
            "Terrify (Cost: 1d6). The target must succeed on a Wisdom saving throw, or it has the Frightened condition for 1 minute. While the target is Frightened in this way, you have Advantage on attack rolls against the target.\n"
            "The Frightened target repeats the save at the end of each of its turns, ending the effect on itself on a success."
        )
        return description


class AuraofMalevolence(Feature):
    def __init__(self):
        super().__init__(
            name="Aura of Malevolence", origin="Scion of the Three Rogue Level 13"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "You radiate malignant power associated with one of the Dead Three. When you use Bloodthirst and teleport, each creature of your choice within 10 feet of either the space you left or your destination space (your choice) takes damage equal to your Intelligence modifier; the damage type is the same as the damage Resistance granted by your choice in the Dread Allegiance feature. Damage dealt by this feature ignores Resistance."
        return description


class DreadIncarnate(Feature):
    def __init__(self):
        super().__init__(
            name="Dread Incarnate", origin="Scion of the Three Rogue Level 17"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the following benefits.\n"
            "Cutthroat. You regain one expended use of Bloodthirst when you finish a Short Rest.\n"
            "Murderous Intent. When you roll for your Sneak Attack damage, you can treat a roll of a 1 or 2 on the die as a 3."
        )
        return description
