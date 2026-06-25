from Definitions import Ability, Skill
from Features.BaseFeatures import CharacterFeature, TextFeature
from Utils import StringUtils
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class GeneralFeatCharacterFeature(CharacterFeature):
    pass


class GeneralFeatTextFeature(TextFeature):
    pass


GeneralFeat = GeneralFeatCharacterFeature | GeneralFeatTextFeature


class _AbilityScoreFeat(GeneralFeatTextFeature):
    """Base class for the common Level 4+ general feats that grant +1 to one ability.

    Subclasses declare:
        _NAME       – feat display name
        _ORIGIN     – origin string (defaults to "General Feat Level 4+")
        _ABILITIES  – tuple of allowed Ability values for the +1 bonus
        _MIN_LEVEL  – minimum character level (defaults to 4)

    They only need to implement ``get_description``.
    """

    _NAME: str
    _ORIGIN: str = "General Feat Level 4+"
    _ABILITIES: tuple
    _MIN_LEVEL: int = 4

    def __init__(self, character_level: int, ability: Ability):
        if character_level < self._MIN_LEVEL:
            raise ValueError(
                f"{self._NAME} requires character level {self._MIN_LEVEL} or higher."
            )
        if ability not in self._ABILITIES:
            allowed = " or ".join(a.value for a in self._ABILITIES)
            raise ValueError(
                f"{self._NAME} ability increase must be {allowed}."
            )
        self.ability = ability
        super().__init__(name=self._NAME, origin=self._ORIGIN)

    def modify(self, character_stat_block: CharacterStatBlock):
        character_stat_block.abilities.add_bonus(self.ability, 1)


# ---------------------------------------------------------------------------
# Common General Feats (PHB)
# ---------------------------------------------------------------------------


class AbilityScoreImprovement(GeneralFeatCharacterFeature):
    """Also add either [+1, +1] OR [+2] to any abilities."""

    def __init__(self, bonuses: list[tuple[Ability, int]]):
        self.bonuses = bonuses
        if sum(bonus[1] for bonus in self.bonuses) != 2:
            raise ValueError("Bonuses must sum to 2.")

    def modify(self, character_stat_block: CharacterStatBlock):
        for ability, bonus in self.bonuses:
            character_stat_block.abilities.add_bonus(ability, bonus)


class Actor(_AbilityScoreFeat):
    _NAME = "Actor"
    _ABILITIES = (Ability.CHARISMA,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Charisma 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Charisma score by 1, to a maximum of 20.\n"
            "Impersonation. While you're disguised as a real or fictional person, you have Advantage on Charisma (Deception or Performance) checks to convince others that you are that person.\n"
            "Mimicry. You can mimic the sounds of other creatures, including speech. A creature that hears the mimicry must succeed on a Wisdom (Insight) check to determine the effect is faked (DC 8 plus your Charisma modifier and Proficiency Bonus).\n"
        )


class Athlete(_AbilityScoreFeat):
    _NAME = "Athlete"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Climb Speed. You gain a Climb Speed equal to your Speed.\n"
            "Hop Up. When you have the Prone condition, you can right yourself with only 5 feet of movement.\n"
            "Jumping. You can make a running Long or High Jump after moving only 5 feet.\n"
        )


class Charger(_AbilityScoreFeat):
    _NAME = "Charger"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Improved Dash. When you take the Dash action, your Speed increases by 10 feet for that action.\n"
            "Charge Attack. If you move at least 10 feet in a straight line toward a target immediately before hitting it with a melee attack roll as part of the Attack action, choose one of the following effects: gain a 1d8 bonus to the attack's damage roll, or push the target up to 10 feet away if it is no more than one size larger than you. You can use this benefit only once on each of your turns.\n"
        )


class Chef(_AbilityScoreFeat):
    _NAME = "Chef"
    _ABILITIES = (Ability.WISDOM, Ability.CONSTITUTION)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Wisdom score by 1, to a maximum of 20.\n"
            "Cook's Utensils. You gain proficiency with Cook's Utensils if you don't already have it.\n"
            "Replenishing Meal. As part of a Short Rest, you can cook special food if you have ingredients and Cook's Utensils on hand. You can prepare enough of this food for a number of creatures equal to 4 plus your Proficiency Bonus. At the end of the Short Rest, any creature who eats the food and spends one or more Hit Dice to regain Hit Points regains an extra 1d8 Hit Points.\n"
            "Bolstering Treats. With 1 hour of work or when you finish a Long Rest, you can cook a number of treats equal to your Proficiency Bonus if you have ingredients and Cook's Utensils on hand. These special treats last 8 hours after being made. A creature can use a Bonus Action to eat one of those treats to gain a number of Temporary Hit Points equal to your Proficiency Bonus.\n"
        )


class CrossbowExpert(_AbilityScoreFeat):
    _NAME = "Crossbow Expert"
    _ABILITIES = (Ability.DEXTERITY,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity score by 1, to a maximum of 20.\n"
            "Ignore Loading. You ignore the Loading property of the Hand Crossbow, Heavy Crossbow, and Light Crossbow. If you're holding one of them, you can load a piece of ammunition into it even if you lack a free hand.\n"
            "Firing in Melee. Being within 5 feet of an enemy doesn't impose Disadvantage on your attack rolls with crossbows.\n"
            "Dual Wielding. When you make the extra attack of the Light property, you can add your ability modifier to the damage of the extra attack if that attack is with a crossbow that has the Light property and you aren't already adding that modifier to the damage.\n"
        )


