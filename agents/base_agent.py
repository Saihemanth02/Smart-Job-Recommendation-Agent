from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Any, Optional, Dict
from abc import ABC, abstractmethod
import uuid
import time
from llm.llm_router import call_llm

@dataclass
class AgentMessage:
    message_id: str
    trace_id: str
    from_agent: str
    to_agent: str
    task: str
    payload: dict
    status: Literal["pending", "success", "error"]
    result: Optional[dict] = None
    timestamp: datetime = datetime.now()
    latency_ms: Optional[int] = None

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str, model_backend: Literal["sklearn", "groq", "gemini", "hybrid"]):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_backend = model_backend

    @abstractmethod
    def handle(self, message: AgentMessage) -> AgentMessage:
        """
        Processes the message and returns a new AgentMessage with the result.
        """
        pass

    def call_llm(self, user_prompt: str, json_mode: bool = False, task_size: Literal["small", "large"] = "small") -> dict | str:
        """
        Helper method to call the LLM Router using the agent's specific system prompt.
        """
        return call_llm(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            json_mode=json_mode,
            task_size=task_size
        )
