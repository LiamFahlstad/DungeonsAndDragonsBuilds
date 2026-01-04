import Definitions
from StatBlocks import BasicEntity


class Darkvision(BasicEntity.Trait):
    def __init__(self, distance: int = 60):
        self.distance = distance
        super().__init__(name="Darkvision")

    def get_description(self) -> str:
        return f"Darkvision {self.distance} ft."


class Flyby(BasicEntity.Trait):
    def __init__(self):
        super().__init__(name="Flyby")

    def get_description(self) -> str:
        return f"The beast doesn't provoke Opportunity Attacks when it flies out of an enemy's reach."


class PrimalBond(BasicEntity.Trait):
    def __init__(self):
        super().__init__(name="Primal Bond")

    def get_description(self) -> str:
        return f"Add your Proficiency Bonus to any ability check or saving throw the beast makes."


class BeastsStrike(BasicEntity.Action):
    def __init__(self, wisdom_modifier: int, spell_attack_modifier: int):
        self.wisdom_modifier = wisdom_modifier
        self.spell_attack_modifier = spell_attack_modifier
        super().__init__(name="Beast's Strike")

    def get_description(self) -> str:
        return f"Melee Attack Roll: Bonus equals your spell attack modifier ({self.spell_attack_modifier:+}), reach 5 ft. Hit: 1d4 + 3 plus your Wisdom modifier ({self.wisdom_modifier:+}) Slashing damage."


class BeastMasterBeastOfTheSky(BasicEntity.BasicEntity):
    def __init__(
        self,
        wisdom_modifier: int,
        ranger_level: int,
        proficiency_bonus: int,
        spell_attack_modifier: int,
    ):
        hit_points = 4 + (4 * ranger_level)
        armor_class = 13 + wisdom_modifier
        super().__init__(
            name="Beast of the Sky",
            hit_points=hit_points,
            armor_class=armor_class,
            speed=10,
            size=Definitions.CreatureSize.SMALL,
            ability_scores={
                Definitions.Ability.STRENGTH: 6,
                Definitions.Ability.DEXTERITY: 16,
                Definitions.Ability.CONSTITUTION: 13,
                Definitions.Ability.INTELLIGENCE: 8,
                Definitions.Ability.WISDOM: 14,
                Definitions.Ability.CHARISMA: 11,
            },
            proficiency_bonus=proficiency_bonus,
            fly_speed=60,
            traits=[
                Darkvision(distance=60),
                Flyby(),
                PrimalBond(),
            ],
            actions=[
                BeastsStrike(
                    wisdom_modifier=wisdom_modifier,
                    spell_attack_modifier=spell_attack_modifier,
                ),
            ],
        )
