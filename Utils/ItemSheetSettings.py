"""Campaign-wide toggles for the standalone item sheet engine
(RunItemSheets.py). Edit these to match how a specific campaign actually
runs, rather than hardcoding one campaign's assumptions into every
generator function. Only affects Builds/ItemSheets output - the real
character sheets (RunCharacterCreator.py) are unaffected."""

# Whether ranged weapon cards show the Ammunition property (chip +
# tracking description). Set False if your campaign doesn't track
# ammunition (arrows, bolts, bullets, needles) so the card doesn't imply
# otherwise.
TRACK_AMMUNITION = False
