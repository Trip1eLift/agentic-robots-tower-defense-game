from __future__ import annotations
import json
import re
from backend.models import RobotAction, SupportAction, parse_robot_action


class ActionParser:
    # Matches flat JSON objects only (no nested braces). Current action models
    # are all flat, so this is sufficient. If models ever gain nested fields,
    # this pattern must be updated.
    _JSON_PATTERN = re.compile(r'\{[^{}]*\}', re.DOTALL)

    def parse(self, llm_response: str) -> RobotAction:
        candidates = self._JSON_PATTERN.findall(llm_response)
        for candidate in candidates:
            try:
                data = json.loads(candidate)
                if "action" in data:
                    return parse_robot_action(data)
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
        return SupportAction(action="idle", reason="Could not parse LLM response")
