from Model.Content.Feature import Feature, FeatureActivation, ActionType, FeatureTarget
from Core.Definitions import CharacterClass
from Model.View import CharacterView


class Maneuver(Feature):
    def __init__(
        self,
        name: str,
        activation: "FeatureActivation | None" = None,
        usage_tags: list | None = None,
    ):
        super().__init__(
            name=name,
            origin="Maneuver",
            activation=activation,
            usage_tags=usage_tags,
        )


class ManeuverWithSavingThrow(Maneuver):
    def get_saving_throw_dc(self, character: CharacterView) -> int:
        proficiency_bonus = character.get_proficiency_bonus()
        str_mod = character.get_strength_modifier()
        dex_mod = character.get_dexterity_modifier()
        return 8 + proficiency_bonus + max(str_mod, dex_mod)

    def calculate_dc(self, character: CharacterView) -> int:
        return self.get_saving_throw_dc(character)


class Ambush(Maneuver):
    def __init__(self):
        super().__init__(name="Ambush:", usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return "When you make a Dexterity (Stealth) check or an Initiative roll, you can expend one Superiority Die and add the die to the roll, unless you have the Incapacitated condition."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class BaitAndSwitch(Maneuver):
    def __init__(self):
        super().__init__(
            name="Bait and Switch",
            activation=FeatureActivation(duration="Until Start of Next Turn"),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "When you're within 5 feet of a creature on your turn, you can expend one Superiority Die and switch places with that creature, provided you spend at least 5 feet of movement and the creature is willing and doesn't have the Incapacitated condition. This movement doesn't provoke Opportunity Attacks.\nRoll the Superiority Die. Until the start of your next turn, you or the other creature (your choice) gains a bonus to AC equal to the number rolled."

    def get_concise_description(self, character: CharacterView) -> str:
        return "When you're within 5 feet of a willing creature on your turn, expend one Superiority Die to switch places (costs 5 feet of movement; no Opportunity Attacks). Until the start of your next turn, you or the creature gains a bonus to AC equal to the die roll."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class Brace(Maneuver):
    def __init__(self):
        super().__init__(
            name="Brace",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "Brace: When a creature you can see moves into the reach you have with the melee weapon you're wielding, you can use your reaction to expend one superiority die and make one attack against the creature, using that weapon. If the attack hits, add the superiority die to the weapon's damage roll."

    def get_concise_description(self, character: CharacterView) -> str:
        return "As a reaction when a creature moves into your reach with a melee weapon, expend one superiority die to make one attack. Add the die to the damage roll if you hit."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class CommandersStrike(Maneuver):
    def __init__(self):
        super().__init__(
            name="Commander's Strike",
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "When you take the Attack action on your turn, you can replace one of your attacks to direct one of your companions to strike. When you do so, choose a willing creature who can see or hear you and expend one Superiority Die. That creature can immediately use its Reaction to make one attack with a weapon or an Unarmed Strike, adding the Superiority Die to the attack's damage roll on a hit."

    def get_concise_description(self, character: CharacterView) -> str:
        return "When you take the Attack action, replace one attack and expend one Superiority Die to direct a willing creature who can see or hear you. It can immediately use its Reaction to make a weapon or Unarmed Strike attack, adding the die to the damage on a hit."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class CommandingPresence(Maneuver):
    def __init__(self):
        super().__init__(name="Commanding Presence", usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return "When you make a Charisma (Intimidation, Performance, or Persuasion) check, you can expend one Superiority Die and add that die to the roll."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class DisarmingAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(name="Disarming Attack", usage_tags=["damage", "control"])

    def get_description(self, character: CharacterView) -> str:
        return f"When you hit a creature with an attack roll, you can expend one Superiority Die to attempt to disarm the target. Add the Superiority Die roll to the attack's damage roll. The target must succeed on a Strength saving throw (DC {self.get_saving_throw_dc(character)}) or drop one object of your choice that it's holding, with the object landing in its space."

    def get_concise_description(self, character: CharacterView) -> str:
        return f"When you hit with an attack roll, expend one Superiority Die to add it to damage. The target must succeed on a Strength saving throw (DC {self.get_saving_throw_dc(character)}) or drop one object of your choice that it's holding."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class DistractingStrike(Maneuver):
    def __init__(self):
        super().__init__(
            name="Distracting Strike",
            activation=FeatureActivation(duration="Until Start of Next Turn"),
            usage_tags=["damage", "buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "When you hit a creature with an attack roll, you can expend one Superiority Die to distract the target. Add the Superiority Die roll to the attack's damage roll. The next attack roll against the target by an attacker other than you has Advantage if the attack is made before the start of your next turn."

    def get_concise_description(self, character: CharacterView) -> str:
        return "When you hit with an attack roll, expend one Superiority Die to add it to damage. The next attack roll against the target by another attacker has Advantage if made before the start of your next turn."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class EvasiveFootwork(Maneuver):
    def __init__(self):
        super().__init__(
            name="Evasive Footwork",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "As a Bonus Action, you can expend one Superiority Die and take the Disengage action. You also roll the die and add the number rolled to your AC until the start of your next turn."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class FeintingAttack(Maneuver):
    def __init__(self):
        super().__init__(
            name="Feinting Attack",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["buff", "damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "As a Bonus Action, you can expend one Superiority Die to feint, choosing one creature within 5 feet of yourself as your target. You have Advantage on your next attack roll against that target this turn. If that attack hits, add the Superiority Die to the attack's damage roll."

    def get_concise_description(self, character: CharacterView) -> str:
        return "As a Bonus Action, expend one Superiority Die to feint against a creature within 5 feet. You have Advantage on your next attack roll against it this turn; if that attack hits, add the die to the damage."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class GoadingAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(
            name="Goading Attack",
            activation=FeatureActivation(duration="Until End of Next Turn"),
            usage_tags=["damage", "control"],
        )

    def get_description(self, character: CharacterView) -> str:
        return f"When you hit a creature with an attack roll, you can expend one Superiority Die to attempt to goad the target into attacking you. Add the Superiority Die to the attack's damage roll. The target must succeed on a Wisdom saving throw (DC {self.get_saving_throw_dc(character)}) or have Disadvantage on attack rolls against targets other than you until the end of your next turn."

    def get_concise_description(self, character: CharacterView) -> str:
        return f"When you hit with an attack roll, expend one Superiority Die to add it to damage. The target must succeed on a Wisdom saving throw (DC {self.get_saving_throw_dc(character)}) or have Disadvantage on attack rolls against targets other than you until the end of your next turn."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class GrapplingStrike(Maneuver):
    def __init__(self):
        super().__init__(
            name="Grappling Strike",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["control"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "Grappling Strike: Immediately after you hit a creature with a melee attack on your turn, you can expend one superiority die and then try to grapple the target as a bonus action (see the Player's Handbook for rules on grappling). Add the superiority die to your Strength (Athletics) check."

    def get_concise_description(self, character: CharacterView) -> str:
        return "Immediately after you hit with a melee attack, expend one superiority die and try to grapple the target as a bonus action. Add the die to your Strength (Athletics) check."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class LungingAttack(Maneuver):
    def __init__(self):
        super().__init__(
            name="Lunging Attack",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "As a Bonus Action, you can expend one Superiority Die and take the Dash action. If you move at least 5 feet in a straight line immediately before hitting with a melee attack as part of the Attack action on this turn, you can add the Superiority Die to the attack's damage roll."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class ManeuveringAttack(Maneuver):
    def __init__(self):
        super().__init__(name="Maneuvering Attack", usage_tags=["damage", "buff"])

    def get_description(self, character: CharacterView) -> str:
        return "When you hit a creature with an attack roll, you can expend one Superiority Die to maneuver one of your comrades into another position. Add the Superiority Die roll to the attack's damage roll, and choose a willing creature who can see or hear you. That creature can use its Reaction to move up to half its Speed without provoking Opportunity Attacks from the target of your attack."

    def get_concise_description(self, character: CharacterView) -> str:
        return "When you hit with an attack roll, expend one Superiority Die to add it to damage. A willing creature who can see or hear you can use its Reaction to move up to half its Speed without provoking Opportunity Attacks from your target."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class MenacingAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(
            name="Menacing Attack",
            activation=FeatureActivation(duration="Until End of Next Turn"),
            usage_tags=["damage", "control"],
        )

    def get_description(self, character: CharacterView) -> str:
        return f"When you hit a creature with an attack roll, you can expend one Superiority Die to attempt to frighten the target. Add the Superiority Die to the attack's damage roll. The target must succeed on a Wisdom saving throw (DC {self.get_saving_throw_dc(character)}) or have the Frightened condition until the end of your next turn."

    def get_concise_description(self, character: CharacterView) -> str:
        return f"When you hit with an attack roll, expend one Superiority Die to add it to damage. The target must succeed on a Wisdom saving throw (DC {self.get_saving_throw_dc(character)}) or have the Frightened condition until the end of your next turn."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Parry(Maneuver):
    def __init__(self):
        super().__init__(
            name="Parry",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["buff"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "When another creature damages you with a melee attack roll, you can take a Reaction and expend one Superiority Die to reduce the damage by the number you roll on your Superiority Die plus your Strength or Dexterity modifier (your choice)."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class PrecisionAttack(Maneuver):
    def __init__(self):
        super().__init__(name="Precision Attack", usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return "When you miss with an attack roll, you can expend one Superiority Die, roll that die, and add it to the attack roll, potentially causing the attack to hit."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class PushingAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(name="Pushing Attack", usage_tags=["damage", "control"])

    def get_description(self, character: CharacterView) -> str:
        return f"When you hit a creature with an attack roll using a weapon or an Unarmed Strike, you can expend one Superiority Die to attempt to drive the target back. Add the Superiority Die to the attack's damage roll. If the target is Large or smaller, it must succeed on a Strength saving throw (DC {self.get_saving_throw_dc(character)}) or be pushed up to 15 feet directly away from you."

    def get_concise_description(self, character: CharacterView) -> str:
        return f"When you hit with a weapon or Unarmed Strike, expend one Superiority Die to add it to damage. If the target is Large or smaller, it must succeed on a Strength saving throw (DC {self.get_saving_throw_dc(character)}) or be pushed up to 15 feet directly away from you."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class QuickToss(Maneuver):
    def __init__(self):
        super().__init__(
            name="Quick Toss",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "Quick Toss: As a bonus action, you can expend one superiority die and make a ranged attack with a weapon that has the thrown property. You can draw the weapon as part of making this attack. If you hit, add the superiority die to the weapon's damage roll."

    def get_concise_description(self, character: CharacterView) -> str:
        return "As a bonus action, expend one superiority die to make a ranged attack with a thrown weapon (can draw as part of the attack). If you hit, add the die to the damage roll."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class Rally(Maneuver):
    def __init__(self):
        super().__init__(
            name="Rally",
            activation=FeatureActivation(action_type=ActionType.BONUS_ACTION),
            usage_tags=["heal"],
        )

    def get_description(self, character: CharacterView) -> str:
        return f"As a Bonus Action, you can expend one Superiority Die to bolster the resolve of a companion. Choose an ally of yours within 30 feet of yourself who can see or hear you. That creature gains Temporary Hit Points equal to the Superiority Die roll plus half your Fighter level (round down, currently {character.get_class_level(CharacterClass.FIGHTER) // 2})."

    def get_concise_description(self, character: CharacterView) -> str:
        return f"As a Bonus Action, expend one Superiority Die to give an ally within 30 feet who can see or hear you Temporary Hit Points equal to the die roll plus half your Fighter level (round down, currently {character.get_class_level(CharacterClass.FIGHTER) // 2})."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ALLY


class Riposte(Maneuver):
    def __init__(self):
        super().__init__(
            name="Riposte",
            activation=FeatureActivation(action_type=ActionType.REACTION),
            usage_tags=["damage"],
        )

    def get_description(self, character: CharacterView) -> str:
        return "When a creature misses you with a melee attack roll, you can take a Reaction and expend one Superiority Die to make a melee attack roll with a weapon or an Unarmed Strike against the creature. If you hit, add the Superiority Die to the attack's damage."

    def get_concise_description(self, character: CharacterView) -> str:
        return "When a creature misses you with a melee attack roll, use your Reaction and expend one Superiority Die to make a melee weapon or Unarmed Strike attack against it. If you hit, add the die to the damage."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class SweepingAttack(Maneuver):
    def __init__(self):
        super().__init__(name="Sweeping Attack", usage_tags=["damage"])

    def get_description(self, character: CharacterView) -> str:
        return "When you hit a creature with a melee attack roll using a weapon or an Unarmed Strike, you can expend one Superiority Die to attempt to damage another creature. Choose another creature within 5 feet of the original target and within your reach. If the original attack roll would hit the second creature, it takes damage equal to the number you roll on your Superiority Die. The damage is of the same type dealt by the original attack."

    def get_concise_description(self, character: CharacterView) -> str:
        return "When you hit with a melee weapon or Unarmed Strike attack, expend one Superiority Die to damage another creature within 5 feet of the target and within your reach. If the original attack roll would hit it, it takes damage equal to the die roll, of the same type as the original attack."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY


class TacticalAssessment(Maneuver):
    def __init__(self):
        super().__init__(name="Tactical Assessment", usage_tags=["buff"])

    def get_description(self, character: CharacterView) -> str:
        return "When you make an Intelligence (History or Investigation) check or a Wisdom (Insight) check, you can expend one Superiority Die and add that die to the ability check."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.SELF


class TripAttack(ManeuverWithSavingThrow):
    def __init__(self):
        super().__init__(name="Trip Attack", usage_tags=["damage", "control"])

    def get_description(self, character: CharacterView) -> str:
        return f"When you hit a creature with an attack roll using a weapon or an Unarmed Strike, you can expend one Superiority Die and add the die to the attack's damage roll. If the target is Large or smaller, it must succeed on a Strength saving throw (DC {self.get_saving_throw_dc(character)}) or have the Prone condition."

    def get_concise_description(self, character: CharacterView) -> str:
        return f"When you hit with a weapon or Unarmed Strike, expend one Superiority Die to add it to damage. If the target is Large or smaller, it must succeed on a Strength saving throw (DC {self.get_saving_throw_dc(character)}) or have the Prone condition."

    def target(self, character: CharacterView) -> "FeatureTarget | None":
        return FeatureTarget.ENEMY
