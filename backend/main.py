from __future__ import annotations
import asyncio
import json
import logging
import os
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from backend.action_parser import ActionParser
from backend.config_loader import ConfigLoader
from backend.event_queue import EventQueue
from backend.mock_llm import MockLLM
from backend.models import SupportAction, WsIncoming, WsOutgoing
from backend.ollama_client import OllamaClient
from backend.prompt_builder import PromptBuilder
from backend.robot_state import RobotStateStore

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"

app = FastAPI()

config_loader = ConfigLoader(DATA_DIR)
robot_state_store = RobotStateStore()
event_queue = EventQueue()
prompt_builder = PromptBuilder()
action_parser = ActionParser()
USE_MOCK_LLM = os.environ.get("USE_MOCK_LLM", "false").lower() == "true"
ollama_client = MockLLM() if USE_MOCK_LLM else OllamaClient()


@app.on_event("startup")
async def startup():
    global _ollama_semaphore, _ws_send_lock
    _ollama_semaphore = asyncio.Semaphore(1)
    _ws_send_lock = asyncio.Lock()


async def process_robot_events(robot_id: str, websocket: WebSocket) -> None:
    robot_config = config_loader.get_robot(robot_id)
    try:
        while True:
            event = await event_queue.dequeue(robot_id)
            try:
                state = robot_state_store.get(robot_id)
            except KeyError:
                continue

            if not state.is_alive:
                continue

            try:
                runtime_stats = {"health": state.health, "ammo": state.ammo}
                prompt = prompt_builder.build(robot_config, runtime_stats, event)
                async with _ollama_semaphore:
                    llm_response = await ollama_client.think(prompt)
                action = action_parser.parse(llm_response)
            except Exception as e:
                logger.error(f"LLM processing failed for {robot_id}: {e}")
                action = SupportAction(action="idle", reason=f"LLM error: {type(e).__name__}")

            robot_state_store.set_current_action(robot_id, action.action)

            outgoing = WsOutgoing(type="robot_action", robot_id=robot_id, action=action)
            async with _ws_send_lock:
                await websocket.send_text(outgoing.model_dump_json())
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Processor task for {robot_id} died: {e}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    processor_tasks: dict[str, asyncio.Task] = {}

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                async with _ws_send_lock:
                    await websocket.send_text(json.dumps({"error": "Invalid JSON received"}))
                continue

            try:
                if data.get("type") == "register_robot":
                    robot_id = data["robot_id"]
                    robot_state_store.register(
                        robot_id=robot_id,
                        health=data["health"],
                        max_health=data["health"],
                        ammo=data["ammo"],
                        position=tuple(data["position"])
                    )
                    if robot_id not in processor_tasks:
                        processor_tasks[robot_id] = asyncio.create_task(
                            process_robot_events(robot_id, websocket)
                        )
                    continue

                if data.get("type") == "state_update":
                    robot_id = data["robot_id"]
                    if "health" in data:
                        robot_state_store.update_health(robot_id, data["health"])
                    if "position" in data:
                        robot_state_store.update_position(robot_id, tuple(data["position"]))
                    if "ammo" in data:
                        robot_state_store.get(robot_id).ammo = data["ammo"]
                    continue

                msg = WsIncoming(**data)
                await event_queue.enqueue(msg.to_robot_event())

            except (KeyError, ValidationError) as e:
                logger.warning(f"Bad message: {e}")
                async with _ws_send_lock:
                    await websocket.send_text(json.dumps({"error": str(e)}))
                continue

    except WebSocketDisconnect:
        pass
    finally:
        for task in processor_tasks.values():
            task.cancel()
