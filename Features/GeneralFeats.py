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


class MountedCombatant(GeneralFeatTextFeature):
    def __init__(self, character_level: int, ability: Ability):
        if character_level < 4:
            raise ValueError("Mounted Combatant requires character level 4 or higher.")
        if ability not in [Ability.STRENGTH, Ability.DEXTERITY, Ability.WISDOM]:
            raise ValueError(
                "Mounted Combatant ability increase must be Strength, Dexterity, or Wisdom."
            )
        self.ability = ability
        super().__init__(
            name="Mounted Combatant",
            origin="General Feat Level 4+",
        )

    def modify(self, character_stat_block: CharacterStatBlock):
        # Player chooses one; here we assume a selection system exists.
        # Replace with your actual choice handling if needed.
        character_stat_block.abilities.add_bonus(self.ability, 1)

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "You gain the following benefits.\n"
            "Ability Score Increase. Increase your Strength, Dexterity, or Wisdom score by 1, to a maximum of 20.\n"
            "Mounted Strike. While mounted, you have Advantage on attack rolls against any unmounted creature within 5 feet of your mount that is at least one size smaller than the mount.\n"
            "Leap Aside. If your mount is subjected to an effect that allows it to make a Dexterity saving throw to take only half damage, it instead takes no damage if it succeeds on the saving throw and only half damage if it fails. For your mount to gain this benefit, you must be riding it, and neither of you can have the Incapacitated condition.\n"
            "Veer. While mounted, you can force an attack that hits your mount to hit you instead if you don't have the Incapacitated condition.\n"
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


