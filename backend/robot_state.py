from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RobotState:
    robot_id: str
    health: int
    max_health: int
    ammo: int
    position: tuple[float, float]
    current_action: Optional[str] = None
    is_alive: bool = True


class RobotStateStore:
    def __init__(self):
        self._states: dict[str, RobotState] = {}

    def register(self, robot_id: str, health: int, max_health: int, ammo: int, position: tuple[float, float]) -> None:
        self._states[robot_id] = RobotState(
            robot_id=robot_id,
            health=health,
            max_health=max_health,
            ammo=ammo,
            position=position,
        )

    def get(self, robot_id: str) -> RobotState:
        if robot_id not in self._states:
            raise KeyError(f"Robot not registered: {robot_id}")
        return self._states[robot_id]

    def update_health(self, robot_id: str, new_health: int) -> None:
        state = self.get(robot_id)
        state.health = max(0, min(state.max_health, new_health))
        state.is_alive = state.health > 0

    def update_position(self, robot_id: str, new_position: tuple[float, float]) -> None:
        self.get(robot_id).position = new_position

    def set_current_action(self, robot_id: str, action: str) -> None:
        self.get(robot_id).current_action = action

    def all_states(self) -> list[RobotState]:
        return list(self._states.values())
