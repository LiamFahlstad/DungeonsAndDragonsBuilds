from Core.Definitions import MONK_HIT_DIE
from CharacterContent.Features.Core.BaseFeatures import Feature
from StatBlocks.CharacterStatBlock import CharacterStatBlock


class ArmsOfTheAstralSelf(Feature):
    def __init__(self):
        super().__init__(name="Arms of the Astral Self", origin="Way of the Astral Self Monk Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "At 3rd level, your mastery of your ki allows you to summon a portion of your astral self. As a bonus action, you can spend 1 ki point to summon the arms of your astral self. When you do so, each creature of your choice that you can see within 10 feet of you must succeed on a Dexterity saving throw or take force damage equal to two rolls of your Martial Arts die.\n"
            "\n"
            "For 10 minutes, these spectral arms hover near your shoulders or surround your arms (your choice). You determine the arms' appearance, and they vanish early if you are incapacitated or die.\n"
            "\n"
            "While the spectral arms are present, you gain the following benefits:\n"
            "    * You can use your Wisdom modifier in place of your Strength modifier when making Strength checks and Strength saving throws.\n"
            "    * You can use the spectral arms to make unarmed strikes.\n"
            "    * When you make an unarmed strike with the arms on your turn, your reach for it is 5 feet greater than normal.\n"
            "    * The unarmed strikes you make with the arms can use your Wisdom modifier in place of your Strength or Dexterity modifier for the attack and damage rolls, and their damage type is force."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus action"),
            ("Cost", "1 ki point"),
            ("Duration", "10 minutes"),
            ("Range", "10 feet"),
            ("Save", "Dexterity"),
            ("Damage", "2d (force, where d = Martial Arts die)"),
            ("Benefits", "Use Wisdom for Strength checks/saves, reach +5 ft, use Wisdom for attack/damage rolls with arms"),
        ]


class VisageOfTheAstralSelf(Feature):
    def __init__(self):
        super().__init__(name="Visage of the Astral Self", origin="Way of the Astral Self Monk Level 6")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "When you reach 6th level, you can summon the visage of your astral self. As a bonus action, or as part of the bonus action you take to activate Arms of the Astral Self, you can spend 1 ki point to summon this visage for 10 minutes. It vanishes early if you are incapacitated or die.\n"
            "\n"
            "The spectral visage covers your face like a helmet or mask. You determine its appearance.\n"
            "\n"
            "While the spectral visage is present, you gain the following benefits.\n"
            "\n"
            "Astral Sight. You can see normally in darkness, both magical and nonmagical, to a distance of 120 feet.\n"
            "\n"
            "Wisdom of the Spirit. You have advantage on Wisdom (Insight) and Charisma (Intimidation) checks.\n"
            "\n"
            "Word of the Spirit. When you speak, you can direct your words to a creature of your choice that you can see within 60 feet of you, making it so only that creature can hear you. Alternatively, you can amplify your voice so that all creatures within 600 feet can hear you."
        )
        return description


class BodyOfTheAstralSelf(Feature):
    def __init__(self):
        super().__init__(name="Body of the Astral Self", origin="Way of the Astral Self Monk Level 11")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 11th level, when you have both your astral arms and visage summoned, you can cause the body of your astral self to appear (no action required). This spectral body covers your physical form like a suit of armor, connecting with the arms and visage. You determine its appearance.\n"
            "\n"
            "While the spectral body is present, you gain the following benefits.\n"
            "\n"
            "Deflect Energy. When you take acid, cold, fire, force, lightning, or thunder damage, you can use your reaction to deflect it. When you do so, the damage you take is reduced by 1d10 + your Wisdom modifier (minimum reduction of 1).\n"
            "\n"
            "Empowered Arms. Once on each of your turns when you hit a target with the Arms of the Astral Self, you can deal extra damage to the target equal to your Martial Arts die."
        )
        return description


class AwakenedAstralSelf(Feature):
    def __init__(self):
        super().__init__(name="Awakened Astral Self", origin="Way of the Astral Self Monk Level 17")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "Starting at 17th level, your connection to your astral self is complete, allowing you to unleash its full potential. As a bonus action, you can spend 5 ki points to summon the arms, visage, and body of your astral self and awaken it for 10 minutes. This awakening ends early if you are incapacitated or die.\n"
            "\n"
            "While your astral self is awakened, you gain the following benefits.\n"
            "\n"
            "Armor of the Spirit. You gain a +2 bonus to Armor Class.\n"
            "\n"
            "Astral Barrage. Whenever you use the Extra Attack feature to attack twice, you can instead attack three times if all the attacks are made with your astral arms."
        )
        return description

    def get_table_description(self, character_stat_block: CharacterStatBlock) -> list[tuple[str, str]]:
        return [
            ("Action", "Bonus action"),
            ("Cost", "5 ki points"),
            ("Duration", "10 minutes"),
            ("AC Bonus", "+2"),
            ("Extra Attacks", "3 attacks with Extra Attack (instead of 2) if all use astral arms"),
        ]
