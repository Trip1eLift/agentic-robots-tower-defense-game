import pytest
from pathlib import Path
from backend.config_loader import ConfigLoader

DATA_DIR = Path(__file__).parent.parent.parent / "data"


def test_load_robot_config():
    loader = ConfigLoader(DATA_DIR)
    robot = loader.get_robot("architect_common_hana")
    assert robot["name"] == "Hana"
    assert robot["class"] == "architect"
    assert robot["base_stats"]["intelligence"] == 5


def test_load_all_robots():
    loader = ConfigLoader(DATA_DIR)
    robots = loader.get_all_robots()
    assert len(robots) == 4
    classes = {r["class"] for r in robots}
    assert classes == {"architect", "vanguard", "striker", "medic"}


def test_load_map_config():
    loader = ConfigLoader(DATA_DIR)
    map_cfg = loader.get_map("ch01_collapsed_road")
    assert map_cfg["name"] == "Collapsed Road"
    assert len(map_cfg["strategic_positions"]) == 4


def test_load_mission_config():
    loader = ConfigLoader(DATA_DIR)
    mission = loader.get_mission("ch01_mission_01")
    assert mission["title"] == "First Contact"
    assert len(mission["waves"]) == 3


def test_load_enemy_config():
    loader = ConfigLoader(DATA_DIR)
    enemy = loader.get_enemy("zombie")
    assert enemy["stats"]["health"] == 50


def test_missing_robot_raises():
    loader = ConfigLoader(DATA_DIR)
    with pytest.raises(KeyError):
        loader.get_robot("nonexistent_robot")
