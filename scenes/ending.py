from __future__ import annotations

import pygame
from engine import Scene, SceneManager, GameState
from ui.typewriter import TypewriterRenderer
from data.dialogue import GOOD_ENDING, DREAM_ENDING, KHONSHU_ENDING


class EndingScene(Scene):
    """Ending scene showing narrative conclusion and freeplay unlock."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.typewriter: TypewriterRenderer | None = None
        self.game_state: GameState | None = None
        self.key: str = "good"

    def on_enter(self, context: object) -> None:
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        if isinstance(context, dict):
            self.game_state = context.get("game_state")
            self.key = context.get("key", "good")
        elif isinstance(context, GameState):
            self.game_state = context
        if self.game_state is not None:
            self.game_state.freeplay_unlocked = True
        ending_text = {
            "good": GOOD_ENDING,
            "dream": DREAM_ENDING,
            "khonshu": KHONSHU_ENDING,
        }.get(self.key, GOOD_ENDING)
        self.typewriter = TypewriterRenderer(
            ending_text,
            self.small_font,
            (220, 220, 220),
            pygame.Rect(40, 120, 940, 540),
            chars_per_second=35.0,
        )

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.typewriter is None or self.game_state is None:
            return
        if event.key == pygame.K_RETURN and self.typewriter.complete:
            self.manager.switch_to("title", self.game_state)
        elif event.key == pygame.K_RETURN:
            self.typewriter.skip()

    def update(self, dt: float) -> None:
        if self.typewriter is not None:
            self.typewriter.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        assert self.font is not None and self.small_font is not None and self.typewriter is not None
        if self.manager.background is None:
            surface.fill((5, 4, 3))
        else:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((5, 4, 3, 220))
            surface.blit(overlay, (0, 0))
        title = self.font.render("The End", True, (220, 220, 200))
        surface.blit(title, (40, 24))
        self.typewriter.draw(surface)
        if self.typewriter.complete:
            prompt = self.small_font.render("Press ENTER to return to title", True, (200, 200, 200))
            surface.blit(prompt, (40, 680))
