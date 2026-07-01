import time
from datetime import datetime
import uuid
import logging
from typing import List, Dict, Any, Optional

from agents.base_agent import BaseAgent, AgentMessage
from utils.db import log_message_to_db, save_session_context, get_session_context

# Import specialist agents
from agents.resume_intelligence_agent import ResumeIntelligenceAgent
from agents.skill_extraction_agent import SkillExtractionAgent
from agents.job_prediction_agent import JobPredictionAgent
from agents.market_intelligence_agent import MarketIntelligenceAgent
from agents.salary_prediction_agent import SalaryPredictionAgent
from agents.skill_gap_roadmap_agent import SkillGapRoadmapAgent
from agents.resume_optimizer_agent import ResumeOptimizerAgent
from agents.interview_prep_agent import InterviewPrepAgent

logger = logging.getLogger(__name__)

class Orchestrator(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are the Career Advisor, lead coordinator of a team of specialist "
            "career-analysis agents. You never analyze resumes yourself — you "
            "delegate to the correct specialist agent, wait for their structured "
            "result, and weave the combined output into one coherent, encouraging, "
            "and honest final report for the candidate. Never repeat raw JSON to "
            "the user; always translate it into clear, supportive language. Flag "
            "low-confidence predictions explicitly rather than overstating them."
        )
        super().__init__(
            name="Career Advisor",
            role="Orchestrator",
            system_prompt=system_prompt,
            model_backend="hybrid"
        )
        
        # Instantiate the agents
        self.resume_intelligence = ResumeIntelligenceAgent()
        self.skill_extraction = SkillExtractionAgent()
        self.job_prediction = JobPredictionAgent()
        self.market_intelligence = MarketIntelligenceAgent()
        self.salary_prediction = SalaryPredictionAgent()
        self.skill_gap_roadmap = SkillGapRoadmapAgent()
        self.resume_optimizer = ResumeOptimizerAgent()
        self.interview_prep = InterviewPrepAgent()
        
        # Local log in-memory
        self.message_log: List[AgentMessage] = []
        self.context: Dict[str, Any] = {}

    def _log_message(self, message: AgentMessage):
        self.message_log.append(message)
        log_message_to_db(message)

    def handle(self, message: AgentMessage) -> AgentMessage:
        # Orchestrator does not process standard handle commands from other agents;
        # it is the caller and DAG executor.
        return message

    def run_pipeline(self, raw_resume_text: str, filename: str, location_tier: int = 1) -> Dict[str, Any]:
        """
        Executes the Multi-Agent Pipeline DAG:
        ResumeIntelligenceAgent -> SkillExtractionAgent -> JobPredictionAgent 
        -> (MarketIntelligenceAgent & SalaryPredictionAgent) -> SkillGapRoadmapAgent -> Summary
        """
        trace_id = str(uuid.uuid4())
        self.message_log = [] # Clear memory log
        
        self.context = {
            "trace_id": trace_id,
            "filename": filename,
            "location_tier": location_tier,
            "raw_text": raw_resume_text
        }
        
        # --- 1. RESUME INTELLIGENCE AGENT ---
        print("[Orchestrator] Running ResumeIntelligenceAgent...")
        msg_parser = AgentMessage(
            message_id=str(uuid.uuid4()),
            trace_id=trace_id,
            from_agent=self.name,
            to_agent=self.resume_intelligence.name,
            task="parse_resume",
            payload={"raw_text": raw_resume_text},
            status="pending",
            timestamp=datetime.now()
        )
        self._log_message(msg_parser)
        
        try:
            resp_parser = self.resume_intelligence.handle(msg_parser)
            self._log_message(resp_parser)
            if resp_parser.status == "success":
                parsed_data = resp_parser.result.get("parsed_resume", {})
            else:
                raise ValueError("Parsing agent returned error status.")
        except Exception as e:
            logger.error(f"ResumeIntelligenceAgent failed: {str(e)}")
            # Degraded fallback parsing
            parsed_data = {
                "name": "Candidate Profile",
                "email": "not-found@example.com",
                "phone": "+91-00000-00000",
                "education": ["Graduate Degree"],
                "experience": [],
                "projects": [],
                "certifications": [],
                "raw_skills_text": ""
            }
            self._log_message(AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=trace_id,
                from_agent=self.resume_intelligence.name,
                to_agent=self.name,
                task="parse_resume",
                payload={"raw_text": raw_resume_text},
                status="error",
                result={"error": f"Degraded mode: {str(e)}"},
                timestamp=datetime.now(),
                latency_ms=0
            ))
            
        self.context["parsed_resume"] = parsed_data
        
        # --- 2. SKILL EXTRACTION AGENT ---
        print("[Orchestrator] Running SkillExtractionAgent...")
        msg_skills = AgentMessage(
            message_id=str(uuid.uuid4()),
            trace_id=trace_id,
            from_agent=self.name,
            to_agent=self.skill_extraction.name,
            task="extract_skills",
            payload={"resume_text": raw_resume_text},
            status="pending",
            timestamp=datetime.now()
        )
        self._log_message(msg_skills)
        
        try:
            resp_skills = self.skill_extraction.handle(msg_skills)
            self._log_message(resp_skills)
            if resp_skills.status == "success":
                skills_info = resp_skills.result.get("skills", {})
                confidence_info = resp_skills.result.get("confidence", {})
            else:
                raise ValueError("Skill Extraction agent returned error status.")
        except Exception as e:
            logger.error(f"SkillExtractionAgent failed: {str(e)}")
            skills_info = {"technical": [], "tools": [], "soft": [], "domain": []}
            confidence_info = {}
            self._log_message(AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=trace_id,
                from_agent=self.skill_extraction.name,
                to_agent=self.name,
                task="extract_skills",
                payload={"resume_text": raw_resume_text},
                status="error",
                result={"error": f"Degraded mode: {str(e)}"},
                timestamp=datetime.now(),
                latency_ms=0
            ))
            
        self.context["skills"] = skills_info
        self.context["skills_confidence"] = confidence_info
        
        # --- 3. JOB PREDICTION AGENT ---
        print("[Orchestrator] Running JobPredictionAgent...")
        msg_jobs = AgentMessage(
            message_id=str(uuid.uuid4()),
            trace_id=trace_id,
            from_agent=self.name,
            to_agent=self.job_prediction.name,
            task="predict_jobs",
            payload={"skills": skills_info, "parsed_resume": parsed_data},
            status="pending",
            timestamp=datetime.now()
        )
        self._log_message(msg_jobs)
        
        try:
            resp_jobs = self.job_prediction.handle(msg_jobs)
            self._log_message(resp_jobs)
            if resp_jobs.status == "success":
                jobs_result = resp_jobs.result
            else:
                raise ValueError("Job Prediction agent returned error status.")
        except Exception as e:
            logger.error(f"JobPredictionAgent failed: {str(e)}")
            jobs_result = {
                "coarse_category": "Software Development",
                "top_roles": [{"role": "Frontend Developer", "confidence": 0.5, "category": "Software Development", "category_match": True}],
                "candidate_features": [],
                "experience_years": 0,
                "education_encoded": 2
            }
            self._log_message(AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=trace_id,
                from_agent=self.job_prediction.name,
                to_agent=self.name,
                task="predict_jobs",
                payload={"skills": skills_info, "parsed_resume": parsed_data},
                status="error",
                result={"error": f"Degraded mode: {str(e)}"},
                timestamp=datetime.now(),
                latency_ms=0
            ))
            
        self.context["coarse_category"] = jobs_result.get("coarse_category", "Unknown")
        self.context["top_roles"] = jobs_result.get("top_roles", [])
        self.context["candidate_features"] = jobs_result.get("candidate_features", [])
        self.context["experience_years"] = jobs_result.get("experience_years", 0)
        self.context["education_encoded"] = jobs_result.get("education_encoded", 2)
        
        # Primary targeted role for subsequent agents is the top predicted role
        top_role = self.context["top_roles"][0]["role"] if self.context["top_roles"] else "Frontend Developer"
        self.context["primary_target_role"] = top_role
        
        # --- 4. MARKET INTELLIGENCE AGENT (Runs in parallel with salary) ---
        print("[Orchestrator] Running MarketIntelligenceAgent...")
        msg_market = AgentMessage(
            message_id=str(uuid.uuid4()),
            trace_id=trace_id,
            from_agent=self.name,
            to_agent=self.market_intelligence.name,
            task="get_market_intel",
            payload={"predicted_role": top_role},
            status="pending",
            timestamp=datetime.now()
        )
        self._log_message(msg_market)
        
        try:
            resp_market = self.market_intelligence.handle(msg_market)
            self._log_message(resp_market)
            if resp_market.status == "success":
                market_result = resp_market.result
            else:
                raise ValueError("Market Intel agent returned error status.")
        except Exception as e:
            logger.error(f"MarketIntelligenceAgent failed: {str(e)}")
            market_result = {
                "salary_stats": {"mean": 4.5, "median": 4.5, "min": 3.0, "max": 8.0, "std": 1.0},
                "salary_by_tier": {1: 4.8, 2: 4.0, 3: 3.2},
                "salary_by_experience": {0: 4.0, 1: 5.5, 2: 7.0, 3: 8.5},
                "top_skills": {"React": 10, "JavaScript": 10},
                "trend_summary": "Steady demand for frontend development roles."
            }
            self._log_message(AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=trace_id,
                from_agent=self.market_intelligence.name,
                to_agent=self.name,
                task="get_market_intel",
                payload={"predicted_role": top_role},
                status="error",
                result={"error": f"Degraded mode: {str(e)}"},
                timestamp=datetime.now(),
                latency_ms=0
            ))
            
        self.context["market_data"] = market_result
        
        # --- 5. SALARY PREDICTION AGENT ---
        print("[Orchestrator] Running SalaryPredictionAgent...")
        
        # Calculate skill count from skills_info
        num_skills = 0
        if isinstance(skills_info, dict):
            for cat, s_list in skills_info.items():
                if isinstance(s_list, list):
                    num_skills += len(s_list)
        if num_skills == 0:
            num_skills = 5  # default fallback
            
        msg_salary = AgentMessage(
            message_id=str(uuid.uuid4()),
            trace_id=trace_id,
            from_agent=self.name,
            to_agent=self.salary_prediction.name,
            task="predict_salary",
            payload={
                "predicted_role": top_role,
                "experience_years": self.context["experience_years"],
                "location_tier": location_tier,
                "num_skills": num_skills,
                "education_encoded": self.context["education_encoded"],
                "num_certifications": len(parsed_data.get("certifications", []))
            },
            status="pending",
            timestamp=datetime.now()
        )
        self._log_message(msg_salary)
        
        try:
            resp_salary = self.salary_prediction.handle(msg_salary)
            self._log_message(resp_salary)
            if resp_salary.status == "success":
                salary_result = resp_salary.result
            else:
                raise ValueError("Salary Prediction agent returned error status.")
        except Exception as e:
            logger.error(f"SalaryPredictionAgent failed: {str(e)}")
            salary_result = {
                "predicted_salary_mean": 4.5,
                "predicted_salary_std": 0.5,
                "salary_low": 4.0,
                "salary_high": 5.0,
                "market_note": "A typical starting compensation range in India."
            }
            self._log_message(AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=trace_id,
                from_agent=self.salary_prediction.name,
                to_agent=self.name,
                task="predict_salary",
                payload=msg_salary.payload,
                status="error",
                result={"error": f"Degraded mode: {str(e)}"},
                timestamp=datetime.now(),
                latency_ms=0
            ))
            
        self.context["salary_data"] = salary_result
        
        # --- 6. SKILL GAP & ROADMAP AGENT ---
        print("[Orchestrator] Running SkillGapRoadmapAgent...")
        msg_roadmap = AgentMessage(
            message_id=str(uuid.uuid4()),
            trace_id=trace_id,
            from_agent=self.name,
            to_agent=self.skill_gap_roadmap.name,
            task="generate_roadmap",
            payload={"skills": skills_info, "target_role": top_role},
            status="pending",
            timestamp=datetime.now()
        )
        self._log_message(msg_roadmap)
        
        try:
            resp_roadmap = self.skill_gap_roadmap.handle(msg_roadmap)
            self._log_message(resp_roadmap)
            if resp_roadmap.status == "success":
                roadmap_result = resp_roadmap.result
            else:
                raise ValueError("Skill Gap & Roadmap agent returned error status.")
        except Exception as e:
            logger.error(f"SkillGapRoadmapAgent failed: {str(e)}")
            roadmap_result = {
                "missing_skills": [],
                "prioritized_gaps": {"high": [], "medium": [], "low": []},
                "roadmap": "Focus on sharpening fundamental engineering concepts."
            }
            self._log_message(AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=trace_id,
                from_agent=self.skill_gap_roadmap.name,
                to_agent=self.name,
                task="generate_roadmap",
                payload={"skills": skills_info, "target_role": top_role},
                status="error",
                result={"error": f"Degraded mode: {str(e)}"},
                timestamp=datetime.now(),
                latency_ms=0
            ))
            
        self.context["roadmap_data"] = roadmap_result
        
        # --- 7. FINAL EXECUTIVE SUMMARY (Orchestrator generates summary) ---
        print("[Orchestrator] Generating final report summary...")
        try:
            summary_prompt = (
                f"Candidate: {parsed_data.get('name', 'Applicant')}\n"
                f"Primary Target Role Fit: {top_role} (Confidence: {self.context['top_roles'][0]['confidence']:.2f})\n"
                f"Salary Estimate: {salary_result['salary_low']:.2f}L - {salary_result['salary_high']:.2f}L LPA\n"
                f"Key Missing Skills: {', '.join(roadmap_result['missing_skills'][:4])}\n\n"
                f"Please write a cohesive, encouraging, and honest 150-word final career assessment report "
                f"for the candidate. Do not repeat raw JSON, structure it in clean, supportive paragraphs, "
                f"and explicitly address if any prediction carries a low-confidence rating (e.g. confidence < 0.5)."
            )
            report_summary = self.call_llm(user_prompt=summary_prompt, json_mode=False, task_size="small")
        except Exception as e:
            logger.error(f"Orchestrator LLM summary failed: {str(e)}")
            report_summary = (
                f"Based on our analysis, we recommend you pursue the {top_role} role. "
                f"The target entry compensation is estimated between {salary_result['salary_low']:.1f} LPA "
                f"and {salary_result['salary_high']:.1f} LPA. To increase your competitiveness, focus on gaining "
                f"skills in {', '.join(roadmap_result['missing_skills'][:3])}."
            )
            
        self.context["executive_summary"] = report_summary
        
        # Persist final session to database
        save_session_context(trace_id, filename, self.context)
        print(f"[Orchestrator] Session saved successfully. trace_id={trace_id}")
        
        return self.context

    def run_resume_optimizer(self, trace_id: str, target_jd: str) -> Dict[str, Any]:
        """
        Runs the ResumeOptimizerAgent on demand.
        """
        session_ctx = get_session_context(trace_id)
        if not session_ctx:
            raise ValueError(f"No active session found for trace ID {trace_id}")
            
        resume_text = session_ctx.get("raw_text", "")
        
        msg_opt = AgentMessage(
            message_id=str(uuid.uuid4()),
            trace_id=trace_id,
            from_agent=self.name,
            to_agent=self.resume_optimizer.name,
            task="optimize_resume",
            payload={"resume_text": resume_text, "target_jd": target_jd},
            status="pending",
            timestamp=datetime.now()
        )
        self._log_message(msg_opt)
        
        try:
            resp_opt = self.resume_optimizer.handle(msg_opt)
            self._log_message(resp_opt)
            if resp_opt.status == "success":
                result = resp_opt.result
                # Update saved context
                session_ctx["optimizer_data"] = result
                session_ctx["target_jd"] = target_jd
                save_session_context(trace_id, session_ctx.get("filename", "Resume"), session_ctx)
                return result
            else:
                raise ValueError(resp_opt.result.get("error", "Optimizer agent returned error status."))
        except Exception as e:
            logger.error(f"ResumeOptimizerAgent failed: {str(e)}")
            # Log failure message
            self._log_message(AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=trace_id,
                from_agent=self.resume_optimizer.name,
                to_agent=self.name,
                task="optimize_resume",
                payload={"resume_text": resume_text, "target_jd": target_jd},
                status="error",
                result={"error": str(e)},
                timestamp=datetime.now(),
                latency_ms=0
            ))
            raise e

    def run_interview_prep(self, trace_id: str) -> Dict[str, Any]:
        """
        Runs the InterviewPrepAgent on demand.
        """
        session_ctx = get_session_context(trace_id)
        if not session_ctx:
            raise ValueError(f"No active session found for trace ID {trace_id}")
            
        primary_role = session_ctx.get("primary_target_role", "Frontend Developer")
        
        # Flatten skills
        skills_dict = session_ctx.get("skills", {})
        skills_flat = []
        for cat, list_skills in skills_dict.items():
            skills_flat.extend(list_skills)
            
        msg_prep = AgentMessage(
            message_id=str(uuid.uuid4()),
            trace_id=trace_id,
            from_agent=self.name,
            to_agent=self.interview_prep.name,
            task="generate_interview_questions",
            payload={"predicted_role": primary_role, "skills": skills_flat},
            status="pending",
            timestamp=datetime.now()
        )
        self._log_message(msg_prep)
        
        try:
            resp_prep = self.interview_prep.handle(msg_prep)
            self._log_message(resp_prep)
            if resp_prep.status == "success":
                result = resp_prep.result
                # Update saved context
                session_ctx["interview_prep_data"] = result
                save_session_context(trace_id, session_ctx.get("filename", "Resume"), session_ctx)
                return result
            else:
                raise ValueError(resp_prep.result.get("error", "Interview coach agent returned error status."))
        except Exception as e:
            logger.error(f"InterviewPrepAgent failed: {str(e)}")
            self._log_message(AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=trace_id,
                from_agent=self.interview_prep.name,
                to_agent=self.name,
                task="generate_interview_questions",
                payload={"predicted_role": primary_role, "skills": skills_flat},
                status="error",
                result={"error": str(e)},
                timestamp=datetime.now(),
                latency_ms=0
            ))
            raise e
