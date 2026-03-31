import asyncio
import pytest
from backend.event_queue import EventQueue
from backend.models import EventType, LocalContext, RobotEvent


def _make_event(robot_id: str, event_type=EventType.ENEMY_SPOTTED) -> RobotEvent:
    return RobotEvent(
        robot_id=robot_id,
        event_type=event_type,
        event_detail="test event",
        local_context=LocalContext(
            nearby_enemies=[], nearby_allies=[], structures=[],
            recent_events=[], strategic_positions=[]
        ),
        player_instructions="Hold position.",
    )


@pytest.mark.asyncio
async def test_enqueue_and_dequeue():
    queue = EventQueue()
    event = _make_event("architect_common_hana")
    await queue.enqueue(event)
    dequeued = await queue.dequeue("architect_common_hana")
    assert dequeued.robot_id == "architect_common_hana"


@pytest.mark.asyncio
async def test_queue_is_per_robot():
    queue = EventQueue()
    await queue.enqueue(_make_event("architect_common_hana"))
    await queue.enqueue(_make_event("vanguard_common_rex"))
    hana_event = await queue.dequeue("architect_common_hana")
    assert hana_event.robot_id == "architect_common_hana"


@pytest.mark.asyncio
async def test_dequeue_empty_returns_none():
    queue = EventQueue()
    result = await queue.dequeue_nowait("architect_common_hana")
    assert result is None


@pytest.mark.asyncio
async def test_coalescing_keeps_latest_event():
    queue = EventQueue()
    await queue.enqueue(_make_event("architect_common_hana", EventType.ENEMY_SPOTTED))
    await queue.enqueue(_make_event("architect_common_hana", EventType.TAKING_DAMAGE))
    assert queue.size("architect_common_hana") == 1
    event = await queue.dequeue("architect_common_hana")
    assert event.event_type == EventType.TAKING_DAMAGE
    assert "ENEMY_SPOTTED" in event.local_context.merged_recent_events


@pytest.mark.asyncio
async def test_coalescing_does_not_affect_other_robots():
    queue = EventQueue()
    await queue.enqueue(_make_event("architect_common_hana", EventType.ENEMY_SPOTTED))
    await queue.enqueue(_make_event("vanguard_common_rex", EventType.TAKING_DAMAGE))
    assert queue.size("architect_common_hana") == 1
    assert queue.size("vanguard_common_rex") == 1


@pytest.mark.asyncio
async def test_coalescing_merges_multiple_older_events():
    queue = EventQueue()
    await queue.enqueue(_make_event("architect_common_hana", EventType.ENEMY_SPOTTED))
    await queue.enqueue(_make_event("architect_common_hana", EventType.AMMO_LOW))
    await queue.enqueue(_make_event("architect_common_hana", EventType.TAKING_DAMAGE))
    assert queue.size("architect_common_hana") == 1
    event = await queue.dequeue("architect_common_hana")
    assert event.event_type == EventType.TAKING_DAMAGE
    assert "ENEMY_SPOTTED" in event.local_context.merged_recent_events
    assert "AMMO_LOW" in event.local_context.merged_recent_events
