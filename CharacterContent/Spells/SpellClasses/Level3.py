"""Level 3 spells as classes (CharacterContent/Spells/SpellFactory/ClassSpell.py),
which SpellFactory uses instead of their JSON records. Written by
CharacterContent/Spells/SpellClassConverter.py; edit them by hand from
then on: each class is its spell's one source."""

from CharacterContent.Spells.SpellFactory.ClassSpell import ClassSpell, SpellRules
from Core.Definitions import Ability, DamageType
from Model.Content.CombatEffect import CombatDamage, CombatEffect
from Model.Content.Feature import FeatureTarget
from Model.Content.FeatureText import Block, Facts, Option, Table
from Model.View import CharacterView


class Fireball(ClassSpell):
    rules = SpellRules(
        name="Fireball",
        level=3,
        school="Evocation",
        classes=("Sorcerer", "Wizard"),
        casting_time="Action",
        range="150 feet",
        components="V, S, M (a ball of bat guano and sulfur)",
        duration="Instantaneous",
        source="Player's Handbook",
        description=(
            "A bright streak flashes from you to a point you choose within range and then blossoms with a low roar into a fiery explosion. Each creature in a 20-foot-radius Sphere centered on that point makes a Dexterity saving throw, taking 8d6 Fire damage on a failed save or half as much damage on a successful one.\n"
            "Flammable objects in the area that aren’t being worn or carried start burning.\n"
            "Using a Higher-Level Spell Slot. The damage increases by 1d6 for each spell slot level above 3."
        ),
        usage_tags=("damage",),
        target=FeatureTarget.AREA,
    )

    @property
    def improved_description(self) -> list[Block]:
        return [
            Facts(
                (
                    (
                        "Flavor",
                        "A bright streak flashes from you to a point you choose within range and then blossoms with a low roar into a fiery explosion.",
                    ),
                    (
                        "Area",
                        "20-foot-radius Sphere centered on a point you choose within range",
                    ),
                    ("Save", "Dexterity, made by each creature in the area"),
                )
            ),
            Table(
                ("Failed save", "Successful save"),
                (("8d6 Fire damage", "Half as much damage"),),
            ),
            Facts(
                (
                    (
                        "Objects",
                        "Flammable objects in the area that aren't being worn or carried start burning",
                    ),
                )
            ),
            Option(
                "Using a Higher-Level Spell Slot",
                (Facts((("Damage", "+1d6 for each spell slot level above 3"),)),),
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
                damage=(CombatDamage("8d6", DamageType.FIRE, upcast="1d6"),),
            )
        ]


SPELLS = [Fireball]
