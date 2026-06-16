"""Attack definitions for all enemy types, bosses, and player starting attacks."""

from entities.attack import Attack

# ---------------------------------------------------------------------------
# Heretic attacks
# ---------------------------------------------------------------------------
Stab = Attack(name="Stab", damage=3, special=None)
Slash = Attack(name="Slash", damage=4, special=None)
DaggerThrow = Attack(name="Dagger Throw", damage=3, special=None)
BloodSpit = Attack(name="Blood Spit", damage=2, special=None)
Sacrifice = Attack(name="Sacrifice", damage=5, special="selfdamage")

HERETIC_ATTACKS = [Stab, Slash, DaggerThrow, BloodSpit, Sacrifice]

# ---------------------------------------------------------------------------
# Creature attacks
# ---------------------------------------------------------------------------
Shudder = Attack(name="Shudder", damage=2, special=None)
Bite = Attack(name="Bite", damage=4, special=None)
Scream = Attack(name="Scream", damage=3, special=None)
Claw = Attack(name="Claw", damage=4, special=None)
Shatter = Attack(name="Shatter", damage=6, special="critical")

CREATURE_ATTACKS = [Shudder, Bite, Scream, Claw, Shatter]

# ---------------------------------------------------------------------------
# Revenant attacks
# ---------------------------------------------------------------------------
SoulDrain = Attack(name="Soul Drain", damage=3, special=None)
WraithStrike = Attack(name="Wraith Strike", damage=5, special="selfdamage")
HauntingGaze = Attack(name="Haunting Gaze", damage=2, special=None)
DeathCoil = Attack(name="Death Coil", damage=7, special="chargeup")
Consume = Attack(name="Consume", damage=4, special="suicide")

REVENANT_ATTACKS = [SoulDrain, WraithStrike, HauntingGaze, DeathCoil, Consume]

# ---------------------------------------------------------------------------
# Architect attacks
# ---------------------------------------------------------------------------
StoneFist = Attack(name="Stone Fist", damage=4, special=None)
RuneBlast = Attack(name="Rune Blast", damage=5, special=None)
Fortify = Attack(name="Fortify", damage=0, special=None)  # raises own shield in CombatScene
GravityCrush = Attack(name="Gravity Crush", damage=6, special="chargeup")
Collapse = Attack(name="Collapse", damage=8, special="suicide")

ARCHITECT_ATTACKS = [StoneFist, RuneBlast, Fortify, GravityCrush, Collapse]

# ---------------------------------------------------------------------------
# Boss attacks — Horus
# ---------------------------------------------------------------------------
GaleWing = Attack(name="Gale Wing", damage=3, special=None)
TalonSweep = Attack(name="Talon Sweep", damage=4, special=None)
SolarFlare = Attack(name="Solar Flare", damage=5, special=None)
Vengeance = Attack(name="Vengeance", damage=6, special="selfdamage")
Judgement = Attack(name="Judgement", damage=7, special="selfdamage")

HORUS_ATTACKS = [GaleWing, TalonSweep, SolarFlare, Vengeance, Judgement]

# ---------------------------------------------------------------------------
# Boss attacks — Anubis
# ---------------------------------------------------------------------------
WeighingOfHearts = Attack(name="Weighing of Hearts", damage=5, special=None)
ScalesOfMaat = Attack(name="Scales of Ma'at", damage=8, special="chargeup")
DeathSentence = Attack(name="Death Sentence", damage=6, special=None)

ANUBIS_ATTACKS = [WeighingOfHearts, ScalesOfMaat, DeathSentence]

# ---------------------------------------------------------------------------
# Boss attacks — Set
# ---------------------------------------------------------------------------
SandWhip = Attack(name="Sand Whip", damage=4, special=None)
DesertStorm = Attack(name="Desert Storm", damage=10, special="chargeup")
ChaosBlade = Attack(name="Chaos Blade", damage=6, special=None)
ShatterStorm = Attack(name="Shatter Storm", damage=5, special="critical")

SET_ATTACKS = [SandWhip, DesertStorm, ChaosBlade, ShatterStorm]

# ---------------------------------------------------------------------------
# Boss attacks — Khonshu
# ---------------------------------------------------------------------------
Moonbeam = Attack(name="Moonbeam", damage=5, special=None)
LunarWrath = Attack(name="Lunar Wrath", damage=7, special="critical")
TimeFracture = Attack(name="Time Fracture", damage=9, special="chargeup")
Nightmare = Attack(name="Nightmare", damage=6, special="selfdamage")

KHONSHU_ATTACKS = [Moonbeam, LunarWrath, TimeFracture, Nightmare]

# ---------------------------------------------------------------------------
# Player starting attacks
# ---------------------------------------------------------------------------
Punch = Attack(name="Punch", damage=3, special=None)
Tackle = Attack(name="Tackle", damage=2, special=None)

PLAYER_STARTING_ATTACKS = [Punch, Tackle]
