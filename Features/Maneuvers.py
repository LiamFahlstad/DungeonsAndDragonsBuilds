from StatBlocks.CharacterStatBlock import CharacterStatBlock
from Features.BaseFeatures import TextFeature
from Definitions import Ability


class Maneuver(TextFeature):
    def __init__(self, name: str):
        super().__init__(name=name, origin="Maneuver")


class ManeuverWithSavingThrow(Maneuver):
    def get_saving_throw_dc(self, character_stat_block: CharacterStatBlock) -> int:
        """Calculates the saving throw DC for maneuvers that require one."""
        proficiency_bonus = character_stat_block.get_proficiency_bonus()
        # Assuming the maneuver uses Strength or Dexterity for the saving throw; adjust as needed
        strength_modifier = character_stat_block.get_ability_modifier(Ability.STRENGTH)
        dexterity_modifier = character_stat_block.get_ability_modifier(
            Ability.DEXTERITY
        )
        ability_modifier = max(strength_modifier, dexterity_modifier)
        return 8 + proficiency_bonus + ability_modifier


class Ambush(Maneuver):
    def __init__(self):
        super().__init__(name="Ambush:")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Ambush: When you make a Dexterity (Stealth) check or an initiative roll, you can expend one superiority die and add the die to the roll, provided you aren't incapacitated."


class BaitAndSwitch(Maneuver):
    def __init__(self):
        super().__init__(name="Bait and Switch")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Bait and Switch: When you're within 5 feet of a creature on your turn, you can expend one superiority die and switch places with that creature, provided you spend at least 5 feet of movement and the creature is willing and isn't incapacitated. This movement doesn't provoke opportunity attacks. Roll the superiority die. Until the start of your next turn, you or the other creature (your choice) gains a bonus to AC equal to the number rolled."


class Brace(Maneuver):
    def __init__(self):
        super().__init__(name="Brace")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Brace: When a creature you can see moves into the reach you have with the melee weapon you're wielding, you can use your reaction to expend one superiority die and make one attack against the creature, using that weapon. If the attack hits, add the superiority die to the weapon's damage roll."


class CommandersStrike(Maneuver):
    def __init__(self):
        super().__init__(name="Commander's Strike")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Commander's Strike: When you take the Attack action on your turn, you can forgo one of your attacks and use a bonus action to direct one of your companions to strike. When you do so, choose a friendly creature who can see or hear you and expend one superiority die. That creature can immediately use its reaction to make one weapon attack, adding the superiority die to the attack's damage roll."


class CommandingPresence(Maneuver):
    def __init__(self):
        super().__init__(name="Commanding Presence")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Commanding Presence: When you make a Charisma (Intimidation), a Charisma (Performance), or a Charisma (Persuasion) check, you can expend one superiority die and add the superiority die to the ability check."


class DisarmingAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(name="Disarming Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        dc = self.get_saving_throw_dc(character_stat_block)
        return f"Disarming Attack: When you hit a creature with a weapon attack, you can expend one superiority die to attempt to disarm the target, forcing it to drop one item of your choice that it's holding. You add the superiority die to the attack's damage roll, and the target must make a Strength saving throw (DC {dc}). On a failed save, it drops the object you choose. The object lands at its feet."


class DistractingStrike(Maneuver):
    def __init__(self):
        super().__init__(name="Distracting Strike")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Distracting Strike: When you hit a creature with a weapon attack, you can expend one superiority die to distract the creature, giving your allies an opening. You add the superiority die to the attack's damage roll. The next attack roll against the target by an attacker other than you has advantage if the attack is made before the start of your next turn."


class EvasiveFootwork(Maneuver):
    def __init__(self):
        super().__init__(name="Evasive Footwork")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Evasive Footwork: When you move, you can expend one superiority die, rolling the die and adding the number rolled to your AC until you stop moving."


class FeintingAttack(Maneuver):
    def __init__(self):
        super().__init__(name="Feinting Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Feinting Attack: You can expend one superiority die and use a bonus action on your turn to feint, choosing one creature within 5 feet of you as your target. You have advantage on your next attack roll against that creature this turn. If that attack hits, add the superiority die to the attack's damage roll."


class GoadingAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(name="Goading Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        dc = self.get_saving_throw_dc(character_stat_block)
        return (
            "When you hit a creature with an attack roll, you can expend one Superiority\n"
            "Die to attempt to goad the target into attacking you. Add the Superiority Die to the attack's\n"
            f"damage roll. The target must succeed on a Wisdom saving throw (DC {dc}) or the target has\n"
            "Disadvantage on attack rolls against targets other than you until the end of your next turn.\n"
        )


class GrapplingStrike(Maneuver):
    def __init__(self):
        super().__init__(name="Grappling Strike")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Grappling Strike: Immediately after you hit a creature with a melee attack on your turn, you can expend one superiority die and then try to grapple the target as a bonus action (see the Player's Handbook for rules on grappling). Add the superiority die to your Strength (Athletics) check."


class LungingAttack(Maneuver):
    def __init__(self):
        super().__init__(name="Lunging Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Lunging Attack: When you make a melee weapon attack on your turn, you can expend one superiority die to increase your reach for that attack by 5 feet. If you hit, you add the superiority die to the attack's damage roll."


class ManeuveringAttack(Maneuver):
    def __init__(self):
        super().__init__(name="Maneuvering Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Maneuvering Attack: When you hit a creature with a weapon attack, you can expend one superiority die to maneuver one of your comrades into a more advantageous position. You add the superiority die to the attack's damage roll, and you choose a friendly creature who can see or hear you. That creature can use its reaction to move up to half its speed without provoking opportunity attacks from the target of your attack."


class MenacingAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(name="Menacing Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        dc = self.get_saving_throw_dc(character_stat_block)
        return f"Menacing Attack: When you hit a creature with a weapon attack, you can expend one superiority die to attempt to frighten the target. You add the superiority die to the attack's damage roll, and the target must make a Wisdom saving throw (DC {dc}) . On a failed save, it is frightened of you until the end of your next turn."


class Parry(Maneuver):
    def __init__(self):
        super().__init__(name="Parry")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Parry: When another creature damages you with a melee attack, you can use your reaction and expend one superiority die to reduce the damage by the number you roll on your superiority die + your Dexterity modifier."


class PrecisionAttack(Maneuver):
    def __init__(self):
        super().__init__(name="Precision Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Precision Attack: When you make a weapon attack roll against a creature, you can expend one superiority die to add it to the roll. You can use this maneuver before or after making the attack roll, but before any effects of the attack are applied."


class PushingAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(name="Pushing Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        dc = self.get_saving_throw_dc(character_stat_block)
        return (
            f"When you hit a creature with a weapon attack, you can expend one superiority die to attempt to drive the target back.\n"
            f"You add the superiority die to the attack's damage roll, and if the target is Large or smaller, it must make a Strength saving throw (DC {dc}).\n"
            "On a failed save, you push the target up to 15 feet away from you."
        )


class QuickToss(Maneuver):
    def __init__(self):
        super().__init__(name="Quick Toss")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Quick Toss: As a bonus action, you can expend one superiority die and make a ranged attack with a weapon that has the thrown property. You can draw the weapon as part of making this attack. If you hit, add the superiority die to the weapon's damage roll."


class Rally(Maneuver):
    def __init__(self):
        super().__init__(name="Rally")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Rally: On your turn, you can use a bonus action and expend one superiority die to bolster the resolve of one of your companions. When you do so, choose a friendly creature who can see or hear you. That creature gains temporary hit points equal to the superiority die roll + your Charisma modifier."


class Riposte(Maneuver):
    def __init__(self):
        super().__init__(name="Riposte")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return (
            "When a creature misses you with a melee attack,\n"
            "you can use your reaction and expend one superiority die to make a melee weapon attack against the creature.\n"
            "If you hit, you add the superiority die to the attack's damage roll."
        )


class SweepingAttack(Maneuver):
    def __init__(self):
        super().__init__(name="Sweeping Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Sweeping Attack: When you hit a creature with a melee weapon attack, you can expend one superiority die to attempt to damage another creature with the same attack. Choose another creature within 5 feet of the original target and within your reach. If the original attack roll would hit the second creature, it takes damage equal to the number you roll on your superiority die. The damage is of the same type dealt by the original attack."


class TacticalAssessment(Maneuver):
    def __init__(self):
        super().__init__(name="Tactical Assessment")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        return "Tactical Assessment: When you make an Intelligence (Investigation), an Intelligence (History), or a Wisdom (Insight) check, you can expend one superiority die and add the superiority die to the ability check."


class TripAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(name="Trip Attack")

    def get_description(self, character_stat_block: CharacterStatBlock) -> str:
        dc = self.get_saving_throw_dc(character_stat_block)
        return f"Trip Attack: When you hit a creature with a weapon attack, you can expend one superiority die to attempt to knock the target down. You add the superiority die to the attack's damage roll, and if the target is Large or smaller, it must make a Strength saving throw (DC {dc}). On a failed save, you knock the target prone"
