from Core.Definitions import Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class CircleSporesSpells(Feature):
    def __init__(self):
        super().__init__(name="Circle of Spores Spells", origin="Circle of Spores Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your symbiotic link to fungi and your ability to tap into the cycle of life and death grants you access to certain spells. You learn the Chill Touch cantrip.\n"
            "At 3rd, 5th, 7th, and 9th level you gain access to the spells listed for that level in the Circle of Spores Spells table. Once you gain access to one of these spells, you always have it prepared, and it doesn't count against the number of spells you can prepare each day. If you gain access to a spell that doesn't appear on the druid spell list, the spell is nonetheless a druid spell for you.\n"
            "Circle of Spores Spells\n"
            "Druid Level\tCircle Spells\n"
            "3rd\tBlindness/Deafness, Gentle Repose\n"
            "5th\tAnimate Dead, Gaseous Form\n"
            "7th\tBlight, Confusion\n"
            "9th\tCloudkill, Contagion"
        )
        return description


class HaloOfSpores(Feature):
    def __init__(self):
        super().__init__(name="Halo of Spores", origin="Circle of Spores Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You are surrounded by invisible, necrotic spores that are harmless until you unleash them on a creature nearby. When a creature you can see moves into a space within 10 feet of you or starts its turn there, you can use your reaction to deal necrotic damage to that creature unless it succeeds on a Constitution saving throw against your spell save DC.\n"
            "Halo of Spores Damage by Druid Level\n"
            "Druid Level\tDamage\n"
            "2nd-5th\t1d4\n"
            "6th-9th\t1d6\n"
            "10th-13th\t1d8\n"
            "14th-20th\t1d10"
        )
        return description


class SymbioticEntity(Feature):
    def __init__(self):
        super().__init__(name="Symbiotic Entity", origin="Circle of Spores Druid Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to channel magic into your spores. As an action, you can expend a use of your Wild Shape feature to awaken those spores, rather than transforming into a beast form, and you gain temporary hit points equal to 4 times your Druid level. While this feature is active, you gain the following benefits:\n"
            "    * When you deal your Halo of Spores damage, roll the damage die a second time and add it to the total.\n"
            "    * Your melee weapon attacks deal an extra 1d6 necrotic damage to any target they hit.\n"
            "These benefits last for 10 minutes, until you lose all these temporary hit points, or until you use your Wild Shape again."
        )
        return description


class FungalInfestation(Feature):
    def __init__(self):
        super().__init__(name="Fungal Infestation", origin="Circle of Spores Druid Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        wisdom_mod = character_stat_block.get_ability_modifier(Ability.WISDOM)
        uses = max(1, wisdom_mod)

        description = (
            "Your spores gain the ability to infest a corpse and animate it. If a beast or a humanoid that is Small or Medium dies within 10 feet of you, you can use your reaction to animate it, causing it to stand up immediately with 1 hit point. The creature uses the Zombie stat block in the Monster Manual. It remains animate for 1 hour, after which time it collapses and dies.\n"
            "In combat, the zombie's turn comes immediately after yours. It obeys your mental commands, and the only action it can take is the Attack action, making one melee attack."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class SpreadingSpores(Feature):
    def __init__(self):
        super().__init__(name="Spreading Spores", origin="Circle of Spores Druid Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You gain the ability to seed an area with deadly spores. As a bonus action while your Symbiotic Entity feature is active, you can hurl spores up to 30 feet away, where they swirl in a 10-foot cube for 1 minute. The spores disappear early if you use this feature again, if you dismiss them as a bonus action, or if your Symbiotic Entity feature is no longer active.\n"
            "Whenever a creature moves into the cube or starts its turn there, that creature takes your Halo of Spores damage, unless the creature succeeds on a Constitution saving throw against your spell save DC. A creature can take this damage no more than once per turn.\n"
            "While the cube of spores persists, you can't use your Halo of Spores reaction."
        )
        return description


class FungalBody(Feature):
    def __init__(self):
        super().__init__(name="Fungal Body", origin="Circle of Spores Druid Level 14")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "The fungal spores in your body alter you: you can't be blinded, deafened, frightened, or poisoned, and any critical hit against you counts as a normal hit instead, unless you're incapacitated."
        )
        return description
