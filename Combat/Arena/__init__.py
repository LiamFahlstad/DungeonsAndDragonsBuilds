"""The battle map, without Qt, so the combat window and the tests share it
(Notes/combat-arena-plan.md).

- geometry: cells, the grid's shape and the distance rules (RULES).
- arena: the map's settings, where each combatant is, distances between
  creatures, where one can move to, and where new tokens go.
- areas: areas of effect, what cells each covers aimed at a cell.
- lasting: areas that stay on the map, held by an active spell.
- cover: the cover a target has from the map, and where areas stop.
"""
