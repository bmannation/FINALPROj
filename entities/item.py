from dataclasses import dataclass


class Item:
    """Base class for all items."""
    pass


@dataclass
class ConsumableItem(Item):
    name: str
    value: int
    affected: str   # stat name: "attack","defense","agility","sanity","playerhealth"
    is_temp: bool   # True = buff lasts until end of combat; False = permanent


@dataclass
class EquippableItem(Item):
    name: str
    stat: str       # "attack"|"defense"|"agility"|"sanity"|"playerhealth"
    value: int
    slot: str       # "weapon"|"armor"|"accessory"


@dataclass
class KeyItem(Item):
    name: str
    # Not usable, not discardable; only triggers effect in specific contexts
