class PsionicPower(TextFeature):
    def __init__(self):
        super().__init__(name="Psionic Power", origin="Psi Warrior Fighter Level 3")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You harbor a wellspring of psionic energy within yourself. It is represented by your Psionic Energy Dice, which fuel powers you have from this subclass. The Psi Warrior Energy Dice table shows the die size and number of these dice you have when you reach certain Fighter levels.\n"
            "Psi Warrior Energy Dice\n"
            "Fighter Level	Die Size	Number\n"
            "3	D6	4\n"
            "5	D8	6\n"
            "9	D8	8\n"
            "11	D10	8\n"
            "13	D10	10\n"
            "17	D12	12\n"
            "Any features in this subclass that use a Psionic Energy Die use only the dice from this subclass. Some of your powers expend the Psionic Energy Die, as specified in a power’s description, and you can’t use a power if it requires you to use a die when all your Psionic Energy Dice are expended.\n"
            "You regain one of your expended Psionic Energy Dice when you finish a Short Rest, and you regain all of them when you finish a Long Rest.\n"
            "Protective Field. When you or another creature you can see within 30 feet of you takes damage, you can take a Reaction to expend one Psionic Energy Die, roll the die, and reduce the damage taken by the number rolled plus your Intelligence modifier (minimum reduction of 1), as you create a momentary shield of telekinetic force.\n"
            "Psionic Strike. You can propel your weapons with psionic force. Once on each of your turns, immediately after you hit a target within 30 feet of yourself with an attack and deal damage to it with a weapon, you can expend one Psionic Energy Die, rolling it and dealing Force damage to the target equal to the number rolled plus your Intelligence modifier.\n"
            "Telekinetic Movement. You can move an object or a creature with your mind. As a Magic action, choose one target you can see within 30 feet of yourself; the target must be a loose object that is Large or smaller or one willing creature other than you. You transport the target up to 30 feet to an unoccupied space you can see. Alternatively, if the target is a Tiny object, you can transport it to or from your hand.\n"
            "Once you take this action, you can’t do so again until you finish a Short or Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description


class TelekineticAdept(TextFeature):
    def __init__(self):
        super().__init__(name="Telekinetic Adept", origin="Psi Warrior Fighter Level 7")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have mastered new ways to use your telekinetic abilities, detailed below.\n"
            "Psi-Powered Leap. As a Bonus Action, you gain a Fly Speed equal to twice your Speed until the end of the current turn. Once you take this Bonus Action, you can’t do so again until you finish a Short or Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it.\n"
            "Telekinetic Thrust. When you deal damage to a target with your Psionic Strike, you can force the target to make a Strength saving throw (DC 8 plus your Intelligence modifier and Proficiency Bonus). On a failed save, you can give the target the Prone condition or transport it up to 10 feet horizontally."
        )
        return description


class GuardedMind(TextFeature):
    def __init__(self):
        super().__init__(name="Guarded Mind", origin="Psi Warrior Fighter Level 10")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You have Resistance to Psychic damage. Moreover, if you start your turn with the Charmed or Frightened condition, you can expend a Psionic Energy Die (no action required) and end every effect on yourself giving you those conditions."
        )
        return description


class BulwarkofForce(TextFeature):
    def __init__(self):
        super().__init__(name="Bulwark of Force", origin="Psi Warrior Fighter Level 15")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You can shield yourself and others with telekinetic force. As a Bonus Action, you can choose creatures, including yourself, within 30 feet of yourself, up to a number of creatures equal to your Intelligence modifier (minimum of one creature). Each of the chosen creatures has Half Cover for 1 minute or until you have the Incapacitated condition.\n"
            "Once you use this feature, you can’t do so again until you finish a Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description


class TelekineticMaster(TextFeature):
    def __init__(self):
        super().__init__(name="Telekinetic Master", origin="Psi Warrior Fighter Level 18")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        description = (
            "You always have the telekinesis spell prepared. With this feature, you can cast it without a spell slot or components, and your spellcasting ability for it is Intelligence. On each of your turns while you maintain Concentration on it, including the turn when you cast it, you can make one attack with a weapon as a Bonus Action.\n"
            "Once you cast the spell with this feature, you can’t do so in this way again until you finish a Long Rest unless you expend a Psionic Energy Die (no action required) to restore your use of it."
        )
        return description


