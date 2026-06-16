import math
import random

import pygame
from dataclasses import dataclass, field


@dataclass
class Animation:
    kind: str           # "attack_flash" | "hit_shake" | "hit_flash" | "critical_flash"
    duration: float     # total seconds
    elapsed: float = 0.0
    rect: pygame.Rect | None = None
    magnitude: float = 0.0
    color: tuple[int, int, int] = (255, 0, 0)
    alpha: int = 128


class CombatAnimator:
    """Tracks active Animation objects and drives per-frame update/draw."""

    def __init__(self) -> None:
        self._animations: list[Animation] = []
        self._shake_offset: tuple[int, int] = (0, 0)

    @property
    def is_playing(self) -> bool:
        return len(self._animations) > 0

    def trigger_attack_flash(self, sprite_rect: pygame.Rect) -> None:
        """200 ms bright white overlay on the attacker."""
        self._animations.append(Animation(
            kind="attack_flash",
            duration=0.200,
            rect=sprite_rect.copy(),
            color=(255, 255, 200),
            alpha=180,
        ))

    def trigger_hit_shake(self, damage: float) -> None:
        """300 ms screen shake; offset = min(damage/10, 20) px."""
        magnitude = min(damage / 10.0, 20.0)
        self._animations.append(Animation(
            kind="hit_shake",
            duration=0.300,
            magnitude=magnitude,
        ))

    def trigger_hit_flash(self, sprite_rect: pygame.Rect) -> None:
        """150 ms red-tint overlay at 50% opacity on the target."""
        self._animations.append(Animation(
            kind="hit_flash",
            duration=0.150,
            rect=sprite_rect.copy(),
            color=(220, 50, 50),
            alpha=128,
        ))

    def trigger_critical_flash(self, sprite_rect: pygame.Rect) -> None:
        """225 ms enlarged (1.5×) gold flash on the target."""
        inflated = sprite_rect.inflate(
            int(sprite_rect.width * 0.5),
            int(sprite_rect.height * 0.5),
        )
        self._animations.append(Animation(
            kind="critical_flash",
            duration=0.225,
            rect=inflated,
            color=(255, 215, 0),
            alpha=200,
        ))

    def update(self, dt: float) -> None:
        self._shake_offset = (0, 0)
        still_active: list[Animation] = []
        for anim in self._animations:
            anim.elapsed += dt
            if anim.elapsed < anim.duration:
                still_active.append(anim)
                if anim.kind == "hit_shake":
                    phase = anim.elapsed / anim.duration
                    decay = 1.0 - phase
                    ox = int(math.sin(anim.elapsed * 60) * anim.magnitude * decay)
                    oy = int(random.uniform(-1, 1) * anim.magnitude * decay)
                    self._shake_offset = (ox, oy)
        self._animations = still_active

    def draw(self, surface: pygame.Surface) -> None:
        for anim in self._animations:
            if anim.rect is None:
                continue
            overlay = pygame.Surface((anim.rect.width, anim.rect.height), pygame.SRCALPHA)
            overlay.fill((*anim.color, anim.alpha))
            surface.blit(overlay, anim.rect.topleft)

    def get_shake_offset(self) -> tuple[int, int]:
        return self._shake_offset
