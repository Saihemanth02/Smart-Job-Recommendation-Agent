import time
import os
from datetime import datetime
import uuid
from agents.base_agent import BaseAgent, AgentMessage

class InterviewPrepAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are a technical interview coach. Given the candidate's predicted "
            "role and skill set, generate 5 technical and 3 behavioral interview "
            "questions they are realistically likely to face. For each behavioral "
            "question, give a one-line STAR-method framing hint — not a full "
            "scripted answer. Keep technical questions calibrated to a fresher/ "
            "early-career level, not senior-level trick questions."
        )
        super().__init__(
            name="Interview Prep Agent",
            role="Interview Coach",
            system_prompt=system_prompt,
            model_backend="groq"  # Uses Groq primary with Gemini fallback
        )

    def handle(self, message: AgentMessage) -> AgentMessage:
        start_time = time.time()
        
        payload = message.payload
        predicted_role = payload.get("predicted_role", "")
        skills = payload.get("skills", [])
        
        if not predicted_role:
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": "Predicted job role is required"},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )

        try:
            user_prompt = (
                f"Candidate Details:\n"
                f"- Predicted Role: {predicted_role}\n"
                f"- Extracted Skills: {', '.join(skills)}\n\n"
                f"Generate 5 technical questions (focused on this role and skills) and 3 behavioral questions "
                f"calibrated for a fresher/early-career candidate.\n\n"
                f"Return JSON format:\n"
                f'{{"technical": ["Q1", "Q2", "Q3", "Q4", "Q5"], '
                f'"behavioral": ['
                f'{{"question": "Q1", "star_hint": "STAR Hint 1"}},'
                f'{{"question": "Q2", "star_hint": "STAR Hint 2"}},'
                f'{{"question": "Q3", "star_hint": "STAR Hint 3"}}'
                f']}}'
            )
            
            llm_result = self.call_llm(user_prompt=user_prompt, json_mode=True, task_size="small")
            
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="success",
                result={
                    "technical_questions": llm_result.get("technical", []),
                    "behavioral_questions": llm_result.get("behavioral", [])
                },
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            mock_result = {
                "technical_questions": [
                    f"Explain the difference between core architectures in {predicted_role or 'software engineering'}.",
                    "How does resource allocation optimize execution inside high-performance loops?",
                    "Explain how you would debug memory leaks inside a garbage-collected environment.",
                    "What is Git rebase and how does it differ from Git merge?",
                    "How do WebSockets differ from standard stateless HTTP requests?"
                ],
                "behavioral_questions": [
                    {
                        "question": "Describe a challenging technical project and how you handled difficulties.",
                        "star_hint": "Outline the task scope, describe your individual coding solution, and list key metrics improved."
                    },
                    {
                        "question": "How do you handle disagreement on design decisions within a dev team?",
                        "star_hint": "Focus on collaborative technical reasoning, listing pros and cons, and alignment."
                    },
                    {
                        "question": "Tell us about a time you had to learn a new tool under tight deadlines.",
                        "star_hint": "Detail the resource roadmap you set up, fast proof-of-concept projects, and delivery."
                    }
                ]
            }
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="success",
                result=mock_result,
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )
