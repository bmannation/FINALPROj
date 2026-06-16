from dataclasses import dataclass

VALID_SPECIALS = {None, "critical", "selfdamage", "suicide", "chargeup"}


@dataclass
class Attack:
    name: str
    damage: int
    special: str | None = None

    def __post_init__(self) -> None:
        assert self.special in VALID_SPECIALS, f"Unknown special: {self.special!r}"

    def clone(self) -> "Attack":
        return Attack(name=self.name, damage=self.damage, special=self.special)
