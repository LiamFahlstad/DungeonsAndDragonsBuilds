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


class Actor(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Actor requires character level 4 or higher.")
        if ability not in [Ability.CHARISMA]:
            raise ValueError("Actor ability increase must be Charisma.")
        self.ability = ability
        super().__init__(
            name="Actor",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+, Charisma 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Charisma score by 1, to a maximum of 20.\n"
            "Impersonation. While you're disguised as a real or fictional person, you have Advantage on Charisma (Deception or Performance) checks to convince others that you are that person.\n"
            "Mimicry. You can mimic the sounds of other creatures, including speech. A creature that hears the mimicry must succeed on a Wisdom (Insight) check to determine the effect is faked (DC 8 plus your Charisma modifier and Proficiency Bonus).\n"
        )
        return text


class Athlete(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Athlete requires character level 4 or higher.")
        if ability not in [Ability.STRENGTH, Ability.DEXTERITY]:
            raise ValueError("Athlete ability increase must be Strength or Dexterity.")
        self.ability = ability
        super().__init__(
            name="Athlete",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Climb Speed. You gain a Climb Speed equal to your Speed.\n"
            "Hop Up. When you have the Prone condition, you can right yourself with only 5 feet of movement.\n"
            "Jumping. You can make a running Long or High Jump after moving only 5 feet.\n"
        )
        return text


class Charger(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Charger requires character level 4 or higher.")
        if ability not in [Ability.STRENGTH, Ability.DEXTERITY]:
            raise ValueError("Charger ability increase must be Strength or Dexterity.")
        self.ability = ability
        super().__init__(
            name="Charger",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Improved Dash. When you take the Dash action, your Speed increases by 10 feet for that action.\n"
            "Charge Attack. If you move at least 10 feet in a straight line toward a target immediately before hitting it with a melee attack roll as part of the Attack action, choose one of the following effects: gain a 1d8 bonus to the attack's damage roll, or push the target up to 10 feet away if it is no more than one size larger than you. You can use this benefit only once on each of your turns.\n"
        )
        return text


class Chef(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Chef requires character level 4 or higher.")
        if ability not in [Ability.WISDOM, Ability.CONSTITUTION]:
            raise ValueError("Chef ability increase must be Wisdom or Constitution.")
        self.ability = ability
        super().__init__(
            name="Chef",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Wisdom score by 1, to a maximum of 20.\n"
            "Cook's Utensils. You gain proficiency with Cook's Utensils if you don't already have it.\n"
            "Replenishing Meal. As part of a Short Rest, you can cook special food if you have ingredients and Cook's Utensils on hand. You can prepare enough of this food for a number of creatures equal to 4 plus your Proficiency Bonus. At the end of the Short Rest, any creature who eats the food and spends one or more Hit Dice to regain Hit Points regains an extra 1d8 Hit Points.\n"
            "Bolstering Treats. With 1 hour of work or when you finish a Long Rest, you can cook a number of treats equal to your Proficiency Bonus if you have ingredients and Cook's Utensils on hand. These special treats last 8 hours after being made. A creature can use a Bonus Action to eat one of those treats. to gain a number of Temporary Hit Points equal to your Proficiency Bonus.\n"
        )
        return text


class Crusher(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Crusher requires character level 4 or higher.")
        if ability not in [Ability.STRENGTH, Ability.CONSTITUTION]:
            raise ValueError(
                "Crusher ability increase must be Strength or Constitution."
            )
        self.ability = ability
        super().__init__(
            name="Crusher",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+, Strength or Constitution 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Constitution score by 1, to a maximum of 20.\n"
            "Push. Once per turn, when you hit a creature with an attack that deals Bludgeoning damage, you can move it 5 feet to an unoccupied space if the target is no more than one size larger than you.\n"
            "Enhanced Critical. When you score a Critical Hit that deals Bludgeoning damage to a creature, attack rolls against that creature have Advantage until the start of your next turn.\n"
        )
        return text


class DualWielder(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Dual Wielder requires character level 4 or higher.")
        if ability not in [Ability.STRENGTH, Ability.DEXTERITY]:
            raise ValueError(
                "Dual Wielder ability increase must be Strength or Dexterity."
            )
        self.ability = ability
        super().__init__(
            name="Dual Wielder",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Enhanced Dual Wielding. When you take the Attack action on your turn and attack with a weapon that has the Light property, you can make one extra attack as a Bonus Action later on the same turn with a different weapon, which must be a Melee weapon that lacks the Two-Handed property. You don't add your ability modifier to the extra attack's damage unless that modifier is negative.\n"
            "Quick Draw. You can draw or stow two weapons that lack the Two-Handed property when you would normally be able to draw or stow only one.\n"
        )
        return text


class FeyTouched(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Fey Touched requires character level 4 or higher.")
        if ability not in [Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA]:
            raise ValueError(
                "Fey Touched ability increase must be Intelligence, Wisdom, or Charisma."
            )
        self.ability = ability
        super().__init__(
            name="Fey Touched",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+\n"
            "Your exposure to the Feywild's magic grants you the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Fey Magic. Choose one level 1 spell from the Divination or Enchantment school of magic. You always have that spell and the Misty Step spell prepared. You can cast each of these spells without expending a spell slot. Once you cast either spell in this way, you can't cast that spell in this way again until you finish a Long Rest. You can also cast these spells using spell slots you have of the appropriate level. The spells' spellcasting ability is the ability increased by this feat.\n"
        )
        return text


class Grappler(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Grappler requires character level 4 or higher.")
        if ability not in [Ability.STRENGTH, Ability.DEXTERITY]:
            raise ValueError("Grappler ability increase must be Strength or Dexterity.")
        self.ability = ability
        super().__init__(
            name="Grappler",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Punch and Grab. When you hit a creature with an Unarmed Strike as part of the Attack action on your turn, you can use both the Damage and the Grapple option. You can use this benefit only once per turn.\n"
            "Attack Advantage. You have Advantage on attack rolls against a creature Grappled by you.\n"
            "Fast Wrestler. You don’t have to spend extra movement to move a creature Grappled by you if the creature is your size or smaller.\n"
        )
        return text


class InspiringPerformance(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError(
                "Inspiring Performance requires character level 4 or higher."
            )
        if ability not in [Ability.WISDOM, Ability.CHARISMA]:
            raise ValueError(
                "Inspiring Performance ability increase must be Wisdom or Charisma."
            )
        self.ability = ability
        super().__init__(
            name="Inspiring Performance",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+, Wisdom or Charisma 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Wisdom or Charisma score by 1, to a maximum of 20.\n"
            "Bolstering Performance. When you finish a Short or Long Rest, you can give an inspiring performance: a speech, song, or dance. When you do so, choose up to six allies (which can include yourself) within 30 feet of yourself who witness the performance. The chosen creatures each gain Temporary Hit Points equal to your character level plus the modifier of the ability you increased with this feat.\n"
        )
        return text


class MageSlayer(GeneralFeatTextFeature):

    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Mage Slayer requires character level 4 or higher.")
        if ability not in [Ability.STRENGTH, Ability.DEXTERITY]:
            raise ValueError(
                "Mage Slayer ability increase must be Strength or Dexterity."
            )
        self.ability = ability
        super().__init__(
            name="Mage Slayer",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Concentration Breaker. When you damage a creature that is concentrating, it has Disadvantage on the saving throw it makes to maintain Concentration.\n"
            "Guarded Mind. If you fail an Intelligence, a Wisdom, or a Charisma saving throw, you can cause yourself to succeed instead. Once you use this benefit, you can't use it again until you finish a Short or Long Rest.\n"
        )
        return text
