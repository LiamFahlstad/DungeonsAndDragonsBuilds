"""Level 4 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
which SpellFactory uses instead of their JSON records. Written by
CharacterContent/Spells/SpellClassConverter.py; edit them by hand from
then on: each class is its spell's one source."""

from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell, SpellRules
from CharacterContent.Spells.SpellFactory.Enums import Component, School
from Core.Definitions import Ability, CharacterClass, DamageType
from Model.Content.CombatEffect import CombatDamage, CombatEffect
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Paragraph, Table
from Model.View import CharacterView


class IceStorm(ClassSpell):
    rules = SpellRules(
        name="Ice Storm",
        level=4,
        school=School.EVOCATION,
        classes=(CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD),
        casting_time="Action",
        range="300 feet",
        components=(Component.VERBAL, Component.SOMATIC, Component.MATERIAL),
        material="a mitten",
        duration="Instantaneous",
        source="Player's Handbook",
        description=(
            "Hail falls in a 20-foot-radius, 40-foot-high Cylinder centered on a point within range. Each creature in the Cylinder makes a Dexterity saving throw. A creature takes 2d10 Bludgeoning damage and 4d6 Cold damage on a failed save or half as much damage on a successful one.\n"
            "Hailstones turn ground in the Cylinder into Difficult Terrain until the end of your next turn.\n"
            "Using a Higher-Level Spell Slot. The Bludgeoning damage increases by 1d10 for each spell slot level above 4."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )

    @property
    def improved_description(self) -> list[Block]:
        return [
            Paragraph("Hail falls in an area."),
            Facts(
                (
                    (
                        "Area",
                        "20-foot-radius, 40-foot-high Cylinder centered on a point within range",
                    ),
                    ("Save", "Dexterity, made by each creature in the Cylinder"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (
                    (
                        "2d10 Bludgeoning damage and 4d6 Cold damage",
                        "Half as much damage",
                    ),
                ),
            ),
            Facts(
                (
                    (
                        "Terrain",
                        "Hailstones turn ground in the Cylinder into Difficult Terrain until the end of your next turn",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (
                    Facts(
                        (
                            (
                                "Bludgeoning damage",
                                "+1d10 for each spell slot level above 4",
                            ),
                        )
                    ),
                ),
            ),
        ]

    def combat_effects(
        self, character: CharacterView | None = None
    ) -> list[CombatEffect]:
        return [
            CombatEffect(
                roll="save",
                save_ability=Ability.DEXTERITY,
                half_on_success=True,
                damage=(
                    CombatDamage("2d10", DamageType.BLUDGEONING, upcast="1d10"),
                    CombatDamage("4d6", DamageType.COLD),
                ),
                notes=(
                    "The ground in the Cylinder is Difficult Terrain until the end of your next turn.",
                ),
            )
        ]


SPELLS = [IceStorm]
