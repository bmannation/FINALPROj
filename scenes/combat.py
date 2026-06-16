from __future__ import annotations

import math
import random
import pygame
from enum import Enum, auto
from engine import Scene, SceneManager, GameState
from ui.typewriter import TypewriterRenderer
from ui.animator import CombatAnimator
from entities.party_member import PartyMember
from entities.attack import Attack
from entities.item import ConsumableItem
from data.dialogue import (
    SCARAB_DIALOGUE,
    KHONSHU_BOSS_INTRO,
    SAVING_ROLL_PROMPT,
    SAVING_ROLL_SUCCESS,
    SAVING_ROLL_FAILURE,
)
from data.items import SCARAB_AMULET, PERM_ITEMS
from data.enemies import make_khonshu


class CombatPhase(Enum):
    PLAYER_CHOOSE_ACTION = auto()
    PLAYER_CHOOSE_ATTACK = auto()
    ROLL_D20 = auto()
    CRITICAL_GUESS = auto()
    ANIMATE_ATTACK = auto()
    ENEMY_TURN = auto()
    ANIMATE_HIT = auto()
    CHECK_WIN_LOSS = auto()
    SAVING_ROLL = auto()
    NEGOTIATION = auto()
    COMBAT_END = auto()


class CombatScene(Scene):
    """Turn-based combat scene with action choices and animations."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self.font: pygame.font.Font | None = None
        self.small_font: pygame.font.Font | None = None
        self.game_state: GameState | None = None
        self.enemy = None
        self.return_scene: str = "dungeon"
        self.active_member_index: int = 0
        self.phase = CombatPhase.PLAYER_CHOOSE_ACTION
        self.animator = CombatAnimator()
        self.message_renderer: TypewriterRenderer | None = None
        self.pending_message: str | None = None
        self.pending_message_delay: float = 0.0
        self.message_hold_timer: float = 0.0
        self.message_waiting_for_confirm: bool = False
        self.current_attack: Attack | None = None
        self.d20_roll: int = 0
        self.roll_timer: float = 0.0
        self.blocking: bool = False
        self.last_turn_was_player: bool = True
        self.saving_roll_input: int = 10
        self.saving_roll_picks: int = 1
        self.negotiation_reward_item = None
        self.negotiation_recruit: PartyMember | None = None
        self.negstat: int = 0
        self.critical_guess_active: bool = False
        self.critical_guess_target: int | None = None
        self.critical_success: bool = False
        self.ending_target: str = "dungeon"
        self.ending_context: object | None = None
        self.next_scene: str | None = None
        self.enemy_rect = pygame.Rect(620, 220, 140, 180)
        self.member_rects: list[pygame.Rect] = []
        self.pending_khonshu: bool = False
        self.message_sequence: list[str] = []
        self._sticky_active_member: bool = False

    def on_enter(self, context: object) -> None:
        assert isinstance(context, dict), "CombatScene requires a context dict"
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.game_state = context["game_state"]
        self.enemy = context["enemy"]
        self.return_scene = context.get("return_scene", "dungeon")
        self.room_index = context.get("room_index")
        self.active_member_index = 0
        self.phase = CombatPhase.PLAYER_CHOOSE_ACTION
        self.animator = CombatAnimator()
        self.message_renderer = None
        self.pending_message = None
        self.pending_message_delay = 0.0
        self.message_hold_timer = 0.0
        self.message_waiting_for_confirm = False
        self.current_attack = None
        self.d20_roll = 0
        self.roll_timer = 0.0
        self.blocking = False
        self.last_turn_was_player = True
        self.saving_roll_input = 10
        self.saving_roll_picks: int = 1
        self.negotiation_reward_item = None
        self.negotiation_recruit = None
        self.negstat = 0
        self.critical_guess_active = False
        self.critical_guess_target = None
        self.critical_success = False
        self.ending_target = self.return_scene
        self.ending_context = None
        self.next_scene = None
        self.pending_khonshu = False
        self.message_sequence = []
        self.member_rects = [pygame.Rect(120, 220 + i * 120, 100, 130) for i in range(len(self.game_state.party))]
        self._sticky_active_member = False
        if self.game_state.party:
            self._update_current_member()
        self._ensure_current_member_is_alive()

    def on_exit(self) -> None:
        self.message_renderer = None

    def _ensure_member_rects(self) -> None:
        if self.game_state is None:
            return
        for i in range(len(self.member_rects), len(self.game_state.party)):
            self.member_rects.append(pygame.Rect(120, 220 + i * 120, 100, 130))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN or self.font is None or self.small_font is None or self.game_state is None:
            return

        if self.message_renderer is not None:
            if not self.message_renderer.complete:
                # allow the player to skip typing with Enter
                if event.key == pygame.K_RETURN:
                    self.message_renderer.skip()
                return
            self.message_renderer = None
            self.message_waiting_for_confirm = False
            if self.phase not in (
                CombatPhase.PLAYER_CHOOSE_ACTION,
                CombatPhase.PLAYER_CHOOSE_ATTACK,
                CombatPhase.SAVING_ROLL,
                CombatPhase.CRITICAL_GUESS,
                CombatPhase.NEGOTIATION,
                CombatPhase.COMBAT_END,
            ):
                return

        if self.phase == CombatPhase.PLAYER_CHOOSE_ACTION:
            if event.key in (pygame.K_a, pygame.K_1):
                self.phase = CombatPhase.PLAYER_CHOOSE_ATTACK
                self._queue_message("Choose an attack.", wait_for_confirm=False, delay=0.0)
            elif event.key in (pygame.K_b, pygame.K_2):
                self.blocking = True
                self.last_turn_was_player = True
                self._queue_message("You brace for the enemy's blow.", wait_for_confirm=False, delay=0.0)
                self.phase = CombatPhase.ENEMY_TURN
            elif event.key in (pygame.K_i, pygame.K_3):
                self._use_consumable()
            elif event.key in (pygame.K_n, pygame.K_4):
                self._negotiate()
            elif event.key in (pygame.K_s, pygame.K_5):
                self._switch_active_member()
        elif self.phase == CombatPhase.PLAYER_CHOOSE_ATTACK:
            index = self._key_to_attack_index(event.key)
            if index is not None and self.current_member(attacks=True):
                attacks = self.current_member().attacks
                if 0 <= index < len(attacks):
                    self.current_attack = attacks[index]
                    self.phase = CombatPhase.ROLL_D20
                    self.roll_timer = 0.0
                    self._queue_message("Rolling for accuracy...", wait_for_confirm=False, delay=0.0)
        elif self.phase == CombatPhase.SAVING_ROLL:
            new_value = self._key_to_wager(event.key)
            if new_value is not None:
                self.saving_roll_input = new_value
                self._queue_message(f"Wager {new_value} sanity for a chance to return.", wait_for_confirm=False, delay=0.0)
            elif event.key == pygame.K_RETURN:
                self._resolve_saving_roll()
        elif self.phase == CombatPhase.CRITICAL_GUESS:
            guess = self._key_to_critical_guess(event.key)
            if guess is not None:
                self.critical_guess_active = False
                self.critical_guess_target = guess
                self.critical_success = random.randint(1, 6) == guess
                self.phase = CombatPhase.ANIMATE_ATTACK
                self._trigger_player_attack_animation()
        elif self.phase == CombatPhase.NEGOTIATION:
            if event.key in (pygame.K_r, pygame.K_1):
                self._complete_negotiation_reward(recruit=True)
            elif event.key in (pygame.K_w, pygame.K_2):
                self._complete_negotiation_reward(recruit=False)
        elif self.phase == CombatPhase.COMBAT_END and self.ending_target is not None:
            # any key advances from combat end
            self.manager.switch_to(self.ending_target, self.ending_context)

    def update(self, dt: float) -> None:
        if self.pending_message is not None:
            self.pending_message_delay -= dt
            if self.pending_message_delay <= 0:
                self.message_renderer = TypewriterRenderer(
                    self.pending_message,
                    self.small_font,
                    (220, 220, 220),
                    pygame.Rect(120, 520, 640, 120),
                )
                self.pending_message = None
                self.pending_message_delay = 0.0

        if self.message_renderer is not None:
            self.message_renderer.update(dt)
            if self.message_renderer.complete:
                if self.message_waiting_for_confirm:
                    pass
                elif self.message_hold_timer <= 0.0:
                    self.message_hold_timer = 0.1
                else:
                    self.message_hold_timer -= dt
                    if self.message_hold_timer <= 0.0:
                        self.message_renderer = None

        if self.pending_message is not None or self.message_renderer is not None or self.message_waiting_for_confirm:
            return

        if self.phase == CombatPhase.ROLL_D20:
            self._resolve_roll()
        elif self.phase == CombatPhase.ANIMATE_ATTACK:
            self.animator.update(dt)
            if not self.animator.is_playing:
                self._resolve_player_attack()
        elif self.phase == CombatPhase.ANIMATE_HIT:
            self.animator.update(dt)
            if not self.animator.is_playing:
                self.phase = CombatPhase.CHECK_WIN_LOSS
        elif self.phase == CombatPhase.ENEMY_TURN:
            self._execute_enemy_turn()
        elif self.phase == CombatPhase.CHECK_WIN_LOSS:
            self._check_win_loss()
        elif self.phase == CombatPhase.COMBAT_END:
            if self.message_sequence:
                next_text = self.message_sequence.pop(0)
                self.message_renderer = TypewriterRenderer(next_text, self.small_font, (220, 220, 220), pygame.Rect(120, 520, 640, 120))
            elif self.next_scene is not None and self.ending_context is not None:
                self.manager.switch_to(self.next_scene, self.ending_context)

    def draw(self, surface: pygame.Surface) -> None:
        assert self.font is not None and self.small_font is not None
        if self.manager.background is None:
            surface.fill((15, 12, 10))
        else:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((15, 12, 10, 200))
            surface.blit(overlay, (0, 0))
        offset = self.animator.get_shake_offset()

        pygame.draw.rect(surface, (24, 22, 20), pygame.Rect(100 + offset[0], 200 + offset[1], 420, 360))
        self._ensure_member_rects()
        for idx, member in enumerate(self.game_state.party if self.game_state else []):
            rect = self.member_rects[idx].copy()
            rect.move_ip(offset)
            color = (120, 120, 180) if member.defeated else (140, 100, 70)
            pygame.draw.rect(surface, color, rect)
            if idx == self.active_member_index:
                pygame.draw.rect(surface, (240, 220, 140), rect, 3)
            label = self.small_font.render(member.name, True, (240, 240, 240))
            surface.blit(label, (rect.x + 4, rect.y + 4))
            hp_text = self.small_font.render(f"HP {int(member.hp)}/{int(member.max_hp)}", True, (220, 220, 220))
            surface.blit(hp_text, (rect.x + 4, rect.y + 28))

        pygame.draw.rect(surface, (90, 70, 40), self.enemy_rect.move(offset))
        name_label = self.font.render(self.enemy.name, True, (235, 210, 170))
        surface.blit(name_label, (self.enemy_rect.x + 4 + offset[0], self.enemy_rect.y + 4 + offset[1]))
        type_label = self.small_font.render(f"{self.enemy.enemy_type} ({self.enemy.modifier})", True, (210, 190, 170))
        surface.blit(type_label, (self.enemy_rect.x + 4 + offset[0], self.enemy_rect.y + 34 + offset[1]))
        shield_label = self.small_font.render(f"Shield: {int(self.enemy.shield_hp)}", True, (200, 180, 180))
        surface.blit(shield_label, (self.enemy_rect.x + 4 + offset[0], self.enemy_rect.y + 58 + offset[1]))
        hp_frac = self.enemy.hp / max(self.enemy.max_hp, 1)
        hp_bar = pygame.Rect(self.enemy_rect.x + 4 + offset[0], self.enemy_rect.y + 84 + offset[1], int(max(0.0, min(1.0, hp_frac)) * 132), 14)
        pygame.draw.rect(surface, (60, 40, 30), pygame.Rect(self.enemy_rect.x + 4 + offset[0], self.enemy_rect.y + 84 + offset[1], 132, 14))
        pygame.draw.rect(surface, (190, 70, 70), hp_bar)
        sanity_frac = self.enemy.sanity / max(self.enemy.max_sanity, 1)
        sanity_bar = pygame.Rect(self.enemy_rect.x + 4 + offset[0], self.enemy_rect.y + 104 + offset[1], int(max(0.0, min(1.0, sanity_frac)) * 90), 10)
        pygame.draw.rect(surface, (40, 30, 20), pygame.Rect(self.enemy_rect.x + 4 + offset[0], self.enemy_rect.y + 104 + offset[1], 90, 10))
        pygame.draw.rect(surface, (100, 170, 220), sanity_bar)
        sanity_label = self.small_font.render(f"Resolve: {int(self.enemy.sanity)}/{int(self.enemy.max_sanity)}", True, (180, 210, 240))
        surface.blit(sanity_label, (self.enemy_rect.x + 4 + offset[0], self.enemy_rect.y + 118 + offset[1]))

        if self.message_renderer is not None:
            self.message_renderer.draw(surface)
        elif not self.animator.is_playing:
            phase_text = self.font.render(f"Phase: {self.phase.name.replace('_', ' ')}", True, (220, 220, 220))
            surface.blit(phase_text, (120, 520))

        if self.phase == CombatPhase.PLAYER_CHOOSE_ACTION:
            actions = ["[A]ttack", "[B]lock", "[I]tem", "[N]egotiate", "[S]witch"]
            for index, label in enumerate(actions):
                action_surface = self.small_font.render(label, True, (220, 220, 220))
                surface.blit(action_surface, (120, 560 + index * 24))
        elif self.phase == CombatPhase.PLAYER_CHOOSE_ATTACK and self.current_member() is not None:
            for idx, attack in enumerate(self.current_member().attacks):
                attack_surface = self.small_font.render(f"{idx + 1}. {attack.name} ({attack.damage})", True, (220, 220, 220))
                surface.blit(attack_surface, (120, 560 + idx * 24))
        elif self.phase == CombatPhase.SAVING_ROLL:
            prompt = self.small_font.render(
                f"{SAVING_ROLL_PROMPT} Wager {self.saving_roll_input}. Press ENTER.", True, (220, 220, 220)
            )
            surface.blit(prompt, (120, 560))
        elif self.phase == CombatPhase.NEGOTIATION:
            option_text = f"[R]ecruit {self.enemy.name} or [W]eapon: {self.negotiation_reward_item.name if self.negotiation_reward_item else 'Unknown'}"
            option_surface = self.small_font.render(option_text, True, (220, 220, 220))
            surface.blit(option_surface, (120, 560))

    def _ensure_current_member_is_alive(self) -> None:
        if self.game_state is None:
            return
        alive = [i for i, member in enumerate(self.game_state.party) if not member.defeated and member.hp > 0]
        if alive:
            if self.active_member_index not in alive:
                self.active_member_index = alive[0]
        self._update_current_member()

    def _switch_active_member(self) -> None:
        if self.game_state is None:
            return
        alive = [i for i, member in enumerate(self.game_state.party) if not member.defeated and member.hp > 0]
        if len(alive) <= 1:
            self._queue_message("No other party member is available to switch.", wait_for_confirm=False, delay=0.0)
            return
        if self.active_member_index not in alive:
            self.active_member_index = alive[0]
        else:
            current = alive.index(self.active_member_index)
            self.active_member_index = alive[(current + 1) % len(alive)]
        member = self.current_member()
        if member is not None:
            self._queue_message(f"{member.name} takes the lead.", wait_for_confirm=False, delay=0.0)
        # keep this selection sticky so turn rotation doesn't immediately override it
        self._sticky_active_member = True
        self._update_current_member()
        self.phase = CombatPhase.PLAYER_CHOOSE_ACTION

    def _update_current_member(self) -> None:
        if self.game_state is None:
            return
        member = self.current_member()
        if member is not None:
            member.compute_class()

    def current_member(self, attacks: bool = False) -> PartyMember | None:
        if self.game_state is None or not self.game_state.party:
            return None
        if 0 <= self.active_member_index < len(self.game_state.party):
            return self.game_state.party[self.active_member_index]
        return None

    def _key_to_attack_index(self, key: int) -> int | None:
        if pygame.K_1 <= key <= pygame.K_9:
            return key - pygame.K_1
        return None

    def _key_to_wager(self, key: int) -> int | None:
        if pygame.K_1 <= key <= pygame.K_9:
            return (key - pygame.K_1 + 1) * 10
        return None

    def _key_to_critical_guess(self, key: int) -> int | None:
        if pygame.K_1 <= key <= pygame.K_6:
            return key - pygame.K_1 + 1
        return None

    def _queue_message(self, text: str, wait_for_confirm: bool = False, delay: float = 0.18) -> None:
        self.pending_message = text
        self.pending_message_delay = delay
        self.message_renderer = None
        self.message_waiting_for_confirm = wait_for_confirm
        self.message_hold_timer = 0.0

    def _resolve_roll(self) -> None:
        self.d20_roll = random.randint(1, 20)
        if self.d20_roll == 20:
            self.critical_guess_active = True
            self.phase = CombatPhase.CRITICAL_GUESS
            self._queue_message("Critical! Guess a D6 number (1-6).", wait_for_confirm=False, delay=0.0)
        else:
            self.phase = CombatPhase.ANIMATE_ATTACK
            self._trigger_player_attack_animation()

    def _start_negotiation_win(self) -> None:
        self.negotiation_reward_item = random.choice(PERM_ITEMS)
        self.negotiation_recruit = self._create_recruit_from_enemy()
        self._queue_message(
            f"{self.enemy.name} collapses in defeat. Choose recruit [R] or weapon [W].",
            wait_for_confirm=False,
            delay=0.0,
        )
        self.phase = CombatPhase.NEGOTIATION

    def _create_recruit_from_enemy(self) -> PartyMember:
        assert self.enemy is not None
        hp = max(1, self.enemy.max_hp * 0.75)
        attack_val = max(4, int(self.enemy.max_hp / 35))
        defense_val = max(3, int(self.enemy.shield_hp / 30))
        recruit = PartyMember(
            name=self.enemy.name,
            hp=hp,
            max_hp=self.enemy.max_hp,
            sanity=100,
            attack=attack_val,
            defense=defense_val,
            agility=4,
            attacks=[attack.clone() for attack in self.enemy.attack_pool],
        )
        recruit.compute_class()
        return recruit

    def _complete_negotiation_reward(self, recruit: bool) -> None:
        if self.game_state is None:
            return
        if recruit and self.negotiation_recruit is not None:
            self.game_state.party.append(self.negotiation_recruit)
            self._queue_message(f"{self.negotiation_recruit.name} joins your party!", wait_for_confirm=False, delay=0.0)
        elif not recruit and self.negotiation_reward_item is not None:
            self.game_state.inventory.append(self.negotiation_reward_item)
            self._queue_message(f"You receive {self.negotiation_reward_item.name}.", wait_for_confirm=False, delay=0.0)
        else:
            self._queue_message("Negotiation ends with no reward.", wait_for_confirm=False, delay=0.0)
        self.next_scene = self.return_scene
        self.ending_context = {"game_state": self.game_state, "victory": True, "cleared_room": getattr(self, "room_index", None)}
        self.phase = CombatPhase.COMBAT_END

    def _use_consumable(self) -> None:
        if self.game_state is None:
            return
        consumables = [item for item in self.game_state.inventory if isinstance(item, ConsumableItem)]
        if not consumables or self.current_member() is None:
            self._queue_message("No consumables available.", wait_for_confirm=False, delay=0.0)
            self.last_turn_was_player = True
            self.phase = CombatPhase.ENEMY_TURN
            return
        item = consumables[0]
        self.game_state.inventory.remove(item)
        member = self.current_member()
        assert member is not None
        if item.affected == "playerhealth":
            member.hp = min(member.max_hp, member.hp + item.value)
        elif item.affected == "attack":
            member.apply_temp_buff("attack", item.value)
        elif item.affected == "defense":
            member.apply_temp_buff("defense", item.value)
        elif item.affected == "agility":
            member.apply_temp_buff("agility", item.value)
        elif item.affected == "sanity":
            member.sanity += item.value
            member.compute_class()
        self._queue_message(f"{member.name} uses {item.name}.", wait_for_confirm=False, delay=0.0)
        self.last_turn_was_player = True
        self.phase = CombatPhase.ENEMY_TURN

    def _negotiate(self) -> None:
        member = self.current_member()
        if member is None or self.enemy is None:
            return
        chance = {
            "Fiend": 30,
            "Branded": 40,
            "Human": 60,
            "Enlightened": 70,
            "Fanatical": 80,
        }.get(member.player_class, 50)
        result = random.randint(1, 100) <= chance
        self.last_turn_was_player = True
        if result:
            resolve_damage = max(3, int(self.enemy.sanity * 0.2))
            self.enemy.sanity = max(0, self.enemy.sanity - resolve_damage)
            if self.enemy.sanity <= 0:
                self._start_negotiation_win()
                return
            self._queue_message(
                f"Your words pierce {self.enemy.name}. Resolve drops by {resolve_damage}.",
                wait_for_confirm=False,
                delay=0.0,
            )
            self.phase = CombatPhase.CHECK_WIN_LOSS
        else:
            self._queue_message("Negotiation fails. The enemy presses the attack.", wait_for_confirm=False, delay=0.0)
            self.phase = CombatPhase.CHECK_WIN_LOSS

    def _trigger_player_attack_animation(self) -> None:
        self.last_turn_was_player = True
        self.animator.trigger_attack_flash(self.enemy_rect)
        self._queue_message(f"{self.current_member().name} unleashes {self.current_attack.name}.", wait_for_confirm=False)

    def _resolve_player_attack(self) -> None:
        member = self.current_member()
        if member is None or self.current_attack is None:
            self.phase = CombatPhase.ENEMY_TURN
            return
        damage = round((self.current_attack.damage * self.d20_roll) / 1.5, 1) + member.attack + member.temp_attack
        if self.critical_success:
            damage = int(damage * 1.5)
            self.animator.trigger_critical_flash(self.enemy_rect)
        if self.enemy.shield_hp > 0:
            shield_damage = min(self.enemy.shield_hp, damage)
            self.enemy.shield_hp -= shield_damage
            damage -= shield_damage
        if damage <= 0 and self.current_attack is not None and self.current_attack.damage > 0:
            damage = 1
        self.enemy.hp = max(0, self.enemy.hp - damage)
        message_text = f"{member.name} deals {int(damage)} damage."
        if self.current_attack.special == "selfdamage":
            self_damage = max(1, int(damage // 2))
            member.hp = max(0, member.hp - self_damage)
            if member.hp <= 0:
                member.defeated = True
            message_text += f" {member.name} suffers {self_damage} recoil damage."
        self._queue_message(message_text, wait_for_confirm=False)
        self.animator.trigger_hit_shake(damage)
        self.animator.trigger_hit_flash(self.enemy_rect)
        self.phase = CombatPhase.ANIMATE_HIT

    def _execute_enemy_turn(self) -> None:
        self.blocking = False
        self.last_turn_was_player = False
        defender = self.current_member()
        attack = self.enemy.choose_attack(defender)
        # If this is the 'charging' placeholder, show the warning and keep charge_pending
        if attack.special == "chargeup" and attack.damage == 0:
            self._queue_message(f"{self.enemy.name} is charging a powerful strike.", wait_for_confirm=False)
            self.phase = CombatPhase.CHECK_WIN_LOSS
            return
        # If this was a real charged attack or any normal attack, clear the pending flag
        if getattr(self.enemy, "charge_pending", None) is not None:
            self.enemy.charge_pending = None
        defender = self.current_member()
        if defender is None:
            self.phase = CombatPhase.CHECK_WIN_LOSS
            return
        damage = attack.damage
        if self.enemy.modifier != "True Damage":
            damage = max(0, damage - (defender.defense + defender.temp_defense))
        if self.enemy.modifier == "True Damage":
            damage = attack.damage
        if attack.special == "suicide":
            self.enemy.hp = 0
        if attack.special == "selfdamage":
            self.enemy.hp = max(0, self.enemy.hp - max(1, attack.damage // 2))
        if self.enemy.name == "Anubis" and defender.sanity < 75:
            damage = int(damage * 1.5)
        if attack.name == "Desert Storm":
            total = 0
            for member in self.game_state.party:
                if not member.defeated and member.hp > 0:
                    hit = int(damage * (0.75 if self.blocking else 1.0))
                    if hit <= 0 and damage > 0:
                        hit = 1
                    member.hp = max(0, member.hp - hit)
                    if member.hp == 0:
                        member.defeated = True
                    total += hit
            self._queue_message(f"{self.enemy.name} unleashes Desert Storm for {total} total damage.", wait_for_confirm=False)
            self.animator.trigger_hit_shake(total)
            self.phase = CombatPhase.ANIMATE_HIT
            return
        if self.blocking:
            damage = int(damage * 0.5)
        if damage <= 0 and attack.damage > 0:
            damage = 1
        defender.hp = max(0, defender.hp - damage)
        if defender.hp == 0:
            defender.defeated = True
        self._queue_message(f"{self.enemy.name} hits {defender.name} for {damage} damage.", wait_for_confirm=False)
        self.animator.trigger_hit_shake(damage)
        self.animator.trigger_hit_flash(self.member_rects[self.active_member_index])
        self.phase = CombatPhase.ANIMATE_HIT

    def _check_win_loss(self) -> None:
        if self.enemy.hp <= 0:
            self.game_state.wins += 1
            if self.enemy.name == "Horus" and any(
                getattr(item, "name", None) == SCARAB_AMULET.name for item in self.game_state.inventory
            ):
                self.message_sequence = [SCARAB_DIALOGUE, KHONSHU_BOSS_INTRO]
                self.message_renderer = TypewriterRenderer(
                    self.message_sequence.pop(0), self.small_font, (220, 220, 220), pygame.Rect(120, 520, 640, 120)
                )
                self.next_scene = "combat"
                self.ending_context = {
                    "game_state": self.game_state,
                    "enemy": make_khonshu(self.game_state.freeplay_difficulty if self.return_scene == "freeplay" else 1.0),
                    "return_scene": self.return_scene,
                }
                self.phase = CombatPhase.COMBAT_END
                return
            if self.enemy.name == "Horus":
                self.next_scene = "ending"
                self.ending_context = {"game_state": self.game_state, "key": "dream"}
            elif self.enemy.name == "Khonshu":
                self.next_scene = "ending"
                self.ending_context = {"game_state": self.game_state, "key": "good"}
            else:
                self.next_scene = self.return_scene
                self.ending_context = {"game_state": self.game_state, "victory": True, "cleared_room": getattr(self, "room_index", None)}
            if self.return_scene == "freeplay":
                self.game_state.freeplay_streak += 1
                if self.game_state.freeplay_streak % 5 == 0:
                    self.game_state.freeplay_difficulty += 0.5
            self._queue_message("Enemy defeated.", wait_for_confirm=False)
            self.phase = CombatPhase.COMBAT_END
            return
        alive_members = [m for m in self.game_state.party if m.hp > 0]
        if not alive_members:
            if self.enemy.name == "Khonshu":
                self.next_scene = "ending"
                self.ending_context = {"game_state": self.game_state, "key": "khonshu"}
            else:
                self.next_scene = self.return_scene
                self.ending_context = {"game_state": self.game_state, "victory": False}
            self._queue_message("Your party has been defeated.", wait_for_confirm=False)
            self.phase = CombatPhase.COMBAT_END
            return
        current = self.current_member()
        if current is not None and current.hp <= 0:
            current.defeated = True
            self.saving_roll_picks = max(1, min(5, current.sanity // 10))
            self.phase = CombatPhase.SAVING_ROLL
            self._queue_message(SAVING_ROLL_PROMPT, wait_for_confirm=False, delay=0.0)
            return
        # if the enemy is still alive, determine whether it should act again or hand control back to the party
        if self.enemy.hp > 0:
            if self.last_turn_was_player:
                self.phase = CombatPhase.ENEMY_TURN
            else:
                if self._sticky_active_member:
                    # honor the player's manual selection once, then clear sticky
                    self._sticky_active_member = False
                    self._ensure_current_member_is_alive()
                else:
                    self.active_member_index = (self.active_member_index + 1) % len(self.game_state.party)
                    self._ensure_current_member_is_alive()
                self.phase = CombatPhase.PLAYER_CHOOSE_ACTION
                self.message_renderer = None
            return

        # otherwise advance to the next party member
        if self._sticky_active_member:
            self._sticky_active_member = False
            self._ensure_current_member_is_alive()
        else:
            self.active_member_index = (self.active_member_index + 1) % len(self.game_state.party)
            self._ensure_current_member_is_alive()
        self.phase = CombatPhase.PLAYER_CHOOSE_ACTION
        self.message_renderer = None

    def _resolve_saving_roll(self) -> None:
        current = self.current_member()
        if current is None:
            return
        picks = max(1, min(5, self.saving_roll_input // 10))
        roll = random.randint(1, 6)
        if roll <= picks:
            current.hp = min(150, current.max_hp)
            current.defeated = False
            self._queue_message(SAVING_ROLL_SUCCESS, wait_for_confirm=False, delay=0.0)
            self.phase = CombatPhase.CHECK_WIN_LOSS
        else:
            self._queue_message(SAVING_ROLL_FAILURE, wait_for_confirm=False, delay=0.0)
            current.defeated = True
            self.phase = CombatPhase.CHECK_WIN_LOSS

    def _complete_combat_end(self) -> None:
        if self.next_scene is not None and self.ending_context is not None:
            self.manager.switch_to(self.next_scene, self.ending_context)
