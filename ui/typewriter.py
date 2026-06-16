import pygame


class TypewriterRenderer:
    """Non-blocking character-by-character text renderer."""

    def __init__(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple,
        rect: pygame.Rect,
        chars_per_second: float = 22.0,
    ) -> None:
        self.text = text
        self.font = font
        self.color = color
        self.rect = rect
        self.chars_per_second = chars_per_second
        self.elapsed: float = 0.0
        self.chars_shown: int = 0
        self.complete: bool = False

    def update(self, dt: float) -> None:
        if self.complete:
            return
        self.elapsed += dt
        self.chars_shown = min(int(self.elapsed * self.chars_per_second), len(self.text))
        if self.chars_shown >= len(self.text):
            self.complete = True

    def draw(self, surface: pygame.Surface) -> None:
        visible = self.text[: self.chars_shown]
        self._render_wrapped(surface, visible)

    def _render_wrapped(self, surface: pygame.Surface, text: str) -> None:
        words = text.split(" ")
        lines: list[str] = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if self.font.size(test)[0] <= self.rect.width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        line_height = self.font.get_linesize()
        for i, line in enumerate(lines):
            surf = self.font.render(line, True, self.color)
            surface.blit(surf, (self.rect.x, self.rect.y + i * line_height))

    def skip(self) -> None:
        self.chars_shown = len(self.text)
        self.elapsed = len(self.text) / self.chars_per_second
        self.complete = True

    def reset(self, new_text: str) -> None:
        self.text = new_text
        self.elapsed = 0.0
        self.chars_shown = 0
        self.complete = False
