from Core.Definitions import Ability, Skill
from CharacterContent.Features.Core.BaseFeatures import Feature
from CharacterContent.Features.Core.Improvements import SkillProficiencyChoice
from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Utils import StringUtils


class ArcaneArcherLore(Feature):
    def __init__(self, skill: Skill, cantrip: str):
        super().__init__(name="Arcane Archer Lore", origin="Arcane Archer Fighter Level 3", skippable_in_concise=True)
        self._skill = skill
        self._cantrip = cantrip
        self._proficiency_choice = SkillProficiencyChoice(
            [skill],
            [Skill.ARCANA, Skill.NATURE],
            count=1,
            error_prefix="Arcane Archer Lore",
        )

    def apply(self, character_stat_block: CharacterStatBlock):
        self._proficiency_choice.apply(character_stat_block)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, you learn magical theory or some of the secrets of nature - typical for practitioners of this elven martial tradition. "
            f"You choose to gain proficiency in either the Arcana or the Nature skill, and you choose to learn either the Prestidigitation or Druidcraft cantrip. "
            f"You chose {self._skill.value} and {self._cantrip}."
        )
        return description


class ArcaneShot(Feature):
    def __init__(self):
        super().__init__(name="Arcane Shot", origin="Arcane Archer Fighter Level 3", usage_tags=["damage", "control"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        intelligence_modifier = character_stat_block.get_ability_modifier(Ability.INTELLIGENCE)
        arcane_shot_save_dc = 8 + proficiency_bonus + intelligence_modifier

        description = (
            "At 3rd level, you learn to unleash special magical effects with some of your shots. When you gain this feature, you learn two Arcane Shot options of your choice (see below).\n"
            "\n"
            "Once per turn when you fire an arrow from a shortbow or longbow as part of the Attack action, you can apply one of your Arcane Shot options to that arrow. You decide to use the option when the arrow hits, unless the option doesn't involve an attack roll. You have two uses of this ability, and you regain all expended uses of it when you finish a short or long rest.\n"
            "\n"
            "You gain an additional Arcane Shot option of your choice when you reach certain levels in this class: 7th, 10th, 15th, and 18th level. Each option also improves when you become an 18th-level fighter.\n"
            "\n"
            "Arcane Shot Options\n"
            "The Arcane Shot feature lets you choose options for it at certain levels. The options are presented here in alphabetical order. They are all magical effects, and each one is associated with one of the schools of magic.\n"
            "\n"
            f"If an option requires a saving throw, your Arcane Shot save DC equals 8 + your proficiency bonus + your Intelligence modifier = {arcane_shot_save_dc}.\n"
            "\n"
            "Banishing Arrow. You use abjuration magic to try to temporarily banish your target to a harmless location in the Feywild. The creature hit by the arrow must also succeed on a Charisma saving throw or be banished. While banished in this way, its speed is 0, and it is incapacitated. At the end of its next turn, the target reappears in the space it vacated or in the nearest unoccupied space if that space is occupied. After you reach 18th level in this class, a target also takes 2d6 force damage when the arrow hits it.\n"
            "\n"
            "Beguiling Arrow. Your enchantment magic causes this arrow to temporarily beguile its target. The creature hit by the arrow takes an extra 2d6 psychic damage, and choose one of your allies within 30 feet of the target. The target must succeed on a Wisdom saving throw, or it is charmed by the chosen ally until the start of your next turn. This effect ends early if the chosen ally attacks the charmed target, deals damage to it, or forces it to make a saving throw. The psychic damage increases to 4d6 when you reach 18th level in this class.\n"
            "\n"
            "Bursting Arrow. You imbue your arrow with force energy drawn from the school of evocation. The arrow detonates after your attack. Immediately after the arrow hits the creature, the target and all other creatures within 10 feet of it take 2d6 force damage each. The force damage increases to 4d6 when you reach 18th level in this class.\n"
            "\n"
            "Enfeebling Arrow. You weave necromantic magic into your arrow. The creature hit by the arrow takes an extra 2d6 necrotic damage. The target must also succeed on a Constitution saving throw, or the damage dealt by its weapon attacks is halved until the start of your next turn. The necrotic damage increases to 4d6 when you reach 18th level in this class.\n"
            "\n"
            "Grasping Arrow. When this arrow strikes its target, conjuration magic creates grasping, poisonous brambles, which wrap around the target. The creature hit by the arrow takes an extra 2d6 poison damage, its speed is reduced by 10 feet, and it takes 2d6 slashing damage the first time on each turn it moves 1 foot or more without teleporting. The target or any creature that can reach it can use its action to remove the brambles with a successful Strength (Athletics) check against your Arcane Shot save DC. Otherwise, the brambles last for 1 minute or until you use this option again. The poison damage and slashing damage both increase to 4d6 when you reach 18th level in this class.\n"
            "\n"
            "Piercing Arrow. You use transmutation magic to give your arrow an ethereal quality. When you use this option, you don't make an attack roll for the attack. Instead, the arrow fires forward in a line, which is 1 foot wide and 30 feet long, before disappearing. The arrow passes harmlessly through objects, ignoring cover. Each creature in that line must make a Dexterity saving throw. On a failed save, a creature takes damage as if it were hit by the arrow, plus an extra 1d6 piercing damage. On a successful save, a target takes half as much damage. The piercing damage increases to 2d6 when you reach 18th level in this class.\n"
            "\n"
            "Seeking Arrow. Using divination magic, you grant your arrow the ability to seek out your target, allowing the arrow to curve and twist its path in search of its prey. When you use this option, you don't make an attack roll for the attack. Instead, choose one creature you have seen in the past minute. The arrow flies toward that creature, moving around corners if necessary and ignoring three-quarters cover and half cover. If the target is within the weapon's range and there is a path large enough for the arrow to travel to the target, the target must make a Dexterity saving throw. On a failed save, it takes damage as if it were hit by the arrow, plus an extra 1d6 force damage, and you learn the target's current location. On a successful save, the target takes half as much damage, and you don't learn its location. The force damage increases to 2d6 when you reach 18th level in this class.\n"
            "\n"
            "Shadow Arrow. You weave illusion magic into your arrow, causing it to occlude your foe's vision with shadows. The creature hit by the arrow takes an extra 2d6 psychic damage, and it must succeed on a Wisdom saving throw or be unable to see anything farther than 5 feet away until the start of your next turn. The psychic damage increases to 4d6 when you reach 18th level in this class."
        )
        return StringUtils.add_boxes(description, 2, regain_all_on="short or long rest")


class MagicArrow(Feature):
    def __init__(self):
        super().__init__(name="Magic Arrow", origin="Arcane Archer Fighter Level 7", usage_tags=["buff"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 7th level, you gain the ability to infuse arrows with magic. Whenever you fire a nonmagical arrow from a shortbow or longbow, you can make it magical for the purpose of overcoming resistance and immunity to nonmagical attacks and damage. The magic fades from the arrow immediately after it hits or misses its target."
        return description


class CurvingShot(Feature):
    def __init__(self):
        super().__init__(name="Curving Shot", origin="Arcane Archer Fighter Level 7", action_type="bonus_action", range="60 Feet", usage_tags=["damage"])

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "At 7th level, you learn how to direct an errant arrow toward a new target. When you make an attack roll with a magic arrow and miss, you can use a bonus action to reroll the attack roll against a different target within 60 feet of the original target."
        return description


class EverReadyShot(Feature):
    def __init__(self):
        super().__init__(name="Ever-Ready Shot", origin="Arcane Archer Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Starting at 15th level, your magical archery is available whenever battle starts. If you roll initiative and have no uses of Arcane Shot remaining, you regain one use of it."
        return description
