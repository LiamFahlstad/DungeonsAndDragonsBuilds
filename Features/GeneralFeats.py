from Definitions import Ability
from Features.BaseFeatures import CharacterFeature, TextFeature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class GeneralFeatCharacterFeature(CharacterFeature):
    pass


class GeneralFeatTextFeature(TextFeature):
    pass


GeneralFeat = GeneralFeatCharacterFeature | GeneralFeatTextFeature


class AbilityScoreImprovement(GeneralFeatCharacterFeature):
    """Also add either [+1, +1] OR [+2] to any abilities."""

    def __init__(self, bonuses: list[tuple[Ability, int]]):
        self.bonuses = bonuses
        # Validate
        if not (sum([bonus[1] for bonus in self.bonuses]) == 2):
            raise ValueError("Bonuses must sum to 2.")

    def modify(self, character_stat_block: CharacterStatBlock):
        for ability, bonus in self.bonuses:
            character_stat_block.abilities.add_bonus(ability, bonus)


class WarCaster(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("War Caster requires character level 4 or higher.")
        if ability not in [Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA]:
            raise ValueError(
                "War Caster ability increase must be Intelligence, Wisdom, or Charisma."
            )
        self.ability = ability
        super().__init__(
            name="War Caster",
            origin=f"General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:

        text = (
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Concentration. You have Advantage on Constitution saving throws that you make to maintain Concentration.\n"
            "Reactive Spell. When a creature provokes an Opportunity Attack from you by leaving your reach, you can take a Reaction to cast a spell at the creature rather than making an Opportunity Attack. The spell must have a casting time of one action and must target only that creature.\n"
            "Somatic Components. You can perform the Somatic components of spells even when you have weapons or a Shield in one or both hands."
        )
        return text


class Sentinel(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Sentinel requires character level 4 or higher.")
        if ability not in [Ability.STRENGTH, Ability.DEXTERITY]:
            raise ValueError("Sentinel ability increase must be Strength or Dexterity.")
        self.ability = ability
        super().__init__(
            name="Sentinel",
            origin=f"General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Guardian. Immediately after a creature within 5 feet of you takes the Disengage action or hits a target other than you with an attack, you can make an Opportunity Attack against that creature.\n"
            "Halt. When you hit a creature with an Opportunity Attack, the creature’s Speed becomes 0 for the rest of the current turn."
        )
        return text


class GreatWeaponMaster(GeneralFeatTextFeature):
    def __init__(self, character_level: int):
        if character_level < 4:
            raise ValueError(
                "Great Weapon Master requires character level 4 or higher."
            )
        super().__init__(
            name="Great Weapon Master",
            origin=f"General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(Ability.STRENGTH, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength score by 1, to a maximum of 20.\n"
            "Heavy Weapon Mastery. When you hit a creature with a weapon that has the Heavy property as part of the Attack action on your turn, you can cause the weapon to deal extra damage to the target. The extra damage equals your Proficiency Bonus.\n"
            "Hew. Immediately after you score a Critical Hit with a Melee weapon or reduce a creature to 0 Hit Points with one, you can make one attack with the same weapon as a Bonus Action.\n"
        )
