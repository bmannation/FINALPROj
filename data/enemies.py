"""Enemy type definitions, boss factories, and enemy generation logic."""

import random
from entities.enemy import Enemy
from data.attacks import (
    HERETIC_ATTACKS, CREATURE_ATTACKS, REVENANT_ATTACKS, ARCHITECT_ATTACKS,
    HORUS_ATTACKS, ANUBIS_ATTACKS, SET_ATTACKS, KHONSHU_ATTACKS,
)

# ---------------------------------------------------------------------------
# Attack pools (by enemy type string key)
# ---------------------------------------------------------------------------
ATTACK_POOLS = {
    "Heretic":   HERETIC_ATTACKS,
    "Creature":  CREATURE_ATTACKS,
    "Revenant":  REVENANT_ATTACKS,
    "Architect": ARCHITECT_ATTACKS,
}

# ---------------------------------------------------------------------------
# Random enemy name list (from original main.py)
# ---------------------------------------------------------------------------
ENEMY_NAMES = ["Bryton", "Owen", "Ridwan", "Khafra", "Nebka", "Thutmose", "Senusret", "Amet"]

# ---------------------------------------------------------------------------
# Enemy types and modifiers
# ---------------------------------------------------------------------------
ENEMY_TYPES = ["Heretic", "Creature", "Revenant", "Architect"]
MODIFIERS = ["Shielded", "True Damage", "Thief", "Fanatic"]

# ---------------------------------------------------------------------------
# Random enemy factory
# ---------------------------------------------------------------------------
def make_enemy(difficulty: float) -> Enemy:
    """Generate a random enemy scaled to difficulty."""
    enemy_type = random.choice(ENEMY_TYPES)
    modifier = random.choice(MODIFIERS)
    name = random.choice(ENEMY_NAMES)
    hp = random.randint(55, 85) * (1 + 0.5 * difficulty)
    sanity = 40 * (1 + difficulty)
    shield_hp = 0.0
    if modifier == "Shielded":
        shield_hp = 80 * difficulty
    return Enemy(
        name=name,
        enemy_type=enemy_type,
        modifier=modifier,
        hp=hp,
        max_hp=hp,
        sanity=sanity,
        max_sanity=sanity,
        shield_hp=shield_hp,
        attack_pool=list(ATTACK_POOLS[enemy_type]),
        is_boss=False,
    )

# ---------------------------------------------------------------------------
# Boss factories
# ---------------------------------------------------------------------------
def make_anubis(difficulty: float) -> Enemy:
    hp = random.randint(100, 130) * (1 + 0.5 * difficulty)
    sanity = 80 * (1 + difficulty)
    return Enemy(
        name="Anubis",
        enemy_type="Heretic",
        modifier="True Damage",
        hp=hp,
        max_hp=hp,
        sanity=sanity,
        max_sanity=sanity,
        shield_hp=0.0,
        attack_pool=list(ANUBIS_ATTACKS),
        is_boss=True,
    )

def make_set(difficulty: float) -> Enemy:
    hp = random.randint(110, 140) * (1 + 0.5 * difficulty)
    shield_hp = 80 * difficulty
    sanity = 90 * (1 + difficulty)
    return Enemy(
        name="Set",
        enemy_type="Architect",
        modifier="Shielded",
        hp=hp,
        max_hp=hp,
        sanity=sanity,
        max_sanity=sanity,
        shield_hp=shield_hp,
        attack_pool=list(SET_ATTACKS),
        is_boss=True,
    )

def make_horus(difficulty: float) -> Enemy:
    hp = random.randint(120, 150) * (1 + 0.5 * difficulty)
    sanity = 90 * (1 + difficulty)
    return Enemy(
        name="Horus",
        enemy_type="Creature",
        modifier="Fanatic",
        hp=hp,
        max_hp=hp,
        sanity=sanity,
        max_sanity=sanity,
        shield_hp=0.0,
        attack_pool=list(HORUS_ATTACKS),
        is_boss=True,
    )

def make_khonshu(difficulty: float) -> Enemy:
    hp = random.randint(130, 160) * (1 + 0.5 * difficulty)
    sanity = 100 * (1 + difficulty)
    return Enemy(
        name="Khonshu",
        enemy_type="Heretic",
        modifier="True Damage",
        hp=hp,
        max_hp=hp,
        sanity=sanity,
        max_sanity=sanity,
        shield_hp=0.0,
        attack_pool=list(KHONSHU_ATTACKS),
        is_boss=True,
    )
