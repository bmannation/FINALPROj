from __future__ import annotations

import pygame
from engine import Scene, SceneManager, GameState


class PartyScene(Scene):
    """Party detail screen showing stats and equipment."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.game_state: GameState | None = None
        self.return_scene: str = "dungeon"
        self.font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None

    def on_enter(self, context: object) -> None:
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        if isinstance(context, dict) and "game_state" in context:
            self.game_state = context["game_state"]
            self.return_scene = context.get("return_scene", "dungeon")
        elif isinstance(context, GameState):
            self.game_state = context

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.game_state is not None:
            self.manager.switch_to(self.return_scene, {"game_state": self.game_state})

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        assert self.font is not None and self.small_font is not None and self.game_state is not None
        if self.manager.background is None:
            surface.fill((16, 14, 10))
        else:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((16, 14, 10, 200))
            surface.blit(overlay, (0, 0))
        title = self.font.render("Party", True, (240, 220, 180))
        surface.blit(title, (40, 24))
        instructions = self.small_font.render("ESC to return", True, (200, 200, 200))
        surface.blit(instructions, (40, 58))

        y = 110
        for member in self.game_state.party:
            name = self.small_font.render(f"{member.name} ({member.player_class})", True, (220, 220, 180))
            surface.blit(name, (40, y))
            y += 24
            stats = self.small_font.render(
                f"HP:{int(member.hp)}/{int(member.max_hp)} ATK:{member.attack} DEF:{member.defense} AGI:{member.agility} SAN:{member.sanity}",
                True,
                (200, 200, 200),
            )
            surface.blit(stats, (48, y))
            y += 24
            equipment_lines = [
                f"Weapon: {member.equipment['weapon'].name if member.equipment['weapon'] else '(none)'}",
                f"Armor: {member.equipment['armor'].name if member.equipment['armor'] else '(none)'}",
                f"Accessory: {member.equipment['accessory'].name if member.equipment['accessory'] else '(none)'}",
            ]
            for line in equipment_lines:
                equip_label = self.small_font.render(line, True, (185, 185, 175))
                surface.blit(equip_label, (56, y))
                y += 22
            attacks = ", ".join(attack.name for attack in member.attacks)
            attack_label = self.small_font.render(f"Attacks: {attacks}", True, (185, 185, 175))
            surface.blit(attack_label, (56, y))
            y += 30