class Crusher(_AbilityScoreFeat):
    _NAME = "Crusher"
    _ABILITIES = (Ability.STRENGTH, Ability.CONSTITUTION)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Constitution score by 1, to a maximum of 20.\n"
            "Push. Once per turn, when you hit a creature with an attack that deals Bludgeoning damage, you can move it 5 feet to an unoccupied space if the target is no more than one size larger than you.\n"
            "Enhanced Critical. When you score a Critical Hit that deals Bludgeoning damage to a creature, attack rolls against that creature have Advantage until the start of your next turn.\n"
        )


class DefensiveDuelist(_AbilityScoreFeat):
    _NAME = "Defensive Duelist"
    _ABILITIES = (Ability.DEXTERITY,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity score by 1, to a maximum of 20.\n"
            "Parry. If you're holding a Finesse weapon and another creature hits you with a melee attack, you can take a Reaction to add your Proficiency Bonus to your Armor Class, potentially causing the attack to miss you. You gain this bonus to your AC against melee attacks until the start of your next turn.\n"
        )


class DualWielder(_AbilityScoreFeat):
    _NAME = "Dual Wielder"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Enhanced Dual Wielding. When you take the Attack action on your turn and attack with a weapon that has the Light property, you can make one extra attack as a Bonus Action later on the same turn with a different weapon, which must be a Melee weapon that lacks the Two-Handed property. You don't add your ability modifier to the extra attack's damage unless that modifier is negative.\n"
            "Quick Draw. You can draw or stow two weapons that lack the Two-Handed property when you would normally be able to draw or stow only one.\n"
        )


class Durable(_AbilityScoreFeat):
    _NAME = "Durable"
    _ABILITIES = (Ability.CONSTITUTION,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution score by 1, to a maximum of 20.\n"
            "Defy Death. You have Advantage on Death Saving Throws.\n"
            "Speedy Recovery. As a Bonus Action, you can expend one of your Hit Point Dice, roll the die, and regain a number of Hit Points equal to the roll.\n"
        )


class ElementalAdept(_AbilityScoreFeat):
    _NAME = "Elemental Adept"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Energy Mastery. Choose one of the following damage types: Acid, Cold, Fire, Lightning, or Thunder. Spells you cast ignore Resistance to damage of the chosen type. In addition, when you roll damage for a spell you cast that deals damage of that type, you can treat any 1 on a damage die as a 2.\n"
            "Repeatable. You can take this feat more than once, but you must choose a different damage type each time for Energy Mastery.\n"
        )


class FeyTouched(_AbilityScoreFeat):
    _NAME = "Fey Touched"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "Your exposure to the Feywild's magic grants you the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Fey Magic. Choose one level 1 spell from the Divination or Enchantment school of magic. You always have that spell and the Misty Step spell prepared. You can cast each of these spells without expending a spell slot. Once you cast either spell in this way, you can't cast that spell in this way again until you finish a Long Rest. You can also cast these spells using spell slots you have of the appropriate level. The spells' spellcasting ability is the ability increased by this feat.\n"
        )


class Grappler(_AbilityScoreFeat):
    _NAME = "Grappler"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Punch and Grab. When you hit a creature with an Unarmed Strike as part of the Attack action on your turn, you can use both the Damage and the Grapple option. You can use this benefit only once per turn.\n"
            "Attack Advantage. You have Advantage on attack rolls against a creature Grappled by you.\n"
            "Fast Wrestler. You don't have to spend extra movement to move a creature Grappled by you if the creature is your size or smaller.\n"
        )


class GreatWeaponMaster(_AbilityScoreFeat):
    _NAME = "Great Weapon Master"
    _ABILITIES = (Ability.STRENGTH,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Strength 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength score by 1, to a maximum of 20.\n"
            "Heavy Weapon Mastery. When you hit a creature with a weapon that has the Heavy property as part of the Attack action on your turn, you can cause the weapon to deal extra damage to the target. The extra damage equals your Proficiency Bonus.\n"
            "Hew. Immediately after you score a Critical Hit with a Melee weapon or reduce a creature to 0 Hit Points with one, you can make one attack with the same weapon as a Bonus Action.\n"
        )


class HeavilyArmored(_AbilityScoreFeat):
    _NAME = "Heavily Armored"
    _ABILITIES = (Ability.CONSTITUTION, Ability.STRENGTH)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Medium Armor Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Strength score by 1, to a maximum of 20.\n"
            "Armor Training. You gain training with Heavy armor.\n"
        )


class HeavyArmorMaster(_AbilityScoreFeat):
    _NAME = "Heavy Armor Master"
    _ABILITIES = (Ability.CONSTITUTION, Ability.STRENGTH)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Heavy Armor Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Strength score by 1, to a maximum of 20.\n"
            "Damage Reduction. When you're hit by an attack while you're wearing Heavy armor, any Bludgeoning, Piercing, and Slashing damage dealt to you by that attack is reduced by an amount equal to your Proficiency Bonus.\n"
        )


