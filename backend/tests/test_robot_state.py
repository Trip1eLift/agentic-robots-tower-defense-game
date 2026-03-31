import pytest
from backend.robot_state import RobotStateStore, RobotState


def test_register_robot():
    store = RobotStateStore()
    store.register("architect_common_hana", health=100, max_health=100, ammo=40, position=(512, 460))
    state = store.get("architect_common_hana")
    assert state.health == 100
    assert state.position == (512, 460)
    assert state.is_alive is True


def test_update_health():
    store = RobotStateStore()
    store.register("vanguard_common_rex", health=200, max_health=200, ammo=60, position=(512, 420))
    store.update_health("vanguard_common_rex", new_health=150)
    assert store.get("vanguard_common_rex").health == 150


def test_robot_dies_at_zero_health():
    store = RobotStateStore()
    store.register("striker_common_aurora", health=90, max_health=90, ammo=80, position=(200, 300))
    store.update_health("striker_common_aurora", new_health=0)
    assert store.get("striker_common_aurora").is_alive is False


def test_update_position():
    store = RobotStateStore()
    store.register("medic_common_lily", health=110, max_health=110, ammo=30, position=(512, 460))
    store.update_position("medic_common_lily", new_position=(300, 400))
    assert store.get("medic_common_lily").position == (300, 400)


def test_set_current_action():
    store = RobotStateStore()
    store.register("architect_common_hana", health=100, max_health=100, ammo=40, position=(512, 460))
    store.set_current_action("architect_common_hana", "build")
    assert store.get("architect_common_hana").current_action == "build"


def test_health_clamps_to_max():
    store = RobotStateStore()
    store.register("vanguard_common_rex", health=200, max_health=200, ammo=60, position=(512, 420))
    store.update_health("vanguard_common_rex", new_health=999)
    assert store.get("vanguard_common_rex").health == 200


def test_negative_health_clamps_to_zero():
    store = RobotStateStore()
    store.register("striker_common_aurora", health=90, max_health=90, ammo=80, position=(200, 300))
    store.update_health("striker_common_aurora", new_health=-50)
    assert store.get("striker_common_aurora").health == 0
    assert store.get("striker_common_aurora").is_alive is False


def test_revive_after_death():
    store = RobotStateStore()
    store.register("medic_common_lily", health=110, max_health=110, ammo=30, position=(512, 460))
    store.update_health("medic_common_lily", new_health=0)
    assert store.get("medic_common_lily").is_alive is False
    store.update_health("medic_common_lily", new_health=50)
    assert store.get("medic_common_lily").is_alive is True
    assert store.get("medic_common_lily").health == 50


def test_all_states():
    store = RobotStateStore()
    store.register("a", health=100, max_health=100, ammo=40, position=(0, 0))
    store.register("b", health=200, max_health=200, ammo=60, position=(1, 1))
    states = store.all_states()
    assert len(states) == 2
    ids = {s.robot_id for s in states}
    assert ids == {"a", "b"}


def test_get_missing_robot_raises():
    store = RobotStateStore()
    with pytest.raises(KeyError):
        store.get("nonexistent")
