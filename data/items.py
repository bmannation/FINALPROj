"""Item definitions and consumable generation logic."""

import random

from entities.item import ConsumableItem, EquippableItem, KeyItem

# ---------------------------------------------------------------------------
# Key items
# ---------------------------------------------------------------------------

SCARAB_AMULET = KeyItem(name="Scarab Amulet")

# ---------------------------------------------------------------------------
# Equippable items
# ---------------------------------------------------------------------------

BRASS_KNUCKLES = EquippableItem(name="Brass Knuckles", stat="attack", value=4, slot="weapon")
ESSENCE_OF_VITALITY = EquippableItem(name="Essence of Vitality", stat="playerhealth", value=100, slot="accessory")
ANCIENT_TOME = EquippableItem(name="Ancient Tome of Power", stat="attack", value=2, slot="weapon")
MEDALLION_OF_RESILIENCE = EquippableItem(name="Medallion of Resilience", stat="defense", value=3, slot="armor")
ELIXIR_OF_REFLEXES = EquippableItem(name="Elixir of Reflexes", stat="agility", value=5, slot="accessory")
VOID_TOUCHED_CRYSTAL = EquippableItem(name="Void-Touched Crystal", stat="sanity", value=50, slot="accessory")
WARRIORS_HEARTSTONE = EquippableItem(name="Warrior's Heartstone", stat="attack", value=4, slot="weapon")

# ---------------------------------------------------------------------------
# Permanent items list (all equippables available as permanent rewards)
# ---------------------------------------------------------------------------

PERM_ITEMS = [
    BRASS_KNUCKLES,
    ESSENCE_OF_VITALITY,
    ANCIENT_TOME,
    MEDALLION_OF_RESILIENCE,
    ELIXIR_OF_REFLEXES,
    VOID_TOUCHED_CRYSTAL,
    WARRIORS_HEARTSTONE,
]

# ---------------------------------------------------------------------------
# Consumable generation
# ---------------------------------------------------------------------------

def generate_consumable(rarity: int) -> ConsumableItem:
    """Generate a random consumable item. rarity maps to difficulty level."""
    stats = ["attack", "defense", "agility", "sanity", "playerhealth"]
    stat = random.choice(stats)
    stat_display = {
        "attack": "Attack",
        "defense": "Defense",
        "agility": "Agility",
        "sanity": "Sanity",
        "playerhealth": "Health",
    }[stat]
    value = random.randint(3, 2 * rarity + 1)
    return ConsumableItem(
        name=f"Ankh of {stat_display}",
        value=value,
        affected=stat,
        is_temp=True,
    )
