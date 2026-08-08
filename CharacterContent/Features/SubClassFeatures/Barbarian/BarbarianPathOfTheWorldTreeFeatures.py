import Core.Definitions as Definitions
from Core.Definitions import BARBARIAN_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class VitalityOfTheTree(Feature):
    def __init__(self):
        super().__init__(
            name="Vitality of the Tree",
            origin="Path Of The World Tree Barbarian Level 3",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Your Rage taps into the life force of the World Tree. You gain the following benefits.\n"
            "Vitality Surge. When you activate your Rage, you gain a number of Temporary Hit Points equal to your Barbarian level.\n"
            "Life-Giving Force. At the start of each of your turns while your Rage is active, you can choose another creature within 10 feet of yourself to gain Temporary Hit Points. To determine the number of Temporary Hit Points, roll a number of d6s equal to your Rage Damage bonus, and add them together. If any of these Temporary Hit Points remain when your Rage ends, they vanish."
        )
        return description

    def get_concise_description(self, character_stat_block: CharacterStatBlock) -> str:
        barbarian_level = character_stat_block.get_class_level(
            Definitions.CharacterClass.BARBARIAN
        )
        from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import (
            get_rage_damage_bonus,
        )
        rage_damage = get_rage_damage_bonus(barbarian_level)
        return (
            f"When you activate your Rage, gain Temporary Hit Points equal to your Barbarian level ({barbarian_level}). "
            f"At the start of each of your turns while Raging, choose a creature within 10 feet to grant Temporary Hit Points equal to {rage_damage}d6 "
            f"(these vanish when your Rage ends)."
        )


class BranchesOfTheTree(Feature):
    def __init__(self):
        super().__init__(
            name="Branches of the Tree",
            origin="Path Of The World Tree Barbarian Level 6",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "Whenever a creature you can see starts its turn within 30 feet of you while your Rage is active, you can take a Reaction to summon spectral branches of the World Tree around it. The target must succeed on a Strength saving throw (DC 8 plus your Strength modifier and Proficiency Bonus) or be teleported to an unoccupied space you can see within 5 feet of yourself or in the nearest unoccupied space you can see. After the target teleports, you can reduce its Speed to 0 until the end of the current turn."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        strength_modifier = character_stat_block.get_ability_modifier(
            Definitions.Ability.STRENGTH
        )
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        dc = 8 + strength_modifier + proficiency_bonus
        return [
            ("Trigger", "Creature starts turn within 30 feet (while Rage active)"),
            ("Action", "Reaction"),
            ("Save", f"Strength save, DC {dc}"),
            ("On Failure", "Teleport within 5 feet or nearest space"),
            ("Effect", "Reduce Speed to 0 until end of turn"),
        ]


class BatteringRoots(Feature):
    def __init__(self):
        super().__init__(
            name="Battering Roots", origin="Path Of The World Tree Barbarian Level 10"
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "During your turn, your reach is 10 feet greater with any Melee weapon that has the Heavy or Versatile property, as tendrils of the World Tree extend from you. When you hit with such a weapon on your turn, you can activate the Push or Topple mastery property in addition to a different mastery property you're using with that weapon."
        return description


class TravelAlongTheTree(Feature):
    def __init__(self):
        super().__init__(
            name="Travel along the Tree",
            origin="Path Of The World Tree Barbarian Level 14",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = "When you activate your Rage and as a Bonus Action while your Rage is active, you can teleport up to 60 feet to an unoccupied space you can see. In addition, once per Rage, you can increase the range of that teleport to 150 feet. When you do so, you can also bring up to six willing creatures who are within 10 feet of you. Each creature teleports to an unoccupied space of your choice within 10 feet of your destination space."
        return description

    def get_table_description(
        self, character_stat_block: CharacterStatBlock
    ) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus Action (or activation of Rage)"),
            ("Range", "60 feet (150 feet once per Rage)"),
            ("Requirement", "Rage must be active"),
            ("Additional Effect", "Can bring up to 6 willing creatures"),
            ("Creature Teleport Range", "Within 10 feet of destination"),
        ]