class InspiringLeader(_AbilityScoreFeat):
    _NAME = "Inspiring Leader"
    _ABILITIES = (Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Wisdom or Charisma 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Wisdom or Charisma score by 1, to a maximum of 20.\n"
            "Bolstering Performance. When you finish a Short or Long Rest, you can give an inspiring performance: a speech, song, or dance. When you do so, choose up to six allies (which can include yourself) within 30 feet of yourself who witness the performance. The chosen creatures each gain Temporary Hit Points equal to your character level plus the modifier of the ability you increased with this feat.\n"
        )


class KeenMind(_AbilityScoreFeat):
    _NAME = "Keen Mind"
    _ABILITIES = (Ability.INTELLIGENCE,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Intelligence 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence score by 1, to a maximum of 20.\n"
            "Lore Knowledge. Choose one of the following skills: Arcana, History, Investigation, Nature, or Religion. If you lack proficiency in the chosen skill, you gain proficiency in it, and if you already have proficiency in it, you gain Expertise in it.\n"
            "Quick Study. You can take the Study action as a Bonus Action.\n"
        )


class LightlyArmored(_AbilityScoreFeat):
    _NAME = "Lightly Armored"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Armor Training. You gain training with Light armor and Shields.\n"
        )


class MageSlayer(_AbilityScoreFeat):
    _NAME = "Mage Slayer"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Concentration Breaker. When you damage a creature that is concentrating, it has Disadvantage on the saving throw it makes to maintain Concentration.\n"
            "Guarded Mind. If you fail an Intelligence, a Wisdom, or a Charisma saving throw, you can cause yourself to succeed instead. Once you use this benefit, you can't use it again until you finish a Short or Long Rest.\n"
        )


class MartialWeaponTraining(_AbilityScoreFeat):
    _NAME = "Martial Weapon Training"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Weapon Proficiency. You gain proficiency with Martial weapons.\n"
        )


class MediumArmorMaster(_AbilityScoreFeat):
    _NAME = "Medium Armor Master"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Medium Armor Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Dexterous Wearer. While you're wearing Medium armor, you can add 3, rather than 2, to your AC if you have a Dexterity score of 16 or higher.\n"
        )


class ModeratelyArmored(_AbilityScoreFeat):
    _NAME = "Moderately Armored"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Light Armor Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Armor Training. You gain training with Medium armor.\n"
        )


class MountedCombatant(_AbilityScoreFeat):
    _NAME = "Mounted Combatant"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY, Ability.WISDOM)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength, Dexterity, or Wisdom score by 1, to a maximum of 20.\n"
            "Mounted Strike. While mounted, you have Advantage on attack rolls against any unmounted creature within 5 feet of your mount that is at least one size smaller than the mount.\n"
            "Leap Aside. If your mount is subjected to an effect that allows it to make a Dexterity saving throw to take only half damage, it instead takes no damage if it succeeds on the saving throw and only half damage if it fails. For your mount to gain this benefit, you must be riding it, and neither of you can have the Incapacitated condition.\n"
            "Veer. While mounted, you can force an attack that hits your mount to hit you instead if you don't have the Incapacitated condition.\n"
        )


class Observant(_AbilityScoreFeat):
    _NAME = "Observant"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Intelligence or Wisdom 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence or Wisdom score by 1, to a maximum of 20.\n"
            "Keen Observer. Choose one of the following skills: Insight, Investigation, or Perception. If you lack proficiency with the chosen skill, you gain proficiency in it, and if you already have proficiency in it, you gain Expertise in it.\n"
            "Quick Search. You can take the Search action as a Bonus Action.\n"
        )


class Piercer(_AbilityScoreFeat):
    _NAME = "Piercer"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity by 1, to a maximum of 20.\n"
            "Puncture. Once per turn, when you hit a creature with an attack that deals Piercing damage, you can reroll one of the attack's damage dice, and you must use the new roll.\n"
            "Enhanced Critical. When you score a Critical Hit that deals Piercing damage to a creature, you can roll one additional damage die when determining the extra Piercing damage the target takes.\n"
        )


class Poisoner(_AbilityScoreFeat):
    _NAME = "Poisoner"
    _ABILITIES = (Ability.DEXTERITY, Ability.INTELLIGENCE)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Intelligence score by 1, to a maximum of 20.\n"
            "Potent Poison. When you make a damage roll that deals Poison damage, it ignores Resistance to Poison damage.\n"
            "Brew Poison. You gain proficiency with the Poisoner's Kit. With 1 hour of work using such a kit and expending 50 GP worth of materials, you can create a number of poison doses equal to your Proficiency Bonus. As a Bonus Action, you can apply a poison dose to a weapon or piece of ammunition. Once applied, the poison retains its potency for 1 minute or until you deal damage with the poisoned item, whichever is shorter. When a creature takes damage from the poisoned item, that creature must succeed on a Constitution saving throw (DC 8 plus the modifier of the ability increased by this feat and your Proficiency Bonus) or take 2d8 Poison damage and have the Poisoned condition until the end of your next turn.\n"
        )


class PolearmMaster(_AbilityScoreFeat):
    _NAME = "Polearm Master"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Strength score by 1, to a maximum of 20.\n"
            "Pole Strike. Immediately after you take the Attack action and attack with a Quarterstaff, a Spear, or a weapon that has the Heavy and Reach properties, you can use a Bonus Action to make a melee attack with the opposite end of the weapon. The weapon deals Bludgeoning damage, and the weapon's damage die for this attack is a d4.\n"
            "Reactive Strike. While you're holding a Quarterstaff, a Spear, or a weapon that has the Heavy and Reach properties, you can take a Reaction to make one melee attack against a creature that enters the reach you have with that weapon.\n"
        )


