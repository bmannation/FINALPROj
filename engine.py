from __future__ import annotations
from dataclasses import dataclass, field
import os
import pygame


@dataclass
class GameState:
    """Shared game state threaded through every scene via on_enter."""
    party: list = field(default_factory=list)          # list[PartyMember]
    inventory: list = field(default_factory=list)      # list[Item]
    floor: int = 1
    room: int = 0
    wins: int = 0
    freeplay_unlocked: bool = False
    freeplay_difficulty: float = 1.0
    freeplay_streak: int = 0


class Scene:
    """Base class for all game scenes."""
    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager

    def on_enter(self, context: object) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass


class SceneManager:
    """Manages scene transitions and routing."""
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.scenes: dict[str, Scene] = {}
        self.active: Scene | None = None
        self.active_name: str | None = None
        self.background: pygame.Surface | None = None
        self._load_background()

    def _load_background(self) -> None:
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        background_path = os.path.join(assets_dir, "duatbackground.jpg")
        if os.path.exists(background_path):
            try:
                self.background = pygame.image.load(background_path).convert()
            except pygame.error:
                self.background = None
        else:
            self.background = None

    def register(self, name: str, scene: Scene) -> None:
        self.scenes[name] = scene

    def register_all(self) -> None:
        # Imported here to avoid circular imports at module level
        from scenes.title import TitleScene
        from scenes.dungeon import DungeonScene
        from scenes.combat import CombatScene
        from scenes.inventory import InventoryScene
        from scenes.party import PartyScene
        from scenes.ending import EndingScene
        from scenes.freeplay import FreeplayScene
        self.register("title", TitleScene(self))
        self.register("dungeon", DungeonScene(self))
        self.register("combat", CombatScene(self))
        self.register("inventory", InventoryScene(self))
        self.register("party", PartyScene(self))
        self.register("ending", EndingScene(self))
        self.register("freeplay", FreeplayScene(self))

    def switch_to(self, name: str, context: object) -> None:
        if name not in self.scenes:
            print(f"[SceneManager] ERROR: scene '{name}' not found; staying on '{self.active_name}'")
            return
        if self.active is not None:
            self.active.on_exit()
        self.active_name = name
        self.active = self.scenes[name]
        self.active.on_enter(context)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.active:
            self.active.handle_event(event)

    def update(self, dt: float) -> None:
        if self.active:
            self.active.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.background is not None:
            bg = pygame.transform.smoothscale(self.background, surface.get_size())
            surface.blit(bg, (0, 0))
        else:
            surface.fill((0, 0, 0))
        if self.active:
            self.active.draw(surface)
