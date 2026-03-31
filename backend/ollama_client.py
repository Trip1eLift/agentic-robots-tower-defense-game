from __future__ import annotations
import asyncio
import logging
import ollama

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, model: str = "dolphin-mistral"):
        self._model = model
        self._client = ollama.AsyncClient()

    async def think(self, prompt: str) -> str:
        try:
            response = await asyncio.wait_for(
                self._client.chat(
                    model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.3, "num_predict": 200},
                    format="json"
                ),
                timeout=30,
            )
            # SDK v0.3.x returns dict, newer versions return object
            if isinstance(response, dict):
                return response["message"]["content"]
            return response.message.content
        except asyncio.TimeoutError:
            logger.error("Ollama request timed out after 30s")
            return '{"action": "idle", "reason": "LLM timeout"}'
        except Exception as e:
            logger.error(f"Ollama request failed: {e}")
            return '{"action": "idle", "reason": "LLM connection error"}'