class Resilient(_AbilityScoreFeat):
    _NAME = "Resilient"
    _ABILITIES = tuple(Ability)  # any ability is valid

    def modify(self, character_stat_block: CharacterStatBlock):
        super().modify(character_stat_block)
        character_stat_block.add_proficiency_in_saving_throw(self.ability)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Choose one ability in which you lack saving throw proficiency. Increase the chosen ability score by 1, to a maximum of 20.\n"
            "Saving Throw Proficiency. You gain saving throw proficiency with the chosen ability.\n"
        )


class RitualCaster(_AbilityScoreFeat):
    _NAME = "Ritual Caster"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Intelligence, Wisdom, or Charisma 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Ritual Spells. Choose a number of level 1 spells equal to your Proficiency Bonus that have the Ritual tag. You always have those spells prepared, and you can cast them with any spell slots you have. The spells' spellcasting ability is the ability increased by this feat. Whenever your Proficiency Bonus increases thereafter, you can add an additional level 1 spell with the Ritual tag to the spells always prepared with this feature.\n"
            "Quick Ritual. With this benefit, you can cast a Ritual spell that you have prepared using its regular casting time rather than the extended time for a Ritual. Doing so doesn't require a spell slot. Once you cast the spell in this way, you can't use this benefit again until you finish a Long Rest.\n"
        )


class Sentinel(_AbilityScoreFeat):
    _NAME = "Sentinel"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Strength or Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Guardian. Immediately after a creature within 5 feet of you takes the Disengage action or hits a target other than you with an attack, you can make an Opportunity Attack against that creature.\n"
            "Halt. When you hit a creature with an Opportunity Attack, the creature's Speed becomes 0 for the rest of the current turn.\n"
        )


class ShadowTouched(_AbilityScoreFeat):
    _NAME = "Shadow Touched"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "Your exposure to the Shadowfell's magic grants you the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Shadow Magic. Choose one level 1 spell from the Illusion or Necromancy school of magic. You always have that spell and the Invisibility spell prepared. You can cast each of these spells without expending a spell slot. Once you cast either spell in this way, you can't cast that spell in this way again until you finish a Long Rest. You can also cast these spells using spell slots you have of the appropriate level. The spells' spellcasting ability is the ability increased by this feat.\n"
        )


class Sharpshooter(_AbilityScoreFeat):
    _NAME = "Sharpshooter"
    _ABILITIES = (Ability.DEXTERITY,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity score by 1, to a maximum of 20.\n"
            "Bypass Cover. Your ranged attacks with weapons ignore Half Cover and Three-Quarters Cover.\n"
            "Firing in Melee. Being within 5 feet of an enemy doesn't impose Disadvantage on your attack rolls with Ranged weapons.\n"
            "Long Shots. Attacking at long range doesn't impose Disadvantage on your attack rolls with Ranged weapons.\n"
        )


class ShieldMaster(_AbilityScoreFeat):
    _NAME = "Shield Master"
    _ABILITIES = (Ability.STRENGTH,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Shield Training\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength score by 1, to a maximum of 20.\n"
            "Shield Bash. If you attack a creature within 5 feet of you as part of the Attack action and hit with a Melee weapon, you can immediately bash the target with your Shield if it's equipped, forcing the target to make a Strength saving throw (DC 8 plus your Strength modifier and Proficiency Bonus). On a failed save, you either push the target 5 feet from you or cause it to have the Prone condition (your choice). You can use this benefit only once on each of your turns.\n"
            "Interpose Shield. If you're subjected to an effect that allows you to make a Dexterity saving throw to take only half damage, you can take a Reaction to take no damage if you succeed on the saving throw and are holding a Shield.\n"
        )


class SkillExpert(_AbilityScoreFeat):
    _NAME = "Skill Expert"
    _ABILITIES = tuple(Ability)  # any ability is valid

    def __init__(self, character_level: int, ability: Ability, skill: Skill):
        self.skill = skill
        super().__init__(character_level, ability)

    def modify(self, character_stat_block: CharacterStatBlock):
        super().modify(character_stat_block)
        if not character_stat_block.skills.is_proficient(self.skill):
            character_stat_block.skills.add_skill_proficiency(self.skill)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase one ability score of your choice by 1, to a maximum of 20.\n"
            "Skill Proficiency. You gain proficiency in one skill of your choice.\n"
            "Expertise. Choose one skill in which you have proficiency but lack Expertise. You gain Expertise with that skill.\n"
        )


class Skulker(_AbilityScoreFeat):
    _NAME = "Skulker"
    _ABILITIES = (Ability.DEXTERITY,)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity score by 1, to a maximum of 20.\n"
            "Blindsight. You have Blindsight with a range of 10 feet.\n"
            "Fog of War. You exploit the distractions of battle, gaining Advantage on any Dexterity (Stealth) check you make as part of the Hide action during combat.\n"
            "Sniper. If you make an attack roll while hidden and the roll misses, making the attack roll doesn't reveal your location.\n"
        )


