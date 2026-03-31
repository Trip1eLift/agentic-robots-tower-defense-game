from __future__ import annotations
from enum import Enum
from typing import Any, Literal, Optional, Union
from pydantic import BaseModel, Field


class EventType(str, Enum):
    ENEMY_SPOTTED = "ENEMY_SPOTTED"
    ENEMY_IN_RANGE = "ENEMY_IN_RANGE"
    TAKING_DAMAGE = "TAKING_DAMAGE"
    AMMO_LOW = "AMMO_LOW"
    ATTACK_MISSED = "ATTACK_MISSED"
    ENEMY_ELIMINATED = "ENEMY_ELIMINATED"
    BUILD_COMPLETE = "BUILD_COMPLETE"
    ALLY_DIED = "ALLY_DIED"
    ALLY_NEEDS_HEAL = "ALLY_NEEDS_HEAL"
    BASE_UNDER_ATTACK = "BASE_UNDER_ATTACK"
    OBJECTIVE_UPDATE = "OBJECTIVE_UPDATE"
    COMMANDER_BROADCAST = "COMMANDER_BROADCAST"


class LocalContext(BaseModel):
    nearby_enemies: list[dict[str, Any]]
    nearby_allies: list[dict[str, Any]]
    structures: list[dict[str, Any]]
    recent_events: list[str]
    strategic_positions: list[dict[str, Any]]
    # Filled by event queue coalescing: older events merged from prior think cycles
    merged_recent_events: list[str] = []


class RobotEvent(BaseModel):
    robot_id: str
    event_type: EventType
    event_detail: str
    local_context: LocalContext
    player_instructions: str
    commander_broadcast: Optional[str] = None


class MoveAction(BaseModel):
    action: Literal["move"]
    destination: str = Field(min_length=1)
    reason: Optional[str] = None


class AttackAction(BaseModel):
    # "snipe" is a range-focused variant; approach still applies (sniper uses maintain_range or stay_back)
    action: Literal["attack", "snipe"]
    # Runtime instance ID assigned by Godot game manager (1, 2, 3...), not config-level IDs
    target_id: int
    approach: Literal["close_in", "maintain_range", "stay_back"]
    reason: Optional[str] = None


class BuildAction(BaseModel):
    action: Literal["build", "deploy_turret"]
    structure: Literal["wall", "barricade", "watchtower", "ammo_depot", "medic_station", "turret"]
    destination: str = Field(min_length=1)
    reason: Optional[str] = None


class RetreatAction(BaseModel):
    action: Literal["retreat"]
    destination: str = Field(min_length=1)
    reason: Optional[str] = None


class SupportAction(BaseModel):
    action: Literal["heal", "idle"]
    # Runtime instance ID (1, 2, 3...) or None for idle
    target_id: Optional[int] = None
    reason: Optional[str] = None


RobotAction = Union[MoveAction, AttackAction, BuildAction, RetreatAction, SupportAction]

_ACTION_MAP = {
    "move": MoveAction,
    "attack": AttackAction,
    "snipe": AttackAction,
    "build": BuildAction,
    "deploy_turret": BuildAction,
    "retreat": RetreatAction,
    "heal": SupportAction,
    "idle": SupportAction,
}


def parse_robot_action(data: dict[str, Any]) -> RobotAction:
    action_type = data.get("action")
    model = _ACTION_MAP.get(action_type)
    if model is None:
        raise ValueError(f"Unknown action type: {action_type}")
    return model(**data)


class WsIncoming(BaseModel):
    # TODO: Expand to discriminated union when additional message types are added
    type: Literal["robot_event"]
    robot_id: str
    event_type: EventType
    event_detail: str
    local_context: LocalContext
    player_instructions: str
    commander_broadcast: Optional[str] = None

    def to_robot_event(self) -> RobotEvent:
        return RobotEvent(
            robot_id=self.robot_id,
            event_type=self.event_type,
            event_detail=self.event_detail,
            local_context=self.local_context,
            player_instructions=self.player_instructions,
            commander_broadcast=self.commander_broadcast,
        )


class WsOutgoing(BaseModel):
    robot_id: str
    action: RobotAction
