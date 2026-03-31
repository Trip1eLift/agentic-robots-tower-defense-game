from __future__ import annotations
import json
import re


class MockLLM:
    """Rule-based mock that implements the same interface as OllamaClient.

    Parses the prompt to determine robot class and context, then returns
    a deterministic JSON action string.
    """

    _CLASS_PATTERN = re.compile(r"a \w+ (\w+) robot")
    _ENEMIES_PATTERN = re.compile(r"Nearby enemies: (\[.*\])")
    _ALLIES_PATTERN = re.compile(r"Nearby allies: (\[.*\])")
    _POSITIONS_PATTERN = re.compile(r"- (\w+): ")

    async def think(self, prompt: str) -> str:
        robot_class = self._extract_class(prompt)
        enemies = self._extract_json_list(prompt, self._ENEMIES_PATTERN)
        allies = self._extract_json_list(prompt, self._ALLIES_PATTERN)
        positions = self._POSITIONS_PATTERN.findall(prompt)

        if robot_class == "vanguard":
            return self._vanguard(enemies)
        elif robot_class == "striker":
            return self._striker(enemies)
        elif robot_class == "architect":
            return self._architect(positions)
        elif robot_class == "medic":
            return self._medic(allies)
        return json.dumps({"action": "idle", "reason": "Unknown class"})

    def _extract_class(self, prompt: str) -> str:
        match = self._CLASS_PATTERN.search(prompt)
        return match.group(1).lower() if match else "unknown"

    def _extract_json_list(self, prompt: str, pattern: re.Pattern) -> list:
        match = pattern.search(prompt)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        return []

    def _vanguard(self, enemies: list) -> str:
        if enemies:
            nearest = enemies[0]
            return json.dumps({"action": "attack", "target_id": nearest["id"],
                               "approach": "close_in", "reason": "Engaging nearest enemy"})
        return json.dumps({"action": "move", "destination": "base_entrance",
                           "reason": "No enemies, moving to defend base"})

    def _striker(self, enemies: list) -> str:
        if enemies:
            nearest = enemies[0]
            return json.dumps({"action": "attack", "target_id": nearest["id"],
                               "approach": "maintain_range", "reason": "Engaging nearest enemy in range"})
        return json.dumps({"action": "idle", "reason": "No enemies in range, holding position"})

    def _architect(self, positions: list) -> str:
        dest = positions[0] if positions else "base_entrance"
        # Alternate between building and moving based on position count
        if len(positions) >= 2:
            return json.dumps({"action": "build", "structure": "wall", "destination": dest,
                               "reason": "Fortifying strategic position"})
        return json.dumps({"action": "move", "destination": dest,
                           "reason": "Moving to uncovered strategic position"})

    def _medic(self, allies: list) -> str:
        if allies:
            lowest = min(allies, key=lambda a: a["health"])
            # target_id must be int to match SupportAction schema; use index as fallback
            tid = lowest.get("id")
            if not isinstance(tid, int):
                tid = allies.index(lowest) + 1
            return json.dumps({"action": "heal", "target_id": tid,
                               "reason": "Healing lowest-health ally"})
        return json.dumps({"action": "idle", "reason": "No allies to heal"})
