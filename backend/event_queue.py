from __future__ import annotations
import asyncio
from typing import Optional
from backend.models import RobotEvent


class EventQueue:
    """Per-robot async event queue with coalescing.

    Event coalescing: when a new event arrives for a robot, older queued
    events are drained but their event types are preserved in the new
    event's local_context.merged_recent_events list. This keeps the
    latest context while still informing the LLM about recent history.
    """

    def __init__(self):
        self._queues: dict[str, asyncio.Queue[RobotEvent]] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def _get_queue(self, robot_id: str) -> asyncio.Queue[RobotEvent]:
        if robot_id not in self._queues:
            self._queues[robot_id] = asyncio.Queue()
        return self._queues[robot_id]

    def _get_lock(self, robot_id: str) -> asyncio.Lock:
        if robot_id not in self._locks:
            self._locks[robot_id] = asyncio.Lock()
        return self._locks[robot_id]

    async def enqueue(self, event: RobotEvent) -> None:
        # Note: coalescing mutates event.local_context.merged_recent_events
        async with self._get_lock(event.robot_id):
            q = self._get_queue(event.robot_id)
            merged: list[str] = []
            while not q.empty():
                try:
                    old_event = q.get_nowait()
                    merged.extend(old_event.local_context.merged_recent_events)
                    merged.append(old_event.event_type.value)
                except asyncio.QueueEmpty:
                    break
            if merged:
                event.local_context.merged_recent_events = merged
            await q.put(event)

    async def dequeue(self, robot_id: str) -> RobotEvent:
        return await self._get_queue(robot_id).get()

    async def dequeue_nowait(self, robot_id: str) -> Optional[RobotEvent]:
        try:
            return self._get_queue(robot_id).get_nowait()
        except asyncio.QueueEmpty:
            return None

    def size(self, robot_id: str) -> int:
        return self._get_queue(robot_id).qsize()
