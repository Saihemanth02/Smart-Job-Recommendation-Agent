import time
import os
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
from config.settings import DATA_DIR
from agents.base_agent import BaseAgent, AgentMessage

class MarketIntelligenceAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are a labor-market analyst. Given aggregate statistics — top "
            "trending skills, salary distribution by role, demand by location — "
            "summarize the 3 most actionable insights for someone targeting the "
            "candidate's predicted role. No filler, no generic 'the job market is "
            "competitive' statements — only insights traceable to the numbers "
            "you were given."
        )
        super().__init__(
            name="Market Intelligence Agent",
            role="Labor Market Analyst",
            system_prompt=system_prompt,
            model_backend="sklearn"
        )

    def handle(self, message: AgentMessage) -> AgentMessage:
        start_time = time.time()
        payload = message.payload
        predicted_role = payload.get("predicted_role", "")
        
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

        resumes_path = DATA_DIR / "resumes_seed.csv"
        salary_path = DATA_DIR / "salary_seed.csv"
        
        if not resumes_path.exists() or not salary_path.exists():
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": "Seed data files missing"},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )

        try:
            # 1. Load data
            df_resumes = pd.read_csv(resumes_path)
            df_salary = pd.read_csv(salary_path)
            
            # Filter for target role
            role_salaries = df_salary[df_salary['job_role'] == predicted_role]
            role_resumes = df_resumes[df_resumes['job_role'] == predicted_role]
            
            if role_salaries.empty or role_resumes.empty:
                # Fallback to general stats if target role has no records
                role_salaries = df_salary
                role_resumes = df_resumes
                
            # Calculate aggregate stats
            # A. Salary stats
            sal_stats = {
                "mean": float(role_salaries['salary'].mean()),
                "median": float(role_salaries['salary'].median()),
                "min": float(role_salaries['salary'].min()),
                "max": float(role_salaries['salary'].max()),
                "std": float(role_salaries['salary'].std())
            }
            
            # B. Salary by location tier
            sal_by_tier = role_salaries.groupby('location_tier')['salary'].mean().to_dict()
            sal_by_tier = {int(k): float(v) for k, v in sal_by_tier.items()}
            
            # C. Salary by years experience
            sal_by_exp = role_salaries.groupby('years_experience')['salary'].mean().to_dict()
            sal_by_exp = {int(k): float(v) for k, v in sal_by_exp.items()}
            
            # D. Most common skills in this role (based on resumes_seed.csv)
            all_skills = []
            for skills_list in role_resumes['skills'].dropna():
                all_skills.extend([s.strip() for s in skills_list.split(",")])
                
            skills_series = pd.Series(all_skills)
            top_skills = skills_series.value_counts().head(5).to_dict()
            top_skills = {str(k): int(v) for k, v in top_skills.items()}
            
            # Prepare statistics string for LLM call
            stats_context = (
                f"Predicted Role: {predicted_role}\n"
                f"- Salary statistics: Min={sal_stats['min']:.2f}L, Mean={sal_stats['mean']:.2f}L, Max={sal_stats['max']:.2f}L\n"
                f"- Salary by Location Tier: " + ", ".join([f"Tier {k}: {v:.2f}L" for k, v in sal_by_tier.items()]) + "\n"
                f"- Salary by Experience Level: " + ", ".join([f"{k} yrs: {v:.2f}L" for k, v in sal_by_exp.items()]) + "\n"
                f"- Top 5 trending skills in applicant resumes: " + ", ".join([f"{k} ({v} applicants)" for k, v in top_skills.items()])
            )
            
            user_prompt = (
                f"Here are the aggregate labor market statistics for {predicted_role}:\n\n"
                f"{stats_context}\n\n"
                f"Write a sharp 3-sentence labor market trend summary."
            )
            
            trend_summary = self.call_llm(user_prompt=user_prompt, json_mode=False, task_size="small")
            
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="success",
                result={
                    "salary_stats": sal_stats,
                    "salary_by_tier": sal_by_tier,
                    "salary_by_experience": sal_by_exp,
                    "top_skills": top_skills,
                    "trend_summary": trend_summary
                },
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
