from dataclasses import dataclass, field
from entities.attack import Attack
from entities.item import EquippableItem

PLAYER_CLASSES = ["Fiend", "Branded", "Human", "Enlightened", "Fanatical"]


@dataclass
class PartyMember:
    name: str
    hp: float
    max_hp: float
    sanity: int
    attack: int
    defense: int
    agility: int
    temp_attack: int = 0
    temp_defense: int = 0
    temp_agility: int = 0
    player_class: str = "Human"
    equipment: dict = field(default_factory=lambda: {"weapon": None, "armor": None, "accessory": None})
    defeated: bool = False
    attacks: list[Attack] = field(default_factory=list)

    def compute_class(self) -> str:
        s = self.sanity
        if s <= 50:
            self.player_class = "Fiend"
        elif s <= 74:
            self.player_class = "Branded"
        elif s <= 174:
            self.player_class = "Human"
        elif s <= 199:
            self.player_class = "Enlightened"
        else:
            self.player_class = "Fanatical"
        return self.player_class

    def equip(self, item: EquippableItem) -> EquippableItem | None:
        """Equip item; returns the displaced item (or None)."""
        slot = item.slot
        displaced = self.equipment[slot]
        if displaced is not None:
            self.unequip(slot)
        self.equipment[slot] = item
        self._apply_equip_delta(item, +1)
        return displaced

    def unequip(self, slot: str) -> EquippableItem | None:
        item = self.equipment.get(slot)
        if item is not None:
            self._apply_equip_delta(item, -1)
            self.equipment[slot] = None
        return item

    def _apply_equip_delta(self, item: EquippableItem, sign: int) -> None:
        if item.stat == "attack":
            self.attack += sign * item.value
        elif item.stat == "defense":
            self.defense += sign * item.value
        elif item.stat == "agility":
            self.agility += sign * item.value
        elif item.stat == "sanity":
            self.sanity += sign * item.value
            self.compute_class()
        elif item.stat == "playerhealth":
            self.max_hp += sign * item.value
            self.hp = min(self.hp, self.max_hp)

    def apply_temp_buff(self, stat: str, val: int) -> None:
        if stat == "attack":
            self.temp_attack += val
        elif stat == "defense":
            self.temp_defense += val
        elif stat == "agility":
            self.temp_agility += val

    def clear_temp_buffs(self) -> None:
        self.temp_attack = 0
        self.temp_defense = 0
        self.temp_agility = 0