class Slasher(_AbilityScoreFeat):
    _NAME = "Slasher"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Hamstring. Once per turn when you hit a creature with an attack that deals Slashing damage, you can reduce the Speed of that creature by 10 feet until the start of your next turn.\n"
            "Enhanced Critical. When you score a Critical Hit that deals Slashing damage to a creature, it has Disadvantage on attack rolls until the start of your next turn.\n"
        )


class Speedy(_AbilityScoreFeat):
    _NAME = "Speedy"
    _ABILITIES = (Ability.DEXTERITY, Ability.CONSTITUTION)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Dexterity or Constitution 13+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Constitution score by 1, to a maximum of 20.\n"
            "Speed Increase. Your Speed increases by 10 feet.\n"
            "Dash over Difficult Terrain. When you take the Dash action on your turn, Difficult Terrain doesn't cost you extra movement for the rest of that turn.\n"
            "Agile Movement. Opportunity Attacks have Disadvantage against you.\n"
        )


class SpellSniper(_AbilityScoreFeat):
    _NAME = "Spell Sniper"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Bypass Cover. Your attack rolls for spells ignore Half Cover and Three-Quarters Cover.\n"
            "Casting in Melee. Being within 5 feet of an enemy doesn't impose Disadvantage on your attack rolls with spells.\n"
            "Increased Range. When you cast a spell that has a range of at least 10 feet and requires you to make an attack roll, you can increase the spell's range by 60 feet.\n"
        )


class Telekinetic(_AbilityScoreFeat):
    _NAME = "Telekinetic"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Minor Telekinesis. You learn the Mage Hand spell. You can cast it without Verbal or Somatic components, you can make the spectral hand Invisible, and its range and the distance it can be away from you both increase by 30 feet when you cast it. The spell's spellcasting ability is the ability increased by this feat.\n"
            "Telekinetic Shove. As a Bonus Action, you can telekinetically shove one creature you can see within 30 feet of yourself. When you do so, the target must succeed on a Strength saving throw (DC 8 plus the ability modifier of the score increased by this feat and your Proficiency Bonus) or be moved 5 feet toward or away from you.\n"
        )


class Telepathic(_AbilityScoreFeat):
    _NAME = "Telepathic"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Telepathic Utterance. You can speak telepathically to any creature you can see within 60 feet of yourself. Your telepathic utterances are in a language you know, and the creature understands you only if it knows that language. Your communication doesn't give the creature the ability to respond to you telepathically.\n"
            "Detect Thoughts. You always have the Detect Thoughts spell prepared. You can cast it without a spell slot or spell components, and you must finish a Long Rest before you can cast it in this way again. You can also cast it using spell slots you have of the appropriate level. Your spellcasting ability for the spell is the ability increased by this feat.\n"
        )


class WarCaster(_AbilityScoreFeat):
    _NAME = "War Caster"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+, Spellcasting or Pact Magic Feature\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Concentration. You have Advantage on Constitution saving throws that you make to maintain Concentration.\n"
            "Reactive Spell. When a creature provokes an Opportunity Attack from you by leaving your reach, you can take a Reaction to cast a spell at the creature rather than making an Opportunity Attack. The spell must have a casting time of one action and must target only that creature.\n"
            "Somatic Components. You can perform the Somatic components of spells even when you have weapons or a Shield in one or both hands.\n"
        )


class WeaponMaster(_AbilityScoreFeat):
    _NAME = "Weapon Master"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Prerequisite: Level 4+\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Mastery Property. Your training with weapons allows you to use the mastery property of one kind of Simple or Martial weapon of your choice, provided you have proficiency with it. Whenever you finish a Long Rest, you can change the kind of weapon to another eligible kind.\n"
        )


# ---------------------------------------------------------------------------
# Faerun General Feats (Heroes of Faerun)
# ---------------------------------------------------------------------------


class ColdCaster(_AbilityScoreFeat):
    _NAME = "Cold Caster"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Cantrip. You learn the Ray of Frost cantrip. If you already know it, you learn a different Wizard cantrip of your choice. The spell's spellcasting ability is the ability increased by this feat.\n"
            "Frostbite. Once per turn when you hit a creature with an attack roll and deal Cold damage, you can temporarily negate the creature's defenses. The creature subtracts 1d4 from the next saving throw it makes before the end of your next turn.\n"
        )


class Dragonscarred(_AbilityScoreFeat):
    _NAME = "Dragonscarred"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.CONSTITUTION, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Cult of the Dragon Initiate Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Constitution or Charisma score by 1, to a maximum of 20.\n"
            "Damage Resistance. When you gain this feat, choose Acid, Cold, Fire, Lightning, or Poison. You have Resistance to the chosen damage type.\n"
            "Fearsome Power. When you deal damage to a creature as part of the Attack or Magic action on your turn, you can use the Dragon's Terror benefit of the Cult of the Dragon Initiate feat as a Bonus Action this turn.\n"
        )


class EnclaveMAGIC(_AbilityScoreFeat):
    _NAME = "Enclave Magic"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Emerald Enclave Fledgling Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Friend to Animals. You have Advantage on ability checks when taking the Influence action with Beasts.\n"
            "Two Hearts, One Mind. You always have the Beast Sense spell prepared. You can cast it once without a spell slot, and you regain the ability to cast it in that way when you finish a Long Rest. When you cast it without a spell slot using this feature, it doesn't require Concentration. You can also cast the spell using any spell slots you have of the appropriate level. The spell's spellcasting ability is the ability increased by this feat.\n"
        )


