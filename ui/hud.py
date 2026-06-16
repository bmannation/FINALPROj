import pygame

PANEL_WIDTH = 240
PANEL_HEIGHT = 568
PANEL_MARGIN = 16


class HUD:
    """Persistent heads-up display for dungeon and combat scenes."""

    def __init__(self, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
        self.font = font
        self.small_font = small_font

    def draw(self, surface: pygame.Surface, game_state: object) -> None:
        panel_rect = pygame.Rect(surface.get_width() - PANEL_WIDTH - PANEL_MARGIN, PANEL_MARGIN, PANEL_WIDTH, PANEL_HEIGHT)
        panel = pygame.Surface((panel_rect.width, panel_rect.height))
        panel.fill((34, 30, 22))
        pygame.draw.rect(panel, (110, 95, 70), panel.get_rect(), 3)

        header = self.small_font.render("Dungeon Ledger", True, (220, 200, 150))
        panel.blit(header, (12, 12))

        floor_text = self.font.render(f"Floor {game_state.floor}", True, (230, 220, 200))
        room_text = self.small_font.render(f"Room {game_state.room + 1}", True, (190, 180, 160))
        wins_text = self.small_font.render(f"Victories: {game_state.wins}", True, (190, 180, 160))
        panel.blit(floor_text, (12, 42))
        panel.blit(room_text, (12, 72))
        panel.blit(wins_text, (12, 98))

        for idx, member in enumerate(game_state.party):
            self._draw_member(panel, member, idx)

        surface.blit(panel, panel_rect.topleft)

    def _draw_member(self, surface: pygame.Surface, member: object, slot_index: int) -> None:
        top = 130 + slot_index * 108
        name_color = (170, 170, 170) if member.defeated else (235, 225, 190)
        class_color = (180, 160, 120)

        name_label = self.small_font.render(member.name, True, name_color)
        class_label = self.small_font.render(member.player_class, True, class_color)
        surface.blit(name_label, (12, top))
        surface.blit(class_label, (12, top + 18))

        hp_ratio = max(0.0, min(1.0, member.hp / member.max_hp if member.max_hp else 0.0))
        sanity_ratio = max(0.0, min(1.0, member.sanity / 200.0))

        hp_bar_bg = pygame.Rect(12, top + 44, 216, 12)
        hp_bar_fg = pygame.Rect(12, top + 44, int(hp_ratio * 216), 12)
        sanity_bar_fg = pygame.Rect(12, top + 62, int(sanity_ratio * 216), 8)

        pygame.draw.rect(surface, (50, 40, 30), hp_bar_bg)
        bar_color = (120, 210, 120) if hp_ratio > 0.4 else (210, 80, 80)
        pygame.draw.rect(surface, bar_color, hp_bar_fg)
        pygame.draw.rect(surface, (50, 40, 30), sanity_bar_fg)
        pygame.draw.rect(surface, (120, 160, 220), sanity_bar_fg)

        hp_text = self.small_font.render(f"HP {int(member.hp)}/{int(member.max_hp)}", True, (220, 220, 220))
        sanity_text = self.small_font.render(f"SAN {member.sanity}", True, (200, 200, 255))
        surface.blit(hp_text, (12, top + 80))
        surface.blit(sanity_text, (130, top + 80))

        buff_parts: list[str] = []
        if member.temp_attack > 0:
            buff_parts.append(f"ATK ↑{member.temp_attack}")
        if member.temp_defense > 0:
            buff_parts.append(f"DEF ↑{member.temp_defense}")
        if member.temp_agility > 0:
            buff_parts.append(f"AGI ↑{member.temp_agility}")
        if buff_parts:
            buff_text = self.small_font.render(" ".join(buff_parts), True, (130, 190, 250))
            surface.blit(buff_text, (12, top + 94))