class DarkGift(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Dark Gift requires character level 1 or higher.")
        super().__init__(
            name="Dark Gift",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Exposure to alien horrors like those of the Far Realm has warmed your physical form in supernatural ways. You gain the following features.\n"
            " * Breathless. You can hold your breath for 1 hour.\n"
            " * Extrasensory Perception. You have proficiency in the Perception skill, if you lack it. You also gain Expertise in that skill.\n"
            " * Blindsight. In addition, you have Blindsight with a range of 15 feet.\n"
            " * Warping Flesh. Immediately after you make a D20 Test and roll a 1 on the d20, the aberrant influence infecting your form flares, wrenching control of your flesh. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Stunned condition until the end of your next turn."
        )
        return text


class EchoingSoul(GeneralFeatTextFeature):
    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Echoing Soul requires character level 1 or higher.")
        super().__init__(
            name="Echoing Soul",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "You experience echoes from a past or alternate life. You gain the following features.\n"
            " * Channelled Prowess. You have proficiency in two skills of your choice. In addition, choose one skill you have proficiency in. You gain Expertise in that skill. Whenever you finish a Long Rest you can change your choice of for this benefit.\n"
            " * Inherent Tongues. You know one additional language of your choice, which you choose from the language tables in the Player's Handbook.\n"
            " * Intrusive Echoes. Immediately after you make a D20 Test and roll a 1 on the d20, memories and sensations from your soul's other life threaten to overtake you. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Incapacitated condition until the end of your next turn. While you are Incapacitated in this way, your Speed is halved."
        )
        return text


class GatheredWhispers(GeneralFeatTextFeature):
    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Gathered Whispers requires character level 1 or higher.")
        super().__init__(
            name="Gathered Whispers",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "You are haunted by a cacophony of whispering spirits only you can hear. You gain the following features.\n"
            " * Spirit Whispers. You learn the Message spell and can cast it without Material components. Additionally, you always have the Augury spell prepared. You can cast it without a spell slot or spell components, and you must finish a Long Rest before you can cast it in this way again. You can also cast the spell using any spell slots you have.\n"
            " * Intelligence, Wisdom, or Charisma is your spellcasting ability for this benefit (choose when you select this feat).\n"
            " * Unearthly Scream. When you are hit by an attack roll, you can take a Reaction to channel your haunting spirits into a protective, otherworldly scream. You can add your Proficiency Bonus to your AC against that attack, potentially causing it to miss. You can use this benefit a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Voices from Beyond. Immediately after you make a D20 Test and roll a 1 on the d20, the haunting whispers rise to a ghastly volume. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Deafened condition until the end of your next turn. While Deafened, you have Disadvantage on ability checks and attack rolls."
        )
        return text


class LivingShadow(GeneralFeatTextFeature):
    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Living Shadow requires character level 1 or higher.")
        super().__init__(
            name="Living Shadow",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "The shadow you cast is animate and ever-present - sometimes it even acts according to its own will. You gain the following features.\n"
            " * Grasping Shadow. You learn the Mage Hand spell and can cast it without spell components. Intelligence, Wisdom or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            " * Lengthened Strike. When you make a melee attack roll as part of the Attack or Magic action on your turn, you can increase your reach for that attack by 10 feet, as your shadow stretches to aid you. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Ominous Will. Immediately after you make a D20 Test and roll a 1 on the d20, your shadow attempts to exert its will. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Incapacitated condition until the start of your next turn, at which point you must roll on the Shadow's Will table to determine what you do during that turn.\n"
            "Shadow's Will\n"
            "1d8	Behaviour\n"
            "1	You don't take any action or a Bonus Action, and you use all your movement to move. Roll 1d4 for the direction 1, north: 2, east; 3, south; 4, west.\n"
            "2-6	You don't move or take a Bonus Action, and you take the Attack action to make one melee attack against a random creature within reach. If none are within reach, you take no action.\n"
            "7-8	You have the Prone condition, and your turn ends."
        )
        return text


class MistWalker(GeneralFeatTextFeature):
    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Mist Walker requires character level 1 or higher.")
        super().__init__(
            name="Mist Walker",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "You know how to slip through the Mists’ grasp, but this freedom comes at a price: If you remain in one area for too long, the Mists find you and drain your life force. You gain the following features.\n"
            "Domain Traveler. When you enter the Mists intent on reaching a specific domain, you are treated as if you possess a Mist talisman keyed to that domain. To use this feature, you must know the name of the domain you have chosen as your destination, but you don’t need to have previously visited that land. This trait doesn’t allow you to bypass domain borders closed by a Darklord’s will.\n"
            "Mist Walk. When you take damage or fail a saving throw to avoid or end the Grappled or Restrained condition, you can take a Reaction and teleport up to 15 feet to an unoccupied space you can see. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Poisoned Roots. When you finish a Long Rest, the world around you in a 10-mile radius becomes a siphon that leeches away at your vitality. Whenever you finish a Short Rest in that area, make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you get no benefits from finishing that rest."
        )
        return text


class SecondSkin(GeneralFeatTextFeature):

    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Second Skin requires character level 1 or higher.")
        super().__init__(
            name="Second Skin",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Your skin is toughened and hardened by the Mists, granting you unnatural resilience. You gain the following features.\n"
            " * Hardened Skin. Your base AC becomes 13 + your Dexterity modifier. You can use a shield and still gain this benefit.\n"
            " * Resilient Form. When you take damage, you can take a Reaction to reduce that damage by an amount equal to your Proficiency Bonus. You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            " * Vulnerable Weakness. Immediately after you make a D20 Test and roll a 1 on the d20, your toughened skin becomes brittle and vulnerable. Make a Constitution saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Vulnerable condition until the end of your next turn.\n"
            "After you experience the catalyst, at the start of your next turn, make a Charisma saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you immediately use Alternate Form to cast Alter Self without a spell slot. If you’ve already expended the use of that feature, you instead have the Stunned condition until the start of your next turn.\n"
            "Change Catalyst\n"
            "1d6	Catalyst\n"
            "1	Seeing a particular phase of the moon\n"
            "2	Smelling the scent of a certain type of flower\n"
            "3	Hearing temple bells ringing\n"
            "4	Hearing a particular melody\n"
            "5	Touching pure silver with your bare skin\n"
            "6	Seeing someone who resembles a specific individual\n"
        )
        return text


class SymbioticBeing(GeneralFeatTextFeature):
    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Symbiotic Being requires character level 1 or higher.")
        super().__init__(
            name="Symbiotic Being",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "A second being resides within your body, offering knowledge and assistance while furthering its own agenda. You gain the following features.\n"
            "Entwined Existence. The symbiote can’t be targeted. If you die, so does your symbiote. If you are returned to life, your symbiote also revives.\n"
            "Second Mind. You gain proficiency in one of the following skills: Arcana, Deception, History, Intimidation, Insight, Investigation, Nature, Religion, Perception, or Persuasion. You also know one additional language of your choice, chosen from the language tables in the Player’s Handbook.\n"
            "Sustained Symbiosis. When you fail a saving throw, you can take a Reaction and expend one of your Hit Dice. Roll the die and add the number rolled to the saving throw, potentially turning the failure into a success.\n"
            "You can use this feature a number of times equal to your Proficiency Bonus, and you regain all expended uses when you finish a Long Rest.\n"
            "Symbiotic Agenda. Immediately after you make a D20 Test and roll a 1 on the d20, your symbiote attempts to assert control. Make a Charisma saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have the Charmed condition for 1d12 hours. While Charmed, you must try to follow the symbiote’s commands and further its goals, as determined by the DM. Whenever you take damage, you can repeat this save, ending the effect on a success.\n"
            "At the DM’s discretion, you might make this saving throw whenever you act contrary to the symbiote’s agenda."
        )
        return text


class TouchOfDeath(GeneralFeatTextFeature):
    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Touch of Death requires character level 1 or higher.")
        super().__init__(
            name="Touch of Death",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Deathly power resides within you, bursting out at the slightest provocation. You gain the following features.\n"
            "Death Touch. You learn the Chill Touch spell and can cast it without spell components. Necrotic damage you deal with this spell ignores Resistance. Intelligence, Wisdom, or Charisma is your spellcasting ability for this spell (choose when you select this feat).\n"
            "Pull of the Grave. You have Disadvantage on Death Saving Throws."
        )
        return text


class Watchers(GeneralFeatTextFeature):
    def __init__(self, character_level: int):
        if character_level < 1:
            raise ValueError("Watchers requires character level 1 or higher.")
        super().__init__(
            name="Watchers",
            origin="General Feat Ravenloft Campaign",
        )

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        text = (
            "Something unnatural is always watching you, taking the form of scurrying vermin and other eerie creatures. You gain the following features.\n"
            "Borrowed Eyes. You always have the Beast Sense and Speak with Animals spells prepared. You can cast each spell without a spell slot, and you must finish a Long Rest before you can cast it in this way again. You can also cast these spells using spell slots you have of the appropriate level.\n"
            "Heightened Suspicion. Whenever you take the Search action, you can roll 1d4 and add the number rolled to any ability check made as part of that action.\n"
            "Incessant Watchers. You have Disadvantage on saving throws made against the Scrying spell.\n"
            "In addition, immediately after you make a D20 Test and roll a 1 on the d20, paranoia threatens to overwhelm you. Make a Wisdom saving throw (DC 13 plus your Proficiency Bonus). On a failed save, you have Disadvantage on D20 Tests for 1 minute. You can repeat the save at the end of each of your turns, ending the effect early on a success."
        )
        return text
