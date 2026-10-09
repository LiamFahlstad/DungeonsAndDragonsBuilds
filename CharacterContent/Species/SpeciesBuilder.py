from abc import abstractmethod

from Core.Definitions import Ability
from Model.CharacterSources import CharacterSources
from Model.Grants import Grants
from Model.Records.GrantStamp import GrantKind


class SpeciesGrants(Grants):
    """The scope a species grants through. Species spells aren't granted at a
    class level: they're stamped level 1, like every other grant outside the
    per-level class flow, and listed under the species - so a spell the class
    also grants (Rock Gnome Prestidigitation on a Wizard) appears for both.

    It also carries the two facts some species traits depend on:
    `character_level` (Aasimar's Celestial Revelation at level 3, Elf and
    Tiefling spells at levels 3 and 5) and `spell_casting_ability`, for the
    species spells whose ability the build doesn't choose itself (the best of
    Intelligence, Wisdom and Charisma)."""

    def __init__(
        self,
        sources: CharacterSources,
        species_name: str,
        spell_casting_ability: Ability,
    ):
        super().__init__(sources, 1, species_name, GrantKind.SPECIES)
        # Species are granted after every class, so this is the final level.
        self.character_level = sources.character_level
        self.spell_casting_ability = spell_casting_ability


class SpeciesBuilder:
    def __init__(
        self,
        name: str,
    ):
        self.name = name

    def build(
        self, sources: CharacterSources, spell_casting_ability: Ability
    ) -> CharacterSources:
        """Grant this species' traits (speed, size, features, spells) straight
        into `sources` and return them."""
        self._grant(SpeciesGrants(sources, self.name, spell_casting_ability))
        return sources

    @abstractmethod
    def _grant(self, data: SpeciesGrants) -> None:
        pass