class FairyTrickster(_AbilityScoreFeat):
    _NAME = "Fairy Trickster"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.DEXTERITY, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Charisma ability score by 1, to a maximum of 20.\n"
            "Faerie Trod Trotter. When you take the Disengage action on your turn, Difficult Terrain doesn't cost you extra movement for the rest of that turn.\n"
            "Flustering Strike. When you hit a creature with an attack roll, you can attempt to fluster the target. The target must succeed on a Wisdom saving throw (DC 8 plus the ability modifier of the score increased by this feat and your Proficiency Bonus) or have Disadvantage on saving throws until the end of your next turn.\n"
            "You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class GenieMagic(_AbilityScoreFeat):
    _NAME = "Genie Magic"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Wish Magic. As a Magic action, you can cast a level 1 spell of your choice from the Sorcerer spell list that has a casting time of an action. Once you use this benefit, you can't do so again until you finish a Long Rest. The spell's spellcasting ability is the ability increased by this feat.\n"
            "When you reach level 11, the spell you cast with this feat is cast as though using a level 2 spell slot. When you reach level 17, the spell is cast as though using a level 3 spell slot.\n"
        )


class HarperTeamwork(_AbilityScoreFeat):
    _NAME = "Harper Teamwork"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.DEXTERITY, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Harper Agent Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Charisma score by 1, to a maximum of 20.\n"
            "Withering Wordplay. When you take the Help action to assist an ally's attack roll against an enemy, that enemy also has Disadvantage on the first saving throw it makes before the start of your next turn.\n"
            "Inspiring Willpower. If you succeed on a saving throw to end the Frightened or Paralyzed condition on yourself, you can choose one ally you can see within 30 feet of yourself that has the same condition. That condition immediately ends for that ally.\n"
        )


class LordlyResolve(_AbilityScoreFeat):
    _NAME = "Lordly Resolve"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.STRENGTH, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Lords' Alliance Agent Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Charisma score by 1, to a maximum of 20.\n"
            "Standard Bearer. As a Bonus Action, choose up to three creatures within 60 feet of yourself that can see you. Each target can immediately take a Reaction to right itself and end the Prone condition, provided its Speed isn't 0.\n"
            "Additionally, you bolster the targets' resolve, which lasts for 1 minute or until you have the Incapacitated condition. While bolstered, a target can't be possessed or gain the Charmed or Frightened condition; if a target is already possessed, Charmed, or Frightened, the target has Advantage on any new saving throw against the relevant effect.\n"
            "Once you use this benefit, you can't do so again until you finish a Long Rest.\n"
        )


class MythalTouched(_AbilityScoreFeat):
    _NAME = "Mythal Touched"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Mythal Ward. If a spell attack hits you or you fail a saving throw against a spell, you can take a Reaction to roll on the Mythal-Touched Magic table to create a magical effect. If an effect requires a saving throw, the DC equals 8 plus the modifier of the ability increased by this feat and your Proficiency Bonus.\n"
            "You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Mythal-Touched Magic (roll 1d20):\n"
            "1-2: You and each creature within 15 feet of you make a Dexterity saving throw, taking Force damage equal to 1d8 times the level of the triggering spell on a failed save or half as much on a success.\n"
            "3-7: You and the triggering spell's caster form a telepathic link for 1 hour.\n"
            "8-10: Gravity is reversed in a 15-foot-radius, 60-foot-tall Cylinder centered on you for 1 minute, per the Reverse Gravity spell.\n"
            "11-13: You and the triggering spell's caster each make a Constitution saving throw. On a failed save, the creature has the Stunned condition until the end of its next turn.\n"
            "14-17: You gain a +2 bonus to AC for 1 minute, potentially turning the triggering spell into a miss if it was a spell attack.\n"
            "18-19: Any flammable, nonmagical object within 10 feet of the triggering spell's caster bursts into flame, takes 1d4 Fire damage, and is burning.\n"
            "20: The triggering spell dissipates with no effect, and the action used to cast it is wasted. If cast with a spell slot, the slot isn't expended."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class OrdersResilience(_AbilityScoreFeat):
    _NAME = "Order's Resilience"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.STRENGTH, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Tyro of the Gauntlet Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Resurge. When you have the Prone condition, you can right yourself with only 5 feet of movement.\n"
            "Stronger Together. If you are within 5 feet of an ally that doesn't have the Incapacitated condition, you and that ally have Advantage on Strength saving throws. You can't use this benefit while you have the Incapacitated condition.\n"
        )


class PurpleDragonCommandant(_AbilityScoreFeat):
    _NAME = "Purple Dragon Commandant"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "General Feat (Prerequisite: Level 4+, Purple Dragon Rook Feat or Martial Weapon Proficiency)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Encourage Ally. As a Bonus Action, you bolster one ally you can see within 30 feet. The ally gains Temporary Hit Points equal to 2d6 plus the modifier of the ability score increased by this feat. You can take this Bonus Action a number of times equal to your Proficiency Bonus, and you regain all uses when you finish a Long Rest.\n"
            "Last Stand. You have Advantage on attack rolls while Bloodied."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class SpellfireAdept(_AbilityScoreFeat):
    _NAME = "Spellfire Adept"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.INTELLIGENCE, Ability.WISDOM, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Spellfire Spark Feat or the Spellcasting or Pact Magic Feature)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Intelligence, Wisdom, or Charisma score by 1, to a maximum of 20.\n"
            "Fueled Spellfire. Once per turn, when a spell you cast deals Radiant damage, you can expend up to two Hit Point Dice, roll them, and add the total rolled to one damage roll of the spell.\n"
            "Searing Spellfire. When you make a damage roll that deals Radiant damage, it ignores Resistance to Radiant damage.\n"
        )


