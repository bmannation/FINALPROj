from __future__ import annotations

import pygame
from engine import Scene, SceneManager, GameState
from entities.item import ConsumableItem, EquippableItem, KeyItem
from entities.party_member import PartyMember


class InventoryScene(Scene):
    """Inventory management scene for equipping and consuming items."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.game_state: GameState | None = None
        self.return_scene: str = "dungeon"
        self.selection_index: int = 0
        self.section: str = "inventory"
        self.font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    def on_enter(self, context: object) -> None:
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 20)
        if isinstance(context, dict) and "game_state" in context:
            self.game_state = context["game_state"]
            self.return_scene = context.get("return_scene", "dungeon")
        elif isinstance(context, GameState):
            self.game_state = context
        self.selection_index = 0

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.game_state is None:
            return
        if event.key == pygame.K_ESCAPE:
            self.manager.switch_to(self.return_scene, {"game_state": self.game_state})
            return
        inventory = self.game_state.inventory
        if event.key == pygame.K_DOWN:
            self.selection_index = min(len(inventory) - 1, self.selection_index + 1)
        elif event.key == pygame.K_UP:
            self.selection_index = max(0, self.selection_index - 1)
        elif event.key == pygame.K_e:
            self._equip_or_consume()
        elif event.key == pygame.K_u:
            self._unequip_first()

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        assert self.font is not None and self.small_font is not None and self.game_state is not None
        if self.manager.background is None:
            surface.fill((18, 16, 12))
        else:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((18, 16, 12, 200))
            surface.blit(overlay, (0, 0))
        title = self.font.render("Inventory", True, (240, 230, 200))
        surface.blit(title, (40, 24))
        instructions = self.small_font.render("UP/DOWN: select  E: equip/use  U: unequip  ESC: back", True, (200, 200, 200))
        surface.blit(instructions, (40, 58))

        y = 110
        inventory = self.game_state.inventory
        if not inventory:
            empty = self.small_font.render("No items carried.", True, (180, 180, 180))
            surface.blit(empty, (40, y))
        for idx, item in enumerate(inventory):
            color = (240, 240, 180) if idx == self.selection_index else (220, 220, 220)
            label = self.small_font.render(f"{idx + 1}. {item.name}", True, color)
            surface.blit(label, (40, y + idx * 24))

        x = 520
        y = 110
        for member in self.game_state.party:
            label = self.small_font.render(member.name, True, (220, 220, 180))
            surface.blit(label, (x, y))
            y += 22
            for slot, equipped in member.equipment.items():
                equip_text = equipped.name if equipped else "(empty)"
                slot_label = self.small_font.render(f"{slot.title()}: {equip_text}", True, (200, 200, 200))
                surface.blit(slot_label, (x + 8, y))
                y += 20
            y += 10

    def _equip_or_consume(self) -> None:
        if self.game_state is None or not self.game_state.inventory:
            return
        item = self.game_state.inventory[self.selection_index]
        member = self.game_state.party[0] if self.game_state.party else None
        if member is None:
            return
        if isinstance(item, EquippableItem):
            displaced = member.equip(item)
            self.game_state.inventory.pop(self.selection_index)
            if displaced is not None:
                self.game_state.inventory.append(displaced)
            self.selection_index = min(len(self.game_state.inventory) - 1, self.selection_index)
        elif isinstance(item, ConsumableItem):
            if item.affected == "playerhealth":
                member.hp = min(member.max_hp, member.hp + item.value)
            elif item.affected == "attack":
                member.apply_temp_buff("attack", item.value)
            elif item.affected == "defense":
                member.apply_temp_buff("defense", item.value)
            elif item.affected == "agility":
                member.apply_temp_buff("agility", item.value)
            elif item.affected == "sanity":
                member.sanity += item.value
                member.compute_class()
            self.game_state.inventory.pop(self.selection_index)
            self.selection_index = min(len(self.game_state.inventory) - 1, self.selection_index)
        elif isinstance(item, KeyItem):
            return

    def _unequip_first(self) -> None:
        if self.game_state is None:
            return
        member = self.game_state.party[0] if self.game_state.party else None
        if member is None:
            return
        for slot in ("weapon", "armor", "accessory"):
            dropped = member.unequip(slot)
            if dropped is not None:
                self.game_state.inventory.append(dropped)
                return
