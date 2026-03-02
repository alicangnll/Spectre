"""Session state management."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from ..core.types import Message, Role, ToolResult, TokenUsage


@dataclass
class SessionState:
    """Holds the state of one Rikugan conversation session."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: float = field(default_factory=time.time)
    messages: List[Message] = field(default_factory=list)
    total_usage: TokenUsage = field(default_factory=TokenUsage)
    current_turn: int = 0
    is_running: bool = False
    provider_name: str = ""
    model_name: str = ""
    idb_path: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def add_message(self, msg: Message) -> None:
        self.messages.append(msg)
        if msg.token_usage:
            self.total_usage.prompt_tokens += msg.token_usage.prompt_tokens
            self.total_usage.completion_tokens += msg.token_usage.completion_tokens
            self.total_usage.total_tokens += msg.token_usage.total_tokens

    def clear(self) -> None:
        self.messages.clear()
        self.total_usage = TokenUsage()
        self.current_turn = 0
        self.is_running = False

    def get_messages_for_provider(self) -> List[Message]:
        """Return messages sanitized for the provider API.

        Ensures every assistant message that contains tool_calls has
        matching tool_result entries in the following TOOL message.
        Orphaned tool_use blocks (e.g. from cancellation mid-execution)
        get synthetic error results appended so the API never sees a
        tool_use without a corresponding tool_result.
        """
        msgs = list(self.messages)
        sanitized: List[Message] = []
        i = 0
        while i < len(msgs):
            msg = msgs[i]
            if msg.role == Role.ASSISTANT and msg.tool_calls:
                sanitized.append(msg)
                i += 1
                # Collect all tool_call ids that need results
                needed_ids: Set[str] = {tc.id for tc in msg.tool_calls}
                # Look ahead for the TOOL message with results
                if i < len(msgs) and msgs[i].role == Role.TOOL:
                    tool_msg = msgs[i]
                    found_ids = {tr.tool_call_id for tr in tool_msg.tool_results}
                    missing = needed_ids - found_ids
                    if missing:
                        # Add stubs for missing results
                        patched_results = list(tool_msg.tool_results)
                        for tc in msg.tool_calls:
                            if tc.id in missing:
                                patched_results.append(ToolResult(
                                    tool_call_id=tc.id, name=tc.name,
                                    content="Cancelled.", is_error=True,
                                ))
                        sanitized.append(Message(
                            role=Role.TOOL, tool_results=patched_results,
                        ))
                    else:
                        sanitized.append(tool_msg)
                    i += 1
                else:
                    # No TOOL message at all — create one with error stubs
                    stubs = [
                        ToolResult(
                            tool_call_id=tc.id, name=tc.name,
                            content="Cancelled.", is_error=True,
                        )
                        for tc in msg.tool_calls
                    ]
                    sanitized.append(Message(role=Role.TOOL, tool_results=stubs))
            else:
                sanitized.append(msg)
                i += 1
        return sanitized

    def message_count(self) -> int:
        return len(self.messages)
