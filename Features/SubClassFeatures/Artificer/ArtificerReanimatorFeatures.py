from Core.Definitions import ARTIFICER_HIT_DIE, Ability
from Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class ReanimatorSpells(Feature):
    def __init__(self):
        super().__init__(
            name="Reanimator Spells", origin="Reanimator Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach an Artificer level specified in the Reanimator Spells table, you thereafter always have the listed spells prepared.\n"
            "Reanimator Spells\n"
            "Artificer Level	Spells\n"
            "3	False Life, Spare the Dying, Witch Bolt\n"
            "5	Blindness/Deafness, Enhance Ability\n"
            "9	Animate Dead, Lightning Bolt\n"
            "13	Blight, Death Ward\n"
            "17	Antilife Shell, Raise Dead"
        )
        return description


class ReanimatorsSkillSet(Feature):
    def __init__(self):
        super().__init__(
            name="Reanimator's Skill Set", origin="Reanimator Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        intelligence_modifier = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        uses = max(1, intelligence_modifier)
        description = (
            "You gain the following benefits.\n"
            "Jolt to Life. When you cast Spare the Dying, you can modify the spell so that it sends a jolt of electricity through the target, reviving it. The target regains a number of Hit Points equal to your Artificer level, and each creature of your choice in a 10-foot Emanation originating from the target makes a Dexterity saving throw against your spell save DC, taking 2d4 Lightning damage on a failed save or half as much damage on a successful one.\n"
            "You can modify the spell this way a number of times equal to your Intelligence modifier (minimum of once), and you regain all expended uses when you finish a Long Rest. The Lightning damage of this feature increases by 1d4 when you reach Artificer levels 11 (3d4) and 17 (4d4).\n"
            "Reanimator's Tools. You gain proficiency with Alchemist's Supplies. If you already have this proficiency, you gain proficiency with one other type of Artisan's Tools of your choice."
        )
        return StringUtils.add_boxes(description, uses, regain_all_on="long rest")


class ReanimatedCompanion(Feature):
    def __init__(self):
        super().__init__(
            name="Reanimated Companion", origin="Reanimator Artificer Level 3"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Using Tinker's Tools or another type of Artisan's Tools with which you have proficiency, you can take a Magic action to create a Reanimated Companion (see the stat block) through the power of necromancy and science. The companion manifests in an unoccupied space within 5 feet of you. You determine the companion's appearance; your choices don't affect the companion's game statistics.\n"
            "The companion is Friendly to you and your allies and obeys you. It lasts until you finish a Long Rest or until you take a Magic action to dismiss it early, at which point it harmlessly collapses into a pile of viscera. It immediately drops to 0 Hit Points and dies (triggering its Death Burst trait) if you die.\n"
            "Once you create a companion, you can't do so again until you finish a Long Rest or expend a spell slot to create one. You can have only one companion at a time and can't create one while your companion is present.\n"
            "The Companion in Combat. In combat, the companion acts during your turn. It can move and take its Reaction on its own, but the only action it takes is the Dodge action unless you take a Bonus Action to command it to take an action. If you have the Incapacitated condition, the companion acts on its own and isn't limited to the Dodge action."
        )
        return description


class StrangeModifications(Feature):
    def __init__(self):
        super().__init__(
            name="Strange Modifications", origin="Reanimator Artificer Level 5"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Whenever you create a Reanimated Companion, it gains one of the following options of your choice; choose when you create the companion.\n"
            "Arcane Conduit. You can cast spells as though you were in the companion's space, but you must use your own senses. Once per turn, when you cast an Artificer spell from the Evocation or Necromancy school and deal damage while your companion is within 120 feet of you, you can add your Intelligence modifier to one damage roll of that spell.\n"
            "Ferocity. The damage die of the companion's Dreadful Swipe increases to 1d6."
        )
        return description


class ImprovedReanimation(Feature):
    def __init__(self):
        super().__init__(
            name="Improved Reanimation", origin="Reanimator Artificer Level 9"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "The damage of your Reanimated Companion's Death Burst increases to 4d4. Necrotic damage dealt by your companion ignores Resistance."
        return description


class MacabreModifications(Feature):
    def __init__(self):
        super().__init__(
            name="Macabre Modifications", origin="Reanimator Artificer Level 9"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You experiment and alter your companion further. Whenever you create a Reanimated Companion, the companion now gains two options for Strange Modifications, instead of one. Additionally, when picking options for Strange Modifications, you can also choose from the following options.\n"
            "Bloated. The companion becomes Large. Whenever it hits a Large or smaller creature with its Dreadful Swipe action, that creature is pushed up to 10 feet away from the companion. Additionally, you can add your Intelligence modifier to the damage dealt by the companion's Death Burst.\n"
            "Gaunt. The companion's Speed increases to 45 feet, and it gains a Climb Speed equal to its Speed. It can climb difficult surfaces, including along ceilings, without needing to make an ability check. In addition, whenever a creature of your choice starts its turn within a 10-foot Emanation originating from your companion, the creature must succeed on a Wisdom saving throw against your spell save DC or have the Frightened condition until the start of its next turn.\n"
            "Moist. The companion gains a Swim Speed equal to its Speed, and it can move through a space as narrow as 1 inch without expending extra movement to do so. In addition, whenever the companion is hit by an attack roll from a creature within 10 feet of itself, the attacker takes Acid damage equal to your Intelligence modifier."
        )
        return description


class RefinedReanimation(Feature):
    def __init__(self):
        super().__init__(
            name="Refined Reanimation", origin="Reanimator Artificer Level 15"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have mastered the science of revivification, granting you the following benefits.\n"
            "Facilitated Revival. You can cast Raise Dead once without expending a spell slot and without Material components, provided you use Tinker's Tools or another type of Artisan's Tools with which you have proficiency as the Spellcasting Focus. Once you use this feature, you can't use it again until you finish a Long Rest.\n"
            "Life Transfer. You can siphon the animating magic of your Reanimated Companion to bolster yourself. When you or your companion takes damage, you can take a Reaction to gain a number of Hit Points equal to your companion's current Hit Points. The companion then immediately drops to 0 Hit Points and dies (triggering its Death Burst trait).\n"
            "Superior Modifications. Whenever you create a Reanimated Companion, the companion now gains three options for Strange Modifications."
        )
        return description
