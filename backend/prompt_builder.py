from __future__ import annotations
import json
from backend.models import RobotEvent


class PromptBuilder:
    def build(self, robot_config: dict, runtime_stats: dict, event: RobotEvent) -> str:
        stats = robot_config["base_stats"]
        intelligence = stats["intelligence"]
        max_instruction_chars = intelligence * 100

        instructions = event.player_instructions[:max_instruction_chars]

        ctx = event.local_context
        enemies_text = json.dumps(ctx.nearby_enemies, indent=None)
        allies_text = json.dumps(ctx.nearby_allies, indent=None)
        structures_text = json.dumps(ctx.structures, indent=None)
        events_text = "\n".join(ctx.recent_events) if ctx.recent_events else "None"
        positions_text = "\n".join(
            f"- {p['id']}: {p['description']}" for p in ctx.strategic_positions
        )

        broadcast_line = (
            f'Commander broadcast: "{event.commander_broadcast}"'
            if event.commander_broadcast
            else "Commander broadcast: None"
        )

        health = runtime_stats.get("health", stats["health"])
        ammo = runtime_stats.get("ammo", stats["ammo"])

        return f"""[System]
You are {robot_config['name']}, a {robot_config['rarity']} {robot_config['class']} robot. {robot_config['personality_prompt']}
Your stats: speed={stats['speed']}, damage={stats['damage']}, armor={stats['armor']}, health={health}/{stats['health']}, ammo={ammo}, building_skill={stats['building_skill']}

[Player Instructions]
{instructions}

[Environment]
Nearby enemies: {enemies_text}
Nearby allies: {allies_text}
Structures: {structures_text}
Recent events:
{events_text}
Strategic positions:
{positions_text}

[Global]
{broadcast_line}

[Event]
{event.event_type.value}: {event.event_detail}

[Instruction]
You MUST respond with ONLY a JSON object. No other text.
Valid actions: move, attack, snipe, build, deploy_turret, retreat, heal, idle.
Enemy target_id values are small sequential integers (1, 2, 3...) as shown in the enemy list above.

PRIORITY RULES:
1. If enemies are nearby, you MUST attack or snipe. Do NOT move or idle when enemies are present.
2. If you are a medic and an ally has low health, you MUST heal them.
3. Only move if no enemies are nearby and you need to reposition.
4. Only idle if there is truly nothing to do.

Example: {{"action": "attack", "target_id": 1, "approach": "close_in", "reason": "Enemy nearby, engaging"}}
Example: {{"action": "snipe", "target_id": 2, "approach": "maintain_range", "reason": "Picking off target at range"}}
Example: {{"action": "heal", "target_id": 2, "reason": "Ally at low health"}}
Example: {{"action": "move", "destination": "north_chokepoint", "reason": "Repositioning to chokepoint"}}
Example: {{"action": "build", "structure": "wall", "destination": "north_chokepoint", "reason": "Fortifying position"}}
"""
