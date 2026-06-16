from __future__ import annotations

import random
import pygame
from dataclasses import dataclass
from engine import Scene, SceneManager, GameState
from data.dialogue import LORE_FRAGMENTS, ANUBIS_INTRO, SET_INTRO, HORUS_INTRO
from data.items import generate_consumable
from data.enemies import make_enemy, make_anubis, make_set, make_horus
from ui.hud import HUD
from ui.typewriter import TypewriterRenderer


ROOM_COLORS = {
    "combat": (164, 64, 64),
    "item": (78, 132, 78),
    "rest": (94, 94, 170),
    "lore": (170, 134, 74),
    "exit": (190, 140, 60),
}

ROOM_WEIGHTS = ["combat", "combat", "combat", "item", "rest", "lore"]


@dataclass
class Room:
    room_type: str
    cleared: bool
    pos: tuple[int, int]
    discovered: bool = False


class DungeonScene(Scene):
    """Dungeon traversal scene with map and room handling."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.game_state: GameState | None = None
        self.rooms: list[Room] = []
        self.selected_index: int = 0
        self.edges: list[tuple[int, int]] = []
        self.font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.hud: HUD | None = None
        self.message_renderer: TypewriterRenderer | None = None
        self.message_waiting_for_confirm: bool = False
        self.pending_boss: dict | None = None
        self.current_fragment: str | None = None
        self.camera_offset = pygame.math.Vector2(0, 0)
        self.target_camera_offset = pygame.math.Vector2(0, 0)

    def on_enter(self, context: object) -> None:
        if isinstance(context, dict) and "game_state" in context:
            self.game_state = context["game_state"]
            if context.get("cleared_room") is not None and self.rooms:
                index = context["cleared_room"]
                if 0 <= index < len(self.rooms):
                    self.rooms[index].cleared = True
        elif isinstance(context, GameState):
            self.game_state = context
        else:
            self.game_state = GameState()

        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 20)
        self.hud = HUD(self.font, self.small_font)
        self.camera_offset = pygame.math.Vector2(0, 0)
        self.target_camera_offset = pygame.math.Vector2(0, 0)
        self.selected_index = min(self.selected_index, len(self.rooms) - 1) if self.rooms else 0
        if not self.rooms or self.game_state.floor != getattr(self, "current_floor", None):
            self.current_floor = self.game_state.floor
            self.generate_floor()
        if self.rooms:
            self._discover_adjacent(self.selected_index)
            self._set_camera_target()
        else:
            self.edges = []

    def on_exit(self) -> None:
        self.message_renderer = None
        self.pending_boss = None
        self.current_fragment = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.game_state is None:
            return

        if self.message_renderer is not None:
            # allow skipping when the renderer is still typing
            if not self.message_renderer.complete:
                if event.key == pygame.K_RETURN:
                    self.message_renderer.skip()
                return
            # renderer is complete: require Enter to clear / progress
            if event.key == pygame.K_RETURN:
                # if a boss was queued, start the combat
                if self.pending_boss is not None:
                    boss = self.pending_boss.pop("boss")
                    self.message_renderer = None
                    self.message_waiting_for_confirm = False
                    self.manager.switch_to("combat", boss)
                    return
                # otherwise just clear the message
                self.message_renderer = None
                self.message_waiting_for_confirm = False
                return

        if event.key == pygame.K_LEFT:
            self._move_selection(pygame.Vector2(-1, 0))
        elif event.key == pygame.K_RIGHT:
            self._move_selection(pygame.Vector2(1, 0))
        elif event.key == pygame.K_UP:
            self._move_selection(pygame.Vector2(0, -1))
        elif event.key == pygame.K_DOWN:
            self._move_selection(pygame.Vector2(0, 1))
        elif event.key == pygame.K_RETURN:
            self.enter_room(self.selected_index)
        elif event.key == pygame.K_i:
            self.manager.switch_to("inventory", {"game_state": self.game_state, "return_scene": "dungeon"})
        elif event.key == pygame.K_p:
            self.manager.switch_to("party", {"game_state": self.game_state, "return_scene": "dungeon"})

    def update(self, dt: float) -> None:
        if self.message_renderer is not None and self.font is not None:
            self.message_renderer.update(dt)
            # when complete, require player confirmation to progress
            if self.message_renderer.complete:
                self.message_waiting_for_confirm = True
        self._update_camera(dt)

    def draw(self, surface: pygame.Surface) -> None:
        assert self.font is not None and self.small_font is not None and self.hud is not None
        if self.manager.background is None:
            surface.fill((20, 18, 14))
        else:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((20, 18, 14, 180))
            surface.blit(overlay, (0, 0))

        offset = self.camera_offset
        for idx, room in enumerate(self.rooms):
            visible = room.discovered or room.cleared
            color = ROOM_COLORS.get(room.room_type, (100, 100, 100)) if visible else (90, 90, 90)
            pos = pygame.Vector2(room.pos) + offset
            radius = 22
            pygame.draw.circle(surface, (60, 60, 60), pos, radius + 4)
            pygame.draw.circle(surface, color, pos, radius)
            if room.cleared:
                pygame.draw.circle(surface, (255, 255, 255), pos, radius - 8)
            if idx == self.selected_index:
                pygame.draw.circle(surface, (255, 255, 255), pos, radius + 8, 3)
            label_text = room.room_type.title() if visible else "Unknown"
            label = self.small_font.render(label_text, True, (240, 240, 240))
            surface.blit(label, (pos.x - label.get_width() / 2, pos.y + radius + 8))

        # draw edges (backbone + branches)
        for a, b in self.edges:
            if 0 <= a < len(self.rooms) and 0 <= b < len(self.rooms):
                start = pygame.Vector2(self.rooms[a].pos) + offset
                end = pygame.Vector2(self.rooms[b].pos) + offset
                pygame.draw.line(surface, (90, 90, 90), start, end, 4)

        if self.message_renderer is not None:
            panel = pygame.Surface((560, 140))
            panel.fill((18, 16, 14))
            pygame.draw.rect(panel, (140, 125, 90), panel.get_rect(), 2)
            surface.blit(panel, (120, 560))
            text_rect = pygame.Rect(130, 570, 540, 120)
            self.message_renderer.rect = text_rect
            self.message_renderer.draw(surface)
        else:
            status = self.font.render("Use arrow keys to move, ENTER to explore. I=Inventory P=Party", True, (200, 190, 170))
            surface.blit(status, (120, 520))
            current = self.rooms[self.selected_index]
            info = self.small_font.render(f"Selected: {current.room_type.title()} ({'Cleared' if current.cleared else 'Uncleared'})", True, (220, 220, 220))
            surface.blit(info, (120, 540))

        self.hud.draw(surface, self.game_state)

    def generate_floor(self) -> None:
        if self.game_state is None:
            return
        # scale room count with floor and allow branching
        self.rooms = []
        self.edges = []
        base = random.randint(4, 6)
        extra = max(0, (self.game_state.floor - 1) // 2)
        count = base + extra
        # ensure some variability and larger floors
        count += random.randint(0, min(3, self.game_state.floor // 3))

        # construct a backbone of rooms left-to-right
        backbone_types = ["combat"] + [random.choice(ROOM_WEIGHTS) for _ in range(count - 2)] + ["exit"]
        x = 160
        for idx, room_type in enumerate(backbone_types):
            y = 220 + random.randint(-60, 60)
            self.rooms.append(Room(room_type=room_type, cleared=False, pos=(x, y)))
            if idx > 0:
                # connect sequential backbone
                self.edges.append((idx - 1, idx))
            x += 140

        # add a few longer cardinal branches off the backbone
        branch_count = random.randint(0, max(1, self.game_state.floor // 5))
        for _ in range(branch_count):
            parent = random.randint(1, max(1, count - 2))
            branch_len = random.randint(2, 4 + (self.game_state.floor // 3))
            direction = random.choice(["up", "down"])
            bx = self.rooms[parent].pos[0]
            by = self.rooms[parent].pos[1] + (-120 if direction == "up" else 120)
            for i in range(branch_len):
                self.rooms.append(
                    Room(
                        room_type=random.choice(ROOM_WEIGHTS),
                        cleared=False,
                        pos=(bx, by),
                    )
                )
                new_idx = len(self.rooms) - 1
                self.edges.append((parent, new_idx))
                parent = new_idx
                by += -120 if direction == "up" else 120

        # choose a sensible selected index (first non-exit)
        self.selected_index = next((i for i, room in enumerate(self.rooms) if room.room_type != "exit"), 0)
        self.current_floor = self.game_state.floor
        self._discover_adjacent(self.selected_index)

    def room_difficulty(self) -> float:
        if self.game_state is None:
            return 1.0
        return 1 + ((self.game_state.floor - 1) // 2)

    def _discover_adjacent(self, index: int) -> None:
        if not self.rooms:
            return
        self.rooms[index].discovered = True
        for neighbor in self._get_neighbors(index):
            self.rooms[neighbor].discovered = True

    def _get_neighbors(self, index: int) -> list[int]:
        if not self.rooms:
            return []
        neighbors: list[int] = []
        for a, b in self.edges:
            if a == index:
                neighbors.append(b)
            elif b == index:
                neighbors.append(a)
        return neighbors

    def _move_selection(self, direction: pygame.Vector2) -> None:
        if not self.rooms:
            return
        current_pos = pygame.Vector2(self.rooms[self.selected_index].pos)
        best_index: int | None = None
        best_score = 0.0
        norm_direction = direction.normalize()
        for neighbor in self._get_neighbors(self.selected_index):
            room = self.rooms[neighbor]
            if not room.discovered:
                continue
            if not self._is_passable(neighbor):
                continue
            delta = pygame.Vector2(room.pos) - current_pos
            if delta.length_squared() == 0:
                continue
            score = norm_direction.dot(delta.normalize())
            if score > best_score and score > 0.5:
                best_score = score
                best_index = neighbor
        if best_index is not None:
            self.selected_index = best_index
            self._discover_adjacent(self.selected_index)
            self._set_camera_target()

    def _is_passable(self, target_index: int) -> bool:
        if self.selected_index == target_index:
            return True
        if not self.rooms or target_index < 0 or target_index >= len(self.rooms):
            return False
        visited = {self.selected_index}
        queue = [self.selected_index]
        while queue:
            current = queue.pop(0)
            for neighbor in self._get_neighbors(current):
                if neighbor in visited:
                    continue
                room = self.rooms[neighbor]
                if not room.discovered:
                    continue
                if room.room_type == "combat" and not room.cleared and neighbor != target_index:
                    continue
                visited.add(neighbor)
                if neighbor == target_index:
                    return True
                queue.append(neighbor)
        return False

    def _calculate_camera_target(self) -> pygame.math.Vector2:
        display = pygame.display.get_surface()
        if display is None or not self.rooms:
            return pygame.math.Vector2(0, 0)
        width, height = display.get_size()
        selected_pos = pygame.Vector2(self.rooms[self.selected_index].pos)
        # Keep the selected room centered in the visible dungeon area.
        target_screen = pygame.math.Vector2(width / 2, height / 2 - 40)
        return target_screen - selected_pos

    def _set_camera_target(self) -> None:
        self.target_camera_offset = self._calculate_camera_target()

    def _update_camera(self, dt: float) -> None:
        if not self.rooms:
            return
        self.target_camera_offset = self._calculate_camera_target()
        difference = self.target_camera_offset - self.camera_offset
        if difference.length_squared() > 0.0:
            self.camera_offset += difference * min(1.0, dt * 6.0)

    def enter_room(self, room_index: int) -> None:
        if self.game_state is None:
            return
        room = self.rooms[room_index]
        if room.cleared:
            self.message_renderer = TypewriterRenderer(
                "This room has already been explored.", self.small_font, (220, 220, 220), pygame.Rect(130, 570, 540, 120)
            )
            return

        if room.room_type == "combat":
            room.discovered = True
            enemy = make_enemy(self.room_difficulty())
            self.manager.switch_to(
                "combat",
                {
                    "game_state": self.game_state,
                    "enemy": enemy,
                    "return_scene": "dungeon",
                    "room_index": room_index,
                },
            )
            return

        if room.room_type == "item":
            item = generate_consumable(int(self.room_difficulty()))
            self.game_state.inventory.append(item)
            room.cleared = True
            room.discovered = True
            self.message_renderer = TypewriterRenderer(
                f"You discover {item.name}. It affects {item.affected.title()}.",
                self.small_font,
                (220, 220, 220),
                pygame.Rect(130, 570, 540, 120),
            )
            return

        if room.room_type == "rest":
            for member in self.game_state.party:
                if member.hp > 0:
                    heal = member.max_hp * 0.25
                    member.hp = min(member.max_hp, member.hp + heal)
            room.cleared = True
            room.discovered = True
            self.message_renderer = TypewriterRenderer(
                "A calm chamber restores your wounds. Your party recovers 25% of their maximum health.",
                self.small_font,
                (220, 220, 220),
                pygame.Rect(130, 570, 540, 120),
            )
            return

        if room.room_type == "lore":
            fragment = random.choice(LORE_FRAGMENTS)
            room.cleared = True
            room.discovered = True
            self.message_renderer = TypewriterRenderer(fragment, self.small_font, (220, 220, 220), pygame.Rect(130, 570, 540, 120))
            return

        if room.room_type == "exit":
            if any(r.room_type == "combat" and not r.cleared for r in self.rooms):
                room.discovered = True
                self.message_renderer = TypewriterRenderer(
                    "The exit remains locked until all combat rooms are cleared.",
                    self.small_font,
                    (220, 220, 220),
                    pygame.Rect(130, 570, 540, 120),
                )
                return
            room.discovered = True
            if self.game_state.floor == 4:
                self.pending_boss = {
                    "boss": {
                        "game_state": self.game_state,
                        "enemy": make_anubis(self.room_difficulty()),
                        "return_scene": "dungeon",
                    }
                }
                room.cleared = True
                self.message_renderer = TypewriterRenderer(ANUBIS_INTRO, self.small_font, (230, 230, 230), pygame.Rect(130, 570, 540, 120))
                return
            if self.game_state.floor == 6:
                self.pending_boss = {
                    "boss": {
                        "game_state": self.game_state,
                        "enemy": make_set(self.room_difficulty()),
                        "return_scene": "dungeon",
                    }
                }
                room.cleared = True
                self.message_renderer = TypewriterRenderer(SET_INTRO, self.small_font, (230, 230, 230), pygame.Rect(130, 570, 540, 120))
                return
            if self.game_state.floor == 7:
                self.pending_boss = {
                    "boss": {
                        "game_state": self.game_state,
                        "enemy": make_horus(self.room_difficulty()),
                        "return_scene": "dungeon",
                    }
                }
                room.cleared = True
                self.message_renderer = TypewriterRenderer(HORUS_INTRO, self.small_font, (230, 230, 230), pygame.Rect(130, 570, 540, 120))
                return
            self.game_state.floor += 1
            self.game_state.room = 0
            self.generate_floor()
            self.message_renderer = TypewriterRenderer(
                f"You advance to floor {self.game_state.floor}.",
                self.small_font,
                (220, 220, 220),
                pygame.Rect(130, 570, 540, 120),
            )