class StreetJustice(_AbilityScoreFeat):
    _NAME = "Street Justice"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.STRENGTH, Ability.DEXTERITY)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength or Dexterity score by 1, to a maximum of 20.\n"
            "Headlock. Your allies have Advantage on attack rolls against a creature Grappled by you.\n"
            "Sturdy Knot. When you use Chain, Manacles, or Rope to bind a creature, add your Proficiency Bonus to the DC to escape or burst the Chain, Manacles, or Rope.\n"
            "Tough Talk. A creature's Hostile attitude doesn't impose Disadvantage on your Charisma (Intimidation) checks to influence that creature.\n"
        )


class ZhentarimTactics(_AbilityScoreFeat):
    _NAME = "Zhentarim Tactics"
    _ORIGIN = "General Feat Level 4+ (Faerun)"
    _ABILITIES = (Ability.DEXTERITY, Ability.CHARISMA)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "General Feat (Prerequisite: Level 4+, Zhentarim Ruffian Feat)\n"
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Dexterity or Charisma score by 1, to a maximum of 20.\n"
            "Retaliate. Immediately after a creature within 5 feet of you hits you with a melee attack, you can make an Opportunity Attack against that creature.\n"
            "Versatile Merc. When you finish a Long Rest, choose a skill in which you have proficiency. You have Expertise in that skill until you finish your next Long Rest.\n"
        )


# ---------------------------------------------------------------------------
# Ravenloft Campaign General Feats
# ---------------------------------------------------------------------------


