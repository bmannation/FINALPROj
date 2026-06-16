from __future__ import annotations

import pygame
from engine import Scene, SceneManager, GameState
from entities.party_member import PartyMember
from data.attacks import PLAYER_STARTING_ATTACKS
from data.items import BRASS_KNUCKLES, SCARAB_AMULET
import graphic


class TitleScene(Scene):
    """Title screen scene implementing ASCII art and new-game entry."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.player_name: str = ""
        self.blink_timer: float = 0.0
        self.show_prompt: bool = True
        self.freeplay_unlocked: bool = False
        self.error_text: str = ""

    def on_enter(self, context: object) -> None:
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.player_name = ""
        self.blink_timer = 0.0
        self.show_prompt = True
        self.freeplay_unlocked = bool(context and getattr(context, "freeplay_unlocked", False))
        self.error_text = ""

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.font is None or self.small_font is None:
            return

        if event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
            return

        if event.key == pygame.K_RETURN:
            if 1 <= len(self.player_name) <= 20:
                party_member = PartyMember(
                    name=self.player_name,
                    hp=200.0,
                    max_hp=200.0,
                    sanity=100,
                    attack=5,
                    defense=5,
                    agility=5,
                    attacks=list(PLAYER_STARTING_ATTACKS),
                )
                party_member.compute_class()
                game_state = GameState(
                    party=[party_member],
                    inventory=[SCARAB_AMULET, BRASS_KNUCKLES],
                    floor=1,
                    room=0,
                    wins=0,
                    freeplay_unlocked=self.freeplay_unlocked,
                    freeplay_difficulty=1.0,
                    freeplay_streak=0,
                )
                self.manager.switch_to("dungeon", game_state)
            else:
                self.error_text = "Enter a name between 1 and 20 characters."
            return

        if event.key == pygame.K_f and self.freeplay_unlocked:
            self.manager.switch_to("freeplay", context if context is not None else GameState())
            return

        if event.unicode and len(self.player_name) < 20 and event.unicode.isprintable():
            self.player_name += event.unicode

    def update(self, dt: float) -> None:
        self.blink_timer += dt
        if self.blink_timer >= 0.5:
            self.blink_timer -= 0.5
            self.show_prompt = not self.show_prompt

    def draw(self, surface: pygame.Surface) -> None:
        assert self.font is not None and self.small_font is not None
        if self.manager.background is None:
            surface.fill((10, 8, 6))
        else:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((10, 8, 6, 180))
            surface.blit(overlay, (0, 0))

        title_lines = [line for line in graphic.title.strip("\n").splitlines() if line.strip()]
        line_height = self.small_font.get_linesize()
        y = 40
        for line in title_lines:
            surf = self.small_font.render(line, True, (212, 175, 55))
            surface.blit(surf, (32, y))
            y += line_height

        prompt_color = (220, 220, 220)
        if self.show_prompt:
            prompt = self.font.render("Press ENTER to start", True, prompt_color)
            surface.blit(prompt, (38, 620))

        if self.freeplay_unlocked:
            freeplay = self.small_font.render("Freeplay [F]", True, (180, 200, 240))
            surface.blit(freeplay, (38, 660))

        entry_label = self.font.render("Name:", True, (200, 180, 150))
        surface.blit(entry_label, (38, 560))

        input_box = pygame.Rect(120, 558, 420, 32)
        pygame.draw.rect(surface, (60, 50, 40), input_box)
        pygame.draw.rect(surface, (180, 160, 110), input_box, 2)
        name_text = self.font.render(self.player_name or "Enter your name...", True, (230, 230, 230))
        surface.blit(name_text, (input_box.x + 8, input_box.y + 2))

        if self.error_text:
            error_surf = self.small_font.render(self.error_text, True, (240, 120, 120))
            surface.blit(error_surf, (38, 700))
