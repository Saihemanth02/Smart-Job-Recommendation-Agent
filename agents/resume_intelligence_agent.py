import time
from datetime import datetime
import uuid
from agents.base_agent import BaseAgent, AgentMessage

class ResumeIntelligenceAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are a resume-parsing specialist. Given raw extracted resume "
            "text, output ONLY structured JSON with keys: name, email, phone, "
            "education (list), experience (list of {title, company, duration, "
            "description}), projects (list), certifications (list), raw_skills_text.\n"
            "Never invent information that is not present in the text. If a field "
            "is missing, return null or an empty list. Never include commentary "
            "outside the JSON object."
        )
        super().__init__(
            name="Resume Intelligence Agent",
            role="Resume Parser & Structurer",
            system_prompt=system_prompt,
            model_backend="hybrid"
        )

    def handle(self, message: AgentMessage) -> AgentMessage:
        start_time = time.time()
        raw_text = message.payload.get("raw_text", "")
        
        if not raw_text:
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": "Empty raw text provided"},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )

        try:
            # Request small model output as JSON mode
            structured_data = self.call_llm(
                user_prompt=f"Parse the following resume text:\n\n{raw_text}",
                json_mode=True,
                task_size="small"
            )
            
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="success",
                result={"parsed_resume": structured_data},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": str(e)},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )
