from __future__ import annotations
import json
from pathlib import Path


class ConfigLoader:
    def __init__(self, data_dir: Path):
        self._data_dir = data_dir
        self._robots: dict = {}
        self._maps: dict = {}
        self._missions: dict = {}
        self._enemies: dict = {}
        self._load_all()

    def _load_json(self, path: Path) -> dict:
        cfg = json.loads(path.read_text(encoding="utf-8"))
        if "id" not in cfg:
            raise KeyError(f"Missing 'id' field in config file: {path}")
        return cfg

    def _load_all(self) -> None:
        for path in (self._data_dir / "robots" / "archetypes").glob("*.json"):
            cfg = self._load_json(path)
            self._robots[cfg["id"]] = cfg

        for path in (self._data_dir / "maps").glob("*.json"):
            cfg = self._load_json(path)
            self._maps[cfg["id"]] = cfg

        for path in (self._data_dir / "enemies").glob("*.json"):
            cfg = self._load_json(path)
            self._enemies[cfg["id"]] = cfg

        for path in (self._data_dir / "campaign").rglob("mission_*.json"):
            cfg = self._load_json(path)
            self._missions[cfg["id"]] = cfg

    def get_robot(self, robot_id: str) -> dict:
        if robot_id not in self._robots:
            raise KeyError(f"Robot not found: {robot_id}")
        return self._robots[robot_id]

    def get_all_robots(self) -> list[dict]:
        return list(self._robots.values())

    def get_map(self, map_id: str) -> dict:
        if map_id not in self._maps:
            raise KeyError(f"Map not found: {map_id}")
        return self._maps[map_id]

    def get_mission(self, mission_id: str) -> dict:
        if mission_id not in self._missions:
            raise KeyError(f"Mission not found: {mission_id}")
        return self._missions[mission_id]

    def get_enemy(self, enemy_id: str) -> dict:
        if enemy_id not in self._enemies:
            raise KeyError(f"Enemy not found: {enemy_id}")
        return self._enemies[enemy_id]
