# Rough numbers by CR

Calibrate against 1-2 sibling monsters of a similar role at the target CR first (grep `Combat/Monsters/CR_<tier>/monsters.py`); they are already tuned to this campaign's power curve. Use this table only when no sibling is close enough, and in all cases `monster_score.py` (the `balance-monster` skill) has the final word.

Rough DMG guideline if no sibling monster is close enough (treat as a loose sanity check, not gospel):

| CR | Prof | AC | HP | Attack bonus | Dmg/round | Save DC |
|---|---|---|---|---|---|---|
| 0–2 | +2 | 13 | 1–100 | +3 | 0–20 | 13 |
| 3–4 | +2 | 14 | 101–130 | +4/+5 | 21–32 | 13–14 |
| 5–7 | +3 | 15 | 131–175 | +6 | 33–50 | 15 |
| 8–10 | +3/+4 | 16–17 | 176–220 | +7 | 51–68 | 16 |
| 11–13 | +4/+5 | 17–18 | 221–265 | +8 | 69–86 | 17–18 |
| 14–16 | +5 | 18 | 266–310 | +8/+9 | 87–104 | 18 |
| 17–20 | +6 | 19 | 311–400 | +10 | 105–140 | 19 |
| 21+ | +7+ | 19 | 400+ | +11+ | 141+ | 20+ |
