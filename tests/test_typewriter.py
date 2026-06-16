"""Unit tests for TypewriterRenderer._render_wrapped."""
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, call, patch

import pygame

# ---------------------------------------------------------------------------
# Minimal pygame initialisation so Font / Rect work without a display window
# ---------------------------------------------------------------------------
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame.init()

from ui.typewriter import TypewriterRenderer  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_renderer(
    text: str,
    rect_width: int = 200,
    char_width: int = 10,
    line_height: int = 20,
) -> tuple["TypewriterRenderer", MagicMock]:
    """
    Build a TypewriterRenderer whose font is a MagicMock.

    font.size(text) returns (len(text) * char_width, line_height).
    font.get_linesize() returns line_height.
    font.render(...) returns a dummy Surface-like mock.
    """
    font = MagicMock()
    font.size.side_effect = lambda t: (len(t) * char_width, line_height)
    font.get_linesize.return_value = line_height
    font.render.side_effect = lambda text, aa, color: MagicMock(name=f"surf<{text}>")

    rect = pygame.Rect(5, 10, rect_width, 300)
    renderer = TypewriterRenderer(
        text=text,
        font=font,
        color=(255, 255, 255),
        rect=rect,
    )
    return renderer, font


def _blit_positions(surface_mock) -> list[tuple[int, int]]:
    """Extract the (x, y) position args from every surface.blit() call."""
    return [c.args[1] for c in surface_mock.blit.call_args_list]


def _blit_surfs(font_mock, surface_mock) -> list[str]:
    """Return the text strings passed to font.render in call order.

    font.render is called once per line immediately before each blit, so the
    i-th render call corresponds to the i-th blit call.
    """
    return [c.args[0] for c in font_mock.render.call_args_list]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRenderWrapped(unittest.TestCase):

    def test_single_word_fits_on_one_line(self):
        """A short word that fits inside rect.width is rendered on a single line."""
        renderer, font = _make_renderer("Hello", rect_width=200, char_width=10)
        surface = MagicMock()

        renderer._render_wrapped(surface, "Hello")

        self.assertEqual(surface.blit.call_count, 1)
        pos = _blit_positions(surface)[0]
        # x should equal rect.x (5), y should equal rect.y (10)
        self.assertEqual(pos, (5, 10))

    def test_two_words_fit_on_one_line(self):
        """'Hi there' with char_width=10, rect_width=200 → single line (80 px < 200)."""
        renderer, font = _make_renderer("Hi there", rect_width=200, char_width=10)
        surface = MagicMock()

        renderer._render_wrapped(surface, "Hi there")

        self.assertEqual(surface.blit.call_count, 1)

    def test_long_text_wraps_onto_multiple_lines(self):
        """Words that overflow the width are pushed to subsequent lines."""
        # Each char = 10 px; rect_width = 50 → max ~5 chars per line.
        # "one two three four" → "one" (3), "two" (3), "three" (5), "four" (4)
        # "one two" = 7 chars = 70 px > 50 → wraps after "one"
        renderer, font = _make_renderer(
            "one two three four", rect_width=50, char_width=10
        )
        surface = MagicMock()

        renderer._render_wrapped(surface, "one two three four")

        texts = _blit_surfs(font, surface)
        self.assertEqual(texts, ["one", "two", "three", "four"])

    def test_line_y_positions_increment_by_line_height(self):
        """Each successive line is offset by font.get_linesize() on the y-axis."""
        renderer, font = _make_renderer(
            "one two three", rect_width=50, char_width=10, line_height=20
        )
        surface = MagicMock()

        renderer._render_wrapped(surface, "one two three")

        positions = _blit_positions(surface)
        rect_y = renderer.rect.y  # 10
        for i, (x, y) in enumerate(positions):
            self.assertEqual(y, rect_y + i * 20, f"Line {i} y mismatch")

    def test_all_lines_share_rect_x(self):
        """All lines blit at rect.x regardless of their content."""
        renderer, font = _make_renderer(
            "alpha beta gamma", rect_width=50, char_width=10
        )
        surface = MagicMock()

        renderer._render_wrapped(surface, "alpha beta gamma")

        positions = _blit_positions(surface)
        for x, _y in positions:
            self.assertEqual(x, renderer.rect.x)

    def test_empty_string_renders_nothing(self):
        """An empty string should produce no blit calls."""
        renderer, font = _make_renderer("", rect_width=200, char_width=10)
        surface = MagicMock()

        renderer._render_wrapped(surface, "")

        surface.blit.assert_not_called()

    def test_single_very_long_word_stays_on_one_line(self):
        """A word longer than rect.width still renders as one line (no sub-word break)."""
        # char_width=10, rect_width=30 → "verylongword" (12 chars = 120 px) exceeds width
        renderer, font = _make_renderer(
            "verylongword", rect_width=30, char_width=10
        )
        surface = MagicMock()

        renderer._render_wrapped(surface, "verylongword")

        # Should still render the word (can't break mid-word)
        self.assertEqual(surface.blit.call_count, 1)
        texts = _blit_surfs(font, surface)
        self.assertEqual(texts, ["verylongword"])

    def test_draw_passes_visible_slice_to_render_wrapped(self):
        """draw() slices text to chars_shown before calling _render_wrapped."""
        renderer, font = _make_renderer("Hello world", rect_width=200, char_width=10)
        surface = MagicMock()

        # Manually advance 5 chars
        renderer.chars_shown = 5
        with patch.object(renderer, "_render_wrapped") as mock_rw:
            renderer.draw(surface)
            mock_rw.assert_called_once_with(surface, "Hello")


if __name__ == "__main__":
    unittest.main()
