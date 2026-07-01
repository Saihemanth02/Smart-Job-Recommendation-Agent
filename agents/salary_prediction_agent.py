import time
import os
import joblib
import numpy as np
from datetime import datetime
import uuid
import pandas as pd

from config.settings import MODEL_DIR
from agents.base_agent import BaseAgent, AgentMessage

class SalaryPredictionAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are a compensation analyst. Given a predicted salary range, "
            "the candidate's experience level, predicted role, and location, "
            "write a short, realistic note on how this compares to the current "
            "Indian job market for freshers/early-career hires in this role. "
            "Mention 1-2 concrete factors that could move the number up or down "
            "(certifications, internship brand, location tier). Never state a "
            "number as guaranteed — always frame it as a data-driven estimate."
        )
        super().__init__(
            name="Salary Prediction Agent",
            role="Compensation Analyst",
            system_prompt=system_prompt,
            model_backend="sklearn"
        )
        
        try:
            self.preprocessor = joblib.load(MODEL_DIR / "salary_preprocessor.pkl")
            self.regressor = joblib.load(MODEL_DIR / "salary_rf.pkl")
            self.artifacts_loaded = True
        except Exception as e:
            self.artifacts_loaded = False
            print(f"Error loading Salary Prediction Agent models: {str(e)}")

    def handle(self, message: AgentMessage) -> AgentMessage:
        start_time = time.time()
        
        if not self.artifacts_loaded:
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": "Salary models not found or loaded"},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )

        payload = message.payload
        predicted_role = payload.get("predicted_role", "")
        experience_years = payload.get("experience_years", 0)
        location_tier = payload.get("location_tier", 1)  # 1, 2, or 3
        num_skills = payload.get("num_skills", 0)
        education_encoded = payload.get("education_encoded", 2)
        num_certifications = payload.get("num_certifications", 0)
        
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
            # Create a dataframe representing the input row
            input_df = pd.DataFrame([{
                "job_role": predicted_role,
                "years_experience": experience_years,
                "location_tier": location_tier,
                "num_skills": num_skills,
                "education_encoded": education_encoded,
                "num_certifications": num_certifications
            }])
            
            # Preprocess the row
            X_processed = self.preprocessor.transform(input_df)
            
            # Get predictions from all estimators in the Random Forest ensemble
            estimator_preds = []
            for estimator in self.regressor.estimators_:
                # Transformed row may be a sparse matrix or dense
                pred = estimator.predict(X_processed)[0]
                estimator_preds.append(pred)
                
            mean_salary = float(np.mean(estimator_preds))
            std_salary = float(np.std(estimator_preds))
            
            # Calculate salary range (mean +/- std)
            low_salary = max(2.5, round(mean_salary - std_salary, 2))
            high_salary = round(mean_salary + std_salary, 2)
            
            # Location Tier Mapping
            tier_cities = {
                1: "Tier 1 Metro (Bangalore, Hyderabad, Pune, Mumbai, Chennai)",
                2: "Tier 2 City (Vizag, Kochi, Coimbatore, Jaipur)",
                3: "Tier 3 City (Vijayawada, Kakinada, Nellore, Warangal)"
            }.get(location_tier, "Tier 1 Metro")
            
            # Generate LLM compensation analyst notes
            user_prompt = (
                f"Candidate Details:\n"
                f"- Predicted Job Role: {predicted_role}\n"
                f"- Experience: {experience_years} years\n"
                f"- Education Level: {education_encoded} (1=B.Sc, 2=B.Tech, 3=M.Sc, 4=MCA, 5=M.Tech)\n"
                f"- Skills Count: {num_skills}\n"
                f"- Certifications Count: {num_certifications}\n"
                f"- Location: {tier_cities}\n"
                f"- Predicted Salary Range: {low_salary:.2f} LPA - {high_salary:.2f} LPA\n\n"
                f"Please write a short, realistic compensation note based on these parameters."
            )
            
            llm_note = self.call_llm(user_prompt=user_prompt, json_mode=False, task_size="small")
            
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="success",
                result={
                    "predicted_salary_mean": mean_salary,
                    "predicted_salary_std": std_salary,
                    "salary_low": low_salary,
                    "salary_high": high_salary,
                    "market_note": llm_note
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
