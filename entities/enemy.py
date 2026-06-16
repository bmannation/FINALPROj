from dataclasses import dataclass, field
import random
from typing import Any
from entities.attack import Attack


@dataclass
class Enemy:
    name: str
    enemy_type: str          # "Heretic" | "Creature" | "Revenant" | "Architect"
    modifier: str            # "Shielded" | "True Damage" | "Thief" | "Fanatic"
    hp: float
    max_hp: float
    sanity: float
    max_sanity: float
    shield_hp: float
    attack_pool: list[Attack]
    is_boss: bool = False
    charge_pending: Attack | None = None  # Set when a chargeup attack was chosen last turn

    def choose_attack(self, defender: Any | None = None) -> Attack:
        """
        Returns the attack to execute this turn.
        If charge_pending is set, returns it (CombatScene must clear this after resolving).
        Otherwise picks randomly from attack_pool; if chargeup is chosen, sets charge_pending
        and returns a sentinel 'charging' attack so CombatScene can show the warning.
        """
        if self.charge_pending is not None:
            return self.charge_pending  # CombatScene clears this after resolving
        # If a defender is provided and is low on HP, prefer an attack that will finish them
        try:
            target_hp = getattr(defender, "hp", None)
            target_max = getattr(defender, "max_hp", 0)
        except Exception:
            target_hp = None
            target_max = 0
        if target_hp is not None:
            low_threshold = max(1, int(target_max * 0.25))
            if target_hp <= low_threshold:
                # search for an attack that would be lethal against the defender
                for atk in self.attack_pool:
                    # don't consider attacks that would damage or kill the user
                    if atk.special in ("suicide", "selfdamage"):
                        continue
                    dmg = atk.damage
                    if self.modifier != "True Damage":
                        defender_def = getattr(defender, "defense", 0) + getattr(defender, "temp_defense", 0)
                        effective = max(0, dmg - defender_def)
                    else:
                        effective = dmg
                    if effective >= target_hp:
                        if atk.special == "chargeup":
                            self.charge_pending = atk
                            return Attack(name=f"{atk.name} (charging…)", damage=0, special="chargeup")
                        return atk
        chosen = random.choice(self.attack_pool)
        if chosen.special == "chargeup":
            self.charge_pending = chosen
            # Return a zero-damage "charging" placeholder so CombatScene shows the warning
            return Attack(name=f"{chosen.name} (charging…)", damage=0, special="chargeup")
        return chosen