class DarkGift(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Dark Gift requires character level 1 or higher.")
        super().__init__(
            name="Dark Gift",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Exposure to alien horrors like those of the Far Realm has warmed your physical form in supernatural ways. You gain the following features.\n"
            " * Breathless. You can hold your breath for 1 hour.\n"
            " * Extrasensory Perception. You have proficiency in the Perception skill, if you lack it. You also gain Expertise in that skill.\n"
            " * Blindsight. In addition, you have Blindsight with a range of 15 feet.\n"
            " * Warping Flesh. Immediately after you make a D20 Test and roll a 1 on the d20, the aberrant influence infecting your form flares, wrenching control of your flesh. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Stunned condition until the end of your next turn."
        )


class EchoingSoul(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Echoing Soul requires character level 1 or higher.")
        super().__init__(
            name="Echoing Soul",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You experience echoes from a past or alternate life. You gain the following features.\n"
            " * Channelled Prowess. You have proficiency in two skills of your choice. In addition, choose one skill you have proficiency in. You gain Expertise in that skill. Whenever you finish a Long Rest you can change your choice of for this benefit.\n"
            " * Inherent Tongues. You know one additional language of your choice, which you choose from the language tables in the Player's Handbook.\n"
            " * Intrusive Echoes. Immediately after you make a D20 Test and roll a 1 on the d20, memories and sensations from your soul's other life threaten to overtake you. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Incapacitated condition until the end of your next turn. While you are Incapacitated in this way, your Speed is halved."
        )


class GatheredWhispers(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Gathered Whispers requires character level 1 or higher.")
        super().__init__(
            name="Gathered Whispers",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "You are haunted by a cacophony of whispering spirits only you can hear. You gain the following features.\n"
            " * Spirit Whispers. You learn the Message spell and can cast it without Material components. Additionally, you always have the Augury spell prepared. You can cast it without a spell slot or spell components, and you must finish a Long Rest before you can cast it in this way again. You can also cast the spell using any spell slots you have.\n"
            " * Intelligence, Wisdom, or Charisma is your spellcasting ability for this benefit (choose when you select this feat).\n"
            " * Unearthly Scream. When you are hit by an attack roll, you can take a Reaction to channel your haunting spirits into a protective, otherworldly scream. You can add your Proficiency Bonus to your AC against that attack, potentially causing it to miss. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Voices from Beyond. Immediately after you make a D20 Test and roll a 1 on the d20, the haunting whispers rise to a ghastly volume. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Deafened condition until the end of your next turn. While Deafened, you have Disadvantage on ability checks and attack rolls."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class LivingShadow(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Living Shadow requires character level 1 or higher.")
        super().__init__(
            name="Living Shadow",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "The shadow you cast is animate and ever-present - sometimes it even acts according to its own will. You gain the following features.\n"
            " * Grasping Shadow. You learn the Mage Hand spell and can cast it without spell components. Intelligence, Wisdom or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            " * Lengthened Strike. When you make a melee attack roll as part of the Attack or Magic action on your turn, you can increase your reach for that attack by 10 feet, as your shadow stretches to aid you. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Ominous Will. Immediately after you make a D20 Test and roll a 1 on the d20, your shadow attempts to exert its will. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Incapacitated condition until the start of your next turn, at which point you must roll on the Shadow's Will table to determine what you do during that turn.\n"
            "Shadow's Will\n"
            "1d8\tBehaviour\n"
            "1\tYou don't take any action or a Bonus Action, and you use all your movement to move. Roll 1d4 for the direction 1, north: 2, east; 3, south; 4, west.\n"
            "2-6\tYou don't move or take a Bonus Action, and you take the Attack action to make one melee attack against a random creature within reach. If none are within reach, you take no action.\n"
            "7-8\tYou have the Prone condition, and your turn ends."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class MistWalker(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Mist Walker requires character level 1 or higher.")
        super().__init__(
            name="Mist Walker",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "You know how to slip through the Mists' grasp, but this freedom comes at a price: If you remain in one area for too long, the Mists find you and drain your life force. You gain the following features.\n"
            "Domain Traveler. When you enter the Mists intent on reaching a specific domain, you are treated as if you possess a Mist talisman keyed to that domain. To use this feature, you must know the name of the domain you have chosen as your destination, but you don't need to have previously visited that land. This trait doesn't allow you to bypass domain borders closed by a Darklord's will.\n"
            "Mist Walk. When you take damage or fail a saving throw to avoid or end the Grappled or Restrained condition, you can take a Reaction and teleport up to 15 feet to an unoccupied space you can see. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Poisoned Roots. When you finish a Long Rest, the world around you in a 10-mile radius becomes a siphon that leeches away at your vitality. Whenever you finish a Short Rest in that area, make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you get no benefits from finishing that rest."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class SecondSkin(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Second Skin requires character level 1 or higher.")
        super().__init__(
            name="Second Skin",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "Your skin is toughened and hardened by the Mists, granting you unnatural resilience. You gain the following features.\n"
            " * Hardened Skin. Your base AC becomes 13 + your Dexterity modifier. You can use a shield and still gain this benefit.\n"
            " * Resilient Form. When you take damage, you can take a Reaction to reduce that damage by an amount equal to your Proficiency Bonus. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Vulnerable Weakness. Immediately after you make a D20 Test and roll a 1 on the d20, your toughened skin becomes brittle and vulnerable. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Vulnerable condition until the end of your next turn.\n"
            "After you experience the catalyst, at the start of your next turn, make a Charisma saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you immediately use Alternate Form to cast Alter Self without a spell slot. If you've already expended the use of that feature, you instead have the Stunned condition until the start of your next turn.\n"
            "Change Catalyst\n"
            "1d6\tCatalyst\n"
            "1\tSeeing a particular phase of the moon\n"
            "2\tSmelling the scent of a certain type of flower\n"
            "3\tHearing temple bells ringing\n"
            "4\tHearing a particular melody\n"
            "5\tTouching pure silver with your bare skin\n"
            "6\tSeeing someone who resembles a specific individual\n"
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class SymbioticBeing(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Symbiotic Being requires character level 1 or higher.")
        super().__init__(
            name="Symbiotic Being",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        description = (
            "A second being resides within your body, offering knowledge and assistance while furthering its own agenda. You gain the following features.\n"
            "Entwined Existence. The symbiote can't be targeted. If you die, so does your symbiote. If you are returned to life, your symbiote also revives.\n"
            "Second Mind. You gain proficiency in one of the following skills: Arcana, Deception, History, Intimidation, Insight, Investigation, Nature, Religion, Perception, or Persuasion. You also know one additional language of your choice, chosen from the language tables in the Player's Handbook.\n"
            "Sustained Symbiosis. When you fail a saving throw, you can take a Reaction and expend one of your Hit Dice. Roll the die and add the number rolled to the saving throw, potentially turning the failure into a success.\n"
            "You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Symbiotic Agenda. Immediately after you make a D20 Test and roll a 1 on the d20, your symbiote attempts to assert control. Make a Charisma saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Charmed condition for 1d12 hours. While Charmed, you must try to follow the symbiote's commands and further its goals, as determined by the DM. Whenever you take damage, you can repeat this save, ending the effect on a success.\n"
            "At the DM's discretion, you might make this saving throw whenever you act contrary to the symbiote's agenda."
        )
        return StringUtils.add_boxes(description, proficiency_bonus)


class TouchOfDeath(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Touch of Death requires character level 1 or higher.")
        super().__init__(
            name="Touch of Death",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Deathly power resides within you, bursting out at the slightest provocation. You gain the following features.\n"
            "Death Touch. You learn the Chill Touch spell and can cast it without spell components. Necrotic damage you deal with this spell ignores Resistance. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            "Pull of the Grave. You have Disadvantage on Death Saving Throws."
        )


class Watchers(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Watchers requires character level 1 or higher.")
        super().__init__(
            name="Watchers",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "Something unnatural is always watching you, taking the form of scurrying vermin and other eerie creatures. You gain the following features.\n"
            "Borrowed Eyes. You always have the Beast Sense and Speak with Animals spells prepared. You can cast each spell without a spell slot, and you must finish a Long Rest before you can cast it in this way again. You can also cast these spells using spell slots you have of the appropriate level.\n"
            "Heightened Suspicion. Whenever you take the Search action, you can roll 1d4 and add the number rolled to any ability check made as part of that action.\n"
            "Incessant Watchers. You have Disadvantage on saving throws made against the Scrying spell.\n"
            "In addition, immediately after you make a D20 Test and roll a 1 on the d20, paranoia threatens to overwhelm you. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have Disadvantage on D20 Tests for 1 minute. You can repeat the save at the end of each of your turns, ending the effect early on a success."
        )
