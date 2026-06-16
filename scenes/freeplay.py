from __future__ import annotations

import pygame
from engine import Scene, SceneManager, GameState
from data.enemies import make_enemy, make_anubis, make_set, make_horus, make_khonshu
from data.attacks import HERETIC_ATTACKS, CREATURE_ATTACKS, REVENANT_ATTACKS, ARCHITECT_ATTACKS
from data.attacks import HORUS_ATTACKS, ANUBIS_ATTACKS, SET_ATTACKS, KHONSHU_ATTACKS
from data.items import SCARAB_AMULET


ENEMY_CHOICES = [
    ("Heretic", lambda diff: make_enemy(diff)),
    ("Creature", lambda diff: make_enemy(diff)),
    ("Revenant", lambda diff: make_enemy(diff)),
    ("Architect", lambda diff: make_enemy(diff)),
    ("Anubis", lambda diff: make_anubis(diff)),
    ("Set", lambda diff: make_set(diff)),
    ("Horus", lambda diff: make_horus(diff)),
    ("Khonshu", lambda diff: make_khonshu(diff)),
]


class FreeplayScene(Scene):
    """Endless freeplay combat sandbox with streak tracking."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.game_state: GameState | None = None
        self.selection: int = 0
        self.font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.message: str | None = None
        self.defeat_mode: bool = False

    def on_enter(self, context: object) -> None:
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        self.selection = 0
        self.message = None
        self.defeat_mode = False
        if isinstance(context, dict) and "game_state" in context:
            self.game_state = context["game_state"]
            if context.get("victory"):
                self.game_state.freeplay_streak += 1
                if self.game_state.freeplay_streak % 5 == 0:
                    self.game_state.freeplay_difficulty += 0.5
            if context.get("defeat"):
                self.defeat_mode = True
                self.message = "Defeat. Press R to resume or T to return to title."
        elif isinstance(context, GameState):
            self.game_state = context

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.game_state is None:
            return
        if self.defeat_mode:
            if event.key == pygame.K_r:
                self.defeat_mode = False
                self.message = None
                return
            if event.key == pygame.K_t:
                self.game_state.freeplay_streak = 0
                self.manager.switch_to("title", self.game_state)
                return
        if event.key == pygame.K_DOWN:
            self.selection = min(len(ENEMY_CHOICES) - 1, self.selection + 1)
        elif event.key == pygame.K_UP:
            self.selection = max(0, self.selection - 1)
        elif event.key == pygame.K_RETURN:
            name, factory = ENEMY_CHOICES[self.selection]
            enemy = factory(self.game_state.freeplay_difficulty)
            self.manager.switch_to(
                "combat",
                {
                    "game_state": self.game_state,
                    "enemy": enemy,
                    "return_scene": "freeplay",
                },
            )

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        assert self.font is not None and self.small_font is not None and self.game_state is not None
        if self.manager.background is None:
            surface.fill((12, 10, 8))
        else:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((12, 10, 8, 200))
            surface.blit(overlay, (0, 0))
        title = self.font.render("Freeplay Arena", True, (240, 220, 190))
        surface.blit(title, (40, 24))
        streak = self.small_font.render(f"Streak: {self.game_state.freeplay_streak}", True, (220, 220, 220))
        diff = self.small_font.render(f"Difficulty: {self.game_state.freeplay_difficulty:.1f}", True, (220, 220, 220))
        surface.blit(streak, (40, 62))
        surface.blit(diff, (220, 62))

        y = 120
        for idx, (name, _) in enumerate(ENEMY_CHOICES):
            color = (240, 220, 140) if idx == self.selection else (200, 200, 200)
            label = self.small_font.render(f"{idx + 1}. {name}", True, color)
            surface.blit(label, (40, y + idx * 28))

        if self.defeat_mode and self.message is not None:
            msg = self.small_font.render(self.message, True, (220, 140, 140))
            surface.blit(msg, (40, 420))
        else:
            hint = self.small_font.render("Use UP/DOWN to choose an enemy, ENTER to fight.", True, (180, 180, 180))
            surface.blit(hint, (40, 420))
